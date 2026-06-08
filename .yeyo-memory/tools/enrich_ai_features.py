#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path.cwd()
MEMORY_ROOT = ROOT / ".yeyo-memory"
CARDS_DIR = MEMORY_ROOT / "cards"
REPORTS_DIR = MEMORY_ROOT / "reports"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def norm(value: str) -> str:
    value = value.lower()
    value = value.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    value = value.replace("ü", "u").replace("ñ", "n")
    return value


def contains(text: str, *needles: str) -> bool:
    ntext = norm(text)
    return any(norm(needle) in ntext for needle in needles)


def load_cards() -> list[tuple[Path, dict[str, Any]]]:
    return [(path, json.loads(path.read_text(encoding="utf-8"))) for path in sorted(CARDS_DIR.glob("*.json"))]


def source_corpus(card: dict[str, Any]) -> str:
    top = card.get("top_dir") or ""
    path = card.get("path") or ""
    if top == "Helios Sole":
        return "Proyecto Helios Sole"
    if top == "Documentos en Servidor Atlántica":
        return "Servidor Atlantica"
    if top == "Planos Solana":
        return "Planos Solana"
    if top == "Ejemplo PCI":
        return "Ejemplo PCI"
    if top.startswith("0") or top.startswith("1") or "Solana" in path:
        return "Repositorio Solana / Yeyo"
    return top or "Sin origen"


def project_area(card: dict[str, Any]) -> str:
    text = f"{card.get('top_dir','')} {card.get('path','')} {card.get('title','')}"
    if contains(text, "helios i", "helios 1"):
        return "Helios I"
    if contains(text, "helios ii", "helios 2"):
        return "Helios II"
    if contains(text, "tes", "solana", "almac"):
        return "TES / almacenamiento"
    if contains(text, "la/t", "laat", "lsat", "15 kv", "subestacion", "se colectora", "se elevadora"):
        return "Infraestructura electrica"
    return "General"


def deliverable_part(card: dict[str, Any], pdf: dict[str, str], plan: dict[str, str]) -> str:
    text = f"{card.get('path','')} {card.get('title','')} {pdf.get('type','')} {pdf.get('topic','')} {plan.get('plan_kind','')}"
    if card.get("status") == "tagged_plan" or contains(text, "dwg", "plano", "drawing", "pid", "p&id", "isometrico", "layout"):
        return "Planos"
    if contains(text, "presupuesto", "medicion", "mto", "recuento", "partida", "budget", "quantity"):
        return "Mediciones y presupuestos"
    if contains(text, "pliego", "condiciones", "spec", "especificacion", "ppi", "procedimiento", "manual"):
        return "Pliego de condiciones"
    if contains(text, "memoria", "anejo", "calculo", "nota tecnica", "technical note", "tn-", "cal-"):
        return "Memoria y anejos"
    if contains(text, "lista", "lis-", "index", "indice"):
        return "Listados e indices"
    return "Documentacion auxiliar"


def discipline(card: dict[str, Any], pdf: dict[str, str], plan: dict[str, str]) -> str:
    text = f"{card.get('path','')} {card.get('title','')} {pdf.get('topic','')} {plan.get('plan_kind','')}"
    if contains(text, "pci", "fire", "incendio"):
        return "PCI"
    if contains(text, "htf", "hm balance", "h&mb", "proceso", "mecanica", "equipos", "valvula", "tuberia", "isometrico", "pid", "p&id"):
        return "Proceso / mecanica / tuberias"
    if contains(text, "civil", "estructura", "cimentacion", "foundation", "obra civil", "grading", "plataforma"):
        return "Civil / estructuras"
    if contains(text, "instrument", "control", "ic-", "dcs", "instrumentacion"):
        return "Instrumentacion y control"
    if contains(text, "electrico", "electric", "15 kv", "bt", "mt", "alta tension", "baja tension", "subestacion", "laat", "lsat"):
        return "Electrica"
    if contains(text, "permiso", "licencia", "oficial", "oca", "boletin", "cdo", "apm"):
        return "Permisos / legalizacion"
    if contains(text, "fabricacion", "compra", "inspeccion", "calidad", "ppi"):
        return "Fabricacion / compras / calidad"
    return "General"


def extraction_quality(card: dict[str, Any]) -> str:
    status = card.get("status") or ""
    ext = card.get("ext") or ""
    text_chars = int(card.get("text_chars") or 0)
    metadata = card.get("metadata") or {}
    pages = int(metadata.get("pages") or 0)
    if status == "ok":
        if pages and text_chars / max(pages, 1) < 250:
            return "baja_texto_escaso_por_pagina"
        return "alta_texto_extraido"
    if status == "tagged_plan":
        return "plano_etiquetado_sin_ocr"
    if status == "needs_ocr_or_empty":
        if pages:
            return "requiere_ocr"
        return "sin_texto_util"
    if status == "metadata_only":
        if ext in {"dwg", "nwd"}:
            return "formato_tecnico_metadata_only"
        return "metadata_only"
    if status == "archive_listed":
        return "archivo_comprimido_listado"
    return status or "desconocida"


def ai_action(card: dict[str, Any], features: dict[str, str]) -> str:
    status = card.get("status") or ""
    ext = card.get("ext") or ""
    size = int(card.get("size_bytes") or 0)
    if status == "ok":
        return "usar_chunks"
    if status == "tagged_plan":
        return "usar_solo_etiqueta_y_metadatos"
    if status == "needs_ocr_or_empty":
        if size > 50 * 1024 * 1024:
            return "priorizar_revision_manual_u_ocr_selectivo"
        return "ocr_local_si_es_relevante"
    if ext in {"dwg", "nwd"}:
        return "usar_indices_o_pdf_equivalente"
    if status == "archive_listed":
        return "descomprimir_solo_si_indice_lo_justifica"
    return "usar_metadatos"


def reuse_priority(card: dict[str, Any], features: dict[str, str], index_count: int) -> str:
    if card.get("status") == "error":
        return "baja"
    if features["deliverable_part"] in {"Memoria y anejos", "Pliego de condiciones", "Mediciones y presupuestos"} and card.get("status") == "ok":
        return "alta"
    if index_count >= 2 and card.get("status") in {"ok", "tagged_plan"}:
        return "media_alta"
    if features["deliverable_part"] == "Planos":
        return "media"
    if card.get("status") == "needs_ocr_or_empty":
        return "pendiente_ocr"
    return "media"


def main() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    pdf_data = {row["path"]: row for row in read_csv(REPORTS_DIR / "pdf-catalog.csv")}
    plan_data = {row["path"]: row for row in read_csv(REPORTS_DIR / "plan-tags.csv")}
    match_rows = read_csv(REPORTS_DIR / "document-index-matches.csv")
    match_counts: dict[str, int] = {}
    for row in match_rows:
        key = row.get("matched_card_path", "")
        if key:
            match_counts[key] = match_counts.get(key, 0) + 1

    now = datetime.now(timezone.utc).isoformat()
    rows: list[dict[str, Any]] = []

    for path, card in load_cards():
        doc_path = card.get("path") or ""
        pdf = pdf_data.get(doc_path, {})
        plan = plan_data.get(doc_path, {})
        metadata = card.setdefault("metadata", {})
        index_matches = metadata.get("index_matches") or []
        index_count = len(index_matches) or match_counts.get(card.get("card_path") or "", 0)
        pages = int((metadata or {}).get("pages") or 0)
        features = {
            "source_corpus": source_corpus(card),
            "project_area": project_area(card),
            "deliverable_part": deliverable_part(card, pdf, plan),
            "discipline": discipline(card, pdf, plan),
            "extraction_quality": extraction_quality(card),
            "ai_action": "",
            "reuse_priority": "",
            "page_count": pages,
            "indexed_reference_count": index_count,
            "enriched_at": now,
        }
        features["ai_action"] = ai_action(card, features)
        features["reuse_priority"] = reuse_priority(card, features, index_count)
        metadata["ai_features"] = features
        path.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        rows.append(
            {
                "path": doc_path,
                "top_dir": card.get("top_dir") or "",
                "ext": card.get("ext") or "",
                "status": card.get("status") or "",
                "title": card.get("title") or "",
                "doc_code": card.get("doc_code") or "",
                "revision": card.get("revision") or "",
                "text_chars": card.get("text_chars") or 0,
                "chunks": card.get("chunks") or 0,
                **features,
            }
        )

    columns = [
        "path",
        "top_dir",
        "ext",
        "status",
        "title",
        "doc_code",
        "revision",
        "source_corpus",
        "project_area",
        "deliverable_part",
        "discipline",
        "extraction_quality",
        "ai_action",
        "reuse_priority",
        "page_count",
        "indexed_reference_count",
        "text_chars",
        "chunks",
        "enriched_at",
    ]
    with (REPORTS_DIR / "ai-features.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    counters: dict[str, dict[str, int]] = {}
    for key in ["source_corpus", "project_area", "deliverable_part", "discipline", "extraction_quality", "ai_action", "reuse_priority"]:
        bucket: dict[str, int] = {}
        for row in rows:
            value = str(row[key])
            bucket[value] = bucket.get(value, 0) + 1
        counters[key] = dict(sorted(bucket.items(), key=lambda item: (-item[1], item[0])))

    lines = [
        "# Features para IA",
        "",
        f"- Generado: {now}",
        f"- Documentos enriquecidos: {len(rows)}",
        "",
        "Estas features sirven para filtrar y priorizar contexto antes de enviarlo a un modelo IA.",
        "",
    ]
    labels = {
        "source_corpus": "Corpus / origen",
        "project_area": "Área de proyecto",
        "deliverable_part": "Parte documental",
        "discipline": "Disciplina",
        "extraction_quality": "Calidad de extracción",
        "ai_action": "Acción recomendada IA",
        "reuse_priority": "Prioridad de reutilización",
    }
    for key, label in labels.items():
        lines.extend([f"## {label}", "", "| Valor | Documentos |", "|---|---:|"])
        lines.extend(f"| {value} | {count} |" for value, count in counters[key].items())
        lines.append("")
    lines.extend(
        [
            "Archivo generado:",
            "",
            "- `ai-features.csv`: una fila por documento con señales de filtrado para IA/RAG.",
        ]
    )
    (REPORTS_DIR / "ai-features.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
