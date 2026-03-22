# GUI Benutzerhandbuch 🖥️

Vollständiger Leitfaden für die grafische Benutzeroberfläche des Audio Transcribers.

## Installation & Start

### Installation

```bash
# Falls noch nicht installiert
uv sync
```

### GUI Starten

```bash
# Direkt über den Befehl
uv run audio-transcriber-gui

# Oder über Python-Modul
uv run python -m audio_transcriber.gui
```

---

## Benutzeroberfläche Übersicht

Die GUI ist in **6 Tabs** organisiert:

### 📁 Tab 1: Haupteinstellungen

**Eingabe-Bereich:**
- **Audio-Datei oder Ordner**: Wähle eine einzelne Datei oder einen kompletten Ordner
  - Klicke "Datei wählen" für einzelne Audio-Dateien
  - Klicke "Ordner wählen" für Batch-Verarbeitung

**Ausgabe-Bereich:**
- **Transkriptions-Ordner**: Wo die finalen Transkriptionen gespeichert werden (Standard: `./transcriptions`)
- **Segment-Ordner**: Wo temporäre Audio-Segmente gespeichert werden (Standard: `./segments`)
- **Ausgabeformat**: Wähle zwischen:
  - `text` - Einfacher Text (Standard)
  - `json` - JSON mit Metadaten
  - `srt` - SubRip Untertitel
  - `vtt` - WebVTT Untertitel
  - `verbose_json` - Detailliertes JSON

**Verhalten:**
- ☑️ **Segmente behalten**: Temporäre Segment-Dateien nicht löschen
- ☑️ **Existierende Dateien überspringen**: Bereits verarbeitete Dateien überspringen
- ☑️ **Verbose Logging**: Detaillierte Log-Ausgabe

---

### 🔌 Tab 2: API Konfiguration

**API Einstellungen:**
- **API Key**: Dein API-Schlüssel (wird automatisch aus Umgebungsvariable `AUDIO_TRANSCRIBE_API_KEY` geladen)
  - Klicke "Anzeigen" um den Key ein-/auszublenden
- **Base URL**: API Endpunkt
- **Model**: Modellname für die Transkription

**Provider-Beispiele:**

#### OpenAI (Standard)
```
Base URL: https://api.openai.com/v1
Model: gpt-4o-mini-transcribe
API Key: sk-...
```

#### Groq (Schnell & Kostenlos)
```
Base URL: https://api.groq.com/openai/v1
Model: whisper-large-v3
API Key: gsk_...
```

#### Ollama (Lokal & Privat)
```
Base URL: http://localhost:11434/v1
API Key: ollama
Model: whisper
```

#### Together.ai
```
Base URL: https://api.together.xyz/v1
Model: whisper-large-v3
API Key: (your-key)
```

---

### ⚙️ Tab 3: Erweitert

**Segmentierungs-Parameter:**
- **Segment-Länge**: Wie lange jedes Audio-Segment sein soll (60-1800 Sekunden, Standard: 600)
  - Längere Segmente = weniger API-Aufrufe, aber größere Dateien
  - Kürzere Segmente = mehr API-Aufrufe, schnellere Verarbeitung
- **Überlappung**: Überlappung zwischen Segmenten (0-60 Sekunden, Standard: 10)
  - Hilft bei nahtloser Zusammenführung der Transkripte

**Performance:**
- **Parallele Transkriptionen**: Anzahl gleichzeitiger Transkriptionen (1-16, Standard: 4)
  - Höhere Werte = schneller, aber mehr API-Aufrufe
  - Beachte API Rate Limits!

---

### 📝 Tab 4: Transkription

**Sprach-Einstellungen:**
- **Sprache (ISO-639-1)**: Manuelle Sprachauswahl
  - Beispiele: `en` (Englisch), `de` (Deutsch), `es` (Spanisch), `fr` (Französisch)
  - Leer lassen für automatische Erkennung
- ☑️ **Sprache automatisch erkennen**: Aktiviert automatische Spracherkennung

**Model-Parameter:**
- **Temperature**: Zufälligkeit des Modells (0.0-1.0, Standard: 0.0)
  - 0.0 = Deterministisch, gleiche Eingabe → gleiche Ausgabe
  - Höhere Werte = Mehr Variation

**Kontext-Prompt:**
- Optionaler Text zur Verbesserung der Genauigkeit
- **Verwenden für:**
  - Namen von Personen
  - Fachbegriffe
  - Spezifische Terminologie
  
**Beispiele:**
```
"Podcast mit Dr. Sarah Johnson über KI und maschinelles Lernen. 
Begriffe: Transformer, GPT, Neural Networks, Training."
```

```
"Deutsche Podcastsendung über Technologie. 
Sprecher: Thomas Müller, Lisa Schmidt."
```

---

## Workflow: Schritt-für-Schritt

### 1. Vorbereitung

**API Key setzen:**
```bash
# Linux/macOS
export AUDIO_TRANSCRIBE_API_KEY="sk-..."

# Windows CMD
set AUDIO_TRANSCRIBE_API_KEY=sk-...

# Windows PowerShell
$env:AUDIO_TRANSCRIBE_API_KEY="sk-..."
```

Oder direkt in der GUI eintragen (Tab "API Konfiguration").

### 2. Audio-Datei(en) auswählen

1. Gehe zu Tab "📁 Haupteinstellungen"
2. Klicke "Datei wählen" für einzelne Datei ODER "Ordner wählen" für mehrere Dateien
3. Wähle deine Audio-Datei(en) aus

### 3. Ausgabe konfigurieren

1. Optional: Ändere **Transkriptions-Ordner** (Standard ist OK)
2. Optional: Ändere **Segment-Ordner** (Standard ist OK)
3. Wähle **Ausgabeformat**:
   - Text → Für einfache Texte
   - SRT/VTT → Für Untertitel
   - JSON → Für weitere Verarbeitung

### 4. API konfigurieren (falls nötig)

1. Gehe zu Tab "🔌 API Konfiguration"
2. Überprüfe/Ändere API-Einstellungen
3. Wähle Provider (OpenAI, Groq, Ollama, etc.)

### 5. Erweiterte Einstellungen (optional)

1. Gehe zu Tab "⚙️ Erweitert"
2. Passe Segment-Länge an (für lange Dateien)
3. Erhöhe Parallelität für schnellere Verarbeitung

### 6. Transkription starten

1. Klicke "▶ Transkription starten"
2. Beobachte den Fortschritt im Log-Fenster
3. Warte bis "ZUSAMMENFASSUNG" erscheint

### 7. Ergebnisse prüfen

- Finale Transkriptionen → `./transcriptions/` Ordner
- Segmente (falls behalten) → `./segments/` Ordner

---

## Tipps & Tricks

### Für beste Ergebnisse

1. **Gute Audio-Qualität verwenden**
   - Klare Aufnahme ohne viel Hintergrundgeräusch
   - Gute Mikrofonqualität

2. **Kontext-Prompt nutzen**
   - Namen von Sprechern angeben
   - Fachbegriffe auflisten
   - Thema beschreiben

3. **Richtige Sprache wählen**
   - Manuelle Auswahl für gemischte Sprachen
   - Automatisch für eindeutige Sprache

4. **Segment-Länge optimieren**
   - Längere Segmente (900s) für besseren Kontext
   - Kürzere Segmente (300s) für schnellere Verarbeitung

### Batch-Verarbeitung

1. Alle Audio-Dateien in einen Ordner legen
2. Ordner in GUI auswählen
3. "Existierende Dateien überspringen" aktivieren
4. Starten → Alle Dateien werden verarbeitet

### Kosten sparen

1. **Ollama lokal nutzen** (kostenlos):
   ```
   Base URL: http://localhost:11434/v1
   API Key: ollama
   Model: whisper
   ```

2. **Groq Free Tier nutzen**:
   - Höhere Limits als OpenAI Free Tier
   - Sehr schnell

3. **Segment-Länge erhöhen**:
   - Weniger API-Aufrufe = niedrigere Kosten

---

## Fehlerbehebung

### "Bitte geben Sie einen API Key ein"

**Lösung:**
1. Tab "🔌 API Konfiguration" öffnen
2. API Key eingeben
3. Oder Umgebungsvariable setzen

### "Pfad existiert nicht"

**Lösung:**
- Überprüfe, ob die Audio-Datei/der Ordner existiert
- Verwende "Datei wählen" / "Ordner wählen" Buttons

### GUI startet nicht

**Lösung:**
```bash
# PySide6 installieren/aktualisieren
uv pip install -U PySide6
```

### Langsame Verarbeitung

**Lösungen:**
1. Parallelität erhöhen (Tab "⚙️ Erweitert")
2. Groq API nutzen (schneller als OpenAI)
3. Ollama lokal nutzen
4. Segment-Länge erhöhen

### Segmente nicht gelöscht

**Lösung:**
- Standardmäßig werden Segmente automatisch gelöscht
- Falls "Segmente behalten" aktiviert ist, manuell löschen:
  ```bash
  rm -rf ./segments/*
  ```

---

## Tastenkombinationen

Keine speziellen Tastenkombinationen implementiert. Verwende die Buttons.

---

## Sicherheit

### API Key Schutz

- API Key wird mit `***` angezeigt
- Klicke "Anzeigen" um temporär anzuzeigen
- Wird nicht in Logs gespeichert

### Empfehlungen

1. **Umgebungsvariable verwenden:**
   ```bash
   export AUDIO_TRANSCRIBE_API_KEY="sk-..."
   ```

2. **Nicht in Screenshots teilen**

3. **Key regelmäßig rotieren**

---

## Screenshots

> **Hinweis:** Screenshots können mit den folgenden Schritten erstellt werden:

1. Öffne GUI: `audio-transcriber-gui`
2. Konfiguriere Beispieleinstellungen
3. Erstelle Screenshots für Dokumentation

**Vorgeschlagene Screenshots:**
- Hauptfenster mit allen Tabs
- Ausgefüllte Eingabefelder
- Laufende Transkription mit Log
- Fertige Transkription mit Zusammenfassung

---

## Vergleich: CLI vs GUI

| Feature | CLI | GUI |
|---------|-----|-----|
| **Einsteigerfreundlich** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Automatisierung** | ⭐⭐⭐⭐⭐ | ⭐ |
| **Batch-Verarbeitung** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Visualisierung** | ⭐ | ⭐⭐⭐⭐⭐ |
| **Scripting** | ⭐⭐⭐⭐⭐ | ❌ |
| **Progress Tracking** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Verwende CLI wenn:** Automatisierung, Scripting, Cron-Jobs  
**Verwende GUI wenn:** Einmalige Nutzung, Einfachheit, visuelles Feedback

---

## Weitere Ressourcen

- [README.md](README.md) - Hauptdokumentation
- [USAGE_EXAMPLES.md](docs/USAGE_EXAMPLES.md) - CLI Beispiele
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Problemlösung
- [PROJECT_GUIDELINES.md](PROJECT_GUIDELINES.md) - Entwickler-Richtlinien

---

## Support

Bei Problemen:
1. [GitHub Issues](https://github.com/lucmuss/audio-transcriber/issues)
2. [GitHub Discussions](https://github.com/lucmuss/audio-transcriber/discussions)
3. Log-Ausgabe in GUI prüfen (mit Verbose aktiviert)

**Viel Erfolg mit der Audio-Transkription! 🎙️→📝**
