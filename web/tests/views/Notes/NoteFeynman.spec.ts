import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

// NoteFeynman.vue ne parle plus directement à `api` (revue de branche
// reviser-hub, finding #5) : le titre de la note passe par notesStore
// (qui, lui, appelle `api` — d'où ce mock au niveau du client HTTP partagé),
// et les appels IA passent par feynmanService, mocké directement ici.
const api = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}))
vi.mock('../../../src/services/api', () => ({ default: api }))

const feynmanService = vi.hoisted(() => ({
  analyze: vi.fn(),
  pollTask: vi.fn(),
}))
vi.mock('../../../src/services/feynmanService', () => ({ default: feynmanService }))

import NoteFeynman from '../../../src/views/Notes/NoteFeynman.vue'

const NOTE = { id: '42', binder_id: null, title: 'Ma note', content: 'Contenu de la note', created_at: '', updated_at: '', tags: [] }

interface ApiOverrides {
  note?: () => Promise<unknown>
}

function makeGetImpl(over: ApiOverrides = {}) {
  return (url: string) => {
    if (/^\/notes\/\d+$/.test(url)) {
      return (over.note ?? (() => Promise.resolve({ data: NOTE })))()
    }
    return Promise.reject(new Error(`URL GET non mockée dans le test: ${url}`))
  }
}

const stub = { template: '<div />' }

function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/notes/:id', name: 'NoteEdit', component: stub },
      { path: '/notes/:id/feynman', name: 'NoteFeynman', component: stub },
    ],
  })
}

async function mountNoteFeynman(to = '/notes/42/feynman') {
  const pinia = createPinia()
  setActivePinia(pinia)

  const router = createTestRouter()
  await router.push(to)
  await router.isReady()

  const wrapper = mount(NoteFeynman, {
    global: { plugins: [pinia, router] },
  })

  await flushPromises()

  return { wrapper, router }
}

describe('NoteFeynman', () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.get.mockImplementation(makeGetImpl())
    feynmanService.analyze.mockReset()
    feynmanService.pollTask.mockReset()
  })

  it("charge le titre de la note (via notesStore) au montage", async () => {
    const { wrapper } = await mountNoteFeynman()
    expect(api.get).toHaveBeenCalledWith('/notes/42')
    expect(wrapper.text()).toContain('Ma note')
  })

  it("soumet l'explication et affiche le score renvoye par l'IA (via feynmanService)", async () => {
    feynmanService.analyze.mockResolvedValue({
      status: 'SUCCESS',
      result: {
        clarity_score: 82,
        jargon: [],
        gaps: [],
        feedback: 'Bien',
        suggestion: '',
      },
    })

    const { wrapper } = await mountNoteFeynman()

    const textarea = wrapper.get('textarea')
    await textarea.setValue("Voici mon explication simplifiée du concept.")

    const submitButton = wrapper
      .findAll('button')
      .find((b) => b.text().includes("Analyser mon explication avec l'IA"))!
    await submitButton.trigger('click')
    await flushPromises()

    expect(feynmanService.analyze).toHaveBeenCalledWith(
      '42',
      'Voici mon explication simplifiée du concept.',
      expect.any(Number),
    )
    // notes-ia-planning-corrections, Task 7 : score /10 a une decimale (formattedScore
    // computed, harmonise avec Notation/Blurting), plus de pourcentage brut.
    expect(wrapper.text()).toContain('8,2')
    expect(wrapper.text()).not.toContain('82%')
    expect(wrapper.text()).toContain('Bien')
  })

  it("suit le polling de tâche (feynmanService.pollTask) quand l'analyse n'est pas synchrone", async () => {
    vi.useFakeTimers()
    try {
      feynmanService.analyze.mockResolvedValue({ status: 'PENDING', task_id: 'task-1' })
      feynmanService.pollTask.mockResolvedValue({
        status: 'SUCCESS',
        result: { clarity_score: 60, jargon: ['osmose'], gaps: [], feedback: '', suggestion: '' },
      })

      const { wrapper } = await mountNoteFeynman()
      const textarea = wrapper.get('textarea')
      await textarea.setValue('Explication.')
      const submitButton = wrapper
        .findAll('button')
        .find((b) => b.text().includes("Analyser mon explication avec l'IA"))!
      await submitButton.trigger('click')
      // Le polling attend 2s (setTimeout) avant le premier appel à pollTask.
      await vi.advanceTimersByTimeAsync(2000)
      await flushPromises()

      expect(feynmanService.pollTask).toHaveBeenCalledWith('task-1')
      // notes-ia-planning-corrections, Task 7 : score /10 (60 -> "6,0").
      expect(wrapper.text()).toContain('6,0')
      expect(wrapper.text()).toContain('osmose')
    } finally {
      vi.useRealTimers()
    }
  })
})
