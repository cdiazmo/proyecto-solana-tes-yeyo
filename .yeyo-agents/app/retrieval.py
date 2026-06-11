from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

from .db import document_conn
from .settings import MAX_CONTEXT_CHARS, MAX_CONTEXT_CHUNKS


import re
import sqlite3
import unicodedata
from typing import Any

from .db import document_conn
from .settings import MAX_CONTEXT_CHARS, MAX_CONTEXT_CHUNKS


TOKEN_RE = re.compile(r"[\wÁÉÍÓÚÜÑáéíóúüñ.-]+", re.UNICODE)
REGISTRY_KEY_RE = re.compile(r"(?<![A-Z0-9])([A-Z]{1,6})[-_ ]?(\d{4,10})(?![A-Z0-9])", re.I)


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))


def extract_keywords(query: str) -> list[str]:
    terms = TOKEN_RE.findall(query.lower())
    stop_words = {
        "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "en", "para", "por", "con",
        "que", "qué", "como", "cómo", "sobre", "y", "o", "a", "al", "documento", "documentos",
        "hablan", "habla", "este", "esta", "estos", "estas", "busca", "buscar", "quien", "quién",
        "me", "mi", "mis", "te", "tu", "tus", "su", "sus", "nos", "os", "les"
    }
    cleaned = [term.replace('"', "") for term in terms if len(term) > 1 and term not in stop_words]
    if not cleaned:
        cleaned = [term.replace('"', "") for term in terms if len(term) > 1]
    
    # Expand keywords to include both accented and unaccented versions
    expanded = []
    for term in cleaned:
        expanded.append(term)
        stripped = strip_accents(term)
        if stripped != term:
            expanded.append(stripped)
    return list(dict.fromkeys(expanded))


def _fts_query(query: str) -> str:
    kws = extract_keywords(query)
    if not kws:
        return query
    return " OR ".join(f'"{kw}"' for kw in kws[:16])


def search_chunks(query: str, limit: int = 12) -> list[dict[str, Any]]:
    fts = _fts_query(query)
    with document_conn() as conn:
        try:
            rows = conn.execute(
                """
                SELECT
                    chunks_fts.id,
                    chunks.document_id,
                    chunks_fts.path,
                    snippet(chunks_fts, 2, '[', ']', ' ... ', 28) AS snippet,
                    chunks.text,
                    documents.title,
                    documents.doc_code,
                    documents.revision,
                    documents.ext,
                    documents.status,
                    documents.card_path,
                    documents.extracted_path
                FROM chunks_fts
                JOIN chunks ON chunks.id = chunks_fts.id
                JOIN documents ON documents.id = chunks.document_id
                WHERE chunks_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (fts, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            like = f"%{query}%"
            rows = conn.execute(
                """
                SELECT
                    chunks.id,
                    chunks.document_id,
                    chunks.path,
                    substr(chunks.text, 1, 360) AS snippet,
                    chunks.text,
                    documents.title,
                    documents.doc_code,
                    documents.revision,
                    documents.ext,
                    documents.status,
                    documents.card_path,
                    documents.extracted_path
                FROM chunks
                JOIN documents ON documents.id = chunks.document_id
                WHERE chunks.text LIKE ? OR chunks.path LIKE ?
                LIMIT ?
                """,
                (like, like, limit),
            ).fetchall()
    return [dict(row) for row in rows]


def search_documents(query: str, limit: int = 20) -> list[dict[str, Any]]:
    kws = extract_keywords(query)
    if not kws:
        # Fallback to simple query if no keywords extracted
        like = f"%{query}%"
        with document_conn() as conn:
            rows = conn.execute(
                """
                SELECT id, path, top_dir, ext, size_human, title, doc_code, revision,
                       status, text_chars, chunks, token_estimate, card_path, extracted_path,
                       1 AS score
                FROM documents
                WHERE path LIKE ? OR title LIKE ? OR doc_code LIKE ?
                ORDER BY text_chars DESC
                LIMIT ?
                """,
                (like, like, like, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    conditions = []
    params = []
    score_exprs = []
    for kw in kws:
        like_pattern = f"%{kw}%"
        conditions.append("(path LIKE ? OR title LIKE ? OR doc_code LIKE ?)")
        params.extend([like_pattern, like_pattern, like_pattern])
        score_exprs.append("CASE WHEN path LIKE ? OR title LIKE ? OR doc_code LIKE ? THEN 1 ELSE 0 END")
        params.extend([like_pattern, like_pattern, like_pattern])
        
    where_clause = " OR ".join(conditions)
    score_clause = " + ".join(score_exprs)
    params.append(limit)
    
    query_str = f"""
        SELECT id, path, top_dir, ext, size_human, title, doc_code, revision,
               status, text_chars, chunks, token_estimate, card_path, extracted_path,
               ({score_clause}) AS score
        FROM documents
        WHERE {where_clause}
        ORDER BY score DESC, text_chars DESC
        LIMIT ?
    """
    with document_conn() as conn:
        rows = conn.execute(query_str, params).fetchall()
    return [dict(row) for row in rows]


def normalize_registry_key(value: str) -> str:
    match = REGISTRY_KEY_RE.search(value.upper())
    if not match:
        return value.upper().strip()
    return f"{match.group(1).upper()}-{match.group(2)}"


def search_registry_keys(query: str, limit: int = 20) -> list[dict[str, Any]]:
    normalized = normalize_registry_key(query)
    key_tokens = [f"{match.group(1).upper()}-{match.group(2)}" for match in REGISTRY_KEY_RE.finditer(query)]
    raw_terms = TOKEN_RE.findall(query)
    prefix_terms = [term for term in raw_terms if re.fullmatch(r"[A-Z]{2,8}", term)]
    if not key_tokens and not prefix_terms:
        return []
    where_parts = []
    params: list[str | int] = []
    for key in key_tokens:
        where_parts.extend(["key = ?", "key LIKE ?"])
        params.extend([key, f"%{key}%"])
    for prefix in prefix_terms[:4]:
        where_parts.append("prefix = ?")
        params.append(prefix)
    params.append(limit)
    with document_conn() as conn:
        table = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='registry_keys'"
        ).fetchone()
        if not table:
            return []
        rows = conn.execute(
            f"""
            SELECT key, prefix, number, path, source, field, location, context
            FROM registry_keys
            WHERE {" OR ".join(where_parts)}
            ORDER BY key, path, source, location
            LIMIT ?
            """,
            params,
        ).fetchall()
    return [dict(row) for row in rows]


def get_chunk_location(doc_id: str, chunk_text: str) -> tuple[str | None, int | None]:
    try:
        extracted_file = Path(".yeyo-memory/extracted") / f"{doc_id}.txt"
        if not extracted_file.exists():
            return None, None
        doc_text = extracted_file.read_text(encoding="utf-8")
        pos = doc_text.find(chunk_text)
        if pos == -1:
            return None, None
            
        before_text = doc_text[:pos]
        # Search backwards for [page X]
        page_matches = list(re.finditer(r"\[page\s+(\d+)\]", before_text))
        page_num = page_matches[-1].group(1) if page_matches else None
        
        # If no page matches, check sheet matches for Excel files
        if not page_num:
            sheet_matches = list(re.finditer(r"\[sheet\s+([^\]]+)\]", before_text))
            page_num = sheet_matches[-1].group(1) if sheet_matches else None
            
        # Line number calculation
        if page_matches:
            last_page_pos = page_matches[-1].end()
            line_in_page = doc_text[last_page_pos:pos].count("\n") + 1
        elif sheet_matches:
            last_sheet_pos = sheet_matches[-1].end()
            line_in_page = doc_text[last_sheet_pos:pos].count("\n") + 1
        else:
            line_in_page = before_text.count("\n") + 1
            
        return page_num, line_in_page
    except Exception as e:
        print(f"Error finding page and line: {e}", file=sys.stderr)
        return None, None


def build_context(query: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    kws = extract_keywords(query)
    # Search top matching documents in the catalog
    matched_docs = search_documents(query, limit=25)
    # Search relevant chunks
    chunks = search_chunks(query, limit=MAX_CONTEXT_CHUNKS)
    registry_hits = search_registry_keys(query, limit=20)
    
    parts: list[str] = []
    
    if matched_docs:
        parts.append("### DOCUMENTOS COINCIDENTES EN EL INVENTARIO/CATÁLOGO:")
        for idx, doc in enumerate(matched_docs, start=1):
            ref = doc.get("doc_code") or doc.get("title") or doc["path"]
            parts.append(
                f"Doc #{idx}: {ref}\n"
                f"Ruta: {doc['path']}\n"
                f"Título: {doc.get('title') or '-'}\n"
                f"Código: {doc.get('doc_code') or '-'}\n"
                f"Estado en BD: {doc['status']}"
            )
        parts.append("---")

    if registry_hits:
        parts.append("### CLAVES DE REGISTRO COINCIDENTES:")
        for idx, hit in enumerate(registry_hits, start=1):
            parts.append(
                f"Clave #{idx}: {hit['key']}\n"
                f"Ruta: {hit['path']}\n"
                f"Fuente: {hit['source']} / {hit['field']} / {hit.get('location') or '-'}\n"
                f"Contexto: {hit.get('context') or '-'}"
            )
        parts.append("---")
        
    if chunks:
        parts.append("### EXTRACTOS Y FRAGMENTOS DE TEXTO RELEVANTES ENCONTRADOS EN LA MEMORIA:")
        total = 0
        for index, chunk in enumerate(chunks, start=1):
            text = chunk["text"].strip()
            if not text:
                continue
            remaining = MAX_CONTEXT_CHARS - total
            if remaining <= 0:
                break
            text = text[:remaining]
            total += len(text)
            
            # Find page and line for this chunk
            page, line = get_chunk_location(chunk["document_id"], chunk["text"])
            chunk["page"] = page
            chunk["line"] = line
            
            ref = chunk.get("doc_code") or chunk.get("title") or chunk["path"]
            loc_str = ""
            if page:
                loc_str = f" (Pág./Hoja: {page}, Lín: {line})"
            parts.append(
                f"Extracto #{index}{loc_str} (fuente: {ref})\n"
                f"Ruta: {chunk['path']}\n"
                f"{text}"
            )
            
    return chunks, matched_docs, "\n\n".join(parts)


def inventory_stats() -> dict[str, Any]:
    with document_conn() as conn:
        totals = dict(
            conn.execute(
                """
                SELECT COUNT(*) AS documents,
                       SUM(size_bytes) AS size_bytes,
                       SUM(text_chars) AS text_chars,
                       SUM(chunks) AS chunks,
                       SUM(token_estimate) AS token_estimate
                FROM documents
                """
            ).fetchone()
        )
        by_ext = [dict(row) for row in conn.execute(
            "SELECT ext, COUNT(*) AS n FROM documents GROUP BY ext ORDER BY n DESC LIMIT 20"
        )]
        by_status = [dict(row) for row in conn.execute(
            "SELECT status, COUNT(*) AS n FROM documents GROUP BY status ORDER BY n DESC"
        )]
    totals["by_ext"] = by_ext
    totals["by_status"] = by_status
    return totals
