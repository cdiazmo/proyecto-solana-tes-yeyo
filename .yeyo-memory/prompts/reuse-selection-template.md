# Selección de documentación reutilizable

## Objetivo

Seleccionar documentación candidata para reutilización en un proyecto nuevo.

## Criterios de ranking

Priorizar:

- `reuse_priority = alta` o `media_alta`.
- `ai_score >= 70`.
- `send_policy = enviar_chunks_prioritarios`.
- Documentos con `indexed_reference_count > 0`.
- Documentos de las partes principales:
  - Memoria y anejos.
  - Pliego de condiciones.
  - Mediciones y presupuestos.
  - Planos, solo si están etiquetados o tienen PDF legible.

Penalizar:

- `needs_ocr_or_empty` sin OCR.
- `metadata_only`, salvo que venga de índice XLS.
- DWG/NWD sin PDF equivalente.
- Archivos comprimidos no inspeccionados.

## Salida

| Prioridad | Documento | Parte | Disciplina | Evidencia | Acción siguiente |
|---|---|---|---|---|---|

Después añade una lista corta de riesgos y huecos.
