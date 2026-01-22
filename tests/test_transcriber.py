"""
Tests for audio transcription orchestrator.
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from openai import APIError

from audio_transcriber.constants import DEFAULT_MODEL
from audio_transcriber.transcriber import AudioTranscriber


class TestAudioTranscriber:
    """Tests for AudioTranscriber class."""

    def setup_method(self, method):
        """Setup test fixtures."""
        self.api_key = "test-api-key"
        self.base_url = "https://api.test.com/v1"
        self.model = "whisper-1"

        with patch("audio_transcriber.transcriber.OpenAI"):
            self.transcriber = AudioTranscriber(
                api_key=self.api_key, base_url=self.base_url, model=self.model
            )

    @patch("audio_transcriber.transcriber.OpenAI")
    def test_init_default_values(self, mock_openai):
        """Test initialization with default values."""
        transcriber = AudioTranscriber(api_key="key")

        assert transcriber.api_key == "key"
        assert transcriber.base_url == "https://api.openai.com/v1"
        assert transcriber.model == DEFAULT_MODEL

    @patch("audio_transcriber.transcriber.OpenAI")
    def test_init_custom_values(self, mock_openai):
        """Test initialization with custom values."""
        transcriber = AudioTranscriber(
            api_key="custom-key", base_url="https://custom.api/v1", model="custom-model"
        )

        assert transcriber.api_key == "custom-key"
        assert transcriber.base_url == "https://custom.api/v1"
        assert transcriber.model == "custom-model"

    def test_transcribe_file_invalid_params(self, tmp_path):
        """Test transcribe_file with invalid parameters."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()
        output_dir = tmp_path / "output"

        # Invalid segment length
        with pytest.raises(ValueError, match="Segment length must be positive"):
            self.transcriber.transcribe_file(audio_file, output_dir, segment_length=-1)

        # Invalid overlap
        with pytest.raises(ValueError, match="Overlap must be non-negative"):
            self.transcriber.transcribe_file(audio_file, output_dir, overlap=-5)

        # Overlap >= segment length
        with pytest.raises(ValueError, match="must be less than segment length"):
            self.transcriber.transcribe_file(audio_file, output_dir, segment_length=60, overlap=60)

        # Invalid concurrency
        with pytest.raises(ValueError, match="Concurrency must be positive"):
            self.transcriber.transcribe_file(audio_file, output_dir, concurrency=0)

        # Invalid temperature
        with pytest.raises(ValueError, match="Temperature must be between"):
            self.transcriber.transcribe_file(audio_file, output_dir, temperature=1.5)

    def test_transcribe_file_skip_existing(self, tmp_path):
        """Test skip_existing functionality."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create existing output file (must match naming pattern: {stem}_{ext}_full.{format})
        existing_output = output_dir / "test_mp3_full.text"
        existing_output.write_text("existing transcription")

        result = self.transcriber.transcribe_file(audio_file, output_dir, skip_existing=True)

        assert result["status"] == "skipped"
        assert result["file"] == str(audio_file)

    @patch.object(AudioTranscriber, "_cleanup_segments")
    def test_transcribe_file_duration_error(self, mock_cleanup, tmp_path):
        """Test error handling when getting audio duration fails."""
        audio_file = tmp_path / "bad.mp3"
        audio_file.touch()
        output_dir = tmp_path / "output"

        with patch.object(self.transcriber.segmenter, "get_audio_duration") as mock_duration:
            mock_duration.side_effect = Exception("Cannot read file")

            result = self.transcriber.transcribe_file(audio_file, output_dir)

            assert result["status"] == "error"
            assert "Cannot read file" in result["error"]

    @patch.object(AudioTranscriber, "_cleanup_segments")
    def test_transcribe_file_segmentation_error(self, mock_cleanup, tmp_path):
        """Test error handling when segmentation fails."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()
        output_dir = tmp_path / "output"

        with patch.object(self.transcriber.segmenter, "get_audio_duration") as mock_duration:
            mock_duration.return_value = 120.0

            with patch.object(self.transcriber.segmenter, "segment_audio") as mock_segment:
                mock_segment.side_effect = Exception("Segmentation failed")

                result = self.transcriber.transcribe_file(audio_file, output_dir)

                assert result["status"] == "error"
                assert "Segmentation failed" in result["error"]

    @patch.object(AudioTranscriber, "_cleanup_segments")
    @patch.object(AudioTranscriber, "_transcribe_segments")
    def test_transcribe_file_no_segments_created(self, mock_transcribe, mock_cleanup, tmp_path):
        """Test handling when no segments are created."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()
        output_dir = tmp_path / "output"

        with patch.object(self.transcriber.segmenter, "get_audio_duration") as mock_duration:
            mock_duration.return_value = 120.0

            with patch.object(self.transcriber.segmenter, "segment_audio") as mock_segment:
                mock_segment.return_value = []

                result = self.transcriber.transcribe_file(audio_file, output_dir)

                assert result["status"] == "error"
                assert "No segments created" in result["error"]

    @patch.object(AudioTranscriber, "_cleanup_segments")
    @patch.object(AudioTranscriber, "_transcribe_segments")
    @patch.object(AudioTranscriber, "_detect_language")
    def test_transcribe_file_all_segments_failed(
        self, mock_detect, mock_transcribe, mock_cleanup, tmp_path
    ):
        """Test handling when all segments fail transcription."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()
        output_dir = tmp_path / "output"
        segments_dir = tmp_path / "segments"

        segment_files = [segments_dir / f"seg{i}.mp3" for i in range(3)]
        for seg in segment_files:
            seg.parent.mkdir(exist_ok=True)
            seg.touch()

        with patch.object(self.transcriber.segmenter, "get_audio_duration") as mock_duration:
            mock_duration.return_value = 120.0

            with patch.object(self.transcriber.segmenter, "segment_audio") as mock_segment:
                mock_segment.return_value = segment_files
                mock_detect.return_value = "en"
                mock_transcribe.return_value = ([], 3)  # No successful transcriptions

                result = self.transcriber.transcribe_file(
                    audio_file, output_dir, segments_dir=segments_dir
                )

                assert result["status"] == "error"
                assert result["failed_segments"] == 3
                mock_cleanup.assert_called_once()

    @patch.object(AudioTranscriber, "_cleanup_segments")
    @patch.object(AudioTranscriber, "_transcribe_segments")
    @patch.object(AudioTranscriber, "_detect_language")
    def test_transcribe_file_merge_failure(
        self, mock_detect, mock_transcribe, mock_cleanup, tmp_path
    ):
        """Test handling when merging transcriptions fails."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()
        output_dir = tmp_path / "output"

        segment_files = [tmp_path / "seg1.mp3"]
        segment_files[0].touch()

        with patch.object(self.transcriber.segmenter, "get_audio_duration") as mock_duration:
            mock_duration.return_value = 30.0

            with patch.object(self.transcriber.segmenter, "segment_audio") as mock_segment:
                mock_segment.return_value = segment_files
                mock_detect.return_value = "en"
                mock_transcribe.return_value = (["transcription"], 0)

                with patch.object(self.transcriber.merger, "merge") as mock_merge:
                    mock_merge.side_effect = Exception("Merge error")

                    result = self.transcriber.transcribe_file(audio_file, output_dir)

                    assert result["status"] == "error"
                    assert "Merge failed" in result["error"]
                    mock_cleanup.assert_called()

    @patch.object(AudioTranscriber, "_cleanup_segments")
    @patch.object(AudioTranscriber, "_transcribe_segments")
    @patch.object(AudioTranscriber, "_detect_language")
    def test_transcribe_file_success(self, mock_detect, mock_transcribe, mock_cleanup, tmp_path):
        """Test successful transcription workflow."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()
        output_dir = tmp_path / "output"

        segment_files = [tmp_path / f"seg{i}.mp3" for i in range(2)]
        for seg in segment_files:
            seg.touch()

        with patch.object(self.transcriber.segmenter, "get_audio_duration") as mock_duration:
            mock_duration.return_value = 90.0

            with patch.object(self.transcriber.segmenter, "segment_audio") as mock_segment:
                mock_segment.return_value = segment_files
                mock_detect.return_value = "en"
                mock_transcribe.return_value = (["Hello", "World"], 0)

                with patch.object(self.transcriber.merger, "merge") as mock_merge:
                    mock_merge.return_value = "Hello World"

                    result = self.transcriber.transcribe_file(audio_file, output_dir)

                    assert result["status"] == "success"
                    assert result["segments"] == 2
                    assert result["transcribed"] == 2
                    assert result["failed"] == 0
                    assert result["duration_seconds"] == 90.0
                    assert result["language"] == "en"

                    # Check output file was created
                    output_file = Path(result["output"])
                    assert output_file.exists()
                    assert output_file.read_text() == "Hello World"

                    # Cleanup should be called without keep_segments
                    mock_cleanup.assert_called_once_with(segment_files)

    @patch.object(AudioTranscriber, "_cleanup_segments")
    @patch.object(AudioTranscriber, "_transcribe_segments")
    def test_transcribe_file_with_segments_dir(self, mock_transcribe, mock_cleanup, tmp_path):
        """Test that segments_dir parameter is used correctly."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()
        output_dir = tmp_path / "transcriptions"
        segments_dir = tmp_path / "segments"

        segment_files = [segments_dir / "seg1.mp3"]

        with patch.object(self.transcriber.segmenter, "get_audio_duration") as mock_duration:
            mock_duration.return_value = 30.0

            with patch.object(self.transcriber.segmenter, "segment_audio") as mock_segment:
                mock_segment.return_value = segment_files
                mock_transcribe.return_value = (["text"], 0)

                with patch.object(self.transcriber.merger, "merge") as mock_merge:
                    mock_merge.return_value = "text"

                    self.transcriber.transcribe_file(
                        audio_file, output_dir, segments_dir=segments_dir
                    )

                    # Verify segment_audio was called with segments_dir
                    mock_segment.assert_called_once()
                    args = mock_segment.call_args[0]
                    assert args[3] == segments_dir

    @patch.object(AudioTranscriber, "_cleanup_segments")
    @patch.object(AudioTranscriber, "_transcribe_segments")
    def test_transcribe_file_keep_segments(self, mock_transcribe, mock_cleanup, tmp_path):
        """Test keep_segments parameter."""
        audio_file = tmp_path / "test.mp3"
        audio_file.touch()
        output_dir = tmp_path / "output"

        segment_files = [tmp_path / "seg1.mp3"]
        segment_files[0].touch()

        with patch.object(self.transcriber.segmenter, "get_audio_duration") as mock_duration:
            mock_duration.return_value = 30.0

            with patch.object(self.transcriber.segmenter, "segment_audio") as mock_segment:
                mock_segment.return_value = segment_files
                mock_transcribe.return_value = (["text"], 0)

                with patch.object(self.transcriber.merger, "merge") as mock_merge:
                    mock_merge.return_value = "text"

                    self.transcriber.transcribe_file(audio_file, output_dir, keep_segments=True)

                    # Cleanup should NOT be called when keep_segments=True
                    mock_cleanup.assert_not_called()

    def test_detect_language_success(self, tmp_path):
        """Test successful language detection."""
        segment_file = tmp_path / "seg1.mp3"
        segment_file.touch()

        mock_response = Mock()
        mock_response.language = "de"

        with patch.object(self.transcriber.client.audio.transcriptions, "create") as mock_create:
            mock_create.return_value = mock_response

            language = self.transcriber._detect_language(segment_file)

            assert language == "de"
            mock_create.assert_called_once()

    def test_detect_language_failure(self, tmp_path):
        """Test language detection failure handling."""
        segment_file = tmp_path / "seg1.mp3"
        segment_file.touch()

        with patch.object(self.transcriber.client.audio.transcriptions, "create") as mock_create:
            mock_create.side_effect = Exception("API error")

            language = self.transcriber._detect_language(segment_file)

            assert language is None

    def test_detect_language_no_language_attribute(self, tmp_path):
        """Test language detection when response has no language attribute."""
        segment_file = tmp_path / "seg1.mp3"
        segment_file.touch()

        mock_response = Mock(spec=[])  # No language attribute

        with patch.object(self.transcriber.client.audio.transcriptions, "create") as mock_create:
            mock_create.return_value = mock_response

            language = self.transcriber._detect_language(segment_file)

            assert language is None

    def test_transcribe_segment_success_text_format(self, tmp_path):
        """Test successful segment transcription with text format."""
        segment_file = tmp_path / "seg1.mp3"
        segment_file.touch()

        with patch.object(self.transcriber.client.audio.transcriptions, "create") as mock_create:
            mock_create.return_value = "Transcribed text"

            result = self.transcriber._transcribe_segment(
                segment_file, language="en", response_format="text", temperature=0.0, prompt=None
            )

            assert result == "Transcribed text"

    def test_transcribe_segment_success_json_format(self, tmp_path):
        """Test successful segment transcription with JSON format."""
        segment_file = tmp_path / "seg1.mp3"
        segment_file.touch()

        mock_response = Mock()
        mock_response.model_dump_json.return_value = '{"text": "Hello"}'

        with patch.object(self.transcriber.client.audio.transcriptions, "create") as mock_create:
            mock_create.return_value = mock_response

            result = self.transcriber._transcribe_segment(
                segment_file, language="en", response_format="json", temperature=0.0, prompt=None
            )

            assert result == '{"text": "Hello"}'

    def test_transcribe_segment_with_prompt(self, tmp_path):
        """Test segment transcription with custom prompt."""
        segment_file = tmp_path / "seg1.mp3"
        segment_file.touch()

        with patch.object(self.transcriber.client.audio.transcriptions, "create") as mock_create:
            mock_create.return_value = "text"

            self.transcriber._transcribe_segment(
                segment_file,
                language="en",
                response_format="text",
                temperature=0.5,
                prompt="Custom context",
            )

            # Verify prompt was passed
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["prompt"] == "Custom context"
            assert call_kwargs["temperature"] == 0.5

    def test_transcribe_segment_retry_on_api_error(self, tmp_path):
        """Test retry logic on API errors."""
        segment_file = tmp_path / "seg1.mp3"
        segment_file.touch()

        with patch.object(self.transcriber.client.audio.transcriptions, "create") as mock_create:
            # Create proper APIError instances with message and request
            mock_request = Mock()
            mock_request.method = "POST"
            mock_request.url = "https://api.openai.com/v1/audio/transcriptions"

            # Fail twice, then succeed
            error1 = APIError(message="Rate limit", request=mock_request, body=None)
            error2 = APIError(message="Server error", request=mock_request, body=None)
            mock_create.side_effect = [error1, error2, "Success"]

            result = self.transcriber._transcribe_segment(
                segment_file,
                language="en",
                response_format="text",
                temperature=0.0,
                prompt=None,
                max_retries=3,
            )

            assert result == "Success"
            assert mock_create.call_count == 3

    def test_transcribe_segment_max_retries_exceeded(self, tmp_path):
        """Test that None is returned after max retries."""
        segment_file = tmp_path / "seg1.mp3"
        segment_file.touch()

        with patch.object(self.transcriber.client.audio.transcriptions, "create") as mock_create:
            # Create proper APIError instance
            mock_request = Mock()
            mock_request.method = "POST"
            mock_request.url = "https://api.openai.com/v1/audio/transcriptions"
            error = APIError(message="Persistent error", request=mock_request, body=None)
            mock_create.side_effect = error

            result = self.transcriber._transcribe_segment(
                segment_file,
                language="en",
                response_format="text",
                temperature=0.0,
                prompt=None,
                max_retries=2,
            )

            assert result is None
            assert mock_create.call_count == 2

    def test_transcribe_segment_unexpected_error(self, tmp_path):
        """Test handling of unexpected errors."""
        segment_file = tmp_path / "seg1.mp3"
        segment_file.touch()

        with patch.object(self.transcriber.client.audio.transcriptions, "create") as mock_create:
            mock_create.side_effect = ValueError("Unexpected error")

            result = self.transcriber._transcribe_segment(
                segment_file, language="en", response_format="text", temperature=0.0, prompt=None
            )

            assert result is None

    def test_cleanup_segments_delete_files(self, tmp_path):
        """Test cleanup deletes segment files."""
        segment_files = [tmp_path / f"seg{i}.mp3" for i in range(3)]
        for seg in segment_files:
            seg.touch()

        assert all(seg.exists() for seg in segment_files)

        self.transcriber._cleanup_segments(segment_files, keep=False)

        assert not any(seg.exists() for seg in segment_files)

    def test_cleanup_segments_keep_files(self, tmp_path):
        """Test cleanup keeps files when keep=True."""
        segment_files = [tmp_path / f"seg{i}.mp3" for i in range(3)]
        for seg in segment_files:
            seg.touch()

        self.transcriber._cleanup_segments(segment_files, keep=True)

        assert all(seg.exists() for seg in segment_files)

    def test_cleanup_segments_handles_missing_files(self, tmp_path):
        """Test cleanup handles already deleted files gracefully."""
        segment_files = [tmp_path / "existing.mp3", tmp_path / "missing.mp3"]
        segment_files[0].touch()

        # Should not raise even though one file doesn't exist
        self.transcriber._cleanup_segments(segment_files, keep=False)

        assert not segment_files[0].exists()

    def test_cleanup_segments_handles_deletion_errors(self, tmp_path):
        """Test cleanup handles deletion errors gracefully."""
        segment_files = [tmp_path / "seg1.mp3"]
        segment_files[0].touch()

        with patch.object(Path, "unlink") as mock_unlink:
            mock_unlink.side_effect = PermissionError("Cannot delete")

            # Should not raise exception
            self.transcriber._cleanup_segments(segment_files, keep=False)

    @patch("audio_transcriber.transcriber.ThreadPoolExecutor")
    def test_transcribe_segments_parallel_execution(self, mock_executor, tmp_path):
        """Test that segments are transcribed in parallel."""
        segment_files = [tmp_path / f"seg{i}.mp3" for i in range(4)]
        for seg in segment_files:
            seg.touch()

        # Create separate mock futures for each segment
        mock_futures = [Mock() for _ in range(4)]
        for future in mock_futures:
            future.result.return_value = "transcription"

        # Create mock executor instance with proper context manager support
        mock_executor_instance = MagicMock()
        mock_executor_instance.submit.side_effect = mock_futures
        mock_executor_instance.__enter__.return_value = mock_executor_instance
        mock_executor_instance.__exit__.return_value = None

        mock_executor.return_value = mock_executor_instance

        with patch("audio_transcriber.transcriber.as_completed") as mock_as_completed:
            mock_as_completed.return_value = mock_futures

            transcriptions, failed = self.transcriber._transcribe_segments(
                segment_files=segment_files,
                language="en",
                response_format="text",
                temperature=0.0,
                prompt=None,
                concurrency=4,
            )

            # Verify ThreadPoolExecutor was created with correct concurrency
            mock_executor.assert_called_once_with(max_workers=4)

            # Verify all segments were submitted
            assert mock_executor_instance.submit.call_count == 4

            assert len(transcriptions) == 4
            assert failed == 0
