import { getGeminiClient } from './geminiClient.js';
import { config } from '../config.js';

/**
 * Generates an embedding vector for the given text using Gemini.
 * Returns a float array (1536 dims for gemini-embedding-001).
 */
export async function embedText(text: string): Promise<number[]> {
  const client = getGeminiClient();

  const response = await client.models.embedContent({
    model: config.gemini.embeddingModel,
    contents: text,
  });

  const values = response.embeddings?.[0]?.values;
  if (!values || values.length === 0) {
    throw new Error('Gemini embedding returned empty values');
  }

  return values;
}

/**
 * Generates embeddings for multiple texts in batch.
 * Processes sequentially to respect rate limits.
 */
export async function embedBatch(texts: string[]): Promise<number[][]> {
  const results: number[][] = [];
  for (let i = 0; i < texts.length; i++) {
    const embedding = await embedText(texts[i]!);
    results.push(embedding);
    // Small delay to avoid hitting rate limits on large batches
    if (i < texts.length - 1) {
      await new Promise((r) => setTimeout(r, 100));
    }
  }
  return results;
}
