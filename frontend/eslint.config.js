const pluginJs = require("@eslint/js");
const importPlugin = require("eslint-plugin-import");
const pluginReact = require("eslint-plugin-react");
const globals = require("globals");
const tseslint = require("typescript-eslint");


module.exports = [
  {files: ["**/*.{js,mjs,cjs,ts,jsx,tsx}"]},
  // {languageOptions: {globals: globals.browser}},
  {
    languageOptions: {
      ecmaVersion: 2020, // ECMAScript version
      sourceType: "module", // Specify using ES modules
      globals: {
        ...globals.node, // Node.js global variables (like `module`, `__dirname`)
        ...globals.browser, // Browser globals (for React)
      },
    }
  },
  pluginJs.configs.recommended,
  ...tseslint.configs.recommended,
  pluginReact.configs.flat.recommended,
  {
    plugins: {
      import: importPlugin,  // Add this line to register the plugin
    },
    rules: {
      "import/order": [
        "error",
        {
          "groups": ["builtin", "external", "internal", ["parent", "sibling", "index"]],
          "newlines-between": "always",
          "alphabetize": {"order": "asc", "caseInsensitive": true},
        },
      ],
    },
  },
];
