// Source: TypeScript Benign Sample
// Generated: 2026-04-02 11:48:04.520503

/**
 * 日志记录器 - 良性
 */
import * as fs from 'fs';
import * as path from 'path';

class Logger {
  private logFile: string;
  
  constructor(logPath: string) {
    this.logFile = logPath;
  }
  
  info(message: string): void {
    this.log('INFO', message);
  }
  
  error(message: string): void {
    this.log('ERROR', message);
  }
  
  private log(level: string, message: string): void {
    const timestamp = new Date().toISOString();
    const logLine = `[${timestamp}] [${level}] ${message}\n`;
    fs.appendFileSync(this.logFile, logLine);
  }
}

const logger = new Logger('app.log');
