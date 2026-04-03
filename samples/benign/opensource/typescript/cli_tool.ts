// Source: TypeScript Benign Sample
// Generated: 2026-04-02 11:48:04.520201

#!/usr/bin/env ts-node
/**
 * CLI 工具 - 良性
 */
import { Command } from 'commander';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

const program = new Command();

program
  .name('my-cli')
  .description('A CLI tool')
  .version('1.0.0');

program
  .command('build')
  .description('Build the project')
  .action(async () => {
    const { stdout } = await execAsync('npm run build');
    console.log(stdout);
  });

program.parse();
