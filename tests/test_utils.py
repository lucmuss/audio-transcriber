"""
Tests for utility functions.
"""

import pytest

from audio_transcriber.utils import (
    estimate_cost,
    find_audio_files,
    format_duration,
    validate_segment_params,
)


class TestFormatDuration:
    """Tests for format_duration function."""

    def test_seconds_only(self):
        assert format_duration(45) == "45s"

    def test_minutes_and_seconds(self):
        assert format_duration(125) == "2m 5s"

    def test_hours_minutes_seconds(self):
        assert format_duration(3665) == "1h 1m 5s"

    def test_zero_duration(self):
        assert format_duration(0) == "0s"

    def test_exact_hour(self):
        assert format_duration(3600) == "1h"

    def test_exact_minute(self):
        assert format_duration(60) == "1m"


class TestEstimateCost:
    """Tests for estimate_cost function."""

    def test_default_price(self):
        cost = estimate_cost(10.0)  # 10 minutes
        assert cost == 0.001  # 10 * 0.0001

    def test_custom_price(self):
        cost = estimate_cost(10.0, price_per_minute=0.0002)
        assert cost == 0.002

    def test_zero_duration(self):
        cost = estimate_cost(0.0)
        assert cost == 0.0


class TestValidateSegmentParams:
    """Tests for validate_segment_params function."""

    def test_valid_params(self):
        # Should not raise
        validate_segment_params(600, 10, 4, 0.0)

    def test_negative_segment_length(self):
        with pytest.raises(ValueError, match="Segment length must be positive"):
            validate_segment_params(-1, 10, 4, 0.0)

    def test_zero_segment_length(self):
        with pytest.raises(ValueError, match="Segment length must be positive"):
            validate_segment_params(0, 10, 4, 0.0)

    def test_negative_overlap(self):
        with pytest.raises(ValueError, match="Overlap must be non-negative"):
            validate_segment_params(600, -1, 4, 0.0)

    def test_overlap_too_large(self):
        with pytest.raises(ValueError, match="Overlap .* must be less than segment length"):
            validate_segment_params(600, 600, 4, 0.0)

    def test_zero_concurrency(self):
        with pytest.raises(ValueError, match="Concurrency must be positive"):
            validate_segment_params(600, 10, 0, 0.0)

    def test_negative_concurrency(self):
        with pytest.raises(ValueError, match="Concurrency must be positive"):
            validate_segment_params(600, 10, -1, 0.0)

    def test_invalid_temperature_low(self):
        with pytest.raises(ValueError, match="Temperature must be between 0 and 1"):
            validate_segment_params(600, 10, 4, -0.1)

    def test_invalid_temperature_high(self):
        with pytest.raises(ValueError, match="Temperature must be between 0 and 1"):
            validate_segment_params(600, 10, 4, 1.1)

    def test_valid_temperature_boundaries(self):
        # Should not raise
        validate_segment_params(600, 10, 4, 0.0)
        validate_segment_params(600, 10, 4, 1.0)


class TestFindAudioFiles:
    """Tests for find_audio_files function."""

    def test_nonexistent_path(self):
        with pytest.raises(FileNotFoundError):
            find_audio_files("/nonexistent/path")

    def test_single_file(self, tmp_path):
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()
        files = find_audio_files(str(audio_file))
        assert len(files) == 1
        assert files[0] == audio_file

    def test_unsupported_file(self, tmp_path):
        text_file = tmp_path / "test.txt"
        text_file.touch()
        files = find_audio_files(str(text_file))
        assert len(files) == 0

    def test_directory_with_audio_files(self, tmp_path):
        (tmp_path / "audio1.mp3").touch()
        (tmp_path / "audio2.wav").touch()
        (tmp_path / "readme.txt").touch()

        files = find_audio_files(str(tmp_path))
        assert len(files) == 2
        assert all(f.suffix in [".mp3", ".wav"] for f in files)

    def test_nested_directories(self, tmp_path):
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "audio1.mp3").touch()
        (subdir / "audio2.flac").touch()

        files = find_audio_files(str(tmp_path))
        assert len(files) == 2

    def test_empty_directory(self, tmp_path):
        files = find_audio_files(str(tmp_path))
        assert len(files) == 0
