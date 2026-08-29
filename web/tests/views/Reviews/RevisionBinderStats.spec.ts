import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import RevisionBinderStats from '../../../src/views/Reviews/RevisionBinderStats.vue'

function setSummary(id: number, type: string | null, overrides: Record<string, unknown> = {}) {
  return {
    set_id: id,
    type,
    name: `Ensemble ${id}`,
    items_count: 1,
    reviewed_items: 1,
    mastered_count: 0,
    mastery_rate: 0,
    avg_success_rate: 0,
    true_retention: 0,
    leeches_count: 0,
    due_count: 0,
    avg_difficulty: 1,
    ...overrides,
  }
}

function deckSummary(id: number, name: string, overrides: Record<string, unknown> = {}) {
  return { id, binder_id: 'b1', name, description: '', reversed: false, tuning_default: 1, card_count: 10, created_at: '2026-01-01', tags: [], ...overrides }
}

function deckStats(id: number, retentionRate: number, overrides: Record<string, unknown> = {}) {
  return { deck_id: id, retention_rate: retentionRate, next_review: null, cards_to_review: 3, total_cards: 10, ...overrides }
}

const stub = { template: '<div />' }
function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/revision/binders/:id/stats', name: 'RevisionBinderStats', component: stub },
      { path: '/revision/sets/:id/stats', name: 'RevisionSetStats', component: stub },
      { path: '/decks/:id/study', name: 'StudyDeck', component: stub },
      { path: '/bibliotheque/:id/reviser', name: 'BinderStudy', component: stub },
    ],
  })
}

async function mountBinderStats(opts: {
  sets?: ReturnType<typeof setSummary>[]
  byType?: { type: string; sets_count: number; items_count: number; mastered_count: number; mastery_rate: number }[]
  decks?: ReturnType<typeof deckSummary>[]
  deckStatsById?: Record<number, ReturnType<typeof deckStats>>
  totalDurationSeconds?: number
  binderIds?: string[]
  statsError?: boolean
}) {
  const sets = opts.sets ?? []
  const byType = opts.byType ?? []
  const decks = opts.decks ?? []
  const deckStatsById = opts.deckStatsById ?? {}
  const totalDurationSeconds = opts.totalDurationSeconds ?? 0
  const binderIds = opts.binderIds ?? ['b1']

  const pinia = createPinia()
  setActivePinia(pinia)
  api.get.mockImplementation((url: string) => {
    if (/\/stats\/binders\//.test(url)) {
      if (opts.statsError) return Promise.reject(new Error('network down'))
      return Promise.resolve({
        data: {
          binder_id: 'b1',
          binder_ids: binderIds,
          name: 'Classeur',
          include_descendants: true,
          sets_count: sets.length,
          items_count: sets.reduce((n, s) => n + (s.items_count as number), 0),
          reviewed_items: 0,
          mastered_count: 0,
          mastery_rate: 0,
          avg_success_rate: 0,
          true_retention: 0,
          leeches_count: 0,
          due_count: 0,
          avg_difficulty: 1,
          by_type: byType,
          sets,
          weakest_sets: sets,
          verdicts: [],
          total_duration_seconds: totalDurationSeconds,
        },
      })
    }
    if (/\/stats\/decks\//.test(url)) {
      const id = Number(url.split('/').pop())
      return Promise.resolve({ data: deckStatsById[id] ?? deckStats(id, 0) })
    }
    if (/^\/decks\?/.test(url)) {
      return Promise.resolve({ data: { data: decks } })
    }
    return Promise.reject(new Error(`URL non mockée: ${url}`))
  })
  const router = createTestRouter()
  await router.push('/revision/binders/b1/stats')
  await router.isReady()
  const wrapper = mount(RevisionBinderStats, { global: { plugins: [pinia, router] } })
  await flushPromises()
  await flushPromises()
  return wrapper
}

describe('RevisionBinderStats', () => {
  beforeEach(() => vi.clearAllMocks())

  it('affiche une ligne par deck classique et par ensemble de revision, triees par maitrise decroissante', async () => {
    const decks = [deckSummary(1, 'Deck fort'), deckSummary(2, 'Deck faible')]
    const deckStatsById = {
      1: deckStats(1, 90),
      2: deckStats(2, 40),
    }
    const sets = [
      setSummary(10, 'qcm', { name: 'Set fort', mastery_rate: 80, reviewed_items: 5 }),
      setSummary(20, 'vf', { name: 'Set faible', mastery_rate: 20, reviewed_items: 5 }),
    ]
    const wrapper = await mountBinderStats({ decks, deckStatsById, sets })

    const rows = wrapper.findAll('[data-test="merged-row"]')
    expect(rows).toHaveLength(4)
    const names = rows.map((r) => r.text())
    // Ordre attendu par maitrise decroissante : 90 (Deck fort), 80 (Set fort), 40 (Deck faible), 20 (Set faible)
    expect(names[0]).toContain('Deck fort')
    expect(names[1]).toContain('Set fort')
    expect(names[2]).toContain('Deck faible')
    expect(names[3]).toContain('Set faible')
  })

  it("affiche Mixte pour un ensemble heterogene dans la liste des ensembles", async () => {
    const wrapper = await mountBinderStats({ sets: [setSummary(1, null)] })
    expect(wrapper.text()).toContain('Mixte')
  })

  it('affiche le temps total d etude reel comme 5e carte, sans remplacer les 4 existantes (Task 9)', async () => {
    const wrapper = await mountBinderStats({
      sets: [setSummary(1, 'qcm')],
      totalDurationSeconds: 8100,
    })
    expect(wrapper.text()).toContain("Temps total d'étude")
    expect(wrapper.text()).toContain('2h 15')
    // Les 4 cartes existantes (Task 6, deja revues/approuvees) restent presentes.
    expect(wrapper.text()).toContain('Cartes totales')
    expect(wrapper.text()).toContain('Cartes maîtrisées')
    expect(wrapper.text()).toContain('Taux de réussite moyen')
    expect(wrapper.text()).toContain('À réviser')
  })

  it('affiche le libelle Flashcards dans la repartition par type', async () => {
    const wrapper = await mountBinderStats({
      sets: [setSummary(1, null, { items_count: 2 })],
      byType: [
        { type: 'flashcard', sets_count: 1, items_count: 1, mastered_count: 0, mastery_rate: 0 },
        { type: 'vf', sets_count: 1, items_count: 1, mastered_count: 0, mastery_rate: 0 },
      ],
    })
    expect(wrapper.text()).toContain('Flashcards')
    expect(wrapper.text()).toContain('Vrai / Faux')
  })

  // ── Finding #3 (revue de branche reviser-hub) : un deck dont le parent
  // direct est un SOUS-classeur doit apparaitre dans la liste fusionnee quand
  // includeDescendants est actif (meme perimetre que les ensembles de
  // revision), et en disparaitre quand il ne l'est plus ─────────────────────
  describe('perimetre descendants (decks d\'un sous-classeur)', () => {
    it('inclut un deck d\'un sous-classeur quand le backend renvoie ce sous-classeur dans binder_ids', async () => {
      const decks = [deckSummary(1, 'Deck racine', { binder_id: 'b1' }), deckSummary(2, 'Deck enfant', { binder_id: 'child-1' })]
      const deckStatsById = { 1: deckStats(1, 50), 2: deckStats(2, 70) }
      const wrapper = await mountBinderStats({
        decks,
        deckStatsById,
        binderIds: ['b1', 'child-1'],
      })
      const rows = wrapper.findAll('[data-test="merged-row"]')
      expect(rows).toHaveLength(2)
      expect(wrapper.text()).toContain('Deck racine')
      expect(wrapper.text()).toContain('Deck enfant')
    })

    it('exclut un deck d\'un sous-classeur quand binder_ids ne contient que le classeur racine (descendants desactives)', async () => {
      const decks = [deckSummary(1, 'Deck racine', { binder_id: 'b1' }), deckSummary(2, 'Deck enfant', { binder_id: 'child-1' })]
      const deckStatsById = { 1: deckStats(1, 50), 2: deckStats(2, 70) }
      const wrapper = await mountBinderStats({
        decks,
        deckStatsById,
        binderIds: ['b1'],
      })
      const rows = wrapper.findAll('[data-test="merged-row"]')
      expect(rows).toHaveLength(1)
      expect(wrapper.text()).toContain('Deck racine')
      expect(wrapper.text()).not.toContain('Deck enfant')
    })
  })

  // ── Finding #4 (revue de branche reviser-hub) : page blanche sans message
  // ni retry en cas d'echec de chargement des stats ──────────────────────────
  describe('etat erreur', () => {
    it('affiche un message d\'erreur (et pas une page blanche) quand /stats/binders/:id echoue', async () => {
      const wrapper = await mountBinderStats({ statsError: true })
      const error = wrapper.find('[data-test="stats-error"]')
      expect(error.exists()).toBe(true)
      expect(error.text()).toBe('Impossible de charger les statistiques.')
      expect(wrapper.find('[data-test="revise-binder-button"]').exists()).toBe(false)
    })
  })
})
