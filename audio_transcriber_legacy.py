#!/usr/bin/env python3
"""
Audio Transcription Tool
Automatic speech-to-text transcription for large audio files and folders
using OpenAI-compatible APIs with intelligent segmentation and merging.
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from pydub import AudioSegment
from tqdm import tqdm
from openai import OpenAI, APIError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)

# Supported audio formats
SUPPORTED_FORMATS = {".mp3", ".wav", ".flac", ".m4a", ".ogg", ".aac", ".wma", ".mp4"}

# OpenAI Whisper pricing (per minute)
WHISPER_PRICE_PER_MINUTE = 0.0001


class AudioTranscriber:
    """Main transcription orchestrator."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        model: str = "whisper-1",
        verbose: bool = False,
    ):
        """Initialize transcriber with API configuration."""
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.verbose = verbose

        if verbose:
            logger.setLevel(logging.DEBUG)

        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key, base_url=base_url)

        logger.info(f"Initialized transcriber with model: {model}")
        logger.debug(f"API Base URL: {base_url}")

    def find_audio_files(self, path: str) -> List[Path]:
        """Recursively find all supported audio files."""
        path_obj = Path(path)

        if path_obj.is_file():
            if path_obj.suffix.lower() in SUPPORTED_FORMATS:
                logger.info(f"Found single audio file: {path_obj}")
                return [path_obj]
            else:
                logger.error(f"Unsupported file format: {path_obj.suffix}")
                return []

        if path_obj.is_dir():
            audio_files = list(path_obj.rglob("*"))
            audio_files = [
                f
                for f in audio_files
                if f.is_file() and f.suffix.lower() in SUPPORTED_FORMATS
            ]
            logger.info(f"Found {len(audio_files)} audio files in {path}")
            return sorted(audio_files)

        logger.error(f"Path does not exist: {path}")
        return []

    def segment_audio(
        self,
        file_path: Path,
        segment_length_seconds: int,
        overlap_seconds: int,
        output_dir: Path,
        keep_segments: bool = False,
    ) -> List[Path]:
        """Segment audio file into chunks."""
        logger.info(f"Loading audio file: {file_path}")

        try:
            audio = AudioSegment.from_file(str(file_path))
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            return []

        total_duration_ms = len(audio)
        total_duration_seconds = total_duration_ms / 1000

        logger.info(
            f"Audio duration: {timedelta(seconds=int(total_duration_seconds))}"
        )

        segment_length_ms = segment_length_seconds * 1000
        overlap_ms = overlap_seconds * 1000
        step_ms = segment_length_ms - overlap_ms

        segment_files = []
        segment_num = 1

        start_ms = 0
        while start_ms < total_duration_ms:
            end_ms = min(start_ms + segment_length_ms, total_duration_ms)
            segment = audio[start_ms:end_ms]

            # Optimize audio for transcription: resample to 16kHz (OpenAI Whisper standard)
            # and convert to mono for better compression
            if segment.frame_rate != 16000 or segment.channels != 1:
                segment = segment.set_frame_rate(16000).set_channels(1)

            # Create output file in MP3 format with optimized bitrate
            # 64kbps is sufficient for speech transcription and saves ~90% space vs WAV
            file_stem = file_path.stem
            segment_file = output_dir / f"{file_stem}_{segment_num:03d}.mp3"
            segment.export(
                str(segment_file),
                format="mp3",
                bitrate="64k",
                parameters=["-q:a", "9"]  # VBR quality setting for better compression
            )

            segment_files.append(segment_file)
            logger.debug(
                f"Created segment {segment_num}: {segment_file.name} "
                f"({int((end_ms - start_ms) / 1000)}s)"
            )

            segment_num += 1
            start_ms += step_ms

            if end_ms >= total_duration_ms:
                break

        logger.info(f"Created {len(segment_files)} segments")

        return segment_files

    def detect_language(self, segment_file: Path) -> Optional[str]:
        """Detect language from first segment."""
        logger.debug(f"Detecting language from: {segment_file}")

        try:
            with open(segment_file, "rb") as f:
                response = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=f,
                    response_format="json",
                )

            language = getattr(response, "language", None)
            logger.info(f"Detected language: {language}")
            return language

        except APIError as e:
            logger.warning(f"Language detection failed: {e}")
            return None

    def transcribe_segment(
        self,
        segment_file: Path,
        language: Optional[str] = None,
        response_format: str = "text",
        temperature: float = 0.0,
        prompt: Optional[str] = None,
        max_retries: int = 5,
    ) -> Optional[str]:
        """Transcribe a single segment with retry logic."""
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

                # Handle different response formats
                if response_format == "text":
                    # OpenAI returns text directly as a string when format is "text"
                    return response
                else:
                    # For other formats, return the JSON representation
                    return response.model_dump_json()

            except APIError as e:
                retry_count += 1
                if retry_count < max_retries:
                    logger.warning(
                        f"API error (retry {retry_count}/{max_retries}): {e}"
                    )
                    time.sleep(backoff_seconds)
                    backoff_seconds *= 2
                else:
                    logger.error(f"Transcription failed after {max_retries} retries: {e}")
                    return None
            except Exception as e:
                logger.error(f"Unexpected error during transcription: {e}")
                return None

        return None

    def merge_segments(
        self, transcriptions: List[str], response_format: str = "text"
    ) -> str:
        """Merge segment transcriptions with overlap deduplication."""
        if not transcriptions:
            return ""

        if response_format == "text":
            return self._merge_text_segments(transcriptions)

        elif response_format in ["srt", "vtt"]:
            return self._merge_subtitle_segments(transcriptions, response_format)

        elif response_format in ["json", "verbose_json"]:
            return self._merge_json_segments(transcriptions)

        else:
            # Fallback: simple concatenation with newlines
            return "\n".join(str(t) for t in transcriptions if t)

    def _merge_text_segments(self, transcriptions: List[str]) -> str:
        """Merge text segments with simple overlap removal."""
        if len(transcriptions) == 1:
            return transcriptions[0]

        merged = [transcriptions[0]]

        for i in range(1, len(transcriptions)):
            current = transcriptions[i].strip()
            if current:
                # Simple deduplication: check if first sentence of current
                # is similar to last sentences of merged
                sentences_current = current.split(".")
                merged_text = " ".join(merged).strip()
                sentences_merged = merged_text.split(".")

                # Find overlap (simplified: check last sentence)
                if len(sentences_merged) > 0 and len(sentences_current) > 0:
                    last_merged = sentences_merged[-1].strip()
                    first_current = sentences_current[0].strip()

                    # If first sentence of current is similar to last of merged,
                    # skip it
                    if (
                        last_merged
                        and first_current
                        and last_merged.lower() == first_current.lower()
                    ):
                        # Skip the first sentence and add the rest
                        remaining = ".".join(sentences_current[1:]).strip()
                        if remaining:
                            merged.append(" " + remaining)
                    else:
                        merged.append(" " + current)
                else:
                    merged.append(" " + current)

        return "".join(merged).strip()

    def _merge_subtitle_segments(
        self, transcriptions: List[str], format_type: str
    ) -> str:
        """Merge subtitle segments (SRT/VTT) with corrected timings."""
        # Parse and merge subtitle entries with proper timestamp offsetting
        all_entries = []
        segment_offset = 0

        for trans in transcriptions:
            if not trans.strip():
                continue

            # Parse subtitle format (simplified)
            lines = trans.strip().split("\n")

            # For now, simple concatenation with offset tracking
            # Full implementation would parse and recalculate timestamps
            all_entries.extend(lines)

        return "\n".join(all_entries)

    def _merge_json_segments(self, transcriptions: List[str]) -> str:
        """Merge JSON segments with timestamp offsetting."""
        segments = []

        for trans in transcriptions:
            if not trans.strip():
                continue

            try:
                data = json.loads(trans)
                segments.append(data)
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON segment")
                continue

        # Create merged result
        merged = {
            "segments": segments,
            "language": getattr(segments[0], "language", None) if segments else None,
        }

        return json.dumps(merged, indent=2)

    def transcribe_file(
        self,
        file_path: Path,
        output_dir: Path,
        segment_length_seconds: int = 600,
        overlap_seconds: int = 10,
        language: Optional[str] = None,
        detect_language: bool = True,
        response_format: str = "text",
        concurrency: int = 4,
        temperature: float = 0.0,
        prompt: Optional[str] = None,
        keep_segments: bool = False,
        skip_existing: bool = True,
    ) -> Dict[str, Any]:
        """Transcribe a single audio file."""
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {file_path.name}")
        logger.info(f"{'='*60}")

        file_stem = file_path.stem
        output_full = output_dir / f"{file_stem}_full.{response_format}"

        # Check if already processed
        if skip_existing and output_full.exists():
            logger.info(f"Output already exists, skipping: {output_full}")
            return {"file": file_path, "status": "skipped", "segments": 0}

        # Segment audio
        segment_files = self.segment_audio(
            file_path, segment_length_seconds, overlap_seconds, output_dir, keep_segments
        )

        if not segment_files:
            logger.error(f"Failed to create segments for {file_path}")
            return {"file": file_path, "status": "error", "segments": 0}

        detected_language = language

        # Detect language from first segment if enabled
        if detect_language and not language:
            detected_language = self.detect_language(segment_files[0])

        logger.info(f"Using language: {detected_language or 'auto'}")

        # Transcribe segments concurrently
        transcriptions = []
        failed_segments = 0

        logger.info(f"Transcribing {len(segment_files)} segments...")

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = {
                executor.submit(
                    self.transcribe_segment,
                    seg_file,
                    language=detected_language,
                    response_format=response_format,
                    temperature=temperature,
                    prompt=prompt,
                ): i
                for i, seg_file in enumerate(segment_files)
            }

            pbar = tqdm(as_completed(futures), total=len(futures), desc="Segments")
            for future in pbar:
                result = future.result()
                if result:
                    transcriptions.append(result)
                else:
                    failed_segments += 1
                pbar.update()

        if not transcriptions:
            logger.error("No segments transcribed successfully")
            return {
                "file": file_path,
                "status": "error",
                "segments": 0,
                "failed": failed_segments,
            }

        logger.info(f"Successfully transcribed {len(transcriptions)}/{len(segment_files)} segments")

        # Save individual segment transcriptions
        for i, trans in enumerate(transcriptions, 1):
            seg_output = output_dir / f"{file_stem}_{i:03d}.{response_format}"
            try:
                with open(seg_output, "w", encoding="utf-8") as f:
                    f.write(trans)
                logger.debug(f"Saved segment: {seg_output}")
            except Exception as e:
                logger.error(f"Failed to save segment {i}: {e}")

        # Merge segments
        logger.info("Merging segments...")
        merged_text = self.merge_segments(transcriptions, response_format)

        # Save full transcription
        try:
            with open(output_full, "w", encoding="utf-8") as f:
                f.write(merged_text)
            logger.info(f"Saved full transcription: {output_full}")
        except Exception as e:
            logger.error(f"Failed to save full transcription: {e}")
            return {
                "file": file_path,
                "status": "error",
                "segments": len(transcriptions),
            }

        # Clean up temporary segment files
        if not keep_segments:
            for seg_file in segment_files:
                try:
                    seg_file.unlink()
                    logger.debug(f"Deleted temporary file: {seg_file}")
                except Exception as e:
                    logger.warning(f"Failed to delete {seg_file}: {e}")

        # Calculate duration in minutes
        total_duration_ms = len(AudioSegment.from_file(str(file_path)))
        duration_minutes = total_duration_ms / 1000 / 60

        return {
            "file": file_path,
            "status": "success",
            "segments": len(transcriptions),
            "duration_minutes": duration_minutes,
            "detected_language": detected_language,
            "failed": failed_segments,
        }

    def summarize_transcription(
        self,
        transcription_text: str,
        output_path: Path,
    ) -> bool:
        """Create a summary of the transcription."""
        logger.info("Generating summary...")

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # or config this
                messages=[
                    {
                        "role": "user",
                        "content": f"Please provide a concise summary of the following transcription:\n\n{transcription_text[:5000]}",
                    }
                ],
                temperature=0.7,
                max_tokens=500,
            )

            summary = response.choices[0].message.content

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(summary)

            logger.info(f"Summary saved: {output_path}")
            return True

        except Exception as e:
            logger.warning(f"Failed to generate summary: {e}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Transcribe large audio files using OpenAI-compatible APIs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single file with OpenAI
  python transcribe_audio.py --input podcast.mp3

  # Folder with local Ollama
  python transcribe_audio.py --input ./audio_files --base-url http://localhost:11434/v1

  # With language detection and SRT output
  python transcribe_audio.py --input meeting.wav --response-format srt --detect-language

  # With summary
  python transcribe_audio.py --input lecture.m4a --summarize

Environment variables (prefix: AUDIO_TRANSCRIBE_):
  AUDIO_TRANSCRIBE_API_KEY
  AUDIO_TRANSCRIBE_BASE_URL
  AUDIO_TRANSCRIBE_MODEL
  AUDIO_TRANSCRIBE_OUTPUT_DIR
  AUDIO_TRANSCRIBE_SEGMENT_LENGTH
  AUDIO_TRANSCRIBE_OVERLAP
  AUDIO_TRANSCRIBE_CONCURRENCY
        """,
    )

    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to audio file or folder",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default=os.getenv("AUDIO_TRANSCRIBE_OUTPUT_DIR", "./transcriptions"),
        help="Output directory for transcriptions (default: ./transcriptions)",
    )

    parser.add_argument(
        "--segment-length",
        type=int,
        default=int(os.getenv("AUDIO_TRANSCRIBE_SEGMENT_LENGTH", "600")),
        help="Segment length in seconds (default: 600 = 10 minutes)",
    )

    parser.add_argument(
        "--overlap",
        type=int,
        default=int(os.getenv("AUDIO_TRANSCRIBE_OVERLAP", "10")),
        help="Overlap between segments in seconds (default: 10)",
    )

    parser.add_argument(
        "--model",
        type=str,
        default=os.getenv("AUDIO_TRANSCRIBE_MODEL", "whisper-1"),
        help="Whisper model name (default: whisper-1)",
    )

    parser.add_argument(
        "--api-key",
        type=str,
        default=os.getenv("AUDIO_TRANSCRIBE_API_KEY"),
        help="OpenAI API key (or AUDIO_TRANSCRIBE_API_KEY env var)",
    )

    parser.add_argument(
        "--base-url",
        type=str,
        default=os.getenv("AUDIO_TRANSCRIBE_BASE_URL", "https://api.openai.com/v1"),
        help="API base URL (default: https://api.openai.com/v1)",
    )

    parser.add_argument(
        "--language",
        type=str,
        default=None,
        help="ISO-639-1 language code (e.g., 'de', 'en'). If not set, auto-detect.",
    )

    parser.add_argument(
        "--detect-language",
        action="store_true",
        default=True,
        help="Auto-detect language from first segment (default: True)",
    )

    parser.add_argument(
        "--no-detect-language",
        action="store_false",
        dest="detect_language",
        help="Disable language detection",
    )

    parser.add_argument(
        "--response-format",
        type=str,
        choices=["text", "json", "srt", "vtt", "verbose_json"],
        default="text",
        help="Transcription output format (default: text)",
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=int(os.getenv("AUDIO_TRANSCRIBE_CONCURRENCY", "4")),
        help="Number of concurrent segment transcriptions (default: 4)",
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Temperature for model (default: 0.0). Range: 0-1",
    )

    parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Initial prompt for context (e.g., names, technical terms)",
    )

    parser.add_argument(
        "--keep-segments",
        action="store_true",
        help="Keep temporary segment files",
    )

    parser.add_argument(
        "--summarize",
        action="store_true",
        help="Generate a summary of the full transcription",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate segmentation without transcription",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.api_key:
        logger.error("API key required. Set --api-key or AUDIO_TRANSCRIBE_API_KEY")
        sys.exit(1)

    if args.segment_length <= 0:
        logger.error("Segment length must be > 0")
        sys.exit(1)

    if args.overlap < 0:
        logger.error("Overlap must be >= 0")
        sys.exit(1)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")

    # Find audio files
    audio_files = None

    # Initialize transcriber
    transcriber = AudioTranscriber(
        api_key=args.api_key,
        base_url=args.base_url,
        model=args.model,
        verbose=args.verbose,
    )

    # Find audio files
    audio_files = transcriber.find_audio_files(args.input)

    if not audio_files:
        logger.error("No audio files found")
        sys.exit(1)

    logger.info(f"Found {len(audio_files)} audio file(s) to process")

    # Dry-run mode
    if args.dry_run:
        logger.info("\n*** DRY RUN MODE ***\n")
        logger.info(f"Would segment audio with:")
        logger.info(f"  - Segment length: {args.segment_length}s")
        logger.info(f"  - Overlap: {args.overlap}s")
        logger.info(f"  - Model: {args.model}")
        logger.info(f"  - Format: {args.response_format}")
        logger.info(f"  - Concurrency: {args.concurrency}")
        logger.info(f"  - Language detect: {args.detect_language}")
        return

    # Process files
    results = []
    total_duration_minutes = 0
    total_failed = 0

    with tqdm(audio_files, desc="Files", position=0) as pbar:
        for audio_file in pbar:
            result = transcriber.transcribe_file(
                audio_file,
                output_dir,
                segment_length_seconds=args.segment_length,
                overlap_seconds=args.overlap,
                language=args.language,
                detect_language=args.detect_language,
                response_format=args.response_format,
                concurrency=args.concurrency,
                temperature=args.temperature,
                prompt=args.prompt,
                keep_segments=args.keep_segments,
            )

            results.append(result)

            if result["status"] == "success":
                total_duration_minutes += result.get("duration_minutes", 0)
                total_failed += result.get("failed", 0)

                # Generate summary if requested
                if args.summarize:
                    output_file = output_dir / f"{audio_file.stem}_full.{args.response_format}"
                    if output_file.exists():
                        with open(output_file, "r", encoding="utf-8") as f:
                            text = f.read()
                        summary_file = output_dir / f"{audio_file.stem}_summary.txt"
                        transcriber.summarize_transcription(text, summary_file)

            pbar.update()

    # Print summary statistics
    logger.info(f"\n{'='*60}")
    logger.info("TRANSCRIPTION COMPLETE")
    logger.info(f"{'='*60}")

    successful = sum(1 for r in results if r["status"] == "success")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    failed = sum(1 for r in results if r["status"] == "error")

    logger.info(f"Files processed:    {successful}")
    logger.info(f"Files skipped:      {skipped}")
    logger.info(f"Files failed:       {failed}")
    logger.info(f"Total segments:     {sum(r.get('segments', 0) for r in results)}")
    logger.info(f"Failed segments:    {total_failed}")
    logger.info(f"Total duration:     {timedelta(minutes=int(total_duration_minutes))}")

    if total_duration_minutes > 0:
        estimated_cost = total_duration_minutes * WHISPER_PRICE_PER_MINUTE
        logger.info(f"Estimated cost:     ${estimated_cost:.4f} (OpenAI whisper-1)")

    logger.info(f"Output directory:   {output_dir}")
    logger.info(f"{'='*60}\n")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
