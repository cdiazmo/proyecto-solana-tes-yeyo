import fs from 'node:fs/promises';
import path from 'node:path';

const ROOT = process.cwd();
const OUT = path.join(ROOT, '.yeyo-index');
const TOP_OUT = path.join(OUT, 'top-level');

const IGNORED_DIRS = new Set([
  '.git',
  '.venv',
  '.venv312',
  '.yeyo-agents',
  '.yeyo-index',
  '.yeyo-memory',
  'knowledge-base-rag',
  'node_modules',
  '__pycache__',
]);

const IGNORED_FILES = new Set([
  '.DS_Store',
  '.gitignore',
  'AGENTS.md',
  'PROPUESTA-SISTEMA-MULTIAGENTE.md',
  'indice-documental.html',
]);

function humanSize(bytes) {
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let size = bytes;
  let unit = 0;
  while (size >= 1024 && unit < units.length - 1) {
    size /= 1024;
    unit += 1;
  }
  return `${size.toFixed(size >= 10 || unit === 0 ? 0 : 1)} ${units[unit]}`;
}

function csvEscape(value) {
  const s = String(value ?? '');
  return /[",\n]/.test(s) ? `"${s.replaceAll('"', '""')}"` : s;
}

function sanitizeName(value) {
  return value
    .replaceAll(/[^\p{L}\p{N}._-]+/gu, '_')
    .replaceAll(/^_+|_+$/g, '')
    .slice(0, 120) || 'root';
}

async function walk(dir, relBase = '') {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    if (entry.isDirectory()) {
      if (IGNORED_DIRS.has(entry.name)) continue;
      const nested = await walk(path.join(dir, entry.name), path.join(relBase, entry.name));
      files.push(...nested);
      continue;
    }
    if (!entry.isFile()) continue;
    if (relBase === '' && IGNORED_FILES.has(entry.name)) continue;
    const relPath = path.join(relBase, entry.name);
    const fullPath = path.join(dir, entry.name);
    const stat = await fs.stat(fullPath);
    const topDir = relPath.split(path.sep)[0] || '.';
    const ext = path.extname(entry.name).slice(1).toLowerCase() || '[no_ext]';
    files.push({
      path: relPath,
      size_bytes: stat.size,
      size_human: humanSize(stat.size),
      ext,
      top_dir: topDir,
      depth: relPath.split(path.sep).length - 1,
      mtime_iso: stat.mtime.toISOString(),
    });
  }
  return files;
}

function summarize(files) {
  const topDirs = new Map();
  const extCounts = new Map();
  for (const file of files) {
    const top = file.top_dir;
    const topSummary = topDirs.get(top) ?? { files: 0, bytes: 0 };
    topSummary.files += 1;
    topSummary.bytes += file.size_bytes;
    topDirs.set(top, topSummary);

    extCounts.set(file.ext, (extCounts.get(file.ext) ?? 0) + 1);
  }

  const topDirsRows = [...topDirs.entries()]
    .map(([top_dir, data]) => ({ top_dir, files: data.files, bytes: data.bytes, size_human: humanSize(data.bytes) }))
    .sort((a, b) => b.bytes - a.bytes || a.top_dir.localeCompare(b.top_dir));

  const extRows = [...extCounts.entries()]
    .map(([ext, files]) => ({ ext, files }))
    .sort((a, b) => b.files - a.files || a.ext.localeCompare(b.ext));

  return { topDirsRows, extRows };
}

async function writeCsv(filePath, rows, columns) {
  const lines = [columns.join(',')];
  for (const row of rows) {
    lines.push(columns.map((column) => csvEscape(row[column])).join(','));
  }
  await fs.writeFile(filePath, `${lines.join('\n')}\n`, 'utf8');
}

async function main() {
  await fs.mkdir(TOP_OUT, { recursive: true });
  const files = await walk(ROOT);
  files.sort((a, b) => a.path.localeCompare(b.path));

  const { topDirsRows, extRows } = summarize(files);
  const totalBytes = files.reduce((sum, file) => sum + file.size_bytes, 0);

  const manifest = {
    generated_at: new Date().toISOString(),
    root: ROOT,
    file_count: files.length,
    total_bytes: totalBytes,
    total_size_human: humanSize(totalBytes),
    top_level_count: topDirsRows.length,
  };

  await fs.mkdir(OUT, { recursive: true });
  await fs.writeFile(path.join(OUT, 'manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');
  await writeCsv(path.join(OUT, 'files.csv'), files, ['path', 'size_bytes', 'size_human', 'ext', 'top_dir', 'depth', 'mtime_iso']);
  await writeCsv(path.join(OUT, 'top-level-summary.csv'), topDirsRows, ['top_dir', 'files', 'bytes', 'size_human']);
  await writeCsv(path.join(OUT, 'extensions.csv'), extRows, ['ext', 'files']);

  const grouped = new Map();
  for (const file of files) {
    const key = file.top_dir;
    const bucket = grouped.get(key) ?? [];
    bucket.push(file);
    grouped.set(key, bucket);
  }

  for (const [topDir, bucket] of grouped.entries()) {
    const dirName = `${sanitizeName(topDir)}.csv`;
    await writeCsv(path.join(TOP_OUT, dirName), bucket, ['path', 'size_bytes', 'size_human', 'ext', 'depth', 'mtime_iso']);
  }

  const summaryMd = [
    '# Document index',
    '',
    `- Generated: ${manifest.generated_at}`,
    `- Files: ${manifest.file_count}`,
    `- Total size: ${manifest.total_size_human}`,
    `- Top-level folders: ${manifest.top_level_count}`,
    '',
    '## Top-level folders by size',
    '',
    '| Folder | Files | Size |',
    '|---|---:|---:|',
    ...topDirsRows.map((row) => `| ${row.top_dir} | ${row.files} | ${row.size_human} |`),
    '',
    '## Extensions',
    '',
    '| Ext | Files |',
    '|---|---:|',
    ...extRows.map((row) => `| ${row.ext} | ${row.files} |`),
    '',
    '## Layout',
    '',
    '- `manifest.json`: compact summary for quick loading',
    '- `files.csv`: full file inventory',
    '- `top-level-summary.csv`: one row per top-level folder',
    '- `extensions.csv`: extension distribution',
    '- `top-level/*.csv`: per-folder slices to reduce reprocessing',
  ].join('\n');

  await fs.writeFile(path.join(OUT, 'README.md'), `${summaryMd}\n`, 'utf8');
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
