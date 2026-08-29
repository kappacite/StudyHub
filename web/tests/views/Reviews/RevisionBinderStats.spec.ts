import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import RevisionBinderStats from '../../../src/views/Reviews/RevisionBinderStats.vue'

function setSummary(id: number, type: string | null, overrides: Record<string, unknown> = {}) {
  return {
    set_id: id, type, name: `Ensemble ${id}`, items_count: 1, reviewed_items: 1,
    mastered_count: 0, mastery_rate: 0, avg_success_rate: 0, true_retention: 0,
    leeches_count: 0, due_count: 0, avg_difficulty: 1, ...overrides,
  }
}

const stub = { template: '<div />' }
function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/revision/binders/:id/stats', name: 'RevisionBinderStats', component: stub }],
  })
}

async function mountBinderStats(
  sets: ReturnType<typeof setSummary>[],
  byType: { type: string; sets_count: number; items_count: number; mastered_count: number; mastery_rate: number }[],
) {
  const pinia = createPinia()
  setActivePinia(pinia)
  api.get.mockImplementation((url: string) => {
    if (/\/stats\/binders\//.test(url)) {
      return Promise.resolve({
        data: {
          binder_id: 'b1', name: 'Classeur', include_descendants: true, sets_count: sets.length,
          items_count: sets.reduce((n, s) => n + (s.items_count as number), 0), reviewed_items: 0,
          mastered_count: 0, mastery_rate: 0, avg_success_rate: 0, true_retention: 0, leeches_count: 0,
          due_count: 0, avg_difficulty: 1, by_type: byType, sets, weakest_sets: sets, verdicts: [],
        },
      })
    }
    return Promise.reject(new Error(`URL non mockée: ${url}`))
  })
  const router = createTestRouter()
  await router.push('/revision/binders/b1/stats')
  await router.isReady()
  const wrapper = mount(RevisionBinderStats, { global: { plugins: [pinia, router] } })
  await flushPromises()
  return wrapper
}

describe('RevisionBinderStats', () => {
  beforeEach(() => vi.clearAllMocks())

  it("affiche Mixte pour un ensemble heterogene dans la liste des ensembles", async () => {
    const wrapper = await mountBinderStats([setSummary(1, null)], [])
    expect(wrapper.text()).toContain('Mixte')
  })

  it('affiche le libelle Flashcards dans la repartition par type', async () => {
    const wrapper = await mountBinderStats(
      [setSummary(1, null, { items_count: 2 })],
      [
        { type: 'flashcard', sets_count: 1, items_count: 1, mastered_count: 0, mastery_rate: 0 },
        { type: 'vf', sets_count: 1, items_count: 1, mastered_count: 0, mastery_rate: 0 },
      ],
    )
    expect(wrapper.text()).toContain('Flashcards')
    expect(wrapper.text()).toContain('Vrai / Faux')
  })
})
