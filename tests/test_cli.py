"""
Tests for command-line interface.
"""

import sys
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from audio_transcriber.cli import create_parser, main, print_summary, validate_args
from audio_transcriber.constants import (
    DEFAULT_BASE_URL,
    DEFAULT_CONCURRENCY,
    DEFAULT_MODEL,
    DEFAULT_OVERLAP,
    DEFAULT_RESPONSE_FORMAT,
    DEFAULT_SEGMENT_LENGTH,
    DEFAULT_TEMPERATURE,
)


class TestCreateParser:
    """Tests for argument parser creation."""

    def test_parser_creation(self):
        """Test that parser is created successfully."""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "audio-transcriber"

    def test_required_arguments(self):
        """Test that required arguments are enforced."""
        parser = create_parser()

        # Missing --input should fail
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_input_argument(self):
        """Test input argument parsing."""
        parser = create_parser()
        args = parser.parse_args(["--input", "test.mp3"])

        assert args.input == "test.mp3"

    def test_api_key_argument(self):
        """Test API key argument parsing."""
        parser = create_parser()
        args = parser.parse_args(["--input", "test.mp3", "--api-key", "sk-test"])

        assert args.api_key == "sk-test"

    def test_base_url_argument(self):
        """Test base URL argument parsing."""
        parser = create_parser()
        args = parser.parse_args(["--input", "test.mp3", "--base-url", "http://custom.api/v1"])

        assert args.base_url == "http://custom.api/v1"

    def test_model_argument(self):
        """Test model argument parsing."""
        parser = create_parser()
        args = parser.parse_args(["--input", "test.mp3", "--model", "custom-model"])

        assert args.model == "custom-model"

    def test_output_dir_argument(self):
        """Test output directory argument parsing."""
        parser = create_parser()
        args = parser.parse_args(["--input", "test.mp3", "-o", "./output"])

        assert args.output_dir == "./output"

    def test_segments_dir_argument(self):
        """Test segments directory argument parsing."""
        parser = create_parser()
        args = parser.parse_args(["--input", "test.mp3", "--segments-dir", "./segs"])

        assert args.segments_dir == "./segs"

    def test_response_format_argument(self):
        """Test response format argument parsing."""
        parser = create_parser()

        for fmt in ["text", "json", "srt", "vtt", "verbose_json"]:
            args = parser.parse_args(["--input", "test.mp3", "-f", fmt])
            assert args.response_format == fmt

    def test_invalid_response_format(self):
        """Test that invalid format is rejected."""
        parser = create_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["--input", "test.mp3", "-f", "invalid"])

    def test_segment_length_argument(self):
        """Test segment length argument parsing."""
        parser = create_parser()
        args = parser.parse_args(["--input", "test.mp3", "--segment-length", "900"])

        assert args.segment_length == 900

    def test_overlap_argument(self):
        """Test overlap argument parsing."""
        parser = create_parser()
        args = parser.parse_args(["--input", "test.mp3", "--overlap", "15"])

        assert args.overlap == 15

    def test_language_argument(self):
        """Test language argument parsing."""
        parser = create_parser()
        args = parser.parse_args(["--input", "test.mp3", "--language", "de"])

        assert args.language == "de"

    def test_detect_language_flags(self):
        """Test language detection flags."""
        parser = create_parser()

        # Default should be True
        args = parser.parse_args(["--input", "test.mp3"])
        assert args.detect_language is True

        # --detect-language
        args = parser.parse_args(["--input", "test.mp3", "--detect-language"])
        assert args.detect_language is True

        # --no-detect-language
        args = parser.parse_args(["--input", "test.mp3", "--no-detect-language"])
        assert args.detect_language is False

    def test_temperature_argument(self):
        """Test temperature argument parsing."""
        parser = create_parser()
        args = parser.parse_args(["--input", "test.mp3", "--temperature", "0.5"])

        assert args.temperature == 0.5

    def test_prompt_argument(self):
        """Test prompt argument parsing."""
        parser = create_parser()
        args = parser.parse_args(["--input", "test.mp3", "--prompt", "Technical terms"])

        assert args.prompt == "Technical terms"

    def test_concurrency_argument(self):
        """Test concurrency argument parsing."""
        parser = create_parser()
        args = parser.parse_args(["--input", "test.mp3", "-c", "8"])

        assert args.concurrency == 8

    def test_keep_segments_flag(self):
        """Test keep segments flag."""
        parser = create_parser()

        # Default is True (changed from False)
        args = parser.parse_args(["--input", "test.mp3"])
        assert args.keep_segments is True

        # With --no-keep-segments flag
        args = parser.parse_args(["--input", "test.mp3", "--no-keep-segments"])
        assert args.keep_segments is False

    def test_skip_existing_flag(self):
        """Test skip existing flag."""
        parser = create_parser()

        # Default is False (changed from True)
        args = parser.parse_args(["--input", "test.mp3"])
        assert args.skip_existing is False

        # --skip-existing
        args = parser.parse_args(["--input", "test.mp3", "--skip-existing"])
        assert args.skip_existing is True

    def test_dry_run_flag(self):
        """Test dry run flag."""
        parser = create_parser()

        args = parser.parse_args(["--input", "test.mp3"])
        assert args.dry_run is False

        args = parser.parse_args(["--input", "test.mp3", "--dry-run"])
        assert args.dry_run is True

    def test_verbose_flag(self):
        """Test verbose flag."""
        parser = create_parser()

        args = parser.parse_args(["--input", "test.mp3"])
        assert args.verbose is False

        args = parser.parse_args(["--input", "test.mp3", "-v"])
        assert args.verbose is True

    def test_version_flag(self):
        """Test version flag."""
        parser = create_parser()

        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])

        # --version exits with code 0
        assert exc_info.value.code == 0

    def test_default_values(self):
        """Test default values are set correctly."""
        parser = create_parser()
        args = parser.parse_args(["--input", "test.mp3"])

        assert args.output_dir == "./transcriptions"
        assert args.segments_dir == "./segments"
        assert args.response_format == DEFAULT_RESPONSE_FORMAT
        assert args.segment_length == DEFAULT_SEGMENT_LENGTH
        assert args.overlap == DEFAULT_OVERLAP
        assert args.temperature == DEFAULT_TEMPERATURE
        assert args.concurrency == DEFAULT_CONCURRENCY


class TestValidateArgs:
    """Tests for argument validation."""

    def test_validate_missing_api_key(self, tmp_path):
        """Test validation fails without API key."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()

        parser = create_parser()
        args = parser.parse_args(["--input", str(audio_file)])
        args.api_key = None
        args.dry_run = False

        with pytest.raises(SystemExit) as exc_info:
            validate_args(args)

        assert exc_info.value.code == 1

    def test_validate_dry_run_without_api_key(self, tmp_path):
        """Test validation passes in dry-run mode without API key."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()

        parser = create_parser()
        args = parser.parse_args(["--input", str(audio_file), "--dry-run"])
        args.api_key = None

        # Should not raise
        validate_args(args)

    def test_validate_missing_input_file(self):
        """Test validation fails with non-existent input."""
        parser = create_parser()
        args = parser.parse_args(["--input", "/nonexistent/path.mp3", "--api-key", "key"])

        with pytest.raises(SystemExit) as exc_info:
            validate_args(args)

        assert exc_info.value.code == 1

    def test_validate_negative_segment_length(self, tmp_path):
        """Test validation fails with negative segment length."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()

        parser = create_parser()
        args = parser.parse_args(["--input", str(audio_file), "--api-key", "key"])
        args.segment_length = -10

        with pytest.raises(SystemExit) as exc_info:
            validate_args(args)

        assert exc_info.value.code == 1

    def test_validate_zero_segment_length(self, tmp_path):
        """Test validation fails with zero segment length."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()

        parser = create_parser()
        args = parser.parse_args(["--input", str(audio_file), "--api-key", "key"])
        args.segment_length = 0

        with pytest.raises(SystemExit) as exc_info:
            validate_args(args)

        assert exc_info.value.code == 1

    def test_validate_negative_overlap(self, tmp_path):
        """Test validation fails with negative overlap."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()

        parser = create_parser()
        args = parser.parse_args(["--input", str(audio_file), "--api-key", "key"])
        args.overlap = -5

        with pytest.raises(SystemExit) as exc_info:
            validate_args(args)

        assert exc_info.value.code == 1

    def test_validate_overlap_greater_than_segment(self, tmp_path):
        """Test validation fails when overlap >= segment length."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()

        parser = create_parser()
        args = parser.parse_args(["--input", str(audio_file), "--api-key", "key"])
        args.segment_length = 60
        args.overlap = 60

        with pytest.raises(SystemExit) as exc_info:
            validate_args(args)

        assert exc_info.value.code == 1

    def test_validate_zero_concurrency(self, tmp_path):
        """Test validation fails with zero concurrency."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()

        parser = create_parser()
        args = parser.parse_args(["--input", str(audio_file), "--api-key", "key"])
        args.concurrency = 0

        with pytest.raises(SystemExit) as exc_info:
            validate_args(args)

        assert exc_info.value.code == 1

    def test_validate_invalid_temperature_low(self, tmp_path):
        """Test validation fails with temperature < 0."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()

        parser = create_parser()
        args = parser.parse_args(["--input", str(audio_file), "--api-key", "key"])
        args.temperature = -0.1

        with pytest.raises(SystemExit) as exc_info:
            validate_args(args)

        assert exc_info.value.code == 1

    def test_validate_invalid_temperature_high(self, tmp_path):
        """Test validation fails with temperature > 1."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()

        parser = create_parser()
        args = parser.parse_args(["--input", str(audio_file), "--api-key", "key"])
        args.temperature = 1.5

        with pytest.raises(SystemExit) as exc_info:
            validate_args(args)

        assert exc_info.value.code == 1

    def test_validate_valid_arguments(self, tmp_path):
        """Test validation passes with valid arguments."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()

        parser = create_parser()
        args = parser.parse_args(["--input", str(audio_file), "--api-key", "key"])

        # Should not raise
        validate_args(args)


class TestPrintSummary:
    """Tests for summary printing."""

    def test_print_summary_empty_results(self):
        """Test summary with no results."""
        output = StringIO()
        with patch("sys.stdout", output):
            print_summary([], model="gpt-4o-mini-transcribe")

        result = output.getvalue()
        assert "TRANSCRIPTION SUMMARY" in result
        assert "Files processed:     0" in result

    def test_print_summary_successful_files(self):
        """Test summary with successful transcriptions."""
        results = [
            {
                "file": "test1.mp3",
                "status": "success",
                "segments": 3,
                "failed": 0,
                "duration_seconds": 120.0,
            },
            {
                "file": "test2.mp3",
                "status": "success",
                "segments": 2,
                "failed": 1,
                "duration_seconds": 90.0,
            },
        ]

        output = StringIO()
        with patch("sys.stdout", output):
            print_summary(results, model="gpt-4o-mini-transcribe")

        result = output.getvalue()
        assert "Files processed:     2" in result
        assert "Total segments:      5" in result
        assert "Failed segments:     1" in result
        assert "Total duration:" in result
        assert "Estimated cost:" in result

    def test_print_summary_skipped_files(self):
        """Test summary with skipped files."""
        results = [
            {"file": "test1.mp3", "status": "skipped"},
            {"file": "test2.mp3", "status": "skipped"},
        ]

        output = StringIO()
        with patch("sys.stdout", output):
            print_summary(results, model="gpt-4o-mini-transcribe")

        result = output.getvalue()
        assert "Files skipped:       2" in result

    def test_print_summary_failed_files(self):
        """Test summary with failed files."""
        results = [
            {"file": "test1.mp3", "status": "error", "error": "API error"},
            {
                "file": "test2.mp3",
                "status": "success",
                "segments": 1,
                "failed": 0,
                "duration_seconds": 30.0,
            },
        ]

        output = StringIO()
        with patch("sys.stdout", output):
            print_summary(results, model="gpt-4o-mini-transcribe")

        result = output.getvalue()
        assert "Files failed:        1" in result
        assert "Files processed:     1" in result

    def test_print_summary_verbose_mode(self):
        """Test summary in verbose mode."""
        results = [
            {"file": "/path/to/test1.mp3", "status": "success"},
            {"file": "/path/to/test2.mp3", "status": "skipped"},
            {"file": "/path/to/test3.mp3", "status": "error"},
        ]

        output = StringIO()
        with patch("sys.stdout", output):
            print_summary(results, model="gpt-4o-mini-transcribe", verbose=True)

        result = output.getvalue()
        assert "Detailed results:" in result
        assert "test1.mp3" in result
        assert "test2.mp3" in result
        assert "test3.mp3" in result


class TestMain:
    """Tests for main CLI entry point."""

    @patch("audio_transcriber.cli.setup_logging")
    @patch("audio_transcriber.cli.find_audio_files")
    def test_main_no_audio_files(self, mock_find_files, mock_logging, tmp_path):
        """Test main exits when no audio files found."""
        audio_dir = tmp_path / "empty"
        audio_dir.mkdir()

        mock_find_files.return_value = []

        with patch(
            "sys.argv", ["audio-transcriber", "--input", str(audio_dir), "--api-key", "key"]
        ):
            exit_code = main()

        assert exit_code == 1

    @patch("audio_transcriber.cli.setup_logging")
    @patch("audio_transcriber.cli.find_audio_files")
    def test_main_file_not_found_error(self, mock_find_files, mock_logging):
        """Test main handles FileNotFoundError."""
        # validate_args will exit before find_audio_files is called
        with patch(
            "sys.argv", ["audio-transcriber", "--input", "/nonexistent", "--api-key", "key"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

    @patch("audio_transcriber.cli.setup_logging")
    @patch("audio_transcriber.cli.find_audio_files")
    def test_main_dry_run(self, mock_find_files, mock_logging, tmp_path):
        """Test main in dry-run mode."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()

        mock_find_files.return_value = [audio_file]

        output = StringIO()
        with patch("sys.argv", ["audio-transcriber", "--input", str(audio_file), "--dry-run"]):
            with patch("sys.stdout", output):
                exit_code = main()

        assert exit_code == 0
        result = output.getvalue()
        assert "DRY RUN MODE" in result
        assert "No API calls will be made" in result

    @patch("audio_transcriber.cli.setup_logging")
    @patch("audio_transcriber.cli.find_audio_files")
    @patch("audio_transcriber.cli.AudioTranscriber")
    def test_main_successful_transcription(
        self, mock_transcriber_class, mock_find_files, mock_logging, tmp_path
    ):
        """Test successful main execution."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()

        mock_find_files.return_value = [audio_file]

        mock_transcriber = MagicMock()
        mock_transcriber.segmenter.get_audio_duration.return_value = 60.0
        mock_transcriber.transcribe_file.return_value = {
            "file": str(audio_file),
            "status": "success",
            "segments": 2,
            "transcribed": 2,
            "failed": 0,
            "duration_seconds": 60.0,
            "output": str(tmp_path / "test.txt"),
        }
        mock_transcriber_class.return_value = mock_transcriber

        with patch(
            "sys.argv", ["audio-transcriber", "--input", str(audio_file), "--api-key", "test-key"]
        ):
            exit_code = main()

        assert exit_code == 0
        mock_transcriber.transcribe_file.assert_called_once()

    @patch("audio_transcriber.cli.setup_logging")
    @patch("audio_transcriber.cli.find_audio_files")
    @patch("audio_transcriber.cli.AudioTranscriber")
    def test_main_failed_transcription(
        self, mock_transcriber_class, mock_find_files, mock_logging, tmp_path
    ):
        """Test main returns error code when transcription fails."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()

        mock_find_files.return_value = [audio_file]

        mock_transcriber = MagicMock()
        mock_transcriber.segmenter.get_audio_duration.return_value = 60.0
        mock_transcriber.transcribe_file.return_value = {
            "file": str(audio_file),
            "status": "error",
            "error": "API error",
        }
        mock_transcriber_class.return_value = mock_transcriber

        with patch(
            "sys.argv", ["audio-transcriber", "--input", str(audio_file), "--api-key", "test-key"]
        ):
            exit_code = main()

        assert exit_code == 1

    @patch("audio_transcriber.cli.setup_logging")
    @patch("audio_transcriber.cli.find_audio_files")
    @patch("audio_transcriber.cli.AudioTranscriber")
    def test_main_multiple_files(
        self, mock_transcriber_class, mock_find_files, mock_logging, tmp_path
    ):
        """Test main with multiple audio files."""
        audio_files = [tmp_path / f"test{i}.mp3" for i in range(3)]
        for f in audio_files:
            f.touch()

        mock_find_files.return_value = audio_files

        mock_transcriber = MagicMock()
        mock_transcriber.segmenter.get_audio_duration.return_value = 30.0
        mock_transcriber.transcribe_file.return_value = {
            "status": "success",
            "segments": 1,
            "failed": 0,
            "duration_seconds": 30.0,
            "output": str(tmp_path / "test.txt"),
        }
        mock_transcriber_class.return_value = mock_transcriber

        with patch(
            "sys.argv", ["audio-transcriber", "--input", str(tmp_path), "--api-key", "test-key"]
        ):
            exit_code = main()

        assert exit_code == 0
        assert mock_transcriber.transcribe_file.call_count == 3

    @patch("audio_transcriber.cli.setup_logging")
    @patch("audio_transcriber.cli.find_audio_files")
    @patch("audio_transcriber.cli.AudioTranscriber")
    def test_main_passes_arguments_correctly(
        self, mock_transcriber_class, mock_find_files, mock_logging, tmp_path
    ):
        """Test that main passes CLI arguments to transcriber."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()

        mock_find_files.return_value = [audio_file]

        mock_transcriber = MagicMock()
        mock_transcriber.segmenter.get_audio_duration.return_value = 30.0
        mock_transcriber.transcribe_file.return_value = {
            "status": "success",
            "segments": 1,
            "failed": 0,
            "duration_seconds": 30.0,
            "output": str(tmp_path / "test.txt"),
        }
        mock_transcriber_class.return_value = mock_transcriber

        with patch(
            "sys.argv",
            [
                "audio-transcriber",
                "--input",
                str(audio_file),
                "--api-key",
                "test-key",
                "--model",
                "custom-model",
                "--base-url",
                "http://custom.api/v1",
                "--output-dir",
                "./out",
                "--segments-dir",
                "./segs",
                "--segment-length",
                "900",
                "--overlap",
                "15",
                "--language",
                "de",
                "--temperature",
                "0.5",
                "--prompt",
                "Context",
                "--concurrency",
                "8",
                "--response-format",
                "srt",
                # Note: defaults changed - keep_segments=True, skip_existing=False
                # So we don't need flags to set them to True/False respectively
            ],
        ):
            main()

        # Verify transcriber was initialized with correct params
        mock_transcriber_class.assert_called_once_with(
            api_key="test-key",
            base_url="http://custom.api/v1",
            model="custom-model",
        )

        # Verify transcribe_file was called with correct params
        call_kwargs = mock_transcriber.transcribe_file.call_args[1]
        assert call_kwargs["segment_length"] == 900
        assert call_kwargs["overlap"] == 15
        assert call_kwargs["language"] == "de"
        assert call_kwargs["temperature"] == 0.5
        assert call_kwargs["prompt"] == "Context"
        assert call_kwargs["concurrency"] == 8
        assert call_kwargs["response_format"] == "srt"
        assert call_kwargs["keep_segments"] is True
        assert call_kwargs["skip_existing"] is False
