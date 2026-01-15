"""
Constants and configuration for Audio Transcriber.
"""

from typing import Set

# Supported audio formats
SUPPORTED_FORMATS: Set[str] = {
    ".mp3",
    ".wav",
    ".flac",
    ".m4a",
    ".ogg",
    ".aac",
    ".wma",
    ".mp4",
}

# Audio processing defaults
DEFAULT_SAMPLE_RATE = 16000  # Hz - OpenAI Whisper standard
DEFAULT_CHANNELS = 1  # Mono
DEFAULT_BITRATE = "64k"  # For MP3 compression

# Transcription defaults
DEFAULT_SEGMENT_LENGTH = 600  # seconds (10 minutes)
DEFAULT_OVERLAP = 10  # seconds
DEFAULT_CONCURRENCY = 4  # parallel segments
DEFAULT_TEMPERATURE = 0.0  # deterministic output
DEFAULT_MAX_RETRIES = 5  # API retry attempts

# API defaults
DEFAULT_MODEL = "whisper-1"
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_RESPONSE_FORMAT = "text"

# Pricing (per minute, in USD)
WHISPER_PRICE_PER_MINUTE = 0.0001

# Output formats
VALID_RESPONSE_FORMATS = {"text", "json", "srt", "vtt", "verbose_json"}

# Environment variable prefix
ENV_PREFIX = "AUDIO_TRANSCRIBE_"
