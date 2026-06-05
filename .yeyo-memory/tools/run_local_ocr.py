#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path.cwd()
MEMORY_ROOT = ROOT / ".yeyo-memory"
TOOLS_DIR = MEMORY_ROOT / "tools"
BIN_DIR = MEMORY_ROOT / "bin"
OCR_DIR = MEMORY_ROOT / "ocr"
CARDS_DIR = MEMORY_ROOT / "cards"
REPORTS_DIR = MEMORY_ROOT / "reports"
CONFIG_PATH = MEMORY_ROOT / "config.json"
SWIFT_SOURCE = TOOLS_DIR / "ocr_pdf_vision.swift"
OCR_BIN = BIN_DIR / "ocr_pdf_vision"
CACHE_DIR = MEMORY_ROOT / "cache"


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def doc_id(rel_path: str) -> str:
    return hashlib.sha1(rel_path.encode("utf-8")).hexdigest()[:16]


def normalize_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


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


def compile_ocr(force: bool = False) -> None:
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    needs_compile = force or not OCR_BIN.exists() or OCR_BIN.stat().st_mtime < SWIFT_SOURCE.stat().st_mtime
    if not needs_compile:
        return

    cmd = [
        "swiftc",
        str(SWIFT_SOURCE),
        "-framework",
        "PDFKit",
        "-framework",
        "Vision",
        "-framework",
        "AppKit",
        "-o",
        str(OCR_BIN),
    ]
    env = os.environ.copy()
    env["CLANG_MODULE_CACHE_PATH"] = str(CACHE_DIR / "clang-module-cache")
    env["SWIFT_MODULE_CACHE_PATH"] = str(CACHE_DIR / "swift-module-cache")
    env["TMPDIR"] = str(CACHE_DIR / "tmp")
    Path(env["TMPDIR"]).mkdir(parents=True, exist_ok=True)
    subprocess.run(cmd, check=True, env=env)


def init_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def replace_document_chunks(conn: sqlite3.Connection, document_id: str, path: str, chunks: list[str]) -> None:
    conn.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
    conn.execute("DELETE FROM chunks_fts WHERE id IN (SELECT id FROM chunks_fts WHERE id LIKE ?)", (f"{document_id}:%",))
    for index, chunk in enumerate(chunks):
        chunk_id = f"{document_id}:{index:04d}"
        conn.execute(
            "INSERT OR REPLACE INTO chunks (id, document_id, chunk_index, path, text) VALUES (?, ?, ?, ?, ?)",
            (chunk_id, document_id, index, path, chunk),
        )
        conn.execute("INSERT INTO chunks_fts (id, path, text) VALUES (?, ?, ?)", (chunk_id, path, chunk))


def update_document_row(conn: sqlite3.Connection, card: dict[str, Any]) -> None:
    conn.execute(
        """
        UPDATE documents
        SET status = ?, text_chars = ?, chunks = ?, token_estimate = ?, extracted_path = ?
        WHERE id = ?
        """,
        (
            card["status"],
            card["text_chars"],
            card["chunks"],
            card["token_estimate"],
            card.get("extracted_path"),
            card["id"],
        ),
    )


def export_chunks_jsonl(conn: sqlite3.Connection, path: Path) -> None:
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


def read_queue() -> list[dict[str, str]]:
    queue_path = REPORTS_DIR / "needs-ocr.csv"
    with queue_path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_run_report(rows: list[dict[str, Any]]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "ocr-run-report.csv"
    columns = ["status", "path", "pages", "chars", "chunks", "seconds", "message", "ocr_path", "metadata_path"]
    with report_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})

    done = sum(1 for row in rows if row["status"] == "ok")
    no_text = sum(1 for row in rows if row["status"] == "no_text")
    failed = sum(1 for row in rows if row["status"] == "error")
    total_chars = sum(int(row.get("chars") or 0) for row in rows)
    total_chunks = sum(int(row.get("chunks") or 0) for row in rows)
    total_seconds = sum(float(row.get("seconds") or 0) for row in rows)

    lines = [
        "# OCR run report",
        "",
        f"- Generated: {datetime.now(timezone.utc).isoformat()}",
        f"- Files attempted: {len(rows)}",
        f"- OCR ok: {done}",
        f"- No text after OCR: {no_text}",
        f"- Errors: {failed}",
        f"- Characters added: {total_chars}",
        f"- Chunks added: {total_chunks}",
        f"- Runtime seconds: {total_seconds:.1f}",
    ]
    (REPORTS_DIR / "ocr-run-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_ocr_for_card(card: dict[str, Any], config: dict[str, Any], conn: sqlite3.Connection) -> dict[str, Any]:
    did = card["id"]
    source_path = ROOT / card["path"]
    ocr_txt = OCR_DIR / f"{did}.txt"
    ocr_json = OCR_DIR / f"{did}.json"
    extracted_path = MEMORY_ROOT / "extracted" / f"{did}.txt"

    start = datetime.now()
    cmd = [str(OCR_BIN), str(source_path), str(ocr_txt), str(ocr_json)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    seconds = (datetime.now() - start).total_seconds()

    if result.returncode != 0:
        return {
            "status": "error",
            "path": card["path"],
            "seconds": f"{seconds:.2f}",
            "message": (result.stderr or result.stdout).strip()[:1000],
        }

    text = normalize_text(ocr_txt.read_text(encoding="utf-8", errors="replace"))
    min_text = int(config.get("min_text_chars", 80))
    if len(text) < min_text:
        return {
            "status": "no_text",
            "path": card["path"],
            "chars": len(text),
            "chunks": 0,
            "seconds": f"{seconds:.2f}",
            "message": "OCR completed but produced less than min_text_chars",
            "ocr_path": str(ocr_txt.relative_to(ROOT)),
            "metadata_path": str(ocr_json.relative_to(ROOT)),
        }

    chunks = chunk_text(text, int(config["chunk_chars"]), int(config["chunk_overlap"]))
    extracted_path.write_text(text + "\n", encoding="utf-8")

    metadata = card.setdefault("metadata", {})
    metadata["ocr"] = json.loads(ocr_json.read_text(encoding="utf-8"))
    metadata["ocr"]["engine"] = "macOS Vision"
    metadata["ocr"]["local_only"] = True

    card["status"] = "ok"
    card["text_chars"] = len(text)
    card["token_estimate"] = max(1, len(text) // 4)
    card["chunks"] = len(chunks)
    card["extracted_path"] = str(extracted_path.relative_to(ROOT))
    card["processed_at"] = datetime.now(timezone.utc).isoformat()

    card_path = ROOT / card["card_path"]
    card_path.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    replace_document_chunks(conn, did, card["path"], chunks)
    update_document_row(conn, card)

    return {
        "status": "ok",
        "path": card["path"],
        "pages": metadata["ocr"].get("pages", ""),
        "chars": len(text),
        "chunks": len(chunks),
        "seconds": f"{seconds:.2f}",
        "message": "",
        "ocr_path": str(ocr_txt.relative_to(ROOT)),
        "metadata_path": str(ocr_json.relative_to(ROOT)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run fully local OCR over Yeyo PDFs queued in needs-ocr.csv.")
    parser.add_argument("--limit", type=int, help="Process only N files.")
    parser.add_argument("--top-dir", help="Only process files in this top-level folder.")
    parser.add_argument("--contains", help="Only process paths containing this text.")
    parser.add_argument("--force-compile", action="store_true", help="Force recompilation of the Swift OCR binary.")
    parser.add_argument("--dry-run", action="store_true", help="List matching files without OCR.")
    args = parser.parse_args()

    config = load_config()
    OCR_DIR.mkdir(parents=True, exist_ok=True)
    (MEMORY_ROOT / "extracted").mkdir(parents=True, exist_ok=True)
    (MEMORY_ROOT / "chunks").mkdir(parents=True, exist_ok=True)

    queue = read_queue()
    if args.top_dir:
        queue = [row for row in queue if row["top_dir"] == args.top_dir]
    if args.contains:
        needle = args.contains.lower()
        queue = [row for row in queue if needle in row["path"].lower()]
    if args.limit:
        queue = queue[: args.limit]

    if args.dry_run:
        for row in queue:
            print(row["path"])
        print(f"matched={len(queue)}", file=sys.stderr)
        return 0

    compile_ocr(args.force_compile)
    conn = init_db(ROOT / config["paths"]["sqlite"])
    rows: list[dict[str, Any]] = []

    try:
        for index, row in enumerate(queue, start=1):
            card_path = ROOT / row["card_path"]
            card = json.loads(card_path.read_text(encoding="utf-8"))
            if card.get("status") == "ok" and card.get("extracted_path") and not args.contains:
                continue
            print(f"[{index}/{len(queue)}] OCR {card['path']}", file=sys.stderr)
            rows.append(run_ocr_for_card(card, config, conn))
            if index % 10 == 0:
                conn.commit()
    finally:
        conn.commit()
        export_chunks_jsonl(conn, MEMORY_ROOT / "chunks" / "chunks.jsonl")
        conn.close()
        write_run_report(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
