// Type definitions for @caidongyun/security-scanner v6.2.0

declare module '@caidongyun/security-scanner' {
  export interface ScanResult {
    file: string;
    detected: boolean;
    score: number;
    findings_count: number;
    risk_level: 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    matched_rules: string[];
    whitelist_applied: boolean;
    is_config_file: boolean;
    layer1_result: {
      matches: [string, string, number][];
      max_weight: number;
      attack_types: string[];
      hit_count: number;
      layer: string;
    };
    layer2_result: {
      hit_count: number;
      matches: Array<{
        rule_id: string;
        category: string;
        confidence: number;
        name: string;
      }>;
    };
  }

  export interface ScanReport {
    summary: {
      total_files: number;
      detected: number;
      safe: number;
      detection_rate: number;
      scan_time: string;
      timeout_count: number;
      timeout_rate: number;
    };
    config: {
      version: string;
      rules_count: number;
      extensions: string;
      max_files: number;
      llm_enabled: boolean;
      llm_model: string | null;
      priority_scan: boolean;
      timeout_tracking: boolean;
    };
    risk_distribution: {
      CRITICAL: number;
      HIGH: number;
      MEDIUM: number;
      LOW: number;
      SAFE: number;
    };
  }

  export interface ScannerOptions {
    extensions?: string[];
    maxDepth?: number;
    maxFiles?: number;
    output?: 'text' | 'json';
    workers?: number;
    llmEnabled?: boolean;
    llmModel?: string;
  }

  export class SecurityScanner {
    constructor(options?: ScannerOptions);
    scanFile(filePath: string): Promise<ScanResult>;
    scanDirectory(dirPath: string, options?: ScannerOptions): Promise<ScanReport>;
  }

  export class ConfigFileDetector {
    isConfigFile(filePath: string, content: string): boolean;
    hasMaliciousConfig(filePath: string, content: string): boolean;
    classifyFile(filePath: string, content: string): [string, string];
  }
}
