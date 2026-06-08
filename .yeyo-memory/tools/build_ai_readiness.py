#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path.cwd()
MEMORY_ROOT = ROOT / ".yeyo-memory"
CARDS_DIR = MEMORY_ROOT / "cards"
REPORTS_DIR = MEMORY_ROOT / "reports"
PACKS_DIR = MEMORY_ROOT / "context-packs"


DELIVERABLES = [
    "Memoria y anejos",
    "Planos",
    "Pliego de condiciones",
    "Mediciones y presupuestos",
    "Listados e indices",
]


DISCIPLINES = [
    "Proceso / mecanica / tuberias",
    "Civil / estructuras",
    "Electrica",
    "Instrumentacion y control",
    "PCI",
    "Permisos / legalizacion",
    "Fabricacion / compras / calidad",
]


def load_cards() -> list[dict[str, Any]]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(CARDS_DIR.glob("*.json"))]


def feature(card: dict[str, Any], key: str, default: Any = "") -> Any:
    return ((card.get("metadata") or {}).get("ai_features") or {}).get(key, default)


def score_card(card: dict[str, Any]) -> tuple[int, list[str]]:
    status = card.get("status") or ""
    ext = card.get("ext") or ""
    text_chars = int(card.get("text_chars") or 0)
    chunks = int(card.get("chunks") or 0)
    index_count = int(feature(card, "indexed_reference_count", 0) or 0)
    deliverable = feature(card, "deliverable_part")
    priority = feature(card, "reuse_priority")
    quality = feature(card, "extraction_quality")
    action = feature(card, "ai_action")

    score = 0
    reasons: list[str] = []

    if status == "ok":
        score += 30
        reasons.append("texto extraido")
    if quality == "alta_texto_extraido":
        score += 15
        reasons.append("calidad alta")
    if chunks:
        score += min(20, chunks // 2)
        reasons.append("chunks disponibles")
    if text_chars > 5000:
        score += 10
    if text_chars > 50000:
        score += 10
        reasons.append("contenido abundante")
    if index_count:
        score += min(20, index_count * 2)
        reasons.append("referenciado en indices")
    if priority == "alta":
        score += 25
        reasons.append("prioridad alta")
    elif priority == "media_alta":
        score += 15
    elif priority == "pendiente_ocr":
        score -= 10
    if deliverable in {"Memoria y anejos", "Pliego de condiciones", "Mediciones y presupuestos"}:
        score += 20
        reasons.append("parte principal del proyecto")
    elif deliverable == "Planos":
        score += 5
    if action == "usar_chunks":
        score += 10
    elif action in {"usar_solo_etiqueta_y_metadatos", "usar_indices_o_pdf_equivalente"}:
        score -= 5
    if status in {"error", "needs_ocr_or_empty"}:
        score -= 20
    if ext in {"dwg", "nwd"}:
        score -= 15

    return max(0, min(100, score)), reasons


def send_policy(card: dict[str, Any], score: int) -> str:
    action = feature(card, "ai_action")
    status = card.get("status") or ""
    if action == "usar_chunks" and score >= 70:
        return "enviar_chunks_prioritarios"
    if action == "usar_chunks":
        return "enviar_chunks_si_consulta_relevante"
    if status == "tagged_plan":
        return "enviar_metadatos_y_tipo_plano"
    if action == "ocr_local_si_es_relevante":
        return "no_enviar_hasta_ocr_selectivo"
    if action == "priorizar_revision_manual_u_ocr_selectivo":
        return "no_enviar_documento_gigante"
    if action == "usar_indices_o_pdf_equivalente":
        return "buscar_pdf_o_indice_equivalente"
    return "metadatos_solamente"


def ocr_score(card: dict[str, Any]) -> int:
    if card.get("status") != "needs_ocr_or_empty":
        return 0
    size_mb = int(card.get("size_bytes") or 0) / (1024 * 1024)
    pages = int(feature(card, "page_count", 0) or 0)
    deliverable = feature(card, "deliverable_part")
    discipline = feature(card, "discipline")
    score = 20
    if deliverable in {"Memoria y anejos", "Pliego de condiciones", "Mediciones y presupuestos"}:
        score += 40
    if discipline in {"Proceso / mecanica / tuberias", "Civil / estructuras", "Electrica", "PCI"}:
        score += 15
    if pages and pages <= 20:
        score += 15
    if size_mb <= 25:
        score += 10
    if size_mb > 50:
        score -= 30
    return max(0, min(100, score))


def compact_doc(card: dict[str, Any], score: int, reasons: list[str]) -> dict[str, Any]:
    return {
        "path": card.get("path") or "",
        "title": card.get("title") or "",
        "doc_code": card.get("doc_code") or "",
        "revision": card.get("revision") or "",
        "ext": card.get("ext") or "",
        "status": card.get("status") or "",
        "size_human": card.get("size_human") or "",
        "text_chars": int(card.get("text_chars") or 0),
        "chunks": int(card.get("chunks") or 0),
        "score": score,
        "score_reasons": reasons,
        "send_policy": send_policy(card, score),
        "ocr_priority": ocr_score(card),
        "source_corpus": feature(card, "source_corpus"),
        "project_area": feature(card, "project_area"),
        "deliverable_part": feature(card, "deliverable_part"),
        "discipline": feature(card, "discipline"),
        "extraction_quality": feature(card, "extraction_quality"),
        "ai_action": feature(card, "ai_action"),
        "reuse_priority": feature(card, "reuse_priority"),
        "page_count": feature(card, "page_count", 0),
        "indexed_reference_count": feature(card, "indexed_reference_count", 0),
        "card_path": card.get("card_path") or "",
        "extracted_path": card.get("extracted_path") or "",
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = [
        "score",
        "send_policy",
        "ocr_priority",
        "path",
        "title",
        "doc_code",
        "revision",
        "ext",
        "status",
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
        "size_human",
        "score_reasons",
        "card_path",
        "extracted_path",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            out = dict(row)
            out["score_reasons"] = "; ".join(out.get("score_reasons") or [])
            writer.writerow({column: out.get(column, "") for column in columns})


def write_context_pack(name: str, rows: list[dict[str, Any]]) -> None:
    PACKS_DIR.mkdir(parents=True, exist_ok=True)
    safe = name.lower().replace("/", "-").replace(" ", "_")
    payload = {
        "name": name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "usage": "Usar como preseleccion local antes de construir prompts RAG. Enviar solo chunks de documentos con send_policy enviar_*.",
        "documents": rows,
    }
    (PACKS_DIR / f"{safe}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    PACKS_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    scored: list[dict[str, Any]] = []
    for card in load_cards():
        score, reasons = score_card(card)
        compact = compact_doc(card, score, reasons)
        scored.append(compact)

    scored.sort(key=lambda row: (-row["score"], row["path"]))
    write_csv(REPORTS_DIR / "ai-readiness.csv", scored)

    ocr_rows = sorted(
        [row for row in scored if row["ocr_priority"]],
        key=lambda row: (-row["ocr_priority"], row["path"]),
    )
    write_csv(REPORTS_DIR / "ocr-priority.csv", ocr_rows)

    by_deliverable: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_discipline: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in scored:
        by_deliverable[row["deliverable_part"]].append(row)
        by_discipline[row["discipline"]].append(row)

    for deliverable in DELIVERABLES:
        write_context_pack(f"deliverable_{deliverable}", by_deliverable.get(deliverable, [])[:50])
    for discipline in DISCIPLINES:
        write_context_pack(f"discipline_{discipline}", by_discipline.get(discipline, [])[:50])

    best_rows = scored[:80]
    write_context_pack("top_reuse_candidates", best_rows)

    lines = [
        "# Readiness IA / RAG",
        "",
        f"- Generado: {now}",
        f"- Documentos puntuados: {len(scored)}",
        f"- Candidatos score >= 80: {sum(1 for row in scored if row['score'] >= 80)}",
        f"- Candidatos score >= 60: {sum(1 for row in scored if row['score'] >= 60)}",
        f"- OCR prioritario: {len(ocr_rows)}",
        "",
        "## Mejores candidatos reutilizables",
        "",
        "| Score | Documento | Parte | Disciplina | Política |",
        "|---:|---|---|---|---|",
    ]
    for row in scored[:25]:
        title = row["doc_code"] or row["title"] or row["path"]
        lines.append(
            f"| {row['score']} | {title} | {row['deliverable_part']} | {row['discipline']} | {row['send_policy']} |"
        )

    lines.extend(["", "## OCR prioritario", "", "| OCR | Documento | Parte | Disciplina | Tamaño |", "|---:|---|---|---|---|"])
    for row in ocr_rows[:25]:
        title = row["doc_code"] or row["title"] or row["path"]
        lines.append(
            f"| {row['ocr_priority']} | {title} | {row['deliverable_part']} | {row['discipline']} | {row['size_human']} |"
        )

    lines.extend(
        [
            "",
            "## Archivos generados",
            "",
            "- `ai-readiness.csv`: ranking completo con score, política de envío y razones.",
            "- `ocr-priority.csv`: documentos donde el OCR local aportaría más valor.",
            "- `.yeyo-memory/context-packs/*.json`: paquetes prefiltrados por parte del proyecto y disciplina.",
            "",
            "## Sugerencias de mejora siguientes",
            "",
            "1. Añadir embeddings locales para búsqueda semántica sobre los chunks ya filtrados.",
            "2. Crear resúmenes extractivos locales por documento antes de llamar a modelos cloud.",
            "3. OCR selectivo solo de documentos con `ocr_priority` alto.",
            "4. Comparar proyectos propios contra estos context-packs para detectar reutilización real.",
            "5. Añadir un campo de aprobación humana para marcar documentos validados por el equipo.",
        ]
    )
    (REPORTS_DIR / "ai-readiness.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
