#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path.cwd()
MEMORY_ROOT = ROOT / ".yeyo-memory"
OCR_DIR = MEMORY_ROOT / "ocr"
REPORTS_DIR = MEMORY_ROOT / "reports"
CONFIG_PATH = MEMORY_ROOT / "config.json"
CACHE_DIR = MEMORY_ROOT / "cache" / "tesseract-pages"
PLAN_TAGS_PATH = REPORTS_DIR / "plan-tags.csv"


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


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


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"Missing required local tool: {name}")
    return path


def available_tesseract_langs(tesseract: str) -> set[str]:
    result = subprocess.run([tesseract, "--list-langs"], capture_output=True, text=True, check=False)
    langs = set()
    for line in result.stdout.splitlines():
        value = line.strip()
        if value and not value.lower().startswith("list of"):
            langs.add(value)
    return langs


def choose_lang(tesseract: str) -> str:
    langs = available_tesseract_langs(tesseract)
    if "eng" in langs and "spa" in langs:
        return "eng+spa"
    if "eng" in langs:
        return "eng"
    if "spa" in langs:
        return "spa"
    return "eng"


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
    with (REPORTS_DIR / "needs-ocr.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_plan_paths() -> set[str]:
    if not PLAN_TAGS_PATH.exists():
        return set()
    with PLAN_TAGS_PATH.open(newline="", encoding="utf-8") as handle:
        return {row["path"] for row in csv.DictReader(handle)}


def render_pdf(pdftoppm: str, pdf_path: Path, output_prefix: Path, dpi: int) -> list[Path]:
    cmd = [pdftoppm, "-r", str(dpi), "-png", str(pdf_path), str(output_prefix)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip())
    images = sorted(output_prefix.parent.glob(output_prefix.name + "-*.png"))
    if not images:
        raise RuntimeError("pdftoppm produced no page images")
    return images


def tesseract_image(tesseract: str, image: Path, lang: str, psm: int) -> str:
    cmd = [tesseract, str(image), "stdout", "-l", lang, "--psm", str(psm)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip())
    return result.stdout


def process_card(
    card: dict[str, Any],
    config: dict[str, Any],
    conn: sqlite3.Connection,
    pdftoppm: str,
    tesseract: str,
    lang: str,
    dpi: int,
    psm: int,
    keep_images: bool,
) -> dict[str, Any]:
    start = datetime.now()
    did = card["id"]
    pdf_path = ROOT / card["path"]
    work_dir = CACHE_DIR / did
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    try:
        images = render_pdf(pdftoppm, pdf_path, work_dir / "page", dpi)
        page_texts = []
        pages_with_text = 0
        for index, image in enumerate(images, start=1):
            text = tesseract_image(tesseract, image, lang, psm)
            text = normalize_text(text)
            if text:
                pages_with_text += 1
            page_texts.append(f"[page {index}]\n{text}")

        full_text = normalize_text("\n\n".join(page_texts))
        seconds = (datetime.now() - start).total_seconds()

        ocr_txt = OCR_DIR / f"{did}.txt"
        ocr_json = OCR_DIR / f"{did}.json"
        ocr_txt.write_text(full_text + "\n", encoding="utf-8")
        metadata = {
            "engine": "tesseract",
            "local_only": True,
            "pdf_renderer": "pdftoppm",
            "dpi": dpi,
            "psm": psm,
            "lang": lang,
            "pages": len(images),
            "pages_with_text": pages_with_text,
            "characters": len(full_text),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        ocr_json.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        min_text = int(config.get("min_text_chars", 80))
        if len(full_text) < min_text:
            return {
                "status": "no_text",
                "path": card["path"],
                "pages": len(images),
                "chars": len(full_text),
                "chunks": 0,
                "seconds": f"{seconds:.2f}",
                "message": "OCR completed but produced less than min_text_chars",
                "ocr_path": str(ocr_txt.relative_to(ROOT)),
                "metadata_path": str(ocr_json.relative_to(ROOT)),
            }

        chunks = chunk_text(full_text, int(config["chunk_chars"]), int(config["chunk_overlap"]))
        extracted_path = MEMORY_ROOT / "extracted" / f"{did}.txt"
        extracted_path.write_text(full_text + "\n", encoding="utf-8")

        card_metadata = card.setdefault("metadata", {})
        card_metadata["ocr"] = metadata
        card["status"] = "ok"
        card["text_chars"] = len(full_text)
        card["token_estimate"] = max(1, len(full_text) // 4)
        card["chunks"] = len(chunks)
        card["extracted_path"] = str(extracted_path.relative_to(ROOT))
        card["processed_at"] = datetime.now(timezone.utc).isoformat()

        (ROOT / card["card_path"]).write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        replace_document_chunks(conn, did, card["path"], chunks)
        update_document_row(conn, card)

        return {
            "status": "ok",
            "path": card["path"],
            "pages": len(images),
            "chars": len(full_text),
            "chunks": len(chunks),
            "seconds": f"{seconds:.2f}",
            "message": "",
            "ocr_path": str(ocr_txt.relative_to(ROOT)),
            "metadata_path": str(ocr_json.relative_to(ROOT)),
        }
    except Exception as exc:
        seconds = (datetime.now() - start).total_seconds()
        return {
            "status": "error",
            "path": card["path"],
            "seconds": f"{seconds:.2f}",
            "message": str(exc)[:1000],
        }
    finally:
        if not keep_images and work_dir.exists():
            shutil.rmtree(work_dir)


def write_report(rows: list[dict[str, Any]]) -> None:
    columns = ["status", "path", "pages", "chars", "chunks", "seconds", "message", "ocr_path", "metadata_path"]
    csv_path = REPORTS_DIR / "tesseract-ocr-run-report.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})

    ok = sum(1 for row in rows if row["status"] == "ok")
    no_text = sum(1 for row in rows if row["status"] == "no_text")
    error = sum(1 for row in rows if row["status"] == "error")
    chars = sum(int(row.get("chars") or 0) for row in rows)
    chunks = sum(int(row.get("chunks") or 0) for row in rows)
    seconds = sum(float(row.get("seconds") or 0) for row in rows)
    pages = sum(int(row.get("pages") or 0) for row in rows)

    md = [
        "# Tesseract OCR run report",
        "",
        f"- Generated: {datetime.now(timezone.utc).isoformat()}",
        f"- Files attempted: {len(rows)}",
        f"- Pages attempted: {pages}",
        f"- OCR ok: {ok}",
        f"- No text after OCR: {no_text}",
        f"- Errors: {error}",
        f"- Characters added: {chars}",
        f"- Chunks added: {chunks}",
        f"- Runtime seconds: {seconds:.1f}",
    ]
    (REPORTS_DIR / "tesseract-ocr-run-report.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local Tesseract OCR over Yeyo PDFs queued in needs-ocr.csv.")
    parser.add_argument("--limit", type=int, help="Process only N files.")
    parser.add_argument("--top-dir", help="Only process files in this top-level folder.")
    parser.add_argument("--contains", help="Only process paths containing this text.")
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--psm", type=int, default=6)
    parser.add_argument("--keep-images", action="store_true")
    parser.add_argument("--include-plans", action="store_true", help="OCR plans too. By default plan PDFs are tag-only.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    pdftoppm = require_tool("pdftoppm")
    tesseract = require_tool("tesseract")
    lang = choose_lang(tesseract)
    config = load_config()

    OCR_DIR.mkdir(parents=True, exist_ok=True)
    (MEMORY_ROOT / "extracted").mkdir(parents=True, exist_ok=True)
    (MEMORY_ROOT / "chunks").mkdir(parents=True, exist_ok=True)

    queue = read_queue()
    if not args.include_plans:
        plan_paths = read_plan_paths()
        queue = [row for row in queue if row["path"] not in plan_paths]
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
        print(f"matched={len(queue)} lang={lang}", file=sys.stderr)
        return 0

    conn = init_db(ROOT / config["paths"]["sqlite"])
    rows: list[dict[str, Any]] = []
    try:
        for index, row in enumerate(queue, start=1):
            card = json.loads((ROOT / row["card_path"]).read_text(encoding="utf-8"))
            if card.get("status") == "ok" and card.get("extracted_path"):
                continue
            print(f"[{index}/{len(queue)}] OCR {card['path']}", file=sys.stderr)
            rows.append(process_card(card, config, conn, pdftoppm, tesseract, lang, args.dpi, args.psm, args.keep_images))
            if index % 10 == 0:
                conn.commit()
    finally:
        conn.commit()
        export_chunks_jsonl(conn, MEMORY_ROOT / "chunks" / "chunks.jsonl")
        conn.close()
        write_report(rows)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
