// @ts-check
// based heavily on the eslint eslint.config.mjs

import { fixupConfigRules, fixupPluginRules } from '@eslint/compat';
import eslintCommentsPlugin from 'eslint-plugin-eslint-comments';
import eslintPluginPlugin from 'eslint-plugin-eslint-plugin';
import importPlugin from 'eslint-plugin-import';
// import jestPlugin from 'eslint-plugin-jest';
import jsdocPlugin from 'eslint-plugin-jsdoc';
import jsxA11yPlugin from 'eslint-plugin-jsx-a11y';
import perfectionistPlugin from 'eslint-plugin-perfectionist';
import eslintPluginPrettier from 'eslint-plugin-prettier';
import eslintPluginPrettierRecommended from 'eslint-plugin-prettier/recommended';
import reactPlugin from 'eslint-plugin-react';
import reactHooksPlugin from 'eslint-plugin-react-hooks';
import regexpPlugin from 'eslint-plugin-regexp';
import simpleImportSortPlugin from 'eslint-plugin-simple-import-sort';
import sonarjsPlugin from 'eslint-plugin-sonarjs';
import unicornPlugin from 'eslint-plugin-unicorn';
import globals from 'globals';
import tseslint from 'typescript-eslint';
import { FlatCompat } from '@eslint/eslintrc';
import eslint from '@eslint/js';

import url from 'node:url';

const __dirname = url.fileURLToPath(new URL('.', import.meta.url));
const compat = new FlatCompat({ baseDirectory: __dirname });

export default tseslint.config(
  // register all of the plugins up-front
  {
    // note - intentionally uses computed syntax to make it easy to sort the keys
    /* eslint-disable no-useless-computed-key */
    plugins: {
      ['@typescript-eslint']: tseslint.plugin,
      ['eslint-comments']: eslintCommentsPlugin,
      ['eslint-plugin']: eslintPluginPlugin,
      // https://github.com/import-js/eslint-plugin-import/issues/2948
      ['import']: fixupPluginRules(importPlugin),
      // ['jest']: jestPlugin,
      ['jsdoc']: jsdocPlugin,
      ['jsx-a11y']: jsxA11yPlugin,
      // https://github.com/facebook/react/issues/28313
      ['react-hooks']: fixupPluginRules(reactHooksPlugin),
      // https://github.com/jsx-eslint/eslint-plugin-react/issues/3699
      ['react']: fixupPluginRules(reactPlugin),
      ['regexp']: regexpPlugin,
      ['simple-import-sort']: simpleImportSortPlugin,
      ['sonarjs']: sonarjsPlugin,
      ['unicorn']: unicornPlugin,
      ['prettier']: eslintPluginPrettier,
    },
    /* eslint-enable no-useless-computed-key */
  },
  {
    // config with just ignores is the replacement for `.eslintignore`
    ignores: [
      '.nx/',
      '.yarn/',
      '**/jest.config.js',
      '**/node_modules/**',
      '**/dist/**',
      '**/fixtures/**',
      '**/coverage/**',
      '**/build/**',
      '.nx/*',
      '.yarn/*',
      '**/node_modules/**',
    ],
  },

  // extends ...
  eslint.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  jsdocPlugin.configs['flat/recommended-typescript-error'],
  eslintPluginPrettierRecommended,

  // base config
  {
    languageOptions: {
      globals: {
        ...globals.es2020,
        ...globals.node,
        ...globals.browser, // Browser globals (for React)
      },
      parserOptions: {
        projectService: true,
        tsconfigRootDir: __dirname,
        warnOnUnsupportedTypeScriptVersion: false,
      },
    },
    linterOptions: { reportUnusedDisableDirectives: 'error' },
    rules: {
      'prettier/prettier': [
        'warn',
        {},
        {
          usePrettierrc: true,
        },
      ],

      '@typescript-eslint/no-confusing-void-expression': 'off',

      //
      '@typescript-eslint/ban-ts-comment': [
        'error',
        {
          'ts-expect-error': 'allow-with-description',
          'ts-ignore': true,
          'ts-nocheck': true,
          'ts-check': false,
          minimumDescriptionLength: 5,
        },
      ],
      '@typescript-eslint/consistent-type-exports': ['error', { fixMixedExportsWithInlineTypeSpecifier: true }],
      '@typescript-eslint/consistent-type-imports': [
        'error',
        { prefer: 'type-imports', disallowTypeAnnotations: true },
      ],
      '@typescript-eslint/explicit-function-return-type': ['error', { allowIIFEs: true }],
      '@typescript-eslint/no-explicit-any': 'error',
      'no-constant-condition': 'off',
      '@typescript-eslint/no-unnecessary-condition': ['error', { allowConstantLoopConditions: true }],
      '@typescript-eslint/no-unnecessary-type-parameters': 'error',
      '@typescript-eslint/no-unused-expressions': 'error',
      '@typescript-eslint/no-var-requires': 'off',
      '@typescript-eslint/prefer-literal-enum-member': [
        'error',
        {
          allowBitwiseExpressions: true,
        },
      ],
      '@typescript-eslint/prefer-string-starts-ends-with': [
        'error',
        {
          allowSingleElementEquality: 'always',
        },
      ],
      '@typescript-eslint/unbound-method': 'off',
      '@typescript-eslint/restrict-template-expressions': [
        'error',
        {
          allowNumber: true,
          allowBoolean: true,
          allowAny: true,
          allowNullish: true,
          allowRegExp: true,
        },
      ],
      '@typescript-eslint/no-unused-vars': [
        'error',
        {
          caughtErrors: 'all',
          varsIgnorePattern: '^_',
          argsIgnorePattern: '^_',
        },
      ],
      '@typescript-eslint/prefer-nullish-coalescing': [
        'error',
        {
          ignoreConditionalTests: true,
          ignorePrimitives: true,
        },
      ],
      '@typescript-eslint/no-require-imports': [
        'error',
        {
          allow: ['/package\\.json$'],
        },
      ],

      //
      // eslint-base
      //
      curly: ['error', 'all'],
      eqeqeq: [
        'error',
        'always',
        {
          null: 'never',
        },
      ],
      'logical-assignment-operators': 'error',
      'no-else-return': 'error',
      'no-mixed-operators': 'error',
      'no-console': 'error',
      'no-process-exit': 'error',
      'no-fallthrough': ['error', { commentPattern: '.*intentional fallthrough.*' }],
      'no-implicit-coercion': ['error', { boolean: false }],
      'no-lonely-if': 'error',
      'no-unreachable-loop': 'error',
      'no-useless-call': 'error',
      'no-useless-computed-key': 'error',
      'no-useless-concat': 'error',
      'no-var': 'error',
      'no-void': ['error', { allowAsStatement: true }],
      'object-shorthand': 'error',
      'one-var': ['error', 'never'],
      'operator-assignment': 'error',
      'prefer-arrow-callback': 'error',
      'prefer-const': 'error',
      'prefer-object-has-own': 'error',
      'prefer-object-spread': 'error',
      'prefer-rest-params': 'error',
      'prefer-template': 'error',
      radix: 'error',

      //
      // eslint-plugin-eslint-comment
      //

      // require a eslint-enable comment for every eslint-disable comment
      'eslint-comments/disable-enable-pair': [
        'error',
        {
          allowWholeFile: true,
        },
      ],
      // disallow a eslint-enable comment for multiple eslint-disable comments
      'eslint-comments/no-aggregating-enable': 'error',
      // disallow duplicate eslint-disable comments
      'eslint-comments/no-duplicate-disable': 'error',
      // disallow eslint-disable comments without rule names
      'eslint-comments/no-unlimited-disable': 'error',
      // disallow unused eslint-disable comments
      'eslint-comments/no-unused-disable': 'error',
      // disallow unused eslint-enable comments
      'eslint-comments/no-unused-enable': 'error',
      // disallow ESLint directive-comments
      'eslint-comments/no-use': [
        'error',
        {
          allow: ['eslint-disable', 'eslint-disable-line', 'eslint-disable-next-line', 'eslint-enable', 'global'],
        },
      ],

      //
      // eslint-plugin-import
      //
      // enforces consistent type specifier style for named imports
      'import/consistent-type-specifier-style': 'error',
      // disallow non-import statements appearing before import statements
      'import/first': 'error',
      // Require a newline after the last import/require in a group
      'import/newline-after-import': 'error',
      // Forbid import of modules using absolute paths
      'import/no-absolute-path': 'error',
      // disallow AMD require/define
      'import/no-amd': 'error',
      // forbid default exports - we want to standardize on named exports so that imported names are consistent
      'import/no-default-export': 'error',
      // disallow imports from duplicate paths
      'import/no-duplicates': 'error',
      // Forbid the use of extraneous packages
      'import/no-extraneous-dependencies': [
        'error',
        {
          devDependencies: true,
          peerDependencies: true,
          optionalDependencies: false,
        },
      ],
      // Forbid mutable exports
      'import/no-mutable-exports': 'error',
      // Prevent importing the default as if it were named
      'import/no-named-default': 'error',
      // Prohibit named exports
      'import/no-named-export': 'off', // we want everything to be a named export
      // Forbid a module from importing itself
      'import/no-self-import': 'error',
      // Require modules with a single export to use a default export
      'import/prefer-default-export': 'off', // we want everything to be named

      // enforce a sort order across the codebase
      'simple-import-sort/imports': 'error',

      //
      // eslint-plugin-jsdoc
      //

      // We often use @remarks or other ad-hoc tag names
      'jsdoc/check-tag-names': 'off',
      // https://github.com/gajus/eslint-plugin-jsdoc/issues/1169
      'jsdoc/check-param-names': 'off',
      'jsdoc/informative-docs': 'error',
      // https://github.com/gajus/eslint-plugin-jsdoc/issues/1175
      'jsdoc/require-jsdoc': 'off',
      'jsdoc/require-param': 'off',
      'jsdoc/require-returns': 'off',
      'jsdoc/require-yields': 'off',
      'jsdoc/tag-lines': 'off',

      'regexp/no-dupe-disjunctions': 'error',
      'regexp/no-useless-character-class': 'error',
      'regexp/no-useless-flag': 'error',
      'regexp/no-useless-lazy': 'error',
      'regexp/no-useless-non-capturing-group': 'error',
      'regexp/prefer-quantifier': 'error',
      'regexp/prefer-question-quantifier': 'error',
      'regexp/prefer-w': 'error',

      'sonarjs/no-duplicated-branches': 'error',

      //
      // eslint-plugin-unicorn
      //
      'unicorn/no-length-as-slice-end': 'error',
      'unicorn/no-lonely-if': 'error',
      'unicorn/no-typeof-undefined': 'error',
      'unicorn/no-single-promise-in-promise-methods': 'error',
      'unicorn/no-useless-spread': 'error',
      'unicorn/prefer-array-some': 'error',
      'unicorn/prefer-export-from': 'error',
      'unicorn/prefer-node-protocol': 'error',
      'unicorn/prefer-regexp-test': 'error',
      'unicorn/prefer-spread': 'error',
      'unicorn/prefer-string-replace-all': 'error',
      'unicorn/prefer-structured-clone': 'error',
    },
  },
  {
    files: ['**/*.js'],
    extends: [tseslint.configs.disableTypeChecked],
  },

  //
  // test file linting
  //

  // define the jest globals for all test files
  // {
  //   files: ['*/tests/**/*.{ts,tsx,cts,mts}'],
  //   languageOptions: {
  //     globals: {
  //       ...jestPlugin.environments.globals.globals,
  //     },
  //   },
  // },
  // test file specific configuration
  {
    files: ['**/tests/**/*.test.{ts,tsx,cts,mts}'],
    rules: {
      '@typescript-eslint/no-empty-function': ['error', { allow: ['arrowFunctions'] }],
      '@typescript-eslint/no-non-null-assertion': 'off',
      '@typescript-eslint/no-unsafe-assignment': 'off',
      '@typescript-eslint/no-unsafe-call': 'off',
      '@typescript-eslint/no-unsafe-member-access': 'off',
      '@typescript-eslint/no-unsafe-return': 'off',
      'jest/no-disabled-tests': 'error',
      'jest/no-focused-tests': 'error',
      'jest/no-alias-methods': 'error',
      'jest/no-identical-title': 'error',
      'jest/no-jasmine-globals': 'error',
      'jest/no-test-prefixes': 'error',
      'jest/no-done-callback': 'error',
      'jest/no-test-return-statement': 'error',
      'jest/prefer-to-be': 'error',
      'jest/prefer-to-contain': 'error',
      'jest/prefer-to-have-length': 'error',
      'jest/prefer-spy-on': 'error',
      'jest/valid-expect': 'error',
      'jest/no-deprecated-functions': 'error',
    },
  },

  //
  // tools and tests
  //
  {
    files: ['**/tools/**/*.{ts,tsx,cts,mts}', '**/tests/**/*.{ts,tsx,cts,mts}'],
    rules: {
      // allow console logs in tools and tests
      'no-console': 'off',
    },
  },
  {
    files: ['eslint.config.{js,cjs,mjs}'],
    rules: {
      // requirement
      'import/no-default-export': 'off',
    },
  },

  //
  // website linting
  //
  {
    files: ['src/**/*.{ts,tsx,mts,cts,js,jsx}'],
    extends: [
      ...compat.config(jsxA11yPlugin.configs.recommended),
      ...fixupConfigRules(compat.config(reactPlugin.configs.recommended)),
      ...fixupConfigRules(compat.config(reactHooksPlugin.configs.recommended)),
    ],
    rules: {
      'import/no-default-export': 'off',
      'react/jsx-no-target-blank': 'off',
      'react/no-unescaped-entities': 'off',
      'react-hooks/exhaustive-deps': 'warn',
      'react/prop-types': 'off',
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
  },
  {
    files: ['src/**/*.{ts,tsx,cts,mts}'],
    rules: {
      'import/no-default-export': 'off',
    },
  },
  {
    extends: [perfectionistPlugin.configs['recommended-alphabetical']],
    ignores: ['src/configs/*'],
    files: ['{src,tests,typings}/**/*.ts'],
    rules: {
      '@typescript-eslint/sort-type-constituents': 'off',
      'perfectionist/sort-classes': [
        'error',
        {
          order: 'asc',
          partitionByComment: true,
          type: 'natural',
        },
      ],
      // 'perfectionist/sort-enums': 'off',
      'perfectionist/sort-objects': [
        'error',
        {
          order: 'asc',
          partitionByComment: true,
          type: 'natural',
        },
      ],
      'perfectionist/sort-union-types': [
        'error',
        {
          order: 'asc',
          groups: ['unknown', 'keyword', 'nullish'],
          type: 'natural',
        },
      ],
      'simple-import-sort/imports': 'off',
    },
  }
);
