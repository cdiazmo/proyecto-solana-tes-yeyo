#!/bin/zsh
set -euo pipefail

ROOT_DIR="${YEYO_ROOT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
OUT_DIR="$ROOT_DIR/.yeyo-memory/local-ai"
APP_SUPPORT_DIR="$HOME/Library/Application Support/YeyoAutomation"
LOG_DIR="$APP_SUPPORT_DIR/logs"
LOG_FILE="$LOG_DIR/ai-stack-watchdog.log"
LOCK_DIR="$APP_SUPPORT_DIR/watchdog.lock"
GATEWAY_PLIST="$HOME/Library/LaunchAgents/com.carlosdiaz.claude-local-gateway.plist"

mkdir -p "$LOG_DIR"

log() {
  printf '%s %s\n' "$(date '+%F %T')" "$1" >> "$LOG_FILE"
}

cleanup() {
  rmdir "$LOCK_DIR" >/dev/null 2>&1 || true
}

if ! mkdir "$LOCK_DIR" >/dev/null 2>&1; then
  exit 0
fi
trap cleanup EXIT

check_url() {
  local url="$1"
  curl -fsS --max-time 5 "$url" >/dev/null 2>&1
}

applescript_quote() {
  local text="$1"
  text="${text//\\/\\\\}"
  text="${text//\"/\\\"}"
  printf '"%s"' "$text"
}

discover_manager_script() {
  if [[ -n "${GATEWAY_MANAGER_PATH:-}" ]] && [[ -x "${GATEWAY_MANAGER_PATH:-}" ]]; then
    printf '%s\n' "$GATEWAY_MANAGER_PATH"
    return 0
  fi

  if [[ -f "$GATEWAY_PLIST" ]]; then
    local gateway_py
    gateway_py="$(plutil -extract ProgramArguments.1 raw -o - "$GATEWAY_PLIST" 2>/dev/null || true)"
    if [[ -n "$gateway_py" ]]; then
      local candidate
      candidate="$(cd "$(dirname "$gateway_py")" && pwd)/manage-ai-stack.sh"
      if [[ -x "$candidate" ]]; then
        printf '%s\n' "$candidate"
        return 0
      fi
    fi
  fi

  return 1
}

ensure_ai_stack() {
  local manager_script
  if ! manager_script="$(discover_manager_script)"; then
    log "watchdog: no se pudo localizar manage-ai-stack.sh"
    return 1
  fi

  if check_url "http://127.0.0.1:11434/api/tags" \
    && check_url "http://127.0.0.1:8080/v1/models" \
    && check_url "http://127.0.0.1:8318/healthz"; then
    return 0
  fi

  log "watchdog: AI stack no disponible; intentando start"
  if "$manager_script" start >> "$LOG_FILE" 2>&1; then
    sleep 5
  else
    log "watchdog: start falló; intentando restart"
    "$manager_script" restart >> "$LOG_FILE" 2>&1 || true
    sleep 8
  fi

  if check_url "http://127.0.0.1:11434/api/tags" \
    && check_url "http://127.0.0.1:8080/v1/models" \
    && check_url "http://127.0.0.1:8318/healthz"; then
    log "watchdog: AI stack recuperado"
    return 0
  fi

  log "watchdog: AI stack sigue caído tras reintento"
  return 1
}

ensure_supervisor() {
  if pgrep -af 'supervise_local_ai_briefs\.sh' >/dev/null 2>&1; then
    return 0
  fi

  log "watchdog: supervisor no activo; relanzando en Terminal"
  local command
  command="cd \"$ROOT_DIR\" && rm -f .yeyo-memory/local-ai/run.lock .yeyo-memory/local-ai/supervisor.pid && YEYO_ROOT_DIR=\"$ROOT_DIR\" zsh \"$ROOT_DIR/.yeyo-memory/tools/supervise_local_ai_briefs.sh\""
  osascript \
    -e 'tell application "Terminal" to activate' \
    -e "tell application \"Terminal\" to do script $(applescript_quote "$command")" \
    >> "$LOG_FILE" 2>&1 || log "watchdog: no se pudo relanzar el supervisor por Terminal"
}

ensure_ai_stack || true
ensure_supervisor || true
