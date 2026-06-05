import 'dotenv/config';
import { ingestDocuments } from '../ingest/ingestDocuments.js';

async function main() {
  try {
    await ingestDocuments();
    process.exit(0);
  } catch (err) {
    console.error('[ingest] Fatal error:', err);
    process.exit(1);
  }
}

main();
