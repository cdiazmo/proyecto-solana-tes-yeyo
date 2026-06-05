#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".yeyo-agents"))

from app.custodian import run_next_request  # noqa: E402
from app.db import ensure_paths, init_agent_db  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Ejecuta el agente custodio en modo worker.")
    parser.add_argument("--interval", type=float, default=3.0)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    ensure_paths()
    init_agent_db()
    while True:
        request = run_next_request()
        if request:
            print(f"Procesada petición {request['id']} -> {request['status']}", flush=True)
        elif args.once:
            print("No hay peticiones pendientes.", flush=True)
            return 0
        else:
            time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
