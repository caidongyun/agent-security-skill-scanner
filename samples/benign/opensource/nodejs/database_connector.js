// Generated: 2026-04-02 12:15:22.314043\n// Type: Benign JS Sample\n\n// 数据库连接工具 - 良性
const { Pool } = require('pg');

class Database {
  constructor(connectionString) {
    this.pool = new Pool({ connectionString });
  }
  
  async query(text, params) {
    const client = await this.pool.connect();
    try {
      const result = await client.query(text, params);
      return result.rows;
    } finally {
      client.release();
    }
  }
  
  async close() {
    await this.pool.end();
  }
}

module.exports = Database;
