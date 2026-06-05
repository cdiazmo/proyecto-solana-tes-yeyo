from __future__ import annotations

import os
from pathlib import Path


def _root() -> Path:
    configured = os.getenv("YEYO_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


ROOT = _root()
MEMORY_ROOT = ROOT / ".yeyo-memory"
DOCUMENT_DB = Path(os.getenv("YEYO_DOCUMENT_DB", MEMORY_ROOT / "sqlite" / "yeyo-memory.sqlite"))
AGENT_DB = Path(os.getenv("YEYO_AGENT_DB", ROOT / ".yeyo-agents" / "data" / "agents.sqlite"))
STATIC_DIR = ROOT / ".yeyo-agents" / "app" / "static"

MAX_CONTEXT_CHUNKS = int(os.getenv("YEYO_MAX_CONTEXT_CHUNKS", "8"))
MAX_CONTEXT_CHARS = int(os.getenv("YEYO_MAX_CONTEXT_CHARS", "14000"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

APP_NAME = os.getenv("YEYO_APP_NAME", "Gestión Documental")
YEYO_ADMIN_TOKEN = os.getenv("YEYO_ADMIN_TOKEN", "yeyo_admin_token")
