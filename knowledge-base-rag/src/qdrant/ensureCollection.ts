import { getQdrantClient } from './qdrantClient.js';
import { config } from '../config.js';

// gemini-embedding-001 produces 768-dimensional vectors
const VECTOR_SIZE = 768;

/**
 * Creates the Qdrant collection if it doesn't already exist.
 * Uses cosine similarity for semantic search.
 */
export async function ensureCollection(): Promise<void> {
  const client = getQdrantClient();
  const collectionName = config.qdrant.collection;

  try {
    await client.getCollection(collectionName);
    console.log(`[qdrant] Collection "${collectionName}" already exists.`);
  } catch {
    // Collection doesn't exist, create it
    await client.createCollection(collectionName, {
      vectors: {
        size: VECTOR_SIZE,
        distance: 'Cosine',
      },
    });

    // Create payload index for faster filtering by source file
    await client.createPayloadIndex(collectionName, {
      field_name: 'sourceFile',
      field_schema: 'keyword',
    });

    console.log(`[qdrant] Collection "${collectionName}" created with vector size ${VECTOR_SIZE}.`);
  }
}
