"""
Speaker diarization utilities for Audio Transcriber.
"""

import base64
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def to_data_url(path: Path) -> str:
    """
    Convert audio file to data URL for speaker reference.

    Args:
        path: Path to audio file

    Returns:
        Data URL string with base64-encoded audio
    """
    with open(path, "rb") as fh:
        encoded = base64.b64encode(fh.read()).decode("utf-8")
        # Determine mime type based on file extension
        ext = path.suffix.lower()
        mime_types = {
            ".wav": "audio/wav",
            ".mp3": "audio/mpeg",
            ".m4a": "audio/mp4",
            ".flac": "audio/flac",
            ".ogg": "audio/ogg",
        }
        mime_type = mime_types.get(ext, "audio/wav")
        return f"data:{mime_type};base64,{encoded}"


def format_diarized_transcript(diarized_json: str, include_timestamps: bool = True) -> str:
    """
    Convert diarized_json format to readable transcript.

    Args:
        diarized_json: JSON string from diarized transcription
        include_timestamps: Include start/end times in output

    Returns:
        Formatted transcript with speaker labels
    """
    try:
        data = json.loads(diarized_json)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse diarized JSON: {e}")
        return diarized_json  # Return as-is if parsing fails

    segments = data.get("segments", [])
    if not segments:
        logger.warning("No segments found in diarized JSON")
        return ""

    lines = []
    current_speaker: Optional[str] = None
    current_text: List[str] = []

    for segment in segments:
        speaker = segment.get("speaker", "Unknown")
        text = segment.get("text", "").strip()
        start = segment.get("start", 0)
        end = segment.get("end", 0)

        if not text:
            continue

        # Check if speaker changed
        if speaker != current_speaker:
            # Save previous speaker's text
            if current_speaker is not None:
                if current_text:
                    speaker_line = f"{current_speaker}: {' '.join(current_text)}"
                    lines.append(speaker_line)
                current_text = []
            current_speaker = speaker

        # Add text to current speaker
        if include_timestamps:
            current_text.append(f"[{_format_time(start)}-{_format_time(end)}] {text}")
        else:
            current_text.append(text)

    # Add last speaker's text
    if current_speaker and current_text:
        speaker_line = f"{current_speaker}: {' '.join(current_text)}"
        lines.append(speaker_line)

    return "\n\n".join(lines)


def _format_time(seconds: float) -> str:
    """Format seconds as MM:SS or HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def extract_speakers(diarized_json: str) -> List[str]:
    """
    Extract unique speaker names from diarized transcription.

    Args:
        diarized_json: JSON string from diarized transcription

    Returns:
        List of unique speaker names
    """
    try:
        data = json.loads(diarized_json)
    except json.JSONDecodeError:
        return []

    segments = data.get("segments", [])
    speakers = set()

    for segment in segments:
        speaker = segment.get("speaker")
        if speaker:
            speakers.add(speaker)

    return sorted(list(speakers))


def get_speaker_statistics(diarized_json: str) -> Dict[str, Any]:
    """
    Get statistics about speakers in the transcription.

    Args:
        diarized_json: JSON string from diarized transcription

    Returns:
        Dictionary with speaker statistics
    """
    try:
        data = json.loads(diarized_json)
    except json.JSONDecodeError:
        return {}

    segments = data.get("segments", [])
    speaker_stats = {}

    for segment in segments:
        speaker = segment.get("speaker", "Unknown")
        text = segment.get("text", "")
        start = segment.get("start", 0)
        end = segment.get("end", 0)
        duration = end - start

        if speaker not in speaker_stats:
            speaker_stats[speaker] = {
                "segments": 0,
                "total_duration": 0,
                "word_count": 0,
            }

        speaker_stats[speaker]["segments"] += 1
        speaker_stats[speaker]["total_duration"] += duration
        speaker_stats[speaker]["word_count"] += len(text.split())

    return speaker_stats
