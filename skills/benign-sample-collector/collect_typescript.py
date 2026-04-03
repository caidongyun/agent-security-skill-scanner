#!/usr/bin/env python3
"""
TypeScript 良性样本采集器
"""
import os
from datetime import datetime

OUTPUT_DIR = 'samples/benign/opensource/typescript'

def ensure_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f'✅ 目录：{OUTPUT_DIR}')

def generate_typescript_samples():
    """生成 TypeScript 良性样本"""
    
    samples = {
        # Agent 框架示例
        'agent_example.ts': '''#!/usr/bin/env ts-node
/**
 * LangChain.js Agent 示例 - 良性
 */
import { ChatOpenAI } from "@langchain/openai";
import { AgentExecutor, createOpenAIFunctionsAgent } from "langchain/agents";

const model = new ChatOpenAI({ temperature: 0 });
const tools = [];

const agent = createOpenAIFunctionsAgent({
  llm: model,
  tools,
  prompt: null,
});

const executor = new AgentExecutor({
  agent,
  tools,
});

console.log("Agent initialized");
''',
        
        'tool_calling.ts': '''#!/usr/bin/env ts-node
/**
 * Tool Calling 示例 - 良性
 */
import axios from 'axios';

async function callTool(toolName: string, params: any) {
  const response = await axios.post(`http://localhost:3000/tools/${toolName}`, params);
  return response.data;
}

async function main() {
  const result = await callTool('search', { query: 'hello' });
  console.log(result);
}

main();
''',
        
        # NestJS Web 服务器
        'nestjs_app.ts': '''#!/usr/bin/env ts-node
/**
 * NestJS Web 应用 - 良性
 */
import { NestFactory } from '@nestjs/core';
import { Controller, Get, Module } from '@nestjs/common';

@Controller()
class AppController {
  @Get()
  getHello(): string {
    return 'Hello World!';
  }
}

@Module({
  controllers: [AppController],
})
class AppModule {}

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  await app.listen(3000);
  console.log('Server running on port 3000');
}

bootstrap();
''',
        
        # Fastify 服务器
        'fastify_server.ts': '''#!/usr/bin/env ts-node
/**
 * Fastify 服务器 - 良性
 */
import Fastify from 'fastify';

const fastify = Fastify({ logger: true });

fastify.get('/', async (request, reply) => {
  return { hello: 'world' };
});

const start = async () => {
  try {
    await fastify.listen({ port: 3000 });
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();
''',
        
        # CLI 工具
        'cli_tool.ts': '''#!/usr/bin/env ts-node
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
''',
        
        # 类型定义
        'types.ts': '''/**
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
''',
        
        # 数据处理
        'data_processor.ts': '''#!/usr/bin/env ts-node
/**
 * 数据处理 - 良性
 */
import * as fs from 'fs';
import * as path from 'path';

interface DataRecord {
  id: number;
  name: string;
  value: number;
}

async function processData(inputPath: string): Promise<void> {
  const content = await fs.promises.readFile(inputPath, 'utf-8');
  const records: DataRecord[] = JSON.parse(content);
  
  const processed = records
    .filter(r => r.value > 0)
    .map(r => ({ ...r, value: r.value * 2 }));
  
  console.log(`Processed ${processed.length} records`);
}

processData('data.json');
''',
        
        # API 客户端
        'api_client.ts': '''#!/usr/bin/env ts-node
/**
 * API 客户端 - 良性
 */
import axios, { AxiosInstance } from 'axios';

class ApiClient {
  private client: AxiosInstance;
  
  constructor(baseUrl: string, apiKey: string) {
    this.client = axios.create({
      baseURL: baseUrl,
      headers: {
        'Authorization': `Bearer ${apiKey}`,
      },
    });
  }
  
  async getData(endpoint: string): Promise<any> {
    const response = await this.client.get(endpoint);
    return response.data;
  }
  
  async postData(endpoint: string, data: any): Promise<any> {
    const response = await this.client.post(endpoint, data);
    return response.data;
  }
}

const client = new ApiClient('https://api.example.com', 'your-api-key');
''',
        
        # 测试文件
        'app.test.ts': '''/**
 * 测试文件 - 良性
 */
import { describe, it, expect } from '@jest/globals';

describe('App', () => {
  it('should return hello', () => {
    expect('hello').toBe('hello');
  });
  
  it('should add numbers', () => {
    expect(1 + 1).toBe(2);
  });
});
''',
        
        # 配置文件
        'vite.config.ts': '''/**
 * Vite 配置 - 良性
 */
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8080',
    },
  },
});
''',
        
        # 工具函数
        'utils.ts': '''/**
 * 工具函数 - 良性
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function formatBytes(bytes: number): string {
  const units = ['B', 'KB', 'MB', 'GB'];
  let unitIndex = 0;
  let size = bytes;
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  
  return `${size.toFixed(2)} ${units[unitIndex]}`;
}
''',
        
        # 数据库操作
        'database.ts': '''#!/usr/bin/env ts-node
/**
 * 数据库操作 - 良性
 */
import { Client } from 'pg';

async function queryDatabase() {
  const client = new Client({
    host: 'localhost',
    port: 5432,
    database: 'mydb',
    user: 'user',
    password: process.env.DB_PASSWORD,
  });
  
  await client.connect();
  
  const result = await client.query('SELECT * FROM users WHERE active = $1', [true]);
  console.log(`Found ${result.rows.length} active users`);
  
  await client.end();
}

queryDatabase();
''',
        
        # 日志记录
        'logger.ts': '''/**
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
    const logLine = `[${timestamp}] [${level}] ${message}\\n`;
    fs.appendFileSync(this.logFile, logLine);
  }
}

const logger = new Logger('app.log');
''',
        
        # 事件总线
        'event_bus.ts': '''/**
 * 事件总线 - 良性
 */
type EventHandler = (data: any) => void;

class EventBus {
  private handlers: Map<string, Set<EventHandler>> = new Map();
  
  on(event: string, handler: EventHandler): void {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set());
    }
    this.handlers.get(event)!.add(handler);
  }
  
  emit(event: string, data: any): void {
    const handlers = this.handlers.get(event);
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  }
  
  off(event: string, handler: EventHandler): void {
    const handlers = this.handlers.get(event);
    if (handlers) {
      handlers.delete(handler);
    }
  }
}

export default new EventBus();
''',
        
        # 中间件
        'middleware.ts': '''/**
 * Express 中间件 - 良性
 */
import { Request, Response, NextFunction } from 'express';

export function loggingMiddleware(req: Request, res: Response, next: NextFunction) {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(`${req.method} ${req.path} ${res.statusCode} ${duration}ms`);
  });
  
  next();
}

export function authMiddleware(req: Request, res: Response, next: NextFunction) {
  const token = req.headers.authorization;
  
  if (!token) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  
  // Verify token logic here
  next();
}
''',
    }
    
    # 写入文件
    count = 0
    for filename, content in samples.items():
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f'// Source: TypeScript Benign Sample\n')
            f.write(f'// Generated: {datetime.now()}\n\n')
            f.write(content)
        count += 1
    
    print(f'✅ 生成 {count} 个 TypeScript 样本')
    return count

if __name__ == '__main__':
    print('='*60)
    print('📘 TypeScript 良性样本生成器')
    print('='*60)
    print()
    
    ensure_dir()
    generate_typescript_samples()
    
    print()
    print('='*60)
    print('✅ TypeScript 样本生成完成!')
    print('='*60)
