# Selección de OCR local

## Objetivo

Priorizar OCR local sin enviar documentos a backend.

## Criterios

Procesar primero:

- `ocr_priority >= 80`.
- Pliego, memoria, mediciones o presupuestos.
- PDFs pequeños o medianos.
- Documentos con pocos folios.
- Documentos conectados a índices XLS.

Evitar OCR masivo de:

- Planos ya etiquetados.
- PDFs gigantes.
- DWG/NWD.
- Documentos sin relación con la consulta.

## Salida

| Prioridad OCR | Documento | Motivo | Tamaño | Páginas | Resultado esperado |
|---:|---|---|---|---:|---|
