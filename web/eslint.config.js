import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import tseslint from 'typescript-eslint'
import eslintConfigPrettier from 'eslint-config-prettier'

export default tseslint.config(
  {
    ignores: [
      'dist/**',
      'dist-mobile/**',
      'android/**',
      'node_modules/**',
      'coverage/**',
      'playwright-report/**',
      'test-results/**',
    ],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  {
    files: ['**/*.vue'],
    languageOptions: {
      parserOptions: {
        parser: tseslint.parser,
      },
    },
  },
  {
    rules: {
      // CLAUDE.md : "any" en TypeScript est interdit.
      '@typescript-eslint/no-explicit-any': 'error',
      // Beaucoup de vues StudyHub sont des routes à un seul mot (Notes.vue, Decks.vue…).
      'vue/multi-word-component-names': 'off',
    },
  },
  eslintConfigPrettier,
)
