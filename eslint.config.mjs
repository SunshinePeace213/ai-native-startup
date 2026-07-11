import js from '@eslint/js';
import { defineConfig } from 'eslint/config';
import prettier from 'eslint-config-prettier';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import tseslint from 'typescript-eslint';

export default defineConfig([
  { ignores: ['node_modules/**', '.venv/**', 'dist/**', '.claude/worktrees/**'] },
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    extends: [js.configs.recommended, react.configs.flat.recommended, reactHooks.configs.flat.recommended],
    // Pinned: `detect` warns on every run while react is not yet installed.
    // Switch to `detect` once react lands as a dependency.
    settings: { react: { version: '19.0' } },
  },
  {
    files: ['**/*.{ts,tsx}'],
    extends: [tseslint.configs.recommended],
  },
  prettier,
]);
