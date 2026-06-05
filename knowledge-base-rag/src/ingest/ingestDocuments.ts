import fs from 'fs';
import path from 'path';
import { config } from '../config.js';
import { chunkText } from './chunkText.js';
import { buildMetadata, type TextChunk, type ChunkWithEmbedding } from './metadata.js';
import { loadPdf } from './loaders/loadPdf.js';
import { loadTxt } from './loaders/loadTxt.js';
import { loadMarkdown } from './loaders/loadMarkdown.js';
import { loadDocx } from './loaders/loadDocx.js';
import { embedBatch } from '../gemini/embeddings.js';
import { ensureCollection } from '../qdrant/ensureCollection.js';
import { upsertChunks } from '../qdrant/upsertChunks.js';

const SUPPORTED_EXTENSIONS = new Set(['.pdf', '.txt', '.md', '.markdown', '.docx']);
const MAX_BYTES = config.knowledge.maxDocSizeMb * 1024 * 1024;

/**
 * Scans KNOWLEDGE_DOCS_PATH recursively and returns all supported file paths.
 * Enforces that all paths stay within the configured root (path traversal protection).
 */
function collectFiles(rootDir: string): string[] {
  const results: string[] = [];

  const walk = (dir: string) => {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.resolve(dir, entry.name);

      // Security: reject any path that escapes the root
      if (!fullPath.startsWith(rootDir)) {
        console.warn(`[ingest] Skipping suspicious path: ${fullPath}`);
        continue;
      }

      if (entry.isDirectory()) {
        walk(fullPath);
      } else if (entry.isFile()) {
        const ext = path.extname(entry.name).toLowerCase();
        if (SUPPORTED_EXTENSIONS.has(ext)) {
          results.push(fullPath);
        }
      }
    }
  };

  walk(rootDir);
  return results;
}

/**
 * Processes a single file into text chunks with metadata.
 */
async function processFile(filePath: string, rootDir: string): Promise<TextChunk[]> {
  const stat = fs.statSync(filePath);
  if (stat.size > MAX_BYTES) {
    console.warn(
      `[ingest] Skipping ${filePath}: size ${(stat.size / 1024 / 1024).toFixed(1)} MB exceeds limit of ${config.knowledge.maxDocSizeMb} MB`,
    );
    return [];
  }

  const relPath = path.relative(rootDir, filePath);
  const ext = path.extname(filePath).toLowerCase();
  const chunks: TextChunk[] = [];

  try {
    if (ext === '.pdf') {
      const pages = await loadPdf(filePath);
      for (const page of pages) {
        const textChunks = chunkText(page.text);
        textChunks.forEach((text, i) => {
          chunks.push({
            text,
            metadata: buildMetadata(relPath, 'pdf', i, page.pageNumber),
          });
        });
      }
    } else if (ext === '.txt') {
      const text = loadTxt(filePath);
      chunkText(text).forEach((chunk, i) => {
        chunks.push({ text: chunk, metadata: buildMetadata(relPath, 'txt', i) });
      });
    } else if (ext === '.md' || ext === '.markdown') {
      const text = loadMarkdown(filePath);
      chunkText(text).forEach((chunk, i) => {
        chunks.push({ text: chunk, metadata: buildMetadata(relPath, 'markdown', i) });
      });
    } else if (ext === '.docx') {
      const text = await loadDocx(filePath);
      chunkText(text).forEach((chunk, i) => {
        chunks.push({ text: chunk, metadata: buildMetadata(relPath, 'docx', i) });
      });
    }
  } catch (err) {
    console.error(`[ingest] Error processing ${filePath}:`, err);
  }

  return chunks;
}

/**
 * Main ingestion pipeline:
 * 1. Collect files from KNOWLEDGE_DOCS_PATH
 * 2. Extract and chunk text
 * 3. Generate embeddings in batches
 * 4. Upsert into Qdrant
 */
export async function ingestDocuments(): Promise<void> {
  const rootDir = path.resolve(config.knowledge.docsPath);

  if (!fs.existsSync(rootDir)) {
    throw new Error(`KNOWLEDGE_DOCS_PATH does not exist: ${rootDir}`);
  }

  console.log(`[ingest] Starting ingestion from: ${rootDir}`);
  await ensureCollection();

  const files = collectFiles(rootDir);
  console.log(`[ingest] Found ${files.length} supported files.`);

  let totalChunks = 0;

  for (let fi = 0; fi < files.length; fi++) {
    const filePath = files[fi]!;
    const relPath = path.relative(rootDir, filePath);
    console.log(`[ingest] [${fi + 1}/${files.length}] Processing: ${relPath}`);

    const textChunks = await processFile(filePath, rootDir);
    if (textChunks.length === 0) continue;

    // Generate embeddings in batch for this document
    const texts = textChunks.map((c) => c.text);
    console.log(`[ingest]   → ${textChunks.length} chunks, generating embeddings...`);
    const embeddings = await embedBatch(texts);

    const chunksWithEmbeddings: ChunkWithEmbedding[] = textChunks.map((chunk, i) => ({
      ...chunk,
      embedding: embeddings[i]!,
    }));

    await upsertChunks(chunksWithEmbeddings);
    totalChunks += textChunks.length;
    console.log(`[ingest]   → Done. Total chunks so far: ${totalChunks}`);
  }

  console.log(`[ingest] Ingestion complete. Total chunks indexed: ${totalChunks}`);
}
