"""
Entry point for audio-transcriber package.

This module allows running the package as:
    python -m audio_transcriber
Or when packaged with PyInstaller as a binary.
"""

import sys

from audio_transcriber.cli import main

if __name__ == "__main__":
    sys.exit(main())
