#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


ROOT = Path.cwd()
DB_PATH = ROOT / ".yeyo-memory" / "sqlite" / "yeyo-memory.sqlite"


def main() -> int:
    parser = argparse.ArgumentParser(description="Search indexed registry-like keys.")
    parser.add_argument("query", help="Exact key, prefix, or partial value, e.g. RE-108618 or RE")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    query = args.query.upper().replace("_", "-").strip()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        table = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='registry_keys'"
        ).fetchone()
        if not table:
            raise SystemExit("registry_keys table does not exist. Run .yeyo-memory/tools/index_registry_keys.py first.")
        rows = conn.execute(
            """
            SELECT key, prefix, number, path, source, field, location, context
            FROM registry_keys
            WHERE key = ?
               OR prefix = ?
               OR key LIKE ?
               OR path LIKE ?
               OR context LIKE ?
            ORDER BY key, path, source, location
            LIMIT ?
            """,
            (query, query, f"%{query}%", f"%{query}%", f"%{query}%", args.limit),
        ).fetchall()

    for row in rows:
        data = dict(row)
        if args.json:
            print(json.dumps(data, ensure_ascii=False))
        else:
            print(f"{data['key']} | {data['path']}")
            print(f"  source={data['source']} field={data['field']} location={data['location'] or '-'}")
            if data["context"]:
                print(f"  {data['context']}")
            print()
    if not rows and not args.json:
        print("Sin resultados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
