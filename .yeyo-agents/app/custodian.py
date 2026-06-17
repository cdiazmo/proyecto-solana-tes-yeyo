from __future__ import annotations

import json
import re
from typing import Any

from .db import agent_conn, audit, utcnow
from .llm_google import ask_gemini, gemini_available, local_extractive_answer
from .retrieval import build_context, search_documents


def enqueue_request(requester_id: int, kind: str, prompt: str, payload: dict[str, Any] | None = None, priority: int = 50) -> int:
    now = utcnow()
    with agent_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO requests (requester_id, kind, prompt, status, priority, payload_json, created_at, updated_at)
            VALUES (?, ?, ?, 'queued', ?, ?, ?, ?)
            """,
            (requester_id, kind, prompt, priority, json.dumps(payload or {}, ensure_ascii=False), now, now),
        )
        request_id = int(cur.lastrowid)
    audit(requester_id, "request.enqueue", "request", str(request_id), json.dumps({"kind": kind}, ensure_ascii=False))
    return request_id


def list_requests(limit: int = 50) -> list[dict[str, Any]]:
    with agent_conn() as conn:
        rows = conn.execute(
            """
            SELECT requests.*, users.name AS requester_name
            FROM requests
            JOIN users ON users.id = requests.requester_id
            ORDER BY requests.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    result = []
    for row in rows:
        data = dict(row)
        data["payload"] = json.loads(data.pop("payload_json") or "{}")
        data["result"] = json.loads(data.pop("result_json") or "null")
        result.append(data)
    return result


def get_request(request_id: int) -> dict[str, Any] | None:
    with agent_conn() as conn:
        row = conn.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
    if not row:
        return None
    data = dict(row)
    data["payload"] = json.loads(data.pop("payload_json") or "{}")
    data["result"] = json.loads(data.pop("result_json") or "null")
    return data


import threading

CUSTODIAN_LOCK = threading.Lock()


DOC_CITATION_RE = re.compile(r"Doc\s*#\s*(\d+)", re.I)
EXTRACT_CITATION_RE = re.compile(r"Extracto\s*#\s*(\d+)", re.I)


def append_cited_reference_map(answer: str, documents: list[dict[str, Any]], chunks: list[dict[str, Any]]) -> str:
    doc_nums = sorted({int(match.group(1)) for match in DOC_CITATION_RE.finditer(answer)})
    extract_nums = sorted({int(match.group(1)) for match in EXTRACT_CITATION_RE.finditer(answer)})
    if not doc_nums and not extract_nums:
        return answer

    lines: list[str] = []
    if doc_nums:
        lines.extend(["", "### Documentos citados", ""])
        for num in doc_nums:
            if num < 1 or num > len(documents):
                lines.append(f"- [Doc #{num}]: no disponible en el resultado devuelto.")
                continue
            doc = documents[num - 1]
            ref = doc.get("doc_code") or doc.get("title") or doc.get("path") or f"Documento {num}"
            lines.append(f"- [Doc #{num}]: {ref} — `{doc.get('path') or '-'}`")

    if extract_nums:
        lines.extend(["", "### Extractos citados", ""])
        for num in extract_nums:
            if num < 1 or num > len(chunks):
                lines.append(f"- [Extracto #{num}]: no disponible en el resultado devuelto.")
                continue
            chunk = chunks[num - 1]
            ref = chunk.get("doc_code") or chunk.get("title") or chunk.get("path") or f"Extracto {num}"
            loc = ""
            if chunk.get("page"):
                loc = f" pág./hoja {chunk.get('page')}"
                if chunk.get("line"):
                    loc += f", línea {chunk.get('line')}"
            lines.append(f"- [Extracto #{num}]: {ref}{loc} — `{chunk.get('path') or '-'}`")

    return answer.rstrip() + "\n" + "\n".join(lines)


def run_next_request(custodian_id: int | None = None) -> dict[str, Any] | None:
    with CUSTODIAN_LOCK:
        request_id = None
        with agent_conn() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                row = conn.execute(
                    """
                    SELECT id FROM requests
                    WHERE status = 'queued'
                    ORDER BY priority ASC, created_at ASC
                    LIMIT 1
                    """
                ).fetchone()
                if row:
                    request_id = int(row["id"])
                    conn.execute(
                        "UPDATE requests SET status = 'running', updated_at = ? WHERE id = ?",
                        (utcnow(), request_id),
                    )
                    conn.commit()
                else:
                    conn.rollback()
                    return None
            except Exception:
                conn.rollback()
                raise

        # Retrieve the request row details under a new connection
        with agent_conn() as conn:
            row = conn.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
            row_dict = dict(row)

        try:
            result = execute_request(row_dict)
            status = "done"
            error = None
        except Exception as exc:
            result = None
            status = "failed"
            error = str(exc)

        with agent_conn() as conn:
            conn.execute(
                """
                UPDATE requests
                SET status = ?, result_json = ?, error = ?, updated_at = ?
                WHERE id = ?
                """,
                (status, json.dumps(result, ensure_ascii=False) if result is not None else None, error, utcnow(), request_id),
            )
        audit(custodian_id, f"request.{status}", "request", str(request_id))
        return get_request(request_id)


def execute_request(row: dict[str, Any]) -> dict[str, Any]:
    kind = row["kind"]
    prompt = row["prompt"]
    if kind == "query":
        chunks, matched_docs, context = build_context(prompt)
        answer = ask_gemini(prompt, context) if gemini_available() else local_extractive_answer(prompt, context)
        answer = append_cited_reference_map(answer, matched_docs, chunks)
        return {
            "answer": answer,
            "model": "gemini" if gemini_available() else "local-extractive",
            "sources": [
                {
                    "chunk_id": c["id"],
                    "document_id": c["document_id"],
                    "path": c["path"],
                    "title": c.get("title"),
                    "doc_code": c.get("doc_code"),
                    "revision": c.get("revision"),
                    "card_path": c.get("card_path"),
                    "page": c.get("page"),
                    "line": c.get("line"),
                }
                for c in chunks
            ],
            "documents": [
                {
                    "id": d["id"],
                    "path": d["path"],
                    "title": d.get("title"),
                    "doc_code": d.get("doc_code"),
                    "status": d.get("status"),
                }
                for d in matched_docs
            ],
        }
    if kind == "find_documents":
        return {"documents": search_documents(prompt, limit=50)}
    raise ValueError(f"Tipo de petición no soportado: {kind}")
