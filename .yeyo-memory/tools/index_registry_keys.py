#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path.cwd()
MEMORY_ROOT = ROOT / ".yeyo-memory"
CARDS_DIR = MEMORY_ROOT / "cards"
REPORTS_DIR = MEMORY_ROOT / "reports"
DB_PATH = MEMORY_ROOT / "sqlite" / "yeyo-memory.sqlite"


@dataclass(frozen=True)
class Hit:
    key: str
    prefix: str
    number: str
    document_id: str
    path: str
    source: str
    field: str
    location: str
    context: str


def make_pattern(prefixes: list[str], min_digits: int, max_digits: int, all_prefixes: bool) -> re.Pattern[str]:
    if all_prefixes:
        escaped = r"[A-Z]{2,8}"
        separator = r"[-_ ]+"
    else:
        escaped = "|".join(re.escape(prefix.upper()) for prefix in prefixes)
        separator = r"[-_ ]?"
    return re.compile(
        rf"(?<![A-Z0-9])(?P<key>(?P<prefix>{escaped}){separator}(?P<number>\d{{{min_digits},{max_digits}}}))(?![A-Z0-9])",
        re.I,
    )


def normalize_key(prefix: str, number: str) -> str:
    return f"{prefix.upper()}-{number}"


def compact(value: object, limit: int = 500) -> str:
    text = str(value or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def context_for(text: str, start: int, end: int, radius: int = 120) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    return compact(text[left:right], limit=2 * radius + 80)


def iter_matches(pattern: re.Pattern[str], text: str) -> Iterable[tuple[str, str, str, int, int]]:
    for match in pattern.finditer(text or ""):
        prefix = match.group("prefix").upper()
        number = match.group("number")
        yield normalize_key(prefix, number), prefix, number, match.start(), match.end()


def load_cards() -> list[dict]:
    cards = []
    for card_path in sorted(CARDS_DIR.glob("*.json")):
        card = json.loads(card_path.read_text(encoding="utf-8"))
        card["_card_file"] = str(card_path.relative_to(ROOT))
        cards.append(card)
    return cards


def card_text_fields(card: dict) -> list[tuple[str, str]]:
    metadata = card.get("metadata") or {}
    fields = [
        ("path", card.get("path") or ""),
        ("title", card.get("title") or ""),
        ("doc_code", card.get("doc_code") or ""),
        ("revision", card.get("revision") or ""),
        ("card_path", card.get("card_path") or ""),
    ]
    for key in ("pdf_metadata", "ai_features", "plan_tag", "ocr"):
        value = metadata.get(key)
        if value:
            fields.append((f"metadata.{key}", json.dumps(value, ensure_ascii=False, sort_keys=True)))
    for index, item in enumerate(metadata.get("index_matches") or []):
        if isinstance(item, dict):
            fields.append((f"metadata.index_matches[{index}]", json.dumps(item, ensure_ascii=False, sort_keys=True)))
    return fields


def scan_cards(pattern: re.Pattern[str], cards: list[dict]) -> list[Hit]:
    hits: list[Hit] = []
    for card in cards:
        for field, text in card_text_fields(card):
            for key, prefix, number, start, end in iter_matches(pattern, text):
                hits.append(
                    Hit(
                        key=key,
                        prefix=prefix,
                        number=number,
                        document_id=card.get("id") or "",
                        path=card.get("path") or "",
                        source="card",
                        field=field,
                        location="",
                        context=context_for(text, start, end),
                    )
                )
    return hits


def scan_extracted(pattern: re.Pattern[str], cards: list[dict]) -> list[Hit]:
    hits: list[Hit] = []
    for card in cards:
        extracted = card.get("extracted_path")
        if not extracted:
            continue
        text_path = ROOT / extracted
        if not text_path.exists():
            continue
        text = text_path.read_text(encoding="utf-8", errors="replace")
        for key, prefix, number, start, end in iter_matches(pattern, text):
            before = text[:start]
            page_matches = list(re.finditer(r"\[page\s+([^\]]+)\]", before, re.I))
            sheet_matches = list(re.finditer(r"\[sheet\s+([^\]]+)\]", before, re.I))
            location = ""
            if page_matches:
                location = f"page {page_matches[-1].group(1)}"
            elif sheet_matches:
                location = f"sheet {sheet_matches[-1].group(1)}"
            hits.append(
                Hit(
                    key=key,
                    prefix=prefix,
                    number=number,
                    document_id=card.get("id") or "",
                    path=card.get("path") or "",
                    source="extracted",
                    field=extracted,
                    location=location,
                    context=context_for(text, start, end),
                )
            )
    return hits


def scan_report_csv(pattern: re.Pattern[str], path: Path, source: str) -> list[Hit]:
    if not path.exists():
        return []
    hits: list[Hit] = []
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        reader = csv.DictReader(handle)
        for row_number, row in enumerate(reader, start=2):
            joined = " | ".join(str(value or "") for value in row.values())
            doc_path = row.get("path") or row.get("matched_path") or row.get("index_path") or ""
            document_id = ""
            card_path = row.get("card_path") or ""
            if card_path:
                try:
                    card = json.loads((ROOT / card_path).read_text(encoding="utf-8"))
                    document_id = card.get("id") or ""
                    doc_path = card.get("path") or doc_path
                except Exception:
                    pass
            for key, prefix, number, start, end in iter_matches(pattern, joined):
                hits.append(
                    Hit(
                        key=key,
                        prefix=prefix,
                        number=number,
                        document_id=document_id,
                        path=doc_path,
                        source=source,
                        field=path.name,
                        location=f"row {row_number}",
                        context=context_for(joined, start, end),
                    )
                )
    return hits


def init_table(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DROP TABLE IF EXISTS registry_keys;
        CREATE TABLE registry_keys (
            key TEXT NOT NULL,
            prefix TEXT NOT NULL,
            number TEXT NOT NULL,
            document_id TEXT,
            path TEXT NOT NULL,
            source TEXT NOT NULL,
            field TEXT NOT NULL,
            location TEXT NOT NULL,
            context TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX idx_registry_keys_key ON registry_keys(key);
        CREATE INDEX idx_registry_keys_prefix ON registry_keys(prefix);
        CREATE INDEX idx_registry_keys_document_id ON registry_keys(document_id);
        CREATE INDEX idx_registry_keys_path ON registry_keys(path);
        """
    )


def write_outputs(hits: list[Hit], prefixes: list[str]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = REPORTS_DIR / "registry-keys.csv"
    columns = ["key", "prefix", "number", "document_id", "path", "source", "field", "location", "context"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for hit in sorted(hits, key=lambda item: (item.key, item.path, item.source, item.location)):
            writer.writerow({column: getattr(hit, column) for column in columns})

    by_prefix = Counter(hit.prefix for hit in hits)
    by_source = Counter(hit.source for hit in hits)
    unique_keys = sorted({hit.key for hit in hits})
    lines = [
        "# Claves de registro indexadas",
        "",
        f"- Generado: {datetime.now(timezone.utc).isoformat()}",
        f"- Prefijos buscados: {', '.join(prefixes)}",
        f"- Ocurrencias: {len(hits)}",
        f"- Claves únicas: {len(unique_keys)}",
        "",
        "## Por prefijo",
        "",
        "| Prefijo | Ocurrencias |",
        "|---|---:|",
        *[f"| {prefix} | {count} |" for prefix, count in by_prefix.most_common()],
        "",
        "## Por fuente",
        "",
        "| Fuente | Ocurrencias |",
        "|---|---:|",
        *[f"| {source} | {count} |" for source, count in by_source.most_common()],
        "",
        "## Primeras claves",
        "",
        ", ".join(unique_keys[:80]) if unique_keys else "Sin claves encontradas con los prefijos configurados.",
        "",
        "Archivo detallado: `registry-keys.csv`.",
    ]
    (REPORTS_DIR / "registry-keys.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Index registry-like keys such as RE-108618.")
    parser.add_argument("--prefix", action="append", default=[], help="Prefix to index. Can be repeated. Default: RE")
    parser.add_argument("--all-prefixes", action="store_true", help="Index any 2-8 letter prefix followed by a separator and a long number.")
    parser.add_argument("--min-digits", type=int, default=4, help="Minimum numeric digits after the prefix. Default: 4")
    parser.add_argument("--max-digits", type=int, default=10, help="Maximum numeric digits after the prefix. Default: 10")
    parser.add_argument("--no-extracted", action="store_true", help="Do not scan extracted text files.")
    parser.add_argument("--no-reports", action="store_true", help="Do not scan document index reports.")
    args = parser.parse_args()

    prefixes = [prefix.upper().strip("-_ ") for prefix in (args.prefix or ["RE"]) if prefix.strip("-_ ")]
    pattern = make_pattern(prefixes, args.min_digits, args.max_digits, args.all_prefixes)
    cards = load_cards()

    hits = []
    hits.extend(scan_cards(pattern, cards))
    if not args.no_extracted:
        hits.extend(scan_extracted(pattern, cards))
    if not args.no_reports:
        hits.extend(scan_report_csv(pattern, REPORTS_DIR / "document-index-entries.csv", "document-index-entry"))
        hits.extend(scan_report_csv(pattern, REPORTS_DIR / "document-index-matches.csv", "document-index-match"))

    # Deduplicate exact repeated rows produced by overlapping metadata/report sources.
    hits = list(dict.fromkeys(hits))
    created_at = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        init_table(conn)
        conn.executemany(
            """
            INSERT INTO registry_keys
            (key, prefix, number, document_id, path, source, field, location, context, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    hit.key,
                    hit.prefix,
                    hit.number,
                    hit.document_id,
                    hit.path,
                    hit.source,
                    hit.field,
                    hit.location,
                    hit.context,
                    created_at,
                )
                for hit in hits
            ],
        )
    write_outputs(hits, ["ANY"] if args.all_prefixes else prefixes)
    print(f"registry_keys indexed occurrences={len(hits)} unique={len({hit.key for hit in hits})}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
