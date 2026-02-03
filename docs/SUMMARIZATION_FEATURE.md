# Summarization Feature

## Übersicht

Das Summarization-Feature ermöglicht es, automatisch eine Zusammenfassung der Transkriptionen zu erstellen. Die Zusammenfassungen werden mit einem LLM (z.B. GPT-4o-mini) generiert und im Ordner `summaries` gespeichert.

## Verwendung über die Kommandozeile

### Basis-Verwendung

Um eine Zusammenfassung zusammen mit der Transkription zu erstellen:

```bash
audio-transcriber --input podcast.mp3 --summarize
```

### Erweiterte Optionen

#### Custom Summary-Modell

Sie können das Modell für die Zusammenfassung anpassen:

```bash
audio-transcriber --input podcast.mp3 --summarize --summary-model gpt-4o-mini
```

#### Custom Summary-Ordner

Standardmäßig werden Zusammenfassungen im Ordner `./summaries` gespeichert. Sie können einen anderen Ordner angeben:

```bash
audio-transcriber --input podcast.mp3 --summarize --summary-dir ./meine-summaries
```

#### Custom Summary-Prompt

Sie können den Prompt für die Zusammenfassung anpassen, um spezifische Anforderungen zu erfüllen:

```bash
audio-transcriber --input podcast.mp3 --summarize \
  --summary-prompt "Erstelle eine detaillierte Zusammenfassung mit den wichtigsten Erkenntnissen und Handlungsempfehlungen."
```

### Vollständiges Beispiel

```bash
audio-transcriber \
  --input podcast.mp3 \
  --output-dir ./transcriptions \
  --summarize \
  --summary-dir ./summaries \
  --summary-model gpt-4o-mini \
  --summary-prompt "Fasse die wichtigsten Punkte zusammen und liste die Hauptthemen auf."
```

## CLI-Parameter

| Parameter | Typ | Standard | Beschreibung |
|-----------|-----|----------|--------------|
| `--summarize` | Flag | False | Aktiviert die Zusammenfassungs-Funktion |
| `--summary-dir` | String | `./summaries` | Zielordner für Zusammenfassungen |
| `--summary-model` | String | `gpt-4o-mini` | Modell für die Zusammenfassung |
| `--summary-prompt` | String | (siehe unten) | Custom Prompt für die Zusammenfassung |

### Default Summary Prompt

```
Bitte erstelle eine prägnante Zusammenfassung des folgenden Transkripts. 
Fokussiere dich auf die wichtigsten Punkte, Themen und Erkenntnisse.
```

## Umgebungsvariablen

Sie können auch Umgebungsvariablen verwenden:

```bash
export AUDIO_TRANSCRIBE_SUMMARY_DIR="./summaries"
export AUDIO_TRANSCRIBE_SUMMARY_MODEL="gpt-4o-mini"
```

## Ausgabe-Dateistruktur

Bei der Transkription einer Datei `podcast.mp3` werden folgende Dateien erstellt:

```
transcriptions/
  └── podcast_mp3_full.text      # Vollständige Transkription

summaries/
  └── podcast_mp3_summary.txt    # Zusammenfassung
```

## Funktionsweise

1. **Transkription**: Zuerst wird die Audio-Datei transkribiert und im `transcriptions`-Ordner gespeichert
2. **Zusammenfassung**: Wenn `--summarize` aktiviert ist, wird die Transkription an das angegebene LLM-Modell gesendet
3. **Speicherung**: Die generierte Zusammenfassung wird im `summaries`-Ordner gespeichert

## Skip-Verhalten

- Wenn eine Zusammenfassung bereits existiert und `--skip-existing` aktiv ist (Standard), wird die Zusammenfassung übersprungen
- Mit `--no-skip-existing` werden vorhandene Zusammenfassungen neu generiert

## Fehlerbehandlung

- Wenn die Transkription fehlschlägt, wird keine Zusammenfassung erstellt
- Wenn die Transkription leer ist, wird die Zusammenfassung übersprungen
- API-Fehler bei der Zusammenfassung werden protokolliert, beeinträchtigen aber nicht die Transkription

## Kosten

Die Zusammenfassung verursacht zusätzliche API-Kosten basierend auf:
- Der Länge der Transkription (Input-Tokens)
- Der Länge der Zusammenfassung (Output-Tokens)
- Dem gewählten Modell (z.B. gpt-4o-mini ist kostengünstig)

Für eine typische 1-stündige Podcast-Transkription (~10.000 Wörter):
- Input: ~13.000 Tokens
- Output: ~300-500 Tokens
- Geschätzte Kosten mit gpt-4o-mini: ~$0.002-0.003
