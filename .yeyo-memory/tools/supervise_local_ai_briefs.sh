#!/bin/zsh
set -euo pipefail

ROOT_DIR="${YEYO_ROOT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
OUT_DIR="$ROOT_DIR/.yeyo-memory/local-ai"
LOG_DIR="$OUT_DIR/logs"
SUPERVISOR_LOG="$LOG_DIR/supervisor.log"
PID_FILE="$OUT_DIR/supervisor.pid"
STOP_FILE="$OUT_DIR/stop-supervisor"

mkdir -p "$LOG_DIR"

if [[ -f "$PID_FILE" ]]; then
  existing_pid="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [[ -n "$existing_pid" ]] && kill -0 "$existing_pid" 2>/dev/null; then
    echo "Supervisor ya activo con PID $existing_pid"
    exit 1
  fi
fi

echo $$ > "$PID_FILE"
trap 'rm -f "$PID_FILE"' EXIT

cd "$ROOT_DIR"

while true; do
  if [[ -f "$STOP_FILE" ]]; then
    echo "$(date '+%F %T') stop requested" >> "$SUPERVISOR_LOG"
    rm -f "$STOP_FILE"
    exit 0
  fi

  echo "$(date '+%F %T') run starting" >> "$SUPERVISOR_LOG"

  python3 .yeyo-memory/tools/generate_local_ai_briefs.py \
    --limit 0 \
    --model-policy size \
    --small-model claude-local-coder7b \
    --large-model claude-local-coder7b \
    --repair-model claude-local-coder7b \
    --small-doc-chars 12000 \
    --max-text-chars 300000 \
    --min-score 0 \
    --include-plans \
    --retry-failed \
    --max-doc-attempts 3 \
    --max-consecutive-failures 50 \
    --chunk-chars 8000 \
    --max-chunks-per-doc 0 \
    --gateway-recovery-wait 1800 \
    --gateway-poll-seconds 15 \
    --retries 2 \
    --timeout 600 \
    >> "$SUPERVISOR_LOG" 2>&1 || true

  echo "$(date '+%F %T') run ended; sleeping before next pass" >> "$SUPERVISOR_LOG"
  sleep 60
done
