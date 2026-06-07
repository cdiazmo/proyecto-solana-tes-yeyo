# Coste estimado de procesamiento pendiente

Generado: 2026-06-05

## Pendiente local detectado

| Bloque pendiente | Documentos | Paginas estimadas | Tamano | Observacion |
|---|---:|---:|---:|---|
| PDFs que requieren OCR o no tienen texto util | 620 | 1.549 | 440,7 MB | Principal coste pendiente; resoluble localmente con OCR |
| DWG | 391 | n/a | 296,7 MB | Requiere visor/conversor CAD o correlacion con PDF equivalente |
| NWD | 13 | n/a | 1,55 GB | Modelo 3D, tratar como referencia/metadata salvo export local |
| ZIP / 7z no procesados en profundidad | 151 | n/a | 547,0 MB | Conviene abrir selectivamente y reindexar contenido |
| MSG | 23 | n/a | 116,7 MB | Extraible localmente con libreria especifica |
| XLS antiguos | 31 | n/a | 43,8 MB | Extraible localmente si anadimos soporte `.xls` |
| JPG | 7 | n/a | 14,3 MB | OCR local si aportan documentos |
| Errores reales | 5 | n/a | 4,6 MB | 4 ZIP y 1 XLSX anomalo |

## Estimacion OCR pendiente

- PDFs pendientes de OCR: 620.
- Paginas PDF pendientes: 1.549.
- Densidad real observada en PDFs legibles: ~415 tokens/pagina.
- Texto estimado tras OCR: ~642.610 tokens de entrada.
- Coste API del OCR local: 0 USD.
- Tiempo local orientativo: 26 min a 2 h 10 min si el OCR rinde entre 1 y 5 s/pagina, sin contar instalacion ni conversion de imagenes.

## Coste IA para sintetizar lo pendiente tras OCR

Supuestos:

- Entrada estimada: 642.610 tokens.
- Escenario ficha: 250 tokens de salida/documento = 155.000 tokens de salida.
- Escenario resumen: 500 tokens/documento = 310.000 tokens de salida.
- Escenario profundo: 1.000 tokens/documento = 620.000 tokens de salida.

Precios usados, por 1M tokens, segun OpenAI API pricing consultado el 2026-06-05:

- gpt-5.4-nano standard: input 0,20 USD, output 1,25 USD.
- gpt-5.4-mini standard: input 0,75 USD, output 4,50 USD.
- gpt-5.4 standard: input 2,50 USD, output 15,00 USD.
- Batch/Flex aproximado: mitad del coste standard segun tabla oficial.

| Modelo | Modo | Ficha 250 tok/doc | Resumen 500 tok/doc | Profundo 1.000 tok/doc |
|---|---|---:|---:|---:|
| gpt-5.4-nano | standard | 0,32 USD | 0,52 USD | 0,90 USD |
| gpt-5.4-mini | standard | 1,18 USD | 1,88 USD | 3,27 USD |
| gpt-5.4 | standard | 3,93 USD | 6,26 USD | 10,91 USD |
| gpt-5.4-nano | batch/flex | 0,16 USD | 0,26 USD | 0,45 USD |
| gpt-5.4-mini | batch/flex | 0,59 USD | 0,94 USD | 1,64 USD |
| gpt-5.4 | batch/flex | 1,97 USD | 3,13 USD | 5,45 USD |

## Recomendacion

La ruta optima es:

1. OCR local selectivo de los 620 PDFs pendientes.
2. Generar fichas tecnicas con gpt-5.4-mini batch/flex o gpt-5.4-nano para documentos repetitivos.
3. Reservar gpt-5.4 para capitulos finales, conflictos, comparativas y documentos criticos.

Coste API recomendado para el pendiente OCR, una vez extraido localmente: entre 0,59 y 1,64 USD si usamos gpt-5.4-mini batch/flex, segun profundidad.
