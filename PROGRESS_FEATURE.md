# Fortschrittsanzeige & ETA Feature

## Übersicht

Das Progress/ETA Feature bietet Echtzeit-Fortschrittsverfolgung für Audio-Transkriptionen mit detaillierten Metriken:

- **ETA (Estimated Time to Arrival)**: Geschätzte verbleibende Zeit
- **Durchsatz**: Verarbeitungsgeschwindigkeit (Minuten Audio pro Stunde)
- **Kosten-Tracking**: Laufende und geschätzte Gesamtkosten
- **Prozentanzeige**: Fortschritt in Prozent für Dateien und Segmente

## CLI-Verwendung

### Automatische Fortschrittsanzeige

```bash
audio-transcriber --input podcast.mp3
```

**Ausgabe:**
```
Found 3 audio file(s)

📊 Analysiere Audio-Dateien...
📁 Gesamtdauer: 45m 32s
💰 Geschätzte Kosten: $0.2278

🎵 podcast_part1.mp3: 100%|████████████| 3/3 [00:15<00:00, ETA: 2m 15s | 180.5 min/h | Kosten: $0.0756]

======================================================================
FORTSCHRITT
======================================================================
Dateien:  2/3 (66.7%)
Segmente: 12/18 (66.7%)

Vergangen: 15m 23s
ETA:       7m 45s
Durchsatz: 176.3 min/h

Kosten:    $0.0756 / $0.2278
Verbleibend: $0.1522
======================================================================
```

### Detaillierte Metriken

Der ProgressTracker berechnet automatisch:
- Verstrichene Zeit seit Start
- Verbleibende Zeit basierend auf Verarbeitungsrate
- Audio-Durchsatz (Minuten pro Stunde Echtzeit)
- Aktuelle und geschätzte Gesamtkosten

## GUI-Verwendung

### Visuelle Fortschrittsanzeige

Die GUI zeigt in Echtzeit:

1. **Progress-Bar**: Visueller Fortschrittsbalken mit Prozentanzeige
2. **ETA-Label**: Verbleibende Zeit bis zum Abschluss
3. **Durchsatz-Label**: Verarbeitungsgeschwindigkeit
4. **Kosten-Label**: Aktuelle vs. geschätzte Gesamtkosten

```
[████████████████░░░░░░░░] 67.3%

ETA: 7m 45s    Durchsatz: 176.3 min/h    Kosten: $0.0756 / $0.2278
```

### Live-Updates

Die GUI aktualisiert automatisch nach jeder verarbeiteten Datei:
- Progress-Bar füllt sich
- ETA wird neu berechnet
- Durchsatz passt sich an
- Kosten werden aktualisiert

## Technische Details

### ProgressTracker-Klasse

```python
from audio_transcriber.progress import ProgressTracker

# Initialisierung
tracker = ProgressTracker(price_per_minute=0.0001)
tracker.start()
tracker.set_total_files(10)
tracker.set_total_duration(120.0)  # 120 Minuten Audio

# Während der Verarbeitung
tracker.update_file_completed(duration_minutes=12.5, num_segments=5)

# Metriken abrufen
summary = tracker.get_summary()
print(f"ETA: {summary['time']['eta_formatted']}")
print(f"Durchsatz: {summary['throughput']['formatted']}")
```

### Verfügbare Metriken

**get_summary()** liefert:

```python
{
    "files": {
        "total": 10,
        "completed": 7,
        "failed": 1,
        "skipped": 0,
        "progress_pct": 70.0
    },
    "segments": {
        "total": 50,
        "completed": 35,
        "failed": 2,
        "progress_pct": 70.0
    },
    "time": {
        "elapsed_seconds": 450.5,
        "elapsed_formatted": "7m 30s",
        "eta_seconds": 192.8,
        "eta_formatted": "3m 12s"
    },
    "throughput": {
        "value": 187.5,
        "formatted": "187.5 min/h"
    },
    "cost": {
        "current": 0.0875,
        "total_estimated": 0.1200,
        "remaining_estimated": 0.0325
    },
    "duration": {
        "processed_minutes": 87.5,
        "total_minutes": 120.0,
        "remaining_minutes": 32.5
    }
}
```

## ETA-Berechnung

Die ETA wird dynamisch basierend auf der tatsächlichen Verarbeitungsrate berechnet:

```python
processing_rate = elapsed_time / processed_duration
eta = remaining_duration * processing_rate
```

Diese Methode passt sich automatisch an:
- Netzwerkgeschwindigkeit
- API-Antwortzeiten
- Systemauslastung
- Dateikomplexität

## Durchsatz-Metriken

Der Durchsatz zeigt, wie viel Audio pro Stunde verarbeitet wird:

```python
# Minuten Audio verarbeitet pro Sekunde Echtzeit
rate_per_second = processed_minutes / elapsed_seconds

# Hochrechnung auf Stunden
throughput = rate_per_second * 3600  # min/h
```

**Beispiel-Interpretation:**
- `180 min/h`: 3 Stunden Audio werden in 1 Stunde verarbeitet
- `60 min/h`: Echtzeit-Verarbeitung
- `30 min/h`: 1 Stunde Audio benötigt 2 Stunden Verarbeitung

## Kosten-Tracking

Echtzeit-Kostenberechnung basierend auf OpenAI Whisper Preisen:

```python
# Standard: $0.0001 pro Minute Audio
cost_per_minute = 0.0001

# Aktuelle Kosten
current_cost = processed_minutes * cost_per_minute

# Geschätzte Gesamtkosten
total_cost = total_minutes * cost_per_minute

# Verbleibende Kosten
remaining_cost = total_cost - current_cost
```

## Integration in eigenen Code

### Minimales Beispiel

```python
from audio_transcriber import AudioTranscriber
from audio_transcriber.progress import ProgressTracker

# Setup
transcriber = AudioTranscriber(api_key="sk-...")
tracker = ProgressTracker()
tracker.start()

# Verarbeitung mit Progress-Tracking
for audio_file in audio_files:
    result = transcriber.transcribe_file(audio_file, ...)
    
    if result["status"] == "success":
        tracker.update_file_completed(
            duration_minutes=result["duration_seconds"] / 60,
            num_segments=result["segments"]
        )
    
    # Live-Metriken anzeigen
    summary = tracker.get_summary()
    print(f"ETA: {summary['time']['eta_formatted']}")
    print(f"Kosten: ${summary['cost']['current']:.4f}")

# Abschluss-Summary
tracker.print_summary()
```

### Erweitert mit tqdm

```python
from tqdm import tqdm

with tqdm(total=len(files), desc="Dateien") as pbar:
    for file in files:
        result = process(file)
        tracker.update_file_completed(...)
        
        # tqdm mit Live-Metriken aktualisieren
        summary = tracker.get_summary()
        pbar.set_postfix_str(
            f"ETA: {summary['time']['eta_formatted']} | "
            f"{summary['throughput']['formatted']}"
        )
        pbar.update(1)
```

## Genauigkeit der ETA

Die ETA-Genauigkeit verbessert sich im Laufe der Zeit:

- **Erste Datei**: Keine ETA verfügbar (keine Daten)
- **Nach 20% Fortschritt**: Grobe Schätzung (±50%)
- **Nach 50% Fortschritt**: Gute Schätzung (±20%)
- **Nach 80% Fortschritt**: Präzise Schätzung (±10%)

**Faktoren, die ETA beeinflussen:**
- Dateigrößen-Varianz (große vs. kleine Dateien)
- Audio-Qualität (Hintergrundgeräusche, Sprechgeschwindigkeit)
- Netzwerk-Schwankungen
- API-Auslastung

## Performance-Überlegungen

### CLI
- Minimal Overhead (~0.001s pro Update)
- Asynchrone Fortschrittsanzeige
- Keine Blockierung der Verarbeitung

### GUI
- Updates alle 1-2 Sekunden
- Thread-sicher (Background-Thread)
- Automatische UI-Aktualisierung

## Pausieren/Fortsetzen (Geplant)

Zukünftiges Feature für lange Transkriptions-Jobs:

```python
tracker.pause()   # Verarbeitung pausieren
tracker.resume()  # Verarbeitung fortsetzen
tracker.save_checkpoint("checkpoint.json")
tracker.load_checkpoint("checkpoint.json")
```

## Fehlerbehebung

### ETA zeigt "unbekannt"

**Ursache**: Noch keine Datei vollständig verarbeitet

**Lösung**: Warten bis erste Datei fertig ist

### Durchsatz schwankt stark

**Ursache**: Unterschiedliche Dateigrößen oder Netzwerk-Schwankungen

**Lösung**: Normal bei heterogenen Dateien; stabilisiert sich über Zeit

### Kosten stimmen nicht

**Ursache**: Falscher `price_per_minute` Parameter

**Lösung**: 
```python
# OpenAI Whisper: $0.006 / Minute
tracker = ProgressTracker(price_per_minute=0.006)

# Groq (kostenlos): $0 / Minute  
tracker = ProgressTracker(price_per_minute=0.0)
```

## Best Practices

1. **Total Duration setzen**: Für beste ETA-Genauigkeit
   ```python
   tracker.set_total_duration(calculate_total_duration(files))
   ```

2. **Regelmäßig updaten**: Nach jeder Datei, nicht nach jedem Segment
   ```python
   tracker.update_file_completed(...)  # ✅ Gut
   tracker.update_segment_completed()  # ❌ Zu häufig
   ```

3. **Summary am Ende**: Finale Statistiken ausgeben
   ```python
   tracker.print_summary()
   ```

4. **Fehler tracken**: Auch fehlgeschlagene Dateien melden
   ```python
   if failed:
       tracker.update_file_failed()
   ```

## Siehe auch

- [CLI Usage](QUICKSTART.md)
- [GUI Usage](GUI_GUIDE.md)
- [API Documentation](README.md)
