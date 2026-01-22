"""
Graphical User Interface for Audio Transcriber using Tkinter (English-only).

DEPRECATED: This file is kept for backwards compatibility.
Please use the modular GUI package located in audio_transcriber/gui/
"""

# Import the new modular GUI for backwards compatibility
from .gui.main import AudioTranscriberGUI, main

# Re-export for backwards compatibility
__all__ = ["AudioTranscriberGUI", "main"]
