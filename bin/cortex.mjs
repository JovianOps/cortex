#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const scriptPath = path.resolve(__dirname, '..', 'scripts', 'cortex.py');
const args = [scriptPath, ...process.argv.slice(2)];

const candidates = process.platform === 'win32' ? ['python', 'py', 'python3'] : ['python3', 'python'];
for (const bin of candidates) {
  const res = spawnSync(bin, args, { stdio: 'inherit' });
  if (!res.error) {
    if (res.signal) {
      process.kill(process.pid, res.signal);
    }
    process.exit(res.status ?? 0);
  }
}

console.error('ERROR: Python 3 is required to run the Cortex CLI (`cortex`).');
process.exit(1);
