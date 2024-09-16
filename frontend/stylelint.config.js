module.exports = {
  extends: [
    'stylelint-config-recommended',       // Base config with common rules
    'stylelint-config-standard',          // Standard styling guidelines
    'stylelint-config-css-modules',       // Support for CSS Modules
    'stylelint-config-prettier',          // Prettier integration to avoid conflicts
    'stylelint-config-styled-components', // Support for styled-components (CSS-in-JS)
  ],
  plugins: [
    'stylelint-order',                    // Plugin for property order
    'stylelint-prettier',                 // Prettier plugin for consistent formatting
  ],
  rules: {
    // Prettier formatting rules
    'prettier/prettier': true,

    // Enforce standard ordering of properties
    'order/properties-alphabetical-order': true,

    // Disallow vendor prefixes (let autoprefixer handle it)
    'property-no-vendor-prefix': true,

    // Disallow unknown CSS properties (helps catch typos)
    'property-no-unknown': [true, {
      ignoreProperties: ['/^composes$/'], // Allow 'composes' from CSS Modules
    }],

    // Enforce the use of hyphens in class names
    'selector-class-pattern': '^[a-z][a-z0-9\\-]*[a-z0-9]$',

    // Enforce lowercase for hex colors
    'color-hex-case': 'lower',

    // Enforce short notation for hex colors
    'color-hex-length': 'short',

    // Disallow units for zero lengths
    'length-zero-no-unit': true,

    // Max specificity (e.g., restrict usage of overly complex selectors)
    'selector-max-specificity': '0,3,0',

    // Disallow id selectors in CSS (best practice for React components)
    'selector-no-id': true,

    // No empty sources (useful for cleaning up SCSS imports)
    'no-empty-source': true,

    // Disallow vendor prefixes for values (let autoprefixer handle it)
    'value-no-vendor-prefix': true,

    // Additional rules you may want to add for React-specific practices
  },
  ignoreFiles: [
    'node_modules/**/*.css',             // Ignore external libraries
    '**/*.js', '**/*.jsx', '**/*.ts', '**/*.tsx', // Ignore JavaScript/TypeScript files
  ],
};
