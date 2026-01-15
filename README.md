# Audio Transcriber 🎙️

[![CI](https://github.com/lucmuss/audio-transcriber/workflows/CI/badge.svg)](https://github.com/lucmuss/audio-transcriber/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Professional audio transcription tool using OpenAI-compatible Speech-to-Text APIs with intelligent segmentation and merging.

## ✨ Features

- **🔄 Intelligent Segmentation** - Automatically splits large audio files into processable chunks
- **⚡ Parallel Processing** - Concurrent transcription of multiple segments for faster results
- **🎯 Smart Merging** - Overlap detection and removal for seamless final transcripts
- **🌍 Multi-Format Support** - MP3, WAV, FLAC, M4A, OGG, AAC, WMA, MP4
- **📝 Multiple Output Formats** - Text, JSON, SRT, VTT subtitles, Verbose JSON
- **🔌 OpenAI-Compatible** - Works with OpenAI, Ollama, Groq, LocalAI, Azure, Together.ai
- **🔁 Resume Capability** - Automatically skips already processed files
- **📊 Progress Tracking** - Real-time progress bars and detailed statistics
- **🌐 Language Detection** - Automatic language detection from audio
- **💰 Cost Estimation** - Calculates estimated transcription costs

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
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## ⚡ Quick Start

```bash
# Set your API key
export AUDIO_TRANSCRIBE_API_KEY="sk-..."

# Transcribe a single file
audio-transcriber --input podcast.mp3

# Transcribe all files in a directory
audio-transcriber --input ./audio_files
```

Output will be saved to `./transcriptions/` by default.

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

| Option | Description | Default |
|--------|-------------|---------|
| `-i, --input` | Path to audio file or directory | Required |
| `-o, --output-dir` | Output directory | `./transcriptions` |
| `-f, --response-format` | Output format (text/json/srt/vtt/verbose_json) | `text` |
| `--segment-length` | Segment length in seconds | `600` (10 min) |
| `--overlap` | Overlap between segments in seconds | `10` |
| `-c, --concurrency` | Number of parallel transcriptions | `4` |
| `--language` | ISO-639-1 language code (e.g., 'en', 'de') | Auto-detect |
| `--temperature` | Model temperature (0.0-1.0) | `0.0` |
| `--model` | Model name | `whisper-1` |
| `--api-key` | API key | From env var |
| `--base-url` | API base URL | OpenAI endpoint |
| `--keep-segments` | Keep temporary segment files | `false` |
| `-v, --verbose` | Enable verbose logging | `false` |

### Environment Variables

```bash
export AUDIO_TRANSCRIBE_API_KEY="sk-..."
export AUDIO_TRANSCRIBE_BASE_URL="https://api.openai.com/v1"
export AUDIO_TRANSCRIBE_MODEL="whisper-1"
export AUDIO_TRANSCRIBE_OUTPUT_DIR="./transcriptions"
export AUDIO_TRANSCRIBE_SEGMENT_LENGTH="600"
export AUDIO_TRANSCRIBE_OVERLAP="10"
export AUDIO_TRANSCRIBE_CONCURRENCY="4"
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
python -m venv venv
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

## 🗺️ Roadmap

- [ ] GUI interface
- [ ] Speaker diarization (identify different speakers)
- [ ] Real-time transcription
- [ ] Cloud deployment templates
- [ ] Additional language models support
- [ ] Docker container

---

**Made with ❤️ for the open-source community**
