import { test, expect } from '@playwright/test'

// Parcours d'authentification — la garde de route protège les pages privées.
test.describe('Garde d\'authentification', () => {
  test('un visiteur non authentifié est redirigé vers /login', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page).toHaveURL(/\/login$/)
  })

  test('la page de connexion affiche le formulaire', async ({ page }) => {
    await page.goto('/login')
    await expect(page.locator('input[type="password"]')).toBeVisible()
  })
})
