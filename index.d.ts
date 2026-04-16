// Type definitions for @openclaw/security-scanner v6.1.0

declare module '@openclaw/security-scanner' {
  export interface ScanResult {
    file: string;
    detected: boolean;
    score: number;
    findings_count: number;
    risk_level: 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    matched_rules: string[];
    whitelist_applied: boolean;
  }

  export interface ScanReport {
    results: ScanResult[];
    summary: {
      total_files: number;
      detected: number;
      safe: number;
      detection_rate: number;
    };
  }

  export interface ScannerOptions {
    extensions?: string[];
    maxDepth?: number;
    maxFiles?: number;
    output?: 'text' | 'json';
    workers?: number;
  }

  export class SecurityScanner {
    constructor(options?: ScannerOptions);
    scanFile(filePath: string): Promise<ScanResult>;
    scanDirectory(dirPath: string): Promise<ScanReport>;
  }

  export class ConfigFileDetector {
    isConfigFile(filePath: string, content: string): boolean;
    hasMaliciousConfig(filePath: string, content: string): boolean;
    classifyFile(filePath: string, content: string): [string, string];
  }
}
