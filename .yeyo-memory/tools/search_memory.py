#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


ROOT = Path.cwd()
DB_PATH = ROOT / ".yeyo-memory" / "sqlite" / "yeyo-memory.sqlite"


def main() -> int:
    parser = argparse.ArgumentParser(description="Search the local Yeyo document memory.")
    parser.add_argument("query", help="FTS query, for example: heat tracing")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--json", action="store_true", help="Print JSONL results.")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT
            chunks_fts.id,
            chunks_fts.path,
            snippet(chunks_fts, 2, '[', ']', ' ... ', 28) AS snippet,
            documents.title,
            documents.doc_code,
            documents.revision,
            documents.card_path
        FROM chunks_fts
        JOIN chunks ON chunks.id = chunks_fts.id
        JOIN documents ON documents.id = chunks.document_id
        WHERE chunks_fts MATCH ?
        LIMIT ?
        """,
        (args.query, args.limit),
    ).fetchall()

    for row in rows:
        data = dict(row)
        if args.json:
            print(json.dumps(data, ensure_ascii=False))
        else:
            print(f"{data['id']} | {data['path']}")
            if data.get("doc_code") or data.get("revision"):
                print(f"  code={data.get('doc_code') or '-'} rev={data.get('revision') or '-'}")
            print(f"  {data['snippet']}")
            print(f"  card: {data['card_path']}")
            print()

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
