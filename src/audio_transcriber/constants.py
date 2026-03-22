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
DEFAULT_TEMPERATURE = 0.9  # Good balance for accuracy and variety
DEFAULT_MAX_RETRIES = 5  # API retry attempts

# API defaults
DEFAULT_MODEL = "gpt-4o-mini-transcribe"
DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_RESPONSE_FORMAT = "text"

# Diarization defaults
DEFAULT_DIARIZATION_MODEL = "gpt-4o-transcribe-diarize"
DEFAULT_DIARIZATION_FORMAT = "diarized_json"

# Summarization defaults
DEFAULT_SUMMARY_MODEL = "gpt-5-mini"
DEFAULT_SUMMARY_PROMPT = (
    "Create an extremely detailed and structured summary of the transcription in Markdown format. "
    "Use the following structure (translate headers to the target language):\n"
    "# Detailed Summary\n"
    "[Provide a comprehensive overview of the entire conversation here]\n\n"
    "## Key Topics & Details\n"
    "[List all important topics with sub-points and specific details]\n\n"
    "## Decisions & Outcomes\n"
    "[What was specifically decided?]\n\n"
    "## Open Questions & Issues\n"
    "[What remained unresolved?]\n\n"
    "## Meeting Minutes (TODO List)\n"
    "Create a table with the following columns: Task, Owner, Deadline, Status. "
    "If information is missing, enter 'Not mentioned'.\n\n"
    "LENGTH LIMIT: Ensure the summary is comprehensive but does not exceed approximately 3-4 DIN-A4 pages (maximum 3000 words).\n"
    "IMPORTANT: Write the ENTIRE summary, including all HEADERS and tables, in the SAME LANGUAGE as the transcription."
)

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
VALID_EXPORT_FORMATS = {"docx", "md", "markdown", "latex", "tex"}

# Environment variable prefix
ENV_PREFIX = "AUDIO_TRANSCRIBE_"
