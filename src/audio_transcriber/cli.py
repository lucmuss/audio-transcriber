"""
Command-line interface for Audio Transcriber.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List

from . import __version__
from .constants import (
    DEFAULT_BASE_URL,
    DEFAULT_CONCURRENCY,
    DEFAULT_MODEL,
    DEFAULT_OVERLAP,
    DEFAULT_RESPONSE_FORMAT,
    DEFAULT_SEGMENT_LENGTH,
    DEFAULT_SUMMARY_MODEL,
    DEFAULT_SUMMARY_PROMPT,
    DEFAULT_TEMPERATURE,
    ENV_PREFIX,
    VALID_RESPONSE_FORMATS,
    get_model_price_per_minute,
)
from .exporter import TranscriptionExporter
from .progress import ProgressTracker
from .transcriber import AudioTranscriber
from .utils import estimate_cost, find_audio_files, format_duration, setup_logging


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="audio-transcriber",
        description="Professional audio transcription tool using OpenAI-compatible APIs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transcribe a single file
  audio-transcriber --input podcast.mp3

  # Transcribe all files in a directory
  audio-transcriber --input ./audio_files --output-dir ./transcriptions

  # Use local Ollama
  audio-transcriber --input lecture.mp3 \\
    --base-url http://localhost:11434/v1 \\
    --api-key ollama --model whisper

  # Generate SRT subtitles
  audio-transcriber --input video.mp4 --response-format srt

  # Custom segmentation for long files
  audio-transcriber --input podcast.mp3 \\
    --segment-length 900 --overlap 15 --concurrency 6

Environment Variables:
  AUDIO_TRANSCRIBE_API_KEY       API key
  AUDIO_TRANSCRIBE_BASE_URL      API base URL
  AUDIO_TRANSCRIBE_MODEL         Model name
  AUDIO_TRANSCRIBE_OUTPUT_DIR    Output directory
  AUDIO_TRANSCRIBE_SEGMENT_LENGTH  Segment length (seconds)
  AUDIO_TRANSCRIBE_OVERLAP       Overlap (seconds)
  AUDIO_TRANSCRIBE_CONCURRENCY   Parallel jobs

For more information: https://github.com/lucmuss/audio-transcriber
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    # Required arguments
    required = parser.add_argument_group("required arguments")
    required.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Path to audio file or directory",
    )

    # API configuration
    api_group = parser.add_argument_group("API configuration")
    api_group.add_argument(
        "--api-key",
        type=str,
        default=os.getenv(f"{ENV_PREFIX}API_KEY"),
        help=f"API key (or ${ENV_PREFIX}API_KEY env var)",
    )
    api_group.add_argument(
        "--base-url",
        type=str,
        default=os.getenv(f"{ENV_PREFIX}BASE_URL", DEFAULT_BASE_URL),
        help=f"API base URL (default: {DEFAULT_BASE_URL})",
    )
    api_group.add_argument(
        "--model",
        type=str,
        default=os.getenv(f"{ENV_PREFIX}MODEL", DEFAULT_MODEL),
        help=f"Model name (default: {DEFAULT_MODEL})",
    )

    # Output configuration
    output_group = parser.add_argument_group("output configuration")
    output_group.add_argument(
        "-o",
        "--output-dir",
        type=str,
        default=os.getenv(f"{ENV_PREFIX}OUTPUT_DIR", "./transcriptions"),
        help="Output directory for final transcriptions (default: ./transcriptions)",
    )
    output_group.add_argument(
        "--segments-dir",
        type=str,
        default=os.getenv(f"{ENV_PREFIX}SEGMENTS_DIR", "./segments"),
        help="Output directory for temporary segments (default: ./segments)",
    )
    output_group.add_argument(
        "-f",
        "--response-format",
        type=str,
        choices=list(VALID_RESPONSE_FORMATS),
        default=DEFAULT_RESPONSE_FORMAT,
        help=f"Output format (default: {DEFAULT_RESPONSE_FORMAT})",
    )

    # Segmentation parameters
    segment_group = parser.add_argument_group("segmentation parameters")
    segment_group.add_argument(
        "--segment-length",
        type=int,
        default=int(os.getenv(f"{ENV_PREFIX}SEGMENT_LENGTH", str(DEFAULT_SEGMENT_LENGTH))),
        help=f"Segment length in seconds (default: {DEFAULT_SEGMENT_LENGTH})",
    )
    segment_group.add_argument(
        "--overlap",
        type=int,
        default=int(os.getenv(f"{ENV_PREFIX}OVERLAP", str(DEFAULT_OVERLAP))),
        help=f"Overlap between segments in seconds (default: {DEFAULT_OVERLAP})",
    )

    # Transcription parameters
    trans_group = parser.add_argument_group("transcription parameters")
    trans_group.add_argument(
        "--language",
        type=str,
        default=None,
        help="ISO-639-1 language code (e.g., 'en', 'de'). Auto-detect if not set.",
    )
    trans_group.add_argument(
        "--detect-language",
        action="store_true",
        default=True,
        help="Auto-detect language from first segment (default: enabled)",
    )
    trans_group.add_argument(
        "--no-detect-language",
        action="store_false",
        dest="detect_language",
        help="Disable language auto-detection",
    )
    trans_group.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f"Model temperature 0.0-1.0 (default: {DEFAULT_TEMPERATURE})",
    )
    trans_group.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Context prompt for better accuracy (e.g., names, technical terms)",
    )

    # Performance parameters
    perf_group = parser.add_argument_group("performance parameters")
    perf_group.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=int(os.getenv(f"{ENV_PREFIX}CONCURRENCY", str(DEFAULT_CONCURRENCY))),
        help=f"Number of parallel transcriptions (default: {DEFAULT_CONCURRENCY})",
    )

    # Diarization parameters (Speaker Recognition)
    diarization_group = parser.add_argument_group("diarization parameters (speaker recognition)")
    diarization_group.add_argument(
        "--enable-diarization",
        action="store_true",
        help="Enable speaker diarization (automatically uses gpt-4o-transcribe-diarize model)",
    )
    diarization_group.add_argument(
        "--num-speakers",
        type=int,
        default=None,
        help="Expected number of speakers (optional, auto-detect if not set)",
    )
    diarization_group.add_argument(
        "--known-speaker-names",
        type=str,
        nargs="+",
        default=None,
        help="List of known speaker names (e.g., --known-speaker-names Alice Bob)",
    )
    diarization_group.add_argument(
        "--known-speaker-references",
        type=str,
        nargs="+",
        default=None,
        help=(
            "Paths to reference audio files for known speakers "
            "(e.g., --known-speaker-references alice.wav bob.wav)"
        ),
    )

    # Summarization parameters
    summary_group = parser.add_argument_group("summarization parameters")
    summary_group.add_argument(
        "--summarize",
        action="store_true",
        help="Generate a summary of the transcription",
    )
    summary_group.add_argument(
        "--summary-dir",
        type=str,
        default=os.getenv(f"{ENV_PREFIX}SUMMARY_DIR", "./summaries"),
        help="Output directory for summaries (default: ./summaries)",
    )
    summary_group.add_argument(
        "--summary-model",
        type=str,
        default=os.getenv(f"{ENV_PREFIX}SUMMARY_MODEL", DEFAULT_SUMMARY_MODEL),
        help=f"Model for summarization (default: {DEFAULT_SUMMARY_MODEL})",
    )
    summary_group.add_argument(
        "--summary-prompt",
        type=str,
        default=DEFAULT_SUMMARY_PROMPT,
        help="Custom prompt for summary generation",
    )

    # Export parameters
    export_group = parser.add_argument_group("export parameters")
    export_group.add_argument(
        "--export",
        type=str,
        nargs="+",
        choices=["docx", "md", "markdown", "latex", "tex"],
        help="Export transcriptions to additional formats (e.g., --export docx md latex)",
    )
    export_group.add_argument(
        "--export-dir",
        type=str,
        default=os.getenv(f"{ENV_PREFIX}EXPORT_DIR", "./exports"),
        help="Output directory for exports (default: ./exports)",
    )
    export_group.add_argument(
        "--export-title",
        type=str,
        default=None,
        help="Title for exported documents",
    )
    export_group.add_argument(
        "--export-author",
        type=str,
        default=None,
        help="Author name for exported documents",
    )

    # Behavior options
    behavior_group = parser.add_argument_group("behavior options")
    behavior_group.add_argument(
        "--no-keep-segments",
        action="store_false",
        dest="keep_segments",
        help="Delete temporary segment files after processing (segments are kept by default)",
    )
    behavior_group.add_argument(
        "--skip-existing",
        action="store_true",
        help=(
            "Skip files if transcription output already exists "
            "(by default files are re-processed)"
        ),
    )
    behavior_group.add_argument(
        "--analyze-duration",
        action="store_true",
        help="Analyze audio duration before processing (slower, provides better ETA)",
    )
    behavior_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate processing without API calls",
    )
    behavior_group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser


def validate_args(args: argparse.Namespace) -> None:
    """
    Validate command-line arguments.

    Raises:
        SystemExit: If validation fails
    """
    # Check API key
    if not args.dry_run and not args.api_key:
        print("ERROR: API key required. Set --api-key or AUDIO_TRANSCRIBE_API_KEY", file=sys.stderr)
        print("", file=sys.stderr)
        print("Examples:", file=sys.stderr)
        print("  export AUDIO_TRANSCRIBE_API_KEY='sk-...'", file=sys.stderr)
        print("  audio-transcriber --api-key 'sk-...' --input file.mp3", file=sys.stderr)
        sys.exit(1)

    # Check input path
    if not Path(args.input).exists():
        print(f"ERROR: Input path does not exist: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Validate numeric parameters
    if args.segment_length <= 0:
        print(f"ERROR: Segment length must be positive, got {args.segment_length}", file=sys.stderr)
        sys.exit(1)

    if args.overlap < 0 or args.overlap >= args.segment_length:
        print(
            f"ERROR: Overlap must be between 0 and segment length, got {args.overlap}",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.concurrency <= 0:
        print(f"ERROR: Concurrency must be positive, got {args.concurrency}", file=sys.stderr)
        sys.exit(1)

    if not 0.0 <= args.temperature <= 1.0:
        print(
            f"ERROR: Temperature must be between 0 and 1, got {args.temperature}",
            file=sys.stderr,
        )
        sys.exit(1)


def print_summary(results: List[dict], model: str, verbose: bool = False) -> None:
    """Print summary statistics."""
    successful = sum(1 for r in results if r.get("status") == "success")
    skipped = sum(1 for r in results if r.get("status") == "skipped")
    failed = sum(1 for r in results if r.get("status") == "error")

    total_duration = sum(
        r.get("duration_seconds", 0) for r in results if r.get("status") == "success"
    )
    total_segments = sum(r.get("segments", 0) for r in results)
    failed_segments = sum(r.get("failed", 0) for r in results)

    print("\n" + "=" * 70)
    print("TRANSCRIPTION SUMMARY")
    print("=" * 70)
    print(f"Files processed:     {successful}")
    print(f"Files skipped:       {skipped}")
    print(f"Files failed:        {failed}")
    print(f"Total segments:      {total_segments}")
    print(f"Failed segments:     {failed_segments}")

    if total_duration > 0:
        print(f"Total duration:      {format_duration(total_duration)}")
        price_per_minute = get_model_price_per_minute(model)
        cost = estimate_cost(total_duration / 60, price_per_minute)
        print(f"Estimated cost:      ${cost:.4f} (Model: {model})")

    if verbose and results:
        print("\nDetailed results:")
        for r in results:
            status_icon = (
                "✓"
                if r.get("status") == "success"
                else ("⊘" if r.get("status") == "skipped" else "✗")
            )
            print(f"  {status_icon} {Path(r['file']).name} - {r.get('status')}")

    print("=" * 70 + "\n")


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Validate arguments
    validate_args(args)

    # Find audio files
    try:
        audio_files = find_audio_files(args.input)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if not audio_files:
        print(f"ERROR: No audio files found in {args.input}", file=sys.stderr)
        return 1

    print(f"Found {len(audio_files)} audio file(s)")

    # Dry-run mode
    if args.dry_run:
        print("\n*** DRY RUN MODE ***")
        print("Configuration:")
        print(f"  Model:           {args.model}")
        print(f"  Base URL:        {args.base_url}")
        print(f"  Segment length:  {args.segment_length}s")
        print(f"  Overlap:         {args.overlap}s")
        print(f"  Concurrency:     {args.concurrency}")
        print(f"  Format:          {args.response_format}")
        print(f"  Language:        {args.language or 'auto-detect'}")
        print(f"  Output dir:      {args.output_dir}")
        print("\nNo API calls will be made.")
        return 0

    # Initialize transcriber
    transcriber = AudioTranscriber(
        api_key=args.api_key,
        base_url=args.base_url,
        model=args.model,
    )

    # Initialize progress tracker with model-specific pricing
    model_price = get_model_price_per_minute(args.model)
    progress = ProgressTracker(price_per_minute=model_price)
    progress.start()
    progress.set_total_files(len(audio_files))

    # Calculate total duration for better ETA (only if requested)
    if args.analyze_duration:
        print("\n📊 Analysiere Audio-Dateien...")
        total_duration_seconds = 0.0
        for audio_file in audio_files:
            try:
                duration = transcriber.segmenter.get_audio_duration(audio_file)
                total_duration_seconds += duration
            except Exception:
                pass  # Skip if duration cannot be determined

        if total_duration_seconds > 0:
            progress.set_total_duration(total_duration_seconds / 60.0)
            print(f"📁 Gesamtdauer: {format_duration(total_duration_seconds)}")
            print(f"💰 Geschätzte Kosten: ${progress.stats.total_cost:.4f}\n")
    else:
        print("\n💡 Tipp: Nutze --analyze-duration für bessere ETA-Schätzungen\n")

    # Process files
    output_dir = Path(args.output_dir)
    results = []

    from tqdm import tqdm

    with tqdm(
        total=len(audio_files),
        desc="🎵 Dateien",
        unit="file",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
    ) as file_pbar:
        for audio_file in audio_files:
            # Update progress bar description with current file
            file_pbar.set_description(f"🎵 {audio_file.name[:30]}")

            result = transcriber.transcribe_file(
                file_path=audio_file,
                output_dir=output_dir,
                segments_dir=Path(args.segments_dir),
                segment_length=args.segment_length,
                overlap=args.overlap,
                language=args.language,
                detect_language=args.detect_language,
                response_format=args.response_format,
                concurrency=args.concurrency,
                temperature=args.temperature,
                prompt=args.prompt,
                keep_segments=args.keep_segments,
                skip_existing=args.skip_existing,
                enable_diarization=args.enable_diarization,
                num_speakers=args.num_speakers,
                known_speaker_names=args.known_speaker_names,
                known_speaker_references=args.known_speaker_references,
            )
            results.append(result)

            # Update progress tracker
            if result.get("status") == "success":
                duration_min = result.get("duration_seconds", 0) / 60.0
                num_segments = result.get("segments", 0)
                progress.update_file_completed(duration_min, num_segments)
            elif result.get("status") == "error":
                progress.update_file_failed()
            elif result.get("status") == "skipped":
                progress.update_file_skipped()

            # Display live progress stats
            summary = progress.get_summary()
            eta_str = summary["time"]["eta_formatted"]
            throughput_str = summary["throughput"]["formatted"]
            cost_str = f"${summary['cost']['current']:.4f}"

            file_pbar.set_postfix_str(
                f"ETA: {eta_str} | {throughput_str} | Kosten: {cost_str}",
                refresh=True,
            )
            file_pbar.update(1)

            # Generate summary if requested and transcription was successful
            if args.summarize and result.get("status") == "success":
                summary_result = transcriber.summarize_transcription(
                    transcription_file=Path(result["output"]),
                    summary_dir=Path(args.summary_dir),
                    summary_model=args.summary_model,
                    summary_prompt=args.summary_prompt,
                    skip_existing=args.skip_existing,
                )
                result["summary"] = summary_result

            # Export to additional formats if requested
            if args.export and result.get("status") == "success":
                exporter = TranscriptionExporter()
                export_dir = Path(args.export_dir)
                result["exports"] = []

                # Prepare metadata
                from datetime import datetime

                metadata = {
                    "title": args.export_title or audio_file.stem,
                    "author": args.export_author,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "duration": format_duration(result.get("duration_seconds", 0)),
                    "language": result.get("language"),
                    "model": args.model,
                }

                for fmt in args.export:
                    # Determine output filename
                    file_stem = audio_file.stem
                    if fmt in ("md", "markdown"):
                        export_file = export_dir / f"{file_stem}.md"
                    elif fmt == "docx":
                        export_file = export_dir / f"{file_stem}.docx"
                    elif fmt in ("latex", "tex"):
                        export_file = export_dir / f"{file_stem}.tex"
                    else:
                        continue

                    try:
                        export_result = exporter.export(
                            transcription_file=Path(result["output"]),
                            output_file=export_file,
                            export_format=fmt,
                            metadata=metadata,
                        )
                        result["exports"].append(export_result)

                        if export_result.get("status") == "success":
                            print(f"  📄 Exportiert: {export_file.name}")
                    except Exception as e:
                        print(f"  ⚠️  Export {fmt} fehlgeschlagen: {e}")

    # Print detailed progress summary
    progress.print_summary()

    # Print summary
    print_summary(results, model=args.model, verbose=args.verbose)

    # Return exit code
    failed_count = sum(1 for r in results if r.get("status") == "error")
    return 1 if failed_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
