# Yeyo local document memory

This folder is the local processing layer for the document set. It is designed to minimize model tokens by keeping raw extraction, metadata, document cards, chunks, and search indexes on disk.

## Folders

- `tools/`: reproducible local processing scripts.
- `cards/`: one compact JSON card per source document.
- `extracted/`: raw text extracted locally, one file per document when available.
- `chunks/`: JSONL chunks for retrieval and low-token prompting.
- `reports/`: compact summaries and processing reports.
- `sqlite/`: local SQLite database with document metadata and full-text search.

## Main workflow

```bash
/Users/carlosdiaz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .yeyo-memory/tools/build_memory.py
```

Useful filters:

```bash
/Users/carlosdiaz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .yeyo-memory/tools/build_memory.py --top-dir "06 Especificaciones Tecnicas"
/Users/carlosdiaz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .yeyo-memory/tools/build_memory.py --limit 50
/Users/carlosdiaz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 .yeyo-memory/tools/search_memory.py "heat tracing"
```

## Token strategy

Load `reports/processing-summary.md` first. For detailed work, query SQLite or `chunks/chunks.jsonl` and only send the relevant cards/chunks to the model.

