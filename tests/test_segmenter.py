"""
Tests for audio segmentation module.
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from pydub import AudioSegment

from audio_transcriber.constants import DEFAULT_BITRATE, DEFAULT_CHANNELS, DEFAULT_SAMPLE_RATE
from audio_transcriber.segmenter import AudioSegmenter


class TestAudioSegmenter:
    """Tests for AudioSegmenter class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.segmenter = AudioSegmenter()

    def test_init_default_values(self):
        """Test initialization with default values."""
        segmenter = AudioSegmenter()
        assert segmenter.sample_rate == DEFAULT_SAMPLE_RATE
        assert segmenter.channels == DEFAULT_CHANNELS
        assert segmenter.bitrate == DEFAULT_BITRATE

    def test_init_custom_values(self):
        """Test initialization with custom values."""
        segmenter = AudioSegmenter(sample_rate=44100, channels=2, bitrate="128k")
        assert segmenter.sample_rate == 44100
        assert segmenter.channels == 2
        assert segmenter.bitrate == "128k"

    def test_segment_audio_file_not_found(self, tmp_path):
        """Test segment_audio with non-existent file."""
        non_existent = tmp_path / "does_not_exist.mp3"
        output_dir = tmp_path / "output"

        with pytest.raises(FileNotFoundError, match="Audio file not found"):
            self.segmenter.segment_audio(non_existent, 60, 10, output_dir)

    @patch("audio_transcriber.segmenter.AudioSegment")
    def test_segment_audio_load_failure(self, mock_audio_segment, tmp_path):
        """Test segment_audio when audio loading fails."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()
        output_dir = tmp_path / "output"

        mock_audio_segment.from_file.side_effect = Exception("Failed to load")

        with pytest.raises(RuntimeError, match="Failed to load audio file"):
            self.segmenter.segment_audio(audio_file, 60, 10, output_dir)

    @patch("audio_transcriber.segmenter.AudioSegment")
    def test_segment_audio_single_segment(self, mock_audio_segment, tmp_path):
        """Test segmentation of short audio (single segment)."""
        audio_file = tmp_path / "short.mp3"
        audio_file.touch()
        output_dir = tmp_path / "segments"

        # Mock 30 second audio (less than default segment length)
        mock_audio = MagicMock()
        mock_audio.__len__.return_value = 30000  # 30 seconds in ms
        mock_audio.frame_rate = 44100
        mock_audio.channels = 2
        mock_audio.__getitem__ = Mock(return_value=mock_audio)
        mock_audio.set_frame_rate.return_value = mock_audio
        mock_audio.set_channels.return_value = mock_audio

        mock_audio_segment.from_file.return_value = mock_audio

        segments = self.segmenter.segment_audio(audio_file, 60, 10, output_dir)

        assert len(segments) == 1
        assert segments[0].name == "short_seg001.mp3"
        assert output_dir.exists()

    @patch("audio_transcriber.segmenter.AudioSegment")
    def test_segment_audio_multiple_segments(self, mock_audio_segment, tmp_path):
        """Test segmentation of long audio into multiple segments."""
        audio_file = tmp_path / "long.mp3"
        audio_file.touch()
        output_dir = tmp_path / "segments"

        # Mock 180 second audio (3 minutes)
        mock_audio = MagicMock()
        mock_audio.__len__.return_value = 180000  # 180 seconds
        mock_audio.frame_rate = 16000
        mock_audio.channels = 1
        mock_audio.__getitem__ = Mock(return_value=mock_audio)
        mock_audio.set_frame_rate.return_value = mock_audio
        mock_audio.set_channels.return_value = mock_audio

        mock_audio_segment.from_file.return_value = mock_audio

        segments = self.segmenter.segment_audio(audio_file, 60, 10, output_dir)

        # With 60s segments and 10s overlap (50s step), 180s should create ~4 segments
        assert len(segments) >= 3
        assert all(seg.suffix == ".mp3" for seg in segments)

    @patch("audio_transcriber.segmenter.AudioSegment")
    def test_segment_audio_with_overlap(self, mock_audio_segment, tmp_path):
        """Test that overlap is properly calculated."""
        audio_file = tmp_path / "audio.mp3"
        audio_file.touch()
        output_dir = tmp_path / "segments"

        mock_audio = MagicMock()
        mock_audio.__len__.return_value = 120000  # 120 seconds
        mock_audio.frame_rate = 16000
        mock_audio.channels = 1

        # Track segment boundaries
        segment_calls = []

        def mock_getitem(self, key):
            segment_calls.append(key)
            return mock_audio

        mock_audio.__getitem__ = mock_getitem
        mock_audio.set_frame_rate.return_value = mock_audio
        mock_audio.set_channels.return_value = mock_audio

        mock_audio_segment.from_file.return_value = mock_audio

        self.segmenter.segment_audio(audio_file, 60, 15, output_dir)

        # Verify overlapping: with 60s segments and 15s overlap
        # First segment: 0-60000ms
        # Second segment should start at 45000ms (60000 - 15000 overlap)
        assert len(segment_calls) >= 2
        if len(segment_calls) >= 2:
            # Check that second segment starts before first ends
            assert segment_calls[1].start < 60000

    @patch("audio_transcriber.segmenter.AudioSegment")
    def test_segment_audio_export_failure(self, mock_audio_segment, tmp_path):
        """Test handling of export failures."""
        audio_file = tmp_path / "audio.mp3"
        audio_file.touch()
        output_dir = tmp_path / "segments"

        mock_audio = MagicMock()
        mock_audio.__len__.return_value = 30000
        mock_audio.frame_rate = 16000
        mock_audio.channels = 1
        mock_audio.__getitem__ = Mock(return_value=mock_audio)
        mock_audio.set_frame_rate.return_value = mock_audio
        mock_audio.set_channels.return_value = mock_audio
        mock_audio.export.side_effect = Exception("Export failed")

        mock_audio_segment.from_file.return_value = mock_audio

        with pytest.raises(RuntimeError, match="Failed to export segment"):
            self.segmenter.segment_audio(audio_file, 60, 10, output_dir)

    @patch("audio_transcriber.segmenter.AudioSegment")
    def test_segment_audio_creates_output_dir(self, mock_audio_segment, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        audio_file = tmp_path / "audio.mp3"
        audio_file.touch()
        output_dir = tmp_path / "nested" / "output" / "dir"

        mock_audio = MagicMock()
        mock_audio.__len__.return_value = 30000
        mock_audio.frame_rate = 16000
        mock_audio.channels = 1
        mock_audio.__getitem__ = Mock(return_value=mock_audio)
        mock_audio.set_frame_rate.return_value = mock_audio
        mock_audio.set_channels.return_value = mock_audio

        mock_audio_segment.from_file.return_value = mock_audio

        assert not output_dir.exists()
        self.segmenter.segment_audio(audio_file, 60, 10, output_dir)
        assert output_dir.exists()

    @patch("audio_transcriber.segmenter.AudioSegment")
    def test_segment_audio_different_formats(self, mock_audio_segment, tmp_path):
        """Test segmentation with different audio formats."""
        for format_ext in [".mp3", ".wav", ".flac", ".m4a", ".ogg"]:
            audio_file = tmp_path / f"audio{format_ext}"
            audio_file.touch()
            output_dir = tmp_path / "segments"

            mock_audio = MagicMock()
            mock_audio.__len__.return_value = 30000
            mock_audio.frame_rate = 16000
            mock_audio.channels = 1
            mock_audio.__getitem__ = Mock(return_value=mock_audio)
            mock_audio.set_frame_rate.return_value = mock_audio
            mock_audio.set_channels.return_value = mock_audio

            mock_audio_segment.from_file.return_value = mock_audio

            segments = self.segmenter.segment_audio(audio_file, 60, 10, output_dir)
            assert len(segments) > 0
            assert all(seg.suffix == ".mp3" for seg in segments)

    def test_get_audio_duration_file_not_found(self, tmp_path):
        """Test get_audio_duration with non-existent file."""
        non_existent = tmp_path / "missing.mp3"

        with pytest.raises(FileNotFoundError, match="Audio file not found"):
            self.segmenter.get_audio_duration(non_existent)

    @patch("audio_transcriber.segmenter.AudioSegment")
    def test_get_audio_duration_load_failure(self, mock_audio_segment, tmp_path):
        """Test get_audio_duration when loading fails."""
        audio_file = tmp_path / "bad.mp3"
        audio_file.touch()

        mock_audio_segment.from_file.side_effect = Exception("Corrupt file")

        with pytest.raises(RuntimeError, match="Failed to load audio file"):
            self.segmenter.get_audio_duration(audio_file)

    @patch("audio_transcriber.segmenter.AudioSegment")
    def test_get_audio_duration_success(self, mock_audio_segment, tmp_path):
        """Test successful audio duration retrieval."""
        audio_file = tmp_path / "audio.mp3"
        audio_file.touch()

        mock_audio = MagicMock()
        mock_audio.__len__.return_value = 123456  # milliseconds

        mock_audio_segment.from_file.return_value = mock_audio

        duration = self.segmenter.get_audio_duration(audio_file)

        assert duration == pytest.approx(123.456, rel=0.001)

    @patch("audio_transcriber.segmenter.AudioSegment")
    def test_get_audio_duration_various_lengths(self, mock_audio_segment, tmp_path):
        """Test duration calculation for various audio lengths."""
        audio_file = tmp_path / "audio.mp3"
        audio_file.touch()

        test_cases = [
            (0, 0.0),  # 0 seconds
            (1000, 1.0),  # 1 second
            (60000, 60.0),  # 1 minute
            (3600000, 3600.0),  # 1 hour
        ]

        for ms, expected_seconds in test_cases:
            mock_audio = MagicMock()
            mock_audio.__len__.return_value = ms
            mock_audio_segment.from_file.return_value = mock_audio

            duration = self.segmenter.get_audio_duration(audio_file)
            assert duration == pytest.approx(expected_seconds)

    @patch("audio_transcriber.segmenter.AudioSegment")
    def test_segment_naming_format(self, mock_audio_segment, tmp_path):
        """Test that segment files are named correctly with padding."""
        audio_file = tmp_path / "my_audio_file.mp3"
        audio_file.touch()
        output_dir = tmp_path / "segments"

        mock_audio = MagicMock()
        mock_audio.__len__.return_value = 180000  # Long enough for multiple segments
        mock_audio.frame_rate = 16000
        mock_audio.channels = 1
        mock_audio.__getitem__ = Mock(return_value=mock_audio)
        mock_audio.set_frame_rate.return_value = mock_audio
        mock_audio.set_channels.return_value = mock_audio

        mock_audio_segment.from_file.return_value = mock_audio

        segments = self.segmenter.segment_audio(audio_file, 60, 10, output_dir)

        # Check naming pattern: {stem}_seg{num:03d}.mp3
        for i, seg in enumerate(segments, 1):
            expected_name = f"my_audio_file_seg{i:03d}.mp3"
            assert seg.name == expected_name

    @patch("audio_transcriber.segmenter.AudioSegment")
    def test_segment_audio_normalization(self, mock_audio_segment, tmp_path):
        """Test that audio is normalized to target sample rate and channels."""
        audio_file = tmp_path / "audio.mp3"
        audio_file.touch()
        output_dir = tmp_path / "segments"

        # Mock audio with different specs than target
        mock_audio = MagicMock()
        mock_audio.__len__.return_value = 30000
        mock_audio.frame_rate = 44100  # Different from default 16000
        mock_audio.channels = 2  # Different from default 1

        mock_normalized = MagicMock()
        mock_audio.__getitem__ = Mock(return_value=mock_audio)
        mock_audio.set_frame_rate.return_value = mock_normalized
        mock_normalized.set_channels.return_value = mock_normalized

        mock_audio_segment.from_file.return_value = mock_audio

        self.segmenter.segment_audio(audio_file, 60, 10, output_dir)

        # Verify normalization was called
        mock_audio.set_frame_rate.assert_called_with(DEFAULT_SAMPLE_RATE)
        mock_normalized.set_channels.assert_called_with(DEFAULT_CHANNELS)

    @patch("audio_transcriber.segmenter.AudioSegment")
    def test_segment_audio_no_normalization_needed(self, mock_audio_segment, tmp_path):
        """Test that normalization is skipped when not needed."""
        audio_file = tmp_path / "audio.mp3"
        audio_file.touch()
        output_dir = tmp_path / "segments"

        # Mock audio already at target specs
        mock_audio = MagicMock()
        mock_audio.__len__.return_value = 30000
        mock_audio.frame_rate = DEFAULT_SAMPLE_RATE
        mock_audio.channels = DEFAULT_CHANNELS
        mock_audio.__getitem__ = Mock(return_value=mock_audio)

        mock_audio_segment.from_file.return_value = mock_audio

        self.segmenter.segment_audio(audio_file, 60, 10, output_dir)

        # Normalization methods should not be called
        mock_audio.set_frame_rate.assert_not_called()
