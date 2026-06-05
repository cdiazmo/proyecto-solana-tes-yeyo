const state = {
  token: "",
};

const filesState = {
  q: "",
  limit: 15,
  offset: 0,
  total: 0
};

let pollIntervalId = null;

const $ = (id) => document.getElementById(id);

function headers() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${state.token}`,
  };
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { ...headers(), ...(options.headers || {}) },
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`${response.status}: ${text}`);
  }
  return response.json();
}

function number(value) {
  return new Intl.NumberFormat("es-ES").format(value || 0);
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

async function downloadFile(path) {
  try {
    const response = await fetch(`/api/files/download?path=${encodeURIComponent(path)}`, {
      headers: headers()
    });
    if (!response.ok) {
      throw new Error(`Error ${response.status} al descargar el archivo.`);
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const filename = path.split("/").pop();
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    alert("No se pudo descargar el archivo: " + error.message);
  }
}
window.downloadFile = downloadFile;

async function loadStats() {
  if (!state.token) return;
  const stats = await api("/api/stats");
  $("metrics").innerHTML = `
    <div class="metric"><strong>${number(stats.documents)}</strong><span>documentos</span></div>
    <div class="metric"><strong>${number(stats.chunks)}</strong><span>fragmentos</span></div>
    <div class="metric"><strong>${number(stats.text_chars)}</strong><span>caracteres extraídos</span></div>
    <div class="metric"><strong>${number(stats.token_estimate)}</strong><span>tokens estimados</span></div>
  `;
}

function renderSearch(results, type) {
  if (!results.length) {
    $("search-results").innerHTML = '<div class="result">Sin resultados.</div>';
    return;
  }
  $("search-results").innerHTML = results.map((item) => {
    const path = escapeHtml(item.path);
    const title = escapeHtml(item.title || item.doc_code || path);
    const body = type === "chunks" ? escapeHtml(item.snippet || "") : `Estado: ${escapeHtml(item.status)} · Texto: ${number(item.text_chars)} chars`;
    return `
      <article class="result">
        <div class="result-header">
          <div class="meta">${escapeHtml(item.ext || "")} ${escapeHtml(item.revision || "")}</div>
          <button class="btn-download-sm" onclick="downloadFile('${path}')">Descargar</button>
        </div>
        <strong>${title}</strong>
        <div class="snippet">${body}</div>
        <div class="meta">${path}</div>
      </article>
    `;
  }).join("");
}

async function loadFiles() {
  if (!state.token) return;
  try {
    const data = await api(`/api/files?q=${encodeURIComponent(filesState.q)}&limit=${filesState.limit}&offset=${filesState.offset}`);
    filesState.total = data.total;
    
    const tbody = $("files-list");
    if (data.files.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 20px; color: var(--muted);">No se encontraron archivos.</td></tr>';
    } else {
      tbody.innerHTML = data.files.map(file => {
        const title = escapeHtml(file.title || "Sin título");
        const path = escapeHtml(file.path);
        const ext = escapeHtml(file.ext || "");
        const size = escapeHtml(file.size_human || "");
        const status = escapeHtml(file.status || "");
        return `
          <tr>
            <td><strong>${title}</strong><br><small style="color: var(--muted);">${escapeHtml(file.doc_code || "")}</small></td>
            <td style="max-width: 320px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${path}">${path}</td>
            <td><span class="badge">${ext}</span></td>
            <td>${size}</td>
            <td><small>${status}</small></td>
            <td>
              <button class="btn-download-sm" onclick="downloadFile('${path}')">Descargar</button>
            </td>
          </tr>
        `;
      }).join("");
    }
    
    const currentPage = Math.floor(filesState.offset / filesState.limit) + 1;
    const totalPages = Math.max(1, Math.ceil(filesState.total / filesState.limit));
    $("file-page-info").textContent = `Pág ${currentPage} / ${totalPages} (${filesState.total} total)`;
    
    $("btn-file-prev").disabled = filesState.offset <= 0;
    $("btn-file-next").disabled = (filesState.offset + filesState.limit) >= filesState.total;
  } catch (error) {
    console.error("Error al cargar archivos:", error);
  }
}

function startPollingIfNeeded(requests) {
  const hasActive = requests.some(r => r.status === "queued" || r.status === "running");
  if (hasActive && !pollIntervalId) {
    pollIntervalId = setInterval(async () => {
      await loadRequests();
    }, 2000);
  } else if (!hasActive && pollIntervalId) {
    clearInterval(pollIntervalId);
    pollIntervalId = null;
  }
}

async function loadRequests() {
  if (!state.token) return;
  const data = await api("/api/requests");
  
  startPollingIfNeeded(data.requests);
  
  $("requests").innerHTML = data.requests.map((request) => {
    const result = request.result;
    let answer = "";
    if (result && result.answer) {
      let parsedAnswer = marked.parse(result.answer);
      
      // Inline replacement of [Doc #N]
      if (result.documents && result.documents.length > 0) {
        parsedAnswer = parsedAnswer.replace(/\[Doc #(\d+)\]/gi, (match, num) => {
          const idx = parseInt(num, 10) - 1;
          const doc = result.documents[idx];
          if (doc) {
            const escapedPath = escapeHtml(doc.path);
            return `<a href="#" class="inline-download" onclick="downloadFile('${escapedPath}'); return false;" title="Descargar: ${escapedPath}">[Doc #${num} 📥]</a>`;
          }
          return match;
        });
      }
      
      // Inline replacement of [Extracto #N]
      if (result.sources && result.sources.length > 0) {
        parsedAnswer = parsedAnswer.replace(/\[Extracto #(\d+)\]/gi, (match, num) => {
          const idx = parseInt(num, 10) - 1;
          const src = result.sources[idx];
          if (src) {
            const escapedPath = escapeHtml(src.path);
            let locStr = "";
            if (src.page) {
              const isSheet = isNaN(src.page);
              const label = isSheet ? "Hoja" : "Pág.";
              locStr = ` (${label} ${src.page}`;
              if (src.line) {
                locStr += `, lín. ${src.line}`;
              }
              locStr += ")";
            }
            return `<a href="#" class="inline-download" onclick="downloadFile('${escapedPath}'); return false;" title="Descargar: ${escapedPath}">[Extracto #${num}${locStr} 📥]</a>`;
          }
          return match;
        });
      }
      
      // Inline replacement of simple [N] citations referring to sources
      if (result.sources && result.sources.length > 0) {
        parsedAnswer = parsedAnswer.replace(/\[(\d+)\]/g, (match, num) => {
          const idx = parseInt(num, 10) - 1;
          const src = result.sources[idx];
          if (src) {
            const escapedPath = escapeHtml(src.path);
            let locStr = "";
            if (src.page) {
              const isSheet = isNaN(src.page);
              const label = isSheet ? "Hoja" : "Pág.";
              locStr = ` (${label} ${src.page}`;
              if (src.line) {
                locStr += `, lín. ${src.line}`;
              }
              locStr += ")";
            }
            return `<a href="#" class="inline-download" onclick="downloadFile('${escapedPath}'); return false;" title="Descargar: ${escapedPath}">[${num}${locStr} 📥]</a>`;
          }
          return match;
        });
      }
      
      answer = `<div class="answer">${parsedAnswer}</div>`;
    }
    
    let progress = "";
    if (request.status === "queued" || request.status === "running") {
      const statusText = request.status === "running" ? "Procesando respuesta con IA..." : "En cola de espera...";
      progress = `
        <div class="progress-container">
          <div class="spinner"></div>
          <span class="progress-text">${statusText}</span>
        </div>
      `;
    }
    
    let docs = "";
    if (result && result.documents && result.documents.length > 0) {
      docs = `
        <div class="references-section">
          <strong>Documentos encontrados:</strong>
          <ul class="ref-list">
            ${result.documents.slice(0, 15).map((d) => `
              <li>
                <span class="ref-icon">📄</span>
                <span class="ref-title" title="${escapeHtml(d.title || d.doc_code || d.path)}">${escapeHtml(d.title || d.doc_code || d.path)}</span>
                <span class="ref-path" title="${escapeHtml(d.path)}">${escapeHtml(d.path)}</span>
                <button class="btn-download-sm" onclick="downloadFile('${escapeHtml(d.path)}')">Descargar</button>
              </li>
            `).join("")}
          </ul>
        </div>
      `;
    }
    
    let sources = "";
    if (result && result.sources && result.sources.length > 0) {
      sources = `
        <div class="references-section">
          <strong>Referencias y fuentes de información:</strong>
          <ul class="ref-list">
            ${result.sources.map((s) => `
              <li>
                <span class="ref-icon">📌</span>
                <span class="ref-title" title="${escapeHtml(s.title || s.doc_code || s.path)}">${escapeHtml(s.title || s.doc_code || s.path)}</span>
                <span class="ref-path" title="${escapeHtml(s.path)}">${escapeHtml(s.path)}</span>
                <button class="btn-download-sm" onclick="downloadFile('${escapeHtml(s.path)}')">Descargar</button>
              </li>
            `).join("")}
          </ul>
        </div>
      `;
    }
    
    const error = request.error ? `<div class="error">${escapeHtml(request.error)}</div>` : "";
    return `
      <article class="request">
        <div class="meta">#${request.id} · <span class="badge">${escapeHtml(request.status)}</span> · ${escapeHtml(request.kind)} · ${escapeHtml(request.requester_name || "")}</div>
        <strong>${escapeHtml(request.prompt)}</strong>
        ${progress}
        ${answer}
        ${docs}
        ${sources}
        ${error}
      </article>
    `;
  }).join("");
}

$("search-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const type = $("search-type").value;
  const query = $("search").value.trim();
  const path = type === "chunks" ? "/api/search/chunks" : "/api/search/documents";
  const data = await api(path, {
    method: "POST",
    body: JSON.stringify({ query, limit: 20 }),
  });
  renderSearch(data.results, type);
});

$("clear-search").addEventListener("click", () => {
  $("search").value = "";
  $("search-results").innerHTML = "";
});

$("request-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const prompt = $("prompt").value.trim();
  const kind = $("kind").value;
  if (!prompt) return;
  await api("/api/requests", {
    method: "POST",
    body: JSON.stringify({ prompt, kind }),
  });
  $("prompt").value = "";
  await loadRequests();
});

$("run-next").addEventListener("click", async () => {
  await api("/api/custodian/run-next", { method: "POST", body: "{}" });
  await loadRequests();
});

$("refresh").addEventListener("click", loadRequests);

$("clear-requests").addEventListener("click", async () => {
  if (!confirm("¿Seguro que deseas limpiar todo el historial de peticiones?")) return;
  try {
    await api("/api/requests/clear", { method: "POST" });
    await loadRequests();
  } catch (error) {
    alert("Error al limpiar historial: " + error.message);
  }
});

// File Index Event Listeners
$("file-query").addEventListener("input", (e) => {
  filesState.q = e.target.value.trim();
  filesState.offset = 0;
  loadFiles();
});

$("btn-file-prev").addEventListener("click", () => {
  if (filesState.offset > 0) {
    filesState.offset = Math.max(0, filesState.offset - filesState.limit);
    loadFiles();
  }
});

$("btn-file-next").addEventListener("click", () => {
  if (filesState.offset + filesState.limit < filesState.total) {
    filesState.offset += filesState.limit;
    loadFiles();
  }
});

// Tab Switching logic
document.querySelectorAll(".tab-button").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-button").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    
    document.querySelectorAll(".tab-content").forEach((tc) => tc.classList.add("hidden"));
    const targetTab = btn.getAttribute("data-tab");
    document.getElementById(targetTab).classList.remove("hidden");
  });
});

async function initApp() {
  try {
    const configResponse = await fetch("/api/config");
    if (!configResponse.ok) {
      throw new Error("No se pudo obtener la configuración pública del servidor");
    }
    const config = await configResponse.json();
    state.token = config.token;
    
    // Load app content
    await Promise.all([loadStats(), loadRequests(), loadFiles()]);
  } catch (error) {
    $("metrics").innerHTML = `<div class="metric error" style="grid-column: span 4; text-align: center;">Error de Inicialización: ${escapeHtml(error.message)}</div>`;
  }
}

initApp();
