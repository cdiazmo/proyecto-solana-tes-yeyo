#!/bin/zsh
set -euo pipefail

ROOT_DIR="${YEYO_ROOT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
APP_SUPPORT_DIR="$HOME/Library/Application Support/YeyoAutomation"
mkdir -p "$APP_SUPPORT_DIR"

if pgrep -af 'supervise_local_ai_briefs\.sh' >/dev/null 2>&1; then
  echo "Ya hay un supervisor activo"
  exit 0
fi

command="cd \"$ROOT_DIR\" && rm -f .yeyo-memory/local-ai/run.lock .yeyo-memory/local-ai/supervisor.pid && YEYO_ROOT_DIR=\"$ROOT_DIR\" zsh \"$ROOT_DIR/.yeyo-memory/tools/supervise_local_ai_briefs.sh\""
escaped="${command//\\/\\\\}"
escaped="${escaped//\"/\\\"}"

osascript \
  -e 'tell application "Terminal" to activate' \
  -e "tell application \"Terminal\" to do script \"$escaped\""

echo "Supervisor relanzado en Terminal"
