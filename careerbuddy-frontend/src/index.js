import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';

// Add this line
require('events').EventEmitter.defaultMaxListeners = 15;

const root = createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);