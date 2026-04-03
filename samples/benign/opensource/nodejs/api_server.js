// Generated: 2026-04-02 11:55:15.209802
// Type: Benign JS Sample

// Express API 服务器 - 良性
const express = require('express');
const app = express();

app.use(express.json());

app.get('/api/users', (req, res) => {
  res.json([{ id: 1, name: 'Alice' }]);
});

app.post('/api/users', (req, res) => {
  const user = req.body;
  res.status(201).json(user);
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
