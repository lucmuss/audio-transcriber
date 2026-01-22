"""
Tab modules for Audio Transcriber GUI.
"""

from .api_tab import create_api_tab
from .diarization_tab import create_diarization_tab
from .export_tab import create_export_tab
from .main_tab import create_main_tab
from .preview_tab import create_preview_tab
from .summary_tab import create_summary_tab
from .transcription_tab import create_transcription_tab

__all__ = [
    "create_main_tab",
    "create_api_tab",
    "create_transcription_tab",
    "create_diarization_tab",
    "create_export_tab",
    "create_summary_tab",
    "create_preview_tab",
]
