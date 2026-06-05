from __future__ import annotations

import json
import urllib.error
import urllib.request

from .settings import GEMINI_API_KEY, GEMINI_MODEL


def gemini_available() -> bool:
    return bool(GEMINI_API_KEY)


def ask_gemini(prompt: str, context: str) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY no está configurada")

    instruction = (
        "Eres un asistente de ingeniería experto para el proyecto Solana TES. "
        "Tu tarea es responder a consultas técnicas de forma estructurada, profesional y completa, "
        "usando ÚNICAMENTE el contexto suministrado (el cual contiene un listado de documentos coincidentes "
        "en el catálogo/inventario y extractos/fragmentos de texto relevantes).\n\n"
        "Reglas para tu respuesta:\n"
        "1. Identifica y clasifica los documentos del catálogo/inventario coincidentes con la consulta, "
        "agrupándolos de manera lógica (por ejemplo, por disciplinas como tuberías, civil, mecánica, aislamiento, etc.).\n"
        "2. Si tienes extractos de texto, utilízalos para resumir o detallar el contenido del documento correspondiente, "
        "citando la fuente como [Extracto #N].\n"
        "3. Si un documento aparece en la lista de documentos coincidentes del catálogo pero no tienes extractos de su texto, "
        "menciónalo indicando claramente que está catalogado en el inventario local, pero que no hay extractos de texto disponibles "
        "en el contexto para detallar su contenido.\n"
        "4. Cita siempre las fuentes de manera explícita (por ejemplo: [Doc #N] o [Extracto #N]).\n"
        "5. Estructura tu respuesta con viñetas, títulos y un tono técnico y riguroso."
    )
    body = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            f"{instruction}\n\n"
                            f"Pregunta:\n{prompt}\n\n"
                            f"Contexto recuperado localmente:\n{context}"
                        )
                    }
                ],
            }
        ]
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Error Gemini HTTP {exc.code}: {detail}") from exc

    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    text = "\n".join(part.get("text", "") for part in parts).strip()
    if not text:
        raise RuntimeError("Gemini no devolvió texto")
    return text


def local_extractive_answer(prompt: str, context: str) -> str:
    if not context:
        return "No he encontrado fragmentos relevantes en la memoria local."
    return (
        "Modo local extractivo (sin clave API externa). "
        "A continuación se muestra la información recuperada del inventario local:\n\n"
        f"{context}\n\n"
        "Configure GEMINI_API_KEY para habilitar respuestas redactadas e interpretadas por IA."
    )
