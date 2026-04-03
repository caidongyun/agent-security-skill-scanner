// Source: TypeScript Benign Sample
// Generated: 2026-04-02 11:48:04.520272

#!/usr/bin/env ts-node
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
