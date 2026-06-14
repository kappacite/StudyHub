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

describe('decks store — cartes typées', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('createCard envoie card_type=basic et payload=null par défaut', async () => {
    api.post.mockResolvedValue({ data: { id: 1, deck_id: 7, card_type: 'basic', payload: null } })
    const store = useDecksStore()

    await store.createCard(7, 'Recto', 'Verso')

    expect(api.post).toHaveBeenCalledWith('/decks/7/cards', {
      front: 'Recto',
      back: 'Verso',
      card_type: 'basic',
      payload: null,
    })
  })

  it('createCard transmet le type et le payload structuré (QCM)', async () => {
    const payload = {
      question: 'Capitale de la France ?',
      options: [
        { id: 'a', text: 'Lyon', correct: false },
        { id: 'b', text: 'Paris', correct: true },
      ],
    }
    api.post.mockResolvedValue({ data: { id: 2, deck_id: 7, card_type: 'qcm', payload } })
    const store = useDecksStore()

    await store.createCard(7, 'Capitale de la France ?', 'Paris', 'qcm', payload)

    expect(api.post).toHaveBeenCalledWith('/decks/7/cards', {
      front: 'Capitale de la France ?',
      back: 'Paris',
      card_type: 'qcm',
      payload,
    })
  })
})
