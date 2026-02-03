# Speaker Diarization Feature

## Übersicht

Das Speaker Diarization Feature ermöglicht die automatische Erkennung und Kennzeichnung verschiedener Sprecher in Audio-Aufnahmen. Dieses Feature nutzt das `gpt-4o-transcribe-diarize` Modell von OpenAI.

---

## ✨ Features

- ✅ Automatische Sprechererkennung
- ✅ Kennzeichnung von Sprecherwechseln
- ✅ Optionale Benennung bekannter Sprecher
- ✅ Unterstützung für Sprecher-Referenz-Audio
- ✅ Zeitstempel für jeden Sprecherbeitrag
- ✅ Dual-Output: JSON + Lesbare Textversion

---

## 🚀 Verwendung über die Kommandozeile

### Basis-Verwendung

Einfache Sprecherkennung ohne zusätzliche Parameter:

```bash
audio-transcriber --input meeting.mp3 --enable-diarization
```

### Mit erwarteter Sprecheranzahl

Wenn Sie wissen, wie viele Sprecher erwartet werden:

```bash
audio-transcriber --input interview.mp3 --enable-diarization --num-speakers 2
```

### Mit bekannten Sprecher-Namen

Benennen Sie bekannte Sprecher im Voraus:

```bash
audio-transcriber --input podcast.mp3 --enable-diarization \
  --known-speaker-names Alice Bob
```

### Mit Sprecher-Referenz-Audio

Für noch bessere Genauigkeit können Sie Referenz-Audiodateien angeben:

```bash
audio-transcriber --input meeting.wav --enable-diarization \
  --known-speaker-names "Agent" \
  --known-speaker-references agent.wav
```

**Wichtig:** Die Reihenfolge bei `--known-speaker-references` muss mit `--known-speaker-names` übereinstimmen!

### Vollständiges Beispiel

```bash
audio-transcriber --input conference.mp3 \
  --enable-diarization \
  --num-speakers 3 \
  --known-speaker-names "Alice" "Bob" "Charlie" \
  --known-speaker-references alice_sample.wav bob_sample.wav charlie_sample.wav \
  --output-dir ./transcriptions \
  --segment-length 600 \
  --summarize
```

---

## 📋 CLI-Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `--enable-diarization` | Flag | `False` | Aktiviert Speaker Diarization |
| `--num-speakers` | Integer | Auto | Erwartete Anzahl der Sprecher |
| `--known-speaker-names` | Liste | None | Namen bekannter Sprecher |
| `--known-speaker-references` | Liste | None | Pfade zu Referenz-Audiodateien |

---

## 📁 Output-Struktur

Bei aktivierter Diarization werden **zwei Dateien** erstellt:

### 1. Diarized JSON (Roh-Format)
```
transcriptions/
└── meeting_mp3_full.diarized_json
```

Enthält strukturierte JSON-Daten mit detaillierten Speaker-Informationen, Zeitstempeln und Text.

### 2. Readable Text (Human-Friendly)
```
transcriptions/
└── meeting_mp3_full_readable.txt
```

Automatisch formatierte, lesbare Version:

```
Speaker 1: [00:00-00:15] Guten Morgen allerseits. Willkommen zu unserem wöchentlichen Meeting.

Speaker 2: [00:16-00:28] Danke! Ich möchte gleich mit unserem ersten Thema beginnen.

Speaker 1: [00:29-00:45] Sehr gerne. Bitte fahren Sie fort.
```

---

## 🔧 Technische Details

### Verwendetes Modell

Bei aktivierter Diarization wird automatisch das Modell gewechselt:
- **Standard:** `whisper-1`
- **Mit Diarization:** `gpt-4o-transcribe-diarize`

### Response Format

Die Diarization erzwingt automatisch das Format:
- **Format:** `diarized_json`
- **Chunking Strategy:** `auto`

### API-Aufruf-Struktur

Intern wird folgender API-Aufruf verwendet:

```python
response = client.audio.transcriptions.create(
    model="gpt-4o-transcribe-diarize",
    file=audio_file,
    response_format="diarized_json",
    chunking_strategy="auto",
    extra_body={
        "num_speakers": 2,  # optional
        "known_speaker_names": ["Alice", "Bob"],  # optional
        "known_speaker_references": ["data:audio/wav;base64,..."],  # optional
    }
)
```

---

## 💡 Best Practices

### 1. Referenz-Audio verwenden

Für beste Ergebnisse:
- **Länge:** 5-30 Sekunden pro Sprecher
- **Qualität:** Klare Stimme, wenig Hintergrundgeräusch
- **Format:** WAV, MP3, oder M4A

### 2. Sprecher-Anzahl angeben

Wenn bekannt, verbessert `--num-speakers` die Genauigkeit:
- Bei **Interviews:** `--num-speakers 2`
- Bei **Meetings:** Anzahl der Teilnehmer angeben
- Bei **Podcasts:** Anzahl der Hosts + Gäste

### 3. Segmentierung beachten

Bei langen Aufnahmen:
- Diarization funktioniert **pro Segment**
- Standard: 600 Sekunden (10 Minuten)
- Kann mit `--segment-length` angepasst werden

### 4. Kosten im Blick behalten

Das `gpt-4o-transcribe-diarize` Modell kann teurer sein als Standard Whisper. Überprüfen Sie die aktuellen Preise in der OpenAI-Dokumentation.

---

## 🎯 Anwendungsfälle

### Interviews
```bash
audio-transcriber --input interview.mp3 \
  --enable-diarization \
  --num-speakers 2 \
  --known-speaker-names "Interviewer" "Guest"
```

### Business Meetings
```bash
audio-transcriber --input team_meeting.mp3 \
  --enable-diarization \
  --summarize \
  --summary-prompt "Fasse das Meeting zusammen und liste Action Items auf."
```

### Podcasts
```bash
audio-transcriber --input podcast_episode.mp3 \
  --enable-diarization \
  --num-speakers 3 \
  --known-speaker-names "Host1" "Host2" "Guest"
```

### Call Center / Customer Support
```bash
audio-transcriber --input support_call.wav \
  --enable-diarization \
  --known-speaker-names "Agent" "Customer" \
  --known-speaker-references agent_voice.wav
```

### Gerichtsverhandlungen
```bash
audio-transcriber --input hearing.mp3 \
  --enable-diarization \
  --num-speakers 5 \
  --known-speaker-names "Judge" "Prosecutor" "Defense" "Witness" "Clerk"
```

---

## 🔍 Diarized JSON Format

Das `diarized_json` Format enthält ein `segments` Array:

```json
{
  "segments": [
    {
      "speaker": "Speaker 1",
      "text": "Guten Morgen allerseits.",
      "start": 0.0,
      "end": 2.5
    },
    {
      "speaker": "Speaker 2",
      "text": "Guten Morgen!",
      "start": 2.6,
      "end": 3.8
    }
  ]
}
```

### Felder

- **speaker:** Name des Sprechers (z.B. "Speaker 1" oder "Alice")
- **text:** Gesprochener Text
- **start:** Startzeit in Sekunden
- **end:** Endzeit in Sekunden

---

## 🐛 Troubleshooting

### Problem: Sprecher werden nicht korrekt erkannt

**Lösung:**
1. Referenz-Audio hinzufügen mit `--known-speaker-references`
2. Anzahl der Sprecher mit `--num-speakers` vorgeben
3. Audioqualität verbessern (weniger Hintergrundgeräusche)

### Problem: "Model not found" Fehler

**Lösung:**
- Stellen Sie sicher, dass Ihr OpenAI-Account Zugriff auf `gpt-4o-transcribe-diarize` hat
- Überprüfen Sie die API-Key-Berechtigungen

### Problem: Zu viele/wenige Sprecher erkannt

**Lösung:**
- Nutzen Sie `--num-speakers` um die erwartete Anzahl vorzugeben
- Bei schwierigen Aufnahmen: Referenz-Audio verwenden

### Problem: Referenz-Audio wird nicht akzeptiert

**Lösung:**
- Überprüfen Sie das Audio-Format (WAV, MP3, M4A unterstützt)
- Stellen Sie sicher, dass die Datei existiert und lesbar ist
- Pfad korrekt angeben (absolute oder relative Pfade)

---

## 📊 Vergleich: Mit vs. Ohne Diarization

### Ohne Diarization
```
Guten Morgen allerseits. Willkommen zu unserem Meeting. 
Danke! Ich möchte gleich mit dem ersten Thema beginnen. 
Sehr gerne. Bitte fahren Sie fort.
```

### Mit Diarization
```
Speaker 1: [00:00-00:15] Guten Morgen allerseits. Willkommen zu unserem Meeting.

Speaker 2: [00:16-00:28] Danke! Ich möchte gleich mit dem ersten Thema beginnen.

Speaker 1: [00:29-00:45] Sehr gerne. Bitte fahren Sie fort.
```

---

## 🔗 Integration mit anderen Features

### Mit Summarization
```bash
audio-transcriber --input meeting.mp3 \
  --enable-diarization \
  --summarize \
  --summary-prompt "Erstelle eine Zusammenfassung und ordne Beiträge den Sprechern zu."
```

### Mit Segmentierung
```bash
audio-transcriber --input long_conference.mp3 \
  --enable-diarization \
  --segment-length 900 \
  --overlap 15
```

### Mit verschiedenen Output-Formaten
**Hinweis:** Diar

ization überschreibt das Response-Format zu `diarized_json`. Für andere Formate (SRT, VTT) deaktivieren Sie Diarization.

---

## 💰 Kosten-Abschätzung

Die Kosten für Diarization hängen ab von:
- **Audio-Länge:** Abgerechnet pro Minute
- **Modell-Preis:** `gpt-4o-transcribe-diarize` Preise siehe OpenAI-Preisliste
- **Segmentierung:** Mehrere Segmente = mehrere API-Calls

**Beispiel-Rechnung** (hypothetisch):
- 1-stündiges Meeting
- ~6 Segmente à 10 Minuten
- Preis: Check OpenAI Pricing für aktuelle Kosten

---

## 🎓 Erweiterte Nutzung

### Python API

```python
from audio_transcriber import AudioTranscriber
from pathlib import Path

transcriber = AudioTranscriber(api_key="sk-...")

result = transcriber.transcribe_file(
    file_path=Path("meeting.mp3"),
    output_dir=Path("./transcriptions"),
    enable_diarization=True,
    num_speakers=3,
    known_speaker_names=["Alice", "Bob", "Charlie"],
    known_speaker_references=[
        "alice.wav", 
        "bob.wav", 
        "charlie.wav"
    ]
)

print(f"Readable output: {result['readable_output']}")
```

### Batch-Processing

```bash
for file in ./audio_files/*.mp3; do
    audio-transcriber --input "$file" \
      --enable-diarization \
      --num-speakers 2 \
      --output-dir ./results
done
```

---

## 📝 FAQ

**Q: Kann ich Diarization mit anderen Models (z.B. whisper-1) verwenden?**  
A: Nein, Diarization erfordert das `gpt-4o-transcribe-diarize` Modell.

**Q: Funktioniert Diarization mit lokalen Modellen (Ollama)?**  
A: Derzeit nur mit OpenAI's API. Lokale Diarization ist ein zukünftiges Feature.

**Q: Wie viele Sprecher kann das System erkennen?**  
A: Theoretisch unbegrenzt, aber Genauigkeit sinkt bei >10 Sprechern.

**Q: Wird Diarization in SRT/VTT-Untertiteln unterstützt?**  
A: Aktuell nicht - das ist ein geplantes Feature.

**Q: Kann ich Sprecher nachträglich umbenennen?**  
A: Ja, bearbeiten Sie die JSON-Datei und verwenden Sie ein Script zur Konvertierung.

---

## 🚀 Nächste Schritte

- [ ] GUI-Integration (geplant)
- [ ] SRT/VTT mit Sprecher-Labels
- [ ] Automatisches Merging von Sprechern
- [ ] Sprecher-Statistiken (Redezeit, Wortanzahl)
- [ ] Export als strukturiertes Interview-Format

---

## 📞 Support & Feedback

Probleme oder Vorschläge? Bitte erstellen Sie ein Issue auf GitHub!

**Letzte Aktualisierung:** Januar 2026  
**Version:** 1.0
