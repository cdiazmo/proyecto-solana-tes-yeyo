#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path.cwd()
MEMORY_ROOT = ROOT / ".yeyo-memory"
CARDS_DIR = MEMORY_ROOT / "cards"
REPORTS_DIR = MEMORY_ROOT / "reports"
CONFIG_PATH = MEMORY_ROOT / "config.json"


def norm(value: str | None) -> str:
    text = (value or "").lower()
    replacements = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ü": "u",
        "ñ": "n",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def classify_plan_kind(card: dict[str, Any]) -> str | None:
    metadata = card.get("metadata") or {}
    index_matches = metadata.get("index_matches") or []
    index_text = " ".join(
        f"{item.get('title','')} {item.get('description','')} {item.get('document_title','')}"
        for item in index_matches
        if isinstance(item, dict)
    )
    pdf_metadata = metadata.get("pdf_metadata") or {}
    pdf_metadata_text = " ".join(str(value) for value in pdf_metadata.values())
    text = norm(f"{card.get('path')} {card.get('title')} {card.get('doc_code')} {index_text} {pdf_metadata_text}")

    rules = [
        ("P&ID / diagrama de proceso", ["p&id", "pids", "p&ids", "piping and instrumentation", "-70-", "process diagram"]),
        ("Isometrico de tuberia HTF", ["isometric", "isometrico", "isometricos", "-htf-", "/htf/"]),
        ("Isometrico de tuberia MS", ["isometric", "isometrico", "isometricos", "-ms-", "/ms/"]),
        ("Isometrico de tuberia nitrogeno", ["isometric", "isometrico", "nitrogen", "nitrogeno", "n2"]),
        ("Soporte de tuberia HTF", ["soportes de tuberias htf", "soportes de tubería htf", "pipe support", "support list", "htf tessupport", "58-63"]),
        ("Soporte de tuberia MS", ["soportes para tuberias ms", "soportes para tubería ms", "ms system support", "75-63"]),
        ("Cimentacion / foundation", ["foundation", "foundations", "cimentacion", "cimentación", "exchangers foundation"]),
        ("Plataforma / estructura metalica", ["platform", "plataforma", "structural steel", "steel", "structures"]),
        (
            "Layout / distribucion general",
            [
                "layout",
                "planning layout",
                "distribucion",
                "general arrangement",
                "disposicion general",
                "arrangement",
                "-gad-",
                " gad ",
                "proposed locations",
                "boreholes",
                "layout1",
                "autocad",
            ],
        ),
        ("Tanque / drain back tank", ["tank", "drain back", "drain-back", "deposito", "depósito"]),
        ("Permiso / plano sellado", ["permit", "permiso", "sealed", "sellado", "county", "condado"]),
        ("Grading / obra civil terreno", ["grading", "obra tierra", "earthwork"]),
        (
            "Plano electrico",
            [
                "unifilar",
                "single line",
                "sld",
                "esquema electrico",
                "electrical drawing",
                "electrico plano",
                "plano electrico",
                "heat trace",
                "tracing",
                "edl",
            ],
        ),
        ("Plano instrumentacion/control", ["instrument drawing", "control drawing", "i&c", "charging mode", "discharging mode"]),
    ]

    for label, keywords in rules:
        if any(keyword in text for keyword in keywords):
            return label

    if re.search(r"\b\d{3}-(htf|ms)-", text):
        return "Isometrico de tuberia"
    if any(value in text for value in ["pln", "dra", "sht", "sheet", "dwg", "plano", "drawing", "diagrama", "esquema", "gad", "autocad"]):
        return "Plano / dibujo general"
    return None


def is_plan_like(card: dict[str, Any]) -> bool:
    text = norm(f"{card.get('path')} {card.get('title')} {card.get('doc_code')}")
    if classify_plan_kind(card):
        return True
    return any(
        value in text
        for value in [
            "isometric",
            "isometrico",
            "sht",
            "sheet",
            "layout",
            "pln",
            "dra",
            "dwg",
            "plano",
            "drawing",
            "unifilar",
            "single line",
            "diagrama",
            "esquema",
            "general arrangement",
            "proposed locations",
            "boreholes",
            "gad",
        ]
    )


def update_db_for_tagged_plan(conn: sqlite3.Connection, card: dict[str, Any]) -> None:
    conn.execute("DELETE FROM chunks WHERE document_id = ?", (card["id"],))
    conn.execute("DELETE FROM chunks_fts WHERE id IN (SELECT id FROM chunks_fts WHERE id LIKE ?)", (f"{card['id']}:%",))
    conn.execute(
        """
        UPDATE documents
        SET status = ?, text_chars = 0, chunks = 0, token_estimate = 0, extracted_path = NULL
        WHERE id = ?
        """,
        (card["status"], card["id"]),
    )


def main() -> int:
    config = load_config()
    db_path = ROOT / config["paths"]["sqlite"]
    conn = sqlite3.connect(db_path)
    rows: list[dict[str, Any]] = []
    counts = Counter()

    for card_path in sorted(CARDS_DIR.glob("*.json")):
        card = json.loads(card_path.read_text(encoding="utf-8"))
        if card.get("ext") != "pdf" or not is_plan_like(card):
            continue

        plan_kind = classify_plan_kind(card) or "Plano / dibujo general"
        metadata = card.setdefault("metadata", {})
        metadata["plan_tag"] = {
            "kind": plan_kind,
            "mode": "tag_only_no_ocr",
            "tagged_at": datetime.now(timezone.utc).isoformat(),
            "local_only": True,
        }

        previous_status = card.get("status")
        if previous_status in {"needs_ocr_or_empty", "ok"}:
            ocr = metadata.get("ocr") or {}
            if previous_status == "needs_ocr_or_empty" or ocr.get("engine") == "tesseract":
                card["status"] = "tagged_plan"
                card["text_chars"] = 0
                card["token_estimate"] = 0
                card["chunks"] = 0
                card["extracted_path"] = None
                update_db_for_tagged_plan(conn, card)

        card["processed_at"] = datetime.now(timezone.utc).isoformat()
        card_path.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        counts[plan_kind] += 1
        rows.append(
            {
                "path": card["path"],
                "doc_code": card.get("doc_code") or "",
                "revision": card.get("revision") or "",
                "plan_kind": plan_kind,
                "status": card.get("status") or "",
                "previous_status": previous_status or "",
                "top_dir": card.get("top_dir") or "",
                "size_human": card.get("size_human") or "",
                "card_path": card.get("card_path") or "",
            }
        )

    conn.commit()
    conn.close()

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    columns = ["path", "doc_code", "revision", "plan_kind", "status", "previous_status", "top_dir", "size_human", "card_path"]
    with (REPORTS_DIR / "plan-tags.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in sorted(rows, key=lambda item: (item["plan_kind"], item["path"])):
            writer.writerow(row)

    lines = [
        "# Etiquetas de planos",
        "",
        f"- Generado: {datetime.now(timezone.utc).isoformat()}",
        f"- PDFs etiquetados como planos: {len(rows)}",
        "",
        "| Tipo de plano | PDFs |",
        "|---|---:|",
        *[f"| {kind} | {count} |" for kind, count in counts.most_common()],
        "",
        "Regla: los planos quedan en modo `tag_only_no_ocr`; no se usa OCR completo salvo peticion explicita.",
    ]
    (REPORTS_DIR / "plan-tags.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
