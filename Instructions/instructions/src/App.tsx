// src/App.tsx

import React from 'react';
import TaskTimer from './TaskTimer';
import './App.css';

const App: React.FC = () => {
  return (
    <div className="App">
      <TaskTimer />
    </div>
  );
};

export default App;