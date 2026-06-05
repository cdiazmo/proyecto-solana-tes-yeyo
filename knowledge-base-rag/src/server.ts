import 'dotenv/config';
import Fastify from 'fastify';
import cors from '@fastify/cors';
import { answerQuestion } from './rag/answerQuestion.js';

const PORT = parseInt(process.env['API_PORT'] ?? '3800', 10);
const API_KEY = process.env['RAG_API_KEY']; // Optional: protect the endpoint

const server = Fastify({ logger: true });

await server.register(cors, {
  origin: true, // Allow all origins — restrict in production if needed
});

// Health check
server.get('/health', async () => {
  return { status: 'ok', service: 'knowledge-base-rag' };
});

// Main RAG endpoint
// POST /ask  { "question": "..." }
server.post<{
  Body: { question: string };
}>(
  '/ask',
  {
    schema: {
      body: {
        type: 'object',
        required: ['question'],
        properties: {
          question: { type: 'string', minLength: 1, maxLength: 2000 },
        },
      },
    },
  },
  async (request, reply) => {
    // Optional API key check
    if (API_KEY) {
      const provided = request.headers['x-api-key'];
      if (provided !== API_KEY) {
        return reply.status(401).send({ error: 'Unauthorized' });
      }
    }

    const { question } = request.body;

    try {
      const result = await answerQuestion(question);
      return result;
    } catch (err) {
      server.log.error(err);
      return reply.status(500).send({ error: 'Internal error processing question' });
    }
  },
);

// Start server
try {
  await server.listen({ port: PORT, host: '0.0.0.0' });
  console.log(`[server] knowledge-base-rag API running on port ${PORT}`);
} catch (err) {
  server.log.error(err);
  process.exit(1);
}
