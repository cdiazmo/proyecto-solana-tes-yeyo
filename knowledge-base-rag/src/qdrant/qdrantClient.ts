import { QdrantClient } from '@qdrant/js-client-rest';
import { config } from '../config.js';

let _client: QdrantClient | null = null;

export function getQdrantClient(): QdrantClient {
  if (!_client) {
    _client = new QdrantClient({ url: config.qdrant.url });
  }
  return _client;
}
