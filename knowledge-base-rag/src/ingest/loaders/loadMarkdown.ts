import fs from 'fs';

/**
 * Loads a Markdown file and returns its content.
 * Strips YAML front matter if present.
 */
export function loadMarkdown(filePath: string): string {
  let content = fs.readFileSync(filePath, 'utf-8');

  // Strip YAML front matter (--- ... ---)
  content = content.replace(/^---[\s\S]*?---\n?/, '').trim();

  return content;
}
