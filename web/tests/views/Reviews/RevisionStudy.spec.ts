import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import RevisionStudy from '../../../src/views/Reviews/RevisionStudy.vue'

const HETEROGENEOUS_SET = { id: 7, name: 'Mixte', description: null, type: null, binder_id: null, tuning_default: 1, is_public: false, item_count: 2 }

function item(id: number, type: string, payload: Record<string, unknown>) {
  return { id, set_id: 7, type, payload, tuning: 1, position: 0, interval: 0, ease_factor: 2.5, repetitions: 0, next_review: '', created_at: '', updated_at: '' }
}

const stub = { template: '<div />' }
function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/revision/sets/:id/study', name: 'RevisionStudy', component: stub },
      { path: '/revision/sets/:id/run', name: 'QcmRun', component: stub },
    ],
  })
}

async function mountStudy(path: string, setResponse = HETEROGENEOUS_SET, items: unknown[] = []) {
  const pinia = createPinia()
  setActivePinia(pinia)
  api.get.mockImplementation((url: string) => {
    if (/\/revision\/sets\/\d+$/.test(url)) return Promise.resolve({ data: setResponse })
    if (/\/revision\/sets\/\d+\/study$/.test(url)) return Promise.resolve({ data: items })
    return Promise.reject(new Error(`non mocké: ${url}`))
  })
  const router = createTestRouter()
  await router.push(path)
  await router.isReady()
  const wrapper = mount(RevisionStudy, { global: { plugins: [pinia, router] } })
  await flushPromises()
  return { wrapper, router }
}

describe('RevisionStudy — dispatch par item.type (ensembles heterogenes)', () => {
  beforeEach(() => vi.clearAllMocks())

  it('rend le bon gabarit pour chaque item selon son propre type, dans une session mixte', async () => {
    const items = [item(1, 'vf', { assertion: 'Le ciel est bleu.', correct: true }), item(2, 'flashcard', { front: 'Chat', back: 'Cat' })]
    const { wrapper } = await mountStudy('/revision/sets/7/study', HETEROGENEOUS_SET, items)

    expect(wrapper.text()).toContain('Le ciel est bleu.')
    expect(wrapper.text()).not.toContain('Chat')
  })

  it('branche flashcard : recto, revele le verso, auto-evaluation 1/3/5', async () => {
    api.post.mockResolvedValue({ data: { id: 2, set_id: 7 } })
    const items = [item(2, 'flashcard', { front: 'Chat', back: 'Cat' })]
    const { wrapper } = await mountStudy('/revision/sets/7/study', HETEROGENEOUS_SET, items)

    expect(wrapper.text()).toContain('Chat')
    expect(wrapper.text()).not.toContain('Cat')
    await wrapper.find('[data-test="reveal-flashcard-button"]').trigger('click')
    expect(wrapper.text()).toContain('Cat')

    await wrapper.find('[data-test="self-eval-acquis"]').trigger('click')
    await flushPromises()
    expect(api.post).toHaveBeenCalledWith('/revision/sets/7/study/answer/2', { score: 5 })
  })

  it('filtre la session par type quand ?type= est present', async () => {
    const items = [item(1, 'vf', { assertion: 'A', correct: true }), item(2, 'flashcard', { front: 'B', back: 'C' })]
    const { wrapper } = await mountStudy('/revision/sets/7/study?type=vf', HETEROGENEOUS_SET, items)

    expect(wrapper.text()).toContain('A')
    expect(wrapper.text()).not.toContain('B')
  })

  it('non-regression : branche vf existante fonctionne toujours sur un ensemble homogene', async () => {
    const homogeneous = { ...HETEROGENEOUS_SET, type: 'vf' }
    const items = [item(1, 'vf', { assertion: 'Le ciel est bleu.', correct: true })]
    const { wrapper } = await mountStudy('/revision/sets/7/study', homogeneous, items)
    expect(wrapper.text()).toContain('Le ciel est bleu.')
  })

  it('non-regression : redirige toujours vers /run pour un ensemble QCM homogene sans filtre', async () => {
    const qcmSet = { ...HETEROGENEOUS_SET, type: 'qcm' }
    const { router } = await mountStudy('/revision/sets/7/study', qcmSet, [])
    expect(router.currentRoute.value.fullPath).toBe('/revision/sets/7/run')
  })
})
