#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".yeyo-agents"))

from app.db import create_user, ensure_paths, init_agent_db  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Crea un usuario/token para Gestión Documental.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--email", default="")
    parser.add_argument("--role", choices=["admin", "curator", "viewer"], default="viewer")
    args = parser.parse_args()

    ensure_paths()
    init_agent_db()
    user = create_user(args.name, args.email, args.role)
    print(f"Usuario: {user['name']}")
    print(f"Rol: {user['role']}")
    print(f"Token: {user['token']}")
    print("Guarda este token: no se puede recuperar después.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
