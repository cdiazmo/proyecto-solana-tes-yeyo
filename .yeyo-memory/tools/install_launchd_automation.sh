#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
OUT_DIR="$ROOT_DIR/.yeyo-memory/local-ai"
LOG_DIR="$OUT_DIR/logs"
WATCHDOG_SCRIPT="$ROOT_DIR/.yeyo-memory/tools/watch_local_ai_stack.sh"
START_SCRIPT="$ROOT_DIR/.yeyo-memory/tools/start_local_ai_briefs.sh"
APP_SUPPORT_DIR="$HOME/Library/Application Support/YeyoAutomation"
APP_SUPPORT_LOG_DIR="$APP_SUPPORT_DIR/logs"
WATCHDOG_RUNNER="$APP_SUPPORT_DIR/watch_local_ai_stack.sh"
START_RUNNER="$APP_SUPPORT_DIR/start_local_ai_briefs.sh"
WATCHDOG_LABEL="com.carlosdiaz.yeyo-local-ai-watchdog"
WATCHDOG_PLIST="$HOME/Library/LaunchAgents/$WATCHDOG_LABEL.plist"
SUPERVISOR_LABEL="com.carlosdiaz.yeyo-local-ai-briefs-supervisor"
SUPERVISOR_PLIST="$HOME/Library/LaunchAgents/$SUPERVISOR_LABEL.plist"

mkdir -p "$LOG_DIR" "$APP_SUPPORT_LOG_DIR" "$HOME/Library/LaunchAgents"

chmod +x "$WATCHDOG_SCRIPT" "$START_SCRIPT"
cp "$WATCHDOG_SCRIPT" "$WATCHDOG_RUNNER"
cp "$START_SCRIPT" "$START_RUNNER"
chmod +x "$WATCHDOG_RUNNER" "$START_RUNNER"

cat > "$WATCHDOG_PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${WATCHDOG_LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string>
    <string>${WATCHDOG_RUNNER}</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>YEYO_ROOT_DIR</key>
    <string>${ROOT_DIR}</string>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
  </dict>
  <key>WorkingDirectory</key>
  <string>${APP_SUPPORT_DIR}</string>
  <key>RunAtLoad</key>
  <true/>
  <key>StartInterval</key>
  <integer>120</integer>
  <key>StandardOutPath</key>
  <string>${APP_SUPPORT_LOG_DIR}/watchdog.launchd.out.log</string>
  <key>StandardErrorPath</key>
  <string>${APP_SUPPORT_LOG_DIR}/watchdog.launchd.err.log</string>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)" "$WATCHDOG_PLIST" >/dev/null 2>&1 || true
launchctl bootout "gui/$(id -u)" "$SUPERVISOR_PLIST" >/dev/null 2>&1 || true
rm -f "$SUPERVISOR_PLIST"
launchctl bootstrap "gui/$(id -u)" "$WATCHDOG_PLIST"
launchctl kickstart -k "gui/$(id -u)/$WATCHDOG_LABEL"

echo "Instalado:"
echo "  $WATCHDOG_PLIST"
echo "Runners:"
echo "  $WATCHDOG_RUNNER"
echo "Logs:"
echo "  $APP_SUPPORT_LOG_DIR/ai-stack-watchdog.log"
echo "  $LOG_DIR/supervisor.log"
