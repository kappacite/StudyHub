import { test, expect } from '@playwright/test'
import { authenticate } from './helpers'

// Vérifie les outils d'édition du créateur de diagrammes :
// rendu des nœuds, édition inline du texte (double-clic) et sélection de lien.

const DIAGRAM = {
  id: 1,
  title: 'Cycle cellulaire',
  binder_id: null,
  created_at: '2026-01-01T00:00:00Z',
  tags: [],
  code: JSON.stringify({
    type: 'visual',
    nodes: [
      { id: 1, label: 'Interphase', type: 'rect', x: 180, y: 150, color: 'bg-indigo-600' },
      { id: 2, label: 'Mitose', type: 'circle', x: 420, y: 150, color: 'bg-emerald-500' },
    ],
    connections: [{ from: 1, to: 2 }],
    backgroundImage: null,
    masks: [],
  }),
}

test.beforeEach(async ({ page }) => {
  await authenticate(page)
  await page.route('**/api/v1/**', (route) => {
    const url = route.request().url()
    if (/\/diagrams(\?|$)/.test(url)) return route.fulfill({ json: { data: [DIAGRAM] } })
    return route.fulfill({ json: { data: [] } })
  })
})

test('Diagrams : sélection d\'un diagramme et rendu des nœuds', async ({ page }) => {
  await page.goto('/diagrams')
  await page.getByText('Cycle cellulaire').click()
  await expect(page.getByText('Interphase')).toBeVisible()
  await expect(page.getByText('Mitose')).toBeVisible()
  await expect(page.getByText(/Double-clic\s*:\s*renommer/i)).toBeVisible()
})

test('Diagrams : édition inline du texte d\'un nœud au double-clic', async ({ page }) => {
  await page.goto('/diagrams')
  await page.getByText('Cycle cellulaire').click()
  await page.getByText('Interphase').dblclick()
  const input = page.locator('.cursor-grab input')
  await expect(input).toBeVisible()
  await expect(input).toHaveValue('Interphase')
  await input.fill('Phase G1')
  await input.press('Enter')
  await expect(page.getByText('Phase G1')).toBeVisible()
})

test('Diagrams : contrôles de zoom (zoom + réinitialisation de la vue)', async ({ page }) => {
  await page.goto('/diagrams')
  await page.getByText('Cycle cellulaire').click()

  const reset = page.getByRole('button', { name: 'Réinitialiser la vue' })
  await expect(reset).toHaveText('100%')

  await page.getByRole('button', { name: 'Zoomer', exact: true }).click()
  await expect(reset).not.toHaveText('100%')

  await reset.click()
  await expect(reset).toHaveText('100%')
})

test('Diagrams : ajout d\'une forme « texte libre »', async ({ page }) => {
  await page.goto('/diagrams')
  await page.getByText('Cycle cellulaire').click()
  await page.getByRole('button', { name: 'Texte libre' }).click()
  // .last() = le nœud rendu sur le canevas (le 1er match est le label de la barre latérale)
  await expect(page.getByText('Texte', { exact: true }).last()).toBeVisible()
})

test('Diagrams : sélection d\'un lien et ajout d\'un libellé', async ({ page }) => {
  await page.goto('/diagrams')
  await page.getByText('Cycle cellulaire').click()

  // Clic sur la zone cliquable élargie du lien (stroke transparent → force)
  await page.locator('line.cursor-pointer').first().click({ force: true })
  await expect(page.getByText('Lien sélectionné')).toBeVisible()

  await page.getByPlaceholder('ex: entraîne').fill('active')
  await expect(page.locator('svg text', { hasText: 'active' })).toBeVisible()
})

test('Diagrams : poignée de redimensionnement sur un nœud sélectionné', async ({ page }) => {
  await page.goto('/diagrams')
  await page.getByText('Cycle cellulaire').click()

  // Aucune poignée tant que rien n'est sélectionné
  await expect(page.locator('.cursor-nwse-resize')).toHaveCount(0)

  await page.getByText('Interphase').click()
  await expect(page.locator('.cursor-nwse-resize')).toBeVisible()
})

test('Diagrams : bascule d\'alignement sur la grille', async ({ page }) => {
  await page.goto('/diagrams')
  await page.getByText('Cycle cellulaire').click()

  const snap = page.getByRole('button', { name: /Aligner sur la grille/ })
  await expect(snap).toHaveText(/Aligner sur la grille$/)
  await snap.click()
  await expect(snap).toHaveText(/actif/)
})

test('Diagrams : annuler / rétablir un ajout de forme', async ({ page }) => {
  await page.goto('/diagrams')
  await page.getByText('Cycle cellulaire').click()

  const undo = page.getByRole('button', { name: /Annuler/ })
  const redo = page.getByRole('button', { name: /Rétablir/ })
  await expect(undo).toBeDisabled()

  await page.getByRole('button', { name: 'Texte libre' }).click()
  await expect(page.getByText('Texte', { exact: true }).last()).toBeVisible()
  await expect(undo).toBeEnabled() // après debounce de l'historique

  await undo.click()
  await expect(page.getByText('Texte', { exact: true })).toHaveCount(0)

  await expect(redo).toBeEnabled()
  await redo.click()
  await expect(page.getByText('Texte', { exact: true }).last()).toBeVisible()
})
