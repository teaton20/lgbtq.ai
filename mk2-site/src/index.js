import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { GlobalStateProvider } from './state/GlobalStateContext';
import './styles/colors.css';
import './styles/typography.css';
import './styles/layout.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <GlobalStateProvider>
    <App />
  </GlobalStateProvider>
);
