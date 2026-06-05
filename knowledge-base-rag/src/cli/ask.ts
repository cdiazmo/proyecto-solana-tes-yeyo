import 'dotenv/config';
import { answerQuestion } from '../rag/answerQuestion.js';

async function main() {
  const question = process.argv.slice(2).join(' ').trim();

  if (!question) {
    console.error('Usage: npm run ask "your question here"');
    process.exit(1);
  }

  try {
    const result = await answerQuestion(question);

    console.log('\n' + '='.repeat(60));
    console.log('PREGUNTA:', question);
    console.log('='.repeat(60));
    console.log('\nRESPUESTA:\n');
    console.log(result.answer);
    console.log('\n' + '-'.repeat(60));
    console.log(`Confianza: ${result.confidence.toUpperCase()}`);

    if (result.sources.length > 0) {
      console.log('\nFUENTES CONSULTADAS:');
      for (const src of result.sources) {
        const page = src.pageNumber ? `, página ${src.pageNumber}` : '';
        const score = (src.score * 100).toFixed(1);
        console.log(`  • ${src.sourceFile}${page} (relevancia: ${score}%)`);
      }
    }

    console.log('='.repeat(60) + '\n');
    process.exit(0);
  } catch (err) {
    console.error('[ask] Error:', err);
    process.exit(1);
  }
}

main();
