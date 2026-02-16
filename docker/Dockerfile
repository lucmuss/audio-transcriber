FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_ENVIRONMENT=/app/.venv
ENV PATH="/root/.local/bin:/app/.venv/bin:${PATH}"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    ffmpeg && \
    rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY docker/entrypoint.sh ./docker/entrypoint.sh

RUN chmod +x ./docker/entrypoint.sh ./scripts/bootstrap.sh
RUN uv sync --frozen

RUN mkdir -p /app/input /app/output /app/transcriptions /app/segments /app/summaries /app/exports
ENV AUDIO_TRANSCRIBE_OUTPUT_DIR=/app/output

ENTRYPOINT ["./docker/entrypoint.sh"]
CMD ["audio-transcriber", "--help"]
