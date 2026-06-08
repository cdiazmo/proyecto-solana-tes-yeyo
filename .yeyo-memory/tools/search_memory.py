#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import unicodedata
import json
import re
import sqlite3
from pathlib import Path


ROOT = Path.cwd()
DB_PATH = ROOT / ".yeyo-memory" / "sqlite" / "yeyo-memory.sqlite"
REPORTS_DIR = ROOT / ".yeyo-memory" / "reports"


SYNONYMS = {
    "pliego": ["especificacion", "specification", "condiciones", "technical"],
    "presupuesto": ["mto", "medicion", "mediciones", "recuento", "partida"],
    "mediciones": ["mto", "presupuesto", "quantity", "recuento"],
    "memoria": ["anejo", "calculo", "technical note", "nota tecnica"],
    "planos": ["plano", "drawing", "dwg", "layout"],
    "tuberia": ["tuberias", "piping", "pipe"],
    "instrumentacion": ["instrumentation", "control", "ic"],
    "electrica": ["electric", "electrico", "bt", "mt", "15 kv"],
    "civil": ["estructura", "foundation", "cimentacion"],
    "pci": ["incendio", "fire"],
}


def tokens(query: str) -> list[str]:
    return [token for token in re.findall(r"[\wÁÉÍÓÚÜÑáéíóúüñ.-]+", query.lower()) if len(token) > 1]


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text.lower()).strip()


def fts_query(query: str) -> str:
    terms = tokens(query)
    expanded: list[str] = []
    for term in terms:
        expanded.append(term)
        expanded.extend(SYNONYMS.get(term, []))
    if not expanded:
        return query
    return " OR ".join(f'"{term.replace(chr(34), "")}"' for term in expanded[:24])


def load_readiness() -> dict[str, dict[str, str]]:
    path = REPORTS_DIR / "ai-readiness.csv"
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["path"]: row for row in csv.DictReader(handle)}


def query_intent(query: str) -> dict[str, str]:
    terms = set(tokens(query))
    intent: dict[str, str] = {}
    if terms & {"pliego", "condiciones", "especificacion", "specification"}:
        intent["deliverable_part"] = "Pliego de condiciones"
    elif terms & {"presupuesto", "medicion", "mediciones", "mto", "partida"}:
        intent["deliverable_part"] = "Mediciones y presupuestos"
    elif terms & {"memoria", "anejo", "calculo"}:
        intent["deliverable_part"] = "Memoria y anejos"
    elif terms & {"plano", "planos", "isometrico", "layout", "pid"}:
        intent["deliverable_part"] = "Planos"

    if terms & {"tuberia", "tuberias", "htf", "sales", "mecanica", "proceso"}:
        intent["discipline"] = "Proceso / mecanica / tuberias"
    elif terms & {"civil", "estructura", "cimentacion"}:
        intent["discipline"] = "Civil / estructuras"
    elif terms & {"electrica", "electrico", "bt", "mt", "kv"}:
        intent["discipline"] = "Electrica"
    elif terms & {"instrumentacion", "control"}:
        intent["discipline"] = "Instrumentacion y control"
    elif terms & {"pci", "incendio"}:
        intent["discipline"] = "PCI"
    return intent


def score_result(
    row: dict,
    readiness: dict[str, dict[str, str]],
    seen_doc_count: int,
    intent: dict[str, str],
    query_terms: list[str],
    normalized_query: str,
) -> int:
    meta = readiness.get(row.get("path", ""), {})
    score = int(meta.get("score") or 0)
    index_count = int(meta.get("indexed_reference_count") or 0)
    chunks = int(row.get("chunk_count") or 0)
    text_chars = int(row.get("text_chars") or 0)
    score += min(20, index_count * 2)
    score += min(10, chunks // 4)
    if text_chars > 10000:
        score += 5
    if meta.get("send_policy") == "enviar_chunks_prioritarios":
        score += 15
    elif meta.get("send_policy") == "enviar_chunks_si_consulta_relevante":
        score += 8
    if intent.get("deliverable_part"):
        if meta.get("deliverable_part") == intent["deliverable_part"]:
            score += 45
        else:
            score -= 35
            if meta.get("deliverable_part") == "Planos":
                score -= 25
    if intent.get("discipline"):
        if meta.get("discipline") == intent["discipline"]:
            score += 20
        else:
            score -= 8
    searchable_meta = normalize(" ".join(str(row.get(key) or "") for key in ("path", "title", "doc_code", "revision")))
    if normalized_query and normalized_query in searchable_meta:
        score += 60
    meta_hits = sum(1 for term in query_terms if normalize(term) in searchable_meta)
    if meta_hits:
        score += min(70, meta_hits * 14)
        if meta_hits >= max(2, len(query_terms) - 1):
            score += 30
    score -= seen_doc_count * 35
    return score


def metadata_candidates(conn: sqlite3.Connection, query_terms: list[str], normalized_query: str, limit: int) -> list[dict]:
    rows = conn.execute(
        """
        SELECT
            documents.id AS document_id,
            documents.path,
            documents.title,
            documents.doc_code,
            documents.revision,
            documents.card_path,
            documents.status,
            documents.text_chars,
            documents.chunks AS chunk_count
        FROM documents
        """
    ).fetchall()
    candidates: list[dict] = []
    for row in rows:
        data = dict(row)
        searchable_meta = normalize(" ".join(str(data.get(key) or "") for key in ("path", "title", "doc_code", "revision")))
        hits = sum(1 for term in query_terms if normalize(term) in searchable_meta)
        if normalized_query and normalized_query in searchable_meta:
            hits += len(query_terms) + 2
        if hits < max(2, min(4, len(query_terms))):
            continue
        data.update(
            {
                "id": f"{data['document_id']}:meta",
                "snippet": "[coincidencia en metadatos] " + data.get("path", ""),
                "metadata_hits": hits,
            }
        )
        candidates.append(data)
    candidates.sort(key=lambda item: (-int(item["metadata_hits"]), item["path"]))
    return candidates[:limit]


def main() -> int:
    parser = argparse.ArgumentParser(description="Search the local Yeyo document memory.")
    parser.add_argument("query", help="FTS query, for example: heat tracing")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--candidates", type=int, default=80, help="FTS candidates to rank before returning limit.")
    parser.add_argument("--max-per-doc", type=int, default=1, help="Maximum chunks returned per document.")
    parser.add_argument("--json", action="store_true", help="Print JSONL results.")
    args = parser.parse_args()

    readiness = load_readiness()
    intent = query_intent(args.query)
    query_terms = tokens(args.query)
    normalized_query = normalize(args.query)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT
            chunks_fts.id,
            chunks_fts.path,
            snippet(chunks_fts, 2, '[', ']', ' ... ', 28) AS snippet,
            chunks.document_id,
            documents.title,
            documents.doc_code,
            documents.revision,
            documents.card_path,
            documents.status,
            documents.text_chars,
            documents.chunks AS chunk_count
        FROM chunks_fts
        JOIN chunks ON chunks.id = chunks_fts.id
        JOIN documents ON documents.id = chunks.document_id
        WHERE chunks_fts MATCH ?
        LIMIT ?
        """,
        (fts_query(args.query), args.candidates),
    ).fetchall()

    ranked = []
    seen_docs: dict[str, int] = {}
    for row in rows:
        data = dict(row)
        doc_id = data.get("document_id", "")
        rank_score = score_result(data, readiness, seen_docs.get(doc_id, 0), intent, query_terms, normalized_query)
        meta = readiness.get(data.get("path", ""), {})
        data.update(
            {
                "rank_score": rank_score,
                "ai_score": meta.get("score", ""),
                "send_policy": meta.get("send_policy", ""),
                "deliverable_part": meta.get("deliverable_part", ""),
                "discipline": meta.get("discipline", ""),
                "reuse_priority": meta.get("reuse_priority", ""),
                "indexed_reference_count": meta.get("indexed_reference_count", ""),
            }
        )
        ranked.append(data)
        seen_docs[doc_id] = seen_docs.get(doc_id, 0) + 1

    existing_doc_ids = {item.get("document_id") for item in ranked}
    for data in metadata_candidates(conn, query_terms, normalized_query, args.candidates):
        if data.get("document_id") in existing_doc_ids:
            continue
        rank_score = score_result(data, readiness, seen_docs.get(data["document_id"], 0), intent, query_terms, normalized_query)
        meta = readiness.get(data.get("path", ""), {})
        data.update(
            {
                "rank_score": rank_score,
                "ai_score": meta.get("score", ""),
                "send_policy": meta.get("send_policy", ""),
                "deliverable_part": meta.get("deliverable_part", ""),
                "discipline": meta.get("discipline", ""),
                "reuse_priority": meta.get("reuse_priority", ""),
                "indexed_reference_count": meta.get("indexed_reference_count", ""),
            }
        )
        ranked.append(data)
        seen_docs[data["document_id"]] = seen_docs.get(data["document_id"], 0) + 1

    ranked.sort(key=lambda item: (-int(item["rank_score"]), item["path"], item["id"]))

    selected = []
    emitted_per_doc: dict[str, int] = {}
    for data in ranked:
        doc_id = data.get("document_id", "")
        if emitted_per_doc.get(doc_id, 0) >= args.max_per_doc:
            continue
        selected.append(data)
        emitted_per_doc[doc_id] = emitted_per_doc.get(doc_id, 0) + 1
        if len(selected) >= args.limit:
            break

    for data in selected:
        if args.json:
            print(json.dumps(data, ensure_ascii=False))
        else:
            print(f"{data['id']} | score={data['rank_score']} | {data['path']}")
            if data.get("doc_code") or data.get("revision"):
                print(f"  code={data.get('doc_code') or '-'} rev={data.get('revision') or '-'}")
            if data.get("deliverable_part") or data.get("discipline") or data.get("send_policy"):
                print(
                    f"  part={data.get('deliverable_part') or '-'} discipline={data.get('discipline') or '-'} "
                    f"policy={data.get('send_policy') or '-'} ai_score={data.get('ai_score') or '-'}"
                )
            print(f"  {data['snippet']}")
            print(f"  card: {data['card_path']}")
            print()

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
