# Informe de PDFs

- Generado: 2026-06-08T20:00:48.674371+00:00
- PDFs catalogados: 1.791
- PDFs legibles localmente: 1.067 (59.6%)
- PDFs que requieren OCR o no contienen texto útil: 27 (1.5%)
- PDFs con error real: 0 (0.0%)
- PDFs con código documental inferido: 990 (55.3%)
- Información textual extraída: 31.003.257 caracteres, 20.036 chunks, ~7.750.433 tokens estimados

## Legibilidad por estado

| Estado | PDFs | Legibles | Requiere OCR | Errores | Texto extraído | Chunks |
|---|---:|---:|---:|---:|---:|---:|
| ok | 1067 | 1067 | 0 | 0 | 31.003.257 | 20.036 |
| tagged_plan | 689 | 0 | 0 | 0 | 0 | 0 |
| needs_ocr_or_empty | 27 | 0 | 27 | 0 | 0 | 0 |
| metadata_only | 8 | 0 | 0 | 0 | 0 | 0 |

## Tipos documentales principales

| Tipo | PDFs | Legibles | Legibilidad | Requiere OCR | Texto extraído | Chunks |
|---|---:|---:|---:|---:|---:|---:|
| Otros / sin clasificar | 336 | 246 | 73.2% | 24 | 11.590.053 | 7.426 |
| Calculo | 84 | 84 | 100.0% | 0 | 7.126.838 | 4.553 |
| Especificacion tecnica | 173 | 171 | 98.8% | 2 | 4.450.258 | 2.876 |
| Plano / dibujo | 973 | 367 | 37.7% | 0 | 3.623.120 | 2.437 |
| Procedimiento / manual | 50 | 49 | 98.0% | 0 | 1.711.351 | 1.099 |
| Isometrico | 31 | 15 | 48.4% | 0 | 701.440 | 450 |
| Listado / registro | 59 | 58 | 98.3% | 0 | 578.712 | 392 |
| Memoria / nota tecnica | 24 | 24 | 100.0% | 0 | 497.012 | 325 |

## Información por temática

| Temática | PDFs | Legibles | Legibilidad | Requiere OCR | Texto extraído | Chunks |
|---|---:|---:|---:|---:|---:|---:|
| General / otros | 385 | 267 | 69.4% | 22 | 14.242.624 | 9.122 |
| Proceso y mecanica | 328 | 270 | 82.3% | 4 | 4.686.840 | 3.081 |
| Tuberias e isometricos | 634 | 274 | 43.2% | 1 | 3.543.978 | 2.336 |
| Instrumentacion y control | 91 | 86 | 94.5% | 0 | 3.343.624 | 2.148 |
| Civil y estructuras | 261 | 99 | 37.9% | 0 | 3.136.104 | 2.021 |
| Fabricacion y compras | 24 | 21 | 87.5% | 0 | 885.216 | 569 |
| Permisos y documentacion oficial | 37 | 27 | 73.0% | 0 | 843.860 | 547 |
| Especificaciones tecnicas | 25 | 18 | 72.0% | 0 | 198.535 | 132 |

## Lectura rápida

- `pdf-catalog.csv`: ficha de cada PDF con código, tipo, temática, legibilidad y volumen de información.
- `pdf-type-summary.csv`: resumen agregado por tipo documental.
- `pdf-topic-summary.csv`: resumen agregado por temática.
- `pdf-status-summary.csv`: resumen agregado por estado técnico.

Nota: la clasificación es heurística, basada en ruta, nombre, código documental y metadatos ya extraídos. Es suficiente para priorizar y reducir tokens; puede refinarse cuando empecemos a redactar la memoria final.
