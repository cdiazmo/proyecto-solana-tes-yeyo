import type { SearchResult } from '../qdrant/searchChunks.js';

/**
 * Builds the RAG prompt by injecting retrieved context and the user question.
 */
export function buildPrompt(question: string, chunks: SearchResult[]): string {
  const contextBlocks = chunks.map((chunk, i) => {
    const source = chunk.pageNumber
      ? `[${chunk.sourceFile}, página ${chunk.pageNumber}]`
      : `[${chunk.sourceFile}]`;
    return `--- Fragmento ${i + 1} ${source} ---\n${chunk.text}`;
  });

  const context = contextBlocks.join('\n\n');

  return `Eres un asistente de consulta documental especializado en documentos técnicos de ingeniería.
Responde exclusivamente usando el CONTEXTO proporcionado.
No uses conocimiento externo.
No inventes datos, normativas, valores ni procedimientos.
Si el contexto no contiene la respuesta, di exactamente: "No he encontrado esa información en la base documental."
Cuando respondas, cita las fuentes usando este formato: [archivo, página X] o [archivo] si no hay página.
Si varias fuentes se contradicen, explica la contradicción y muestra ambas.
Mantén la respuesta clara, directa y en español.
Usa listas o secciones cuando la información lo requiera.

CONTEXTO:
${context}

PREGUNTA:
${question}

RESPUESTA:`;
}
