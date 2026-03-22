# 🚀 Quick Start Guide

Schnelleste Möglichkeit, um mit Audio Transcriber zu starten!

## Installation (2 Minuten)

### Option 1: Direkt mit uv (empfohlen) ⭐

```bash
# 1. Klone das Repository
git clone https://github.com/lucmuss/audio-transcriber.git
cd audio-transcriber

# 2. Virtuelle Umgebung und Abhängigkeiten einrichten
uv venv
uv sync

# 3. Done! ✓
```

### Option 2: Mit Justfile (optional)

```bash
git clone https://github.com/lucmuss/audio-transcriber.git
cd audio-transcriber

# just installieren, z. B. via Paketmanager
# Danach Projekt einrichten
just setup
```

Die `just`-Kommandos sind nur ein Komfort-Layer. Alle wichtigen Schritte funktionieren auch direkt mit `uv`.

## Erste Schritte

### 1. API-Key setzen

```bash
export AUDIO_TRANSCRIBE_API_KEY="sk-..."
```

### 2. Dry-Run testen (keine Kosten!)

```bash
uv run audio-transcriber \
  --input examples/tests/test_file.mp3 \
  --language de \
  --dry-run
```

Output: Zeigt Konfiguration und wie viele Dateien gefunden wurden

**Neue Standardwerte (2026):**
- Segment-Länge: 300 Sekunden (5 Minuten)
- Überlappung: 3 Sekunden
- Parallelität: 8 gleichzeitige Transkriptionen
- Modell: gpt-4o-mini-transcribe

### 3. Echte Transkription starten

```bash
uv run audio-transcriber \
  --input examples/tests/test_file.mp3 \
  --language de \
  --output-dir ./transcriptions
```

Output: 
- `./transcriptions/test_file_mp3_full.text` (komplette Transkription)
- Live-Fortschritt mit ETA und Kostenberechnung
- Detaillierte Zusammenfassung am Ende

### 4. GUI starten (Alternative)

```bash
uv run audio-transcriber-gui
```

Die GUI bietet alle Features mit einer benutzerfreundlichen Oberfläche!

## Häufige Fehler & Lösungen

### ❌ "ModuleNotFoundError: No module named 'pydub'"

**Lösung:** Abhängigkeiten installieren oder über uv ausführen.

```bash
uv sync
uv run audio-transcriber --input podcast.mp3
```

### ❌ "externally-managed-environment"

**Lösung:** uv venv nutzen und Abhängigkeiten sauber installieren.

```bash
uv venv
uv sync
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
uv run audio-transcriber --input podcast.mp3
```

### Workflow 2: Ordner mit mehreren Dateien

```bash
uv run audio-transcriber --input ./my_podcasts --concurrency 4
```

### Workflow 3: Mit Untertiteln (SRT/VTT)

```bash
uv run audio-transcriber \
  --input interview.mp3 \
  --response-format srt \
  --output-dir ./subtitles
```

### Workflow 4: Mit AI-Zusammenfassung

```bash
uv run audio-transcriber \
  --input long_podcast.mp3 \
  --summarize
```

### Workflow 5: Speaker Diarization (Sprecher-Erkennung)

```bash
uv run audio-transcriber \
  --input meeting.mp3 \
  --enable-diarization \
  --num-speakers 3
```

### Workflow 6: Export zu Word/Markdown/LaTeX

```bash
uv run audio-transcriber \
  --input interview.mp3 \
  --export docx md latex \
  --export-title "Interview Transkription" \
  --export-author "Dein Name"
```

### Workflow 7: Kompletter Workflow (All-in-One)

```bash
uv run audio-transcriber \
  --input meeting.mp3 \
  --enable-diarization \
  --summarize \
  --export docx md \
  --export-title "Team Meeting Q1 2026"
```

## Performance-Tipps

| Parameter | Schneller | Günstiger | Genauer |
|-----------|-----------|-----------|---------|
| `--segment-length` | 900s | 300s (Standard) | 600s |
| `--overlap` | 0 | 3 (Standard) | 15 |
| `--concurrency` | 12+ | 4 | 8 (Standard) |
| `--language` | setzen | auto | auto |
| `--analyze-duration` | weglassen | weglassen | verwenden |

**Neue Standardwerte (2026):**
- Segment-Länge: 300s (5 Minuten) - optimale Balance zwischen Geschwindigkeit und Kosten
- Überlappung: 3 Sekunden - minimiert Kontextverlust
- Parallelität: 8 - schnellere Verarbeitung durch mehr gleichzeitige Segmente
- Segmente werden standardmäßig behalten (use `--no-keep-segments` um sie zu löschen)
- Dateien werden standardmäßig neu verarbeitet (use `--skip-existing` um existierende zu überspringen)

**Hinweis:** Audio-Analyse mit `--analyze-duration` dauert länger beim Start, bietet aber bessere ETA-Schätzungen während der Verarbeitung.

## Neue Features (2026)

### 🎙️ Speaker Diarization
Automatische Sprecher-Erkennung:
```bash
uv run audio-transcriber --input meeting.mp3 --enable-diarization
```

### 📝 AI Summarization
Automatische Zusammenfassungen:
```bash
uv run audio-transcriber --input podcast.mp3 --summarize
```

### 📄 Document Export
Export zu professionellen Formaten:
```bash
uv run audio-transcriber --input lecture.mp3 --export docx md latex
```

### 📊 Live Progress Tracking
- Echtzeit ETA-Berechnung
- Durchsatz-Metriken (Minuten/Sekunde)
- Live-Kostenberechnung

## Weitere Informationen

- **Alle Parameter:** `uv run audio-transcriber --help`
- **Vollständige Dokumentation:** Siehe `README.md`
- **GUI-Anleitung:** Siehe `GUI_GUIDE.md`
- **Mehr Beispiele:** Siehe `docs/USAGE_EXAMPLES.md`
- **Issues/Bugs:** https://github.com/lucmuss/audio-transcriber/issues

## Nächste Schritte

1. ✓ Installation abgeschlossen
2. ✓ Dry-Run getestet
3. → Jetzt: Echte Transkription starten! 🎙️

```bash
# Beispiel mit deinen Dateien
uv run audio-transcriber --input ./deine_audio_dateien

# Oder die GUI verwenden
uv run audio-transcriber-gui
```

Viel Spaß bei der Transkription! 🎉
