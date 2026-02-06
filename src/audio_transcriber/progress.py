"""
Progress tracking and ETA calculation for Audio Transcriber.
"""

import logging
import time
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ProgressStats:
    """Statistics for progress tracking."""

    total_files: int = 0
    completed_files: int = 0
    failed_files: int = 0
    skipped_files: int = 0

    total_segments: int = 0
    completed_segments: int = 0
    failed_segments: int = 0

    total_duration_minutes: float = 0.0
    processed_duration_minutes: float = 0.0

    total_cost: float = 0.0

    start_time: float = 0.0
    last_update_time: float = 0.0

    def __post_init__(self):
        """Initialize timestamps."""
        if self.start_time == 0.0:
            self.start_time = time.time()
            self.last_update_time = self.start_time


class ProgressTracker:
    """
    Track transcription progress with ETA and throughput calculation.

    This class provides real-time progress tracking including:
    - Elapsed time
    - Estimated time to completion (ETA)
    - Throughput (minutes of audio per hour)
    - Cost tracking in real-time
    """

    def __init__(self, price_per_minute: float = 0.0001):
        """
        Initialize progress tracker.

        Args:
            price_per_minute: Cost per minute of audio (default: OpenAI Whisper pricing)
        """
        self.stats = ProgressStats()
        self.price_per_minute = price_per_minute

    def start(self) -> None:
        """Start progress tracking."""
        self.stats.start_time = time.time()
        self.stats.last_update_time = self.stats.start_time
        logger.debug("Progress tracking started")

    def set_total_files(self, total: int) -> None:
        """
        Set total number of files to process.

        Args:
            total: Total number of files
        """
        self.stats.total_files = total
        logger.debug(f"Total files set to {total}")

    def set_total_duration(self, duration_minutes: float) -> None:
        """
        Set total duration of all audio files.

        Args:
            duration_minutes: Total duration in minutes
        """
        self.stats.total_duration_minutes = duration_minutes
        self.stats.total_cost = duration_minutes * self.price_per_minute
        logger.debug(f"Total duration set to {duration_minutes:.2f} minutes")

    def update_file_completed(self, duration_minutes: float, num_segments: int) -> None:
        """
        Mark a file as completed.

        Args:
            duration_minutes: Duration of processed file in minutes
            num_segments: Number of segments in the file
        """
        self.stats.completed_files += 1
        self.stats.processed_duration_minutes += duration_minutes
        self.stats.total_segments += num_segments
        self.stats.completed_segments += num_segments
        self.stats.last_update_time = time.time()
        logger.debug(f"File completed: {self.stats.completed_files}/{self.stats.total_files}")

    def update_file_failed(self, num_segments: int = 0) -> None:
        """
        Mark a file as failed.

        Args:
            num_segments: Number of segments that failed
        """
        self.stats.failed_files += 1
        self.stats.failed_segments += num_segments
        self.stats.last_update_time = time.time()
        logger.debug(f"File failed: {self.stats.failed_files}")

    def update_file_skipped(self) -> None:
        """Mark a file as skipped."""
        self.stats.skipped_files += 1
        self.stats.last_update_time = time.time()
        logger.debug(f"File skipped: {self.stats.skipped_files}")

    def update_segment_completed(self) -> None:
        """Mark a segment as completed."""
        self.stats.completed_segments += 1
        self.stats.last_update_time = time.time()

    def update_segment_failed(self) -> None:
        """Mark a segment as failed."""
        self.stats.failed_segments += 1
        self.stats.last_update_time = time.time()

    def get_elapsed_time(self) -> float:
        """
        Get elapsed time since start.

        Returns:
            Elapsed time in seconds
        """
        return time.time() - self.stats.start_time

    def get_eta_seconds(self) -> Optional[float]:
        """
        Calculate estimated time to completion (ETA).

        Returns:
            ETA in seconds, or None if cannot be calculated
        """
        if self.stats.processed_duration_minutes == 0:
            return None

        elapsed = self.get_elapsed_time()
        remaining_duration = (
            self.stats.total_duration_minutes - self.stats.processed_duration_minutes
        )

        if remaining_duration <= 0:
            return 0.0

        # Calculate processing rate (seconds per minute of audio)
        processing_rate = elapsed / self.stats.processed_duration_minutes

        # Estimate remaining time
        eta = remaining_duration * processing_rate

        return eta

    def get_throughput(self) -> Optional[float]:
        """
        Calculate throughput in minutes of audio per hour.

        Returns:
            Throughput value, or None if cannot be calculated
        """
        elapsed = self.get_elapsed_time()

        if elapsed == 0:
            return None

        # Minutes of audio processed per second
        rate_per_second = self.stats.processed_duration_minutes / elapsed

        # Convert to minutes per hour
        throughput = rate_per_second * 3600

        return throughput

    def get_current_cost(self) -> float:
        """
        Get current accumulated cost.

        Returns:
            Cost in USD
        """
        return self.stats.processed_duration_minutes * self.price_per_minute

    def get_progress_percentage(self) -> float:
        """
        Get overall progress percentage.

        Returns:
            Progress percentage (0-100)
        """
        if self.stats.total_files == 0:
            return 0.0

        completed = self.stats.completed_files + self.stats.skipped_files
        return (completed / self.stats.total_files) * 100

    def get_segment_progress_percentage(self) -> float:
        """
        Get segment progress percentage for current file.

        Returns:
            Progress percentage (0-100)
        """
        if self.stats.total_segments == 0:
            return 0.0

        return (self.stats.completed_segments / self.stats.total_segments) * 100

    def format_eta(self, eta_seconds: Optional[float]) -> str:
        """
        Format ETA to human-readable string.

        Args:
            eta_seconds: ETA in seconds

        Returns:
            Formatted string (e.g., "1h 23m 45s" or "unknown")
        """
        if eta_seconds is None:
            return "unbekannt"

        hours = int(eta_seconds // 3600)
        minutes = int((eta_seconds % 3600) // 60)
        seconds = int(eta_seconds % 60)

        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")

        return " ".join(parts)

    def format_throughput(self, throughput: Optional[float]) -> str:
        """
        Format throughput to human-readable string.

        Args:
            throughput: Throughput in minutes/hour

        Returns:
            Formatted string (e.g., "120.5 min/h")
        """
        if throughput is None:
            return "0.0 min/h"

        return f"{throughput:.1f} min/h"

    def get_summary(self) -> dict:
        """
        Get complete progress summary.

        Returns:
            Dictionary with all progress information
        """
        elapsed = self.get_elapsed_time()
        eta = self.get_eta_seconds()
        throughput = self.get_throughput()
        current_cost = self.get_current_cost()

        return {
            "files": {
                "total": self.stats.total_files,
                "completed": self.stats.completed_files,
                "failed": self.stats.failed_files,
                "skipped": self.stats.skipped_files,
                "progress_pct": self.get_progress_percentage(),
            },
            "segments": {
                "total": self.stats.total_segments,
                "completed": self.stats.completed_segments,
                "failed": self.stats.failed_segments,
                "progress_pct": self.get_segment_progress_percentage(),
            },
            "time": {
                "elapsed_seconds": elapsed,
                "elapsed_formatted": self.format_eta(elapsed),
                "eta_seconds": eta,
                "eta_formatted": self.format_eta(eta),
            },
            "throughput": {
                "value": throughput,
                "formatted": self.format_throughput(throughput),
            },
            "cost": {
                "current": current_cost,
                "total_estimated": self.stats.total_cost,
                "remaining_estimated": self.stats.total_cost - current_cost,
            },
            "duration": {
                "processed_minutes": self.stats.processed_duration_minutes,
                "total_minutes": self.stats.total_duration_minutes,
                "remaining_minutes": self.stats.total_duration_minutes
                - self.stats.processed_duration_minutes,
            },
        }

    def print_summary(self) -> None:
        """Print progress summary to console."""
        summary = self.get_summary()

        print("\n" + "=" * 70)
        print("FORTSCHRITT")
        print("=" * 70)

        # Files
        print(
            f"Dateien:  {summary['files']['completed']}/{summary['files']['total']} "
            f"({summary['files']['progress_pct']:.1f}%)"
        )
        if summary["files"]["failed"] > 0:
            print(f"Fehler:   {summary['files']['failed']}")
        if summary["files"]["skipped"] > 0:
            print(f"Übersprungen: {summary['files']['skipped']}")

        # Segments
        if summary["segments"]["total"] > 0:
            print(
                f"Segmente: {summary['segments']['completed']}/{summary['segments']['total']} "
                f"({summary['segments']['progress_pct']:.1f}%)"
            )

        # Time
        print(f"\nVergangen: {summary['time']['elapsed_formatted']}")
        if summary["time"]["eta_seconds"] is not None:
            print(f"ETA:       {summary['time']['eta_formatted']}")

        # Throughput
        if summary["throughput"]["value"] is not None:
            print(f"Durchsatz: {summary['throughput']['formatted']}")

        # Cost
        print(
            f"\nKosten:    ${summary['cost']['current']:.4f} / "
            f"${summary['cost']['total_estimated']:.4f}"
        )
        print(f"Verbleibend: ${summary['cost']['remaining_estimated']:.4f}")

        print("=" * 70)
