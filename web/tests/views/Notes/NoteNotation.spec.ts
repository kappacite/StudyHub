import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

const notationService = vi.hoisted(() => ({
  getExisting: vi.fn(),
  grade: vi.fn(),
  pollTask: vi.fn(),
}))
vi.mock('../../../src/services/notationService', () => ({ default: notationService }))

import NoteNotation from '../../../src/views/Notes/NoteNotation.vue'

const NOTE = { id: '42', binder_id: null, title: 'Réactions de substitution nucléophile', content: 'Contenu', created_at: '', updated_at: '', tags: [] }

function makeGetImpl() {
  return (url: string) => {
    if (/^\/notes\/\d+$/.test(url)) return Promise.resolve({ data: NOTE })
    return Promise.reject(new Error(`URL GET non mockée: ${url}`))
  }
}

const stub = { template: '<div />' }
function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/notes/:id', name: 'NoteEdit', component: stub },
      { path: '/notes/:id/notation', name: 'NoteNotation', component: stub },
    ],
  })
}

async function mountNoteNotation() {
  const pinia = createPinia()
  setActivePinia(pinia)
  const router = createTestRouter()
  await router.push('/notes/42/notation')
  await router.isReady()
  const wrapper = mount(NoteNotation, { global: { plugins: [pinia, router] } })
  await flushPromises()
  return { wrapper, router }
}

describe('NoteNotation — écran dédié conforme au canevas (notes-ia-planning-corrections, Task 13)', () => {
  beforeEach(() => {
    api.get.mockReset()
    api.get.mockImplementation(makeGetImpl())
    notationService.getExisting.mockReset()
    notationService.grade.mockReset()
    notationService.pollTask.mockReset()
  })

  it('charge le titre de la note et lance directement la notation quand aucune n\'existe', async () => {
    notationService.getExisting.mockResolvedValue(null)
    notationService.grade.mockResolvedValue({
      status: 'SUCCESS',
      result: { score: 82, verdict: 'Note solide.', points_forts: ['A'], ameliorations: [], suggestions: 'S' },
    })
    const { wrapper } = await mountNoteNotation()

    expect(wrapper.text()).toContain('Réactions de substitution nucléophile')
    expect(wrapper.text()).toContain('Notation de la note')
    expect(notationService.grade).toHaveBeenCalledWith('42')
    expect(wrapper.text()).toContain('8,2')
    expect(wrapper.text()).toContain('Note solide.')
  })

  it('propose voir/reevaluer quand une notation existe deja, ne lance pas immediatement', async () => {
    notationService.getExisting.mockResolvedValue({
      score: 75, verdict: 'Ancien resultat.', points_forts: [], ameliorations: [], suggestions: '',
    })
    const { wrapper } = await mountNoteNotation()

    expect(wrapper.text()).toContain('Voir la notation existante')
    expect(wrapper.text()).toContain('Réévaluer')
    expect(notationService.grade).not.toHaveBeenCalled()
  })

  it('clic sur "Voir la notation existante" affiche le resultat stocke', async () => {
    notationService.getExisting.mockResolvedValue({
      score: 75, verdict: 'Bien joué.', points_forts: [], ameliorations: [], suggestions: '',
    })
    const { wrapper } = await mountNoteNotation()

    const btn = wrapper.findAll('button').find((b) => b.text() === 'Voir la notation existante')!
    await btn.trigger('click')

    expect(wrapper.text()).toContain('Bien joué.')
    expect(notationService.grade).not.toHaveBeenCalled()
  })

  it('clic sur "Réévaluer" lance une nouvelle notation', async () => {
    notationService.getExisting.mockResolvedValue({
      score: 75, verdict: 'Ancien.', points_forts: [], ameliorations: [], suggestions: '',
    })
    notationService.grade.mockResolvedValue({
      status: 'SUCCESS',
      result: { score: 95, verdict: 'Nouveau.', points_forts: [], ameliorations: [], suggestions: '' },
    })
    const { wrapper } = await mountNoteNotation()

    const btn = wrapper.findAll('button').find((b) => b.text() === 'Réévaluer')!
    await btn.trigger('click')
    await flushPromises()

    expect(notationService.grade).toHaveBeenCalledWith('42')
    expect(wrapper.text()).toContain('Nouveau.')
  })

  it('bouton Retour navigue vers la note', async () => {
    notationService.getExisting.mockResolvedValue(null)
    notationService.grade.mockResolvedValue({ status: 'SUCCESS', result: { score: 50 } })
    const { wrapper, router } = await mountNoteNotation()
    const push = vi.spyOn(router, 'push')

    await wrapper.find('[data-test="back-to-note"]').trigger('click')
    expect(push).toHaveBeenCalledWith('/notes/42')
  })
})
