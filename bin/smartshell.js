#!/usr/bin/env node
/**
 * SmartShell npm wrapper - entry point for `smartshell` command
 * Delegates to PowerShell script
 */

const { spawnSync } = require('child_process');
const path = require('path');

const scriptPath = path.join(__dirname, '..', 'SmartShell.ps1');
const batPath = path.join(__dirname, '..', 'START_SMARTSHELL.bat');

const args = process.argv.slice(2);

// If single arg that looks like a command with spaces, split it
let parsedArgs = args;
if (args.length === 1 && args[0].includes(' ')) {
  parsedArgs = args[0].split(' ').filter(Boolean);
}

function runPowerShell() {
  // Check if PowerShell script exists
  const fs = require('fs');
  if (!fs.existsSync(scriptPath)) {
    console.error('SmartShell.ps1 not found. Run `npm install smartshell` to install.');
    process.exit(1);
  }

  // Build PowerShell command
  const psArgs = ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', scriptPath, ...parsedArgs];
  
  const result = spawnSync('powershell', psArgs, {
    stdio: 'inherit',
    shell: true
  });

  process.exit(result.status ?? 0);
}

function runBatch() {
  const fs = require('fs');
  if (!fs.existsSync(batPath)) {
    console.error('START_SMARTSHELL.bat not found. Run `npm install smartshell` to install.');
    process.exit(1);
  }

  const result = spawnSync(batPath, parsedArgs, {
    stdio: 'inherit',
    shell: true
  });

  process.exit(result.status ?? 0);
}

// Default to PowerShell, fallback to batch if needed
runPowerShell();