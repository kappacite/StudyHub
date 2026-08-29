import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}))
vi.mock('../../../src/services/api', () => ({ default: api }))

import NoteFeynman from '../../../src/views/Notes/NoteFeynman.vue'

const NOTE = { id: 42, title: 'Ma note', content: 'Contenu de la note' }

interface ApiOverrides {
  note?: () => Promise<unknown>
  analyze?: () => Promise<unknown>
  task?: () => Promise<unknown>
}

function makeGetImpl(over: ApiOverrides = {}) {
  return (url: string) => {
    if (/^\/notes\/\d+$/.test(url)) {
      return (over.note ?? (() => Promise.resolve({ data: NOTE })))()
    }
    if (/^\/feynman\/tasks\/.+$/.test(url)) {
      return (over.task ?? (() => Promise.reject(new Error(`URL GET non mockée: ${url}`))))()
    }
    return Promise.reject(new Error(`URL GET non mockée dans le test: ${url}`))
  }
}

function makePostImpl(over: ApiOverrides = {}) {
  return (url: string) => {
    if (url === '/feynman/analyze') {
      return (over.analyze ?? (() => Promise.reject(new Error('/feynman/analyze non mocké'))))()
    }
    return Promise.reject(new Error(`URL POST non mockée dans le test: ${url}`))
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
    api.post.mockImplementation(makePostImpl())
  })

  it("charge le titre de la note depuis l'API au montage", async () => {
    const { wrapper } = await mountNoteFeynman()
    expect(api.get).toHaveBeenCalledWith('/notes/42')
    expect(wrapper.text()).toContain('Ma note')
  })

  it("soumet l'explication et affiche le score renvoye par l'IA", async () => {
    api.post.mockImplementation(
      makePostImpl({
        analyze: () =>
          Promise.resolve({
            data: {
              status: 'SUCCESS',
              result: {
                clarity_score: 82,
                jargon: [],
                gaps: [],
                feedback: 'Bien',
                suggestion: '',
              },
            },
          }),
      }),
    )

    const { wrapper } = await mountNoteFeynman()

    const textarea = wrapper.get('textarea')
    await textarea.setValue("Voici mon explication simplifiée du concept.")

    const submitButton = wrapper
      .findAll('button')
      .find((b) => b.text().includes("Analyser mon explication avec l'IA"))!
    await submitButton.trigger('click')
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith('/feynman/analyze', {
      note_id: '42',
      user_explanation: 'Voici mon explication simplifiée du concept.',
      duration_seconds: expect.any(Number),
    })
    expect(wrapper.text()).toContain('82')
    expect(wrapper.text()).toContain('Bien')
  })
})
