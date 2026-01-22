# Usage Examples 📚

Comprehensive guide with 20+ practical examples for audio-transcriber.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Different Providers](#different-providers)
- [Advanced Segmentation](#advanced-segmentation)
- [Subtitle Generation](#subtitle-generation)
- [Speaker Diarization](#speaker-diarization)
- [AI Summarization](#ai-summarization)
- [Document Export](#document-export)
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

## Speaker Diarization

### Example 36: Basic Speaker Diarization

```bash
audio-transcriber \
  --input meeting.mp3 \
  --enable-diarization
```

**Output:** Automatically identifies different speakers and labels them as Speaker 1, Speaker 2, etc.

### Example 37: Diarization with Known Number of Speakers

```bash
audio-transcriber \
  --input podcast.mp3 \
  --enable-diarization \
  --num-speakers 2
```

**Use case:** Two-person interview or podcast.

### Example 38: Diarization with Known Speaker Names

```bash
audio-transcriber \
  --input panel_discussion.mp3 \
  --enable-diarization \
  --known-speaker-names "Alice Johnson" "Bob Smith" "Carol Williams"
```

**Output:** Speakers are labeled with their actual names instead of Speaker 1, Speaker 2, etc.

### Example 39: Diarization with Reference Audio

```bash
audio-transcriber \
  --input conference.mp3 \
  --enable-diarization \
  --known-speaker-names "Dr. Sarah Miller" "Prof. John Davis" \
  --known-speaker-references sarah_voice.wav john_voice.wav
```

**Use case:** Provide voice samples for more accurate speaker identification.

---

## AI Summarization

### Example 40: Basic Summarization

```bash
audio-transcriber \
  --input long_lecture.mp3 \
  --summarize
```

**Output:** 
- `transcriptions/long_lecture_mp3_full.text` (full transcription)
- `summaries/long_lecture_mp3_summary.txt` (AI-generated summary)

### Example 41: Custom Summary Model

```bash
audio-transcriber \
  --input podcast.mp3 \
  --summarize \
  --summary-model gpt-4o
```

**Use case:** Use a more powerful model for better summary quality.

### Example 42: Custom Summary Prompt

```bash
audio-transcriber \
  --input meeting.mp3 \
  --summarize \
  --summary-prompt "Provide a concise summary with: 1) Key discussion points, 2) Decisions made, 3) Action items with assigned owners"
```

### Example 43: Combined Diarization and Summarization

```bash
audio-transcriber \
  --input team_meeting.mp3 \
  --enable-diarization \
  --num-speakers 4 \
  --summarize \
  --summary-prompt "Summarize the key points discussed by each speaker"
```

---

## Document Export

### Example 44: Export to Word Document

```bash
audio-transcriber \
  --input interview.mp3 \
  --export docx
```

**Output:** `exports/interview.docx` (Microsoft Word format)

### Example 45: Export to Markdown

```bash
audio-transcriber \
  --input lecture.mp3 \
  --export md
```

**Output:** `exports/lecture.md` (Markdown format for GitHub, documentation, etc.)

### Example 46: Export to LaTeX

```bash
audio-transcriber \
  --input research_interview.mp3 \
  --export latex
```

**Output:** `exports/research_interview.tex` (for academic papers)

### Example 47: Export to Multiple Formats with Metadata

```bash
audio-transcriber \
  --input conference_talk.mp3 \
  --export docx md latex \
  --export-title "AI Conference 2026 - Keynote Speech" \
  --export-author "Dr. Emily Chen" \
  --export-dir ./publications
```

**Output:** Creates DOCX, Markdown, and LaTeX files with proper metadata and formatting.

### Example 48: Complete Professional Workflow

```bash
audio-transcriber \
  --input board_meeting.mp3 \
  --enable-diarization \
  --known-speaker-names "CEO Alice" "CFO Bob" "CTO Carol" \
  --summarize \
  --export docx \
  --export-title "Q1 2026 Board Meeting Minutes" \
  --export-author "Corporate Secretary"
```

**Output:**
- Full diarized transcription
- AI summary
- Professional Word document with metadata

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

### Example 34: Podcast Post-Production (Enhanced)

```bash
#!/bin/bash
# Complete podcast workflow with new features

EPISODE="episode_42.mp3"
TITLE="The Future of AI"

# All-in-one: transcription, diarization, summary, and export
audio-transcriber \
  --input "$EPISODE" \
  --enable-diarization \
  --num-speakers 2 \
  --known-speaker-names "Host John" "Guest Dr. Smith" \
  --summarize \
  --summary-prompt "Create show notes with: main topics, key insights, and timestamps" \
  --export docx md \
  --export-title "$TITLE - Episode 42" \
  --export-author "TechPod Productions" \
  --response-format srt

echo "Podcast $TITLE processed successfully!"
echo "✓ Diarized transcript with speaker labels"
echo "✓ AI-generated summary for show notes"
echo "✓ SRT subtitles for video version"
echo "✓ Word & Markdown documents"
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
- ✅ Multiple API providers (OpenAI, Groq, Ollama, Together.ai, Azure, LocalAI)
- ✅ Advanced segmentation strategies
- ✅ Subtitle generation (SRT, VTT)
- ✅ **Speaker diarization (NEW)** - Identify who said what
- ✅ **AI summarization (NEW)** - Generate concise summaries
- ✅ **Document export (NEW)** - DOCX, Markdown, LaTeX formats
- ✅ Batch processing techniques
- ✅ Language handling (40+ languages)
- ✅ Automation scripts
- ✅ Integration workflows
- ✅ Quality assurance

## New Features Quick Reference

| Feature | Command | Output |
|---------|---------|--------|
| Speaker Diarization | `--enable-diarization` | Labels who said what |
| AI Summary | `--summarize` | Concise summary in `./summaries/` |
| Export to Word | `--export docx` | `.docx` file in `./exports/` |
| Export to Markdown | `--export md` | `.md` file in `./exports/` |
| Export to LaTeX | `--export latex` | `.tex` file in `./exports/` |
| Live Progress | (automatic) | ETA, throughput, cost tracking |

For more help, see:
- [README.md](../README.md) - Main documentation
- [QUICKSTART.md](../QUICKSTART.md) - Quick start guide
- [GUI_GUIDE.md](../GUI_GUIDE.md) - GUI usage instructions
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues
- [GitHub Issues](https://github.com/lucmuss/audio-transcriber/issues) - Report problems
