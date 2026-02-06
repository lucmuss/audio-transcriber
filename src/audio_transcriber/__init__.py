"""
Audio Transcriber - Professional audio transcription tool.

A robust, production-ready solution for transcribing large audio files
using OpenAI-compatible Speech-to-Text APIs with intelligent segmentation.
"""

__version__ = "1.1.1"
__author__ = "Audio Transcriber Contributors"
__license__ = "MIT"

from .merger import TranscriptionMerger
from .segmenter import AudioSegmenter
from .transcriber import AudioTranscriber

__all__ = [
    "AudioTranscriber",
    "AudioSegmenter",
    "TranscriptionMerger",
]
