import { GoogleGenAI } from '@google/genai';
import { config } from '../config.js';

let _client: GoogleGenAI | null = null;

export function getGeminiClient(): GoogleGenAI {
  if (!_client) {
    _client = new GoogleGenAI({ apiKey: config.gemini.apiKey });
  }
  return _client;
}
