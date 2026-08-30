import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

// NoteEdit.vue parle à `api` à la fois directement et via notesStore/bindersStore/tagsStore
// (qui, eux, appellent le même client HTTP partagé) : on mock ce client une seule fois ici.
const api = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  patch: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
}))
vi.mock('../../../src/services/api', () => ({ default: api }))

import NoteEdit from '../../../src/views/Notes/NoteEdit.vue'

const NOTE = {
  id: '42',
  binder_id: null,
  title: 'Ma note de chimie',
  content: 'Contenu de la note.',
  created_at: '2026-08-01T10:00:00Z',
  updated_at: '2026-08-30T10:00:00Z',
  tags: [],
}

interface ApiOverrides {
  note?: () => Promise<unknown>
}

function makeGetImpl(over: ApiOverrides = {}) {
  return (url: string) => {
    if (/^\/notes\/\d+$/.test(url)) {
      return (over.note ?? (() => Promise.resolve({ data: NOTE })))()
    }
    if (url.startsWith('/notes?')) return Promise.resolve({ data: { data: [] } })
    if (url.startsWith('/binders?')) return Promise.resolve({ data: { data: [] } })
    if (url === '/tags') return Promise.resolve({ data: { data: [] } })
    if (url.startsWith('/diagrams?')) return Promise.resolve({ data: { data: [] } })
    return Promise.reject(new Error(`URL GET non mockée dans le test: ${url}`))
  }
}

const stub = { template: '<div />' }

function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/notes/:id', name: 'NoteEdit', component: NoteEdit },
      { path: '/notes/:id/evaluation', name: 'NoteEvaluation', component: stub },
      { path: '/notes/:id/blurting', name: 'NoteBlurting', component: stub },
      { path: '/notes/:id/feynman', name: 'NoteFeynman', component: stub },
    ],
  })
}

async function mountNoteEdit(to = '/notes/42') {
  const pinia = createPinia()
  setActivePinia(pinia)

  const router = createTestRouter()
  await router.push(to)
  await router.isReady()

  const wrapper = mount(NoteEdit, {
    global: { plugins: [pinia, router] },
  })

  await flushPromises()

  return { wrapper, router }
}

describe('NoteEdit — sidebar Assistant IA & bouton Notation (canevas Direction A)', () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.patch.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
    api.get.mockImplementation(makeGetImpl())
  })

  it('affiche le bouton Notation, désactivé, avec une info-bulle explicative', async () => {
    const { wrapper } = await mountNoteEdit()

    const notationButton = wrapper
      .findAll('button')
      .find((b) => b.text() === 'Notation') as ReturnType<typeof wrapper.find>

    expect(notationButton).toBeTruthy()
    expect(notationButton.attributes('disabled')).toBeDefined()
    expect(notationButton.attributes('title')).toBeTruthy()
  })

  it("affiche la sidebar Assistant IA (3 méthodes) et retire l'ancien bouton Réviser avec l'IA", async () => {
    const { wrapper } = await mountNoteEdit()

    expect(wrapper.text()).toContain('Assistant IA')
    expect(wrapper.text()).toContain('Évaluation mixte')
    expect(wrapper.text()).toContain('Méthode de la feuille blanche')
    expect(wrapper.text()).toContain('Méthode Feynman')
    expect(wrapper.text()).not.toContain("Réviser avec l'IA")
    expect(wrapper.text()).not.toContain('Générer un quiz')
  })

  it("navigue vers /notes/:id/evaluation au clic sur la carte Évaluation mixte de la sidebar", async () => {
    const { wrapper, router } = await mountNoteEdit()
    const push = vi.spyOn(router, 'push')

    const evaluationButton = wrapper
      .findAll('button')
      .find((b) => b.text() === 'Évaluation mixte')!
    await evaluationButton.trigger('click')

    expect(push).toHaveBeenCalledWith('/notes/42/evaluation')
  })

  it("navigue vers /notes/:id/feynman au clic sur la carte Méthode Feynman de la sidebar", async () => {
    const { wrapper, router } = await mountNoteEdit()
    const push = vi.spyOn(router, 'push')

    const feynmanButton = wrapper
      .findAll('button')
      .find((b) => b.text() === 'Méthode Feynman')!
    await feynmanButton.trigger('click')

    expect(push).toHaveBeenCalledWith('/notes/42/feynman')
  })
})
