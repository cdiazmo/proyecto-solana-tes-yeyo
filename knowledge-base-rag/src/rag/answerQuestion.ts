import { retrieveContext } from './retrieveContext.js';
import { buildPrompt } from './buildPrompt.js';
import { generateAnswer } from '../gemini/generateAnswer.js';

export type KnowledgeAnswer = {
  answer: string;
  sources: Array<{
    sourceFile: string;
    pageNumber?: number;
    sectionTitle?: string;
    score: number;
  }>;
  confidence: 'high' | 'medium' | 'low';
  usedChunks: Array<{
    text: string;
    sourceFile: string;
    pageNumber?: number;
    score: number;
  }>;
};

const HIGH_SCORE_THRESHOLD = 0.75;
const MEDIUM_SCORE_THRESHOLD = 0.5;

function calcConfidence(scores: number[]): 'high' | 'medium' | 'low' {
  if (scores.length === 0) return 'low';
  const topScore = scores[0]!;
  if (topScore >= HIGH_SCORE_THRESHOLD) return 'high';
  if (topScore >= MEDIUM_SCORE_THRESHOLD) return 'medium';
  return 'low';
}

/**
 * Main RAG pipeline:
 * 1. Retrieve relevant chunks from Qdrant
 * 2. Build the RAG prompt
 * 3. Call Gemini
 * 4. Return structured answer with sources and confidence
 */
export async function answerQuestion(question: string): Promise<KnowledgeAnswer> {
  if (!question.trim()) {
    throw new Error('Question cannot be empty');
  }

  console.log(`[rag] Question: "${question}"`);

  // Step 1: Retrieve context
  const chunks = await retrieveContext(question);
  console.log(`[rag] Retrieved ${chunks.length} relevant chunks.`);

  if (chunks.length === 0) {
    return {
      answer: 'No he encontrado esa información en la base documental.',
      sources: [],
      confidence: 'low',
      usedChunks: [],
    };
  }

  // Step 2: Build prompt
  const prompt = buildPrompt(question, chunks);

  // Step 3: Generate answer
  const answer = await generateAnswer(prompt);
  console.log(`[rag] Answer generated (${answer.length} chars).`);

  // Step 4: Build response
  const scores = chunks.map((c) => c.score);

  // Deduplicate sources by file
  const sourceMap = new Map<
    string,
    { sourceFile: string; pageNumber?: number; sectionTitle?: string; score: number }
  >();

  for (const chunk of chunks) {
    const key = `${chunk.sourceFile}::${chunk.pageNumber ?? ''}`;
    if (!sourceMap.has(key) || sourceMap.get(key)!.score < chunk.score) {
      sourceMap.set(key, {
        sourceFile: chunk.sourceFile,
        pageNumber: chunk.pageNumber,
        sectionTitle: chunk.sectionTitle,
        score: chunk.score,
      });
    }
  }

  return {
    answer,
    sources: Array.from(sourceMap.values()).sort((a, b) => b.score - a.score),
    confidence: calcConfidence(scores),
    usedChunks: chunks.map((c) => ({
      text: c.text,
      sourceFile: c.sourceFile,
      pageNumber: c.pageNumber,
      score: c.score,
    })),
  };
}
