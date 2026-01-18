# Usage Examples 📚

Comprehensive guide with 20+ practical examples for audio-transcriber.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Different Providers](#different-providers)
- [Advanced Segmentation](#advanced-segmentation)
- [Subtitle Generation](#subtitle-generation)
- [Batch Processing](#batch-processing)
- [Language-Specific](#language-specific)
- [Integration Examples](#integration-examples)
- [Scripting & Automation](#scripting--automation)

---

## Basic Usage

### Example 1: Simple Single File Transcription

```bash
audio-transcriber --input podcast.mp3
```

**Output:** `transcriptions/podcast.txt`

### Example 2: Custom Output Directory

```bash
audio-transcriber --input lecture.mp3 --output-dir ./my_transcriptions
```

### Example 3: JSON Format Output

```bash
audio-transcriber --input interview.mp3 --response-format json
```

**Output includes:** Full text, segments with timestamps, language detection, and metadata.

### Example 4: Verbose Logging

```bash
audio-transcriber --input podcast.mp3 --verbose
```

Shows detailed processing information, API calls, and segment details.

---

## Different Providers

### Example 5: OpenAI Whisper (Default)

```bash
export AUDIO_TRANSCRIBE_API_KEY="sk-..."
audio-transcriber --input podcast.mp3
```

### Example 6: Local Ollama (Free & Private)

```bash
# Start Ollama server first
ollama serve

# Transcribe
audio-transcriber \
  --input podcast.mp3 \
  --base-url http://localhost:11434/v1 \
  --api-key ollama \
  --model whisper
```

### Example 7: Groq (Fast & Free Tier)

```bash
audio-transcriber \
  --input meeting.mp3 \
  --api-key "gsk_..." \
  --base-url "https://api.groq.com/openai/v1" \
  --model "whisper-large-v3"
```

### Example 8: Together.ai

```bash
audio-transcriber \
  --input podcast.mp3 \
  --api-key "..." \
  --base-url "https://api.together.xyz/v1" \
  --model "whisper-large-v3"
```

### Example 9: Azure OpenAI

```bash
audio-transcriber \
  --input audio.mp3 \
  --api-key "your-azure-key" \
  --base-url "https://your-resource.openai.azure.com/openai/deployments/whisper/audio" \
  --model "whisper"
```

### Example 10: LocalAI (Self-Hosted)

```bash
audio-transcriber \
  --input podcast.mp3 \
  --base-url "http://localhost:8080/v1" \
  --api-key "local" \
  --model "whisper-1"
```

---

## Advanced Segmentation

### Example 11: Longer Segments for Better Context

```bash
audio-transcriber \
  --input long_podcast.mp3 \
  --segment-length 900 \
  --overlap 15
```

**Use case:** 15-minute segments with 15-second overlap for better context continuity.

### Example 12: Maximum Concurrency

```bash
audio-transcriber \
  --input large_file.mp3 \
  --concurrency 10
```

**Note:** Check your API rate limits before increasing concurrency.

### Example 13: Keep Segment Files for Debugging

```bash
audio-transcriber \
  --input problematic_audio.mp3 \
  --keep-segments \
  --verbose
```

Useful for troubleshooting segmentation issues.

### Example 14: Custom Temperature for Creative Content

```bash
audio-transcriber \
  --input creative_podcast.mp3 \
  --temperature 0.3
```

**Default is 0.0** (most deterministic). Higher values (up to 1.0) allow more variation.

---

## Subtitle Generation

### Example 15: SRT Subtitles

```bash
audio-transcriber \
  --input video.mp4 \
  --response-format srt \
  --output-dir ./subtitles
```

**Output:** `subtitles/video.srt` (compatible with most video players)

### Example 16: WebVTT Subtitles for Web

```bash
audio-transcriber \
  --input presentation.mp4 \
  --response-format vtt
```

**Use case:** HTML5 video `<track>` elements.

### Example 17: Multi-Language Subtitles

```bash
# German
audio-transcriber --input video.mp4 --response-format srt --language de -o ./subs/de

# English
audio-transcriber --input video.mp4 --response-format srt --language en -o ./subs/en

# French
audio-transcriber --input video.mp4 --response-format srt --language fr -o ./subs/fr
```

---

## Batch Processing

### Example 18: Process Entire Directory

```bash
audio-transcriber --input ./podcast_episodes
```

Processes all audio files in the directory.

### Example 19: Resume Interrupted Batch Job

```bash
# Start processing
audio-transcriber --input ./100_files

# Interrupted with Ctrl+C or crash
# ...

# Resume - automatically skips completed files
audio-transcriber --input ./100_files
```

### Example 20: Filter by File Type

```bash
# Process only MP3 files
find ./audio -name "*.mp3" -exec audio-transcriber --input {} \;

# Or use a loop
for file in ./audio/*.mp3; do
  audio-transcriber --input "$file"
done
```

---

## Language-Specific

### Example 21: Auto-Detect Language

```bash
audio-transcriber \
  --input multilingual_audio.mp3 \
  --detect-language
```

### Example 22: German Transcription

```bash
audio-transcriber \
  --input deutsches_interview.mp3 \
  --language de
```

### Example 23: Spanish with Context Prompt

```bash
audio-transcriber \
  --input spanish_podcast.mp3 \
  --language es \
  --prompt "Este es un podcast sobre tecnología y inteligencia artificial."
```

### Example 24: Technical Content with Terminology

```bash
audio-transcriber \
  --input tech_conference.mp3 \
  --language en \
  --prompt "Technical presentation featuring terms: Kubernetes, Docker, CI/CD, microservices, API gateway, service mesh. Speakers: Dr. Jane Smith, Prof. John Doe."
```

---

## Integration Examples

### Example 25: Integrate with YouTube-DL

```bash
#!/bin/bash
# Download and transcribe YouTube video

VIDEO_URL="https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Download audio
yt-dlp -x --audio-format mp3 -o "youtube_audio.mp3" "$VIDEO_URL"

# Transcribe
audio-transcriber --input youtube_audio.mp3 --response-format srt
```

### Example 26: Process with FFmpeg Pre-Processing

```bash
# Extract audio from video and transcribe
ffmpeg -i video.mkv -vn -acodec libmp3lame -q:a 2 audio.mp3
audio-transcriber --input audio.mp3
```

### Example 27: Combine with Translation API

```bash
#!/bin/bash
# Transcribe and translate

# Transcribe to JSON
audio-transcriber --input spanish_audio.mp3 --response-format json -o transcript.json

# Parse and translate (pseudo-code)
# cat transcript.json | jq '.text' | translate-cli es en > translated.txt
```

---

## Scripting & Automation

### Example 28: Cron Job for Automated Processing

```bash
# Add to crontab
0 2 * * * cd /path/to/project && audio-transcriber --input ./incoming --output-dir ./processed
```

Runs daily at 2 AM.

### Example 29: Watch Folder Script

```bash
#!/bin/bash
# watch_and_transcribe.sh

WATCH_DIR="./incoming"
OUTPUT_DIR="./transcriptions"

inotifywait -m -e close_write "$WATCH_DIR" |
while read path action file; do
  if [[ "$file" =~ \.(mp3|wav|m4a)$ ]]; then
    echo "New file detected: $file"
    audio-transcriber --input "$WATCH_DIR/$file" --output-dir "$OUTPUT_DIR"
  fi
done
```

### Example 30: Parallel Processing Script

```bash
#!/bin/bash
# parallel_transcribe.sh

INPUT_DIR="./audio_files"
OUTPUT_DIR="./transcriptions"
MAX_PARALLEL=4

find "$INPUT_DIR" -type f \( -name "*.mp3" -o -name "*.wav" \) | \
  xargs -n 1 -P "$MAX_PARALLEL" -I {} \
  audio-transcriber --input {} --output-dir "$OUTPUT_DIR"
```

### Example 31: Cost Estimation Before Processing

```bash
#!/bin/bash
# estimate_costs.sh

TOTAL_DURATION=0

for file in ./audio/*.mp3; do
  DURATION=$(ffprobe -i "$file" -show_entries format=duration -v quiet -of csv="p=0")
  TOTAL_DURATION=$(echo "$TOTAL_DURATION + $DURATION" | bc)
done

TOTAL_MINUTES=$(echo "$TOTAL_DURATION / 60" | bc)
ESTIMATED_COST=$(echo "$TOTAL_MINUTES * 0.0001" | bc -l)

echo "Total duration: $TOTAL_MINUTES minutes"
echo "Estimated cost (OpenAI): \$$ESTIMATED_COST"
```

### Example 32: Metadata Preservation

```bash
#!/bin/bash
# transcribe_with_metadata.sh

INPUT="$1"
BASENAME=$(basename "$INPUT" .mp3)

# Transcribe
audio-transcriber --input "$INPUT" --response-format json -o "transcriptions/${BASENAME}.json"

# Extract metadata
ffprobe -v quiet -print_format json -show_format "$INPUT" > "transcriptions/${BASENAME}_metadata.json"

echo "Transcription and metadata saved for: $BASENAME"
```

---

## Advanced Workflows

### Example 33: Conference Recording Processing

```bash
#!/bin/bash
# Process multi-speaker conference recording

INPUT="conference_2024.mp3"

# High-quality transcription with speaker context
audio-transcriber \
  --input "$INPUT" \
  --response-format verbose_json \
  --segment-length 600 \
  --overlap 10 \
  --temperature 0.0 \
  --prompt "Conference recording with multiple speakers discussing AI and machine learning. Main speakers: Dr. Sarah Johnson, Prof. Michael Chen, Dr. Emily Rodriguez." \
  --output-dir ./conference_transcripts
```

### Example 34: Podcast Post-Production

```bash
#!/bin/bash
# Complete podcast workflow

EPISODE="episode_42.mp3"
TITLE="The Future of AI"

# 1. Transcribe for show notes
audio-transcriber --input "$EPISODE" --response-format text -o "shownotes.txt"

# 2. Generate subtitles for video version
audio-transcriber --input "$EPISODE" --response-format srt -o "subtitles.srt"

# 3. Generate JSON for searching
audio-transcriber --input "$EPISODE" --response-format json -o "searchable.json"

echo "Podcast $TITLE processed successfully!"
```

### Example 35: Quality Assurance Check

```bash
#!/bin/bash
# Transcribe same file with different providers and compare

FILE="test_audio.mp3"

# OpenAI
audio-transcriber --input "$FILE" -o "./qa/openai.txt"

# Groq
audio-transcriber --input "$FILE" \
  --base-url "https://api.groq.com/openai/v1" \
  --api-key "$GROQ_KEY" \
  -o "./qa/groq.txt"

# Ollama (local)
audio-transcriber --input "$FILE" \
  --base-url "http://localhost:11434/v1" \
  --api-key "ollama" \
  -o "./qa/ollama.txt"

# Compare results
diff ./qa/openai.txt ./qa/groq.txt
```

---

## Summary

These examples cover:
- ✅ Basic to advanced usage patterns
- ✅ Multiple API providers
- ✅ Batch processing techniques
- ✅ Subtitle generation
- ✅ Language handling
- ✅ Automation scripts
- ✅ Integration workflows
- ✅ Quality assurance

For more help, see:
- [README.md](../README.md) - Main documentation
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues
- [GitHub Issues](https://github.com/lucmuss/audio-transcriber/issues) - Report problems
