# Skill: knowledge-base-rag

## Cuándo usar esta skill

Usa esta skill cuando el usuario pregunte sobre:
- Documentos internos del proyecto (memorias, anejos, planos, pliegos)
- Especificaciones técnicas, normativa, manuales, procedimientos
- PDFs, actas, circulares, reglamentos
- Cualquier información que pueda estar en la base de conocimiento documental
- Preguntas del tipo "¿Qué dice el documento...?", "¿Dónde aparece...?", "¿Cuáles son los requisitos de...?"

## Reglas de comportamiento

1. **Siempre buscar antes de responder.** Antes de generar ninguna respuesta, busca en la base de conocimiento.
2. **Responde solo con el contexto recuperado.** No uses conocimiento externo. No inventes datos.
3. **Cita siempre las fuentes** con el formato: `[archivo, página X]` o `[archivo, sección Y]`.
4. **Si no hay contexto suficiente**, responde: "No he encontrado esa información en la base documental."
5. **Si hay contradicciones entre documentos**, explícalo claramente y muestra ambas fuentes.
6. **Mantén la respuesta breve y directa** salvo que el usuario pida detalle explícitamente.
7. **No devuelvas el texto completo** de los documentos, solo los fragmentos relevantes.

## Cómo invocar la skill

```typescript
import { answerQuestion } from './src/rag/answerQuestion';

const result = await answerQuestion("¿Cuáles son los requisitos de instalación de bombas?");
console.log(result.answer);
console.log(result.sources);
```

## Tipo de respuesta

```typescript
type KnowledgeAnswer = {
  answer: string
  sources: Array<{
    sourceFile: string
    pageNumber?: number
    sectionTitle?: string
    score: number
  }>
  confidence: "high" | "medium" | "low"
  usedChunks: Array<{
    text: string
    sourceFile: string
    pageNumber?: number
    score: number
  }>
}
```

## Integración con Moltbot/OpenClaw

Exporta `answerQuestion` desde el punto de entrada principal (`src/index.ts`) y úsala como handler de la skill. El campo `answer` es la respuesta lista para enviar al usuario. El campo `sources` puede usarse para enriquecer la respuesta con referencias.
