# AGENTS.md

Guia para agentes/IA que trabajen en esta carpeta documental.

## Contexto

Esta carpeta contiene documentacion tecnica del proyecto Yeyo/Solana TES, con PDFs, planos, DWG, XLS/XLSX, ZIP, MSG, NWD y otros documentos. El objetivo es gestionar la informacion de forma local-first, minimizando tokens y evitando enviar documentos completos a servicios externos.

Directorio raiz:

```text
/Users/carlosdiaz/Downloads/Yeyo
```

No asumir que esta ruta sera estable. Las herramientas y el HTML estan preparados con rutas relativas siempre que sea posible.

## Regla principal

No procesar documentos completos en conversacion si se puede evitar.

Orden recomendado:

1. Consultar indices y reportes locales.
2. Buscar en SQLite/chunks.
3. Leer fichas JSON concretas.
4. Leer texto extraido concreto.
5. Solo entonces usar IA para sintetizar.

## Estructura auxiliar

### `.yeyo-index/`

Inventario base de archivos.

- `manifest.json`: resumen compacto.
- `files.csv`: todos los archivos con tamano, extension, carpeta y fecha.
- `top-level-summary.csv`: resumen por carpeta raiz.
- `extensions.csv`: resumen por extension.
- `top-level/*.csv`: particiones por carpeta.
- `rebuild-index.mjs`: regenerador del inventario.

Comando:

```bash
node .yeyo-index/rebuild-index.mjs
```

### `.yeyo-memory/`

Memoria local procesada.

- `cards/`: una ficha JSON por documento.
- `extracted/`: texto extraido localmente.
- `chunks/chunks.jsonl`: fragmentos buscables.
- `sqlite/yeyo-memory.sqlite`: base local con metadatos y FTS.
- `reports/`: informes CSV/Markdown.
- `tools/`: scripts reproducibles.
- `ocr/`: resultados OCR locales.
- `vendor/`: dependencias Python locales instaladas para este flujo.
- `cache/`: cache temporal local.

## Estado actual

Resultados principales:

- Documentos totales indexados: 2.243.
- PDFs catalogados: 1.409.
- PDFs legibles localmente: 793.
- PDFs etiquetados como planos sin OCR completo: 587.
- PDFs pendientes reales de OCR: 29.
- Planos etiquetados: 1.105.
- Indices XLS/XLSX detectados: 39.
- Filas extraidas de indices: 4.937.
- Cruces indice-documento: 20.625.
- Documentos unicos enriquecidos por indices: 1.066.

## Informes clave

- `indice-documental.html`: indice navegable portable en la raiz.
- `.yeyo-memory/reports/processing-summary.md`: resumen general.
- `.yeyo-memory/reports/pdf-report.md`: resumen de PDFs.
- `.yeyo-memory/reports/pdf-catalog.csv`: catalogo PDF completo.
- `.yeyo-memory/reports/plan-tags.md`: resumen de planos etiquetados.
- `.yeyo-memory/reports/plan-tags.csv`: catalogo de planos.
- `.yeyo-memory/reports/document-indexes.md`: resumen de indices XLS/XLSX.
- `.yeyo-memory/reports/document-indexes.csv`: libros detectados como indices.
- `.yeyo-memory/reports/document-index-entries.csv`: filas extraidas de indices.
- `.yeyo-memory/reports/document-index-matches.csv`: cruces entre indices y documentos.
- `.yeyo-memory/reports/pending-cost-estimate.md`: estimacion de coste pendiente.

## Scripts principales

### Reconstruir memoria documental

```bash
/Users/carlosdiaz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .yeyo-memory/tools/build_memory.py
```

La ejecucion normal es incremental. Si no hay cambios, salta documentos ya procesados.

Filtros utiles:

```bash
/Users/carlosdiaz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .yeyo-memory/tools/build_memory.py --top-dir "06 Especificaciones Tecnicas"
/Users/carlosdiaz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .yeyo-memory/tools/build_memory.py --limit 50
```

### Buscar en memoria local

```bash
/Users/carlosdiaz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .yeyo-memory/tools/search_memory.py "heat exchanger"
```

Usar esto antes de leer archivos grandes.

### Generar informes PDF

```bash
/Users/carlosdiaz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .yeyo-memory/tools/report_pdfs.py
```

### Etiquetar planos

```bash
/Users/carlosdiaz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .yeyo-memory/tools/tag_plan_pdfs.py
```

Regla vigente: los planos se etiquetan por tipo y no se OCRan completos salvo peticion explicita.

### Extraer indices XLS/XLSX

```bash
/Users/carlosdiaz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .yeyo-memory/tools/extract_document_indexes.py
```

Estos indices son muy importantes. Muchos XLS/XLSX sirven como lista maestra de documentos, soportes, EDL, MTO, listas de valvulas, instrumentos, etc. Usarlos antes de intentar OCR o inferencias desde nombres.

### Generar HTML navegable

```bash
/Users/carlosdiaz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .yeyo-memory/tools/generate_html_index.py
```

Salida:

```text
indice-documental.html
```

Debe usar referencias relativas y no depender de la ruta absoluta del equipo.

### OCR local

Hay dos rutas:

- `run_tesseract_ocr.py`: OCR local con Tesseract + Poppler.
- `run_local_ocr.py` + `ocr_pdf_vision.swift`: OCR local con macOS Vision. Esta ruta dio problemas de buffer en sandbox para planos grandes, por lo que no es la preferida.

Tesseract y Poppler fueron instalados localmente via Homebrew. El OCR no envia documentos a backend.

Comando recomendado, solo para no-planos:

```bash
/Users/carlosdiaz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .yeyo-memory/tools/run_tesseract_ocr.py --dpi 150 --psm 6
```

Por defecto `run_tesseract_ocr.py` excluye planos presentes en `plan-tags.csv`. Usar `--include-plans` solo si el usuario lo pide expresamente.

## Politica sobre planos

El usuario indico que, si son planos, solo se debe extraer el tipo de plano para dejar el fichero etiquetado.

Por tanto:

- No hacer OCR completo de planos por defecto.
- Etiquetar planos con `tag_plan_pdfs.py`.
- Usar indices XLS/XLSX para obtener descripcion, revision, estado y relacion.
- Solo abrir/OCRar un plano concreto si se necesita inspeccion puntual.

Tipos de plano detectados incluyen:

- Soporte de tuberia MS.
- Isometrico de tuberia HTF.
- Plano / dibujo general.
- P&ID / diagrama de proceso.
- Soporte de tuberia HTF.
- Permiso / plano sellado.
- Plataforma / estructura metalica.
- Plano instrumentacion/control.
- Isometrico de tuberia MS.
- Layout / distribucion general.
- Tanque / drain back tank.
- Plano electrico.
- Isometrico de tuberia nitrogeno.
- Cimentacion / foundation.
- Grading / obra civil terreno.

## Formatos y tratamiento

- `pdf`: texto extraido si es legible; planos etiquetados; OCR solo para no-planos pendientes.
- `xlsx`/`xlsm`: extraidos localmente con `openpyxl`; revisar si son indices.
- `xls`: actualmente muchos estan como `metadata_only`; se podria anadir soporte con libreria local si fuera necesario.
- `dwg`: metadata-only; no intentar interpretar sin herramienta CAD local. Muchos estan representados por PDF/indices.
- `nwd`: metadata-only; modelo 3D, tratar como referencia.
- `zip`/`7z`: actualmente listados o metadata-only; descomprimir selectivamente si el indice lo justifica.
- `msg`: metadata-only; se podria anadir extractor local si el usuario lo pide.
- `jpg`: OCR local solo si se considera documento relevante.

## Buenas practicas para otros agentes

- No borrar ni regenerar todo sin motivo.
- No revertir cambios existentes.
- No usar rutas absolutas en archivos portables.
- No enviar documentos a backend sin permiso explicito.
- No hacer OCR masivo de planos.
- Antes de resumir, buscar localmente y leer solo chunks/fichas relevantes.
- Si se modifica la clasificacion, regenerar los informes y despues `indice-documental.html`.

## Flujo recomendado para crear memoria final

1. Usar `document-indexes` y `plan-tags` para consolidar catalogo.
2. Usar `search_memory.py` para localizar informacion por tema.
3. Generar capitulos por disciplina:
   - Proceso y mecanica.
   - Tuberias e isometricos.
   - Civil y estructuras.
   - Instrumentacion y control.
   - Electricidad.
   - Fabricacion/compras/calidad.
   - Permisos/inspecciones.
   - As built.
4. Usar IA solo para sintetizar chunks y fichas seleccionadas.
5. Mantener trazabilidad con rutas relativas a documentos originales.

## Archivos portables importantes

El usuario pidio un HTML portable. Mantener:

```text
indice-documental.html
```

en la raiz, con referencias relativas. Si se mueve la carpeta completa, el indice deberia seguir funcionando.

## Sistema multiagente

Se ha añadido una implementación inicial en `.yeyo-agents/` para consultas remotas con varias personas:

- API web FastAPI.
- Interfaz web en `.yeyo-agents/app/static/`.
- Base operativa separada en `.yeyo-agents/data/agents.sqlite`.
- Memoria documental `.yeyo-memory/sqlite/yeyo-memory.sqlite` abierta en solo lectura.
- Cola de peticiones.
- Agente custodio como ejecutor único.
- Integración opcional con Gemini mediante `GEMINI_API_KEY`.
- Modo local extractivo cuando no hay clave externa.

Documentación específica:

- `.yeyo-agents/README.md`
- `.yeyo-agents/ARCHITECTURE.md`
- `PROPUESTA-SISTEMA-MULTIAGENTE.md`
