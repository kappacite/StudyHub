import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import Reviews from '../../../src/views/Reviews/Reviews.vue'

const HOMOGENEOUS_SET = { id: 1, name: 'QCM Bio', description: null, type: 'qcm', binder_id: null, tuning_default: 1, is_public: false, item_count: 3, read_only: false }
const MIXED_SET = { id: 2, name: 'Ensemble mixte', description: null, type: null, binder_id: null, tuning_default: 1, is_public: false, item_count: 5, read_only: false }

const stub = { template: '<div />' }
function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/reviser', name: 'Reviser', component: stub },
      { path: '/revision/sets/:id', name: 'RevisionSetDetail', component: stub },
      { path: '/revision/sets/:id/study', name: 'RevisionStudy', component: stub },
      { path: '/revision/sets/:id/run', name: 'QcmRun', component: stub },
      { path: '/revision/sets/:id/stats', name: 'RevisionSetStats', component: stub },
    ],
  })
}

async function mountReviews() {
  const pinia = createPinia()
  setActivePinia(pinia)
  api.get.mockImplementation((url: string) => {
    if (/^\/decks\?/.test(url)) return Promise.resolve({ data: { data: [] } })
    if (/^\/notes\?/.test(url)) return Promise.resolve({ data: { data: [] } })
    if (/^\/binders\?/.test(url)) return Promise.resolve({ data: { data: [] } })
    if (/^\/revision\/sets\?/.test(url)) return Promise.resolve({ data: { data: [HOMOGENEOUS_SET, MIXED_SET] } })
    if (/^\/focus\/today/.test(url)) return Promise.resolve({ data: { total_due: 0, late_count: 0, flashcard_count: 0, blurting_count: 0, assignment_count: 0, items: [] } })
    if (/^\/focus\/forecast/.test(url)) return Promise.resolve({ data: { forecast: [] } })
    if (/^\/focus\/retention/.test(url)) return Promise.resolve({ data: { by_subject: [] } })
    return Promise.reject(new Error(`URL non mockée: ${url}`))
  })
  const router = createTestRouter()
  await router.push('/reviser')
  await router.isReady()
  const wrapper = mount(Reviews, { global: { plugins: [pinia, router] } })
  await flushPromises()
  return { wrapper, router }
}

describe('Reviews - onglet Mixte', () => {
  beforeEach(() => vi.clearAllMocks())

  it("liste uniquement les ensembles heterogenes (type: null) dans l'onglet Mixte", async () => {
    const { wrapper } = await mountReviews()
    await wrapper.find('[data-test="tab-set-mixte"]').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Ensemble mixte')
    expect(wrapper.text()).not.toContain('QCM Bio')
  })

  it("le bouton Etudier de l'onglet Mixte navigue vers /study (jamais /run)", async () => {
    const { wrapper, router } = await mountReviews()
    await wrapper.find('[data-test="tab-set-mixte"]').trigger('click')
    await flushPromises()

    await wrapper.find('[data-test="study-set-2"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/revision/sets/2/study')
  })

  it('le bouton Gerer navigue vers RevisionSetDetail, plus vers /manage', async () => {
    const { wrapper, router } = await mountReviews()
    await wrapper.find('[data-test="tab-set-qcm"]').trigger('click')
    await flushPromises()

    await wrapper.find('[data-test="manage-set-1"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/revision/sets/1')
  })
})
