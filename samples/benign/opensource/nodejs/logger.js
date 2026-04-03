// Generated: 2026-04-02 12:15:22.314098\n// Type: Benign JS Sample\n\n// 日志工具 - 良性
const fs = require('fs');
const path = require('path');

class Logger {
  constructor(logFile = 'app.log') {
    this.logFile = path.join(__dirname, logFile);
  }
  
  info(message) {
    this.log('INFO', message);
  }
  
  error(message) {
    this.log('ERROR', message);
  }
  
  log(level, message) {
    const timestamp = new Date().toISOString();
    const logLine = `[${timestamp}] [${level}] ${message}\n`;
    fs.appendFileSync(this.logFile, logLine);
    console.log(logLine.trim());
  }
}

module.exports = Logger;
