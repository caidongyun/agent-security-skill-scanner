#!/usr/bin/env node

/**
 * Agent Security Scanner - npm CLI Entry Point
 * 
 * Wraps the Python scanner for npm users
 */

const { spawn } = require('child_process');
const path = require('path');

// Get Python scanner path
const SCANNER_PATH = path.join(__dirname, 'scanner.py');

// Get command line arguments (skip node and script path)
const args = process.argv.slice(2);

// Spawn Python process
const python = spawn('python3', [SCANNER_PATH, ...args], {
  stdio: 'inherit',
  cwd: process.cwd()
});

// Handle process exit
python.on('close', (code) => {
  process.exit(code);
});

// Handle errors
python.on('error', (err) => {
  console.error('Failed to start Python scanner:', err.message);
  console.error('Please ensure Python 3.7+ is installed.');
  process.exit(1);
});
