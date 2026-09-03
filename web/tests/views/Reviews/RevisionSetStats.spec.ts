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
    routes: [
      { path: '/revision/sets/:id/stats', name: 'RevisionSetStats', component: stub },
      { path: '/revision/sets/:id/study', name: 'RevisionStudy', component: stub },
      { path: '/revision/sets/:id/run', name: 'QcmRun', component: stub },
    ],
  })
}

interface MountOverrides {
  items?: ReturnType<typeof itemSummary>[]
  grade_distribution?: { again: number; hard: number; good: number; easy: number }
  weekly_progression?: { reviews: number; success_rate: number }[]
  session_history?: {
    date: string
    reviews: number
    success_rate: number
    duration_seconds?: number
  }[]
  total_duration_seconds?: number
  next_review_at?: string | null
  statsError?: boolean
  avg_retrievability?: number
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
      if (overrides.statsError) return Promise.reject(new Error('network down'))
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
          avg_retrievability: overrides.avg_retrievability ?? 0,
          leeches_count: 0,
          due_count: 0,
          avg_difficulty: 1,
          verdicts: [],
          items,
          grade_distribution: overrides.grade_distribution ?? { again: 0, hard: 0, good: 0, easy: 0 },
          weekly_progression: overrides.weekly_progression ?? defaultWeeklyProgression(),
          session_history: overrides.session_history ?? [],
          total_duration_seconds: overrides.total_duration_seconds ?? 0,
          next_review_at: overrides.next_review_at ?? null,
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
  return { wrapper, router }
}

describe('RevisionSetStats', () => {
  beforeEach(() => vi.clearAllMocks())

  it("affiche Mixte quand l'ensemble est heterogene", async () => {
    const { wrapper } = await mountStats(null, {
      items: [itemSummary(1, 'flashcard'), itemSummary(2, 'vf')],
    })
    expect(wrapper.text()).toContain('Mixte')
  })

  it("affiche le libelle du type concret quand l'ensemble est homogene", async () => {
    const { wrapper } = await mountStats('qcm', { items: [itemSummary(1, 'qcm')] })
    expect(wrapper.text()).toContain('QCM')
    expect(wrapper.text()).not.toContain('Mixte')
  })

  it('affiche le taux de reussite global dans la carte hero', async () => {
    const { wrapper } = await mountStats('qcm', { items: [itemSummary(1, 'qcm')] })
    expect(wrapper.text()).toContain('87')
  })

  // notes-ia-planning-corrections : demande explicite utilisateur -- ajoute la
  // rétention actuelle (avg_retrievability, Ebbinghaus) dans la carte hero, même
  // métrique que RevisionBinderStats.vue (décroît en continu depuis la dernière
  // révision, jamais bloquée à 0 comme true_retention tant que rien n'est mûr).
  it('affiche la rétention actuelle (avg_retrievability) dans la carte hero', async () => {
    const { wrapper } = await mountStats('qcm', {
      items: [itemSummary(1, 'qcm')],
      avg_retrievability: 54.2,
    })
    expect(wrapper.text()).toContain('Rétention actuelle : 54.2%')
  })

  it('affiche les 4 barres de repartition des notes SM2', async () => {
    const { wrapper } = await mountStats('qcm', {
      items: [itemSummary(1, 'qcm')],
      grade_distribution: { again: 2, hard: 1, good: 3, easy: 1 },
    })
    expect(wrapper.findAll('[data-test="grade-bar"]')).toHaveLength(4)
  })

  it('affiche une ligne par jour dans l historique des sessions', async () => {
    const { wrapper } = await mountStats('qcm', {
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
    const { wrapper } = await mountStats('qcm', {
      items: [itemSummary(1, 'qcm')],
      session_history: [],
    })
    expect(wrapper.findAll('[data-test="session-history-row"]')).toHaveLength(0)
    expect(wrapper.text()).toContain('Aucune session enregistrée')
  })

  it('affiche "Cartes vues" comme libelle de colonne (et non "Revisions")', async () => {
    const { wrapper } = await mountStats('qcm', {
      items: [itemSummary(1, 'qcm')],
      session_history: [{ date: '2026-08-29', reviews: 2, success_rate: 50 }],
    })
    expect(wrapper.text()).toContain('Cartes vues')
  })

  it('colore le score de session avec le meme seuil (>=70 succes, sinon echec) que partout ailleurs', async () => {
    const { wrapper } = await mountStats('qcm', {
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

  it('affiche le temps cumule reel dans le trio hero, formate en heures/minutes (Task 9)', async () => {
    const { wrapper } = await mountStats('qcm', {
      items: [itemSummary(1, 'qcm')],
      total_duration_seconds: 8100,
    })
    expect(wrapper.text()).toContain('Temps cumulé')
    expect(wrapper.text()).toContain('2h 15')
  })

  it('affiche la duree reelle par jour dans la colonne Duree de l historique (Task 9)', async () => {
    const { wrapper } = await mountStats('qcm', {
      items: [itemSummary(1, 'qcm')],
      session_history: [{ date: '2026-08-29', reviews: 2, success_rate: 50, duration_seconds: 480 }],
    })
    const rows = wrapper.findAll('[data-test="session-history-row"]')
    expect(rows[0].text()).toContain('8 min')
  })

  it('colore les barres de progression hebdomadaire avec le meme seuil de reussite (>=70)', async () => {
    const { wrapper } = await mountStats('qcm', {
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

  // ── Finding #8 (revue de branche reviser-hub) : le bouton "Reviser cette
  // serie" ignorait la branche /run pour un ensemble QCM homogene ──────────
  describe('bouton "Reviser cette serie"', () => {
    it('navigue vers /revision/sets/:id/run pour un ensemble QCM homogene', async () => {
      const { wrapper, router } = await mountStats('qcm', { items: [itemSummary(1, 'qcm')] })
      await wrapper.get('[data-test="study-set-button"]').trigger('click')
      await flushPromises()
      expect(router.currentRoute.value.fullPath).toBe('/revision/sets/7/run')
    })

    it('navigue vers /revision/sets/:id/study pour un ensemble heterogene', async () => {
      const { wrapper, router } = await mountStats(null, {
        items: [itemSummary(1, 'flashcard'), itemSummary(2, 'vf')],
      })
      await wrapper.get('[data-test="study-set-button"]').trigger('click')
      await flushPromises()
      expect(router.currentRoute.value.fullPath).toBe('/revision/sets/7/study')
    })

    it('navigue vers /revision/sets/:id/study pour un ensemble homogene non-QCM', async () => {
      const { wrapper, router } = await mountStats('vf', { items: [itemSummary(1, 'vf')] })
      await wrapper.get('[data-test="study-set-button"]').trigger('click')
      await flushPromises()
      expect(router.currentRoute.value.fullPath).toBe('/revision/sets/7/study')
    })
  })

  // ── Finding #4 (revue de branche reviser-hub) : page blanche sans message
  // ni retry en cas d'echec de chargement des stats ──────────────────────────
  describe('etat erreur', () => {
    it('affiche un message d\'erreur (et pas une page blanche) quand /stats/sets/:id echoue', async () => {
      const { wrapper } = await mountStats('qcm', { statsError: true })
      const error = wrapper.find('[data-test="stats-error"]')
      expect(error.exists()).toBe(true)
      expect(error.text()).toBe('Impossible de charger les statistiques.')
      expect(wrapper.find('[data-test="study-set-button"]').exists()).toBe(false)
    })
  })

  // ── Task 7 : date de prochaine echeance (next_review_at, Task 4 backend) ──
  describe('prochaine echeance (next_review_at)', () => {
    it('affiche la date formatee quand next_review_at est fourni', async () => {
      const { wrapper } = await mountStats('qcm', {
        items: [itemSummary(1, 'qcm')],
        next_review_at: '2026-09-15T10:00:00Z',
      })
      const next = wrapper.find('[data-test="next-review-at"]')
      expect(next.exists()).toBe(true)
      expect(next.text()).toContain('15')
      expect(next.text()).toContain('sept')
      expect(next.text()).toContain('2026')
    })

    it("n'affiche pas de date factice quand next_review_at est null (ensemble sans item)", async () => {
      const { wrapper } = await mountStats('qcm', {
        items: [],
        next_review_at: null,
      })
      expect(wrapper.find('[data-test="next-review-at"]').exists()).toBe(false)
    })
  })
})
