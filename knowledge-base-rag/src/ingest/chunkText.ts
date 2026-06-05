import { config } from '../config.js';

/**
 * Splits text into overlapping chunks of roughly CHUNK_SIZE characters.
 * Tries to split on paragraph boundaries first, then sentence boundaries,
 * then falls back to hard character split.
 */
export function chunkText(
  text: string,
  chunkSize = config.knowledge.chunkSize,
  overlap = config.knowledge.chunkOverlap,
): string[] {
  const cleanText = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n').trim();

  if (cleanText.length <= chunkSize) {
    return cleanText ? [cleanText] : [];
  }

  const chunks: string[] = [];
  let start = 0;

  while (start < cleanText.length) {
    let end = Math.min(start + chunkSize, cleanText.length);

    if (end < cleanText.length) {
      // Try to break at paragraph boundary (\n\n)
      const paragraphBreak = cleanText.lastIndexOf('\n\n', end);
      if (paragraphBreak > start + chunkSize / 2) {
        end = paragraphBreak + 2;
      } else {
        // Try sentence boundary (. followed by space or newline)
        const sentenceBreak = cleanText.lastIndexOf('. ', end);
        if (sentenceBreak > start + chunkSize / 2) {
          end = sentenceBreak + 2;
        } else {
          // Try word boundary (space)
          const wordBreak = cleanText.lastIndexOf(' ', end);
          if (wordBreak > start + chunkSize / 2) {
            end = wordBreak + 1;
          }
          // else: hard cut at chunkSize
        }
      }
    }

    const chunk = cleanText.slice(start, end).trim();
    if (chunk) {
      chunks.push(chunk);
    }

    // Move forward by (chunkSize - overlap)
    start = end - overlap;
    if (start <= 0) start = end; // safety guard
  }

  return chunks;
}
