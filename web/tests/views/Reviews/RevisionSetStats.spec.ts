import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import RevisionSetStats from '../../../src/views/Reviews/RevisionSetStats.vue'
import RevisionItemModal from '../../../src/components/decks/RevisionItemModal.vue'

const SET = {
  id: 7,
  name: 'Ensemble',
  description: null,
  type: null,
  binder_id: null,
  tuning_default: 1,
  is_public: false,
  item_count: 2,
  read_only: false,
}

function itemSummary(id: number, type: string, overrides: Record<string, unknown> = {}) {
  return {
    item_id: id,
    type,
    label: `Item ${id}`,
    reviews: 1,
    success_rate: 100,
    difficulty: 1,
    retrievability: 1,
    is_leech: false,
    is_mature: false,
    due: false,
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

interface MountOverrides {
  items?: ReturnType<typeof itemSummary>[]
  grade_distribution?: { again: number; hard: number; good: number; easy: number }
  weekly_progression?: { reviews: number; success_rate: number }[]
  session_history?: { date: string; reviews: number; success_rate: number }[]
  fetchedItems?: unknown[]
}

function defaultWeeklyProgression() {
  return Array.from({ length: 6 }, () => ({ reviews: 0, success_rate: 0 }))
}

async function mountStats(setType: string | null, overrides: MountOverrides = {}) {
  const items = overrides.items ?? [itemSummary(1, 'flashcard'), itemSummary(2, 'vf')]
  const pinia = createPinia()
  setActivePinia(pinia)
  api.get.mockImplementation((url: string) => {
    if (/\/stats\/sets\/\d+$/.test(url)) {
      return Promise.resolve({
        data: {
          set_id: 7,
          type: setType,
          name: 'Ensemble',
          items_count: items.length,
          reviewed_items: items.length,
          mastered_count: 0,
          mastery_rate: 0,
          avg_success_rate: 87,
          true_retention: 0,
          leeches_count: 0,
          due_count: 0,
          avg_difficulty: 1,
          verdicts: [],
          items,
          grade_distribution: overrides.grade_distribution ?? { again: 0, hard: 0, good: 0, easy: 0 },
          weekly_progression: overrides.weekly_progression ?? defaultWeeklyProgression(),
          session_history: overrides.session_history ?? [],
        },
      })
    }
    if (/\/revision\/sets\/\d+$/.test(url)) return Promise.resolve({ data: { ...SET, type: setType } })
    if (/\/revision\/sets\/\d+\/items$/.test(url))
      return Promise.resolve({ data: { data: overrides.fetchedItems ?? [] } })
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
    const wrapper = await mountStats(null, {
      items: [itemSummary(1, 'flashcard'), itemSummary(2, 'vf')],
    })
    expect(wrapper.text()).toContain('Mixte')
  })

  it("affiche le libelle du type concret quand l'ensemble est homogene", async () => {
    const wrapper = await mountStats('qcm', { items: [itemSummary(1, 'qcm')] })
    expect(wrapper.text()).toContain('QCM')
    expect(wrapper.text()).not.toContain('Mixte')
  })

  it('affiche le taux de reussite global dans la carte hero', async () => {
    const wrapper = await mountStats('qcm', { items: [itemSummary(1, 'qcm')] })
    expect(wrapper.text()).toContain('87')
  })

  it('affiche les 4 barres de repartition des notes SM2', async () => {
    const wrapper = await mountStats('qcm', {
      items: [itemSummary(1, 'qcm')],
      grade_distribution: { again: 2, hard: 1, good: 3, easy: 1 },
    })
    expect(wrapper.findAll('[data-test="grade-bar"]')).toHaveLength(4)
  })

  it('affiche une ligne par jour dans l historique des sessions', async () => {
    const wrapper = await mountStats('qcm', {
      items: [itemSummary(1, 'qcm')],
      session_history: [
        { date: '2026-08-29', reviews: 2, success_rate: 50 },
        { date: '2026-08-28', reviews: 1, success_rate: 100 },
      ],
    })
    const rows = wrapper.findAll('[data-test="session-history-row"]')
    expect(rows).toHaveLength(2)
    expect(rows[0].text()).toContain('50%')
    expect(rows[1].text()).toContain('100%')
  })

  it('affiche un etat vide quand aucune session n a ete enregistree', async () => {
    const wrapper = await mountStats('qcm', {
      items: [itemSummary(1, 'qcm')],
      session_history: [],
    })
    expect(wrapper.findAll('[data-test="session-history-row"]')).toHaveLength(0)
    expect(wrapper.text()).toContain('Aucune session enregistrée')
  })

  it('affiche une icone de type par item dans la gestion des elements', async () => {
    const wrapper = await mountStats(null, {
      items: [itemSummary(1, 'flashcard'), itemSummary(2, 'vf'), itemSummary(3, 'qcm')],
    })
    expect(wrapper.findAll('[data-test="item-type-icon"]')).toHaveLength(3)
  })

  it('permet de modifier un element existant', async () => {
    const fetchedItem = {
      id: 1,
      set_id: 7,
      type: 'qcm',
      payload: { question: 'Q', options: [], points: 1 },
      tuning: 1,
      position: 0,
      interval: 1,
      ease_factor: 2.5,
      repetitions: 0,
      next_review: '2026-08-29T00:00:00Z',
      created_at: '2026-08-29T00:00:00Z',
      updated_at: '2026-08-29T00:00:00Z',
    }
    const wrapper = await mountStats('qcm', {
      items: [itemSummary(1, 'qcm')],
      fetchedItems: [fetchedItem],
    })

    expect(wrapper.text()).not.toContain("Modifier l'élément")
    await wrapper.get('[data-test="edit-item-1"]').trigger('click')
    expect(wrapper.text()).toContain("Modifier l'élément")

    const statsCallsBefore = api.get.mock.calls.filter((c) => /\/stats\/sets\/\d+$/.test(c[0])).length

    // Simule la sauvegarde : la modale emet "updated", le parent doit rafraichir les stats.
    const modalWrapper = wrapper.findComponent(RevisionItemModal)
    expect(modalWrapper.exists()).toBe(true)
    await modalWrapper.vm.$emit('updated')
    await flushPromises()

    const statsCallsAfter = api.get.mock.calls.filter((c) => /\/stats\/sets\/\d+$/.test(c[0])).length
    expect(statsCallsAfter).toBeGreaterThan(statsCallsBefore)
  })
})
