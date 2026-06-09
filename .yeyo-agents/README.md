# Gestión Documental multiagente

Este directorio contiene una primera implementación de sistema multiagente para trabajar en remoto sobre la memoria documental de Yeyo.

La idea operativa es sencilla:

- Los usuarios acceden por interfaz web o API.
- Los usuarios pueden buscar en lectura sobre la memoria local.
- Las peticiones complejas entran en una cola.
- El agente custodio procesa la cola de forma secuencial.
- La base documental `.yeyo-memory/sqlite/yeyo-memory.sqlite` se abre en solo lectura.
- La escritura operativa vive en `.yeyo-agents/data/agents.sqlite`: usuarios, cola y auditoría.

## Estructura

- `app/main.py`: API FastAPI.
- `app/retrieval.py`: búsqueda local en SQLite FTS.
- `app/custodian.py`: cola y ejecución del agente custodio.
- `app/llm_google.py`: integración opcional con Gemini.
- `app/static/`: interfaz web.
- `scripts/create_user.py`: crea tokens de acceso.
- `scripts/run_custodian.py`: worker del agente custodio.
- `config/example.env`: variables de entorno.
- `systemd/`: unidades de despliegue en Linux.

## Roles

- `viewer`: consulta y crea peticiones.
- `curator`: puede ejecutar el custodio manualmente.
- `admin`: crea usuarios y administra.

## Arranque local

Desde la raíz del repositorio documental:

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r .yeyo-agents/requirements.txt
.venv/bin/python .yeyo-agents/scripts/create_user.py --name "Carlos" --email "carlos@example.com" --role admin
.venv/bin/uvicorn app.main:app --app-dir .yeyo-agents --host 127.0.0.1 --port 8080
```

Usar Python 3.11 o 3.12. En macOS con Python 3.14 algunas dependencias nativas de Pydantic todavía pueden fallar.

Abrir:

```text
http://127.0.0.1:8080
```

El token generado se pega en la interfaz web.

Si existe `.yeyo-agents/config/local.env`, se puede arrancar cargando las variables locales:

```bash
set -a
. .yeyo-agents/config/local.env
set +a
.venv/bin/uvicorn app.main:app --app-dir .yeyo-agents --host 127.0.0.1 --port 8080
```

Para procesar la cola automáticamente:

```bash
.venv/bin/python .yeyo-agents/scripts/run_custodian.py
```

## Despliegue Ubuntu automatizado

Desde la raíz del repositorio en Ubuntu:

```bash
bash .yeyo-agents/scripts/deploy_ubuntu.sh --host 0.0.0.0 --port 8081
```

El script comprueba prerrequisitos del sistema, descarga objetos LFS, crea `.venv`, instala dependencias Python, actualiza `.yeyo-agents/config/local.env`, valida la base SQLite y prepara la base operativa de agentes. No ejecuta `apt-get`; instala antes `git`, `git-lfs`, `sqlite3`, `python3-venv` y, si quieres OCR local, `poppler-utils` y `tesseract-ocr`.

Para instalarlo como servicios systemd:

```bash
sudo bash .yeyo-agents/scripts/deploy_ubuntu.sh --root /home/ubuntu/incegex/proyecto-solana-tes-yeyo --env-file /home/ubuntu/incegex/proyecto-solana-tes-yeyo/.yeyo-agents/config/local.env --host 0.0.0.0 --port 8081 --systemd --user ubuntu
```

Si el proyecto está en `/home/ubuntu`, el servicio debe ejecutarse como `ubuntu` o moverse a una ruta de servicio como `/srv/yeyo`. Si se ejecuta como `yeyo` desde `/home/ubuntu`, systemd puede fallar con `status=200/CHDIR`.

Variables útiles:

```bash
YEYO_ADMIN_TOKEN=token-seguro GEMINI_API_KEY=... bash .yeyo-agents/scripts/deploy_ubuntu.sh --host 0.0.0.0 --port 8081
```

Si `GEMINI_API_KEY` se deja vacío, el sistema funciona en modo extractivo local.

## Uso sin IA externa

Si `GEMINI_API_KEY` no está configurada, el sistema no llama a ningún backend externo. En ese modo:

- busca fragmentos localmente,
- muestra evidencias,
- devuelve una respuesta extractiva,
- no envía contenido documental fuera del servidor.

Este es el modo recomendado para validar el piloto.

## Uso con Google Gemini

Si se configura `GEMINI_API_KEY`, el custodio:

1. busca localmente los fragmentos relevantes,
2. construye un contexto reducido,
3. envía solo ese contexto al modelo,
4. devuelve respuesta con fuentes.

Variables:

```bash
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-3.5-flash
```

No se suben documentos completos salvo que alguien cambie deliberadamente el código para hacerlo.

## Despliegue Linux recomendado

1. Crear usuario del sistema:

```bash
sudo useradd --system --create-home --shell /usr/sbin/nologin yeyo
```

2. Copiar la carpeta documental a `/srv/yeyo`.

3. Crear entorno:

```bash
cd /srv/yeyo
python3.12 -m venv .venv
.venv/bin/pip install -r .yeyo-agents/requirements.txt
```

4. Crear `/etc/yeyo-agents.env` a partir de `config/example.env`.

5. Crear usuarios:

```bash
/srv/yeyo/.venv/bin/python /srv/yeyo/.yeyo-agents/scripts/create_user.py --name "Sergio" --email "sergio.luengo@ingecex.es" --role viewer
```

6. Instalar servicios:

```bash
sudo cp /srv/yeyo/.yeyo-agents/systemd/yeyo-agents.service /etc/systemd/system/
sudo cp /srv/yeyo/.yeyo-agents/systemd/yeyo-custodian.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now yeyo-agents yeyo-custodian
```

7. Publicar con Nginx/Caddy detrás de HTTPS o usar VPN.

Recomendación de seguridad: exponerlo solo por VPN o detrás de autenticación corporativa. Los tokens de la app son suficientes para un piloto, pero para producción conviene añadir SSO, logs centralizados y copias de seguridad.

Ejemplo Caddy:

```text
yeyo.tudominio.es {
    reverse_proxy 127.0.0.1:8080
}
```

Ejemplo Nginx:

```nginx
server {
    listen 443 ssl http2;
    server_name yeyo.tudominio.es;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## API mínima

- `GET /api/stats`
- `POST /api/search/chunks`
- `POST /api/search/documents`
- `POST /api/requests`
- `GET /api/requests`
- `POST /api/custodian/run-next`
- `POST /api/admin/users`

Todas salvo `/` y `/api/health` requieren:

```text
Authorization: Bearer <token>
```

## Próximos pasos naturales

- Añadir subida de nuevos proyectos propios como corpus de referencia.
- Separar corpus por origen: repositorio recibido, proyectos propios, nuevo proyecto.
- Añadir embeddings locales con `sentence-transformers` u Ollama para búsqueda semántica real.
- Añadir comparador por documento objetivo: memoria, anejo, plano, pliego o presupuesto.
- Añadir aprobaciones del custodio para cambios persistentes de clasificación.
