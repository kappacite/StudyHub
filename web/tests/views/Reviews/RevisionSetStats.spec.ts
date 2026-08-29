import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import RevisionSetStats from '../../../src/views/Reviews/RevisionSetStats.vue'

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

  it('affiche "Cartes vues" comme libelle de colonne (et non "Revisions")', async () => {
    const wrapper = await mountStats('qcm', {
      items: [itemSummary(1, 'qcm')],
      session_history: [{ date: '2026-08-29', reviews: 2, success_rate: 50 }],
    })
    expect(wrapper.text()).toContain('Cartes vues')
  })

  it('colore le score de session avec le meme seuil (>=70 succes, sinon echec) que partout ailleurs', async () => {
    const wrapper = await mountStats('qcm', {
      items: [itemSummary(1, 'qcm')],
      session_history: [
        { date: '2026-08-29', reviews: 1, success_rate: 70 },
        { date: '2026-08-28', reviews: 1, success_rate: 69 },
      ],
    })
    const scores = wrapper.findAll('[data-test="session-score"]')
    expect(scores[0].classes()).toContain('text-success')
    expect(scores[1].classes()).toContain('text-danger')
  })

  it('colore les barres de progression hebdomadaire avec le meme seuil de reussite (>=70)', async () => {
    const wrapper = await mountStats('qcm', {
      items: [itemSummary(1, 'qcm')],
      weekly_progression: [
        { reviews: 0, success_rate: 0 },
        { reviews: 1, success_rate: 69 },
        { reviews: 1, success_rate: 70 },
        { reviews: 0, success_rate: 0 },
        { reviews: 0, success_rate: 0 },
        { reviews: 0, success_rate: 0 },
      ],
    })
    const bars = wrapper.findAll('[data-test="week-bar"]')
    expect(bars).toHaveLength(6)
    expect(bars[0].classes()).toContain('bg-line') // pas de revision cette semaine-la
    expect(bars[1].classes()).toContain('bg-danger') // 69% < seuil
    expect(bars[2].classes()).toContain('bg-success') // 70% >= seuil
  })
})
