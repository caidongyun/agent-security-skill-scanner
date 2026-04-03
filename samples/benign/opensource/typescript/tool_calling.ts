// Source: TypeScript Benign Sample
// Generated: 2026-04-02 11:48:04.520082

#!/usr/bin/env ts-node
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
