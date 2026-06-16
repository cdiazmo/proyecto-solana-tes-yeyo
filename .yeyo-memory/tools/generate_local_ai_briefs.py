#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import csv
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path.cwd()
MEMORY_ROOT = ROOT / ".yeyo-memory"
REPORTS_DIR = MEMORY_ROOT / "reports"
DEFAULT_OUTPUT_ROOT = MEMORY_ROOT / "local-ai"
READINESS_CSV = REPORTS_DIR / "ai-readiness.csv"

PAGE_MARKER_RE = re.compile(r"(?=^\[(?:page|sheet)\s+[^\]]+\]\s*$)", re.I | re.M)

REUSE_PRIORITY_SCORE = {
    "alta": 4,
    "media_alta": 3,
    "media": 2,
    "baja": 1,
}

FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.I | re.S)
TRAILING_COMMA_RE = re.compile(r",(\s*[}\]])")
BARE_ETC_RE = re.compile(r",\s*etc\.(?=\s*[\]}])", re.I)
SECTION_SPLIT_RE = re.compile(r"(?m)^\d+\.\s+\*\*")


class GatewayUnavailableError(RuntimeError):
    pass


@dataclass
class Candidate:
    doc_id: str
    path: str
    title: str
    doc_code: str
    revision: str
    status: str
    score: int
    send_policy: str
    deliverable_part: str
    discipline: str
    reuse_priority: str
    extracted_path: str
    card_path: str
    text_chars: int
    chunks: int


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_candidates(args: argparse.Namespace) -> list[Candidate]:
    if not READINESS_CSV.exists():
        raise SystemExit(f"No existe {READINESS_CSV}")

    candidates: list[Candidate] = []
    with READINESS_CSV.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            extracted_path = (row.get("extracted_path") or "").strip()
            if not extracted_path:
                continue
            if (row.get("status") or "").strip() != "ok":
                continue
            if int(row.get("score") or 0) < args.min_score:
                continue
            if not args.include_plans and (row.get("deliverable_part") or "").strip().lower() == "planos":
                continue
            if args.top_dir and not (row.get("path") or "").startswith(args.top_dir):
                continue
            if args.path_contains and args.path_contains.lower() not in (row.get("path") or "").lower():
                continue
            text_chars = int(row.get("text_chars") or 0)
            if args.max_text_chars and text_chars > args.max_text_chars:
                continue
            card_path = (row.get("card_path") or "").strip()
            doc_id = Path(card_path).stem if card_path else ""
            if args.doc_id and doc_id != args.doc_id:
                continue
            candidates.append(
                Candidate(
                    doc_id=doc_id,
                    path=(row.get("path") or "").strip(),
                    title=(row.get("title") or "").strip(),
                    doc_code=(row.get("doc_code") or "").strip(),
                    revision=(row.get("revision") or "").strip(),
                    status=(row.get("status") or "").strip(),
                    score=int(row.get("score") or 0),
                    send_policy=(row.get("send_policy") or "").strip(),
                    deliverable_part=(row.get("deliverable_part") or "").strip(),
                    discipline=(row.get("discipline") or "").strip(),
                    reuse_priority=(row.get("reuse_priority") or "").strip(),
                    extracted_path=extracted_path,
                    card_path=card_path,
                    text_chars=text_chars,
                    chunks=int(row.get("chunks") or 0),
                )
            )

    candidates.sort(
        key=lambda item: (
            -item.score,
            -REUSE_PRIORITY_SCORE.get(item.reuse_priority, 0),
            item.text_chars,
            item.path,
        )
    )
    return candidates


def read_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"generated_at": utcnow(), "processed": {}, "failed": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def log_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def error_kind(error_text: str) -> str:
    lowered = (error_text or "").lower()
    if "no se pudo parsear el json devuelto por la ia local" in lowered:
        return "parse_error"
    if "gateway no disponible" in lowered or "502" in lowered or "503" in lowered or "504" in lowered:
        return "gateway_error"
    if "no existe" in lowered:
        return "missing_file"
    return "processing_error"


def cleanup_partial_outputs(output_root: Path, doc_id: str) -> None:
    for path in (
        output_root / "markdown" / f"{doc_id}.md",
        output_root / "summaries" / f"{doc_id}.json",
    ):
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def write_failed_reports(output_root: Path, state: dict[str, Any], max_doc_attempts: int) -> None:
    failed_items: list[dict[str, Any]] = []
    for doc_id, payload in (state.get("failed") or {}).items():
        if not isinstance(payload, dict):
            continue
        attempts = int(payload.get("attempts", 0) or 0)
        failed_items.append(
            {
                "doc_id": doc_id,
                "path": str(payload.get("path") or ""),
                "error": str(payload.get("error") or ""),
                "error_kind": str(payload.get("error_kind") or error_kind(str(payload.get("error") or ""))),
                "failed_at": str(payload.get("failed_at") or ""),
                "model": str(payload.get("model") or ""),
                "attempts": attempts,
                "permanent": attempts >= max_doc_attempts,
            }
        )

    failed_items.sort(key=lambda item: (-int(item["permanent"]), -int(item["attempts"]), item["path"], item["doc_id"]))

    failed_root = output_root / "failed"
    failed_root.mkdir(parents=True, exist_ok=True)

    json_path = failed_root / "failed-documents.json"
    csv_path = failed_root / "failed-documents.csv"
    md_path = failed_root / "failed-documents.md"

    json_path.write_text(json.dumps(failed_items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["doc_id", "path", "error_kind", "error", "attempts", "permanent", "failed_at", "model"],
        )
        writer.writeheader()
        writer.writerows(failed_items)

    lines = [
        "# Documentos fallidos",
        "",
        f"- Total: {len(failed_items)}",
        f"- Definitivos (>= {max_doc_attempts} intentos): {sum(1 for item in failed_items if item['permanent'])}",
        "",
    ]
    if failed_items:
        lines.extend(
            [
                "| Estado | Intentos | doc_id | Ruta | Tipo | Error |",
                "|---|---:|---|---|---|---|",
            ]
        )
        for item in failed_items:
            status = "definitivo" if item["permanent"] else "pendiente"
            path = str(item["path"]).replace("|", "/")
            err = str(item["error"]).replace("|", "/")
            lines.append(
                f"| {status} | {item['attempts']} | {item['doc_id']} | {path} | {item['error_kind']} | {err} |"
            )
    else:
        lines.append("Sin documentos fallidos.")
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")


def normalize_extracted_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_sections(text: str) -> list[str]:
    parts = [part.strip() for part in PAGE_MARKER_RE.split(text) if part.strip()]
    return parts or [text]


def pack_sections(sections: list[str], chunk_chars: int, max_chunks: int) -> list[str]:
    packed: list[str] = []
    current: list[str] = []
    current_len = 0

    for section in sections:
        section_len = len(section)
        if section_len > chunk_chars:
            if current:
                packed.append("\n\n".join(current))
                current = []
                current_len = 0
            for start in range(0, section_len, chunk_chars):
                packed.append(section[start:start + chunk_chars].strip())
            continue
        if current and current_len + section_len + 2 > chunk_chars:
            packed.append("\n\n".join(current))
            current = []
            current_len = 0
        current.append(section)
        current_len += section_len + 2

    if current:
        packed.append("\n\n".join(current))

    if max_chunks <= 0 or len(packed) <= max_chunks:
        return packed
    return packed


def extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    if not text:
        raise ValueError("La IA local no devolvió contenido")
    fence_match = FENCE_RE.search(text)
    if fence_match:
        text = fence_match.group(1).strip()
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    repaired = normalize_json_candidate(text)
    try:
        data = json.loads(repaired)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    if start == -1:
        raise ValueError("No se encontró un objeto JSON en la respuesta")
    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start : index + 1]
                candidate = normalize_json_candidate(candidate)
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    try:
                        data = ast.literal_eval(candidate)
                        if isinstance(data, dict):
                            return data
                    except (SyntaxError, ValueError):
                        pass
    raise ValueError("No se pudo parsear el JSON devuelto por la IA local")


def repair_unescaped_inner_quotes(text: str) -> str:
    out: list[str] = []
    in_string = False
    escape = False

    def next_non_ws(index: int) -> str:
        for pos in range(index + 1, len(text)):
            if not text[pos].isspace():
                return text[pos]
        return ""

    for index, char in enumerate(text):
        if in_string:
            if escape:
                out.append(char)
                escape = False
                continue
            if char == "\\":
                out.append(char)
                escape = True
                continue
            if char == '"':
                follower = next_non_ws(index)
                if follower in {",", "}", "]", ":"} or follower == "":
                    out.append(char)
                    in_string = False
                else:
                    out.append('\\"')
                continue
            out.append(char)
            continue
        out.append(char)
        if char == '"':
            in_string = True
    return "".join(out)


def normalize_json_candidate(text: str) -> str:
    repaired = (
        text.replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2018", "'")
        .replace("\u2019", "'")
    )
    repaired = BARE_ETC_RE.sub("", repaired)
    repaired = TRAILING_COMMA_RE.sub(r"\1", repaired)
    repaired = repair_unescaped_inner_quotes(repaired)
    return repaired


def _extract_fenced_markdown(text: str) -> str:
    matches = re.findall(r"```markdown\s*(.*?)```", text, re.I | re.S)
    if matches:
        return matches[-1].strip()
    start_match = re.search(r"```markdown\s*", text, re.I)
    if start_match:
        return text[start_match.end() :].strip()
    return ""


def _section_text(text: str, label_patterns: list[str]) -> str:
    for pattern in label_patterns:
        match = re.search(pattern, text, re.I | re.S)
        if not match:
            continue
        start = match.end()
        tail = text[start:]
        split = SECTION_SPLIT_RE.search(tail)
        return (tail[: split.start()] if split else tail).strip()
    return ""


def _extract_list_items(section_text: str) -> list[str]:
    items: list[str] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        bullet_match = re.match(r"^(?:[-*]|\d+\.)\s+(.*)$", stripped)
        if bullet_match:
            item = bullet_match.group(1).strip()
            item = re.sub(r"^\*\((?:Check|Note).*?\)\*$", "", item).strip()
            if item and not item.lower().startswith("need ") and "`" not in item:
                items.append(item)
    return items


def extract_structured_fallback(text: str, expected_keys: list[str]) -> dict[str, Any] | None:
    markdown = _extract_fenced_markdown(text)
    if not markdown and "markdown" in expected_keys:
        markdown_section = _section_text(
            text,
            [
                r"Construct [`']?markdown[`']?.*?:",
                r"Draft Markdown:.*?",
            ],
        )
        if markdown_section:
            markdown = markdown_section.strip()

    summary_points = _extract_list_items(
        _section_text(
            text,
            [
                r"Extract Summary Points.*?:",
                r"Summary Points.*?:",
            ],
        )
    )
    references = _extract_list_items(
        _section_text(
            text,
            [
                r"Extract References.*?:",
                r"References.*?:",
            ],
        )
    )
    warnings = _extract_list_items(
        _section_text(
            text,
            [
                r"Extract Warnings.*?:",
                r"Warnings.*?:",
            ],
        )
    )
    keywords = _extract_list_items(
        _section_text(
            text,
            [
                r"Extract Keywords.*?:",
                r"Keywords.*?:",
            ],
        )
    )
    summary = ""
    if not summary_points:
        summary_section = _section_text(text, [r"Summary.*?:"])
        if summary_section and len(summary_section) < 1200:
            summary = summary_section.splitlines()[0].strip()

    data: dict[str, Any] = {}
    if "markdown" in expected_keys:
        data["markdown"] = markdown
    if "summary_points" in expected_keys:
        data["summary_points"] = summary_points
    if "summary" in expected_keys:
        data["summary"] = summary
    if "references" in expected_keys:
        data["references"] = references
    if "warnings" in expected_keys:
        data["warnings"] = warnings
    if "keywords" in expected_keys:
        data["keywords"] = keywords

    populated = 0
    for key, value in data.items():
        if isinstance(value, list) and value:
            populated += 1
        elif isinstance(value, str) and value.strip():
            populated += 1
    markdown_ok = bool(markdown.strip()) and len(markdown.strip()) >= 200
    if markdown_ok:
        return data
    return data if populated >= 2 else None


def wait_for_gateway(health_url: str, max_wait_seconds: int, poll_seconds: float) -> bool:
    deadline = time.time() + max_wait_seconds
    while time.time() < deadline:
        try:
            request = urllib.request.Request(health_url, method="GET")
            with urllib.request.urlopen(request, timeout=10) as response:
                if 200 <= response.status < 300:
                    return True
        except Exception:
            pass
        time.sleep(poll_seconds)
    return False


def post_local_ai(
    api_url: str,
    auth_token: str,
    body: dict[str, Any],
    timeout: int,
    retries: int,
    *,
    health_url: str,
    gateway_recovery_wait: int,
    gateway_poll_seconds: float,
) -> dict[str, Any]:
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}",
    }
    last_error: Exception | None = None
    saw_gateway_error = False
    for attempt in range(1, retries + 1):
        request = urllib.request.Request(api_url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code in {502, 503, 504}:
                saw_gateway_error = True
                recovered = wait_for_gateway(health_url, gateway_recovery_wait, gateway_poll_seconds)
                if recovered:
                    continue
                raise GatewayUnavailableError(f"Gateway no disponible tras esperar {gateway_recovery_wait}s") from exc
            if attempt < retries:
                time.sleep(min(2 * attempt, 5))
        except urllib.error.URLError as exc:
            last_error = exc
            saw_gateway_error = True
            recovered = wait_for_gateway(health_url, gateway_recovery_wait, gateway_poll_seconds)
            if recovered:
                continue
            raise GatewayUnavailableError(f"Gateway no disponible tras esperar {gateway_recovery_wait}s") from exc
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < retries:
                time.sleep(min(2 * attempt, 5))
    assert last_error is not None
    if saw_gateway_error:
        raise GatewayUnavailableError("La gateway devolvió errores 502/503/504 de forma repetida") from last_error
    raise last_error


def model_text(response: dict[str, Any]) -> str:
    parts = response.get("content") or []
    texts = []
    for part in parts:
        if isinstance(part, dict) and part.get("type") == "text":
            texts.append(part.get("text", ""))
    text = "\n".join(part for part in texts if part).strip()
    if not text:
        raise ValueError("La respuesta de la IA local no contiene texto")
    return text


def repair_json_prompt(model: str, raw_text: str, expected_keys: list[str]) -> dict[str, Any]:
    system = (
        "Eres un reparador de salidas JSON. "
        "Tu única tarea es convertir una respuesta defectuosa en un objeto JSON válido. "
        "No inventes datos que no estén ya presentes. Si falta un campo, usa cadena vacía o lista vacía."
    )
    keys_text = ", ".join(expected_keys)
    user = (
        "Devuelve SOLO un objeto JSON válido.\n"
        f"Claves requeridas: {keys_text}\n"
        "- No uses markdown.\n"
        "- No uses bloques ```.\n"
        "- No añadas explicación.\n"
        "- Conserva el contenido útil existente.\n\n"
        "Respuesta defectuosa a reparar:\n"
        f"{raw_text}"
    )
    return {
        "model": model,
        "max_tokens": 4000,
        "temperature": 0,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }


def expected_keys_for_mode(single_chunk: bool) -> list[str]:
    if single_chunk:
        return ["markdown", "summary", "keywords", "references", "warnings"]
    return ["markdown", "summary_points", "references", "warnings"]


def expected_keys_for_final() -> list[str]:
    return ["summary", "keywords", "references", "warnings"]


def ensure_keys(data: dict[str, Any], expected_keys: list[str]) -> dict[str, Any]:
    normalized = dict(data)
    for key in expected_keys:
        if key not in normalized:
            normalized[key] = [] if key in {"keywords", "references", "warnings", "summary_points"} else ""
    return normalized


def parse_ai_json(
    raw_text: str,
    *,
    api_url: str,
    auth_token: str,
    repair_model: str,
    expected_keys: list[str],
    timeout: int,
    retries: int,
    health_url: str,
    gateway_recovery_wait: int,
    gateway_poll_seconds: float,
) -> tuple[dict[str, Any], bool]:
    try:
        return ensure_keys(extract_json_object(raw_text), expected_keys), False
    except ValueError:
        fallback_data = extract_structured_fallback(raw_text, expected_keys)
        if fallback_data:
            return ensure_keys(fallback_data, expected_keys), False
        repair_response = post_local_ai(
            api_url,
            auth_token,
            repair_json_prompt(repair_model, raw_text, expected_keys),
            timeout=timeout,
            retries=retries,
            health_url=health_url,
            gateway_recovery_wait=gateway_recovery_wait,
            gateway_poll_seconds=gateway_poll_seconds,
        )
        repaired_text = model_text(repair_response)
        repaired_data = ensure_keys(extract_json_object(repaired_text), expected_keys)
        usage = repair_response.get("usage") or {}
        repaired_data["_repair_usage"] = {
            "input_tokens": int(usage.get("input_tokens", 0)),
            "output_tokens": int(usage.get("output_tokens", 0)),
            "calls": 1,
        }
        return repaired_data, True


def parse_existing_raw_text(raw_text: str, expected_keys: list[str]) -> dict[str, Any] | None:
    try:
        return ensure_keys(extract_json_object(raw_text), expected_keys)
    except ValueError:
        fallback_data = extract_structured_fallback(raw_text, expected_keys)
        if fallback_data:
            return ensure_keys(fallback_data, expected_keys)
    return None


def choose_model(args: argparse.Namespace, candidate: Candidate) -> str:
    if args.model_policy == "single":
        return args.model
    if candidate.text_chars <= args.small_doc_chars:
        return args.small_model
    return args.large_model


def single_doc_prompt(model: str, candidate: Candidate, chunk_text: str) -> dict[str, Any]:
    system = (
        "Eres un trabajador local de estructuración documental. "
        "Tu tarea es transformar texto extraído de documentos técnicos en artefactos compactos para búsqueda. "
        "No inventes hechos, números, títulos, revisiones, tablas ni conclusiones. "
        "Si el texto es ambiguo u OCR defectuoso, indícalo en warnings. "
        "No muestres thinking, razonamiento interno, borradores ni análisis paso a paso. "
        "Emite solo la respuesta final."
    )
    user = (
        "Devuelve SOLO un objeto JSON válido con estas claves exactas:\n"
        "{\n"
        '  "markdown": string,\n'
        '  "summary": string,\n'
        '  "keywords": string[],\n'
        '  "references": string[],\n'
        '  "warnings": string[]\n'
        "}\n\n"
        "Reglas:\n"
        "- `markdown`: versión estructurada y fiel del texto, en markdown limpio.\n"
        "- `summary`: resumen técnico breve, útil para búsqueda y recuperación.\n"
        "- `keywords`: máximo 15 términos.\n"
        "- `references`: códigos documentales, equipos, tags, revisiones, normas o claves visibles.\n"
        "- `warnings`: OCR dudoso, tablas rotas, texto incompleto, etc.\n"
        "- No uses bloques ```json ni texto fuera del JSON.\n\n"
        f"Metadatos del documento:\n"
        f"- path: {candidate.path}\n"
        f"- title: {candidate.title or '-'}\n"
        f"- doc_code: {candidate.doc_code or '-'}\n"
        f"- revision: {candidate.revision or '-'}\n"
        f"- deliverable_part: {candidate.deliverable_part or '-'}\n"
        f"- discipline: {candidate.discipline or '-'}\n\n"
        "Texto extraído:\n"
        f"{chunk_text}"
    )
    return {
        "model": model,
        "max_tokens": 4000,
        "temperature": 0,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }


def chunk_prompt(model: str, candidate: Candidate, chunk_index: int, chunk_total: int, chunk_text: str) -> dict[str, Any]:
    system = (
        "Eres un trabajador local de estructuración documental. "
        "Convierte texto técnico extraído a markdown fiel y extrae hechos breves para un resumen posterior. "
        "No inventes contenido. "
        "No muestres thinking, razonamiento interno, borradores ni análisis paso a paso. "
        "Emite solo la respuesta final."
    )
    user = (
        "Devuelve SOLO un objeto JSON válido con estas claves exactas:\n"
        "{\n"
        '  "markdown": string,\n'
        '  "summary_points": string[],\n'
        '  "references": string[],\n'
        '  "warnings": string[]\n'
        "}\n\n"
        "Reglas:\n"
        "- `markdown`: versión markdown fiel del fragmento.\n"
        "- `summary_points`: entre 3 y 10 puntos breves y factuales.\n"
        "- `references`: códigos, tags, equipos, revisiones, normas o claves visibles.\n"
        "- `warnings`: problemas de OCR o fragmento confuso.\n"
        "- No uses bloques ```json ni texto fuera del JSON.\n\n"
        f"Documento: {candidate.path}\n"
        f"Fragmento: {chunk_index}/{chunk_total}\n\n"
        "Texto extraído:\n"
        f"{chunk_text}"
    )
    return {
        "model": model,
        "max_tokens": 2600,
        "temperature": 0,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }


def final_summary_prompt(model: str, candidate: Candidate, chunk_points: list[list[str]], references: list[str], warnings: list[str]) -> dict[str, Any]:
    system = (
        "Eres un trabajador local de síntesis documental. "
        "Resume el documento a partir de puntos factuales ya extraídos, sin inventar contenido. "
        "No muestres thinking, razonamiento interno, borradores ni análisis paso a paso. "
        "Emite solo la respuesta final."
    )
    points_text = "\n".join(
        f"Fragmento {index + 1}:\n" + "\n".join(f"- {point}" for point in points)
        for index, points in enumerate(chunk_points)
    )
    refs_text = ", ".join(references[:40]) if references else "-"
    warnings_text = "\n".join(f"- {item}" for item in warnings[:20]) if warnings else "-"
    user = (
        "Devuelve SOLO un objeto JSON válido con estas claves exactas:\n"
        "{\n"
        '  "summary": string,\n'
        '  "keywords": string[],\n'
        '  "references": string[],\n'
        '  "warnings": string[]\n'
        "}\n\n"
        "Reglas:\n"
        "- `summary`: resumen técnico breve, denso y útil para búsqueda.\n"
        "- `keywords`: máximo 20 términos.\n"
        "- `references`: máximo 20 referencias deduplicadas.\n"
        "- `warnings`: deduplicadas y compactas.\n"
        "- No uses bloques ```json ni texto fuera del JSON.\n\n"
        f"Documento: {candidate.path}\n"
        f"Título: {candidate.title or '-'}\n"
        f"Código: {candidate.doc_code or '-'}\n"
        f"Revisión: {candidate.revision or '-'}\n"
        f"Parte: {candidate.deliverable_part or '-'}\n"
        f"Disciplina: {candidate.discipline or '-'}\n\n"
        "Puntos factuales:\n"
        f"{points_text}\n\n"
        f"Referencias visibles: {refs_text}\n\n"
        f"Warnings previos:\n{warnings_text}"
    )
    return {
        "model": model,
        "max_tokens": 1500,
        "temperature": 0,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }


def dedupe_keep_order(values: list[str], limit: int) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        cleaned = re.sub(r"\s+", " ", str(value or "")).strip()
        if not cleaned:
            continue
        key = cleaned.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(cleaned)
        if len(out) >= limit:
            break
    return out


def summary_from_points(summary_points: list[str], limit: int = 12) -> str:
    points = dedupe_keep_order(summary_points, limit)
    if not points:
        return ""
    return "\n".join(f"- {point}" for point in points)


def render_markdown(
    candidate: Candidate,
    markdown_body: str,
    summary: str,
    warnings: list[str],
    chunk_count: int,
    *,
    completed_chunks: int | None = None,
    total_chunks: int | None = None,
) -> str:
    frontmatter = [
        "---",
        f'doc_id: "{candidate.doc_id}"',
        f'path: "{candidate.path.replace(chr(34), chr(39))}"',
        f'title: "{(candidate.title or "").replace(chr(34), chr(39))}"',
        f'doc_code: "{(candidate.doc_code or "").replace(chr(34), chr(39))}"',
        f'revision: "{(candidate.revision or "").replace(chr(34), chr(39))}"',
        f'discipline: "{(candidate.discipline or "").replace(chr(34), chr(39))}"',
        f'deliverable_part: "{(candidate.deliverable_part or "").replace(chr(34), chr(39))}"',
        f"chunk_count: {chunk_count}",
        f"completed_chunks: {completed_chunks if completed_chunks is not None else chunk_count}",
        f"total_chunks: {total_chunks if total_chunks is not None else chunk_count}",
        "---",
        "",
    ]
    body = [
        f"# {candidate.title or candidate.doc_code or candidate.path}",
        "",
        "## Resumen",
        "",
        summary or "Sin resumen generado.",
        "",
    ]
    if warnings:
        body.extend(["## Observaciones", ""])
        body.extend([f"- {item}" for item in warnings])
        body.append("")
    body.extend(["## Markdown estructurado", "", markdown_body.strip(), ""])
    return "\n".join(frontmatter + body).strip() + "\n"


def write_progress_outputs(
    *,
    markdown_path: Path,
    summary_path: Path,
    candidate: Candidate,
    markdown_parts: list[str],
    summary_points: list[str],
    references: list[str],
    keywords: list[str],
    warnings: list[str],
    usage: dict[str, Any],
    repaired_calls: int,
    selected_model: str,
    text_chars: int,
    total_chunks: int,
    completed_chunks: int,
    completed: bool,
) -> None:
    summary = summary_from_points(summary_points)
    markdown_body = "\n\n".join(part for part in markdown_parts if part.strip()).strip()
    markdown_path.write_text(
        render_markdown(
            candidate,
            markdown_body,
            summary,
            warnings,
            total_chunks,
            completed_chunks=completed_chunks,
            total_chunks=total_chunks,
        ),
        encoding="utf-8",
    )
    summary_payload = {
        "doc_id": candidate.doc_id,
        "path": candidate.path,
        "title": candidate.title,
        "doc_code": candidate.doc_code,
        "revision": candidate.revision,
        "discipline": candidate.discipline,
        "deliverable_part": candidate.deliverable_part,
        "summary": summary,
        "summary_points": dedupe_keep_order(summary_points, 40),
        "keywords": dedupe_keep_order(keywords, 20),
        "references": dedupe_keep_order(references, 40),
        "warnings": dedupe_keep_order(warnings, 20),
        "markdown_path": str(markdown_path.relative_to(ROOT)),
        "source_extracted_path": candidate.extracted_path,
        "model": selected_model,
        "generated_at": utcnow(),
        "usage": usage,
        "repaired_calls": repaired_calls,
        "chunk_count": total_chunks,
        "completed_chunks": completed_chunks,
        "completed": completed,
        "text_chars": text_chars,
    }
    summary_path.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def process_candidate(candidate: Candidate, args: argparse.Namespace, output_root: Path) -> dict[str, Any]:
    extracted_path = ROOT / candidate.extracted_path
    if not extracted_path.exists():
        raise FileNotFoundError(f"No existe {extracted_path}")

    text = normalize_extracted_text(extracted_path.read_text(encoding="utf-8", errors="replace"))
    sections = split_sections(text)
    packed_chunks = pack_sections(sections, args.chunk_chars, args.max_chunks_per_doc)
    packed_chunks = [chunk for chunk in packed_chunks if chunk.strip()]
    if not packed_chunks:
        raise ValueError("No hay texto útil para enviar a la IA local")

    selected_model = choose_model(args, candidate)
    markdown_dir = output_root / "markdown"
    summary_dir = output_root / "summaries"
    markdown_dir.mkdir(parents=True, exist_ok=True)
    summary_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = markdown_dir / f"{candidate.doc_id}.md"
    summary_path = summary_dir / f"{candidate.doc_id}.json"

    markdown_parts: list[str] = []
    references: list[str] = []
    warnings: list[str] = []
    keywords: list[str] = []
    summary_points_flat: list[str] = []
    summary = ""
    usage = {"input_tokens": 0, "output_tokens": 0, "calls": 0}
    repaired_calls = 0
    raw_dir = output_root / "raw-responses"
    raw_dir.mkdir(parents=True, exist_ok=True)

    if len(packed_chunks) == 1:
        raw_path = raw_dir / f"{candidate.doc_id}.single.txt"
        if raw_path.exists():
            data = parse_existing_raw_text(raw_path.read_text(encoding="utf-8"), expected_keys_for_mode(True))
            if data:
                markdown_parts.append(str(data.get("markdown") or "").strip())
                summary = str(data.get("summary") or "").strip()
                summary_points_flat.append(summary)
                references.extend(data.get("references") or [])
                keywords.extend(data.get("keywords") or [])
                warnings.extend(data.get("warnings") or [])
                write_progress_outputs(
                    markdown_path=markdown_path,
                    summary_path=summary_path,
                    candidate=candidate,
                    markdown_parts=markdown_parts,
                    summary_points=summary_points_flat,
                    references=references,
                    keywords=keywords,
                    warnings=warnings,
                    usage=usage,
                    repaired_calls=repaired_calls,
                    selected_model=selected_model,
                    text_chars=len(text),
                    total_chunks=1,
                    completed_chunks=1,
                    completed=True,
                )
                return json.loads(summary_path.read_text(encoding="utf-8"))
    else:
        recovered_chunks = 0
        for index in range(1, len(packed_chunks) + 1):
            raw_path = raw_dir / f"{candidate.doc_id}.chunk-{index}.txt"
            if not raw_path.exists():
                break
            data = parse_existing_raw_text(
                raw_path.read_text(encoding="utf-8"),
                expected_keys_for_mode(False),
            )
            if not data:
                break
            markdown_parts.append(str(data.get("markdown") or "").strip())
            summary_points_flat.extend(
                [str(item).strip() for item in (data.get("summary_points") or []) if str(item).strip()]
            )
            references.extend(data.get("references") or [])
            warnings.extend(data.get("warnings") or [])
            recovered_chunks = index

        if recovered_chunks:
            write_progress_outputs(
                markdown_path=markdown_path,
                summary_path=summary_path,
                candidate=candidate,
                markdown_parts=markdown_parts,
                summary_points=summary_points_flat,
                references=references,
                keywords=dedupe_keep_order(references, 20),
                warnings=warnings,
                usage=usage,
                repaired_calls=repaired_calls,
                selected_model=selected_model,
                text_chars=len(text),
                total_chunks=len(packed_chunks),
                completed_chunks=recovered_chunks,
                completed=recovered_chunks == len(packed_chunks),
            )
            if recovered_chunks == len(packed_chunks):
                return json.loads(summary_path.read_text(encoding="utf-8"))

    if len(packed_chunks) == 1:
        response = post_local_ai(
            args.api_url,
            args.auth_token,
            single_doc_prompt(selected_model, candidate, packed_chunks[0]),
            timeout=args.timeout,
            retries=args.retries,
            health_url=args.gateway_health_url,
            gateway_recovery_wait=args.gateway_recovery_wait,
            gateway_poll_seconds=args.gateway_poll_seconds,
        )
        usage["calls"] += 1
        usage["input_tokens"] += int(response.get("usage", {}).get("input_tokens", 0))
        usage["output_tokens"] += int(response.get("usage", {}).get("output_tokens", 0))
        raw_text = model_text(response)
        (raw_dir / f"{candidate.doc_id}.single.txt").write_text(raw_text, encoding="utf-8")
        data, repaired = parse_ai_json(
            raw_text,
            api_url=args.api_url,
            auth_token=args.auth_token,
            repair_model=args.repair_model,
            expected_keys=expected_keys_for_mode(True),
            timeout=args.timeout,
            retries=args.retries,
            health_url=args.gateway_health_url,
            gateway_recovery_wait=args.gateway_recovery_wait,
            gateway_poll_seconds=args.gateway_poll_seconds,
        )
        if repaired:
            repaired_calls += 1
            repair_usage = data.pop("_repair_usage", {})
            usage["calls"] += int(repair_usage.get("calls", 0))
            usage["input_tokens"] += int(repair_usage.get("input_tokens", 0))
            usage["output_tokens"] += int(repair_usage.get("output_tokens", 0))
        markdown_parts.append(str(data.get("markdown") or "").strip())
        summary = str(data.get("summary") or "").strip()
        summary_points_flat.append(summary)
        references.extend(data.get("references") or [])
        keywords.extend(data.get("keywords") or [])
        warnings.extend(data.get("warnings") or [])
        write_progress_outputs(
            markdown_path=markdown_path,
            summary_path=summary_path,
            candidate=candidate,
            markdown_parts=markdown_parts,
            summary_points=summary_points_flat,
            references=references,
            keywords=keywords,
            warnings=warnings,
            usage=usage,
            repaired_calls=repaired_calls,
            selected_model=selected_model,
            text_chars=len(text),
            total_chunks=len(packed_chunks),
            completed_chunks=1,
            completed=True,
        )
    else:
        for index, chunk_text in enumerate(packed_chunks[recovered_chunks:], start=recovered_chunks + 1):
            response = post_local_ai(
                args.api_url,
                args.auth_token,
                chunk_prompt(selected_model, candidate, index, len(packed_chunks), chunk_text),
                timeout=args.timeout,
                retries=args.retries,
                health_url=args.gateway_health_url,
                gateway_recovery_wait=args.gateway_recovery_wait,
                gateway_poll_seconds=args.gateway_poll_seconds,
            )
            usage["calls"] += 1
            usage["input_tokens"] += int(response.get("usage", {}).get("input_tokens", 0))
            usage["output_tokens"] += int(response.get("usage", {}).get("output_tokens", 0))
            raw_text = model_text(response)
            (raw_dir / f"{candidate.doc_id}.chunk-{index}.txt").write_text(raw_text, encoding="utf-8")
            data, repaired = parse_ai_json(
                raw_text,
                api_url=args.api_url,
                auth_token=args.auth_token,
                repair_model=args.repair_model,
                expected_keys=expected_keys_for_mode(False),
                timeout=args.timeout,
                retries=args.retries,
                health_url=args.gateway_health_url,
                gateway_recovery_wait=args.gateway_recovery_wait,
                gateway_poll_seconds=args.gateway_poll_seconds,
            )
            if repaired:
                repaired_calls += 1
                repair_usage = data.pop("_repair_usage", {})
                usage["calls"] += int(repair_usage.get("calls", 0))
                usage["input_tokens"] += int(repair_usage.get("input_tokens", 0))
                usage["output_tokens"] += int(repair_usage.get("output_tokens", 0))
            markdown_parts.append(str(data.get("markdown") or "").strip())
            summary_points_flat.extend(
                [str(item).strip() for item in (data.get("summary_points") or []) if str(item).strip()]
            )
            references.extend(data.get("references") or [])
            warnings.extend(data.get("warnings") or [])
            write_progress_outputs(
                markdown_path=markdown_path,
                summary_path=summary_path,
                candidate=candidate,
                markdown_parts=markdown_parts,
                summary_points=summary_points_flat,
                references=references,
                keywords=keywords,
                warnings=warnings,
                usage=usage,
                repaired_calls=repaired_calls,
                selected_model=selected_model,
                text_chars=len(text),
                total_chunks=len(packed_chunks),
                completed_chunks=index,
                completed=index == len(packed_chunks),
            )

        summary = summary_from_points(summary_points_flat)
        keywords.extend(dedupe_keep_order(references, 20))

    references = dedupe_keep_order(references, 40)
    keywords = dedupe_keep_order(keywords, 20)
    warnings = dedupe_keep_order(warnings, 20)
    markdown_body = "\n\n".join(part for part in markdown_parts if part.strip()).strip()

    write_progress_outputs(
        markdown_path=markdown_path,
        summary_path=summary_path,
        candidate=candidate,
        markdown_parts=markdown_parts,
        summary_points=summary_points_flat,
        references=references,
        keywords=keywords,
        warnings=warnings,
        usage=usage,
        repaired_calls=repaired_calls,
        selected_model=selected_model,
        text_chars=len(text),
        total_chunks=len(packed_chunks),
        completed_chunks=len(packed_chunks),
        completed=True,
    )

    summary_payload = {
        "doc_id": candidate.doc_id,
        "path": candidate.path,
        "title": candidate.title,
        "doc_code": candidate.doc_code,
        "revision": candidate.revision,
        "discipline": candidate.discipline,
        "deliverable_part": candidate.deliverable_part,
        "summary": summary or summary_from_points(summary_points_flat),
        "summary_points": dedupe_keep_order(summary_points_flat, 40),
        "keywords": keywords,
        "references": references,
        "warnings": warnings,
        "markdown_path": str(markdown_path.relative_to(ROOT)),
        "source_extracted_path": candidate.extracted_path,
        "model": selected_model,
        "generated_at": utcnow(),
        "usage": usage,
        "repaired_calls": repaired_calls,
        "chunk_count": len(packed_chunks),
        "completed_chunks": len(packed_chunks),
        "completed": True,
        "text_chars": len(text),
    }
    summary_path.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary_payload


def rebuild_index(output_root: Path, state: dict[str, Any]) -> None:
    index_path = output_root / "index.jsonl"
    summary_paths = sorted(
        {
            entry.get("summary_path")
            for entry in state.get("processed", {}).values()
            if isinstance(entry, dict) and entry.get("summary_path")
        }
    )
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("w", encoding="utf-8") as handle:
        for rel_path in summary_paths:
            summary_file = ROOT / rel_path
            if not summary_file.exists():
                continue
            payload = json.loads(summary_file.read_text(encoding="utf-8"))
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def acquire_lock(lock_path: Path) -> None:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"pid": os.getpid(), "started_at": utcnow(), "cwd": str(ROOT)}
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        try:
            existing = json.loads(lock_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            existing = {}
        existing_pid = int(existing.get("pid") or 0)
        if existing_pid > 0:
            try:
                os.kill(existing_pid, 0)
            except OSError:
                release_lock(lock_path)
                return acquire_lock(lock_path)
        raise SystemExit(f"Ya existe un lock activo en {lock_path}") from exc
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def release_lock(lock_path: Path) -> None:
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate local-AI markdown and summaries from extracted documents.")
    parser.add_argument("--api-url", default="http://127.0.0.1:8318/v1/messages")
    parser.add_argument("--gateway-health-url", default="http://127.0.0.1:8318/healthz")
    parser.add_argument("--gateway-recovery-wait", type=int, default=1800)
    parser.add_argument("--gateway-poll-seconds", type=float, default=15.0)
    parser.add_argument("--auth-token", default="local")
    parser.add_argument("--model", default="claude-local-qwen35b-mlx")
    parser.add_argument("--model-policy", choices=("single", "size"), default="size")
    parser.add_argument("--small-model", default="claude-local-coder7b")
    parser.add_argument("--large-model", default="claude-local-qwen35b-mlx")
    parser.add_argument("--repair-model", default="claude-local-coder7b")
    parser.add_argument("--small-doc-chars", type=int, default=12000)
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--limit", type=int, default=0, help="0 = procesar todos los candidatos elegibles")
    parser.add_argument("--min-score", type=int, default=80)
    parser.add_argument("--top-dir")
    parser.add_argument("--path-contains")
    parser.add_argument("--doc-id")
    parser.add_argument("--max-text-chars", type=int, default=0, help="0 = sin límite")
    parser.add_argument("--include-plans", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--max-doc-attempts", type=int, default=3)
    parser.add_argument("--max-consecutive-failures", type=int, default=25)
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument("--chunk-chars", type=int, default=12000)
    parser.add_argument("--max-chunks-per-doc", type=int, default=8)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--retries", type=int, default=2)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    output_root = ROOT / args.output_root
    state_path = output_root / "state.json"
    lock_path = output_root / "run.lock"
    events_path = output_root / "events.jsonl"

    acquire_lock(lock_path)
    try:
        state = read_state(state_path)
        state.setdefault("processed", {})
        state.setdefault("failed", {})

        candidates = load_candidates(args)
        processed_count = 0
        skipped_existing = 0
        skipped_failed = 0
        consecutive_failures = 0
        limit = args.limit if args.limit > 0 else len(candidates)

        log_event(
            events_path,
            {
                "ts": utcnow(),
                "event": "run_started",
                "candidate_count": len(candidates),
                "limit": args.limit,
                "model_policy": args.model_policy,
            },
        )

        for candidate in candidates:
            if processed_count >= limit:
                break
            if not args.force and candidate.doc_id in state["processed"]:
                skipped_existing += 1
                continue
            if not args.retry_failed and not args.force and candidate.doc_id in state["failed"]:
                skipped_failed += 1
                continue
            failure_meta = state["failed"].get(candidate.doc_id, {})
            if not args.force and int(failure_meta.get("attempts", 0) or 0) >= args.max_doc_attempts:
                skipped_failed += 1
                continue

            started_at = time.time()
            try:
                summary_payload = process_candidate(candidate, args, output_root)
                state["processed"][candidate.doc_id] = {
                    "path": candidate.path,
                    "summary_path": str((output_root / "summaries" / f"{candidate.doc_id}.json").relative_to(ROOT)),
                    "markdown_path": str((output_root / "markdown" / f"{candidate.doc_id}.md").relative_to(ROOT)),
                    "generated_at": summary_payload["generated_at"],
                    "model": summary_payload["model"],
                }
                state["failed"].pop(candidate.doc_id, None)
                write_state(state_path, state)
                rebuild_index(output_root, state)
                write_failed_reports(output_root, state, args.max_doc_attempts)
                processed_count += 1
                consecutive_failures = 0
                elapsed = round(time.time() - started_at, 2)
                print(
                    f"processed doc_id={candidate.doc_id} chunks={summary_payload['chunk_count']} "
                    f"calls={summary_payload['usage']['calls']} model={summary_payload['model']} "
                    f"elapsed_s={elapsed} path={candidate.path}"
                , flush=True)
                log_event(
                    events_path,
                    {
                        "ts": utcnow(),
                        "event": "processed",
                        "doc_id": candidate.doc_id,
                        "path": candidate.path,
                        "model": summary_payload["model"],
                        "elapsed_s": elapsed,
                        "usage": summary_payload["usage"],
                    },
                )
            except GatewayUnavailableError as exc:
                elapsed = round(time.time() - started_at, 2)
                log_event(
                    events_path,
                    {
                        "ts": utcnow(),
                        "event": "gateway_unavailable",
                        "doc_id": candidate.doc_id,
                        "path": candidate.path,
                        "elapsed_s": elapsed,
                        "error": f"{type(exc).__name__}: {exc}",
                    },
                )
                print(f"gateway_unavailable doc_id={candidate.doc_id} elapsed_s={elapsed} error={exc}", flush=True)
                break
            except Exception as exc:  # noqa: BLE001
                consecutive_failures += 1
                elapsed = round(time.time() - started_at, 2)
                error_text = f"{type(exc).__name__}: {exc}"
                cleanup_partial_outputs(output_root, candidate.doc_id)
                previous_attempts = int(failure_meta.get("attempts", 0) or 0)
                new_attempts = previous_attempts + 1
                kind = error_kind(error_text)
                state["failed"][candidate.doc_id] = {
                    "path": candidate.path,
                    "error": error_text,
                    "error_kind": kind,
                    "failed_at": utcnow(),
                    "model": choose_model(args, candidate),
                    "attempts": new_attempts,
                    "permanent": new_attempts >= args.max_doc_attempts,
                }
                write_state(state_path, state)
                write_failed_reports(output_root, state, args.max_doc_attempts)
                log_event(
                    events_path,
                    {
                        "ts": utcnow(),
                        "event": "failed",
                        "doc_id": candidate.doc_id,
                        "path": candidate.path,
                        "elapsed_s": elapsed,
                        "error": error_text,
                        "error_kind": kind,
                        "attempts": new_attempts,
                        "permanent": new_attempts >= args.max_doc_attempts,
                    },
                )
                print(f"failed doc_id={candidate.doc_id} elapsed_s={elapsed} error={error_text}", flush=True)
                if new_attempts >= args.max_doc_attempts:
                    log_event(
                        events_path,
                        {
                            "ts": utcnow(),
                            "event": "failed_permanent",
                            "doc_id": candidate.doc_id,
                            "path": candidate.path,
                            "error_kind": kind,
                            "attempts": new_attempts,
                        },
                    )
                if consecutive_failures >= args.max_consecutive_failures:
                    print(f"stopping: consecutive_failures={consecutive_failures}", flush=True)
                    break

            if args.sleep_seconds > 0:
                time.sleep(args.sleep_seconds)

        state["last_run"] = {
            "finished_at": utcnow(),
            "processed": processed_count,
            "skipped_existing": skipped_existing,
            "skipped_failed": skipped_failed,
            "failed_total": len(state.get("failed", {})),
        }
        write_state(state_path, state)
        rebuild_index(output_root, state)
        write_failed_reports(output_root, state, args.max_doc_attempts)
        log_event(
            events_path,
            {
                "ts": utcnow(),
                "event": "run_finished",
                "processed": processed_count,
                "skipped_existing": skipped_existing,
                "skipped_failed": skipped_failed,
                "failed_total": len(state.get("failed", {})),
            },
        )
        print(
            f"done processed={processed_count} skipped_existing={skipped_existing} "
            f"skipped_failed={skipped_failed} failed_total={len(state.get('failed', {}))} "
            f"output_root={output_root.relative_to(ROOT)} model_policy={args.model_policy}"
        , flush=True)
        return 0
    finally:
        release_lock(lock_path)


if __name__ == "__main__":
    raise SystemExit(main())
