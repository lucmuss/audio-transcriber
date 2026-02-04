#!/bin/bash
set -e

echo "Starting Audio Transcriber container..."

# Run tests after "migrations" (there are no migrations, but run tests for quality assurance)
if [ "$RUN_TESTS" = "true" ]; then
    echo "Running tests..."
    python -m pytest tests/ -v --tb=short
    echo "Tests passed."
fi

# For development, you might want to start a shell or run the app
# For production, this could be the entry point for the CLI
exec "$@"