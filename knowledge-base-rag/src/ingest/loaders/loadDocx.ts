import mammoth from 'mammoth';

/**
 * Loads a DOCX file and extracts plain text using mammoth.
 * Preserves paragraph structure by using the raw text extraction.
 */
export async function loadDocx(filePath: string): Promise<string> {
  const result = await mammoth.extractRawText({ path: filePath });

  if (result.messages.length > 0) {
    const warnings = result.messages
      .filter((m) => m.type === 'warning')
      .map((m) => m.message);
    if (warnings.length > 0) {
      console.warn(`[loadDocx] Warnings for ${filePath}:`, warnings.join(', '));
    }
  }

  return result.value.trim();
}
