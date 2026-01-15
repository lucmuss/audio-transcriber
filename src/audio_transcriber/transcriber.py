"""
Main transcription orchestrator module.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Any

from openai import OpenAI, APIError
from tqdm import tqdm

from .constants import (
    DEFAULT_CONCURRENCY,
    DEFAULT_MAX_RETRIES,
    DEFAULT_MODEL,
    DEFAULT_OVERLAP,
    DEFAULT_RESPONSE_FORMAT,
    DEFAULT_SEGMENT_LENGTH,
    DEFAULT_TEMPERATURE,
)
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
    ) -> Dict[str, Any]:
        """
        Transcribe a single audio file.

        Args:
            file_path: Path to input audio file
            output_dir: Directory for output files
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

        logger.info(f"\n{'='*70}")
        logger.info(f"Processing: {file_path.name}")
        logger.info(f"{'='*70}")

        # Check if already processed
        file_stem = file_path.stem
        output_file = output_dir / f"{file_stem}_full.{response_format}"

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

        # Create segments
        try:
            segment_files = self.segmenter.segment_audio(
                file_path, segment_length, overlap, output_dir
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

        # Transcribe segments
        transcriptions, failed_count = self._transcribe_segments(
            segment_files=segment_files,
            language=detected_language,
            response_format=response_format,
            temperature=temperature,
            prompt=prompt,
            concurrency=concurrency,
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

        logger.info(
            f"Transcribed {len(transcriptions)}/{len(segment_files)} segments successfully"
        )

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
        except Exception as e:
            logger.error(f"Failed to save output: {e}")
            self._cleanup_segments(segment_files, keep_segments)
            return {"file": str(file_path), "status": "error", "error": f"Save failed: {e}"}

        # Cleanup temporary segment files
        if not keep_segments:
            self._cleanup_segments(segment_files)

        return {
            "file": str(file_path),
            "status": "success",
            "output": str(output_file),
            "segments": len(segment_files),
            "transcribed": len(transcriptions),
            "failed": failed_count,
            "duration_seconds": duration_seconds,
            "language": detected_language,
        }

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
    ) -> tuple[List[str], int]:
        """
        Transcribe segments in parallel.

        Returns:
            Tuple of (transcription_list, failed_count)
        """
        transcriptions = [None] * len(segment_files)  # Preserve order
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
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> Optional[str]:
        """
        Transcribe a single segment with retry logic.

        Returns:
            Transcription string or None if failed
        """
        retry_count = 0
        backoff_seconds = 1

        while retry_count < max_retries:
            try:
                with open(segment_file, "rb") as f:
                    kwargs = {
                        "model": self.model,
                        "file": f,
                        "response_format": response_format,
                        "temperature": temperature,
                    }

                    if language:
                        kwargs["language"] = language
                    if prompt:
                        kwargs["prompt"] = prompt

                    response = self.client.audio.transcriptions.create(**kwargs)

                # Handle different response types
                if response_format == "text":
                    return response if isinstance(response, str) else str(response)
                else:
                    return response.model_dump_json() if hasattr(response, "model_dump_json") else str(response)

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
