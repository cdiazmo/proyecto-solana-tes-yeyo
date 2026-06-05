# knowledge-base-rag

Skill RAG (Retrieval-Augmented Generation) para OpenClaw/Moltbot.
Permite responder preguntas sobre documentos internos usando Gemini como LLM y Qdrant como vector store.

## Arquitectura

```
Pregunta usuario
    │
    ▼
embedText() ──► Gemini Embedding API
    │
    ▼
searchChunks() ──► Qdrant (vector search)
    │
    ▼
buildPrompt() ──► prompt RAG con contexto
    │
    ▼
generateAnswer() ──► Gemini (LLM)
    │
    ▼
KnowledgeAnswer { answer, sources, confidence, usedChunks }
```

## Requisitos

- Node.js 22.19+ o 24+
- Docker (para Qdrant)
- API Key de Gemini ([Google AI Studio](https://aistudio.google.com))

## Instalación

```bash
cd knowledge-base-rag
npm install
```

## Configuración

```bash
cp .env.example .env
# Edita .env y añade tu GEMINI_API_KEY y la ruta a tus documentos
```

Variables importantes:

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `GEMINI_API_KEY` | *(requerida)* | Clave de API de Google Gemini |
| `GEMINI_MODEL` | `gemini-3.1-flash-lite` | Modelo LLM |
| `GEMINI_EMBEDDING_MODEL` | `gemini-embedding-001` | Modelo de embeddings |
| `QDRANT_URL` | `http://localhost:6333` | URL de Qdrant |
| `QDRANT_COLLECTION` | `knowledge_base` | Nombre de la colección |
| `KNOWLEDGE_DOCS_PATH` | `/srv/knowledge/docs` | Carpeta con documentos |
| `TOP_K` | `8` | Fragmentos a recuperar por consulta |
| `CHUNK_SIZE` | `1200` | Tamaño de fragmento en caracteres |
| `CHUNK_OVERLAP` | `200` | Solapamiento entre fragmentos |
| `MAX_DOC_SIZE_MB` | `50` | Tamaño máximo de documento |

## Levantar Qdrant

```bash
npm run qdrant
# o directamente:
docker compose up -d
```

Qdrant estará disponible en `http://localhost:6333`.
Dashboard en `http://localhost:6333/dashboard`.

## Añadir documentos

Copia tus PDFs, TXTs, Markdown o DOCX en la carpeta definida en `KNOWLEDGE_DOCS_PATH`:

```bash
cp mis-documentos/*.pdf /srv/knowledge/docs/
```

### Para el proyecto Yeyo/Solana

Puedes apuntar directamente a los documentos ya procesados o a las carpetas que te interesen:

```bash
# En .env:
KNOWLEDGE_DOCS_PATH=/Users/carlosdiaz/Downloads/Yeyo/06 Especificaciones Tecnicas
```

O ingestar múltiples carpetas ejecutando la ingesta varias veces con distintos paths.

## Ejecutar ingesta

```bash
npm run ingest
```

Esto:
1. Escanea todos los documentos en `KNOWLEDGE_DOCS_PATH`
2. Extrae texto (con soporte por página en PDFs)
3. Divide en chunks con solapamiento
4. Genera embeddings con Gemini
5. Guarda los vectores en Qdrant

La ingesta es **idempotente**: si ejecutas de nuevo, los mismos documentos se sobreescriben sin duplicados.

## Hacer una pregunta

```bash
npm run ask "¿Cuáles son los requisitos de instalación de bombas en el área TES?"
```

Ejemplo de salida:

```
============================================================
PREGUNTA: ¿Cuáles son los requisitos de instalación de bombas?
============================================================

RESPUESTA:

Según los pliegos de condiciones, la instalación de bombas debe seguir los planos isométricos
de Abener Teyma [4521-ESP-ANC-58-61-PS002.pdf, página 3]. El subcontratista de tuberías
es responsable de instalar todos los componentes en línea exactamente como se indica en los
planos, y cualquier desviación debe ser aprobada por el Activity Manager antes de proceder.

------------------------------------------------------------
Confianza: HIGH

FUENTES CONSULTADAS:
  • 4521-ESP-ANC-58-61-PS002.pdf, página 3 (relevancia: 87.3%)
  • 4521-ESP-ANC-58-61-PS001.pdf, página 7 (relevancia: 82.1%)
============================================================
```

## Integración con OpenClaw/Moltbot

Importa la función principal desde tu skill handler:

```typescript
import { answerQuestion } from './knowledge-base-rag/src/index.js';
// o tras compilar:
import { answerQuestion } from './knowledge-base-rag/dist/index.js';

// En el handler de Moltbot:
async function handleUserMessage(message: string) {
  const result = await answerQuestion(message);
  
  return {
    text: result.answer,
    metadata: {
      confidence: result.confidence,
      sources: result.sources,
    }
  };
}
```

El campo `answer` contiene la respuesta lista para el usuario.
El campo `sources` permite enriquecer la UI con referencias clickables.
El campo `confidence` puede usarse para mostrar un indicador de fiabilidad.

## Acceso simultáneo desde múltiples dispositivos

Qdrant soporta múltiples clientes concurrentes. Para acceso remoto:

1. Despliega Qdrant en un servidor o VM accesible:
   ```bash
   # En el servidor:
   docker compose up -d
   ```

2. Actualiza `QDRANT_URL` en cada cliente para apuntar al servidor:
   ```
   QDRANT_URL=http://tu-servidor:6333
   ```

3. Todos los dispositivos comparten la misma colección de vectores.
4. La ingesta solo necesita ejecutarse una vez (o cuando añadas documentos nuevos).

## Formatos soportados

| Formato | Extensión | Notas |
|---|---|---|
| PDF | `.pdf` | Extracción por página |
| Texto plano | `.txt` | UTF-8 |
| Markdown | `.md`, `.markdown` | Elimina front matter YAML |
| Word | `.docx` | Via mammoth |

## Seguridad

- Las rutas de documentos se validan para que queden dentro de `KNOWLEDGE_DOCS_PATH`.
- La API key de Gemini nunca se muestra en logs.
- Solo se devuelven fragmentos, nunca documentos completos.
- El tamaño máximo de documento es configurable.
