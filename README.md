# Audio Transcriber 🎙️

Ein professionelles Python-Tool zur automatischen Transkription großer Audio-Dateien und ganzer Ordner mittels OpenAI-kompatibler Speech-to-Text-APIs. Optimiert für lange Podcasts, Interviews, Vorträge und Meetings.

**Hauptmerkmale:**
- ✅ Automatische Segmentierung großer Audio-Dateien
- ✅ Parallele Transkription mehrerer Segmente gleichzeitig
- ✅ Unterstützung für alle gängigen Audio-Formate (MP3, WAV, FLAC, M4A, OGG, AAC, WMA, MP4)
- ✅ Automatische Sprachdetektion
- ✅ Mehrere Output-Formate (Text, JSON, SRT, VTT, Verbose JSON)
- ✅ Intelligentes Zusammenführen von Segmenten mit Duplikat-Entfernung
- ✅ OpenAI-kompatibel (works with OpenAI, Ollama, Groq, LocalAI, Azure, Together.ai, etc.)
- ✅ Wiederaufnahme-Fähigkeit (Resume von unterbrochenen Prozessen)
- ✅ Detaillierte Fortschrittsanzeige und Statistiken
- ✅ Optionale Zusammenfassungen
- ✅ Kostenabschätzung für OpenAI
- ✅ Dry-Run-Modus zum Testen

---

## Installation

### 1. Virtual Environment erstellen (empfohlen)

```bash
git clone https://github.com/lucmuss/audio-transcriber.git
cd audio-transcriber

# Virtual Environment erstellen
python3 -m venv venv

# Virtual Environment aktivieren
source venv/bin/activate  # Linux/macOS
# oder auf Windows:
# venv\Scripts\activate

# Python-Abhängigkeiten installieren
pip install -r requirements.txt
```

### 2. Alternativ: System-Installation ohne venv

Wenn Sie kein venv verwenden möchten (nicht empfohlen):

```bash
pip install --break-system-packages -r requirements.txt
```

### 3. FFmpeg installieren

Das Tool benötigt FFmpeg zur Audio-Verarbeitung. Installieren Sie es für Ihr Betriebssystem:

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
- Download von https://ffmpeg.org/download.html
- Oder über Chocolatey: `choco install ffmpeg`
- Oder über Scoop: `scoop install ffmpeg`

**Überprüfung:**
```bash
ffmpeg -version
```

### 3. API-Konfiguration

**Option A: OpenAI (kostenpflichtig)**

```bash
export AUDIO_TRANSCRIBE_API_KEY="sk-..."
```

**Option B: Lokales Ollama (kostenlos, privat)**

1. Ollama installieren: https://ollama.ai
2. Ollama starten: `ollama serve`
3. Modell herunterladen: `ollama pull llama2` (oder anderes Modell)
4. Tool mit lokaler URL verwenden (siehe Beispiele unten)

---

## Verwendungsbeispiele

### Einfaches Beispiel: Einzelne Datei mit OpenAI

```bash
export AUDIO_TRANSCRIBE_API_KEY="sk-..."
python audio_transcriber.py --input podcast.mp3
```

Output: `./transcriptions/podcast_full.txt`

### Ordner mit mehreren Dateien

```bash
python audio_transcriber.py --input ./my_audio_folder
```

Alle Audio-Dateien im Ordner und allen Unterordnern werden transkribiert.

### Mit lokalem Ollama (kostenlos & privat)

```bash
# Ollama läuft auf localhost:11434
python audio_transcriber.py \
  --input lecture.m4a \
  --base-url http://localhost:11434/v1 \
  --api-key "ollama" \
  --model "neural-chat"
```

### SRT-Untertitel generieren

```bash
python audio_transcriber.py \
  --input meeting.wav \
  --response-format srt \
  --output-dir ./subtitles
```

Output: `./subtitles/meeting_full.srt` (mit Zeitstempeln)

### Mit Sprachdetektion und Deutsche Sprache

```bash
python audio_transcriber.py \
  --input interview.mp3 \
  --language de \
  --detect-language
```

Die Sprache wird vom ersten Segment erkannt und für alle weiteren Segmente verwendet.

### Mit Zusammenfassung

```bash
python audio_transcriber.py \
  --input long_podcast.mp3 \
  --summarize \
  --output-dir ./results
```

Output:
- `./results/long_podcast_full.txt` (Vollständige Transkription)
- `./results/long_podcast_summary.txt` (Zusammenfassung)

### Benutzerdefinierte Kontextinformationen

```bash
python audio_transcriber.py \
  --input tech_talk.mp3 \
  --prompt "This is about Kubernetes, Docker, microservices. Proper names: John Smith, React.js"
```

Dies hilft dem Modell, Fachbegriffe und Namen korrekt zu transkribieren.

### Angepasste Segmentierung

```bash
python audio_transcriber.py \
  --input marathon_recording.mp3 \
  --segment-length 300 \
  --overlap 5 \
  --concurrency 8
```

- `--segment-length 300`: Jedes Segment 5 Minuten (Standard: 10)
- `--overlap 5`: 5 Sekunden Überlappung zwischen Segmenten
- `--concurrency 8`: 8 Segmente gleichzeitig transkribieren

### Dry-Run (nur Segmentierung simulieren)

```bash
python audio_transcriber.py \
  --input podcast.mp3 \
  --dry-run
```

Zeigt, wie viele Segmente erstellt würden, ohne API-Aufrufe zu tätigen.

### Temporäre Segment-Dateien behalten

```bash
python audio_transcriber.py \
  --input podcast.mp3 \
  --keep-segments
```

Standardmäßig werden temporäre Segment-WAV-Dateien nach erfolgreicher Verarbeitung gelöscht.

### Beispiel: Robin Audio (8 Minuten Segmente)

```bash
export AUDIO_TRANSCRIBE_API_KEY="sk-"

python audio_transcriber.py \
  --input examples/robin_audio \
  --api-key "$AUDIO_TRANSCRIBE_API_KEY" \
  --base-url https://api.openai.com/v1 \
  --model gpt-4o-mini-transcribe \
  --language de \
  --segment-length 480 \
  --overlap 15 \
  --output-dir ./transcriptions
```

- `--segment-length 480`: 8 Minuten pro Segment
- `--overlap 15`: 15 Sekunden Überlappung
- `--language de`: Deutsche Sprache

---

## Command-Line Optionen (Vollständige Referenz)

| Option | Typ | Standard | Beschreibung | Umgebungsvariable |
|--------|-----|----------|-------------|-------------------|
| `--input` | str | *(erforderlich)* | Pfad zu Audio-Datei oder Ordner | - |
| `--output-dir` | str | `./transcriptions` | Output-Ordner für Transkriptionen | `AUDIO_TRANSCRIBE_OUTPUT_DIR` |
| `--segment-length` | int | 600 | Segmentlänge in Sekunden (Standard: 10 Min) | `AUDIO_TRANSCRIBE_SEGMENT_LENGTH` |
| `--overlap` | int | 10 | Überlappung zwischen Segmenten (Sekunden) | `AUDIO_TRANSCRIBE_OVERLAP` |
| `--model` | str | `whisper-1` | Whisper-Modellname | `AUDIO_TRANSCRIBE_MODEL` |
| `--api-key` | str | - | OpenAI API-Schlüssel | `AUDIO_TRANSCRIBE_API_KEY` |
| `--base-url` | str | `https://api.openai.com/v1` | API Base-URL (für lokale Instanzen) | `AUDIO_TRANSCRIBE_BASE_URL` |
| `--language` | str | None | ISO-639-1 Sprachcode (z.B. `de`, `en`) | - |
| `--detect-language` | bool | True | Automatische Sprachdetektion | - |
| `--no-detect-language` | bool | - | Sprachdetektion deaktivieren | - |
| `--response-format` | str | `text` | Output-Format: `text`, `json`, `srt`, `vtt`, `verbose_json` | - |
| `--concurrency` | int | 4 | Anzahl gleichzeitiger Segment-Transkriptionen | `AUDIO_TRANSCRIBE_CONCURRENCY` |
| `--temperature` | float | 0.0 | Modell-Temperatur (0.0-1.0) | - |
| `--prompt` | str | None | Initialer Prompt für Kontextinformation | - |
| `--keep-segments` | flag | False | Temporäre Segment-Dateien behalten | - |
| `--summarize` | flag | False | Zusammenfassung generieren (zusätzliche API-Aufrufe) | - |
| `--dry-run` | flag | False | Nur Segmentierung simulieren, keine API-Aufrufe | - |
| `--verbose` | flag | False | Detaillierte Debug-Logs anzeigen | - |

---

## Audio-Format-Support

Alle Formate, die von `ffmpeg` und `pydub` unterstützt werden, funktionieren:

- **Container:** MP3, WAV, M4A, OGG, FLAC, AAC, WMA, MP4 (mit Audio-Track)
- **Codecs:** MP3, AAC, FLAC, Opus, Vorbis, PCM, WMA

---

## Kosten und Performance-Tipps

### OpenAI Whisper-1 Preise
- **Preis:** $0.0001 pro Minute (Stand 2024)
- **Berechnung:** Video-Länge (Minuten) × $0.0001
- **Beispiel:** 60-Minuten-Podcast ≈ $0.006

Das Tool zeigt am Ende eine Kostenabschätzung als "Estimated cost".

### Performance-Optimierungen

1. **Concurrency erhöhen** (wenn API-Limits erlauben)
   ```bash
   --concurrency 8  # Standard: 4
   ```

2. **Segmentlänge anpassen** (größere Segmente = weniger API-Aufrufe)
   ```bash
   --segment-length 900  # 15 Minuten statt 10
   ```

3. **Lokale Modelle verwenden** (Ollama, LocalAI)
   - Kostenlos und unbegrenzt
   - Schneller bei lokaler Hardware
   - Datenschutz (keine Cloud-Uploads)

4. **Batch-Verarbeitung**
   ```bash
   python transcribe_audio.py --input ./folder_with_100_files
   # Alle Dateien sequenziell, mit Parallelisierung pro Datei
   ```

### Speicherverbrauch

- **Tmp-Segmente:** ~20MB pro 10-Minuten-Segment (WAV-Format)
- **Output-Dateien:** ~1% der Originaldateigröße (Text)
- **Beispiel:** 1GB MP3-Datei ≈ 50-100 Tmp-Dateien × 20MB (bereinigt nach Transkription)

---

## Ausgabe-Formate

### 1. Text (Standard)
```
Das ist ein Transkriptionsergebnis. Es ist vollständig und lesbar.
```
**Datei:** `podcast_full.txt`

### 2. JSON
```json
{
  "segments": [
    {"id": 1, "text": "Das ist ein Segment."},
    {"id": 2, "text": "Das ist Segment 2."}
  ],
  "language": "de"
}
```
**Datei:** `podcast_full.json`

### 3. Verbose JSON (mit Timestamps)
```json
{
  "segments": [
    {
      "id": 1,
      "seek": 0,
      "start": 0.0,
      "end": 5.2,
      "text": "Das ist ein Segment.",
      "avg_logprob": -0.35,
      "compression_ratio": 1.2,
      "no_speech_prob": 0.001
    }
  ]
}
```
**Datei:** `podcast_full.verbose_json`

### 4. SRT (SubRip)
```
1
00:00:00,000 --> 00:00:05,200
Das ist ein Segment.

2
00:00:05,200 --> 00:00:10,500
Das ist Segment 2.
```
**Datei:** `podcast_full.srt`

### 5. VTT (WebVTT)
```
WEBVTT

00:00:00.000 --> 00:00:05.200
Das ist ein Segment.

00:00:05.200 --> 00:00:10.500
Das ist Segment 2.
```
**Datei:** `podcast_full.vtt`

---

## Segmentierung und Überlappung erklärt

### Warum Segmentierung?
- **OpenAI Whisper API:** Max. 25MB pro Anfrage
- **Große Dateien:** 1GB Video → 40-50 Segmente
- **Unsicherheit bei Segmentgrenzen:** Wörter können "abgeschnitten" werden

### Überlappungsmechanismus
```
Audio-Timeline:
[========== Segment 1 (600s) ==========]
                    [Overlap (10s)]
                    [========== Segment 2 (600s) ==========]
                                      [Overlap (10s)]
                                      [========== Segment 3 ==========]

Overlap-Bereich:
Segment 1 Ende: "...der König sprach mit großer..."
Segment 2 Anfang: "...Autorität. Der König sprach mit großer..."
                 ↑ Duplikat erkannt und entfernt
```

### Parameter-Auswirkungen
- **--segment-length 600** (Standard)
  - Segmente: ~10 Minuten (ausreichend für Kontext)
  - API-Aufrufe: Weniger, schneller ✓
  - RAM: Moderate Nutzung ✓

- **--segment-length 300** (Kleine Segmente)
  - Segmente: ~5 Minuten (schnelle Verarbeitung)
  - API-Aufrufe: Mehr, höhere Kosten
  - Kontextverlust: Wahrscheinlich

- **--overlap 10** (Standard)
  - Überlappung: Reduziert harte Schnitte
  - Duplikat-Entfernung: Funktioniert gut ✓

---

## Fehlerbehandlung und Troubleshooting

### Fehler: `ffmpeg not found`
```
ERROR: ffmpeg executable not found. Please install FFmpeg.
```
**Lösung:** FFmpeg installieren (siehe Installation oben)

### Fehler: `ImportError: No module named 'pydub'`
```bash
pip install -r requirements.txt
```

### Fehler: `API error: 401 Unauthorized`
```
ERROR: API error: 401 Unauthorized
```
**Lösungen:**
- API-Schlüssel falsch: `export AUDIO_TRANSCRIBE_API_KEY="sk-..."`
- API-Quota ausgeschöpft: Warten Sie oder erhöhen Sie Ihr OpenAI-Limit
- Abgelaufener Schlüssel: Generieren Sie einen neuen auf https://platform.openai.com/api-keys

### Fehler: `No audio files found`
```
ERROR: No audio files found
```
**Lösungen:**
- Pfad prüfen: `python transcribe_audio.py --input "$(pwd)/file.mp3"`
- Dateiformat prüfen: Ist es `.mp3` oder `.MP3`? (Groß-/Kleinschreibung)
- Berechtigungen: `chmod +r file.mp3`

### Fehler: `Connection refused: http://localhost:11434/v1`
```
ERROR: Connection refused
```
**Lösung:** Ollama erst starten: `ollama serve`

### Timeout bei großen Dateien
```
TIMEOUT ERROR: Request timed out after 30s
```
**Lösungen:**
- Segment-Länge reduzieren: `--segment-length 300`
- Concurrency reduzieren: `--concurrency 2`
- Lokales Modell verwenden (schneller)

### Speicherproblem
```
MemoryError: Unable to allocate X GB
```
**Lösungen:**
- Weniger Concurrency: `--concurrency 1`
- Kleinere Segment-Länge: `--segment-length 300`
- RAM freigeben (andere Programme schließen)

---

## Erweiterte Anwendungsfälle

### 1. Automatischer Workflow (Cron-Job)

`./_transcribe_daily.sh:`
```bash
#!/bin/bash
export AUDIO_TRANSCRIBE_API_KEY="sk-..."

python /opt/audio-transcriber/transcribe_audio.py \
  --input /mnt/incoming_podcasts \
  --output-dir "/mnt/transcriptions_$(date +%Y-%m-%d)" \
  --concurrency 4 \
  --summarize

# Archivieren
tar -czf "/archive/transcriptions_$(date +%Y-%m-%d).tar.gz" /mnt/transcriptions_*
```

Crontab:
```bash
0 2 * * * bash /_transcribe_daily.sh >> /_transcribe.log 2>&1
```

### 2. Server-Setup (als Service)

`/etc/systemd/system/transcriber.service:`
```ini
[Unit]
Description=Audio Transcriber Service
After=network.target

[Service]
Type=simple
User=audio-transcriber
WorkingDirectory=/opt/audio-transcriber
ExecStart=/usr/bin/python3 /opt/audio-transcriber/transcribe_audio.py \
  --input /mnt/queue \
  --output-dir /mnt/transcriptions
Restart=on-failure
RestartSec=60

Environment="AUDIO_TRANSCRIBE_API_KEY=sk-..."
Environment="AUDIO_TRANSCRIBE_CONCURRENCY=6"

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start transcriber
sudo systemctl enable transcriber
sudo journalctl -u transcriber -f  # Logs anschauen
```

### 3. Docker-Container

`Dockerfile:`
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY transcribe_audio.py .

ENTRYPOINT ["python", "transcribe_audio.py"]
```

Verwendung:
```bash
docker build -t audio-transcriber .
docker run -e AUDIO_TRANSCRIBE_API_KEY="sk-..." \
  -v /local/audio:/audio \
  -v /local/output:/transcriptions \
  audio-transcriber --input /audio --output-dir /transcriptions
```

### 4. Batch-Verarbeitung mit Resume

```bash
#!/bin/bash
for folder in ./audio_collection/*; do
  echo "Processing $folder..."
  python transcribe_audio.py \
    --input "$folder" \
    --output-dir "./transcriptions/$(basename $folder)" \
    --verbose
  
  if [ $? -ne 0 ]; then
    echo "Failed: $folder - will retry next run (Resume enabled)"
  fi
done
```

Das Tool überspringt bereits transkribierte Dateien automatisch (Resume-Fähigkeit).

---

## Datenschutz und Sicherheit

### OpenAI (Cloud)
- ⚠️ Audio wird an OpenAI-Server übertragen
- ✓ OpenAI löscht Daten nach 30 Tagen (gemäß Datenschutzerklärung)
- 🔒 Verwenden Sie nur für nicht-vertrauliche Inhalte

### Ollama / LocalAI (Lokal)
- ✅ Audio bleibt auf Ihrer Maschine
- ✅ Keine Internet-Verbindung erforderlich
- ✅ Ideal für sensitive/konfidenzielle Inhalte
- ⚠️ Erfordert lokale GPU/CPU-Ressourcen

### Beste Praktiken
1. **API-Schlüssel niemals in Code committen**
   ```bash
   # .gitignore
   .env
   *.log
   transcriptions/
   ```

2. **Umgebungsvariablen verwenden**
   ```bash
   # .env (nicht committen!)
   export AUDIO_TRANSCRIBE_API_KEY="sk-..."
   ```

3. **Lokale Modelle für sensible Daten bevorzugen**

---

## Lizenz

MIT License - Siehe [LICENSE](LICENSE) für Details.

---

## Beitragen

Beiträge sind willkommen! Bitte erstellen Sie einen Fork, eine Feature Branch und einen Pull Request.

```bash
git clone https://github.com/yourusername/audio-transcriber.git
git checkout -b feature/my-feature
git commit -am "Add my feature"
git push origin feature/my-feature
```

---

## Support und Fragen

- 📧 Issues auf GitHub: https://github.com/lucmuss/audio-transcriber/issues
- 📚 Dokumentation: Diese README
- 🆘 Häufig gestellte Fragen: Siehe Troubleshooting oben

---

## Dankbarkeiten

Gebaut mit:
- [OpenAI Python Client](https://github.com/openai/openai-python)
- [pydub](https://github.com/jiaaro/pydub) für Audio-Verarbeitung
- [tqdm](https://github.com/tqdm/tqdm) für Fortschrittsanzeigen

---

**Viel Erfolg bei der Transkription! 🎙️✨**
