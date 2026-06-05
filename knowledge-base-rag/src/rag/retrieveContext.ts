import { embedText } from '../gemini/embeddings.js';
import { searchChunks } from '../qdrant/searchChunks.js';
import { config } from '../config.js';
import type { SearchResult } from '../qdrant/searchChunks.js';

/**
 * Embeds the question and retrieves the most relevant chunks from Qdrant.
 * Returns empty array if no results pass the score threshold.
 */
export async function retrieveContext(question: string): Promise<SearchResult[]> {
  const queryEmbedding = await embedText(question);
  const results = await searchChunks(queryEmbedding, config.knowledge.topK);
  return results;
}
