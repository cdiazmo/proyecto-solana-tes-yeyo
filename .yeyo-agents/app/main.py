from __future__ import annotations

import threading
import time
import urllib.parse
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .custodian import enqueue_request, get_request, list_requests, run_next_request
from .db import create_user, ensure_paths, find_user_by_token, init_agent_db, agent_conn, document_conn, audit
from .retrieval import inventory_stats, search_chunks, search_documents
from .settings import APP_NAME, STATIC_DIR, ROOT, YEYO_ADMIN_TOKEN


class QueryIn(BaseModel):
    query: str = Field(min_length=2)
    limit: int = Field(default=12, ge=1, le=50)


class RequestIn(BaseModel):
    kind: str = Field(default="query")
    prompt: str = Field(min_length=2)
    priority: int = Field(default=50, ge=1, le=100)
    payload: dict[str, Any] = Field(default_factory=dict)


class UserIn(BaseModel):
    name: str
    email: str = ""
    role: str = Field(pattern="^(admin|curator|viewer)$")


app = FastAPI(title=APP_NAME)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def custodian_background_worker() -> None:
    while True:
        try:
            run_next_request()
        except Exception as e:
            print(f"[Custodian Worker Thread Error] {e}", flush=True)
        time.sleep(2.0)


@app.on_event("startup")
def startup() -> None:
    ensure_paths()
    init_agent_db()
    worker_thread = threading.Thread(target=custodian_background_worker, daemon=True)
    worker_thread.start()


def current_user(authorization: Annotated[str | None, Header()] = None) -> dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Falta Authorization: Bearer <token>")
    token = authorization.split(" ", 1)[1].strip()
    user = find_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Token inválido")
    return user


def require_role(*roles: str):
    def dependency(user: Annotated[dict[str, Any], Depends(current_user)]) -> dict[str, Any]:
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        return user

    return dependency


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": APP_NAME}


@app.get("/api/config")
def get_config() -> dict[str, str]:
    return {"token": YEYO_ADMIN_TOKEN}


@app.get("/api/stats")
def stats(user: Annotated[dict[str, Any], Depends(current_user)]) -> dict[str, Any]:
    return inventory_stats()


@app.post("/api/search/chunks")
def api_search_chunks(data: QueryIn, user: Annotated[dict[str, Any], Depends(current_user)]) -> dict[str, Any]:
    return {"results": search_chunks(data.query, data.limit)}


@app.post("/api/search/documents")
def api_search_documents(data: QueryIn, user: Annotated[dict[str, Any], Depends(current_user)]) -> dict[str, Any]:
    return {"results": search_documents(data.query, data.limit)}


@app.post("/api/requests")
def api_create_request(
    data: RequestIn,
    background_tasks: BackgroundTasks,
    user: Annotated[dict[str, Any], Depends(current_user)]
) -> dict[str, Any]:
    request_id = enqueue_request(user["id"], data.kind, data.prompt, data.payload, data.priority)
    background_tasks.add_task(run_next_request)
    return {"id": request_id, "status": "queued"}


@app.get("/api/requests")
def api_list_requests(user: Annotated[dict[str, Any], Depends(current_user)]) -> dict[str, Any]:
    return {"requests": list_requests()}


@app.get("/api/requests/{request_id}")
def api_get_request(request_id: int, user: Annotated[dict[str, Any], Depends(current_user)]) -> dict[str, Any]:
    request = get_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Petición no encontrada")
    return request


@app.post("/api/custodian/run-next")
def api_run_next(user: Annotated[dict[str, Any], Depends(require_role("admin", "curator"))]) -> dict[str, Any]:
    result = run_next_request(custodian_id=user["id"])
    return {"request": result}


@app.post("/api/admin/users")
def api_create_user(data: UserIn, user: Annotated[dict[str, Any], Depends(require_role("admin"))]) -> dict[str, str]:
    return create_user(data.name, data.email, data.role)


@app.get("/api/files")
def api_list_files(
    user: Annotated[dict[str, Any], Depends(current_user)],
    q: str = "",
    limit: int = 20,
    offset: int = 0
) -> dict[str, Any]:
    with document_conn() as conn:
        where_clause = ""
        params = []
        if q:
            where_clause = "WHERE path LIKE ? OR title LIKE ? OR doc_code LIKE ?"
            like_val = f"%{q}%"
            params.extend([like_val, like_val, like_val])
            
        count_query = f"SELECT COUNT(*) FROM documents {where_clause}"
        total_files = conn.execute(count_query, params).fetchone()[0]
        
        select_query = f"""
            SELECT id, path, top_dir, ext, size_human, title, doc_code, revision,
                   status, text_chars, chunks, token_estimate, card_path, extracted_path
            FROM documents
            {where_clause}
            ORDER BY path ASC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        rows = conn.execute(select_query, params).fetchall()
        
    return {
        "files": [dict(row) for row in rows],
        "total": total_files,
        "limit": limit,
        "offset": offset
    }


@app.get("/api/files/download")
def download_file(path: str, user: Annotated[dict[str, Any], Depends(current_user)]) -> FileResponse:
    sanitized_path = path.replace("\\", "/").lstrip("/")
    safe_path = (ROOT / sanitized_path).resolve()
    
    try:
        safe_path.relative_to(ROOT.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Acceso denegado")
        
    if not safe_path.exists():
        raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {path}")
    if not safe_path.is_file():
        raise HTTPException(status_code=400, detail="La ruta especificada no es un archivo")
        
    filename = safe_path.name
    encoded_filename = urllib.parse.quote(filename)
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
    }
    return FileResponse(safe_path, headers=headers)


@app.post("/api/requests/clear")
def api_clear_requests(user: Annotated[dict[str, Any], Depends(require_role("admin"))]) -> dict[str, str]:
    with agent_conn() as conn:
        conn.execute("DELETE FROM requests")
    audit(user["id"], "requests.clear")
    return {"status": "ok", "message": "Historial de peticiones limpiado"}
