"""
Audio segmentation module for creating processable chunks.
"""

import logging
from pathlib import Path
from typing import List

from pydub import AudioSegment

from .constants import DEFAULT_BITRATE, DEFAULT_CHANNELS, DEFAULT_SAMPLE_RATE
from .utils import format_duration

logger = logging.getLogger(__name__)


class AudioSegmenter:
    """
    Handles audio file segmentation with overlap for seamless transcription.
    """

    def __init__(
        self,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        channels: int = DEFAULT_CHANNELS,
        bitrate: str = DEFAULT_BITRATE,
    ):
        """
        Initialize audio segmenter.

        Args:
            sample_rate: Target sample rate in Hz (default: 16000)
            channels: Number of audio channels (default: 1 for mono)
            bitrate: Output bitrate for MP3 encoding (default: "64k")
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.bitrate = bitrate

    def segment_audio(
        self,
        file_path: Path,
        segment_length_seconds: int,
        overlap_seconds: int,
        output_dir: Path,
    ) -> List[Path]:
        """
        Segment audio file into overlapping chunks.

        Args:
            file_path: Path to input audio file
            segment_length_seconds: Length of each segment in seconds
            overlap_seconds: Overlap between consecutive segments in seconds
            output_dir: Directory to save segment files

        Returns:
            List of paths to created segment files

        Raises:
            FileNotFoundError: If input file doesn't exist
            RuntimeError: If audio loading or segmentation fails
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        logger.info(f"Loading audio file: {file_path.name}")

        try:
            audio = AudioSegment.from_file(str(file_path))
        except Exception as e:
            raise RuntimeError(f"Failed to load audio file: {e}") from e

        total_duration_ms = len(audio)
        total_duration_seconds = total_duration_ms / 1000

        logger.info(f"Audio duration: {format_duration(total_duration_seconds)}")
        logger.debug(
            f"Original format - Sample rate: {audio.frame_rate}Hz, Channels: {audio.channels}"
        )

        # Calculate segmentation parameters
        segment_length_ms = segment_length_seconds * 1000
        overlap_ms = overlap_seconds * 1000
        step_ms = segment_length_ms - overlap_ms

        num_segments = max(1, int((total_duration_ms - overlap_ms) / step_ms + 0.5))
        logger.info(
            f"Creating {num_segments} segments "
            f"(length: {segment_length_seconds}s, overlap: {overlap_seconds}s)"
        )

        output_dir.mkdir(parents=True, exist_ok=True)
        segment_files = []
        segment_num = 1
        start_ms = 0

        while start_ms < total_duration_ms:
            end_ms = min(start_ms + segment_length_ms, total_duration_ms)
            segment = audio[start_ms:end_ms]

            # Optimize for transcription: normalize to mono 16kHz
            if segment.frame_rate != self.sample_rate or segment.channels != self.channels:
                segment = segment.set_frame_rate(self.sample_rate).set_channels(self.channels)

            # Export as optimized MP3
            file_stem = file_path.stem
            segment_file = output_dir / f"{file_stem}_seg{segment_num:03d}.mp3"

            try:
                segment.export(
                    str(segment_file),
                    format="mp3",
                    bitrate=self.bitrate,
                    parameters=["-q:a", "9"],  # VBR quality
                )
            except Exception as e:
                raise RuntimeError(f"Failed to export segment {segment_num}: {e}") from e

            segment_files.append(segment_file)

            segment_duration = (end_ms - start_ms) / 1000
            logger.debug(
                f"Created segment {segment_num}/{num_segments}: "
                f"{segment_file.name} ({format_duration(segment_duration)})"
            )

            segment_num += 1
            start_ms += step_ms

            if end_ms >= total_duration_ms:
                break

        logger.info(f"Successfully created {len(segment_files)} segment files")
        return segment_files

    def get_audio_duration(self, file_path: Path) -> float:
        """
        Get audio file duration in seconds.

        Args:
            file_path: Path to audio file

        Returns:
            Duration in seconds

        Raises:
            FileNotFoundError: If file doesn't exist
            RuntimeError: If audio loading fails
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        try:
            audio = AudioSegment.from_file(str(file_path))
            return len(audio) / 1000.0
        except Exception as e:
            raise RuntimeError(f"Failed to load audio file: {e}") from e
