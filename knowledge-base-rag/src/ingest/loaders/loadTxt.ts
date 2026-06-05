import fs from 'fs';

/**
 * Loads a plain text file and returns its content.
 */
export function loadTxt(filePath: string): string {
  return fs.readFileSync(filePath, 'utf-8');
}
