import pluginJs from "@eslint/js";
import importPlugin from "eslint-plugin-import";
import pluginReact from "eslint-plugin-react";
import globals from "globals";
import tseslint from "typescript-eslint";


export default [
  {files: ["**/*.{js,mjs,cjs,ts,jsx,tsx}"]},
  {languageOptions: {globals: globals.browser}},
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
