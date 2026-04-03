// Source: TypeScript Benign Sample
// Generated: 2026-04-02 11:48:04.520467

#!/usr/bin/env ts-node
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
