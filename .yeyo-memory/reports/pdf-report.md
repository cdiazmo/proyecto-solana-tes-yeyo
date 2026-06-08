# Informe de PDFs

- Generado: 2026-06-08T18:41:31.012009+00:00
- PDFs catalogados: 1.791
- PDFs legibles localmente: 929 (51.9%)
- PDFs que requieren OCR o no contienen texto útil: 198 (11.1%)
- PDFs con error real: 0 (0.0%)
- PDFs con código documental inferido: 990 (55.3%)
- Información textual extraída: 30.069.966 caracteres, 19.387 chunks, ~7.517.157 tokens estimados

## Legibilidad por estado

| Estado | PDFs | Legibles | Requiere OCR | Errores | Texto extraído | Chunks |
|---|---:|---:|---:|---:|---:|---:|
| ok | 929 | 929 | 0 | 0 | 30.069.966 | 19.387 |
| tagged_plan | 656 | 0 | 0 | 0 | 0 | 0 |
| needs_ocr_or_empty | 198 | 0 | 198 | 0 | 0 | 0 |
| metadata_only | 8 | 0 | 0 | 0 | 0 | 0 |

## Tipos documentales principales

| Tipo | PDFs | Legibles | Legibilidad | Requiere OCR | Texto extraído | Chunks |
|---|---:|---:|---:|---:|---:|---:|
| Otros / sin clasificar | 336 | 121 | 36.0% | 176 | 10.806.415 | 6.879 |
| Calculo | 84 | 84 | 100.0% | 0 | 7.126.838 | 4.553 |
| Especificacion tecnica | 173 | 170 | 98.3% | 3 | 4.433.093 | 2.865 |
| Plano / dibujo | 973 | 367 | 37.7% | 5 | 3.623.120 | 2.437 |
| Procedimiento / manual | 50 | 48 | 96.0% | 1 | 1.616.453 | 1.039 |
| Isometrico | 31 | 15 | 48.4% | 0 | 701.440 | 450 |
| Listado / registro | 59 | 49 | 83.1% | 10 | 549.247 | 367 |
| Memoria / nota tecnica | 24 | 23 | 95.8% | 1 | 493.130 | 322 |

## Información por temática

| Temática | PDFs | Legibles | Legibilidad | Requiere OCR | Texto extraído | Chunks |
|---|---:|---:|---:|---:|---:|---:|
| General / otros | 385 | 144 | 37.4% | 168 | 13.492.324 | 8.594 |
| Proceso y mecanica | 328 | 262 | 79.9% | 20 | 4.538.284 | 2.984 |
| Tuberias e isometricos | 634 | 273 | 43.1% | 2 | 3.526.813 | 2.325 |
| Instrumentacion y control | 91 | 86 | 94.5% | 0 | 3.343.624 | 2.148 |
| Civil y estructuras | 261 | 99 | 37.9% | 0 | 3.136.104 | 2.021 |
| Fabricacion y compras | 24 | 20 | 83.3% | 3 | 882.909 | 567 |
| Permisos y documentacion oficial | 37 | 27 | 73.0% | 0 | 843.860 | 547 |
| Especificaciones tecnicas | 25 | 13 | 52.0% | 5 | 183.572 | 121 |

## Lectura rápida

- `pdf-catalog.csv`: ficha de cada PDF con código, tipo, temática, legibilidad y volumen de información.
- `pdf-type-summary.csv`: resumen agregado por tipo documental.
- `pdf-topic-summary.csv`: resumen agregado por temática.
- `pdf-status-summary.csv`: resumen agregado por estado técnico.

Nota: la clasificación es heurística, basada en ruta, nombre, código documental y metadatos ya extraídos. Es suficiente para priorizar y reducir tokens; puede refinarse cuando empecemos a redactar la memoria final.
