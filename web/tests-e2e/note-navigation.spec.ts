import { test, expect } from '@playwright/test'
import { authenticate } from './helpers'

// Régression directe du bug corrigé : dans le template de NoteEdit, `noteId.value`
// (au lieu de `noteId`) produisait des URLs `/notes/undefined/...`. Ce test ouvre
// une vraie note dans le navigateur, clique une méthode de la sidebar Assistant IA
// (toujours visible en mode lecture depuis la refonte editeur-notes-notation-ia,
// plus de modale intermédiaire) et vérifie l'URL.
const NOTE_ID = 'e2e-note-1234'

const note = {
  id: NOTE_ID,
  binder_id: null,
  title: 'Note E2E',
  content: 'Contenu de test',
  is_public: false,
  share_token: null,
  flashcards: [],
  tags: [],
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

test.describe('NoteEdit — navigation vers les outils IA', () => {
  test.beforeEach(async ({ page }) => {
    await authenticate(page)

    // Fallback permissif : toutes les listes renvoient un tableau vide.
    await page.route('**/api/v1/**', (route) => route.fulfill({ json: { data: [] } }))
    // La note ouverte est renvoyée comme objet (et non comme liste paginée).
    await page.route(new RegExp(`/api/v1/notes/${NOTE_ID}$`), (route) =>
      route.fulfill({ json: note }),
    )
  })

  test('« Méthode de la feuille blanche » navigue vers /notes/<id>/blurting', async ({ page }) => {
    await page.goto(`/notes/${NOTE_ID}`)

    const button = page.getByRole('button', { name: /Méthode de la feuille blanche/i })
    await expect(button).toBeVisible()
    await button.click()

    await expect(page).toHaveURL(new RegExp(`/notes/${NOTE_ID}/blurting$`))
    expect(page.url()).not.toContain('undefined')
  })

  test('« Méthode Feynman » navigue vers /notes/<id>/feynman', async ({ page }) => {
    await page.goto(`/notes/${NOTE_ID}`)

    const button = page.getByRole('button', { name: /Méthode Feynman/i })
    await expect(button).toBeVisible()
    await button.click()

    await expect(page).toHaveURL(new RegExp(`/notes/${NOTE_ID}/feynman$`))
    expect(page.url()).not.toContain('undefined')
  })
})
