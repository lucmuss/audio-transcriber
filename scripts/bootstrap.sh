#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

BOOTSTRAP_DEBUG="${BOOTSTRAP_DEBUG:-false}"

log() {
    printf '[bootstrap] %s\n' "$1"
}

debug_log() {
    if [[ "${BOOTSTRAP_DEBUG}" == "true" ]]; then
        log "DEBUG: $1"
    fi
}

is_true() {
    case "${1:-}" in
        1|[Tt][Rr][Uu][Ee]|[Yy]|[Yy][Ee][Ss]|[Oo][Nn]) return 0 ;;
        *) return 1 ;;
    esac
}

load_env() {
    if [[ -f ".env" ]]; then
        log "Lade Variablen aus .env"
        set -a
        # shellcheck disable=SC1091
        source ".env"
        set +a
    else
        debug_log ".env nicht gefunden, nutze nur bestehende Umgebungsvariablen."
    fi
}

prepare_directories() {
    local output_dir="${AUDIO_TRANSCRIBE_OUTPUT_DIR:-./transcriptions}"
    local segments_dir="${AUDIO_TRANSCRIBE_SEGMENTS_DIR:-./segments}"
    local summary_dir="${AUDIO_TRANSCRIBE_SUMMARY_DIR:-./summaries}"
    local export_dir="${AUDIO_TRANSCRIBE_EXPORT_DIR:-./exports}"

    mkdir -p "$output_dir" "$segments_dir" "$summary_dir" "$export_dir"
    log "Verzeichnisse vorbereitet: $output_dir, $segments_dir, $summary_dir, $export_dir"
}

run_tests() {
    if is_true "${RUN_TESTS:-false}"; then
        log "RUN_TESTS=true erkannt. Starte Tests."
        if command -v uv >/dev/null 2>&1; then
            uv run pytest tests/ -v --tb=short
        else
            python -m pytest tests/ -v --tb=short
        fi
    else
        debug_log "RUN_TESTS ist nicht true. Tests werden uebersprungen."
    fi
}

show_dev_info() {
    log "Bootstrap abgeschlossen."
}

full_bootstrap() {
    load_env
    prepare_directories
    run_tests
    show_dev_info
}

usage() {
    cat <<'EOF'
Usage: ./scripts/bootstrap.sh [command]

Commands:
  full                 Vollstaendiger Bootstrap (default)
  load_env             Nur .env laden (wenn vorhanden)
  prepare_directories  Ausgabeverzeichnisse erstellen
  run_tests            Tests ausfuehren (nur bei RUN_TESTS=true)
  show_dev_info        Abschlussmeldung ausgeben
EOF
}

main() {
    local command="${1:-full}"
    case "$command" in
        full)
            full_bootstrap
            ;;
        load_env)
            load_env
            ;;
        prepare_directories)
            load_env
            prepare_directories
            ;;
        run_tests)
            load_env
            run_tests
            ;;
        show_dev_info)
            load_env
            show_dev_info
            ;;
        -h|--help|help)
            usage
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

main "$@"
