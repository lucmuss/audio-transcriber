# Multi-stage build for smaller final image
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Set working directory
WORKDIR /app

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .
COPY README.md .
COPY LICENSE .

# Install the package
RUN pip install --no-cache-dir -e .

# Create directories for input/output
RUN mkdir -p /app/input /app/output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV AUDIO_TRANSCRIBE_OUTPUT_DIR=/app/output

# Set the entrypoint
ENTRYPOINT ["audio-transcriber"]

# Default command (can be overridden)
CMD ["--help"]
