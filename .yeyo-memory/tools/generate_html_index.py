#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path.cwd()
MEMORY_ROOT = ROOT / ".yeyo-memory"
CARDS_DIR = MEMORY_ROOT / "cards"
REPORTS_DIR = MEMORY_ROOT / "reports"
OUTPUT = ROOT / "indice-documental.html"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def rel_href(path: str | None) -> str:
    if not path:
        return ""
    return str(path).replace("\\", "/")


def load_cards() -> list[dict[str, Any]]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(CARDS_DIR.glob("*.json"))]


def compact_doc(
    card: dict[str, Any],
    pdf_data: dict[str, dict[str, str]],
    plan_data: dict[str, dict[str, str]],
    match_counts: dict[str, int],
    readiness_data: dict[str, dict[str, str]],
) -> dict[str, Any]:
    path = card.get("path", "")
    pdf = pdf_data.get(path, {})
    plan = plan_data.get(path, {})
    readiness = readiness_data.get(path, {})
    metadata = card.get("metadata") or {}
    ai_features = metadata.get("ai_features") or {}
    index_matches = metadata.get("index_matches") or []
    index_kinds = sorted({item.get("index_kind", "") for item in index_matches if item.get("index_kind")})

    return {
        "path": path,
        "title": card.get("title") or pdf.get("title") or Path(path).stem,
        "doc_code": card.get("doc_code") or pdf.get("doc_code") or plan.get("doc_code") or "",
        "revision": card.get("revision") or pdf.get("revision") or plan.get("revision") or "",
        "ext": card.get("ext") or "",
        "top_dir": card.get("top_dir") or "",
        "status": card.get("status") or "",
        "size_human": card.get("size_human") or "",
        "size_bytes": int(card.get("size_bytes") or 0),
        "text_chars": int(card.get("text_chars") or 0),
        "chunks": int(card.get("chunks") or 0),
        "token_estimate": int(card.get("token_estimate") or 0),
        "type": pdf.get("type") or "",
        "topic": pdf.get("topic") or "",
        "readability": pdf.get("readability") or "",
        "info_band": pdf.get("info_band") or "",
        "plan_kind": plan.get("plan_kind") or ((metadata.get("plan_tag") or {}).get("kind") or ""),
        "source_corpus": ai_features.get("source_corpus") or "",
        "project_area": ai_features.get("project_area") or "",
        "deliverable_part": ai_features.get("deliverable_part") or "",
        "discipline": ai_features.get("discipline") or "",
        "extraction_quality": ai_features.get("extraction_quality") or "",
        "ai_action": ai_features.get("ai_action") or "",
        "reuse_priority": ai_features.get("reuse_priority") or "",
        "page_count": int(ai_features.get("page_count") or (metadata.get("pages") or 0) or 0),
        "ai_score": int(readiness.get("score") or 0),
        "send_policy": readiness.get("send_policy") or "",
        "ocr_priority": int(readiness.get("ocr_priority") or 0),
        "score_reasons": readiness.get("score_reasons") or "",
        "index_match_count": len(index_matches) or match_counts.get(card.get("card_path") or "", 0),
        "index_kinds": ", ".join(index_kinds),
        "card_path": card.get("card_path") or "",
        "extracted_path": card.get("extracted_path") or "",
        "href": rel_href(path),
        "card_href": rel_href(card.get("card_path")),
        "extracted_href": rel_href(card.get("extracted_path")),
    }


def summarize(docs: list[dict[str, Any]]) -> dict[str, Any]:
    status = Counter(doc["status"] for doc in docs)
    ext = Counter(doc["ext"] for doc in docs)
    topic = Counter(doc["topic"] or "Sin tematica" for doc in docs)
    deliverable = Counter(doc["deliverable_part"] or "Sin parte" for doc in docs)
    discipline = Counter(doc["discipline"] or "Sin disciplina" for doc in docs)
    top_dir = Counter(doc["top_dir"] for doc in docs)
    return {
        "docs": len(docs),
        "total_bytes": sum(doc["size_bytes"] for doc in docs),
        "text_chars": sum(doc["text_chars"] for doc in docs),
        "chunks": sum(doc["chunks"] for doc in docs),
        "indexed_matches": sum(1 for doc in docs if doc["index_match_count"]),
        "status": status.most_common(),
        "ext": ext.most_common(),
        "topic": topic.most_common(10),
        "deliverable_part": deliverable.most_common(),
        "discipline": discipline.most_common(),
        "top_dir": top_dir.most_common(),
    }


def json_script(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def main() -> int:
    cards = load_cards()
    pdf_rows = read_csv(REPORTS_DIR / "pdf-catalog.csv")
    plan_rows = read_csv(REPORTS_DIR / "plan-tags.csv")
    match_rows = read_csv(REPORTS_DIR / "document-index-matches.csv")
    readiness_rows = read_csv(REPORTS_DIR / "ai-readiness.csv")

    pdf_data = {row["path"]: row for row in pdf_rows}
    plan_data = {row["path"]: row for row in plan_rows}
    readiness_data = {row["path"]: row for row in readiness_rows}
    match_counts = Counter(row.get("matched_card_path", "") for row in match_rows)

    docs = [compact_doc(card, pdf_data, plan_data, match_counts, readiness_data) for card in cards]
    docs.sort(key=lambda item: (item["top_dir"], item["path"]))
    summary = summarize(docs)

    filter_values = {
        "top_dir": sorted({doc["top_dir"] for doc in docs if doc["top_dir"]}),
        "ext": sorted({doc["ext"] for doc in docs if doc["ext"]}),
        "status": sorted({doc["status"] for doc in docs if doc["status"]}),
        "topic": sorted({doc["topic"] for doc in docs if doc["topic"]}),
        "type": sorted({doc["type"] for doc in docs if doc["type"]}),
        "plan_kind": sorted({doc["plan_kind"] for doc in docs if doc["plan_kind"]}),
        "source_corpus": sorted({doc["source_corpus"] for doc in docs if doc["source_corpus"]}),
        "deliverable_part": sorted({doc["deliverable_part"] for doc in docs if doc["deliverable_part"]}),
        "discipline": sorted({doc["discipline"] for doc in docs if doc["discipline"]}),
        "ai_action": sorted({doc["ai_action"] for doc in docs if doc["ai_action"]}),
        "reuse_priority": sorted({doc["reuse_priority"] for doc in docs if doc["reuse_priority"]}),
        "send_policy": sorted({doc["send_policy"] for doc in docs if doc["send_policy"]}),
    }

    generated_at = datetime.now(timezone.utc).isoformat()

    html_text = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Índice documental Yeyo</title>
  <style>
    :root {{
      --bg: #f6f7f8;
      --panel: #ffffff;
      --text: #182026;
      --muted: #5c6873;
      --line: #d9dee3;
      --accent: #0f766e;
      --accent-2: #1d4ed8;
      --warn: #b45309;
      --bad: #b91c1c;
      --good: #047857;
      --tag: #eef2f7;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.45;
    }}
    header {{
      padding: 24px 28px 18px;
      background: var(--panel);
      border-bottom: 1px solid var(--line);
      position: sticky;
      top: 0;
      z-index: 10;
    }}
    h1 {{
      margin: 0 0 6px;
      font-size: 24px;
      letter-spacing: 0;
    }}
    .sub {{
      color: var(--muted);
      font-size: 13px;
    }}
    main {{
      padding: 18px 28px 36px;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(6, minmax(130px, 1fr));
      gap: 10px;
      margin-bottom: 16px;
    }}
    .stat {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
    }}
    .stat b {{
      display: block;
      font-size: 22px;
    }}
    .stat span {{
      color: var(--muted);
      font-size: 12px;
    }}
    .controls {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      display: grid;
      grid-template-columns: 2fr repeat(3, 1fr);
      gap: 10px;
      margin-bottom: 14px;
    }}
    .controls .row {{
      display: contents;
    }}
    input, select {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 9px 10px;
      font: inherit;
      background: #fff;
      color: var(--text);
    }}
    .toolbar {{
      display: flex;
      gap: 8px;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 8px;
      color: var(--muted);
      font-size: 13px;
    }}
    button {{
      border: 1px solid var(--line);
      background: #fff;
      border-radius: 6px;
      padding: 8px 10px;
      font: inherit;
      cursor: pointer;
    }}
    button:hover {{ border-color: var(--accent); }}
    .table-wrap {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: auto;
      max-height: calc(100vh - 285px);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 1280px;
      font-size: 13px;
    }}
    th, td {{
      padding: 8px 10px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
      text-align: left;
    }}
    th {{
      background: #f9fafb;
      position: sticky;
      top: 0;
      z-index: 2;
      white-space: nowrap;
      font-size: 12px;
      color: #39434d;
    }}
    td.path {{
      max-width: 430px;
      word-break: break-word;
    }}
    a {{
      color: var(--accent-2);
      text-decoration: none;
    }}
    a:hover {{ text-decoration: underline; }}
    .tag {{
      display: inline-block;
      padding: 2px 6px;
      border-radius: 999px;
      background: var(--tag);
      color: #26323a;
      font-size: 12px;
      white-space: nowrap;
      margin-bottom: 2px;
    }}
    .status-ok {{ color: var(--good); font-weight: 600; }}
    .status-needs_ocr_or_empty {{ color: var(--warn); font-weight: 600; }}
    .status-tagged_plan {{ color: var(--accent); font-weight: 600; }}
    .status-error {{ color: var(--bad); font-weight: 600; }}
    .muted {{ color: var(--muted); }}
    .small {{ font-size: 12px; }}
    .links {{
      display: flex;
      flex-direction: column;
      gap: 3px;
    }}
    @media (max-width: 980px) {{
      header, main {{ padding-left: 14px; padding-right: 14px; }}
      .stats {{ grid-template-columns: repeat(2, 1fr); }}
      .controls {{ grid-template-columns: 1fr; }}
      .table-wrap {{ max-height: none; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Índice documental Yeyo</h1>
    <div class="sub">Generado {html.escape(generated_at)}. Archivo portable con enlaces relativos dentro de esta carpeta.</div>
  </header>
  <main>
    <section class="stats" id="stats"></section>
    <section class="controls">
      <input id="q" type="search" placeholder="Buscar por código, título, ruta, temática, tipo o índice...">
      <select id="top_dir"><option value="">Carpeta</option></select>
      <select id="ext"><option value="">Extensión</option></select>
      <select id="status"><option value="">Estado</option></select>
      <select id="topic"><option value="">Temática</option></select>
      <select id="type"><option value="">Tipo documental</option></select>
      <select id="plan_kind"><option value="">Tipo de plano</option></select>
      <select id="source_corpus"><option value="">Corpus</option></select>
      <select id="deliverable_part"><option value="">Parte proyecto</option></select>
      <select id="discipline"><option value="">Disciplina</option></select>
      <select id="ai_action"><option value="">Acción IA</option></select>
      <select id="reuse_priority"><option value="">Prioridad</option></select>
      <select id="send_policy"><option value="">Política envío</option></select>
      <select id="sort">
        <option value="path">Orden: ruta</option>
        <option value="size_desc">Orden: tamaño</option>
        <option value="text_desc">Orden: info extraída</option>
        <option value="index_desc">Orden: cruces con índices</option>
        <option value="priority">Orden: prioridad IA</option>
        <option value="ai_score">Orden: score IA</option>
        <option value="ocr_priority">Orden: OCR</option>
      </select>
    </section>
    <div class="toolbar">
      <div><span id="count"></span> <span class="muted">mostrados</span></div>
      <div>
        <button id="reset">Limpiar filtros</button>
      </div>
    </div>
    <section class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Documento</th>
            <th>Código / Rev.</th>
            <th>Clasificación</th>
            <th>Features IA</th>
            <th>Estado</th>
            <th>Info</th>
            <th>Índices</th>
            <th>Enlaces</th>
          </tr>
        </thead>
        <tbody id="rows"></tbody>
      </table>
    </section>
  </main>
  <script id="doc-data" type="application/json">{json_script({"docs": docs, "summary": summary, "filters": filter_values})}</script>
  <script>
    const payload = JSON.parse(document.getElementById('doc-data').textContent);
    const docs = payload.docs;
    const filters = payload.filters;
    const state = {{
      q: '',
      top_dir: '',
      ext: '',
      status: '',
      topic: '',
      type: '',
      plan_kind: '',
      source_corpus: '',
      deliverable_part: '',
      discipline: '',
      ai_action: '',
      reuse_priority: '',
      send_policy: '',
      sort: 'path',
    }};

    const els = {{
      q: document.getElementById('q'),
      rows: document.getElementById('rows'),
      count: document.getElementById('count'),
      stats: document.getElementById('stats'),
      reset: document.getElementById('reset'),
      sort: document.getElementById('sort'),
      top_dir: document.getElementById('top_dir'),
      ext: document.getElementById('ext'),
      status: document.getElementById('status'),
      topic: document.getElementById('topic'),
      type: document.getElementById('type'),
      plan_kind: document.getElementById('plan_kind'),
      source_corpus: document.getElementById('source_corpus'),
      deliverable_part: document.getElementById('deliverable_part'),
      discipline: document.getElementById('discipline'),
      ai_action: document.getElementById('ai_action'),
      reuse_priority: document.getElementById('reuse_priority'),
      send_policy: document.getElementById('send_policy'),
    }};

    function fmt(n) {{
      return new Intl.NumberFormat('es-ES').format(n || 0);
    }}

    function esc(value) {{
      return String(value ?? '').replace(/[&<>"']/g, ch => ({{
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
      }}[ch]));
    }}

    function fileHref(path) {{
      return encodeURI(path || '');
    }}

    function option(select, value) {{
      const opt = document.createElement('option');
      opt.value = value;
      opt.textContent = value;
      select.appendChild(opt);
    }}

    for (const key of ['top_dir', 'ext', 'status', 'topic', 'type', 'plan_kind', 'source_corpus', 'deliverable_part', 'discipline', 'ai_action', 'reuse_priority', 'send_policy']) {{
      for (const value of filters[key]) option(els[key], value);
    }}

    function renderStats(list) {{
      const readable = list.filter(d => d.status === 'ok').length;
      const tagged = list.filter(d => d.status === 'tagged_plan').length;
      const indexed = list.filter(d => d.index_match_count > 0).length;
      const highPriority = list.filter(d => d.reuse_priority === 'alta' || d.reuse_priority === 'media_alta').length;
      const sendable = list.filter(d => String(d.send_policy || '').startsWith('enviar_')).length;
      const chunks = list.reduce((sum, d) => sum + d.chunks, 0);
      const cards = [
        ['Documentos', list.length],
        ['Legibles', readable],
        ['Planos etiquetados', tagged],
        ['Con índice XLS', indexed],
        ['Prioridad IA', highPriority],
        ['Enviables IA', sendable],
        ['Chunks', chunks],
      ];
      els.stats.innerHTML = cards.map(([label, value]) => `<div class="stat"><b>${{fmt(value)}}</b><span>${{esc(label)}}</span></div>`).join('');
    }}

    function matches(doc) {{
      for (const key of ['top_dir', 'ext', 'status', 'topic', 'type', 'plan_kind', 'source_corpus', 'deliverable_part', 'discipline', 'ai_action', 'reuse_priority', 'send_policy']) {{
        if (state[key] && doc[key] !== state[key]) return false;
      }}
      if (!state.q) return true;
      const haystack = [
        doc.path, doc.title, doc.doc_code, doc.revision, doc.ext, doc.top_dir,
        doc.status, doc.type, doc.topic, doc.plan_kind, doc.index_kinds,
        doc.source_corpus, doc.project_area, doc.deliverable_part, doc.discipline,
        doc.extraction_quality, doc.ai_action, doc.reuse_priority
        , doc.send_policy, doc.score_reasons
      ].join(' ').toLowerCase();
      return haystack.includes(state.q.toLowerCase());
    }}

    function sortDocs(list) {{
      const sorted = [...list];
      if (state.sort === 'size_desc') sorted.sort((a, b) => b.size_bytes - a.size_bytes || a.path.localeCompare(b.path));
      else if (state.sort === 'text_desc') sorted.sort((a, b) => b.text_chars - a.text_chars || a.path.localeCompare(b.path));
      else if (state.sort === 'index_desc') sorted.sort((a, b) => b.index_match_count - a.index_match_count || a.path.localeCompare(b.path));
      else if (state.sort === 'ai_score') sorted.sort((a, b) => b.ai_score - a.ai_score || a.path.localeCompare(b.path));
      else if (state.sort === 'ocr_priority') sorted.sort((a, b) => b.ocr_priority - a.ocr_priority || a.path.localeCompare(b.path));
      else if (state.sort === 'priority') {{
        const rank = {{ alta: 5, media_alta: 4, media: 3, pendiente_ocr: 2, baja: 1 }};
        sorted.sort((a, b) => (rank[b.reuse_priority] || 0) - (rank[a.reuse_priority] || 0) || b.text_chars - a.text_chars || a.path.localeCompare(b.path));
      }}
      else sorted.sort((a, b) => a.path.localeCompare(b.path));
      return sorted;
    }}

    function statusClass(status) {{
      return `status-${{String(status).replace(/[^a-z0-9_]+/g, '_')}}`;
    }}

    function renderRows(list) {{
      const visible = sortDocs(list).slice(0, 1000);
      els.count.textContent = fmt(list.length);
      els.rows.innerHTML = visible.map(doc => {{
        const classification = [
          doc.topic ? `<span class="tag">${{esc(doc.topic)}}</span>` : '',
          doc.type ? `<span class="tag">${{esc(doc.type)}}</span>` : '',
          doc.plan_kind ? `<span class="tag">${{esc(doc.plan_kind)}}</span>` : '',
        ].filter(Boolean).join('<br>');
        const aiFeatures = [
          doc.deliverable_part ? `<span class="tag">${{esc(doc.deliverable_part)}}</span>` : '',
          doc.discipline ? `<span class="tag">${{esc(doc.discipline)}}</span>` : '',
          doc.reuse_priority ? `<span class="tag">Prioridad: ${{esc(doc.reuse_priority)}}</span>` : '',
          doc.ai_score ? `<span class="tag">Score: ${{fmt(doc.ai_score)}}</span>` : '',
          doc.ocr_priority ? `<span class="tag">OCR: ${{fmt(doc.ocr_priority)}}</span>` : '',
          doc.ai_action ? `<div class="muted small">${{esc(doc.ai_action)}}</div>` : '',
          doc.send_policy ? `<div class="muted small">${{esc(doc.send_policy)}}</div>` : '',
        ].filter(Boolean).join('<br>');
        const links = [
          doc.href ? `<a href="${{fileHref(doc.href)}}">Abrir documento</a>` : '',
          doc.extracted_href ? `<a href="${{fileHref(doc.extracted_href)}}">Texto extraído</a>` : '',
          doc.card_href ? `<a href="${{fileHref(doc.card_href)}}">Ficha JSON</a>` : '',
        ].filter(Boolean).join('');
        return `<tr>
          <td class="path">
            <a href="${{fileHref(doc.href)}}">${{esc(doc.title || doc.path)}}</a>
            <div class="muted small">${{esc(doc.path)}}</div>
          </td>
          <td>
            <div>${{esc(doc.doc_code || '-')}}</div>
            <div class="muted small">${{esc(doc.revision || '')}}</div>
          </td>
          <td>${{classification || '<span class="muted">Sin clasificar</span>'}}</td>
          <td>${{aiFeatures || '<span class="muted">Sin features IA</span>'}}</td>
          <td>
            <div class="${{statusClass(doc.status)}}">${{esc(doc.status || '-')}}</div>
            <div class="muted small">${{esc(doc.readability || doc.extraction_quality || '')}}</div>
          </td>
          <td>
            <div>${{esc(doc.size_human)}} · ${{esc(doc.ext)}}</div>
            <div class="muted small">${{fmt(doc.text_chars)}} chars · ${{fmt(doc.chunks)}} chunks · ${{fmt(doc.page_count)}} pág.</div>
          </td>
          <td>
            <div>${{fmt(doc.index_match_count)}} cruces</div>
            <div class="muted small">${{esc(doc.index_kinds || '')}}</div>
          </td>
          <td><div class="links">${{links}}</div></td>
        </tr>`;
      }}).join('');
      if (list.length > visible.length) {{
        els.rows.innerHTML += `<tr><td colspan="8" class="muted">Mostrando 1.000 de ${{fmt(list.length)}} resultados. Usa filtros o búsqueda para acotar.</td></tr>`;
      }}
    }}

    function update() {{
      const list = docs.filter(matches);
      renderStats(list);
      renderRows(list);
    }}

    for (const key of ['top_dir', 'ext', 'status', 'topic', 'type', 'plan_kind', 'source_corpus', 'deliverable_part', 'discipline', 'ai_action', 'reuse_priority', 'send_policy', 'sort']) {{
      els[key].addEventListener('change', () => {{
        state[key] = els[key].value;
        update();
      }});
    }}
    els.q.addEventListener('input', () => {{
      state.q = els.q.value.trim();
      update();
    }});
    els.reset.addEventListener('click', () => {{
      for (const key of Object.keys(state)) state[key] = key === 'sort' ? 'path' : '';
      for (const key of ['top_dir', 'ext', 'status', 'topic', 'type', 'plan_kind', 'source_corpus', 'deliverable_part', 'discipline', 'ai_action', 'reuse_priority', 'send_policy']) els[key].value = '';
      els.sort.value = 'path';
      els.q.value = '';
      update();
    }});

    update();
  </script>
</body>
</html>
"""

    OUTPUT.write_text(html_text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
