import { getQdrantClient } from './qdrantClient.js';
import { config } from '../config.js';
import type { ChunkWithEmbedding } from '../ingest/metadata.js';
import { createHash } from 'crypto';

/**
 * Upserts a batch of chunks with their embeddings into Qdrant.
 * Uses deterministic IDs based on content hash to allow safe re-ingestion.
 */
export async function upsertChunks(chunks: ChunkWithEmbedding[]): Promise<void> {
  const client = getQdrantClient();
  const collectionName = config.qdrant.collection;

  if (chunks.length === 0) return;

  // Qdrant upsert in batches of 100 to avoid payload limits
  const BATCH_SIZE = 100;

  for (let i = 0; i < chunks.length; i += BATCH_SIZE) {
    const batch = chunks.slice(i, i + BATCH_SIZE);

    const points = batch.map((chunk) => {
      // Deterministic UUID-like ID from hash so re-ingestion is idempotent
      const hash = createHash('sha256')
        .update(`${chunk.metadata.sourceFile}::${chunk.metadata.chunkIndex}`)
        .digest('hex');
      // Qdrant requires a number or UUID string — use first 32 hex chars as UUID
      const id = [
        hash.slice(0, 8),
        hash.slice(8, 12),
        hash.slice(12, 16),
        hash.slice(16, 20),
        hash.slice(20, 32),
      ].join('-');

      return {
        id,
        vector: chunk.embedding,
        payload: {
          text: chunk.text,
          sourceFile: chunk.metadata.sourceFile,
          pageNumber: chunk.metadata.pageNumber ?? null,
          sectionTitle: chunk.metadata.sectionTitle ?? null,
          documentType: chunk.metadata.documentType,
          chunkIndex: chunk.metadata.chunkIndex,
          createdAt: chunk.metadata.createdAt,
        },
      };
    });

    await client.upsert(collectionName, { points, wait: true });
    console.log(`[qdrant] Upserted batch ${Math.floor(i / BATCH_SIZE) + 1}: ${batch.length} chunks`);
  }
}
