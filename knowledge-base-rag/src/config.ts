import 'dotenv/config';
import path from 'path';

function requireEnv(key: string): string {
  const val = process.env[key];
  if (!val) throw new Error(`Missing required environment variable: ${key}`);
  return val;
}

export const config = {
  gemini: {
    apiKey: requireEnv('GEMINI_API_KEY'),
    model: process.env['GEMINI_MODEL'] ?? 'gemini-3.1-flash-lite',
    embeddingModel: process.env['GEMINI_EMBEDDING_MODEL'] ?? 'gemini-embedding-001',
  },
  qdrant: {
    url: process.env['QDRANT_URL'] ?? 'http://localhost:6333',
    collection: process.env['QDRANT_COLLECTION'] ?? 'knowledge_base',
  },
  knowledge: {
    docsPath: path.resolve(process.env['KNOWLEDGE_DOCS_PATH'] ?? './docs'),
    topK: parseInt(process.env['TOP_K'] ?? '8', 10),
    chunkSize: parseInt(process.env['CHUNK_SIZE'] ?? '1200', 10),
    chunkOverlap: parseInt(process.env['CHUNK_OVERLAP'] ?? '200', 10),
    maxDocSizeMb: parseInt(process.env['MAX_DOC_SIZE_MB'] ?? '50', 10),
  },
} as const;
