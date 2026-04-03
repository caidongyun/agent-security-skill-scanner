// Source: TypeScript Benign Sample
// Generated: 2026-04-02 11:48:04.520236

/**
 * 类型定义文件 - 良性
 */
export interface AgentConfig {
  name: string;
  model: string;
  temperature?: number;
}

export interface ToolDefinition {
  name: string;
  description: string;
  parameters: Record<string, any>;
}

export type AgentResponse = {
  success: boolean;
  data?: any;
  error?: string;
};
