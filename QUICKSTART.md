# 🚀 Quick Start Guide

Schnelleste Möglichkeit, um mit Audio Transcriber zu starten!

## Installation (2 Minuten)

### Option 1: Automatisches Setup-Skript (empfohlen) ⭐

```bash
# 1. Klone das Repository
git clone https://github.com/lucmuss/audio-transcriber.git
cd audio-transcriber

# 2. Führe das Setup-Skript aus
bash setup.sh

# 3. Aktiviere das Virtual Environment
source venv/bin/activate

# 4. Done! ✓
```

### Option 2: Manuelles Setup

```bash
git clone https://github.com/lucmuss/audio-transcriber.git
cd audio-transcriber

# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# oder auf Windows: venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

## Erste Schritte

### 1. API-Key setzen

```bash
export AUDIO_TRANSCRIBE_API_KEY="sk-"
```

### 2. Dry-Run testen (keine Kosten!)

```bash
python3 audio_transcriber.py \
  --input examples/robin_audio \
  --model gpt-4o-mini-transcribe \
  --language de \
  --segment-length 480 \
  --overlap 15 \
  --dry-run
```

Output: Zeigt wie viele Segmente erstellt würden

### 3. Echte Transkription starten

```bash
python3 audio_transcriber.py \
  --input examples/robin_audio \
  --model gpt-4o-mini-transcribe \
  --language de \
  --segment-length 480 \
  --overlap 15 \
  --output-dir ./transcriptions
```

Output: 
- `./transcriptions/robin_audio_001.txt` (Segment 1)
- `./transcriptions/robin_audio_full.txt` (komplette Transkription)

## Häufige Fehler & Lösungen

### ❌ "ModuleNotFoundError: No module named 'pydub'"

**Lösung:** Virtual Environment nicht aktiviert!

```bash
source venv/bin/activate  # Linux/macOS
# oder
venv\Scripts\activate     # Windows
```

Dann erneut versuchen:
```bash
python3 audio_transcriber.py --input ...
```

### ❌ "externally-managed-environment"

**Lösung:** Virtual Environment nicht aktiviert oder erstellt nicht richtig!

```bash
# Neues venv erstellen
python3 -m venv venv_new

# Aktivieren
source venv_new/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

### ❌ "ffmpeg not found"

**Lösung:** FFmpeg installieren:

```bash
# Linux (Ubuntu/Debian)
sudo apt-get install ffmpeg

# Linux (Fedora)
sudo dnf install ffmpeg

# macOS
brew install ffmpeg

# Windows: https://ffmpeg.org/download.html
```

### ❌ "API error: 401 Unauthorized"

**Lösung:** API-Schlüssel prüfen!

```bash
# Überprüfe, ob API-Key korrekt gesetzt ist
echo $AUDIO_TRANSCRIBE_API_KEY

# Sollte "sk-..." ausgeben, nicht leer sein!
```

## Typische Workflows

### Workflow 1: Einzelne Datei

```bash
python3 audio_transcriber.py --input podcast.mp3
```

### Workflow 2: Ordner mit mehreren Dateien

```bash
python3 audio_transcriber.py --input ./my_podcasts --concurrency 4
```

### Workflow 3: Mit Untertiteln (SRT/VTT)

```bash
python3 audio_transcriber.py \
  --input interview.mp3 \
  --response-format srt \
  --output-dir ./subtitles
```

### Workflow 4: Mit Zusammenfassung

```bash
python3 audio_transcriber.py \
  --input long_podcast.mp3 \
  --summarize
```

## Performance-Tipps

| Parameter | Schneller | Günstiger | Genauer |
|-----------|-----------|-----------|---------|
| `--segment-length` | 900s | 300s | 600s |
| `--overlap` | 0 | 5 | 15 |
| `--concurrency` | 8 | 2 | 4 |
| `--language` | setzen | auto | auto |

## Weitere Informationen

- **Alle Parameter:** `python3 audio_transcriber.py --help`
- **Vollständige Dokumentation:** Siehe `README.md`
- **Mehr Beispiele:** Siehe `examples/EXAMPLES.md`
- **Issues/Bugs:** https://github.com/lucmuss/audio-transcriber/issues

## Nächste Schritte

1. ✓ Installation abgeschlossen
2. ✓ Dry-Run getestet
3. → Jetzt: Echte Transkription starten! 🎙️

```bash
# Beispiel mit deinen Dateien
python3 audio_transcriber.py --input ./deine_audio_dateien
```

Viel Spaß bei der Transkription! 🎉
