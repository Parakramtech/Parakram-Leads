import { mkdirSync, writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const root = resolve(__dirname, '..');

const CLOUDFLARED_URL =
  'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe';

async function main() {
  const outDir = resolve(root, 'dist/runtime');
  mkdirSync(outDir, { recursive: true });

  console.log('Downloading cloudflared (win-x64)...');
  const resp = await fetch(CLOUDFLARED_URL, { redirect: 'follow' });
  if (!resp.ok) throw new Error(`Download failed: ${resp.status}`);
  const buffer = Buffer.from(await resp.arrayBuffer());

  if (buffer.subarray(0, 2).toString('latin1') !== 'MZ') {
    throw new Error('Downloaded file is not a valid Windows executable (bad MZ header)');
  }

  const outPath = resolve(outDir, 'cloudflared.exe');
  writeFileSync(outPath, buffer);

  const size = (buffer.length / 1024 / 1024).toFixed(1);
  console.log(`✓ Downloaded cloudflared (${size} MB) to dist/runtime/cloudflared.exe`);
}

main().catch(e => { console.error(e); process.exit(1); });
