// Generated: 2026-04-02 11:55:15.209707
// Type: Benign JS Sample

// React 应用 - 良性
import React, { useState, useEffect } from 'react';

function App() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    fetch('/api/data')
      .then(res => res.json())
      .then(setData)
      .catch(console.error);
  }, []);
  
  return (
    <div>
      <h1>My App</h1>
      <ul>{data.map(item => <li key={item.id}>{item.name}</li>)}</ul>
    </div>
  );
}

export default App;
