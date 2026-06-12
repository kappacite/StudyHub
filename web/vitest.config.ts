import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

// Configuration des tests frontend (Vitest).
// Les tests vivent dans `tests/` et sont exclus du build (tsconfig.app -> src/**),
// donc `vue-tsc -b` ne les typecheck pas : le job de build reste indépendant.
export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'happy-dom',
    include: ['tests/**/*.spec.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      include: ['src/**/*.{ts,vue}'],
      // Pas de seuil pour l'instant : la couverture frontend démarre.
      // Un plancher sera introduit en phase 4 (cf. docs/testing.md).
    },
  },
})
