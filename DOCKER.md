# Docker Guide 🐳

Complete guide for using audio-transcriber with Docker.

## Table of Contents

- [Quick Start](#quick-start)
- [Building the Image](#building-the-image)
- [Running with Docker](#running-with-docker)
- [Using Docker Compose](#using-docker-compose)
- [Volume Mounting](#volume-mounting)
- [Environment Variables](#environment-variables)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Pull Pre-built Image (when available)

```bash
docker pull ghcr.io/lucmuss/audio-transcriber:latest
```

### Or Build Locally

```bash
docker build -t audio-transcriber .
```

### Run

```bash
# Set your API key
export AUDIO_TRANSCRIBE_API_KEY="sk-..."

# Transcribe a file
docker run --rm \
  -v $(pwd)/input:/app/input:ro \
  -v $(pwd)/output:/app/output \
  -e AUDIO_TRANSCRIBE_API_KEY \
  audio-transcriber \
  --input /app/input/podcast.mp3
```

---

## Building the Image

### Basic Build

```bash
docker build -t audio-transcriber:latest .
```

### Build with Specific Tag

```bash
docker build -t audio-transcriber:1.0.0 .
```

### Build with No Cache

```bash
docker build --no-cache -t audio-transcriber:latest .
```

### Multi-Platform Build

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t audio-transcriber:latest \
  .
```

---

## Running with Docker

### Basic Usage

```bash
docker run --rm \
  -v $(pwd)/audio:/app/input:ro \
  -v $(pwd)/transcriptions:/app/output \
  -e AUDIO_TRANSCRIBE_API_KEY="sk-..." \
  audio-transcriber \
  --input /app/input/file.mp3
```

### Interactive Mode

```bash
docker run -it --rm \
  -v $(pwd):/workspace \
  -e AUDIO_TRANSCRIBE_API_KEY \
  audio-transcriber \
  --input /workspace/podcast.mp3 \
  --verbose
```

### Using Environment File

Create `.env` file:
```bash
AUDIO_TRANSCRIBE_API_KEY=sk-...
AUDIO_TRANSCRIBE_BASE_URL=https://api.openai.com/v1
AUDIO_TRANSCRIBE_MODEL=whisper-1
```

Run with env file:
```bash
docker run --rm \
  --env-file .env \
  -v $(pwd)/audio:/app/input:ro \
  -v $(pwd)/output:/app/output \
  audio-transcriber \
  --input /app/input/podcast.mp3
```

---

## Using Docker Compose

### Basic docker-compose.yml

Already provided in the repository. Usage:

```bash
# Build the image
docker-compose build

# Run with default command (--help)
docker-compose run audio-transcriber

# Transcribe a file
docker-compose run audio-transcriber \
  --input /app/input/podcast.mp3
```

### Custom docker-compose.yml

```yaml
version: '3.8'

services:
  transcriber:
    image: audio-transcriber:latest
    environment:
      - AUDIO_TRANSCRIBE_API_KEY=${AUDIO_TRANSCRIBE_API_KEY}
    volumes:
      - ./my_audio:/app/input:ro
      - ./my_transcriptions:/app/output
    command: ["--input", "/app/input", "--verbose"]
```

### Run in Background

```bash
docker-compose up -d
```

### View Logs

```bash
docker-compose logs -f
```

### Stop and Remove

```bash
docker-compose down
```

---

## Volume Mounting

### Linux/macOS

```bash
# Current directory
-v $(pwd)/audio:/app/input:ro

# Absolute path
-v /home/user/audio:/app/input:ro

# Named volume
-v audio-data:/app/input
```

### Windows (PowerShell)

```powershell
# Current directory
-v ${PWD}/audio:/app/input:ro

# Absolute path
-v C:/Users/Name/audio:/app/input:ro
```

### Windows (CMD)

```cmd
# Current directory
-v %CD%/audio:/app/input:ro

# Absolute path
-v C:\Users\Name\audio:/app/input:ro
```

### Read-Only Mounts

```bash
# Prevent container from modifying input files
-v $(pwd)/audio:/app/input:ro
```

---

## Environment Variables

### Available Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AUDIO_TRANSCRIBE_API_KEY` | - | API key (required) |
| `AUDIO_TRANSCRIBE_BASE_URL` | OpenAI URL | API base URL |
| `AUDIO_TRANSCRIBE_MODEL` | `whisper-1` | Model name |
| `AUDIO_TRANSCRIBE_OUTPUT_DIR` | `/app/output` | Output directory |
| `AUDIO_TRANSCRIBE_SEGMENT_LENGTH` | `600` | Segment length (seconds) |
| `AUDIO_TRANSCRIBE_OVERLAP` | `10` | Overlap (seconds) |
| `AUDIO_TRANSCRIBE_CONCURRENCY` | `4` | Parallel processing |

### Setting Variables

**Command line:**
```bash
docker run --rm \
  -e AUDIO_TRANSCRIBE_API_KEY="sk-..." \
  -e AUDIO_TRANSCRIBE_MODEL="whisper-1" \
  -e AUDIO_TRANSCRIBE_CONCURRENCY=8 \
  audio-transcriber --input /app/input/file.mp3
```

**Environment file (.env):**
```bash
docker run --rm --env-file .env audio-transcriber ...
```

**Docker Compose:**
```yaml
environment:
  - AUDIO_TRANSCRIBE_API_KEY=${AUDIO_TRANSCRIBE_API_KEY}
  - AUDIO_TRANSCRIBE_CONCURRENCY=8
```

---

## Examples

### Example 1: Single File with OpenAI

```bash
docker run --rm \
  -v $(pwd):/workspace \
  -e AUDIO_TRANSCRIBE_API_KEY="sk-..." \
  audio-transcriber \
  --input /workspace/podcast.mp3 \
  --output-dir /workspace/transcriptions
```

### Example 2: Batch Processing Directory

```bash
docker run --rm \
  -v $(pwd)/podcasts:/app/input:ro \
  -v $(pwd)/transcriptions:/app/output \
  -e AUDIO_TRANSCRIBE_API_KEY \
  audio-transcriber \
  --input /app/input \
  --concurrency 6
```

### Example 3: Using Ollama (Local)

First, ensure Ollama is accessible from Docker:

```bash
# On host
ollama serve

# Run transcriber pointing to host
docker run --rm \
  --network host \
  -v $(pwd)/audio:/app/input:ro \
  -v $(pwd)/output:/app/output \
  audio-transcriber \
  --input /app/input/file.mp3 \
  --base-url "http://localhost:11434/v1" \
  --api-key "ollama" \
  --model "whisper"
```

Or use Docker Compose with Ollama:

```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama

  transcriber:
    image: audio-transcriber:latest
    depends_on:
      - ollama
    environment:
      - AUDIO_TRANSCRIBE_BASE_URL=http://ollama:11434/v1
      - AUDIO_TRANSCRIBE_API_KEY=ollama
      - AUDIO_TRANSCRIBE_MODEL=whisper
    volumes:
      - ./input:/app/input:ro
      - ./output:/app/output

volumes:
  ollama-data:
```

### Example 4: Generate Subtitles

```bash
docker run --rm \
  -v $(pwd)/videos:/app/input:ro \
  -v $(pwd)/subtitles:/app/output \
  -e AUDIO_TRANSCRIBE_API_KEY \
  audio-transcriber \
  --input /app/input/video.mp4 \
  --response-format srt
```

### Example 5: Using Groq API

```bash
docker run --rm \
  -v $(pwd)/audio:/app/input:ro \
  -v $(pwd)/output:/app/output \
  -e AUDIO_TRANSCRIBE_API_KEY="gsk_..." \
  -e AUDIO_TRANSCRIBE_BASE_URL="https://api.groq.com/openai/v1" \
  -e AUDIO_TRANSCRIBE_MODEL="whisper-large-v3" \
  audio-transcriber \
  --input /app/input/podcast.mp3
```

### Example 6: With Custom Settings

```bash
docker run --rm \
  -v $(pwd)/audio:/app/input:ro \
  -v $(pwd)/transcriptions:/app/output \
  -e AUDIO_TRANSCRIBE_API_KEY \
  audio-transcriber \
  --input /app/input/long_podcast.mp3 \
  --segment-length 900 \
  --overlap 15 \
  --concurrency 10 \
  --language de \
  --response-format json \
  --verbose
```

### Example 7: Keep Segments for Debugging

```bash
docker run --rm \
  -v $(pwd)/audio:/app/input:ro \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/segments:/app/segments \
  -e AUDIO_TRANSCRIBE_API_KEY \
  audio-transcriber \
  --input /app/input/file.mp3 \
  --keep-segments \
  --verbose
```

---

## Troubleshooting

### Problem: Permission Denied

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**

1. **Check directory permissions:**
```bash
chmod 755 input output
chmod 644 input/*.mp3
```

2. **Run with user ID:**
```bash
docker run --rm \
  --user $(id -u):$(id -g) \
  -v $(pwd)/audio:/app/input:ro \
  -v $(pwd)/output:/app/output \
  audio-transcriber ...
```

---

### Problem: Volume Not Mounting

**Symptoms:** Files not found in container

**Solutions:**

1. **Use absolute paths:**
```bash
docker run -v /full/path/to/audio:/app/input:ro ...
```

2. **Verify mount:**
```bash
docker run --rm -it \
  -v $(pwd)/audio:/app/input:ro \
  audio-transcriber \
  ls -la /app/input
```

---

### Problem: Cannot Connect to Ollama

**Error:**
```
Connection refused: http://localhost:11434
```

**Solution:**

Use host network or correct service name:

```bash
# Option 1: Host network (Linux only)
docker run --network host ...

# Option 2: Use host.docker.internal (Mac/Windows)
docker run \
  -e AUDIO_TRANSCRIBE_BASE_URL="http://host.docker.internal:11434/v1" \
  ...

# Option 3: Docker Compose with service name
# See Example 3 above
```

---

### Problem: Out of Memory

**Error:**
```
MemoryError: Unable to allocate ...
```

**Solution:**

Increase Docker memory limit:

```bash
# Run with memory limit
docker run --memory="2g" --rm ...
```

Or in docker-compose.yml:
```yaml
deploy:
  resources:
    limits:
      memory: 2G
```

---

### Problem: Image Too Large

**Solution:**

The image is already optimized with multi-stage build. If you need smaller:

1. **Use alpine-based image** (modify Dockerfile)
2. **Remove unnecessary dependencies**
3. **Use external volumes for data**

---

## Best Practices

### 1. Use Environment Files

Create `.env` file for sensitive data:
```bash
AUDIO_TRANSCRIBE_API_KEY=sk-...
```

Add to `.gitignore`:
```
.env
```

### 2. Named Volumes for Persistence

```bash
docker volume create audio-transcriptions

docker run --rm \
  -v audio-transcriptions:/app/output \
  audio-transcriber ...
```

### 3. Resource Limits

```bash
docker run --rm \
  --cpus="2.0" \
  --memory="2g" \
  audio-transcriber ...
```

### 4. Health Checks

Add to Dockerfile:
```dockerfile
HEALTHCHECK CMD audio-transcriber --version || exit 1
```

### 5. Logging

```bash
# Save logs
docker run --rm ... audio-transcriber ... 2>&1 | tee transcription.log

# Or with Docker Compose
docker-compose logs -f > logs.txt
```

---

## Advanced Usage

### Build and Push to Registry

```bash
# Build
docker build -t myregistry/audio-transcriber:1.0.0 .

# Login
docker login myregistry

# Push
docker push myregistry/audio-transcriber:1.0.0
```

### Automated Builds

Use GitHub Actions (see `.github/workflows/` for CI/CD).

### Kubernetes Deployment

Example Deployment:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: audio-transcription
spec:
  template:
    spec:
      containers:
      - name: transcriber
        image: audio-transcriber:latest
        env:
        - name: AUDIO_TRANSCRIBE_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: openai-key
        volumeMounts:
        - name: audio-storage
          mountPath: /app/input
        - name: output-storage
          mountPath: /app/output
      restartPolicy: Never
      volumes:
      - name: audio-storage
        persistentVolumeClaim:
          claimName: audio-pvc
      - name: output-storage
        persistentVolumeClaim:
          claimName: output-pvc
```

---

## Summary

Docker provides:
- ✅ Consistent environment across platforms
- ✅ No Python/FFmpeg installation required
- ✅ Easy deployment and scaling
- ✅ Isolation and security
- ✅ Simple CI/CD integration

For more information:
- [README.md](README.md) - Main documentation
- [USAGE_EXAMPLES.md](docs/USAGE_EXAMPLES.md) - Usage examples
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Troubleshooting guide
