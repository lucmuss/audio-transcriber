#!/bin/bash
# Audio Transcriber Setup Script
# Automatische Installation aller Abhängigkeiten

set -e

echo "=========================================="
echo "Audio Transcriber - Setup"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Fehler: Python 3 ist nicht installiert"
    echo "Bitte installieren Sie Python 3!"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python $PYTHON_VERSION gefunden"
echo ""

# Check if venv already exists
if [ -d "venv" ]; then
    echo "⚠️  Virtual Environment existiert bereits"
    read -p "Möchten Sie es neu erstellen? (ja/nein): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Jj]$ ]]; then
        rm -rf venv
        echo "Altes venv gelöscht"
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Erstelle Virtual Environment..."
    python3 -m venv venv
    echo "✓ Virtual Environment erstellt"
fi

echo ""
echo "Aktiviere Virtual Environment..."
source venv/bin/activate
echo "✓ Virtual Environment aktiviert"

echo ""
echo "Installiere Python-Abhängigkeiten..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
echo "✓ Abhängigkeiten installiert"

echo ""
echo "Prüfe FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version | head -n1)
    echo "✓ $FFMPEG_VERSION"
else
    echo "❌ Warnung: FFmpeg nicht gefunden"
    echo "Bitte installieren Sie FFmpeg:"
    echo "  - Linux (Ubuntu): sudo apt-get install ffmpeg"
    echo "  - Linux (Fedora): sudo dnf install ffmpeg"
    echo "  - macOS: brew install ffmpeg"
    echo "  - Windows: https://ffmpeg.org/download.html"
fi

echo ""
echo "=========================================="
echo "✓ Setup abgeschlossen!"
echo "=========================================="
echo ""
echo "Nächste Schritte:"
echo "1. Aktiviere das Virtual Environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Setze deinen API-Key:"
echo "   export AUDIO_TRANSCRIBE_API_KEY='sk-...'"
echo ""
echo "3. Führe das Tool aus:"
echo "   python3 audio_transcriber.py --help"
echo ""
echo "Beispiel (dry-run):"
echo "   python3 audio_transcriber.py --input examples/robin_audio --dry-run"
echo ""
