#!/usr/bin/env bash
set -euo pipefail

APP_USER_WAS_SET=0
if [[ -n "${APP_USER:-}" ]]; then
  APP_USER_WAS_SET=1
fi
APP_USER="${APP_USER:-yeyo}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8081}"
INSTALL_SYSTEMD="${INSTALL_SYSTEMD:-0}"
INSTALL_OCR="${INSTALL_OCR:-1}"
PROJECT_ROOT="${PROJECT_ROOT:-}"
ENV_FILE="${ENV_FILE:-}"
PYTHON_BIN="${PYTHON_BIN:-}"

usage() {
  cat <<'EOF'
Uso:
  bash .yeyo-agents/scripts/deploy_ubuntu.sh [opciones]

Opciones:
  --root PATH          Ruta del proyecto. Por defecto: directorio actual.
  --host HOST          Host de Uvicorn. Por defecto: 127.0.0.1.
  --port PORT          Puerto de Uvicorn. Por defecto: 8081.
  --user USER          Usuario systemd. Por defecto: yeyo.
  --env-file PATH      Fichero de entorno. Por defecto: .yeyo-agents/config/local.env.
  --systemd            Instala y arranca servicios systemd.
  --no-ocr             No comprueba herramientas OCR locales.
  --python PATH        Python concreto a usar.
  -h, --help           Muestra esta ayuda.

Ejemplos:
  bash .yeyo-agents/scripts/deploy_ubuntu.sh --port 8081
  sudo bash .yeyo-agents/scripts/deploy_ubuntu.sh --root /srv/yeyo --host 0.0.0.0 --port 8081 --systemd

Variables opcionales:
  YEYO_ADMIN_TOKEN, GEMINI_API_KEY, GEMINI_MODEL, YEYO_MAX_CONTEXT_CHUNKS, YEYO_MAX_CONTEXT_CHARS
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --root)
      PROJECT_ROOT="$2"
      shift 2
      ;;
    --host)
      HOST="$2"
      shift 2
      ;;
    --port)
      PORT="$2"
      shift 2
      ;;
    --user)
      APP_USER="$2"
      shift 2
      ;;
    --env-file)
      ENV_FILE="$2"
      shift 2
      ;;
    --systemd)
      INSTALL_SYSTEMD="1"
      shift
      ;;
    --no-ocr)
      INSTALL_OCR="0"
      shift
      ;;
    --python)
      PYTHON_BIN="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Opcion no reconocida: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ -z "$PROJECT_ROOT" ]]; then
  PROJECT_ROOT="$(pwd)"
fi
PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd)"

cd "$PROJECT_ROOT"

if [[ -z "$ENV_FILE" ]]; then
  ENV_FILE="$PROJECT_ROOT/.yeyo-agents/config/local.env"
elif [[ "$ENV_FILE" != /* ]]; then
  ENV_FILE="$PROJECT_ROOT/$ENV_FILE"
fi

if [[ ! -d ".yeyo-agents" || ! -f ".yeyo-agents/requirements.txt" ]]; then
  echo "ERROR: $PROJECT_ROOT no parece ser la raiz del proyecto Yeyo." >&2
  exit 1
fi

SUDO=""
if [[ "$INSTALL_SYSTEMD" == "1" && "${EUID:-$(id -u)}" -ne 0 ]]; then
  if command -v sudo >/dev/null 2>&1; then
    SUDO="sudo"
  else
    echo "ERROR: se necesita root o sudo para instalar servicios systemd." >&2
    exit 1
  fi
fi

echo "==> Proyecto: $PROJECT_ROOT"
echo "==> Host/Puerto: $HOST:$PORT"
echo "==> Env file: $ENV_FILE"

require_cmd() {
  local name="$1"
  local hint="$2"
  if ! command -v "$name" >/dev/null 2>&1; then
    echo "ERROR: falta '$name'. $hint" >&2
    exit 1
  fi
}

echo "==> Comprobando prerrequisitos del sistema"
require_cmd git "Instala git antes de ejecutar este script."
require_cmd sqlite3 "Instala sqlite3 antes de ejecutar este script."
if ! git lfs version >/dev/null 2>&1; then
  echo "ERROR: falta Git LFS. Instala git-lfs antes de ejecutar este script." >&2
  exit 1
fi
if [[ "$INSTALL_OCR" == "1" ]]; then
  require_cmd pdftoppm "Instala poppler-utils o ejecuta con --no-ocr."
  require_cmd tesseract "Instala tesseract-ocr o ejecuta con --no-ocr."
fi

echo "==> Activando Git LFS y descargando objetos grandes"
git lfs install --local || git lfs install
git lfs pull

if [[ -z "$PYTHON_BIN" ]]; then
  if command -v python3.12 >/dev/null 2>&1; then
    PYTHON_BIN="python3.12"
  elif command -v python3.11 >/dev/null 2>&1; then
    PYTHON_BIN="python3.11"
  else
    PYTHON_BIN="python3"
  fi
fi

echo "==> Usando Python: $($PYTHON_BIN --version)"
if [[ ! -d ".venv" ]]; then
  "$PYTHON_BIN" -m venv .venv
fi

echo "==> Instalando dependencias Python"
.venv/bin/python -m pip install --upgrade pip wheel
.venv/bin/pip install -r .yeyo-agents/requirements.txt

shell_quote() {
  local value="${1:-}"
  printf "'%s'" "${value//\'/\'\\\'\'}"
}

echo "==> Creando fichero de entorno"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  . "$ENV_FILE"
  set +a
fi
admin_token="${YEYO_ADMIN_TOKEN:-yeyo_admin_token}"
gemini_key="${GEMINI_API_KEY:-}"
gemini_model="${GEMINI_MODEL:-gemini-3.5-flash}"
max_chunks="${YEYO_MAX_CONTEXT_CHUNKS:-8}"
max_chars="${YEYO_MAX_CONTEXT_CHARS:-14000}"

install_dir="$(dirname "$ENV_FILE")"
if [[ "$install_dir" == "$PROJECT_ROOT"* && "${EUID:-$(id -u)}" -ne 0 ]]; then
  install -d -m 0755 "$install_dir"
else
  $SUDO install -d -m 0755 "$install_dir"
fi
tmp_env="$(mktemp)"
cat > "$tmp_env" <<EOF
YEYO_ROOT=$(shell_quote "$PROJECT_ROOT")
YEYO_DOCUMENT_DB=$(shell_quote "$PROJECT_ROOT/.yeyo-memory/sqlite/yeyo-memory.sqlite")
YEYO_AGENT_DB=$(shell_quote "$PROJECT_ROOT/.yeyo-agents/data/agents.sqlite")
YEYO_APP_NAME=$(shell_quote "${YEYO_APP_NAME:-Gestión Documental}")
YEYO_MAX_CONTEXT_CHUNKS=$max_chunks
YEYO_MAX_CONTEXT_CHARS=$max_chars
GEMINI_API_KEY=$(shell_quote "$gemini_key")
GEMINI_MODEL=$(shell_quote "$gemini_model")
YEYO_ADMIN_TOKEN=$(shell_quote "$admin_token")
EOF
if [[ "$install_dir" == "$PROJECT_ROOT"* && "${EUID:-$(id -u)}" -ne 0 ]]; then
  install -m 0600 "$tmp_env" "$ENV_FILE"
else
  $SUDO install -m 0600 "$tmp_env" "$ENV_FILE"
fi
rm -f "$tmp_env"

echo "==> Validando base documental"
.venv/bin/python - <<'PY'
from pathlib import Path
import os
import sqlite3
db = Path(os.environ.get("YEYO_DOCUMENT_DB", ".yeyo-memory/sqlite/yeyo-memory.sqlite"))
if not db.is_absolute():
    db = Path.cwd() / db
if not db.exists():
    raise SystemExit(f"ERROR: no existe la base documental: {db}")
head = db.read_bytes()[:80]
if head.startswith(b"version https://git-lfs.github.com/spec"):
    raise SystemExit(f"ERROR: {db} es un puntero Git LFS. Ejecuta git lfs pull.")
if not head.startswith(b"SQLite format 3\x00"):
    raise SystemExit(f"ERROR: {db} no parece SQLite.")
conn = sqlite3.connect(db)
print("integrity", conn.execute("PRAGMA integrity_check").fetchone()[0])
print("documents", conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0])
print("chunks", conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])
conn.close()
PY

echo "==> Inicializando base operativa de agentes"
set -a
# shellcheck disable=SC1090
. "$ENV_FILE"
set +a
.venv/bin/python - <<'PY'
import sys
sys.path.insert(0, ".yeyo-agents")
from app.db import ensure_paths, init_agent_db
ensure_paths()
init_agent_db()
print("agents db ok")
PY

if [[ "$INSTALL_SYSTEMD" == "1" ]]; then
  echo "==> Instalando servicios systemd"
  if [[ "$APP_USER_WAS_SET" == "0" && -n "${SUDO_USER:-}" && "${SUDO_USER:-}" != "root" && "$PROJECT_ROOT" == "/home/$SUDO_USER/"* ]]; then
    APP_USER="$SUDO_USER"
    echo "==> Proyecto bajo /home/$SUDO_USER; usando usuario systemd: $APP_USER"
  fi
  if ! id "$APP_USER" >/dev/null 2>&1; then
    $SUDO useradd --system --create-home --shell /usr/sbin/nologin "$APP_USER"
  fi
  $SUDO chown -R "$APP_USER:$APP_USER" "$PROJECT_ROOT/.yeyo-agents/data" "$PROJECT_ROOT/.venv"
  if ! $SUDO -u "$APP_USER" test -x "$PROJECT_ROOT" >/dev/null 2>&1; then
    cat >&2 <<EOF
ERROR: el usuario systemd '$APP_USER' no puede acceder a:
  $PROJECT_ROOT

Esto provoca systemd status=200/CHDIR.

Soluciones:
  1. Reejecuta con un usuario que pueda entrar en esa ruta:
     sudo bash .yeyo-agents/scripts/deploy_ubuntu.sh --root $PROJECT_ROOT --env-file $ENV_FILE --host $HOST --port $PORT --systemd --user ${SUDO_USER:-ubuntu}

  2. O mueve el proyecto a una ruta de servicio como /srv/yeyo y usa --user yeyo.
EOF
    exit 1
  fi

  api_service="$(mktemp)"
  cat > "$api_service" <<EOF
[Unit]
Description=Yeyo Gestion Documental API
After=network.target

[Service]
Type=simple
WorkingDirectory=$PROJECT_ROOT
EnvironmentFile=$ENV_FILE
ExecStart=$PROJECT_ROOT/.venv/bin/uvicorn app.main:app --app-dir $PROJECT_ROOT/.yeyo-agents --host $HOST --port $PORT
Restart=always
RestartSec=5
User=$APP_USER
Group=$APP_USER

[Install]
WantedBy=multi-user.target
EOF

  custodian_service="$(mktemp)"
  cat > "$custodian_service" <<EOF
[Unit]
Description=Yeyo Gestion Documental Custodian Worker
After=network.target yeyo-agents.service

[Service]
Type=simple
WorkingDirectory=$PROJECT_ROOT
EnvironmentFile=$ENV_FILE
ExecStart=$PROJECT_ROOT/.venv/bin/python $PROJECT_ROOT/.yeyo-agents/scripts/run_custodian.py
Restart=always
RestartSec=5
User=$APP_USER
Group=$APP_USER

[Install]
WantedBy=multi-user.target
EOF

  $SUDO install -m 0644 "$api_service" /etc/systemd/system/yeyo-agents.service
  $SUDO install -m 0644 "$custodian_service" /etc/systemd/system/yeyo-custodian.service
  rm -f "$api_service" "$custodian_service"
  $SUDO systemctl daemon-reload
  $SUDO systemctl enable --now yeyo-agents yeyo-custodian
  $SUDO systemctl --no-pager --full status yeyo-agents || true
else
  cat <<EOF

==> Despliegue preparado.

Para lanzar la API manualmente:
  cd $PROJECT_ROOT
  set -a
  . $ENV_FILE
  set +a
  .venv/bin/uvicorn app.main:app --app-dir .yeyo-agents --host $HOST --port $PORT

Para lanzar el custodio en otra terminal:
  cd $PROJECT_ROOT
  set -a
  . $ENV_FILE
  set +a
  .venv/bin/python .yeyo-agents/scripts/run_custodian.py

URL:
  http://$HOST:$PORT

Token admin inicial:
  $admin_token

Para instalar servicios systemd:
  sudo bash .yeyo-agents/scripts/deploy_ubuntu.sh --root $PROJECT_ROOT --env-file $ENV_FILE --host $HOST --port $PORT --systemd
EOF
fi
