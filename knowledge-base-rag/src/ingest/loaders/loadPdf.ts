import pdfParse from 'pdf-parse-fork';
import fs from 'fs';

export interface PdfPage {
  text: string;
  pageNumber: number;
}

/**
 * Loads a PDF and returns the text split by page.
 * If per-page extraction fails, returns full text as page 1.
 */
export async function loadPdf(filePath: string): Promise<PdfPage[]> {
  const buffer = fs.readFileSync(filePath);

  const pages: PdfPage[] = [];
  let currentPage = 0;

  await pdfParse(buffer, {
    pagerender(pageData: { getTextContent: () => Promise<{ items: Array<{ str: string }> }> }) {
      currentPage++;
      return pageData.getTextContent().then((content) => {
        const pageText = content.items.map((item) => item.str).join(' ');
        pages.push({ text: pageText, pageNumber: currentPage });
        return pageText;
      });
    },
  });

  // Fallback: if page-by-page extraction yielded nothing
  if (pages.length === 0) {
    const result = await pdfParse(buffer);
    if (result.text) {
      pages.push({ text: result.text, pageNumber: 1 });
    }
  }

  return pages.filter((p) => p.text.trim().length > 0);
}
