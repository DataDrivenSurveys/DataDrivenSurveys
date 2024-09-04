// import { render, screen } from '@testing-library/react';
// import App from './App.js';
//
// test('renders learn react link', () => {
//   render(<App />);
//   const linkElement = screen.getByText(/learn react/i);
//   expect(linkElement).toBeInTheDocument();
// });
import { render, screen } from '@testing-library/react';

import App from './App'; // Assuming App.tsx or App.jsx (no need for '.js' extension in TypeScript)

// Test to check if the "learn react" link is rendered
test('renders learn react link', () => {
  render(<App />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});
