# Features para IA

- Generado: 2026-06-08T20:00:39.318696+00:00
- Documentos enriquecidos: 2717

Estas features sirven para filtrar y priorizar contexto antes de enviarlo a un modelo IA.

## Corpus / origen

| Valor | Documentos |
|---|---:|
| Repositorio Solana / Yeyo | 1558 |
| Documentacion con sello PE 08 | 688 |
| Proyecto Helios Sole | 288 |
| Servidor Atlantica | 140 |
| Planos Solana | 42 |
| Ejemplo PCI | 1 |

## Área de proyecto

| Valor | Documentos |
|---|---:|
| TES / almacenamiento | 1211 |
| General | 1183 |
| Helios I | 310 |
| Infraestructura electrica | 13 |

## Parte documental

| Valor | Documentos |
|---|---:|
| Planos | 1581 |
| Documentacion auxiliar | 535 |
| Pliego de condiciones | 311 |
| Listados e indices | 130 |
| Memoria y anejos | 88 |
| Mediciones y presupuestos | 72 |

## Disciplina

| Valor | Documentos |
|---|---:|
| Proceso / mecanica / tuberias | 1454 |
| General | 751 |
| Electrica | 237 |
| Civil / estructuras | 113 |
| Permisos / legalizacion | 58 |
| Instrumentacion y control | 57 |
| Fabricacion / compras / calidad | 41 |
| PCI | 6 |

## Calidad de extracción

| Valor | Documentos |
|---|---:|
| alta_texto_extraido | 1262 |
| plano_etiquetado_sin_ocr | 689 |
| formato_tecnico_metadata_only | 425 |
| archivo_comprimido_listado | 149 |
| metadata_only | 117 |
| baja_texto_escaso_por_pagina | 42 |
| requiere_ocr | 27 |
| error | 6 |

## Acción recomendada IA

| Valor | Documentos |
|---|---:|
| usar_chunks | 1304 |
| usar_solo_etiqueta_y_metadatos | 689 |
| usar_indices_o_pdf_equivalente | 425 |
| descomprimir_solo_si_indice_lo_justifica | 149 |
| usar_metadatos | 123 |
| ocr_local_si_es_relevante | 27 |

## Prioridad de reutilización

| Valor | Documentos |
|---|---:|
| media | 1625 |
| media_alta | 680 |
| alta | 379 |
| pendiente_ocr | 27 |
| baja | 6 |

Archivo generado:

- `ai-features.csv`: una fila por documento con señales de filtrado para IA/RAG.
