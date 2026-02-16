#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BOOTSTRAP_SCRIPT="${PROJECT_ROOT}/scripts/bootstrap.sh"

echo "Starting Audio Transcriber container..."

if [[ -x "${BOOTSTRAP_SCRIPT}" ]]; then
    "${BOOTSTRAP_SCRIPT}" full
fi

if [[ "$#" -eq 0 ]]; then
    set -- audio-transcriber --help
fi

exec "$@"
