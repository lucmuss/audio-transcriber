# Audio Transcriber - Beispiele

Diese Datei enthält praktische Beispiele für die Verwendung des Audio Transcriber Tools.

## 1. Basis-Transkription mit OpenAI

```bash
# Setzen Sie Ihren API-Schlüssel
export AUDIO_TRANSCRIBE_API_KEY="sk-..."

# Transkribieren Sie eine einzelne Datei
python audio_transcriber.py --input podcast.mp3

# Output: ./transcriptions/podcast_full.txt
```

---

## 2. Mehrere Dateien in einem Ordner transkribieren

```bash
python audio_transcriber.py --input ./my_podcasts

# Wird alle MP3, WAV, M4A, etc. Dateien im Ordner finden und transkribieren
```

---

## 3. Mit lokalem Ollama (kostenlos & privat)

```bash
# 1. Starten Sie zuerst Ollama
ollama serve

# 2. In einer anderen Shell: Modell herunterladen (einmalig)
ollama pull neural-chat

# 3. Transkribieren Sie
python audio_transcriber.py \
  --input long_lecture.m4a \
  --base-url http://localhost:11434/v1 \
  --api-key "ollama" \
  --model "neural-chat"
```

---

## 4. SRT-Untertitel für Videos erstellen

```bash
python audio_transcriber.py \
  --input interview.wav \
  --response-format srt \
  --output-dir ./subtitles

# Output: ./subtitles/interview_full.srt
# Können Sie in VLC, FFmpeg, OBS, etc. verwenden
```

---

## 5. VTT-Untertitel für Web

```bash
python audio_transcriber.py \
  --input webinar.mp3 \
  --response-format vtt \
  --output-dir ./web_subtitles

# Output: ./web_subtitles/webinar_full.vtt
# Für HTML5 <track> Tags
```

---

## 6. Mit Sprachdetektion (Deutsch)

```bash
python audio_transcriber.py \
  --input podcast_deutsch.mp3 \
  --language de \
  --detect-language

# Die Sprache wird vom ersten Segment erkannt
# und für alle weiteren Segmente verwendet
```

---

## 7. Mit Zusammenfassung

```bash
python audio_transcriber.py \
  --input long_podcast.mp3 \
  --summarize

# Output:
# - ./transcriptions/long_podcast_full.txt (Vollständige Transkription)
# - ./transcriptions/long_podcast_summary.txt (KI-generierte Zusammenfassung)
```

---

## 8. Kontextuelle Hinweise für bessere Genauigkeit

```bash
python audio_transcriber.py \
  --input tech_conference.mp3 \
  --prompt "This is a tech conference. Key terms: Kubernetes, Docker, microservices. Speakers: John Smith, Jane Doe, Alex Chen"

# Das Modell nutzt diese Info zur besseren Transkription
```

---

## 9. Schnellere Verarbeitung mit größeren Segmenten

```bash
python audio_transcriber.py \
  --input marathon.mp3 \
  --segment-length 900 \
  --overlap 20 \
  --concurrency 8

# - segment-length 900: 15 Min pro Segment (statt 10)
# - overlap 20: 20s Überlappung (statt 10)
# - concurrency 8: 8 parallele Transkriptionen (statt 4)
```

---

## 10. Sparsam bei Kosten (kleine Segmente)

```bash
python audio_transcriber.py \
  --input expensive_audio.mp3 \
  --segment-length 300 \
  --overlap 5 \
  --concurrency 2

# Kleinere Segmente reduzieren Fehler bei langen Pausen
# Weniger Parallelität spart API-Ressourcen
```

---

## 11. JSON-Format für weitere Verarbeitung

```bash
python audio_transcriber.py \
  --input meeting.wav \
  --response-format json

# Output: ./transcriptions/meeting_full.json
# Maschinenlesbar, kann von anderen Tools weiterverarbeitet werden
```

---

## 12. Verbose JSON mit Zeitstempeln

```bash
python audio_transcriber.py \
  --input presentation.mp3 \
  --response-format verbose_json

# Output: ./transcriptions/presentation_full.verbose_json
# Enthält: start/end timestamps, confidence scores, etc.
```

---

## 13. Dry-Run (nur testen, keine API-Aufrufe)

```bash
python audio_transcriber.py \
  --input large_file.mp3 \
  --dry-run

# Zeigt:
# - Wie viele Segmente erstellt werden
# - Geschätzte Verarbeitungszeit
# - Keine API-Aufrufe, keine Kosten!
```

---

## 14. Temporäre Segment-Dateien behalten

```bash
python audio_transcriber.py \
  --input podcast.mp3 \
  --keep-segments

# Normalerweise werden Segment-WAV-Dateien nach dem Transkribieren gelöscht
# Mit --keep-segments bleiben sie im Output-Ordner
```

---

## 15. Verbose Logging für Debugging

```bash
python audio_transcriber.py \
  --input problem_file.mp3 \
  --verbose

# Zeigt detaillierte Debug-Informationen
# Hilft bei Fehlerbehandlung
```

---

## 16. Benutzerdefinierter Output-Ordner

```bash
python audio_transcriber.py \
  --input audio.mp3 \
  --output-dir /mnt/nas/transcriptions/2024

# Können beliebigen Pfad angeben, wird erstellt falls nicht vorhanden
```

---

## 17. Umgebungsvariablen verwenden (fortgeschritten)

```bash
# .env Datei erstellen:
export AUDIO_TRANSCRIBE_API_KEY="sk-..."
export AUDIO_TRANSCRIBE_BASE_URL="https://api.openai.com/v1"
export AUDIO_TRANSCRIBE_MODEL="whisper-1"
export AUDIO_TRANSCRIBE_OUTPUT_DIR="/data/transcriptions"
export AUDIO_TRANSCRIBE_SEGMENT_LENGTH="600"
export AUDIO_TRANSCRIBE_OVERLAP="10"
export AUDIO_TRANSCRIBE_CONCURRENCY="4"

# Dann laden und verwenden:
source .env
python audio_transcriber.py --input podcast.mp3

# Oder direktes Setzen:
AUDIO_TRANSCRIBE_CONCURRENCY=8 python audio_transcriber.py --input podcast.mp3
```

---

## 18. Batch-Verarbeitung mit Script

```bash
#!/bin/bash
# batch_transcribe.sh

export AUDIO_TRANSCRIBE_API_KEY="sk-..."

for file in ./incoming_podcasts/*.mp3; do
  echo "Processing: $file"
  python audio_transcriber.py \
    --input "$file" \
    --output-dir "./results/$(date +%Y%m%d)" \
    --concurrency 4
  
  if [ $? -eq 0 ]; then
    echo "✓ Erfolg: $file"
  else
    echo "✗ Fehler: $file - wird später erneut versucht"
  fi
done
```

Verwendung:
```bash
chmod +x batch_transcribe.sh
./batch_transcribe.sh
```

---

## 19. Mit Groq (schnellere API)

```bash
python audio_transcriber.py \
  --input podcast.mp3 \
  --api-key "gsk_..." \
  --base-url "https://api.groq.com/openai/v1" \
  --model "whisper-large-v3"

# Groq ist oft schneller und manchmal günstiger
```

---

## 20. Mit Together.ai

```bash
python audio_transcriber.py \
  --input conference.mp3 \
  --api-key "..." \
  --base-url "https://api.together.xyz/v1" \
  --model "whisper"
```

---

## 21. Automatisierung mit Cron (täglich)

```bash
# crontab -e
0 2 * * * /home/user/transcribe_daily.sh >> /var/log/transcriber.log 2>&1
```

`transcribe_daily.sh`:
```bash
#!/bin/bash
export AUDIO_TRANSCRIBE_API_KEY="sk-..."

cd /home/user/audio-transcriber
python audio_transcriber.py \
  --input /mnt/incoming_audio \
  --output-dir "/mnt/transcriptions/$(date +%Y-%m-%d)" \
  --concurrency 4 \
  --summarize

# Optional: Archivieren
tar -czf "/archive/transcriptions_$(date +%Y-%m-%d).tar.gz" \
  /mnt/transcriptions/$(date +%Y-%m-%d)
```

---

## 22. Docker-Verwendung

```bash
# Image bauen
docker build -t audio-transcriber .

# Single file
docker run -e AUDIO_TRANSCRIBE_API_KEY="sk-..." \
  -v /local/audio:/audio \
  -v /local/output:/out \
  audio-transcriber --input /audio/podcast.mp3 --output-dir /out

# Ordner
docker run -e AUDIO_TRANSCRIBE_API_KEY="sk-..." \
  -v /local/podcasts:/audio \
  -v /local/output:/out \
  audio-transcriber --input /audio --output-dir /out
```

---

## 23. Robin Audio Beispiel (8 Minuten Segmente mit Deutsch)

```bash
export AUDIO_TRANSCRIBE_API_KEY="sk-..."

python audio_transcriber.py \
  --input examples/robin_audio \
  --api-key "$AUDIO_TRANSCRIBE_API_KEY" \
  --base-url https://api.openai.com/v1 \
  --model gpt-4o-mini-transcribe \
  --language de \
  --segment-length 480 \
  --overlap 15 \
  --output-dir ./transcriptions

# Erklärung der Parameter:
# - --input examples/robin_audio: Alle Audiodateien in diesem Ordner
# - --segment-length 480: 8 Minuten pro Segment (480 Sekunden)
# - --overlap 15: 15 Sekunden Überlappung zwischen Segmenten
# - --language de: Deutsche Sprache
# - --model gpt-4o-mini-transcribe: OpenAI Modell für Transkription
```

---

## 24. Komplexes Beispiel: Production Setup

```bash
#!/bin/bash
set -euo pipefail

# Konfiguration
API_KEY="${AUDIO_TRANSCRIBE_API_KEY:?Fehler: API_KEY nicht gesetzt}"
INPUT_DIR="/mnt/queue"
OUTPUT_DIR="/mnt/transcriptions"
ARCHIVE_DIR="/archive"
LOG_FILE="/var/log/transcriber_$(date +%Y%m%d).log"

# Logging
exec 1> >(tee -a "$LOG_FILE")
exec 2>&1

echo "===================="
echo "Transcriber started: $(date)"
echo "===================="

# Verarbeitung
if python audio_transcriber.py \
  --input "$INPUT_DIR" \
  --output-dir "$OUTPUT_DIR" \
  --concurrency 6 \
  --verbose \
  --summarize; then
  
  echo "✓ Transkription erfolgreich"
  
  # Archivieren
  tar -czf "$ARCHIVE_DIR/transcriptions_$(date +%Y%m%d_%H%M%S).tar.gz" \
    "$OUTPUT_DIR"
  
  # Cleanup
  rm -rf "$OUTPUT_DIR"/*
  
else
  echo "✗ Fehler bei Transkription"
  exit 1
fi

echo "===================="
echo "Transcriber finished: $(date)"
echo "===================="
```

---

## Tipps & Tricks

### 1. Resume-Mechanismus
Das Tool überspringt automatisch bereits transkribierte Dateien. Sie können es einfach erneut starten!

```bash
# Start
python audio_transcriber.py --input ./100_podcasts

# Unterbrechung nach 20 Dateien (<Ctrl+C>)

# Restart - fährt automatisch fort!
python audio_transcriber.py --input ./100_podcasts
```

### 2. Kosten überwachen
```bash
# Am Ende zeigt das Tool:
# Estimated cost: $0.001234 (OpenAI whisper-1)
```

### 3. Performance-Messung
```bash
time python audio_transcriber.py --input podcast.mp3
# real    2m34.123s
# user    0m45.321s
# sys     0m12.456s
```

### 4. Fehlerbehandlung
```bash
python audio_transcriber.py --input podcast.mp3 || {
  echo "Fehler! Status: $?"
  # Email senden, Alert auslösen, etc.
}
```

---

## Support

Für Probleme oder Fragen:
- GitHub Issues: https://github.com/lucmuss/audio-transcriber/issues
- Dokumentation: https://github.com/lucmuss/audio-transcriber/blob/main/README.md
- Troubleshooting: Siehe README.md
