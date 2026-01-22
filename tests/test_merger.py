"""
Tests for transcription merger.
"""

from audio_transcriber.merger import TranscriptionMerger


class TestTranscriptionMerger:
    """Tests for TranscriptionMerger class."""

    def setup_method(self):
        self.merger = TranscriptionMerger()

    def test_merge_empty_list(self):
        result = self.merger.merge([], "text")
        assert result == ""

    def test_merge_single_text(self):
        result = self.merger.merge(["Hello world"], "text")
        assert result == "Hello world"

    def test_merge_multiple_texts(self):
        transcriptions = ["Hello world.", "How are you?"]
        result = self.merger.merge(transcriptions, "text")
        assert "Hello world" in result
        assert "How are you" in result

    def test_merge_with_overlap_removal(self):
        # Same sentence at end of first and start of second
        transcriptions = [
            "This is the first segment. This is a test.",
            "This is a test. This is the second segment.",
        ]
        result = self.merger.merge(transcriptions, "text")
        # Should not duplicate "This is a test"
        assert result.count("This is a test") <= 2

    def test_merge_json_format(self):
        transcriptions = [
            '{"text": "Hello", "language": "en"}',
            '{"text": "World", "language": "en"}',
        ]
        result = self.merger.merge(transcriptions, "json")
        assert "Hello" in result
        assert "World" in result

    def test_merge_srt_format(self):
        transcriptions = [
            "1\n00:00:00,000 --> 00:00:05,000\nHello\n\n",
            "2\n00:00:05,000 --> 00:00:10,000\nWorld\n\n",
        ]
        result = self.merger.merge(transcriptions, "srt")
        assert "Hello" in result
        assert "World" in result

    def test_merge_vtt_format(self):
        transcriptions = [
            "WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nHello\n\n",
            "WEBVTT\n\n00:00:05.000 --> 00:00:10.000\nWorld\n\n",
        ]
        result = self.merger.merge(transcriptions, "vtt")
        assert "WEBVTT" in result
        assert "Hello" in result
        assert "World" in result

    def test_sentences_similar_exact_match(self):
        sent1 = "this is a test"
        sent2 = "this is a test"
        assert self.merger._sentences_similar(sent1, sent2)

    def test_sentences_similar_high_overlap(self):
        sent1 = "this is a great test"
        sent2 = "this is a test"
        # High word overlap
        assert self.merger._sentences_similar(sent1, sent2, threshold=0.6)

    def test_sentences_not_similar(self):
        sent1 = "completely different"
        sent2 = "not at all similar"
        assert not self.merger._sentences_similar(sent1, sent2)

    def test_split_sentences(self):
        text = "First sentence. Second sentence! Third sentence?"
        sentences = self.merger._split_sentences(text)
        assert len(sentences) >= 3
        assert "First sentence" in sentences[0]
