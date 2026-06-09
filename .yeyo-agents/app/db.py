from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .settings import AGENT_DB, DOCUMENT_DB


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def document_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{DOCUMENT_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def validate_document_db() -> None:
    if not DOCUMENT_DB.exists():
        raise FileNotFoundError(f"No existe la base documental: {DOCUMENT_DB}")
    header = DOCUMENT_DB.read_bytes()[:64]
    if header.startswith(b"version https://git-lfs.github.com/spec"):
        raise RuntimeError(
            f"La base documental parece un puntero de Git LFS, no una SQLite real: {DOCUMENT_DB}. "
            "Ejecuta `git lfs pull` en el servidor."
        )
    if not header.startswith(b"SQLite format 3\x00"):
        raise RuntimeError(f"La base documental no tiene cabecera SQLite valida: {DOCUMENT_DB}")
    try:
        with document_conn() as conn:
            integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
            if integrity != "ok":
                raise RuntimeError(f"PRAGMA integrity_check devolvio: {integrity}")
            required = {"documents", "chunks", "chunks_fts"}
            rows = conn.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'virtual table')").fetchall()
            existing = {row["name"] for row in rows}
            missing = sorted(required - existing)
            if missing:
                raise RuntimeError(f"Faltan tablas en la base documental: {', '.join(missing)}")
            conn.execute("SELECT COUNT(*) FROM documents").fetchone()
            conn.execute("SELECT COUNT(*) FROM chunks").fetchone()
    except sqlite3.DatabaseError as exc:
        raise RuntimeError(f"No se pudo validar la base documental {DOCUMENT_DB}: {exc}") from exc


def agent_conn() -> sqlite3.Connection:
    AGENT_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(AGENT_DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def new_token() -> str:
    return "yeyo_" + secrets.token_urlsafe(32)


def init_agent_db() -> None:
    with agent_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                role TEXT NOT NULL CHECK(role IN ('admin', 'curator', 'viewer')),
                token_hash TEXT NOT NULL UNIQUE,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requester_id INTEGER NOT NULL,
                kind TEXT NOT NULL,
                prompt TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('queued', 'running', 'done', 'failed', 'cancelled')),
                priority INTEGER NOT NULL DEFAULT 50,
                payload_json TEXT NOT NULL DEFAULT '{}',
                result_json TEXT,
                error TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(requester_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_id INTEGER,
                action TEXT NOT NULL,
                target_type TEXT,
                target_id TEXT,
                detail_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                FOREIGN KEY(actor_id) REFERENCES users(id)
            );

            CREATE INDEX IF NOT EXISTS idx_requests_status_priority
            ON requests(status, priority, created_at);
            """
        )
        
        # Ensure the admin user token matches YEYO_ADMIN_TOKEN from settings
        from .settings import YEYO_ADMIN_TOKEN
        digest = hash_token(YEYO_ADMIN_TOKEN)
        admin_row = conn.execute("SELECT id FROM users WHERE role = 'admin'").fetchone()
        if admin_row:
            conn.execute(
                "UPDATE users SET token_hash = ? WHERE id = ?",
                (digest, admin_row["id"]),
            )
        else:
            conn.execute(
                """
                INSERT INTO users (name, email, role, token_hash, active, created_at)
                VALUES (?, ?, ?, ?, 1, ?)
                """,
                ("Admin por Defecto", "admin@yeyo.local", "admin", digest, utcnow()),
            )


def create_user(name: str, email: str, role: str) -> dict[str, str]:
    token = new_token()
    with agent_conn() as conn:
        conn.execute(
            """
            INSERT INTO users (name, email, role, token_hash, active, created_at)
            VALUES (?, ?, ?, ?, 1, ?)
            """,
            (name, email, role, hash_token(token), utcnow()),
        )
    return {"name": name, "email": email, "role": role, "token": token}


def find_user_by_token(token: str) -> dict[str, Any] | None:
    token_digest = hash_token(token)
    with agent_conn() as conn:
        rows = conn.execute(
            "SELECT id, name, email, role, active, token_hash FROM users WHERE active = 1"
        ).fetchall()
    for row in rows:
        if hmac.compare_digest(row["token_hash"], token_digest):
            data = dict(row)
            data.pop("token_hash", None)
            return data
    return None


def audit(actor_id: int | None, action: str, target_type: str | None = None, target_id: str | None = None, detail_json: str = "{}") -> None:
    with agent_conn() as conn:
        conn.execute(
            """
            INSERT INTO audit_log (actor_id, action, target_type, target_id, detail_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (actor_id, action, target_type, target_id, detail_json, utcnow()),
        )


def ensure_paths() -> None:
    validate_document_db()
    Path(AGENT_DB).parent.mkdir(parents=True, exist_ok=True)
