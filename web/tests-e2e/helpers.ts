import type { Page } from '@playwright/test'

export const FAKE_USER = {
  id: 1,
  email: 'e2e@studyhub.test',
  username: 'e2e',
  created_at: '2026-01-01T00:00:00Z',
}

/**
 * Simule une session authentifiée en injectant les clés localStorage lues par
 * authStore.init() (cf. main.ts), avant le chargement des scripts de la page.
 */
export async function authenticate(page: Page): Promise<void> {
  await page.addInitScript((user) => {
    localStorage.setItem('sh_token', 'e2e-fake-access-token')
    localStorage.setItem('sh_refresh_token', 'e2e-fake-refresh-token')
    localStorage.setItem('sh_user', JSON.stringify(user))
  }, FAKE_USER)
}
