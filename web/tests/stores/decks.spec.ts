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

describe('decks store — mode inversé & tuning (A1)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('createDeck transmet reversed et tuning_default', async () => {
    api.post.mockResolvedValue({ data: { id: 3, name: 'D', reversed: true, tuning_default: 1.5 } })
    const store = useDecksStore()

    await store.createDeck('D', '', null, true, 1.5)

    expect(api.post).toHaveBeenCalledWith('/decks', {
      name: 'D',
      description: '',
      binder_id: null,
      reversed: true,
      tuning_default: 1.5,
    })
  })

  it('updateCard transmet le tuning quand fourni', async () => {
    const store = useDecksStore()
    store.cards = [{ id: 4, deck_id: 7, front: 'a', back: 'b', tuning: 1, reverse_of_id: null, interval: 0, ease_factor: 2.5, repetitions: 0, next_review: '' }]
    api.put.mockResolvedValue({ data: { ...store.cards[0], tuning: 0.5 } })

    await store.updateCard(4, 'a', 'b', 0.5)

    expect(api.put).toHaveBeenCalledWith('/decks/7/cards/4', { front: 'a', back: 'b', tuning: 0.5 })
  })

  it('fetchCardHistory lit la série date/grade', async () => {
    api.get.mockResolvedValue({ data: { data: [{ date: '2026-06-15', grade: 4 }] } })
    const store = useDecksStore()

    const hist = await store.fetchCardHistory(7, 4)

    expect(api.get).toHaveBeenCalledWith('/decks/7/cards/4/history')
    expect(hist).toEqual([{ date: '2026-06-15', grade: 4 }])
  })
})
