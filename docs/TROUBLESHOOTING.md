# Troubleshooting Guide 🔧

Common issues and their solutions for audio-transcriber.

## Table of Contents

- [Installation Issues](#installation-issues)
- [API & Authentication](#api--authentication)
- [Audio Processing](#audio-processing)
- [Performance Issues](#performance-issues)
- [Platform-Specific](#platform-specific)
- [Output & Formatting](#output--formatting)
- [Advanced Debugging](#advanced-debugging)

---

## Installation Issues

### Problem: FFmpeg not found

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'
```

**Solution:**

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
```bash
choco install ffmpeg
# Or download from https://ffmpeg.org/download.html
```

**Verify installation:**
```bash
ffmpeg -version
```

---

### Problem: pip install fails

**Error:**
```
error: metadata-generation-failed
```

**Solution:**

1. Upgrade pip:
```bash
python -m pip install --upgrade pip
```

2. Install build tools:
```bash
pip install setuptools wheel
```

3. Try again:
```bash
pip install -e .
```

---

### Problem: Python version too old

**Error:**
```
ERROR: Package requires Python >=3.8
```

**Solution:**

Check your Python version:
```bash
python --version
```

Install Python 3.8 or higher:
- **Ubuntu:** `sudo apt-get install python3.11`
- **macOS:** `brew install python@3.11`
- **Windows:** Download from python.org

---

## API & Authentication

### Problem: API key not recognized

**Error:**
```
openai.AuthenticationError: Invalid API key
```

**Solutions:**

1. **Check environment variable:**
```bash
echo $AUDIO_TRANSCRIBE_API_KEY  # Linux/macOS
echo %AUDIO_TRANSCRIBE_API_KEY%  # Windows
```

2. **Set environment variable correctly:**
```bash
# Linux/macOS
export AUDIO_TRANSCRIBE_API_KEY="sk-..."

# Windows CMD
set AUDIO_TRANSCRIBE_API_KEY=sk-...

# Windows PowerShell
$env:AUDIO_TRANSCRIBE_API_KEY="sk-..."
```

3. **Use command-line option:**
```bash
audio-transcriber --input file.mp3 --api-key "sk-..."
```

4. **Verify key format:**
- OpenAI: starts with `sk-`
- Groq: starts with `gsk_`

---

### Problem: Rate limit exceeded

**Error:**
```
openai.RateLimitError: Rate limit reached
```

**Solutions:**

1. **Reduce concurrency:**
```bash
audio-transcriber --input file.mp3 --concurrency 2
```

2. **Add delays between segments:**
Modify segment processing to include delays.

3. **Use different API provider:**
```bash
# Try Groq (higher free tier limits)
audio-transcriber \
  --input file.mp3 \
  --base-url "https://api.groq.com/openai/v1" \
  --api-key "gsk_..."
```

4. **Upgrade API plan** if using OpenAI frequently.

---

### Problem: Connection timeout

**Error:**
```
requests.exceptions.ConnectionError: Connection timeout
```

**Solutions:**

1. **Check internet connection**

2. **Try different API endpoint:**
```bash
# Use Ollama locally (no internet required)
audio-transcriber \
  --input file.mp3 \
  --base-url "http://localhost:11434/v1" \
  --api-key "ollama"
```

3. **Check firewall/proxy settings**

4. **Increase timeout** (if feature available in future versions)

---

## Audio Processing

### Problem: Audio file not supported

**Error:**
```
pydub.exceptions.CouldntDecodeError: Decoding failed
```

**Solutions:**

1. **Check file format:**
```bash
ffprobe -i yourfile.xxx
```

2. **Convert to supported format:**
```bash
ffmpeg -i input.xxx -acodec libmp3lame output.mp3
```

3. **Supported formats:**
- MP3, WAV, FLAC, M4A, OGG, AAC, WMA, MP4

---

### Problem: File too large

**Error:**
```
File size exceeds maximum (25 MB)
```

**Solutions:**

The tool **automatically segments** large files, but if you still have issues:

1. **Reduce segment length:**
```bash
audio-transcriber --input large.mp3 --segment-length 300
```

2. **Compress audio first:**
```bash
# Reduce bitrate
ffmpeg -i input.mp3 -b:a 64k output.mp3
```

3. **Convert to mono:**
```bash
ffmpeg -i stereo.mp3 -ac 1 mono.mp3
```

---

### Problem: Poor transcription quality

**Symptoms:**
- Missing words
- Incorrect transcriptions
- Garbled text

**Solutions:**

1. **Improve audio quality:**
```bash
# Noise reduction with ffmpeg
ffmpeg -i noisy.mp3 -af "highpass=f=200, lowpass=f=3000" clean.mp3
```

2. **Use context prompt:**
```bash
audio-transcriber \
  --input podcast.mp3 \
  --prompt "Podcast about AI and machine learning with technical terms like neural networks, transformers, GPT."
```

3. **Specify language:**
```bash
audio-transcriber --input file.mp3 --language en
```

4. **Use better model:**
```bash
# Groq with large model
audio-transcriber \
  --input file.mp3 \
  --base-url "https://api.groq.com/openai/v1" \
  --model "whisper-large-v3"
```

5. **Adjust segment overlap:**
```bash
audio-transcriber --input file.mp3 --overlap 15
```

---

### Problem: Segments not merging correctly

**Symptoms:**
- Duplicate sentences
- Missing transitions
- Choppy output

**Solutions:**

1. **Increase overlap:**
```bash
audio-transcriber --input file.mp3 --overlap 20
```

2. **Adjust segment length:**
```bash
audio-transcriber --input file.mp3 --segment-length 900
```

3. **Keep segments for debugging:**
```bash
audio-transcriber --input file.mp3 --keep-segments --verbose
```

4. **Check individual segments** in temp directory.

---

## Performance Issues

### Problem: Transcription too slow

**Solutions:**

1. **Increase concurrency:**
```bash
audio-transcriber --input file.mp3 --concurrency 8
```

2. **Use faster API provider:**
```bash
# Groq is typically faster
audio-transcriber \
  --input file.mp3 \
  --base-url "https://api.groq.com/openai/v1" \
  --api-key "gsk_..."
```

3. **Use local model (Ollama):**
```bash
# One-time setup
ollama pull whisper

# Fast local processing
audio-transcriber \
  --input file.mp3 \
  --base-url "http://localhost:11434/v1" \
  --api-key "ollama"
```

4. **Optimize segment length:**
```bash
# Longer segments = fewer API calls
audio-transcriber --input file.mp3 --segment-length 900
```

---

### Problem: High memory usage

**Solutions:**

1. **Reduce concurrency:**
```bash
audio-transcriber --input file.mp3 --concurrency 2
```

2. **Process files one at a time:**
```bash
# Instead of whole directory
for file in ./audio/*.mp3; do
  audio-transcriber --input "$file"
done
```

3. **Don't keep segments:**
```bash
# Default behavior (segments are deleted)
audio-transcriber --input file.mp3
```

---

## Platform-Specific

### Windows: Path issues

**Problem:**
```
FileNotFoundError: [WinError 3] Path not found
```

**Solutions:**

1. **Use forward slashes:**
```bash
audio-transcriber --input ./audio/file.mp3
```

2. **Or escape backslashes:**
```bash
audio-transcriber --input .\\audio\\file.mp3
```

3. **Use absolute paths:**
```bash
audio-transcriber --input "C:/Users/Name/audio/file.mp3"
```

---

### Windows: Unicode filenames

**Problem:**
Files with non-ASCII characters fail to process.

**Solutions:**

1. **Rename files to ASCII:**
```bash
# Before: "Café_Müller.mp3"
# After: "Cafe_Mueller.mp3"
```

2. **Use UTF-8 encoding** (automatic in Python 3.8+).

---

### macOS: Permission denied

**Problem:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**

1. **Check file permissions:**
```bash
ls -l file.mp3
chmod 644 file.mp3
```

2. **Check directory permissions:**
```bash
chmod 755 ./audio
```

---

### Linux: Missing codecs

**Problem:**
```
Codec not available
```

**Solutions:**

1. **Install full FFmpeg:**
```bash
sudo apt-get install ffmpeg libavcodec-extra
```

2. **For Ubuntu, add universe repository:**
```bash
sudo add-apt-repository universe
sudo apt-get update
sudo apt-get install ubuntu-restricted-extras
```

---

## Output & Formatting

### Problem: Output file empty

**Symptoms:**
- File created but contains no text
- Size is 0 bytes

**Solutions:**

1. **Check with verbose mode:**
```bash
audio-transcriber --input file.mp3 --verbose
```

2. **Verify audio has speech:**
```bash
ffplay file.mp3  # Listen to the audio
```

3. **Try different format:**
```bash
audio-transcriber --input file.mp3 --response-format json
```

4. **Check API credits/quota**

---

### Problem: Wrong output format

**Solutions:**

1. **Specify format explicitly:**
```bash
audio-transcriber --input file.mp3 --response-format srt
```

2. **Available formats:**
- `text` - Plain text (default)
- `json` - JSON with metadata
- `srt` - SubRip subtitles
- `vtt` - WebVTT subtitles
- `verbose_json` - Detailed JSON

---

### Problem: Subtitles not synced

**Solutions:**

1. **Use smaller segments:**
```bash
audio-transcriber \
  --input video.mp4 \
  --response-format srt \
  --segment-length 300
```

2. **Increase overlap:**
```bash
audio-transcriber \
  --input video.mp4 \
  --response-format srt \
  --overlap 15
```

3. **Manually adjust** SRT file if needed.

---

## Advanced Debugging

### Enable verbose logging

```bash
audio-transcriber --input file.mp3 --verbose
```

Shows:
- Segment creation details
- API calls
- Merge operations
- File operations

---

### Keep intermediate files

```bash
audio-transcriber --input file.mp3 --keep-segments
```

Check segments in temp directory for issues.

---

### Test with small file first

```bash
# Create 30-second test clip
ffmpeg -i large.mp3 -t 30 test.mp3

# Transcribe test clip
audio-transcriber --input test.mp3 --verbose
```

---

### Check Python environment

```bash
# Verify Python version
python --version

# Verify packages
pip list | grep -E "openai|pydub|tqdm"

# Check installation
pip show audio-transcriber
```

---

### Run pytest for diagnostics

```bash
# Clone repository
git clone https://github.com/lucmuss/audio-transcriber.git
cd audio-transcriber

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v
```

---

## Getting Help

If none of these solutions work:

1. **Check existing issues:**
   - [GitHub Issues](https://github.com/lucmuss/audio-transcriber/issues)

2. **Create new issue with:**
   - Error message (full traceback)
   - Command you ran
   - Python version (`python --version`)
   - FFmpeg version (`ffmpeg -version`)
   - Operating system
   - Audio file details (`ffprobe -i file.mp3`)

3. **Include verbose output:**
```bash
audio-transcriber --input file.mp3 --verbose 2>&1 | tee debug.log
```

4. **Join discussions:**
   - [GitHub Discussions](https://github.com/lucmuss/audio-transcriber/discussions)

---

## Quick Checklist

Before reporting an issue, verify:

- [ ] FFmpeg is installed (`ffmpeg -version`)
- [ ] Python >=3.8 (`python --version`)
- [ ] API key is set correctly
- [ ] Audio file is valid (`ffprobe -i file.mp3`)
- [ ] Internet connection (if using remote API)
- [ ] Verbose mode doesn't reveal obvious error
- [ ] Tried with small test file
- [ ] Checked existing GitHub issues

---

**Most issues can be resolved with verbose logging and checking the basics above!**
