import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import RevisionSetStats from '../../../src/views/Reviews/RevisionSetStats.vue'

const SET = { id: 7, name: 'Ensemble', description: null, type: null, binder_id: null, tuning_default: 1, is_public: false, item_count: 2, read_only: false }

function itemSummary(id: number, type: string, overrides: Record<string, unknown> = {}) {
  return {
    item_id: id, type, label: `Item ${id}`, reviews: 1, success_rate: 100,
    difficulty: 1, retrievability: 1, is_leech: false, is_mature: false, due: false,
    ...overrides,
  }
}

const stub = { template: '<div />' }
function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/revision/sets/:id/stats', name: 'RevisionSetStats', component: stub }],
  })
}

async function mountStats(setType: string | null, items: ReturnType<typeof itemSummary>[]) {
  const pinia = createPinia()
  setActivePinia(pinia)
  api.get.mockImplementation((url: string) => {
    if (/\/stats\/sets\/\d+$/.test(url)) {
      return Promise.resolve({
        data: {
          set_id: 7, type: setType, name: 'Ensemble', items_count: items.length, reviewed_items: items.length,
          mastered_count: 0, mastery_rate: 0, avg_success_rate: 0, true_retention: 0, leeches_count: 0,
          due_count: 0, avg_difficulty: 1, verdicts: [], items,
        },
      })
    }
    if (/\/revision\/sets\/\d+$/.test(url)) return Promise.resolve({ data: { ...SET, type: setType } })
    if (/\/revision\/sets\/\d+\/items$/.test(url)) return Promise.resolve({ data: { data: [] } })
    return Promise.reject(new Error(`URL non mockée: ${url}`))
  })
  const router = createTestRouter()
  await router.push('/revision/sets/7/stats')
  await router.isReady()
  const wrapper = mount(RevisionSetStats, { global: { plugins: [pinia, router] } })
  await flushPromises()
  return wrapper
}

describe('RevisionSetStats', () => {
  beforeEach(() => vi.clearAllMocks())

  it("affiche Mixte quand l'ensemble est heterogene", async () => {
    const wrapper = await mountStats(null, [itemSummary(1, 'flashcard'), itemSummary(2, 'vf')])
    expect(wrapper.text()).toContain('Mixte')
  })

  it("affiche le libelle du type concret quand l'ensemble est homogene", async () => {
    const wrapper = await mountStats('qcm', [itemSummary(1, 'qcm')])
    expect(wrapper.text()).toContain('QCM')
    expect(wrapper.text()).not.toContain('Mixte')
  })

  it('affiche une icone de type par item', async () => {
    const wrapper = await mountStats(null, [itemSummary(1, 'flashcard'), itemSummary(2, 'vf'), itemSummary(3, 'qcm')])
    expect(wrapper.findAll('[data-test="item-type-icon"]')).toHaveLength(3)
  })
})
