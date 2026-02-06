# Project Guidelines & Best Practices

Umfassende Dokumentation der Projektstruktur, Workflows und Entwicklungspräferenzen für audio-transcriber. Dieses Dokument dient als Blueprint für die Wartung und ähnliche Projekte.

---

## 📋 Inhaltsverzeichnis

- [Projektphilosophie](#projektphilosophie)
- [Repository-Struktur](#repository-struktur)
- [Code-Organisation](#code-organisation)
- [Dokumentationsstandards](#dokumentationsstandards)
- [CI/CD Workflows](#cicd-workflows)
- [Testing-Strategie](#testing-strategie)
- [Release-Management](#release-management)
- [Paket-Distribution](#paket-distribution)
- [Entwicklungs-Workflow](#entwicklungs-workflow)
- [Code-Style & Qualität](#code-style--qualität)

---

## Projektphilosophie

### Kernprinzipien

1. **Production-Ready First** - Jedes Feature sollte vollständig getestet und dokumentiert sein vor dem Release
2. **Mehrere Installationsmethoden** - Support für PyPI, Docker und from-source Installationen
3. **Umfassende Dokumentation** - Separate Guides für verschiedene Use Cases und Zielgruppen
4. **Alles Automatisieren** - CI/CD für Testing, Building und Publishing
5. **Benutzerfreundlich** - CLI mit klaren Fehlermeldungen
6. **Cross-Platform** - Funktioniert auf macOS, Linux und Windows
7. **Professionelle Struktur** - Gut organisiert, skalierbar und wartbar

### Zielgruppen

- **End Users**: CLI-Anwendung für einfache Nutzung
- **Power Users**: CLI mit umfangreichen Optionen und Scripting-Support
- **Entwickler**: Klare API, umfangreiche Tests, klare Contribution Guidelines
- **DevOps**: Docker-Support für containerisierte Deployments

---

## Repository-Struktur

### Standard-Layout

```
audio-transcriber/
├── .github/                        # GitHub-spezifische Dateien
│   └── workflows/                  # GitHub Actions Workflows
│       ├── ci.yml                  # Continuous Integration
│       ├── build-binaries.yml      # Cross-platform Binary Builds
│       └── publish-to-pypi.yml     # PyPI Publication
│
├── src/                            # Source Code (importierbares Package)
│   └── audio_transcriber/
│       ├── __init__.py             # Package-Initialisierung & Version
│       ├── cli.py                  # Command-line Interface
│       ├── transcriber.py          # Transkriptions-Logik
│       ├── segmenter.py            # Audio-Segmentierung
│       ├── merger.py               # Transkript-Zusammenführung
│       ├── utils.py                # Utility-Funktionen
│       └── constants.py            # Konstanten
│
├── tests/                          # Test Suite
│   ├── __init__.py
│   ├── README.md                   # Test-Dokumentation
│   ├── test_*.py                   # Test-Dateien
│   └── fixtures/                   # Test-Daten
│
├── docs/                           # Erweiterte Dokumentation
│   ├── QUICKSTART.md               # Schnellstart
│   ├── TROUBLESHOOTING.md          # Häufige Probleme & Lösungen
│   └── ...                         # Weitere Guides
│
├── examples/                       # Nutzungsbeispiele
│   └── EXAMPLES.md
│
├── docker/                         # Docker Assets
│   ├── Dockerfile                  # Docker Image Definition
│   └── entrypoint.sh
│
├── build/                          # Build-Artefakte (gitignored)
├── dist/                           # Distribution-Dateien (gitignored)
│
├── .dockerignore                   # Docker Ignore-Patterns
├── .gitignore                      # Git Ignore-Patterns
├── docker-compose.yml              # Docker Compose Konfiguration
│
├── pyproject.toml                  # Modernes Python Packaging
├── uv.lock                         # uv Lockfile
├── requirements.txt                # Legacy/Docker Dependencies
│
├── mypy.ini                        # Type Checking Konfiguration
├── setup.cfg                       # Linting Konfiguration
├── build_binary.py                 # Binary Building Script
│
├── README.md                       # Haupt-Projektdokumentation
├── LICENSE                         # Lizenz (MIT)
└── Rules/                          # Projektregeln
```

### Wichtige Strukturentscheidungen

#### 1. Source in `src/` Verzeichnis

```
src/audio_transcriber/        # ✅ Bevorzugt
audio_transcriber/            # ❌ Vermeiden
```

**Warum?**
- Verhindert versehentliche Imports vom Projekt-Root
- Klare Trennung von Source Code und Projekt-Dateien
- Besser für Testing und Packaging

#### 2. Separates Test-Verzeichnis

```
tests/                        # ✅ Auf Projekt-Root-Ebene
src/audio_transcriber/tests/  # ❌ Vermeiden
```

**Warum?**
- Tests sind nicht Teil des distribuierten Packages
- Einfacher alle Tests zu starten
- Klare Grenze zwischen Code und Tests

#### 3. Dokumentationsstruktur

```
README.md                     # High-Level Übersicht, Quick Start
docs/                         # Detaillierte Guides
  ├── USAGE_EXAMPLES.md
  └── TROUBLESHOOTING.md
CONTRIBUTING.md               # Wie man beiträgt
DOCKER.md                     # Docker-spezifischer Guide
PYPI_PUBLISH.md               # Publishing Guide
```

**Warum?**
- README bleibt prägnant und zugänglich
- Spezialisierte Guides für verschiedene Bedürfnisse
- Einfach zu navigieren und zu warten

---

## Code-Organisation

### Modul-Verantwortlichkeiten

```python
# __init__.py - Package-Initialisierung
"""Audio transcriber package."""
__version__ = "1.0.0"
__author__ = "Audio Transcriber Contributors"
__license__ = "MIT"

from .cli import main

__all__ = ["main"]
```

```python
# cli.py - Command-line Interface nur
import argparse
from .transcriber import AudioTranscriber

def main():
    parser = argparse.ArgumentParser()
    # CLI-Logik nur
```

```python
# transcriber.py - Business Logic (kein UI)
class AudioTranscriber:
    """Kern-Funktionalität nutzbar von CLI oder als Library."""
    def transcribe(self, file_path):
        # Reine Logik, kein print() oder UI-Code
```

### Separation of Concerns

```python
# ✅ Gut: Getrennte Verantwortlichkeiten
class AudioSegmenter:
    """Segmentiert Audio-Dateien."""
    def segment(self, audio_path, segment_length):
        return segments

class TranscriptMerger:
    """Führt Transkripte zusammen."""
    def merge(self, transcripts, overlap):
        return merged_text

# ❌ Schlecht: Vermischte Verantwortlichkeiten
class AudioProcessor:
    def process_and_merge(self, file_path):
        # Segmentierung + Transkription + Merging gemischt
```

---

## Dokumentationsstandards

### README.md Struktur

```markdown
# Projektname 🎵

[Badges: CI, Python version, License, Code style]

Kurzbeschreibung (1-2 Sätze)

## ✨ Features
## 📋 Inhaltsverzeichnis
## 🚀 Installation
## ⚡ Quick Start
## 📚 Nutzungsbeispiele
## ⚙️ Konfiguration
## 🧪 Testing
## 🤝 Contributing
## 📝 License
```

### Separate Dokumentationsdateien

1. **USAGE_EXAMPLES.md**
   - 20+ detaillierte Beispiele
   - Nach Komplexität organisiert
   - Real-World-Szenarien
   - Code-Snippets mit Outputs

2. **TROUBLESHOOTING.md**
   - Häufige Fehler mit Lösungen
   - Plattform-spezifische Probleme
   - Performance-Tipps
   - Debug-Anweisungen

3. **DOCKER.md**
   - Vollständiger Docker-Guide
   - docker-compose Beispiele
   - Volume-Mounting-Patterns
   - Plattform-spezifische Befehle

4. **PYPI_PUBLISH.md**
   - Schritt-für-Schritt Publishing Guide
   - Manuelle und automatisierte Methoden
   - Version-Management
   - Troubleshooting

5. **HOMEBREW.md**
   - Tap-Creation Guide
   - Formula-Template
   - Testing-Anweisungen
   - Update-Prozeduren

### Code-Kommentare

```python
# ✅ Gut: WARUM erklären, nicht WAS
def parse_filename(filename):
    """
    Parse filename to extract info.
    
    Handles "Artist - Title" format commonly used when
    metadata tags are missing or incomplete.
    """
    # Split nur am ersten Bindestrich für Titel mit Bindestrichen
    parts = filename.rsplit(" - ", 1)
    return parts

# ❌ Schlecht: Offensichtliche Kommentare
def parse_filename(filename):
    # Split den Dateinamen  (offensichtlich)
    parts = filename.split(" - ")
    # Return die Teile  (offensichtlich)
    return parts
```

---

## CI/CD Workflows

### GitHub Actions Struktur

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
    
    runs-on: ${{ matrix.os }}
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
      - name: Install dependencies
      - name: Run tests
      - name: Upload coverage
```

### Mehrere Workflow-Dateien

```
.github/workflows/
├── ci.yml                    # Allgemeines CI Testing
├── build-binaries.yml        # Executable bauen
└── publish-to-pypi.yml       # Publish zu PyPI
```

**Warum separate Workflows?**
- Verschiedene Trigger (push vs tag)
- Verschiedene Zwecke
- Einfacher zu warten
- Unabhängige Ausführung

### Workflow Best Practices

```yaml
# ✅ Spezifische Versionen verwenden
- uses: actions/checkout@v4          # Version spezifiziert
- uses: actions/upload-artifact@v4   # Aktualisiert zu v4

# ✅ Matrix Builds für Cross-Platform
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ['3.8', '3.11', '3.12']

# ✅ Bedingte Steps
- name: Windows-spezifisch
  if: runner.os == 'Windows'
  run: choco install ffmpeg

# ✅ Richtige Permissions
permissions:
  contents: write              # Für Releases erstellen
```

---

## Testing-Strategie

### Test-Organisation

```
tests/
├── test_cli.py               # CLI Interface Tests
├── test_transcriber.py       # Transcription Tests
├── test_segmenter.py         # Segmentation Tests
├── test_merger.py            # Merge Logic Tests
├── test_utils.py             # Utility Tests
└── fixtures/                 # Test-Daten
```

### Test-Patterns

```python
# test_transcriber.py
import pytest
from pathlib import Path

class TestAudioTranscriber:
    """Test Audio-Transkription."""
    
    @pytest.fixture
    def transcriber(self):
        """Provide transcriber instance."""
        return AudioTranscriber()
    
    @pytest.fixture
    def test_file(self, tmp_path):
        """Create temporary test file."""
        file_path = tmp_path / "test.mp3"
        file_path.write_bytes(b"test data")
        return file_path
    
    def test_transcribe(self, transcriber, test_file):
        """Test transcription."""
        # Arrange
        expected_text = "Test"
        
        # Act
        result = transcriber.transcribe(test_file)
        
        # Assert
        assert result == expected_text
    
    def test_invalid_file(self, transcriber):
        """Test handling of invalid files."""
        with pytest.raises(FileNotFoundError):
            transcriber.transcribe("nonexistent.mp3")
```

### Test Coverage Ziele

- **Core Logic**: 95%+ Coverage
- **CLI**: 80%+ Coverage
- **Integration**: Vollständige User Workflows
- **Edge Cases**: Leere Inputs, Sonderzeichen, große Dateien

### Tests Ausführen

```bash
# Alle Tests
pytest

# Mit Coverage
pytest --cov=audio_transcriber --cov-report=html

# Spezifischer Test
pytest tests/test_merger.py::TestClass::test_method

# Verbose
pytest -v

# Stop bei erstem Fehler
pytest -x
```

---

## Release-Management

### Versionsnummerierung (SemVer)

```
MAJOR.MINOR.PATCH
  1  .  0  .  0

MAJOR: Breaking Changes (2.0.0)
MINOR: Neue Features, backward-compatible (1.1.0)
PATCH: Bug Fixes (1.0.1)
```

### Version Update Checklist

```markdown
- [ ] Update Version in src/audio_transcriber/__init__.py
- [ ] Update Version in pyproject.toml
- [ ] Update CHANGELOG.md (falls vorhanden)
- [ ] Alle Tests ausführen
- [ ] Lokal bauen und testen
- [ ] Git Tag erstellen
- [ ] Tag pushen um Workflows zu triggern
```

### Version Update Locations

```python
# src/audio_transcriber/__init__.py
__version__ = "1.0.1"  # ← Hier updaten

# pyproject.toml
[project]
version = "1.0.1"  # ← Hier updaten
```

### Git Tagging

```bash
# Annotated Tag erstellen
git tag -a v1.0.1 -m "Release version 1.0.1"

# Tag pushen (triggert Workflows)
git push origin v1.0.1

# Tags auflisten
git tag -l

# Tag löschen (bei Fehler)
git tag -d v1.0.1
git push origin :refs/tags/v1.0.1
```

---

## Paket-Distribution

### Mehrere Distributionsmethoden

1. **PyPI** (Python Package Index)
   - Primäre Methode für Python Packages
   - `uv tool install audio-transcriber`
   - Automatisiert via GitHub Actions

2. **Docker** (Containerisiert)
   - Cross-Platform Konsistenz
   - Keine Installation erforderlich
   - Ideal für Server

3. **Binary Executables**
   - PyInstaller-basiert
   - Kein Python erforderlich
   - Pro-Platform Builds

4. **Homebrew** (macOS/Linux) - Optional
   - Native Package Manager Integration
   - `brew install audio-transcriber`
   - Erfordert separates Tap-Repository

---

## Entwicklungs-Workflow

### Branch-Strategie

```
main                    # Production-ready Code
├── develop             # Development Branch
├── feature/xxx         # Neue Features
├── bugfix/xxx          # Bug Fixes
└── docs/xxx            # Dokumentations-Updates
```

### Commit Message Format

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat:` Neues Feature
- `fix:` Bug Fix
- `docs:` Dokumentation
- `test:` Tests
- `refactor:` Code Refactoring
- `style:` Code Style (Formatierung)
- `chore:` Wartung

**Beispiele:**
```
feat: add support for multiple API providers

fix: handle unicode characters in filenames on Windows

docs: add comprehensive troubleshooting guide

test: add integration tests for segment merging

chore: update GitHub Actions to v4
```

---

## Code-Style & Qualität

### Python Style Guide

- **Line length**: 100 Zeichen
- **Quotes**: Double Quotes für Strings
- **Imports**: Gruppiert und sortiert (isort)
- **Formatting**: Black Formatter
- **Type Hints**: Empfohlen aber nicht erforderlich

### Konfigurationsdateien

```ini
# mypy.ini
[mypy]
python_version = 3.8
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true
```

```ini
# .flake8
[flake8]
max-line-length = 100
extend-ignore = E203, W503
exclude = .git, __pycache__, build, dist
```

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311', 'py312']

[tool.isort]
profile = "black"
line_length = 100
```

### Quality Checks

```bash
# Code formatieren
black src tests

# Imports sortieren
isort src tests

# Linting
flake8 src tests --max-line-length=100

# Type Checking
mypy src

# Alle Checks
black . && isort . && flake8 . && mypy src && pytest
```

---

## Umgebungs-spezifische Guidelines

### Docker Best Practices

```dockerfile
# Multi-stage Build für kleinere Images
FROM python:3.11-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
COPY pyproject.toml uv.lock .
RUN uv venv && uv sync --frozen

FROM python:3.11-slim
COPY --from=builder /app/.venv /app/.venv
COPY . /app
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT ["audio-transcriber"]
```

### Windows-Kompatibilität

```python
# ✅ pathlib für Cross-Platform Pfade verwenden
from pathlib import Path
file_path = Path("folder") / "file.txt"

# ❌ String-Konkatenation vermeiden
file_path = "folder\\file.txt"  # Nur Windows

# ✅ Line Endings behandeln
with open(file, "w", newline="") as f:  # Konsistente Line Endings
    writer = csv.writer(f)
```

### Unicode-Handling

```python
# ✅ Explizites Encoding
with open(file, "r", encoding="utf-8") as f:
    content = f.read()

# ✅ Binary I/O wenn nötig
with open(file, "rb") as f:
    data = f.read()
```

---

## Zusammenfassung: Wichtigste Erkenntnisse

### Struktur
- `src/` für Source Code
- Separates `tests/` Verzeichnis
- Mehrere spezialisierte Dokumentationsdateien
- Klare Trennung der Verantwortlichkeiten

### Workflows
- Multi-Platform CI/CD
- Automatisiertes Testing und Building
- Tag-basierte Releases
- Mehrere Distributions-Kanäle

### Qualität
- 90%+ Test Coverage Ziel
- Automatisierte Code-Formatierung
- Type Hints wo sinnvoll
- Umfassende Dokumentation

### Distribution
- PyPI als primär
- Docker für Containerisierung
- Binaries für nicht-technische User
- Homebrew optional

### Entwicklung
- SemVer Versionierung
- Conventional Commits
- Feature Branches
- Detaillierte PR-Templates

---

Diese Struktur gewährleistet:
✅ Professionelles Erscheinungsbild
✅ Einfache Wartung
✅ Cross-Platform Kompatibilität  
✅ Mehrere Benutzertypen unterstützt
✅ Automatisierte Qualitätssicherung
✅ Klarer Contribution-Pfad
✅ Skalierbare Architektur

**Verwende dies als Blueprint für jedes neue Python-Projekt!**
