#!/bin/bash
# =============================================================================
# knowledge-base-rag — Script de instalación para servidor Linux
# Ejecutar como usuario normal con sudo disponible (NO como root)
# Uso: bash setup-server.sh
# =============================================================================

set -euo pipefail

# ─────────────────────────────────────────────
# CONFIGURACIÓN — edita estos valores antes de ejecutar
# ─────────────────────────────────────────────
GEMINI_API_KEY=""                   # ← OBLIGATORIO: tu clave de Gemini
RAG_API_KEY="$(openssl rand -hex 16)"  # Se genera automáticamente (cámbialo si quieres)
INSTALL_DIR="/srv/knowledge-base-rag"
DOCS_DIR="/srv/knowledge/docs"
API_PORT=3800

# ─────────────────────────────────────────────
# Colores
# ─────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC}   $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
error()   { echo -e "${RED}[ERR]${NC}  $*"; exit 1; }

# ─────────────────────────────────────────────
# Validaciones previas
# ─────────────────────────────────────────────
[ "$EUID" -eq 0 ] && error "No ejecutes este script como root. Usa un usuario normal con sudo."
[[ -z "$GEMINI_API_KEY" ]] && error "Debes definir GEMINI_API_KEY al principio del script."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_SOURCE="$SCRIPT_DIR"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  knowledge-base-rag — Instalación en servidor"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
info "Directorio de instalación: $INSTALL_DIR"
info "Directorio de documentos:  $DOCS_DIR"
info "Puerto API:                $API_PORT"
echo ""

# ─────────────────────────────────────────────
# PASO 1 — Actualizar sistema
# ─────────────────────────────────────────────
info "PASO 1/8 — Actualizando paquetes del sistema..."
sudo apt-get update -qq
sudo apt-get install -y -qq curl ca-certificates gnupg openssl
success "Sistema actualizado."

# ─────────────────────────────────────────────
# PASO 2 — Instalar Node.js 22
# ─────────────────────────────────────────────
info "PASO 2/8 — Instalando Node.js 22..."
if node --version 2>/dev/null | grep -q "^v22"; then
    success "Node.js 22 ya está instalado: $(node --version)"
else
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - > /dev/null 2>&1
    sudo apt-get install -y -qq nodejs
    success "Node.js instalado: $(node --version)"
fi

# ─────────────────────────────────────────────
# PASO 3 — Instalar Docker
# ─────────────────────────────────────────────
info "PASO 3/8 — Instalando Docker..."
if docker --version > /dev/null 2>&1; then
    success "Docker ya está instalado: $(docker --version)"
else
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
        | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg > /dev/null 2>&1
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
        https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
        | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update -qq
    sudo apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
    success "Docker instalado: $(docker --version)"
fi

# Añadir usuario al grupo docker
if ! groups "$USER" | grep -q docker; then
    sudo usermod -aG docker "$USER"
    warn "Usuario añadido al grupo docker. Los cambios de grupo aplican en el siguiente login."
    warn "Si docker falla por permisos, ejecuta: newgrp docker"
fi

# ─────────────────────────────────────────────
# PASO 4 — Copiar proyecto al servidor
# ─────────────────────────────────────────────
info "PASO 4/8 — Copiando proyecto a $INSTALL_DIR..."
sudo mkdir -p "$INSTALL_DIR"
sudo chown "$USER:$USER" "$INSTALL_DIR"
rsync -a --exclude='node_modules' --exclude='.env' --exclude='qdrant_storage' \
    "$PROJECT_SOURCE/" "$INSTALL_DIR/"
success "Proyecto copiado a $INSTALL_DIR."

# ─────────────────────────────────────────────
# PASO 5 — Crear carpeta de documentos y .env
# ─────────────────────────────────────────────
info "PASO 5/8 — Configurando entorno..."

sudo mkdir -p "$DOCS_DIR"
sudo chown "$USER:$USER" "$DOCS_DIR"
success "Carpeta de documentos lista: $DOCS_DIR"

ENV_FILE="$INSTALL_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    warn ".env ya existe, no se sobreescribe. Revísalo manualmente en $ENV_FILE"
else
    cat > "$ENV_FILE" <<EOF
GEMINI_API_KEY=${GEMINI_API_KEY}
GEMINI_MODEL=gemini-3.1-flash-lite
GEMINI_EMBEDDING_MODEL=gemini-embedding-001

QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=knowledge_base

KNOWLEDGE_DOCS_PATH=${DOCS_DIR}

TOP_K=8
CHUNK_SIZE=1200
CHUNK_OVERLAP=200
MAX_DOC_SIZE_MB=50

API_PORT=${API_PORT}
RAG_API_KEY=${RAG_API_KEY}
EOF
    chmod 600 "$ENV_FILE"
    success ".env creado en $ENV_FILE"
fi

# ─────────────────────────────────────────────
# PASO 6 — Instalar dependencias npm
# ─────────────────────────────────────────────
info "PASO 6/8 — Instalando dependencias npm..."
cd "$INSTALL_DIR"
npm install --silent
success "Dependencias instaladas."

# ─────────────────────────────────────────────
# PASO 7 — Levantar Qdrant con Docker
# ─────────────────────────────────────────────
info "PASO 7/8 — Arrancando Qdrant con Docker..."
cd "$INSTALL_DIR"

# Necesitamos docker sin sudo (o con newgrp). Usamos sg docker si es necesario.
if docker compose ps 2>/dev/null | grep -q "qdrant"; then
    success "Qdrant ya está corriendo."
else
    sg docker -c "docker compose up -d" 2>/dev/null || docker compose up -d
    sleep 3

    # Esperar a que Qdrant responda
    RETRIES=10
    for i in $(seq 1 $RETRIES); do
        if curl -sf http://localhost:6333/healthz > /dev/null; then
            success "Qdrant está listo en http://localhost:6333"
            break
        fi
        if [ "$i" -eq "$RETRIES" ]; then
            warn "Qdrant no respondió en tiempo. Comprueba con: docker compose ps"
        fi
        sleep 2
    done
fi

# ─────────────────────────────────────────────
# PASO 8 — Crear servicio systemd
# ─────────────────────────────────────────────
info "PASO 8/8 — Creando servicio systemd..."

# Ruta absoluta a tsx
TSX_BIN="$(cd "$INSTALL_DIR" && node -e "const r=require.resolve('tsx/package.json'); console.log(r.replace('/package.json','/dist/cli.mjs'))" 2>/dev/null || echo "$INSTALL_DIR/node_modules/.bin/tsx")"
NODE_BIN="$(which node)"

sudo tee /etc/systemd/system/knowledge-rag.service > /dev/null <<EOF
[Unit]
Description=knowledge-base-rag API Server
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=${USER}
WorkingDirectory=${INSTALL_DIR}
ExecStart=${NODE_BIN} --import tsx/esm ${INSTALL_DIR}/src/server.ts
Restart=on-failure
RestartSec=10
EnvironmentFile=${INSTALL_DIR}/.env

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable knowledge-rag
sudo systemctl start knowledge-rag
sleep 2

if sudo systemctl is-active --quiet knowledge-rag; then
    success "Servicio knowledge-rag activo y habilitado para arranque automático."
else
    warn "El servicio no arrancó correctamente. Comprueba: sudo journalctl -u knowledge-rag -n 50"
fi

# ─────────────────────────────────────────────
# Abrir firewall si ufw está activo
# ─────────────────────────────────────────────
if sudo ufw status 2>/dev/null | grep -q "Status: active"; then
    info "Configurando firewall ufw..."
    sudo ufw allow "${API_PORT}/tcp" comment "knowledge-rag API" > /dev/null
    success "Puerto $API_PORT abierto en ufw."
fi

# ─────────────────────────────────────────────
# Resumen final
# ─────────────────────────────────────────────
SERVER_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}  ✅ Instalación completada${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Proyecto:    $INSTALL_DIR"
echo "  Documentos:  $DOCS_DIR"
echo "  API URL:     http://${SERVER_IP}:${API_PORT}"
echo ""
echo -e "${YELLOW}  API Key generada (guárdala):${NC}"
echo "  RAG_API_KEY=$RAG_API_KEY"
echo ""
echo "  ┌─ PRÓXIMOS PASOS ──────────────────────────────"
echo "  │"
echo "  │  1. Copia tus documentos al servidor:"
echo "  │     scp -r *.pdf usuario@${SERVER_IP}:${DOCS_DIR}/"
echo "  │"
echo "  │  2. Ejecuta la ingesta:"
echo "  │     cd $INSTALL_DIR && npm run ingest"
echo "  │"
echo "  │  3. Configura Moltbot con:"
echo "  │     URL:     http://${SERVER_IP}:${API_PORT}/ask"
echo "  │     Header:  x-api-key: $RAG_API_KEY"
echo "  │     Body:    { \"question\": \"{{user_message}}\" }"
echo "  │"
echo "  │  4. Prueba desde este servidor:"
echo "  │     curl -X POST http://localhost:${API_PORT}/ask \\"
echo "  │       -H 'Content-Type: application/json' \\"
echo "  │       -H 'x-api-key: ${RAG_API_KEY}' \\"
echo "  │       -d '{\"question\": \"prueba\"}'"
echo "  │"
echo "  └────────────────────────────────────────────────"
echo ""
echo "  Logs en tiempo real:"
echo "  sudo journalctl -u knowledge-rag -f"
echo ""
