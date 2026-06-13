import { test, expect } from '@playwright/test'
import { authenticate } from './helpers'

// Smoke-test de rendu : monte les vues clés dans un vrai navigateur (API mockée)
// et vérifie les éléments d'UI exigés par FEATURES.md (onglets, toggles, boutons).

const GROUP = {
  id: 1, name: 'Groupe Bio', description: 'Révisions de biologie',
  invite_code: 'BIO12345', created_by: 1, members_count: 2, binders_count: 1,
  members: [
    { user_id: 1, username: 'alice', email: 'a@x.io', role: 'owner', joined_at: '2026-01-01T00:00:00Z' },
  ],
  binders: [{ group_id: 1, binder_id: 'uuid-1', binder_name: 'Classeur Bio', permission: 'read', pinned: false, added_at: '2026-01-01T00:00:00Z' }],
}

test.beforeEach(async ({ page }) => {
  await authenticate(page)
  await page.route('**/api/v1/**', (route) => {
    const url = route.request().url()
    if (/\/groups\/1$/.test(url)) return route.fulfill({ json: GROUP })
    if (/\/groups\/1\/activity/.test(url)) return route.fulfill({ json: [] })
    if (/\/groups\/1\/members\/progress/.test(url)) return route.fulfill({ json: [] })
    if (/\/groups(\?|$)/.test(url)) return route.fulfill({ json: [GROUP] })
    if (/\/planning\/calendar/.test(url)) return route.fulfill({ json: { days: [
      { date: '2026-06-15', total_due: 5, breakdown: [{ deck_id: 1, deck_name: 'Cellule', count: 5 }] },
      { date: '2026-06-16', total_due: 18, breakdown: [{ deck_id: 1, deck_name: 'Cellule', count: 18 }] },
      { date: '2026-06-17', total_due: 30, breakdown: [{ deck_id: 1, deck_name: 'Cellule', count: 30 }] },
    ] } })
    return route.fulfill({ json: { data: [] } })
  })
})

test('GroupsList rend les actions créer/rejoindre (9.2.6)', async ({ page }) => {
  await page.goto('/groups')
  await expect(page.getByText('Mes Groupes')).toBeVisible()
  await expect(page.getByRole('button', { name: /Créer un groupe/i })).toBeVisible()
  await expect(page.getByText(/Rejoindre avec un code/i)).toBeVisible()
})

test('GroupDetail rend les 4 onglets (9.2.7)', async ({ page }) => {
  await page.goto('/groups/1')
  for (const tab of ['Classeurs partagés', 'Activité', 'Membres', 'Progression']) {
    await expect(page.getByText(tab, { exact: false }).first()).toBeVisible()
  }
})

test('PlanningPage rend le toggle semaine/mois et les révisions anticipées (3.2.7)', async ({ page }) => {
  await page.goto('/planning')
  await expect(page.getByText(/Planning des révisions/i).first()).toBeVisible()
  await expect(page.getByText(/Semaine/i).first()).toBeVisible()
  await expect(page.getByText(/Mois/i).first()).toBeVisible()
  await expect(page.getByText(/anticip/i).first()).toBeVisible()
})
