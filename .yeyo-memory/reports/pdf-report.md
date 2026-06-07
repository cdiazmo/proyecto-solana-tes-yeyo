# Informe de PDFs

- Generado: 2026-06-05T11:35:24.255461+00:00
- PDFs catalogados: 1.409
- PDFs legibles localmente: 793 (56.3%)
- PDFs que requieren OCR o no contienen texto útil: 29 (2.1%)
- PDFs con error real: 0 (0.0%)
- PDFs con código documental inferido: 930 (66.0%)
- Información textual extraída: 17.734.122 caracteres, 11.525 chunks, ~4.433.249 tokens estimados

## Legibilidad por estado

| Estado | PDFs | Legibles | Requiere OCR | Errores | Texto extraído | Chunks |
|---|---:|---:|---:|---:|---:|---:|
| ok | 793 | 793 | 0 | 0 | 17.734.122 | 11.525 |
| tagged_plan | 587 | 0 | 0 | 0 | 0 | 0 |
| needs_ocr_or_empty | 29 | 0 | 29 | 0 | 0 | 0 |

## Tipos documentales principales

| Tipo | PDFs | Legibles | Legibilidad | Requiere OCR | Texto extraído | Chunks |
|---|---:|---:|---:|---:|---:|---:|
| Calculo | 76 | 76 | 100.0% | 0 | 6.938.491 | 4.430 |
| Especificacion tecnica | 173 | 170 | 98.3% | 3 | 4.433.093 | 2.865 |
| Plano / dibujo | 901 | 342 | 38.0% | 0 | 1.922.477 | 1.342 |
| Procedimiento / manual | 50 | 48 | 96.0% | 1 | 1.616.453 | 1.039 |
| Isometrico | 31 | 15 | 48.4% | 0 | 701.440 | 450 |
| Otros / sin clasificar | 59 | 32 | 54.2% | 23 | 527.129 | 347 |
| Listado / registro | 39 | 38 | 97.4% | 1 | 474.713 | 315 |
| Memoria / nota tecnica | 20 | 20 | 100.0% | 0 | 400.096 | 262 |

## Información por temática

| Temática | PDFs | Legibles | Legibilidad | Requiere OCR | Texto extraído | Chunks |
|---|---:|---:|---:|---:|---:|---:|
| Proceso y mecanica | 303 | 238 | 78.5% | 20 | 4.425.597 | 2.896 |
| Tuberias e isometricos | 627 | 267 | 42.6% | 2 | 3.328.117 | 2.199 |
| Instrumentacion y control | 90 | 85 | 94.4% | 0 | 3.319.965 | 2.133 |
| Civil y estructuras | 229 | 90 | 39.3% | 0 | 2.997.309 | 1.929 |
| General / otros | 71 | 48 | 67.6% | 1 | 1.630.317 | 1.053 |
| Fabricacion y compras | 23 | 20 | 87.0% | 2 | 882.909 | 567 |
| Permisos y documentacion oficial | 37 | 27 | 73.0% | 0 | 843.860 | 547 |
| Especificaciones tecnicas | 24 | 13 | 54.2% | 4 | 183.572 | 121 |

## Lectura rápida

- `pdf-catalog.csv`: ficha de cada PDF con código, tipo, temática, legibilidad y volumen de información.
- `pdf-type-summary.csv`: resumen agregado por tipo documental.
- `pdf-topic-summary.csv`: resumen agregado por temática.
- `pdf-status-summary.csv`: resumen agregado por estado técnico.

Nota: la clasificación es heurística, basada en ruta, nombre, código documental y metadatos ya extraídos. Es suficiente para priorizar y reducir tokens; puede refinarse cuando empecemos a redactar la memoria final.
