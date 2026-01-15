"""
Audio Transcriber - Professional audio transcription tool.

A robust, production-ready solution for transcribing large audio files
using OpenAI-compatible Speech-to-Text APIs with intelligent segmentation.
"""

__version__ = "1.0.0"
__author__ = "Audio Transcriber Contributors"
__license__ = "MIT"

from .transcriber import AudioTranscriber
from .segmenter import AudioSegmenter
from .merger import TranscriptionMerger

__all__ = [
    "AudioTranscriber",
    "AudioSegmenter",
    "TranscriptionMerger",
]
