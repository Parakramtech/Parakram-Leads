import { mkdirSync, writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const root = resolve(__dirname, '..');

const WINSW_URL =
  'https://github.com/winsw/winsw/releases/latest/download/WinSW-x64.exe';

async function main() {
  const outDir = resolve(root, 'dist/runtime');
  mkdirSync(outDir, { recursive: true });

  console.log('Downloading WinSW (Windows Service Wrapper, win-x64)...');
  const resp = await fetch(WINSW_URL, { redirect: 'follow' });
  if (!resp.ok) throw new Error(`Download failed: ${resp.status}`);
  const buffer = Buffer.from(await resp.arrayBuffer());

  if (buffer.subarray(0, 2).toString('latin1') !== 'MZ') {
    throw new Error('Downloaded file is not a valid Windows executable (bad MZ header)');
  }

  const outPath = resolve(outDir, 'ParakramVPS-svc.exe');
  writeFileSync(outPath, buffer);

  const size = (buffer.length / 1024 / 1024).toFixed(1);
  console.log(`✓ Downloaded WinSW (${size} MB) to dist/runtime/ParakramVPS-svc.exe`);
}

main().catch(e => { console.error(e); process.exit(1); });
