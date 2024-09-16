import './i18n/i18n'; // Assuming the i18n file is JavaScript and doesn't need renaming
import TimeAgo from 'javascript-time-ago';
import en from 'javascript-time-ago/locale/en';
import React from 'react';
import { createRoot } from 'react-dom/client';

import App from './App';
import reportWebVitals from './reportWebVitals';

// Add default locale for `javascript-time-ago`
TimeAgo.addDefaultLocale(en);

// Get the root DOM node
const rootElement = document.getElementById('root');

// Ensure `rootElement` exists before trying to create the root
if (rootElement) {
  // const root = ReactDOM.createRoot(rootElement);
  const root = createRoot(rootElement);

  root.render(<App />);
}

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
