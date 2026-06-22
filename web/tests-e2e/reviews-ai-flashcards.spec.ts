import { test, expect } from '@playwright/test'
import { authenticate } from './helpers'

// Vérifie que le bouton « Générer depuis Notes / Classeurs » utilise l'endpoint
// IA (/flashcards/generate) puis crée le deck et les cartes renvoyées.

const NOTE = { id: 'n1', title: 'Bio', content: 'La cellule est l unité du vivant.', binder_id: null, tags: [] }

test.beforeEach(async ({ page }) => {
  await authenticate(page)
  await page.route('**/api/v1/**', (route) => {
    const url = route.request().url()
    const method = route.request().method()

    if (/\/flashcards\/generate$/.test(url) && method === 'POST') {
      return route.fulfill({ json: { flashcards: [
        { front: 'Quelle est l unité du vivant ?', back: 'La cellule' },
        { front: 'Donne un organite clé', back: 'La mitochondrie' },
      ], count: 2 } })
    }
    if (/\/notes(\?|$)/.test(url)) return route.fulfill({ json: { data: [NOTE] } })
    if (/\/decks$/.test(url) && method === 'POST') {
      return route.fulfill({ json: { id: 99, name: 'IA Bio', description: '', card_count: 0, tags: [] } })
    }
    if (/\/decks\/99\/cards/.test(url) && method === 'GET') return route.fulfill({ json: { data: [] } })
    if (/\/decks\/99\/cards/.test(url) && method === 'POST') {
      const body = route.request().postDataJSON() as { front: string; back: string }
      return route.fulfill({ status: 201, json: { id: Math.floor(Math.random() * 1e6), ...body } })
    }
    return route.fulfill({ json: { data: [] } })
  })
})

test('Génération de flashcards par IA depuis une note', async ({ page }) => {
  await page.goto('/reviser')

  await page.getByRole('button', { name: /Générer depuis Notes/i }).click()

  // Source = note (par défaut) → choisir la note
  await page.locator('select').first().selectOption('n1')

  // Deck cible = nouveau (par défaut) → nommer le deck
  await page.getByPlaceholder(/Nom du nouveau deck/i).fill('IA Bio')

  await page.getByRole('button', { name: 'Générer', exact: true }).click()

  // Message de succès mentionnant la génération IA
  await expect(page.getByText(/générées par IA/i)).toBeVisible()
  await expect(page.getByText(/2 carte/i)).toBeVisible()
})

// Ouvre la modale et lance la génération (note + nouveau deck nommé).
async function startGeneration(page: import('@playwright/test').Page) {
  await page.goto('/reviser')
  await page.getByRole('button', { name: /Générer depuis Notes/i }).click()
  await page.locator('select').first().selectOption('n1')
  await page.getByPlaceholder(/Nom du nouveau deck/i).fill('IA Bio')
  await page.getByRole('button', { name: 'Générer', exact: true }).click()
}

test('Erreur 401 → message de session expirée (pas « IA indisponible »)', async ({ page }) => {
  await page.route('**/flashcards/generate', (r) => r.fulfill({ status: 401, json: { error: { message: 'token expired' } } }))
  await startGeneration(page)
  await expect(page.getByText(/session a expiré/i)).toBeVisible()
})

test('Erreur 429 → message de quota', async ({ page }) => {
  await page.route('**/flashcards/generate', (r) => r.fulfill({ status: 429, json: { error: { message: 'rate limited' } } }))
  await startGeneration(page)
  await expect(page.getByText(/Trop de générations/i)).toBeVisible()
})

test('Erreur 400 → message backend (source vide)', async ({ page }) => {
  await page.route('**/flashcards/generate', (r) => r.fulfill({ status: 400, json: { error: { message: 'Source vide côté serveur.' } } }))
  await startGeneration(page)
  await expect(page.getByText('Source vide côté serveur.')).toBeVisible()
})

test('Erreur 502 → repli local et message « IA indisponible »', async ({ page }) => {
  await page.route('**/flashcards/generate', (r) => r.fulfill({ status: 502, json: { error: { message: 'AI down' } } }))
  await startGeneration(page)
  await expect(page.getByText(/IA est indisponible/i)).toBeVisible()
})
