"""
Main transcription orchestrator module.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from openai import APIError, OpenAI
from tqdm import tqdm

from .constants import (
    DEFAULT_CONCURRENCY,
    DEFAULT_DIARIZATION_FORMAT,
    DEFAULT_DIARIZATION_MODEL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_MODEL,
    DEFAULT_OVERLAP,
    DEFAULT_RESPONSE_FORMAT,
    DEFAULT_SEGMENT_LENGTH,
    DEFAULT_SUMMARY_MODEL,
    DEFAULT_SUMMARY_PROMPT,
    DEFAULT_TEMPERATURE,
)
from .diarizer import format_diarized_transcript, to_data_url
from .merger import TranscriptionMerger
from .segmenter import AudioSegmenter
from .utils import format_duration, validate_segment_params

logger = logging.getLogger(__name__)


class AudioTranscriber:
    """
    Main orchestrator for audio transcription workflow.

    Handles the complete pipeline: segmentation -> transcription -> merging.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        model: str = DEFAULT_MODEL,
    ):
        """
        Initialize transcriber with API configuration.

        Args:
            api_key: OpenAI API key or compatible service key
            base_url: API base URL (default: OpenAI endpoint)
            model: Model name to use for transcription
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.segmenter = AudioSegmenter()
        self.merger = TranscriptionMerger()

        logger.info(f"Initialized transcriber with model: {model}")
        logger.debug(f"API Base URL: {base_url}")

    def transcribe_file(
        self,
        file_path: Path,
        output_dir: Path,
        segments_dir: Optional[Path] = None,
        segment_length: int = DEFAULT_SEGMENT_LENGTH,
        overlap: int = DEFAULT_OVERLAP,
        language: Optional[str] = None,
        detect_language: bool = True,
        response_format: str = DEFAULT_RESPONSE_FORMAT,
        concurrency: int = DEFAULT_CONCURRENCY,
        temperature: float = DEFAULT_TEMPERATURE,
        prompt: Optional[str] = None,
        keep_segments: bool = False,
        skip_existing: bool = True,
        save_segment_transcriptions: bool = True,
        enable_diarization: bool = False,
        num_speakers: Optional[int] = None,
        known_speaker_names: Optional[List[str]] = None,
        known_speaker_references: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Transcribe a single audio file.

        Args:
            file_path: Path to input audio file
            output_dir: Directory for final transcription output
            segments_dir: Directory for temporary segment files (default: output_dir)
            segment_length: Segment length in seconds
            overlap: Overlap between segments in seconds
            language: ISO-639-1 language code (e.g., 'en', 'de')
            detect_language: Auto-detect language from first segment
            response_format: Output format (text, json, srt, vtt, verbose_json)
            concurrency: Number of parallel transcription jobs
            temperature: Model temperature (0.0 = deterministic)
            prompt: Optional context prompt for better accuracy
            keep_segments: Keep temporary segment files after processing
            skip_existing: Skip if output file already exists

        Returns:
            Dictionary with transcription results and metadata

        Raises:
            ValueError: If parameters are invalid
            FileNotFoundError: If input file doesn't exist
        """
        validate_segment_params(segment_length, overlap, concurrency, temperature)

        logger.info(f"\n{'=' * 70}")
        logger.info(f"Processing: {file_path.name}")
        logger.info(f"{'=' * 70}")

        # Override model and format if diarization is enabled
        effective_model = self.model
        effective_format = response_format

        if enable_diarization:
            effective_model = DEFAULT_DIARIZATION_MODEL
            effective_format = DEFAULT_DIARIZATION_FORMAT
            logger.info("🎤 Diarization enabled - using gpt-4o-transcribe-diarize")
            if num_speakers:
                logger.info(f"Expected speakers: {num_speakers}")
            if known_speaker_names:
                logger.info(f"Known speakers: {', '.join(known_speaker_names)}")

        # Check if already processed
        # Include original extension in output name to avoid collisions
        # e.g., test.mp3 -> test_mp3_full.text, test.wav -> test_wav_full.text
        file_stem = file_path.stem
        file_ext = file_path.suffix.lstrip(".")  # Remove leading dot
        output_filename = (
            f"{file_stem}_{file_ext}_full.{response_format}"
            if file_ext
            else f"{file_stem}_full.{response_format}"
        )
        output_file = output_dir / output_filename

        if skip_existing and output_file.exists():
            logger.info(f"Output already exists, skipping: {output_file.name}")
            return {"file": str(file_path), "status": "skipped", "output": str(output_file)}

        # Get audio duration
        try:
            duration_seconds = self.segmenter.get_audio_duration(file_path)
        except Exception as e:
            logger.error(f"Failed to read audio file: {e}")
            return {"file": str(file_path), "status": "error", "error": str(e)}

        logger.info(f"Duration: {format_duration(duration_seconds)}")

        # Use separate segments directory if provided, otherwise use output_dir
        seg_dir = segments_dir if segments_dir is not None else output_dir

        # Create segments
        try:
            segment_files = self.segmenter.segment_audio(
                file_path, segment_length, overlap, seg_dir
            )
        except Exception as e:
            logger.error(f"Segmentation failed: {e}")
            return {"file": str(file_path), "status": "error", "error": str(e)}

        if not segment_files:
            logger.error("No segments created")
            return {"file": str(file_path), "status": "error", "error": "No segments created"}

        # Detect language if enabled
        detected_language = language
        if detect_language and not language and segment_files:
            try:
                detected_language = self._detect_language(segment_files[0])
                logger.info(f"Detected language: {detected_language or 'unknown'}")
            except Exception as e:
                logger.warning(f"Language detection failed: {e}")

        # Prepare speaker references if provided
        speaker_references = None
        if enable_diarization and known_speaker_references:
            try:
                speaker_references = [to_data_url(Path(ref)) for ref in known_speaker_references]
                logger.info(f"Prepared {len(speaker_references)} speaker reference(s)")
            except Exception as e:
                logger.warning(f"Failed to prepare speaker references: {e}")
                speaker_references = None

        # Transcribe segments
        transcriptions, failed_count = self._transcribe_segments(
            segment_files=segment_files,
            language=detected_language,
            response_format=effective_format,
            temperature=temperature,
            prompt=prompt,
            concurrency=concurrency,
            output_dir=output_dir if save_segment_transcriptions else None,
            file_stem=file_stem,
            file_ext=file_ext,
            effective_model=effective_model,
            enable_diarization=enable_diarization,
            num_speakers=num_speakers,
            known_speaker_names=known_speaker_names,
            speaker_references=speaker_references,
        )

        if not transcriptions:
            logger.error("No segments transcribed successfully")
            self._cleanup_segments(segment_files)
            return {
                "file": str(file_path),
                "status": "error",
                "error": "All segments failed",
                "failed_segments": failed_count,
            }

        logger.info(f"Transcribed {len(transcriptions)}/{len(segment_files)} segments successfully")

        # Merge transcriptions
        try:
            merged_text = self.merger.merge(transcriptions, response_format)
        except Exception as e:
            logger.error(f"Merging failed: {e}")
            self._cleanup_segments(segment_files, keep_segments)
            return {"file": str(file_path), "status": "error", "error": f"Merge failed: {e}"}

        # Save full transcription
        output_dir.mkdir(parents=True, exist_ok=True)
        try:
            output_file.write_text(merged_text, encoding="utf-8")
            logger.info(f"Saved transcription: {output_file.name}")

            # If diarization is enabled, also save a human-readable version
            if enable_diarization and effective_format == "diarized_json":
                readable_filename = (
                    f"{file_stem}_{file_ext}_full_readable.txt"
                    if file_ext
                    else f"{file_stem}_full_readable.txt"
                )
                readable_file = output_dir / readable_filename

                try:
                    readable_text = format_diarized_transcript(merged_text, include_timestamps=True)
                    readable_file.write_text(readable_text, encoding="utf-8")
                    logger.info(f"Saved readable diarized transcription: {readable_file.name}")
                except Exception as e:
                    logger.warning(f"Failed to create readable version: {e}")

        except Exception as e:
            logger.error(f"Failed to save output: {e}")
            self._cleanup_segments(segment_files, keep_segments)
            return {"file": str(file_path), "status": "error", "error": f"Save failed: {e}"}

        # Cleanup temporary segment files
        if not keep_segments:
            self._cleanup_segments(segment_files)

        result = {
            "file": str(file_path),
            "status": "success",
            "output": str(output_file),
            "segments": len(segment_files),
            "transcribed": len(transcriptions),
            "failed": failed_count,
            "duration_seconds": duration_seconds,
            "language": detected_language,
        }

        # Add diarization info if enabled
        if enable_diarization:
            result["diarization_enabled"] = True
            if enable_diarization and effective_format == "diarized_json":
                result["readable_output"] = str(output_dir / readable_filename)

        return result

    def _detect_language(self, segment_file: Path) -> Optional[str]:
        """Detect language from first audio segment."""
        logger.debug(f"Detecting language from: {segment_file.name}")

        try:
            with open(segment_file, "rb") as f:
                response = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=f,
                    response_format="json",
                )

            language = getattr(response, "language", None)
            return language
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return None

    def _transcribe_segments(
        self,
        segment_files: List[Path],
        language: Optional[str],
        response_format: str,
        temperature: float,
        prompt: Optional[str],
        concurrency: int,
        output_dir: Optional[Path] = None,
        file_stem: str = "",
        file_ext: str = "",
        effective_model: str = DEFAULT_MODEL,
        enable_diarization: bool = False,
        num_speakers: Optional[int] = None,
        known_speaker_names: Optional[List[str]] = None,
        speaker_references: Optional[List[str]] = None,
    ) -> Tuple[List[str], int]:
        """
        Transcribe segments in parallel.

        Args:
            output_dir: If provided, save individual segment transcriptions
            file_stem: Base filename for segment transcriptions
            file_ext: File extension for segment transcriptions
            effective_model: Model to use (may be overridden for diarization)
            enable_diarization: Whether diarization is enabled
            num_speakers: Expected number of speakers
            known_speaker_names: List of known speaker names
            speaker_references: List of data URLs for speaker references

        Returns:
            Tuple of (transcription_list, failed_count)
        """
        transcriptions: List[Optional[str]] = [None] * len(segment_files)  # Preserve order
        failed_count = 0

        logger.info(f"Transcribing {len(segment_files)} segments (concurrency: {concurrency})...")

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_to_index = {
                executor.submit(
                    self._transcribe_segment,
                    seg_file,
                    language=language,
                    response_format=response_format,
                    temperature=temperature,
                    prompt=prompt,
                    effective_model=effective_model,
                    enable_diarization=enable_diarization,
                    num_speakers=num_speakers,
                    known_speaker_names=known_speaker_names,
                    speaker_references=speaker_references,
                ): i
                for i, seg_file in enumerate(segment_files)
            }

            with tqdm(total=len(segment_files), desc="Segments", unit="seg") as pbar:
                for future in as_completed(future_to_index):
                    index = future_to_index[future]
                    try:
                        result = future.result()
                        if result:
                            transcriptions[index] = result

                            # Save individual segment transcription if output_dir is provided
                            if output_dir:
                                segment_num = index + 1
                                if file_ext:
                                    segment_filename = (
                                        f"{file_stem}_{file_ext}_segment_"
                                        f"{segment_num:03d}.{response_format}"
                                    )
                                else:
                                    segment_filename = (
                                        f"{file_stem}_segment_{segment_num:03d}.{response_format}"
                                    )
                                segment_output_file = output_dir / segment_filename

                                try:
                                    segment_output_file.write_text(result, encoding="utf-8")
                                    logger.debug(f"Saved segment transcription: {segment_filename}")
                                except Exception as e:
                                    logger.warning(
                                        f"Failed to save segment {segment_num} transcription: {e}"
                                    )
                        else:
                            failed_count += 1
                            logger.warning(f"Segment {index + 1} failed")
                    except Exception as e:
                        failed_count += 1
                        logger.error(f"Segment {index + 1} exception: {e}")

                    pbar.update(1)

        # Filter out None values while preserving order
        valid_transcriptions = [t for t in transcriptions if t is not None]

        return valid_transcriptions, failed_count

    def _transcribe_segment(
        self,
        segment_file: Path,
        language: Optional[str],
        response_format: str,
        temperature: float,
        prompt: Optional[str],
        effective_model: str = DEFAULT_MODEL,
        enable_diarization: bool = False,
        num_speakers: Optional[int] = None,
        known_speaker_names: Optional[List[str]] = None,
        speaker_references: Optional[List[str]] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> Optional[str]:
        """
        Transcribe a single segment with retry logic and optional diarization.

        Args:
            segment_file: Path to audio segment file
            language: Language code
            response_format: Response format
            temperature: Model temperature
            prompt: Context prompt
            effective_model: Model to use (may be diarization model)
            enable_diarization: Whether to use diarization
            num_speakers: Expected number of speakers
            known_speaker_names: List of known speaker names
            speaker_references: List of data URLs for speaker references
            max_retries: Maximum retry attempts

        Returns:
            Transcription string or None if failed
        """
        retry_count = 0
        backoff_seconds = 1

        while retry_count < max_retries:
            try:
                with open(segment_file, "rb") as f:
                    kwargs = {
                        "model": effective_model,
                        "file": f,
                        "response_format": response_format,
                        "temperature": temperature,
                    }

                    if language:
                        kwargs["language"] = language
                    if prompt:
                        kwargs["prompt"] = prompt

                    # Add diarization-specific parameters
                    if enable_diarization:
                        kwargs["chunking_strategy"] = "auto"

                        # Build extra_body for diarization parameters
                        extra_body: Dict[str, Any] = {}

                        if num_speakers:
                            extra_body["num_speakers"] = num_speakers

                        if known_speaker_names:
                            extra_body["known_speaker_names"] = known_speaker_names

                        if speaker_references:
                            extra_body["known_speaker_references"] = speaker_references

                        if extra_body:
                            kwargs["extra_body"] = extra_body

                    response = self.client.audio.transcriptions.create(**kwargs)

                # Handle different response types
                if response_format == "text":
                    return response if isinstance(response, str) else str(response)
                elif response_format == "diarized_json":
                    # For diarized_json, we get the raw JSON response
                    if hasattr(response, "model_dump_json"):
                        return str(response.model_dump_json())
                    else:
                        return str(response)
                else:
                    return (
                        str(response.model_dump_json())
                        if hasattr(response, "model_dump_json")
                        else str(response)
                    )

            except APIError as e:
                retry_count += 1
                if retry_count < max_retries:
                    logger.debug(
                        f"API error for {segment_file.name} "
                        f"(retry {retry_count}/{max_retries}): {e}"
                    )
                    time.sleep(backoff_seconds)
                    backoff_seconds *= 2
                else:
                    logger.error(f"Failed after {max_retries} retries: {segment_file.name}")
                    return None

            except Exception as e:
                logger.error(f"Unexpected error transcribing {segment_file.name}: {e}")
                return None

        return None

    def _cleanup_segments(self, segment_files: List[Path], keep: bool = False) -> None:
        """Delete temporary segment files."""
        if keep:
            logger.info(f"Keeping {len(segment_files)} segment files")
            return

        deleted = 0
        for seg_file in segment_files:
            try:
                if seg_file.exists():
                    seg_file.unlink()
                    deleted += 1
            except Exception as e:
                logger.warning(f"Failed to delete {seg_file.name}: {e}")

        logger.debug(f"Deleted {deleted} temporary segment files")

    def summarize_transcription(
        self,
        transcription_file: Path,
        summary_dir: Path,
        summary_model: str = DEFAULT_SUMMARY_MODEL,
        summary_prompt: str = DEFAULT_SUMMARY_PROMPT,
        skip_existing: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate a summary of a transcription file.

        Args:
            transcription_file: Path to transcription file
            summary_dir: Directory for summary output
            summary_model: Model to use for summarization (e.g., 'gpt-4o-mini')
            summary_prompt: Custom prompt for summary generation
            skip_existing: Skip if summary file already exists

        Returns:
            Dictionary with summary results and metadata
        """
        logger.info(f"\n{'=' * 70}")
        logger.info(f"Generating summary for: {transcription_file.name}")
        logger.info(f"{'=' * 70}")

        # Check if transcription file exists
        if not transcription_file.exists():
            logger.error(f"Transcription file not found: {transcription_file}")
            return {
                "transcription_file": str(transcription_file),
                "status": "error",
                "error": "Transcription file not found",
            }

        # Determine summary output filename
        # e.g., test_mp3_full.text -> test_mp3_summary.txt
        file_stem = transcription_file.stem.replace("_full", "")
        summary_filename = f"{file_stem}_summary.txt"
        summary_file = summary_dir / summary_filename

        # Check if summary already exists
        if skip_existing and summary_file.exists():
            logger.info(f"Summary already exists, skipping: {summary_file.name}")
            return {
                "transcription_file": str(transcription_file),
                "status": "skipped",
                "summary_file": str(summary_file),
            }

        # Read transcription content
        try:
            transcription_text = transcription_file.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read transcription file: {e}")
            return {
                "transcription_file": str(transcription_file),
                "status": "error",
                "error": f"Failed to read file: {e}",
            }

        if not transcription_text.strip():
            logger.warning("Transcription is empty, skipping summarization")
            return {
                "transcription_file": str(transcription_file),
                "status": "skipped",
                "error": "Empty transcription",
            }

        # Generate summary using chat completion API
        logger.info(f"Using model: {summary_model}")
        logger.info(f"Transcription length: {len(transcription_text)} characters")

        try:
            response = self.client.chat.completions.create(
                model=summary_model,
                messages=[
                    {
                        "role": "system",
                        "content": summary_prompt,
                    },
                    {
                        "role": "user",
                        "content": transcription_text,
                    },
                ],
                temperature=0.3,  # Slightly creative but mostly factual
            )

            summary_text = response.choices[0].message.content

            if not summary_text:
                logger.error("Summary generation returned empty content")
                return {
                    "transcription_file": str(transcription_file),
                    "status": "error",
                    "error": "Empty summary returned",
                }

        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return {
                "transcription_file": str(transcription_file),
                "status": "error",
                "error": f"Summary generation failed: {e}",
            }

        # Save summary to file
        summary_dir.mkdir(parents=True, exist_ok=True)
        try:
            summary_file.write_text(summary_text, encoding="utf-8")
            logger.info(f"Saved summary: {summary_file.name}")
            logger.info(f"Summary length: {len(summary_text)} characters")
        except Exception as e:
            logger.error(f"Failed to save summary: {e}")
            return {
                "transcription_file": str(transcription_file),
                "status": "error",
                "error": f"Failed to save summary: {e}",
            }

        return {
            "transcription_file": str(transcription_file),
            "status": "success",
            "summary_file": str(summary_file),
            "summary_model": summary_model,
            "original_length": len(transcription_text),
            "summary_length": len(summary_text),
        }
