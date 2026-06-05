#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path.cwd()
MEMORY_ROOT = ROOT / ".yeyo-memory"
CARDS_DIR = MEMORY_ROOT / "cards"
REPORTS_DIR = MEMORY_ROOT / "reports"


def norm(value: str | None) -> str:
    return (value or "").lower()


def compact_number(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def pct(value: int, total: int) -> str:
    if not total:
        return "0.0%"
    return f"{(value / total) * 100:.1f}%"


def classify_type(card: dict[str, Any]) -> str:
    text = norm(f"{card.get('path')} {card.get('title')} {card.get('doc_code')}")

    rules = [
        ("Plano / dibujo", [r"\bpln\b", r"\bdra\b", "drawing", "layout", "plan ", "plano", "sht", "sheet"]),
        ("Isometrico", ["isometric", "isometrico", "isometricos", "-htf-", "-ms-", "-nitrogen-", "iso"]),
        ("Calculo", [r"\bcal\b", "calculation", "calculo", "calculations"]),
        ("Especificacion tecnica", [r"\besp\b", "specification", "technical specifications", "especificacion"]),
        ("Listado / registro", [r"\blis\b", "list", "lista", "mto", "register"]),
        ("Hoja de datos", [r"\bhdd\b", "datasheet", "data sheet", "hoja tecnica"]),
        ("Memoria / nota tecnica", [r"\bmem\b", r"\bmom\b", "memo", "memorandum", "operational limits", "operation philosophy", "nota tecnica"]),
        ("Procedimiento / manual", ["manual", "procedure", "procedimiento", "operating instructions", "wps", "pqr", "itp"]),
        ("Informe", [r"\binf\b", "report", "informe", "weekly", "monthly"]),
        ("Permiso / paquete oficial", ["permit", "permiso", "county", "condado", "sealed", "sellado", "zoning"]),
        ("Inspeccion", ["inspection", "inspeccion", "inspección", "sealed inspection"]),
        ("Transmision / carta", ["transmittal", "transmision", "transmisión", "cartas de transmision"]),
    ]

    for label, patterns in rules:
        for pattern in patterns:
            if pattern.startswith(r"\b"):
                if re.search(pattern, text):
                    return label
            elif pattern in text:
                return label
    return "Otros / sin clasificar"


def classify_topic(card: dict[str, Any]) -> str:
    text = norm(f"{card.get('top_dir')} {card.get('path')} {card.get('title')} {card.get('doc_code')}")

    rules = [
        ("Civil y estructuras", ["c&s", "civil", "structural", "estructura", "foundation", "platform", "steel", "grading", "apoyos"]),
        ("Tuberias e isometricos", ["tuberia", "tubería", "piping", "pipe", "isometric", "isometrico", "support", "soporte"]),
        ("Proceso y mecanica", ["m&p", "mechanical", "process", "heat exchanger", "hex", "htf", "tes", "pump", "valve", "tank"]),
        ("Electricidad", ["electrico", "eléctrico", "electrical", "heat trace", "tracing", "edl"]),
        ("Instrumentacion y control", ["i&c", "instrument", "control", "charging mode", "discharging mode"]),
        ("Especificaciones tecnicas", ["especificaciones tecnicas", "technical specifications", "specification", "spec"]),
        ("Permisos y documentacion oficial", ["presentado al condado", "permit", "permiso", "county", "zoning", "sealed", "sellado"]),
        ("Fabricacion y compras", ["fabricacion", "fabricación", "compra", "vendor", "quality", "dossier", "fabrication"]),
        ("As built", ["as built", "as-built"]),
        ("Inspeccion final", ["inspeccion final", "inspección final", "inspection"]),
        ("Corrosion y sal", ["corrosion", "corrosión", "sal ", "salt", "chloride", "cloruro"]),
        ("Informes de avance", ["informe", "report", "weekly", "monthly", "construction report"]),
        ("Modelos 3D", ["3dmodel", "3d model", ".nwd"]),
    ]

    for label, keywords in rules:
        if any(keyword in text for keyword in keywords):
            return label
    return "General / otros"


def readability(card: dict[str, Any]) -> str:
    if card["status"] == "ok":
        return "legible"
    if card["status"] == "needs_ocr_or_empty":
        return "requiere OCR o sin texto"
    if card["status"] == "error":
        return "error"
    return card["status"]


def info_band(text_chars: int) -> str:
    if text_chars >= 100_000:
        return "muy alta"
    if text_chars >= 25_000:
        return "alta"
    if text_chars >= 5_000:
        return "media"
    if text_chars >= 500:
        return "baja"
    return "sin texto util"


def load_pdf_cards() -> list[dict[str, Any]]:
    cards = []
    for path in sorted(CARDS_DIR.glob("*.json")):
        card = json.loads(path.read_text(encoding="utf-8"))
        if card.get("ext") == "pdf":
            cards.append(card)
    return cards


def add_summary(bucket: dict[str, Any], card: dict[str, Any]) -> None:
    bucket["pdfs"] += 1
    bucket["text_chars"] += int(card.get("text_chars") or 0)
    bucket["chunks"] += int(card.get("chunks") or 0)
    bucket["token_estimate"] += int(card.get("token_estimate") or 0)
    if card.get("status") == "ok":
        bucket["legibles"] += 1
    elif card.get("status") == "needs_ocr_or_empty":
        bucket["requiere_ocr"] += 1
    elif card.get("status") == "error":
        bucket["errores"] += 1
    if card.get("doc_code"):
        bucket["con_codigo"] += 1


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def main() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    cards = load_pdf_cards()
    generated_at = datetime.now(timezone.utc).isoformat()

    pdf_rows: list[dict[str, Any]] = []
    by_type: dict[str, dict[str, Any]] = defaultdict(lambda: defaultdict(int))
    by_topic: dict[str, dict[str, Any]] = defaultdict(lambda: defaultdict(int))
    by_status: dict[str, dict[str, Any]] = defaultdict(lambda: defaultdict(int))

    for card in cards:
        doc_type = classify_type(card)
        topic = classify_topic(card)
        row = {
            "path": card["path"],
            "doc_code": card.get("doc_code") or "",
            "revision": card.get("revision") or "",
            "title": card.get("title") or "",
            "type": doc_type,
            "topic": topic,
            "readability": readability(card),
            "status": card["status"],
            "size_human": card["size_human"],
            "text_chars": card["text_chars"],
            "chunks": card["chunks"],
            "token_estimate": card["token_estimate"],
            "info_band": info_band(int(card.get("text_chars") or 0)),
            "card_path": card["card_path"],
            "extracted_path": card.get("extracted_path") or "",
        }
        pdf_rows.append(row)
        add_summary(by_type[doc_type], card)
        add_summary(by_topic[topic], card)
        add_summary(by_status[card["status"]], card)

    pdf_rows.sort(key=lambda row: (row["topic"], row["type"], row["path"]))
    total = len(pdf_rows)
    readable = sum(1 for row in pdf_rows if row["readability"] == "legible")
    needs_ocr = sum(1 for row in pdf_rows if row["readability"] == "requiere OCR o sin texto")
    errors = sum(1 for row in pdf_rows if row["readability"] == "error")
    with_code = sum(1 for row in pdf_rows if row["doc_code"])
    total_chars = sum(int(row["text_chars"]) for row in pdf_rows)
    total_chunks = sum(int(row["chunks"]) for row in pdf_rows)
    total_token_estimate = sum(int(row["token_estimate"]) for row in pdf_rows)

    pdf_columns = [
        "path",
        "doc_code",
        "revision",
        "title",
        "type",
        "topic",
        "readability",
        "status",
        "size_human",
        "text_chars",
        "chunks",
        "token_estimate",
        "info_band",
        "card_path",
        "extracted_path",
    ]
    write_csv(REPORTS_DIR / "pdf-catalog.csv", pdf_rows, pdf_columns)

    def summary_rows(summary: dict[str, dict[str, Any]], label: str) -> list[dict[str, Any]]:
        rows = []
        for key, data in summary.items():
            pdfs = int(data["pdfs"])
            rows.append(
                {
                    label: key,
                    "pdfs": pdfs,
                    "legibles": int(data["legibles"]),
                    "legibilidad": pct(int(data["legibles"]), pdfs),
                    "requiere_ocr": int(data["requiere_ocr"]),
                    "errores": int(data["errores"]),
                    "con_codigo": int(data["con_codigo"]),
                    "text_chars": int(data["text_chars"]),
                    "chunks": int(data["chunks"]),
                    "token_estimate": int(data["token_estimate"]),
                }
            )
        return sorted(rows, key=lambda row: (-int(row["text_chars"]), -int(row["pdfs"]), row[label]))

    type_rows = summary_rows(by_type, "type")
    topic_rows = summary_rows(by_topic, "topic")
    status_rows = summary_rows(by_status, "status")

    summary_columns = [
        "pdfs",
        "legibles",
        "legibilidad",
        "requiere_ocr",
        "errores",
        "con_codigo",
        "text_chars",
        "chunks",
        "token_estimate",
    ]
    write_csv(REPORTS_DIR / "pdf-type-summary.csv", type_rows, ["type", *summary_columns])
    write_csv(REPORTS_DIR / "pdf-topic-summary.csv", topic_rows, ["topic", *summary_columns])
    write_csv(REPORTS_DIR / "pdf-status-summary.csv", status_rows, ["status", *summary_columns])

    top_topics = topic_rows[:8]
    top_types = type_rows[:8]

    lines = [
        "# Informe de PDFs",
        "",
        f"- Generado: {generated_at}",
        f"- PDFs catalogados: {compact_number(total)}",
        f"- PDFs legibles localmente: {compact_number(readable)} ({pct(readable, total)})",
        f"- PDFs que requieren OCR o no contienen texto útil: {compact_number(needs_ocr)} ({pct(needs_ocr, total)})",
        f"- PDFs con error real: {compact_number(errors)} ({pct(errors, total)})",
        f"- PDFs con código documental inferido: {compact_number(with_code)} ({pct(with_code, total)})",
        f"- Información textual extraída: {compact_number(total_chars)} caracteres, {compact_number(total_chunks)} chunks, ~{compact_number(total_token_estimate)} tokens estimados",
        "",
        "## Legibilidad por estado",
        "",
        "| Estado | PDFs | Legibles | Requiere OCR | Errores | Texto extraído | Chunks |",
        "|---|---:|---:|---:|---:|---:|---:|",
        *[
            f"| {row['status']} | {row['pdfs']} | {row['legibles']} | {row['requiere_ocr']} | {row['errores']} | {compact_number(row['text_chars'])} | {compact_number(row['chunks'])} |"
            for row in status_rows
        ],
        "",
        "## Tipos documentales principales",
        "",
        "| Tipo | PDFs | Legibles | Legibilidad | Requiere OCR | Texto extraído | Chunks |",
        "|---|---:|---:|---:|---:|---:|---:|",
        *[
            f"| {row['type']} | {row['pdfs']} | {row['legibles']} | {row['legibilidad']} | {row['requiere_ocr']} | {compact_number(row['text_chars'])} | {compact_number(row['chunks'])} |"
            for row in top_types
        ],
        "",
        "## Información por temática",
        "",
        "| Temática | PDFs | Legibles | Legibilidad | Requiere OCR | Texto extraído | Chunks |",
        "|---|---:|---:|---:|---:|---:|---:|",
        *[
            f"| {row['topic']} | {row['pdfs']} | {row['legibles']} | {row['legibilidad']} | {row['requiere_ocr']} | {compact_number(row['text_chars'])} | {compact_number(row['chunks'])} |"
            for row in top_topics
        ],
        "",
        "## Lectura rápida",
        "",
        "- `pdf-catalog.csv`: ficha de cada PDF con código, tipo, temática, legibilidad y volumen de información.",
        "- `pdf-type-summary.csv`: resumen agregado por tipo documental.",
        "- `pdf-topic-summary.csv`: resumen agregado por temática.",
        "- `pdf-status-summary.csv`: resumen agregado por estado técnico.",
        "",
        "Nota: la clasificación es heurística, basada en ruta, nombre, código documental y metadatos ya extraídos. Es suficiente para priorizar y reducir tokens; puede refinarse cuando empecemos a redactar la memoria final.",
    ]

    (REPORTS_DIR / "pdf-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
