import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// L'instance Axios centralisée est mockée : aucun appel réseau réel.
const api = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
}))
vi.mock('../../src/services/api', () => ({ default: api }))

import { useDecksStore } from '../../src/stores/decks'

describe('decks store — flashcards recto/verso (D3c)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('createCard envoie uniquement front/back (pas de type ni payload)', async () => {
    api.post.mockResolvedValue({ data: { id: 1, deck_id: 7, front: 'Recto', back: 'Verso' } })
    const store = useDecksStore()

    await store.createCard(7, 'Recto', 'Verso')

    expect(api.post).toHaveBeenCalledWith('/decks/7/cards', {
      front: 'Recto',
      back: 'Verso',
    })
  })
})
