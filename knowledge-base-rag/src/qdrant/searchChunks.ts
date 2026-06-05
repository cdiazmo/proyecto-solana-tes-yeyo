import { getQdrantClient } from './qdrantClient.js';
import { config } from '../config.js';

export interface SearchResult {
  text: string;
  sourceFile: string;
  pageNumber?: number;
  sectionTitle?: string;
  documentType: string;
  chunkIndex: number;
  score: number;
}

/**
 * Searches Qdrant for the most semantically similar chunks.
 * Returns results above the minimum score threshold.
 */
export async function searchChunks(
  queryVector: number[],
  topK?: number,
  minScore = 0.35,
): Promise<SearchResult[]> {
  const client = getQdrantClient();
  const collectionName = config.qdrant.collection;
  const k = topK ?? config.knowledge.topK;

  const response = await client.search(collectionName, {
    vector: queryVector,
    limit: k,
    with_payload: true,
    score_threshold: minScore,
  });

  return response.map((hit) => {
    const p = hit.payload as Record<string, unknown>;
    return {
      text: (p['text'] as string) ?? '',
      sourceFile: (p['sourceFile'] as string) ?? 'unknown',
      pageNumber: p['pageNumber'] != null ? Number(p['pageNumber']) : undefined,
      sectionTitle: p['sectionTitle'] != null ? String(p['sectionTitle']) : undefined,
      documentType: (p['documentType'] as string) ?? 'unknown',
      chunkIndex: Number(p['chunkIndex'] ?? 0),
      score: hit.score,
    };
  });
}
