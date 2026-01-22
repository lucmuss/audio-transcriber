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
DEFAULT_SEGMENT_LENGTH = 300  # seconds (5 minutes)
DEFAULT_OVERLAP = 3  # seconds
DEFAULT_CONCURRENCY = 8  # parallel segments
DEFAULT_TEMPERATURE = 0.0  # deterministic output
DEFAULT_MAX_RETRIES = 5  # API retry attempts

# API defaults
DEFAULT_MODEL = "gpt-4o-mini-transcribe"
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_RESPONSE_FORMAT = "text"

# Diarization defaults
DEFAULT_DIARIZATION_MODEL = "gpt-4o-transcribe-diarize"
DEFAULT_DIARIZATION_FORMAT = "diarized_json"

# Summarization defaults
DEFAULT_SUMMARY_MODEL = "gpt-4.1-mini"
DEFAULT_SUMMARY_PROMPT = """Bitte erstelle eine prägnante Zusammenfassung des folgenden Transkripts. 
Fokussiere dich auf die wichtigsten Punkte, Themen und Erkenntnisse."""

# Pricing (per minute, in USD) - Model-specific rates
MODEL_PRICES_PER_MINUTE = {
    # Transcription models
    "gpt-4o-transcribe": 0.006,
    "gpt-4o-transcribe-diarize": 0.006,
    "gpt-4o-mini-transcribe": 0.003,
    "whisper-1": 0.006,
    "whisper": 0.006,
    # Legacy/fallback
    "whisper-large-v3": 0.006,
    "distil-whisper": 0.006,
}

# Default price per minute (fallback for unknown models)
DEFAULT_MODEL_PRICE_PER_MINUTE = 0.006


def get_model_price_per_minute(model_name: str) -> float:
    """
    Get the price per minute for a specific transcription model.
    
    Args:
        model_name: Name of the transcription model
        
    Returns:
        Price per minute in USD
    """
    return MODEL_PRICES_PER_MINUTE.get(model_name, DEFAULT_MODEL_PRICE_PER_MINUTE)


# Output formats
VALID_RESPONSE_FORMATS = {"text", "json", "srt", "vtt", "verbose_json", "diarized_json"}

# Export formats
VALID_EXPORT_FORMATS = {"txt", "docx", "md", "latex", "pdf"}

# Environment variable prefix
ENV_PREFIX = "AUDIO_TRANSCRIBE_"
