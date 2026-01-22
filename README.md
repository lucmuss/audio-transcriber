# Audio Transcriber 🎙️

[![CI](https://github.com/lucmuss/audio-transcriber/workflows/CI/badge.svg)](https://github.com/lucmuss/audio-transcriber/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Professional audio transcription tool using OpenAI-compatible Speech-to-Text APIs with intelligent segmentation and merging.

## ✨ Features

- **🖥️ GUI & CLI Interfaces** - User-friendly graphical interface + powerful command-line tool
- **🔄 Intelligent Segmentation** - Automatically splits large audio files into processable chunks
- **⚡ Parallel Processing** - Concurrent transcription of multiple segments for faster results
- **🎙️ Speaker Diarization** - Identify and label different speakers in conversations
- **📝 AI Summarization** - Generate concise summaries of transcriptions
- **📄 Multi-Format Export** - Export to DOCX, Markdown, and LaTeX with metadata
- **🎯 Smart Merging** - Overlap detection and removal for seamless final transcripts
- **🌍 Multi-Format Support** - MP3, WAV, FLAC, M4A, OGG, AAC, WMA, MP4
- **📋 Multiple Output Formats** - Text, JSON, SRT, VTT subtitles, Verbose JSON, Diarized JSON
- **🔌 OpenAI-Compatible** - Works with OpenAI, Ollama, Groq, LocalAI, Azure, Together.ai
- **🔁 Resume Capability** - Automatically skips already processed files
- **📊 Live Progress Tracking** - Real-time ETA, throughput, and cost tracking
- **🌐 Language Detection** - Automatic language detection from audio
- **💰 Cost Estimation** - Live cost calculation during processing
- **📁 Organized Output** - Separate folders for transcriptions, segments, summaries, and exports

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Output Formats](#output-formats)
- [Advanced Features](#advanced-features)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (required for audio processing)

### Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update && sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
```bash
choco install ffmpeg
# Or download from https://ffmpeg.org
```

### Install Audio Transcriber

```bash
# Clone the repository
git clone https://github.com/lucmuss/audio-transcriber.git
cd audio-transcriber

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## ⚡ Quick Start

### CLI (Command Line)

```bash
# Set your API key
export AUDIO_TRANSCRIBE_API_KEY="sk-..."

# Transcribe a single file
audio-transcriber --input podcast.mp3

# Transcribe all files in a directory
audio-transcriber --input ./audio_files
```

Output will be saved to `./transcriptions/` by default.

### GUI (Graphical Interface)

```bash
# Start the GUI
audio-transcriber-gui
```

Die GUI bietet:
- 📁 **Einfache Dateiauswahl** - Browse-Buttons for Dateien und Ordner
- 🔌 **API-Konfiguration** - Visuelle Eingabe für alle API-Einstellungen
- ⚙️ **Alle Optionen** - Segment-Länge, Parallelität, Sprache, etc.
- 📊 **Live-Fortschritt** - Echtzeit-Log-Ausgabe während der Verarbeitung
- 🎯 **Tooltips & Hilfe** - Provider-Beispiele und Tipps direkt in der GUI

Siehe [GUI_GUIDE.md](GUI_GUIDE.md) für detaillierte Anleitungen.

## 📚 Usage Examples

###  Basic Transcription

```bash
# Single file with OpenAI
audio-transcriber --input lecture.mp3
```

### 🌐 Use with Local Ollama (Free & Private)

```bash
# Start Ollama first
ollama serve

# Transcribe using local model
audio-transcriber \
  --input podcast.mp3 \
  --base-url http://localhost:11434/v1 \
  --api-key ollama \
  --model whisper
```

### 📝 Generate Subtitles

```bash
# SRT format
audio-transcriber --input video.mp4 --response-format srt

# VTT format for web
audio-transcriber --input video.mp4 --response-format vtt
```

### 🎯 Custom Segmentation

```bash
# Longer segments for better context
audio-transcriber \
  --input long_podcast.mp3 \
  --segment-length 900 \
  --overlap 15 \
  --concurrency 6
```

### 🌍 Language-Specific Transcription

```bash
# German language
audio-transcriber --input german_audio.mp3 --language de

# Auto-detect language
audio-transcriber --input mixed_audio.mp3 --detect-language
```

### 🎨 With Context Prompt

```bash
# Improve accuracy with context
audio-transcriber \
  --input tech_talk.mp3 \
  --prompt "This is a technical discussion about Kubernetes, Docker, and microservices. Speaker: John Smith"
```

## ⚙️ Configuration

### Command-Line Options

#### Required Arguments
| Option | Description | Default |
|--------|-------------|---------|
| `-i, --input` | Path to audio file or directory | **Required** |

#### API Configuration
| Option | Description | Default |
|--------|-------------|---------|
| `--api-key` | API key | From `AUDIO_TRANSCRIBE_API_KEY` |
| `--base-url` | API base URL | `https://api.openai.com/v1` |
| `--model` | Model name | `gpt-4o-mini-transcribe` |

#### Output Configuration
| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output-dir` | Output directory for transcriptions | `./transcriptions` |
| `--segments-dir` | Directory for temporary segments | `./segments` |
| `-f, --response-format` | Output format (text/json/srt/vtt/verbose_json) | `text` |

#### Segmentation Parameters
| Option | Description | Default |
|--------|-------------|---------|
| `--segment-length` | Segment length in seconds | `300` (5 min) |
| `--overlap` | Overlap between segments in seconds | `3` |

#### Transcription Parameters
| Option | Description | Default |
|--------|-------------|---------|
| `--language` | ISO-639-1 language code (e.g., 'en', 'de') | Auto-detect |
| `--detect-language` | Auto-detect language from first segment | `true` |
| `--no-detect-language` | Disable language auto-detection | - |
| `--temperature` | Model temperature (0.0-1.0) | `0.0` |
| `--prompt` | Context prompt for better accuracy | None |

#### Performance Parameters
| Option | Description | Default |
|--------|-------------|---------|
| `-c, --concurrency` | Number of parallel transcriptions | `8` |

#### Diarization Parameters (Speaker Recognition)
| Option | Description | Default |
|--------|-------------|---------|
| `--enable-diarization` | Enable speaker diarization | `false` |
| `--num-speakers` | Expected number of speakers | Auto-detect |
| `--known-speaker-names` | List of known speaker names | None |
| `--known-speaker-references` | Paths to reference audio files | None |

#### Summarization Parameters
| Option | Description | Default |
|--------|-------------|---------|
| `--summarize` | Generate a summary of transcription | `false` |
| `--summary-dir` | Output directory for summaries | `./summaries` |
| `--summary-model` | Model for summarization | `gpt-4.1-mini` |
| `--summary-prompt` | Custom prompt for summary generation | See code |

#### Export Parameters
| Option | Description | Default |
|--------|-------------|---------|
| `--export` | Export to formats (docx, md, latex) | None |
| `--export-dir` | Output directory for exports | `./exports` |
| `--export-title` | Title for exported documents | Filename |
| `--export-author` | Author name for exported documents | None |

#### Behavior Options
| Option | Description | Default |
|--------|-------------|---------|
| `--no-keep-segments` | Delete temporary segment files after processing | - |
| `--skip-existing` | Skip files if output already exists | `false` |
| `--analyze-duration` | Analyze audio duration before processing (slower, better ETA) | `false` |
| `--dry-run` | Simulate processing without API calls | `false` |
| `-v, --verbose` | Enable verbose logging | `false` |

**Note:** By default, segments are kept and files are re-processed even if outputs exist.

### Environment Variables

```bash
export AUDIO_TRANSCRIBE_API_KEY="sk-..."
export AUDIO_TRANSCRIBE_BASE_URL="https://api.openai.com/v1"
export AUDIO_TRANSCRIBE_MODEL="gpt-4o-mini-transcribe"
export AUDIO_TRANSCRIBE_OUTPUT_DIR="./transcriptions"
export AUDIO_TRANSCRIBE_SEGMENT_LENGTH="300"
export AUDIO_TRANSCRIBE_OVERLAP="3"
export AUDIO_TRANSCRIBE_CONCURRENCY="8"
```

## 📄 Output Formats

### Text (Default)
```
This is the transcribed audio content. It's clean and readable.
```

### JSON
```json
{
  "text": "Full transcription text",
  "segments": [...],
  "language": "en"
}
```

### SRT Subtitles
```
1
00:00:00,000 --> 00:00:05,200
First subtitle line

2
00:00:05,200 --> 00:00:10,500
Second subtitle line
```

### VTT Subtitles
```
WEBVTT

00:00:00.000 --> 00:00:05.200
First subtitle line

00:00:05.200 --> 00:00:10.500
Second subtitle line
```

## 🔧 Advanced Features

### Batch Processing

```bash
# Process entire directories
audio-transcriber --input ./100_podcasts --concurrency 8
```

### Resume Failed Jobs

```bash
# Automatically skips already processed files
audio-transcriber --input ./audio_files
# Interrupt with Ctrl+C
audio-transcriber --input ./audio_files  # Resumes from where it left off
```

### Dry Run Mode

```bash
# Test configuration without API calls
audio-transcriber --input large_file.mp3 --dry-run
```

### Speaker Diarization (Who Said What)

```bash
# Enable speaker diarization
audio-transcriber \
  --input meeting.mp3 \
  --enable-diarization

# With expected number of speakers
audio-transcriber \
  --input podcast.mp3 \
  --enable-diarization \
  --num-speakers 2

# With known speaker names and reference audio
audio-transcriber \
  --input interview.mp3 \
  --enable-diarization \
  --known-speaker-names "Alice Smith" "Bob Johnson" \
  --known-speaker-references alice_voice.wav bob_voice.wav
```

### AI Summarization

```bash
# Generate summary of transcription
audio-transcriber \
  --input lecture.mp3 \
  --summarize

# Custom summary model and prompt
audio-transcriber \
  --input podcast.mp3 \
  --summarize \
  --summary-model gpt-4o \
  --summary-prompt "Summarize the key points and action items"
```

### Document Export

```bash
# Export to Word document
audio-transcriber \
  --input meeting.mp3 \
  --export docx

# Export to multiple formats with metadata
audio-transcriber \
  --input interview.mp3 \
  --export docx md latex \
  --export-title "Company Interview 2026" \
  --export-author "John Doe"
```

### Integration with Other Services

**Groq (Fast):**
```bash
audio-transcriber \
  --api-key "gsk_..." \
  --base-url "https://api.groq.com/openai/v1" \
  --model "whisper-large-v3" \
  --input podcast.mp3
```

**Together.ai:**
```bash
audio-transcriber \
  --api-key "..." \
  --base-url "https://api.together.xyz/v1" \
  --model "whisper" \
  --input podcast.mp3
```

## 💻 Development

### Setup Development Environment

```bash
# Clone and install
git clone https://github.com/lucmuss/audio-transcriber.git
cd audio-transcriber
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Run Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=audio_transcriber --cov-report=html

# Specific test file
pytest tests/test_utils.py
```

### Code Quality

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Lint
flake8 src tests --max-line-length=100

# Type check
mypy src
```

## 📊 Performance & Costs

### OpenAI Whisper Pricing
- **Cost:** $0.0001 per minute (as of Jan 2026)
- **Example:** 60-minute podcast ≈ $0.006

### Performance Tips

1. **Increase Concurrency** (if API limits allow):
   ```bash
   --concurrency 8
   ```

2. **Adjust Segment Length** (larger = fewer API calls):
   ```bash
   --segment-length 900  # 15 minutes
   ```

3. **Use Local Models** (free & unlimited):
   ```bash
   # Ollama, LocalAI - no costs, faster for local hardware
   ```

4. **Batch Processing** (process multiple files efficiently):
   ```bash
   audio-transcriber --input ./folder_with_100_files
   ```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests
5. Run quality checks
6. Commit (`git commit -m 'feat: add amazing feature'`)
7. Push (`git push origin feature/amazing-feature`)
8. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with:
- [OpenAI Python Client](https://github.com/openai/openai-python) - API client
- [pydub](https://github.com/jiaaro/pydub) - Audio processing
- [tqdm](https://github.com/tqdm/tqdm) - Progress bars

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/lucmuss/audio-transcriber/issues)
- **Discussions:** [GitHub Discussions](https://github.com/lucmuss/audio-transcriber/discussions)
- **Documentation:** [README](https://github.com/lucmuss/audio-transcriber#readme)

---

**Made with ❤️ for the open-source community**
