// Suite TDD — relocation de la génération de flashcards IA depuis Reviews.vue
// vers Decks.vue (chantier reviser-hub, tâche 4). Voir
// .superpowers/sdd/2026-08-29-reviser-hub-redesign/task-4-brief.md
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}))
vi.mock('../../../src/services/api', () => ({ default: api }))

import Decks from '../../../src/views/Decks/Decks.vue'
import type { Deck } from '../../../src/stores/decks'
import type { Note } from '../../../src/stores/notes'

const DECK: Deck = {
  id: 1,
  binder_id: null,
  name: 'Chimie organique',
  description: '',
  reversed: false,
  tuning_default: 1,
  card_count: 2,
  created_at: '2026-01-01T00:00:00Z',
  tags: [],
}

const NOTE: Note = {
  id: 'n1',
  binder_id: null,
  title: 'Ma note',
  content: '- **Photosynthèse** : conversion de la lumière en énergie chimique',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
  tags: [],
}

interface ApiOverrides {
  generate?: () => Promise<unknown>
}

function makeGetImpl() {
  return (url: string) => {
    if (url === '/tags') return Promise.resolve({ data: { data: [] } })
    if (url.startsWith('/decks?')) return Promise.resolve({ data: { data: [DECK] } })
    if (url.startsWith('/notes?')) return Promise.resolve({ data: { data: [NOTE] } })
    if (url.startsWith('/binders?')) return Promise.resolve({ data: { data: [] } })
    if (/^\/decks\/\d+\/cards/.test(url)) return Promise.resolve({ data: { data: [] } })
    return Promise.reject(new Error(`URL GET non mockée dans le test: ${url}`))
  }
}

function makePostImpl(over: ApiOverrides = {}) {
  return (url: string, body?: unknown) => {
    if (url === '/flashcards/generate') {
      return (
        over.generate ??
        (() =>
          Promise.resolve({
            data: { flashcards: [{ front: 'Photosynthèse', back: 'Conversion lumière → énergie' }] },
          }))
      )()
    }
    if (url === '/decks') {
      const { name, description } = body as { name: string; description: string }
      return Promise.resolve({
        data: {
          id: 2,
          binder_id: null,
          name,
          description,
          reversed: false,
          tuning_default: 1,
          card_count: 0,
          created_at: '2026-01-01T00:00:00Z',
          tags: [],
        },
      })
    }
    if (/^\/decks\/\d+\/cards$/.test(url)) {
      const { front, back } = body as { front: string; back: string }
      return Promise.resolve({
        data: {
          id: 100,
          deck_id: 2,
          front,
          back,
          tuning: 1,
          reverse_of_id: null,
          interval: 0,
          ease_factor: 2.5,
          repetitions: 0,
          next_review: '2026-01-01T00:00:00Z',
        },
      })
    }
    return Promise.reject(new Error(`URL POST non mockée dans le test: ${url}`))
  }
}

const stub = { template: '<div />' }

function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/decks', name: 'Decks', component: stub },
      { path: '/decks/:id/study', name: 'DeckStudy', component: stub },
    ],
  })
}

async function mountDecks() {
  const pinia = createPinia()
  setActivePinia(pinia)

  const router = createTestRouter()
  await router.push('/decks')
  await router.isReady()

  const wrapper = mount(Decks, {
    global: { plugins: [pinia, router] },
  })

  await flushPromises()

  return { wrapper, router }
}

describe('Decks — génération de flashcards par IA', () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.get.mockImplementation(makeGetImpl())
    api.post.mockImplementation(makePostImpl())
  })

  it('affiche le bouton « Générer depuis Notes / Classeurs »', async () => {
    const { wrapper } = await mountDecks()

    const button = wrapper
      .findAll('button')
      .find((b) => b.text().includes('Générer depuis Notes / Classeurs'))

    expect(button).toBeTruthy()
  })

  it('ouvre la modale de génération et soumet vers /flashcards/generate', async () => {
    const { wrapper } = await mountDecks()

    const openButton = wrapper
      .findAll('button')
      .find((b) => b.text().includes('Générer depuis Notes / Classeurs'))!
    await openButton.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Générer des Flashcards')

    // Sélectionne la note source
    const noteSelect = wrapper.get('select')
    await noteSelect.setValue('n1')

    // Choisit "Nouveau Deck" (déjà la valeur par défaut) et renseigne son nom
    const newDeckInput = wrapper.get('input[placeholder^="Nom du nouveau deck"]')
    await newDeckInput.setValue('Biologie')

    const submitButton = wrapper
      .findAll('button')
      .find((b) => b.text() === 'Générer')!
    await submitButton.trigger('click')
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith(
      '/flashcards/generate',
      { source_type: 'note', note_id: 'n1', coverage: 75 },
      { timeout: 120000 },
    )
    expect(api.post).toHaveBeenCalledWith('/decks', expect.objectContaining({ name: 'Biologie' }))
    expect(wrapper.text()).toContain('Succès !')
  })
})
