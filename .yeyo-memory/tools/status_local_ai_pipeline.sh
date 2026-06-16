#!/bin/zsh
set -euo pipefail

ROOT_DIR="${YEYO_ROOT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
OUT_DIR="$ROOT_DIR/.yeyo-memory/local-ai"
LOG_DIR="$OUT_DIR/logs"
EVENTS_FILE="$OUT_DIR/events.jsonl"
STATE_FILE="$OUT_DIR/state.json"
RUN_LOCK="$OUT_DIR/run.lock"
SUPERVISOR_PID_FILE="$OUT_DIR/supervisor.pid"
WATCHDOG_LOG="$OUT_DIR/logs/ai-stack-watchdog.log"
WATCHDOG_PLIST="$HOME/Library/LaunchAgents/com.carlosdiaz.yeyo-local-ai-watchdog.plist"

check_url() {
  local url="$1"
  curl -fsS --max-time 5 "$url" >/dev/null 2>&1
}

status_line() {
  local label="$1"
  local value="$2"
  printf '%-24s %s\n' "$label" "$value"
}

count_recent_failures() {
  local pattern="$1"
  if [[ ! -f "$EVENTS_FILE" ]]; then
    echo 0
    return 0
  fi
  rg -c "$pattern" "$EVENTS_FILE" 2>/dev/null || echo 0
}

echo "Yeyo local AI pipeline status"
echo "root: $ROOT_DIR"
echo

gateway_status="down"
ollama_status="down"
mlx_status="down"
check_url "http://127.0.0.1:8318/healthz" && gateway_status="ok"
check_url "http://127.0.0.1:11434/api/tags" && ollama_status="ok"
check_url "http://127.0.0.1:8080/v1/models" && mlx_status="ok"

status_line "gateway (8318)" "$gateway_status"
status_line "ollama (11434)" "$ollama_status"
status_line "mlx (8080)" "$mlx_status"

watchdog_status="missing"
if [[ -f "$WATCHDOG_PLIST" ]]; then
  if launchctl print "gui/$(id -u)/com.carlosdiaz.yeyo-local-ai-watchdog" >/dev/null 2>&1; then
    watchdog_status="loaded"
  else
    watchdog_status="plist-present-not-loaded"
  fi
fi
status_line "watchdog" "$watchdog_status"

supervisor_status="down"
supervisor_pid=""
if [[ -f "$SUPERVISOR_PID_FILE" ]]; then
  supervisor_pid="$(cat "$SUPERVISOR_PID_FILE" 2>/dev/null || true)"
  if [[ -n "$supervisor_pid" ]] && kill -0 "$supervisor_pid" 2>/dev/null; then
    supervisor_status="running (pid $supervisor_pid)"
  else
    supervisor_status="stale pid $supervisor_pid"
  fi
fi
status_line "supervisor" "$supervisor_status"

generator_proc="$(pgrep -fal 'generate_local_ai_briefs.py' | head -n 1 || true)"
if [[ -n "$generator_proc" ]]; then
  status_line "generator" "$generator_proc"
else
  status_line "generator" "not running"
fi

if [[ -f "$RUN_LOCK" ]]; then
  lock_payload="$(cat "$RUN_LOCK" 2>/dev/null || true)"
  status_line "run.lock" "present"
  echo "$lock_payload" | sed 's/^/  /'
else
  status_line "run.lock" "absent"
fi

markdown_count="$(find "$OUT_DIR/markdown" -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
summary_count="$(find "$OUT_DIR/summaries" -type f -name '*.json' 2>/dev/null | wc -l | tr -d ' ')"
status_line "markdown files" "$markdown_count"
status_line "summary files" "$summary_count"

json_failures="$(count_recent_failures 'No se pudo parsear el JSON devuelto por la IA local')"
gateway_failures="$(count_recent_failures 'HTTP Error 502: Bad Gateway')"
status_line "json parse failures" "$json_failures"
status_line "502 failures" "$gateway_failures"

echo
echo "Recent events:"
tail -n 8 "$EVENTS_FILE" 2>/dev/null || echo "  no events"

echo
echo "Supervisor log tail:"
tail -n 12 "$LOG_DIR/supervisor.log" 2>/dev/null || echo "  no supervisor log"

echo
echo "Watchdog log tail:"
tail -n 12 "$WATCHDOG_LOG" 2>/dev/null || echo "  no watchdog log"

