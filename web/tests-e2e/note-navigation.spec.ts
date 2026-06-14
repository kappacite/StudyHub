import { test, expect } from '@playwright/test'
import { authenticate } from './helpers'

// Régression directe du bug corrigé : dans le template de NoteEdit, `noteId.value`
// (au lieu de `noteId`) produisait des URLs `/notes/undefined/...`. Ce test ouvre
// une vraie note dans le navigateur, ouvre la modale « Réviser avec l'IA », clique
// les activités IA et vérifie l'URL.
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

  test('« Page blanche » navigue vers /notes/<id>/blurting', async ({ page }) => {
    await page.goto(`/notes/${NOTE_ID}`)

    await page.getByRole('button', { name: /Réviser avec l'IA/i }).click()

    const button = page.getByRole('button', { name: /Page blanche/i })
    await expect(button).toBeVisible()
    await button.click()

    await expect(page).toHaveURL(new RegExp(`/notes/${NOTE_ID}/blurting$`))
    expect(page.url()).not.toContain('undefined')
  })

  test('« QCM » navigue vers /notes/<id>/quiz', async ({ page }) => {
    await page.goto(`/notes/${NOTE_ID}`)

    await page.getByRole('button', { name: /Réviser avec l'IA/i }).click()

    const button = page.getByRole('button', { name: /QCM/i })
    await expect(button).toBeVisible()
    await button.click()

    await expect(page).toHaveURL(new RegExp(`/notes/${NOTE_ID}/quiz$`))
    expect(page.url()).not.toContain('undefined')
  })
})
