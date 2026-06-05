export type DocumentType = 'pdf' | 'txt' | 'markdown' | 'docx';

export interface ChunkMetadata {
  sourceFile: string;       // Relative path from KNOWLEDGE_DOCS_PATH
  pageNumber?: number;      // Page number for PDFs
  sectionTitle?: string;    // Detected section title if available
  documentType: DocumentType;
  chunkIndex: number;       // 0-based index within the document
  createdAt: string;        // ISO 8601 timestamp
}

export interface TextChunk {
  text: string;
  metadata: ChunkMetadata;
}

export interface ChunkWithEmbedding extends TextChunk {
  embedding: number[];
}

/**
 * Builds a ChunkMetadata object for a given document chunk.
 */
export function buildMetadata(
  sourceFile: string,
  documentType: DocumentType,
  chunkIndex: number,
  pageNumber?: number,
  sectionTitle?: string,
): ChunkMetadata {
  return {
    sourceFile,
    documentType,
    chunkIndex,
    pageNumber,
    sectionTitle,
    createdAt: new Date().toISOString(),
  };
}
