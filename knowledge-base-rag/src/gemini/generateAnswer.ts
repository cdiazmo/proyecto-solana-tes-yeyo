import { getGeminiClient } from './geminiClient.js';
import { config } from '../config.js';

/**
 * Generates an answer from Gemini given a fully constructed RAG prompt.
 */
export async function generateAnswer(prompt: string): Promise<string> {
  const client = getGeminiClient();

  const response = await client.models.generateContent({
    model: config.gemini.model,
    contents: [{ role: 'user', parts: [{ text: prompt }] }],
    config: {
      temperature: 0.2,      // Low temperature for factual accuracy
      maxOutputTokens: 2048,
    },
  });

  const text = response.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!text) {
    throw new Error('Gemini returned an empty response');
  }

  return text.trim();
}
