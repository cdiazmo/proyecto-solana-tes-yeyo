#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


ROOT = Path.cwd()
MEMORY_ROOT = ROOT / ".yeyo-memory"
CONFIG_PATH = MEMORY_ROOT / "config.json"
CARDS_DIR = MEMORY_ROOT / "cards"


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def chunk_text(text: str, chunk_chars: int, overlap: int) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_chars, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def init_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = db_path.with_suffix(db_path.suffix + ".rebuild-tmp")
    if tmp_path.exists():
        tmp_path.unlink()
    if db_path.exists():
        header = db_path.read_bytes()[:32]
        if not header.startswith(b"SQLite format 3\x00"):
            db_path.rename(db_path.with_suffix(db_path.suffix + ".corrupt-lfs-pointer"))
    conn = sqlite3.connect(tmp_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """
        CREATE TABLE documents (
            id TEXT PRIMARY KEY,
            path TEXT NOT NULL,
            top_dir TEXT NOT NULL,
            ext TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            size_human TEXT NOT NULL,
            mtime_iso TEXT NOT NULL,
            title TEXT,
            doc_code TEXT,
            revision TEXT,
            status TEXT NOT NULL,
            text_chars INTEGER NOT NULL,
            chunks INTEGER NOT NULL,
            token_estimate INTEGER NOT NULL,
            card_path TEXT NOT NULL,
            extracted_path TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE chunks (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            path TEXT NOT NULL,
            text TEXT NOT NULL,
            FOREIGN KEY(document_id) REFERENCES documents(id)
        )
        """
    )
    conn.execute("CREATE VIRTUAL TABLE chunks_fts USING fts5(id UNINDEXED, path UNINDEXED, text)")
    return conn


def insert_document(conn: sqlite3.Connection, card: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO documents (
            id, path, top_dir, ext, size_bytes, size_human, mtime_iso, title,
            doc_code, revision, status, text_chars, chunks, token_estimate,
            card_path, extracted_path
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            card["id"],
            card["path"],
            card["top_dir"],
            card["ext"],
            int(card.get("size_bytes") or 0),
            card.get("size_human") or "",
            card.get("mtime_iso") or "",
            card.get("title") or "",
            card.get("doc_code"),
            card.get("revision"),
            card.get("status") or "",
            int(card.get("text_chars") or 0),
            int(card.get("chunks") or 0),
            int(card.get("token_estimate") or 0),
            card.get("card_path") or "",
            card.get("extracted_path"),
        ),
    )


def insert_chunks(conn: sqlite3.Connection, card: dict[str, Any], chunks: list[str]) -> None:
    for index, chunk in enumerate(chunks):
        chunk_id = f"{card['id']}:{index:04d}"
        conn.execute(
            "INSERT INTO chunks (id, document_id, chunk_index, path, text) VALUES (?, ?, ?, ?, ?)",
            (chunk_id, card["id"], index, card["path"], chunk),
        )
        conn.execute("INSERT INTO chunks_fts (id, path, text) VALUES (?, ?, ?)", (chunk_id, card["path"], chunk))


def update_document_text_stats(conn: sqlite3.Connection, card: dict[str, Any], text_chars: int, chunks: int) -> None:
    conn.execute(
        """
        UPDATE documents
        SET text_chars = ?, chunks = ?, token_estimate = ?
        WHERE id = ?
        """,
        (text_chars, chunks, max(1, text_chars // 4) if text_chars else 0, card["id"]),
    )


def export_chunks_jsonl(conn: sqlite3.Connection, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        rows = conn.execute("SELECT id, document_id, chunk_index, path, text FROM chunks ORDER BY path, chunk_index")
        for row in rows:
            handle.write(
                json.dumps(
                    {
                        "id": row[0],
                        "document_id": row[1],
                        "chunk_index": row[2],
                        "path": row[3],
                        "text": row[4],
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )


def main() -> int:
    config = load_config()
    db_path = ROOT / config["paths"]["sqlite"]
    tmp_path = db_path.with_suffix(db_path.suffix + ".rebuild-tmp")
    conn = init_db(db_path)
    chunk_chars = int(config["chunk_chars"])
    overlap = int(config["chunk_overlap"])
    min_text = int(config["min_text_chars"])
    docs = 0
    chunk_rows = 0
    try:
        for card_path in sorted(CARDS_DIR.glob("*.json")):
            card = json.loads(card_path.read_text(encoding="utf-8"))
            insert_document(conn, card)
            extracted = card.get("extracted_path")
            if extracted:
                text_path = ROOT / extracted
                if text_path.exists():
                    text = text_path.read_text(encoding="utf-8", errors="replace")
                    chunks = chunk_text(text, chunk_chars, overlap) if len(text) >= min_text else []
                    insert_chunks(conn, card, chunks)
                    update_document_text_stats(conn, card, len(text), len(chunks))
                    chunk_rows += len(chunks)
            docs += 1
            if docs % 250 == 0:
                conn.commit()
        conn.commit()
        export_chunks_jsonl(conn, MEMORY_ROOT / "chunks" / "chunks.jsonl")
    finally:
        conn.close()
    tmp_path.replace(db_path)
    print(f"rebuilt documents={docs} chunks={chunk_rows} db={db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
