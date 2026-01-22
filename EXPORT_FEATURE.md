# Export-Features für Audio Transcriber

## Übersicht

Das Export-Feature ermöglicht den Export von Transkriptionen in verschiedene beliebte Dokumentformate:

- **DOCX**: Microsoft Word-Dokumente (.docx)
- **Markdown**: Markdown-Dateien (.md)
- **LaTeX**: LaTeX-Dokumente (.tex)

Alle Exporte unterstützen Metadaten wie Titel, Autor, Datum, Dauer und Sprache.

## Installation

### Basis-Installation

```bash
pip install python-docx  # Nur für DOCX-Export erforderlich
```

### LaTeX zu PDF (Optional)

Für die Konvertierung von LaTeX zu PDF:

**Ubuntu/Debian:**
```bash
sudo apt-get install texlive-latex-base
```

**macOS:**
```bash
brew install mactex
```

**Windows:**
- Installiere [MiKTeX](https://miktex.org/) oder [TeX Live](https://www.tug.org/texlive/)

## CLI-Verwendung

### Einzelnes Format exportieren

```bash
# Nach DOCX exportieren
audio-transcriber --input podcast.mp3 --export docx

# Nach Markdown exportieren
audio-transcriber --input lecture.wav --export md

# Nach LaTeX exportieren
audio-transcriber --input interview.mp3 --export latex
```

### Mehrere Formate gleichzeitig

```bash
# Alle drei Formate exportieren
audio-transcriber --input podcast.mp3 --export docx md latex

# DOCX und Markdown
audio-transcriber --input lecture.wav --export docx md
```

### Mit Metadaten

```bash
audio-transcriber --input podcast.mp3 \
  --export docx latex \
  --export-title "KI und die Zukunft" \
  --export-author "Dr. Max Mustermann"
```

### Export-Verzeichnis anpassen

```bash
audio-transcriber --input podcast.mp3 \
  --export docx \
  --export-dir ./meine-exports
```

## Ausgabebeispiele

### CLI-Ausgabe

```
Found 1 audio file(s)

📊 Analysiere Audio-Dateien...
📁 Gesamtdauer: 15m 23s
💰 Geschätzte Kosten: $0.0923

🎵 podcast.mp3: 100%|███████████| 1/1 [00:45<00:00, ETA: 0s | 20.5 min/h | Kosten: $0.0923]

  📄 Exportiert: podcast.docx
  📄 Exportiert: podcast.md
  📄 Exportiert: podcast.tex

======================================================================
FORTSCHRITT
======================================================================
Dateien:  1/1 (100.0%)
Vergangen: 45s
Durchsatz: 20.5 min/h
Kosten:    $0.0923 / $0.0923
======================================================================
```

## Programmatische Verwendung

### Basis-Beispiel

```python
from pathlib import Path
from audio_transcriber.exporter import TranscriptionExporter

# Initialisiere Exporter
exporter = TranscriptionExporter()

# Exportiere zu DOCX
result = exporter.export(
    transcription_file=Path("transcription.txt"),
    output_file=Path("output.docx"),
    export_format="docx"
)

print(result)
# {'status': 'success', 'output_file': 'output.docx', 'format': 'docx', 'size_bytes': 12345}
```

### Mit Metadaten

```python
from pathlib import Path
from audio_transcriber.exporter import TranscriptionExporter

exporter = TranscriptionExporter()

# Metadaten definieren
metadata = {
    "title": "Meeting Protokoll",
    "author": "Team-Manager",
    "date": "2026-01-21",
    "duration": "45m 30s",
    "language": "de",
    "model": "whisper-1"
}

# Export zu allen Formaten
for fmt in ["docx", "md", "latex"]:
    result = exporter.export(
        transcription_file=Path("meeting.txt"),
        output_file=Path(f"meeting.{fmt}"),
        export_format=fmt,
        metadata=metadata
    )
    
    if result["status"] == "success":
        print(f"✅ Erfolgreich exportiert: {result['output_file']}")
    else:
        print(f"❌ Fehler: {result['error']}")
```

## Format-Spezifikationen

### DOCX (Microsoft Word)

**Features:**
- Professionelles Layout mit Überschriften
- Metadata-Sektion mit fetter Beschriftung
- Calibri Schriftart, 11pt
- Automatische Absatzformatierung
- Unterstützt JSON- und Textformat

**Struktur:**
```
Titel (zentriert, groß)
---
Author: Max Mustermann
Date: 2026-01-21
Duration: 15m 23s
Language: de
---

Transcription
[Transkriptionstext in Absätzen]
```

**Vorteile:**
- Einfach zu bearbeiten
- Kompatibel mit MS Word, LibreOffice, Google Docs
- Unterstützt Formatierung und Kommentare

### Markdown

**Features:**
- Clean, lesbare Formatierung
- Metadata als Liste
- Überschriften-Hierarchie
- Kompatibel mit GitHub, GitLab, Notion, etc.

**Struktur:**
```markdown
# Meeting Protokoll

## Metadata

- **Author:** Max Mustermann
- **Date:** 2026-01-21
- **Duration:** 15m 23s
- **Language:** de

---

## Transcription

[Transkriptionstext]
```

**Vorteile:**
- Versionskontrolle-freundlich (Git)
- Einfach zu konvertieren (Pandoc)
- Plattform-unabhängig
- Sehr klein (Textformat)

**Konvertierung zu anderen Formaten:**
```bash
# Markdown zu PDF (mit Pandoc)
pandoc meeting.md -o meeting.pdf

# Markdown zu HTML
pandoc meeting.md -o meeting.html

# Markdown zu DOCX
pandoc meeting.md -o meeting.docx
```

### LaTeX

**Features:**
- Professionelles wissenschaftliches Layout
- Typografisch perfekt
- UTF-8 Encoding
- Moderne Fonts (lmodern)
- Optimiert für A4 Paper

**Struktur:**
```latex
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[margin=2.5cm]{geometry}

\title{Meeting Protokoll}
\author{Max Mustermann}
\date{2026-01-21}

\begin{document}
\maketitle

\section*{Metadata}
\begin{itemize}
  \item \textbf{Duration:} 15m 23s
  \item \textbf{Language:} de
\end{itemize}

\section*{Transcription}
[Transkriptionstext]

\end{document}
```

**Kompilierung zu PDF:**
```bash
pdflatex meeting.tex
```

**Vorteile:**
- Höchste typografische Qualität
- Ideal für wissenschaftliche Arbeiten
- Referenzen und Zitate möglich
- Versionskontrolle-freundlich

## Metadaten-Felder

Alle verfügbaren Metadaten-Felder:

| Feld       | Beschreibung                      | Beispiel              |
|------------|-----------------------------------|-----------------------|
| `title`    | Dokumenttitel                     | "Podcast Episode #42" |
| `author`   | Autor/Ersteller                   | "Dr. Jane Smith"      |
| `date`     | Datum                             | "2026-01-21"          |
| `duration` | Audio-Dauer                       | "1h 23m 45s"          |
| `language` | Sprache (ISO 639-1)               | "de", "en", "fr"      |
| `model`    | Verwendetes Transkriptions-Modell | "whisper-1"           |

## Content-Parsing

Der Exporter kann verschiedene Transkriptionsformate verarbeiten:

### Textformat

```
Dies ist ein einfacher Text.
Mit mehreren Absätzen.
```

### JSON-Format (verbose_json)

```json
{
  "text": "Dies ist der transkribierte Text.",
  "language": "de",
  "duration": 123.45
}
```

### Segmente-Format

```json
{
  "segments": [
    {"text": "Erster Satz."},
    {"text": "Zweiter Satz."}
  ]
}
```

## Fehlerbehebung

### Python-docx nicht installiert

**Fehler:**
```
python-docx package not installed
```

**Lösung:**
```bash
pip install python-docx
```

### LaTeX Sonderzeichen-Probleme

**Problem:** LaTeX-Kompilierung schlägt fehl bei Sonderzeichen

**Lösung:** Der Exporter escaped automatisch alle LaTeX-Sonderzeichen:
- `&`, `%`, `$`, `#`, `_`, `{`, `}`, `~`, `^`, `\`

### DOCX-Datei zu groß

**Problem:** Große Transkriptionen erzeugen große DOCX-Dateien

**Lösung:** 
```bash
# Verwende Markdown stattdessen (viel kleiner)
audio-transcriber --input file.mp3 --export md

# Oder komprimiere die DOCX-Datei
zip meeting.docx.zip meeting.docx
```

### LaTeX-Kompilierung fehlschlägt

**Problem:** `pdflatex` nicht gefunden oder Fehler bei Kompilierung

**Checkliste:**
1. LaTeX-Distribution installiert? (`pdflatex --version`)
2. UTF-8 encoding korrekt?
3. Alle Packages installiert? (`lmodern`, `geometry`, `hyperref`)

**Lösung:**
```bash
# Mehrfach kompilieren für Referenzen
pdflatex meeting.tex
pdflatex meeting.tex

# Oder mit latexmk (automatisch)
latexmk -pdf meeting.tex
```

## Best Practices

### 1. Format-Auswahl

**DOCX wählen für:**
- Geschäftsdokumente
- Einfache Bearbeitung erforderlich
- Zusammenarbeit mit MS Office-Nutzern

**Markdown wählen für:**
- Versionskontrolle (Git)
- Websites/Blogs
- Flexible Weiterverarbeitung
- Minimale Dateigröße

**LaTeX wählen für:**
- Wissenschaftliche Arbeiten
- Publikationen
- Höchste typografische Qualität
- Langfristige Archivierung

### 2. Metadaten immer angeben

```bash
# Gut: Mit Metadaten
audio-transcriber --input file.mp3 \
  --export docx \
  --export-title "Wichtiges Meeting" \
  --export-author "Team Alpha"

# Nicht ideal: Ohne Metadaten (verwendet Dateinamen)
audio-transcriber --input file.mp3 --export docx
```

### 3. Batch-Export

```bash
# Alle Dateien in Verzeichnis exportieren
audio-transcriber --input ./audio_files \
  --export docx md \
  --export-dir ./exports \
  --export-author "Ihr Name"
```

### 4. Kombiniere mit anderen Features

```bash
# Transkription + Summary + Export
audio-transcriber --input podcast.mp3 \
  --summarize \
  --export docx md latex \
  --export-title "Podcast #42" \
  --export-author "Podcast Host"
```

## Kosten

Export-Features verursachen **keine zusätzlichen API-Kosten**. Sie arbeiten nur mit bereits transkribierten Texten.

## Performance

**Export-Geschwindigkeit (circa):**
- Markdown: < 0.1s pro Datei
- DOCX: ~0.2-0.5s pro Datei
- LaTeX: < 0.1s pro Datei

**Kompilierung (LaTeX → PDF):**
- ~2-5s pro Datei (abhängig von Länge)

## Siehe auch

- [CLI Usage](QUICKSTART.md)
- [Summarization Feature](SUMMARIZATION_FEATURE.md)
- [Diarization Feature](DIARIZATION_FEATURE.md)
- [Progress/ETA Feature](PROGRESS_FEATURE.md)
