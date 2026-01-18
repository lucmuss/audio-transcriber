"""
Utility functions for Audio Transcriber.
"""

import logging
from pathlib import Path
from typing import List, Optional, Union

from .constants import SUPPORTED_FORMATS

logger = logging.getLogger(__name__)


def find_audio_files(path: Union[str, Path]) -> List[Path]:
    """
    Recursively find all supported audio files in a path.

    Args:
        path: Path to audio file or directory

    Returns:
        List of Path objects for found audio files

    Raises:
        FileNotFoundError: If path doesn't exist
    """
    path_obj = Path(path)

    if not path_obj.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    if path_obj.is_file():
        if path_obj.suffix.lower() in SUPPORTED_FORMATS:
            logger.info(f"Found single audio file: {path_obj.name}")
            return [path_obj]
        else:
            logger.warning(
                f"Unsupported file format: {path_obj.suffix}. "
                f"Supported formats: {', '.join(sorted(SUPPORTED_FORMATS))}"
            )
            return []

    if path_obj.is_dir():
        audio_files = [
            f for f in path_obj.rglob("*") if f.is_file() and f.suffix.lower() in SUPPORTED_FORMATS
        ]
        logger.info(f"Found {len(audio_files)} audio files in {path}")
        return sorted(audio_files)

    return []


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "1h 23m 45s")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def estimate_cost(duration_minutes: float, price_per_minute: float = 0.0001) -> float:
    """
    Estimate transcription cost based on audio duration.

    Args:
        duration_minutes: Audio duration in minutes
        price_per_minute: Cost per minute (default: OpenAI Whisper pricing)

    Returns:
        Estimated cost in USD
    """
    return duration_minutes * price_per_minute


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging for the application.

    Args:
        verbose: Enable debug logging if True
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler()],
    )


def validate_segment_params(
    segment_length: int,
    overlap: int,
    concurrency: int,
    temperature: float,
) -> None:
    """
    Validate segmentation parameters.

    Args:
        segment_length: Segment length in seconds
        overlap: Overlap between segments in seconds
        concurrency: Number of concurrent transcriptions
        temperature: Model temperature

    Raises:
        ValueError: If any parameter is invalid
    """
    if segment_length <= 0:
        raise ValueError(f"Segment length must be positive, got {segment_length}")

    if overlap < 0:
        raise ValueError(f"Overlap must be non-negative, got {overlap}")

    if overlap >= segment_length:
        raise ValueError(
            f"Overlap ({overlap}s) must be less than segment length ({segment_length}s)"
        )

    if concurrency <= 0:
        raise ValueError(f"Concurrency must be positive, got {concurrency}")

    if not 0.0 <= temperature <= 1.0:
        raise ValueError(f"Temperature must be between 0 and 1, got {temperature}")
