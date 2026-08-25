// Suite TDD écran 2 (Accueil) — voir ETAT.md « Écran 2 — Accueil » pour l'inventaire
// complet et le comportement attendu état par état (skill migration-ecran).
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia, type Pinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({
  get: vi.fn(),
}))
vi.mock('../../../src/services/api', () => ({ default: api }))

import Accueil from '../../../src/views/Home/Accueil.vue'
import { BaseButton, BaseEmptyState, ListRow, StatCard } from '../../../src/components/ui/base'
import { useAuthStore, type User } from '../../../src/stores/auth'
import type { FocusItem, ForecastItem, RetentionSubject } from '../../../src/services/focusService'
import type { Deck } from '../../../src/stores/decks'

// ─── Fixtures par défaut ─────────────────────────────────────────────────────

const DEFAULT_USER: User = {
  id: 1,
  email: 'alice@studyhub.fr',
  username: 'alice',
  created_at: '2026-01-01T00:00:00Z',
}

const DEFAULT_ITEMS: FocusItem[] = [
  { type: 'deck', id: 10, title: 'Deck Histoire', count: 5, is_late: true, last_session_ago_days: 3 },
  { type: 'note', id: 20, title: 'Note Chimie', count: 0, is_late: false, last_session_ago_days: null },
]

const DEFAULT_FOCUS_TODAY = {
  total_due: 2,
  late_count: 1,
  flashcard_count: 1,
  blurting_count: 1,
  assignment_count: 0,
  items: DEFAULT_ITEMS,
}

const DEFAULT_FORECAST: ForecastItem[] = Array.from({ length: 14 }, (_, i) => ({
  date: `day-${i}`,
  count: i % 5,
  load_level: (['low', 'medium', 'high'] as const)[i % 3],
}))

const DEFAULT_RETENTION: RetentionSubject[] = [
  { binder_id: 'b1', binder_name: 'Mathématiques', retention_pct: 82, overdue_count: 0, trend_7d: 4 },
  { binder_id: 'b2', binder_name: 'Chimie', retention_pct: 45, overdue_count: 2, trend_7d: -3 },
]

function makeDeck(id: number, overrides: Partial<Deck> = {}): Deck {
  return {
    id,
    binder_id: 'b1',
    name: `Deck ${id}`,
    description: '',
    reversed: false,
    tuning_default: 1,
    card_count: 10,
    created_at: '2026-01-01T00:00:00Z',
    tags: [],
    ...overrides,
  }
}

const DEFAULT_DECKS: Deck[] = [makeDeck(1), makeDeck(2)]

const DEFAULT_OVERVIEW = { total_reviewed: 120, total_correct: 90, total_time_seconds: 5400, streak: 7 }
const DEFAULT_HEATMAP: Array<{ date: string; duration: number; count: number }> = []
const DEFAULT_SESSIONS: Array<{ duration_seconds: number }> = []

interface ApiOverrides {
  focusToday?: () => Promise<unknown>
  focusForecast?: () => Promise<unknown>
  focusRetention?: () => Promise<unknown>
  decks?: () => Promise<unknown>
  overview?: () => Promise<unknown>
  heatmap?: () => Promise<unknown>
  sessions?: () => Promise<unknown>
}

function makeApiGetMock(over: ApiOverrides = {}) {
  return vi.fn((url: string) => {
    if (url.startsWith('/focus/today')) {
      return (over.focusToday ?? (() => Promise.resolve({ data: DEFAULT_FOCUS_TODAY })))()
    }
    if (url.startsWith('/focus/forecast')) {
      return (over.focusForecast ?? (() => Promise.resolve({ data: { forecast: DEFAULT_FORECAST } })))()
    }
    if (url.startsWith('/focus/retention')) {
      return (over.focusRetention ?? (() => Promise.resolve({ data: { by_subject: DEFAULT_RETENTION } })))()
    }
    if (url.startsWith('/decks')) {
      return (over.decks ?? (() => Promise.resolve({ data: { data: DEFAULT_DECKS } })))()
    }
    if (url === '/stats/overview') {
      return (over.overview ?? (() => Promise.resolve({ data: DEFAULT_OVERVIEW })))()
    }
    if (url === '/stats/heatmap') {
      return (over.heatmap ?? (() => Promise.resolve({ data: DEFAULT_HEATMAP })))()
    }
    if (url === '/stats/sessions') {
      return (over.sessions ?? (() => Promise.resolve({ data: DEFAULT_SESSIONS })))()
    }
    return Promise.reject(new Error(`URL non mockée dans le test: ${url}`))
  })
}

// Stub minimal pour les routes de destination (deck/note/bibliothèque) — seul le
// chemin résolu par le routeur mémoire nous importe ici, pas leur rendu.
const stub = { template: '<div />' }

function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/accueil', name: 'Accueil', component: stub },
      { path: '/decks/:id/study', name: 'StudyDeck', component: stub },
      { path: '/notes/:id/blurting', name: 'Blurting', component: stub },
      { path: '/bibliotheque/:id?', name: 'Bibliotheque', component: stub },
    ],
  })
}

async function mountAccueil(opts: { user?: User | null; flush?: boolean } = {}) {
  const { user = DEFAULT_USER, flush = true } = opts

  const pinia: Pinia = createPinia()
  setActivePinia(pinia)
  const authStore = useAuthStore()
  if (user) {
    authStore.token = 'tok'
    authStore.user = user
  }

  const router = createTestRouter()
  router.push('/accueil')
  await router.isReady()

  const wrapper = mount(Accueil, {
    global: {
      plugins: [pinia, router],
      directives: { motion: {} },
    },
  })

  if (flush) await flushPromises()

  return { wrapper, router }
}

describe('Accueil', () => {
  beforeEach(() => {
    api.get.mockImplementation(makeApiGetMock())
  })

  // ── Appels API au montage ────────────────────────────────────────────
  describe('appels API au montage', () => {
    it('déclenche les 6 appels attendus (focus, decks, overview, heatmap, sessions) en parallèle', async () => {
      await mountAccueil()
      const urls = api.get.mock.calls.map((c) => c[0] as string)
      expect(urls.some((u) => u.startsWith('/focus/today'))).toBe(true)
      expect(urls.some((u) => u.startsWith('/focus/forecast'))).toBe(true)
      expect(urls.some((u) => u.startsWith('/focus/retention'))).toBe(true)
      expect(urls.some((u) => u.startsWith('/decks'))).toBe(true)
      expect(urls).toContain('/stats/overview')
      expect(urls).toContain('/stats/heatmap')
      expect(urls).toContain('/stats/sessions')
    })
  })

  // ── En-tête ───────────────────────────────────────────────────────────
  describe('en-tête', () => {
    it('affiche le titre "Accueil" et le sous-titre statique', async () => {
      const { wrapper } = await mountAccueil()
      expect(wrapper.get('h1').text()).toBe('Accueil')
      expect(wrapper.text()).toContain('Vos priorités du jour, en un coup d\'œil.')
    })

    it('affiche le bouton "Continuer à réviser (N)" activé quand des révisions sont dues', async () => {
      const { wrapper } = await mountAccueil()
      const button = wrapper
        .findAllComponents(BaseButton)
        .find((b) => b.text().includes('Continuer à réviser'))!
      expect(button.text()).toContain('Continuer à réviser (2)')
      expect(button.attributes('disabled')).toBeUndefined()
    })

    it('affiche "Tout est à jour" et désactive le bouton quand aucune révision n\'est due', async () => {
      api.get.mockImplementation(
        makeApiGetMock({
          focusToday: () => Promise.resolve({ data: { ...DEFAULT_FOCUS_TODAY, total_due: 0, late_count: 0, items: [] } }),
        }),
      )
      const { wrapper } = await mountAccueil()
      const button = wrapper
        .findAllComponents(BaseButton)
        .find((b) => b.text().trim() === 'Tout est à jour')!
      expect(button.attributes('disabled')).toBeDefined()
    })

    it('le clic sur le bouton d\'action lance la révision unifiée et navigue vers le premier item (en retard prioritaire)', async () => {
      const { wrapper, router } = await mountAccueil()
      const button = wrapper
        .findAllComponents(BaseButton)
        .find((b) => b.text().includes('Continuer à réviser'))!
      await button.trigger('click')
      await flushPromises()
      // Deck Histoire (id 10) est en retard : priorité sur Note Chimie (id 20).
      expect(router.currentRoute.value.fullPath).toBe('/decks/10/study?focus=true')
    })
  })

  // ── Carte hero (salutation, résumé, série) ──────────────────────────
  describe('carte hero', () => {
    it('affiche la salutation avec le nom d\'utilisateur', async () => {
      const { wrapper } = await mountAccueil()
      expect(wrapper.text()).toContain('Prêt·e à apprendre, alice ?')
    })

    it('affiche le résumé du jour avec le décompte en retard', async () => {
      const { wrapper } = await mountAccueil()
      expect(wrapper.text()).toContain('2 élément(s) à réviser aujourd\'hui (dont 1 en retard).')
    })

    it('affiche un résumé positif quand aucune révision n\'est due', async () => {
      api.get.mockImplementation(
        makeApiGetMock({
          focusToday: () => Promise.resolve({ data: { ...DEFAULT_FOCUS_TODAY, total_due: 0, late_count: 0, items: [] } }),
        }),
      )
      const { wrapper } = await mountAccueil()
      expect(wrapper.text()).toContain('Aucune révision en attente aujourd\'hui — beau travail !')
    })

    it('affiche la série (streak) en jours', async () => {
      const { wrapper } = await mountAccueil()
      expect(wrapper.text()).toContain('7 jour(s) de suite')
    })
  })

  // ── File de révision ─────────────────────────────────────────────────
  describe('file de révision ("À réviser maintenant")', () => {
    it('affiche un ListRow par item dû, avec titre et sous-titre selon le type', async () => {
      const { wrapper } = await mountAccueil()
      const rows = wrapper.findAllComponents(ListRow)
      expect(rows).toHaveLength(2)
      expect(rows[0].props('title')).toBe('Deck Histoire')
      expect(rows[0].props('subtitle')).toBe('5 carte(s) mémoire à réviser')
      expect(rows[1].props('title')).toBe('Note Chimie')
      expect(rows[1].props('subtitle')).toBe('Feuille blanche à restituer (Blurting)')
    })

    it('affiche le badge "En retard" uniquement sur les items en retard', async () => {
      const { wrapper } = await mountAccueil()
      const rows = wrapper.findAllComponents(ListRow)
      expect(rows[0].text()).toContain('En retard')
      expect(rows[1].text()).not.toContain('En retard')
    })

    it('navigue vers /decks/:id/study au clic sur "Réviser" pour un deck', async () => {
      const { wrapper, router } = await mountAccueil()
      const rows = wrapper.findAllComponents(ListRow)
      await rows[0].findComponent(BaseButton).trigger('click')
      await flushPromises()
      expect(router.currentRoute.value.fullPath).toBe('/decks/10/study?focus=true')
    })

    it('navigue vers /notes/:id/blurting au clic sur "Réviser" pour une feuille blanche', async () => {
      const { wrapper, router } = await mountAccueil()
      const rows = wrapper.findAllComponents(ListRow)
      await rows[1].findComponent(BaseButton).trigger('click')
      await flushPromises()
      expect(router.currentRoute.value.fullPath).toBe('/notes/20/blurting?focus=true&from=focus')
    })

    it('navigue vers /bibliotheque/:id au clic sur "Réviser" pour un devoir', async () => {
      const items: FocusItem[] = [
        { type: 'assignment', id: 30, title: 'Devoir de maths', count: 0, is_late: false, last_session_ago_days: null, due_date: '2026-09-01' },
      ]
      api.get.mockImplementation(
        makeApiGetMock({ focusToday: () => Promise.resolve({ data: { ...DEFAULT_FOCUS_TODAY, items } }) }),
      )
      const { wrapper, router } = await mountAccueil()
      const rows = wrapper.findAllComponents(ListRow)
      await rows[0].findComponent(BaseButton).trigger('click')
      await flushPromises()
      expect(router.currentRoute.value.fullPath).toBe('/bibliotheque/30')
    })

    it('affiche l\'état vide "Tout est à jour !" quand il n\'y a aucun item à réviser', async () => {
      api.get.mockImplementation(
        makeApiGetMock({
          focusToday: () => Promise.resolve({ data: { ...DEFAULT_FOCUS_TODAY, total_due: 0, late_count: 0, items: [] } }),
        }),
      )
      const { wrapper } = await mountAccueil()
      const empty = wrapper.findComponent(BaseEmptyState)
      expect(empty.exists()).toBe(true)
      expect(empty.props('title')).toBe('Tout est à jour !')
      expect(empty.props('description')).toBe('Aucune révision en attente. Profitez-en pour explorer de nouveaux cours.')
    })
  })

  // ── Compteurs "Aujourd'hui" ───────────────────────────────────────────
  describe('carte "Aujourd\'hui"', () => {
    it('affiche les 5 compteurs avec les valeurs du store focus', async () => {
      const { wrapper } = await mountAccueil()
      const rows = wrapper.findAll('.bg-surface-soft.rounded-xl.px-3.py-2')
      const values = rows.map((r) => ({ label: r.findAll('span')[0].text(), value: r.findAll('span')[1].text() }))
      expect(values).toEqual([
        { label: 'À réviser', value: '2' },
        { label: 'En retard', value: '1' },
        { label: 'Flashcards', value: '1' },
        { label: 'Feuilles blanches', value: '1' },
        { label: 'Devoirs', value: '0' },
      ])
    })
  })

  // ── Charge à venir (14j) ──────────────────────────────────────────────
  describe('carte "Charge à venir (14j)"', () => {
    it('affiche une barre par jour de prévision (14 jours)', async () => {
      const { wrapper } = await mountAccueil()
      const bars = wrapper.findAll('.group.cursor-pointer.relative')
      expect(bars).toHaveLength(14)
    })

    it('expose le nombre de sessions du jour dans l\'info-bulle (visible au survol)', async () => {
      const { wrapper } = await mountAccueil()
      const bars = wrapper.findAll('.group.cursor-pointer.relative')
      expect(bars[2].text()).toContain(String(DEFAULT_FORECAST[2].count))
    })

    it('affiche la légende Bas / Moyen / Fort', async () => {
      const { wrapper } = await mountAccueil()
      expect(wrapper.text()).toContain('Bas')
      expect(wrapper.text()).toContain('Moyen')
      expect(wrapper.text()).toContain('Fort')
    })
  })

  // ── Ligne de StatCard ─────────────────────────────────────────────────
  describe('ligne de progression (StatCard)', () => {
    it('affiche les 4 StatCard avec les libellés et valeurs calculées', async () => {
      const { wrapper } = await mountAccueil()
      const stats = wrapper.findAllComponents(StatCard)
      expect(stats.map((s) => s.props('label'))).toEqual([
        'Cartes révisées',
        'Taux de réussite',
        "Temps d'étude",
        'Decks actifs',
      ])
      // 90/120 = 75% ; 5400s = 1h 30m ; 2 decks actifs.
      expect(stats.map((s) => s.props('value'))).toEqual(['120', '75%', '1h 30m', '2'])
    })
  })

  // ── Heatmap ───────────────────────────────────────────────────────────
  describe('carte "Activité d\'étude" (heatmap)', () => {
    it('affiche une grille de 364 cellules (7×52) et le total de sessions', async () => {
      api.get.mockImplementation(
        makeApiGetMock({
          heatmap: () => Promise.resolve({ data: [{ date: '2026-01-01', duration: 60, count: 2 }] }),
        }),
      )
      const { wrapper } = await mountAccueil()
      const cells = wrapper.findAll('[title]')
      expect(cells).toHaveLength(364)
      expect(wrapper.text()).toContain('Total : 2 sessions')
    })

    it('colore les cellules selon l\'intensité (nombre de sessions du jour)', async () => {
      const today = new Date()
      const fiveDaysAgo = new Date(today)
      fiveDaysAgo.setDate(today.getDate() - 5)
      const fmt = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

      api.get.mockImplementation(
        makeApiGetMock({
          heatmap: () =>
            Promise.resolve({
              data: [
                { date: fmt(today), duration: 300, count: 1 },
                { date: fmt(fiveDaysAgo), duration: 1200, count: 4 },
              ],
            }),
        }),
      )
      const { wrapper } = await mountAccueil()
      const cells = wrapper.findAll('[title]')
      const lowCells = cells.filter((c) => c.classes().includes('bg-primary/30'))
      const highCells = cells.filter((c) => c.classes().includes('bg-primary'))
      expect(lowCells).toHaveLength(1)
      expect(highCells).toHaveLength(1)
    })

    it('affiche la légende Moins → Plus', async () => {
      const { wrapper } = await mountAccueil()
      expect(wrapper.text()).toContain('Moins')
      expect(wrapper.text()).toContain('Plus')
    })
  })

  // ── Objectif hebdomadaire ─────────────────────────────────────────────
  describe('carte "Objectif Hebdomadaire"', () => {
    it('affiche la progression et le temps restant tant que l\'objectif n\'est pas atteint', async () => {
      api.get.mockImplementation(
        makeApiGetMock({
          sessions: () => Promise.resolve({ data: [{ duration_seconds: 3600 }, { duration_seconds: 3600 }] }),
        }),
      )
      const { wrapper } = await mountAccueil()
      expect(wrapper.text()).toContain('2.0h / 5h')
      expect(wrapper.text()).toContain('Plus que 3.0h pour atteindre votre objectif.')
      const bar = wrapper.get('.bg-primary.h-full.rounded-full')
      expect(bar.element.style.width).toBe('40%')
    })

    it('affiche le message d\'objectif atteint quand le temps hebdo dépasse la cible', async () => {
      api.get.mockImplementation(
        makeApiGetMock({
          sessions: () => Promise.resolve({ data: [{ duration_seconds: 20000 }] }),
        }),
      )
      const { wrapper } = await mountAccueil()
      expect(wrapper.text()).toContain('Objectif atteint pour cette semaine ! 🎉')
    })
  })

  // ── Rétention par matière ─────────────────────────────────────────────
  describe('carte "Rétention par matière"', () => {
    it('affiche une ligne par classeur avec nom, pourcentage et tendance', async () => {
      const { wrapper } = await mountAccueil()
      expect(wrapper.text()).toContain('Mathématiques')
      expect(wrapper.text()).toContain('82%')
      expect(wrapper.text()).toContain('▲ 4%')
      expect(wrapper.text()).toContain('Chimie')
      expect(wrapper.text()).toContain('45%')
      expect(wrapper.text()).toContain('▼ 3%')
    })

    it('masque la tendance quand trend_7d vaut 0', async () => {
      const retention: RetentionSubject[] = [
        { binder_id: 'b1', binder_name: 'Physique', retention_pct: 60, overdue_count: 0, trend_7d: 0 },
      ]
      api.get.mockImplementation(
        makeApiGetMock({ focusRetention: () => Promise.resolve({ data: { by_subject: retention } }) }),
      )
      const { wrapper } = await mountAccueil()
      expect(wrapper.text()).not.toContain('▲')
      expect(wrapper.text()).not.toContain('▼')
    })

    it('affiche "Aucun classeur créé." quand la liste de rétention est vide', async () => {
      api.get.mockImplementation(
        makeApiGetMock({ focusRetention: () => Promise.resolve({ data: { by_subject: [] } }) }),
      )
      const { wrapper } = await mountAccueil()
      expect(wrapper.text()).toContain('Aucun classeur créé.')
    })
  })

  // ── État chargement ───────────────────────────────────────────────────
  describe('état chargement', () => {
    it('affiche le spinner et masque le contenu tant que les données ne sont pas chargées', async () => {
      let resolveOverview!: (v: unknown) => void
      const pending = new Promise((resolve) => { resolveOverview = resolve })
      api.get.mockImplementation(
        makeApiGetMock({ overview: () => pending as Promise<unknown> }),
      )
      const { wrapper } = await mountAccueil({ flush: false })
      expect(wrapper.text()).toContain('Chargement de votre accueil...')
      expect(wrapper.text()).not.toContain('À réviser maintenant')

      resolveOverview({ data: DEFAULT_OVERVIEW })
      await flushPromises()
      expect(wrapper.text()).not.toContain('Chargement de votre accueil...')
      expect(wrapper.text()).toContain('À réviser maintenant')
    })
  })

  // ── État erreur ───────────────────────────────────────────────────────
  describe('état erreur', () => {
    it('remplace tout le contenu par un état d\'erreur quand le chargement échoue', async () => {
      api.get.mockImplementation(
        makeApiGetMock({ decks: () => Promise.reject(new Error('network down')) }),
      )
      const { wrapper } = await mountAccueil()
      const empty = wrapper.findComponent(BaseEmptyState)
      expect(empty.exists()).toBe(true)
      expect(empty.props('title')).toBe('Le chargement a échoué')
      expect(empty.props('description')).toBe(
        'Vos données n\'ont pas pu être récupérées. Vérifiez votre connexion et réessayez.',
      )
      expect(wrapper.text()).not.toContain('À réviser maintenant')
      expect(wrapper.text()).not.toContain('Chargement de votre accueil...')
    })

    it('masque le bouton d\'action de l\'en-tête pendant l\'état d\'erreur', async () => {
      api.get.mockImplementation(
        makeApiGetMock({ decks: () => Promise.reject(new Error('network down')) }),
      )
      const { wrapper } = await mountAccueil()
      const headerActionButton = wrapper
        .findAllComponents(BaseButton)
        .find((b) => b.text().includes('Continuer à réviser') || b.text().trim() === 'Tout est à jour')
      expect(headerActionButton).toBeUndefined()
    })

    it('le bouton "Réessayer" relance le chargement et affiche le contenu normal en cas de succès', async () => {
      api.get.mockImplementation(
        makeApiGetMock({ decks: () => Promise.reject(new Error('network down')) }),
      )
      const { wrapper } = await mountAccueil()
      expect(wrapper.findComponent(BaseEmptyState).props('title')).toBe('Le chargement a échoué')

      api.get.mockImplementation(makeApiGetMock())
      const retryButton = wrapper.findComponent(BaseEmptyState).findComponent(BaseButton)
      await retryButton.trigger('click')
      await flushPromises()

      expect(wrapper.text()).not.toContain('Le chargement a échoué')
      expect(wrapper.text()).toContain('À réviser maintenant')
    })

    it('réaffiche le spinner de chargement pendant la nouvelle tentative déclenchée par "Réessayer"', async () => {
      api.get.mockImplementation(
        makeApiGetMock({ decks: () => Promise.reject(new Error('network down')) }),
      )
      const { wrapper } = await mountAccueil()

      let resolveDecks!: (v: unknown) => void
      const pending = new Promise((resolve) => { resolveDecks = resolve })
      api.get.mockImplementation(makeApiGetMock({ decks: () => pending as Promise<unknown> }))

      const retryButton = wrapper.findComponent(BaseEmptyState).findComponent(BaseButton)
      await retryButton.trigger('click')
      expect(wrapper.text()).toContain('Chargement de votre accueil...')

      resolveDecks({ data: { data: DEFAULT_DECKS } })
      await flushPromises()
      expect(wrapper.text()).not.toContain('Chargement de votre accueil...')
    })
  })

  // ── État hors ligne ───────────────────────────────────────────────────
  describe('état hors ligne', () => {
    it('un échec réseau global au montage retombe sur le même état d\'erreur (pas de traitement spécifique)', async () => {
      api.get.mockImplementation(() => Promise.reject(new Error('Network Error')))
      const { wrapper } = await mountAccueil()
      const empty = wrapper.findComponent(BaseEmptyState)
      expect(empty.props('title')).toBe('Le chargement a échoué')
    })
  })

  // ── État dense ────────────────────────────────────────────────────────
  describe('état dense', () => {
    it('affiche tous les items de révision sans en perdre quand la file est longue', async () => {
      const items: FocusItem[] = Array.from({ length: 30 }, (_, i) => ({
        type: 'deck',
        id: i,
        title: `Deck ${i}`,
        count: 1,
        is_late: false,
        last_session_ago_days: null,
      }))
      api.get.mockImplementation(
        makeApiGetMock({ focusToday: () => Promise.resolve({ data: { ...DEFAULT_FOCUS_TODAY, items } }) }),
      )
      const { wrapper } = await mountAccueil()
      expect(wrapper.findAllComponents(ListRow)).toHaveLength(30)
    })

    it('tronque les noms de classeurs longs et garde le défilement horizontal de la heatmap', async () => {
      const retention: RetentionSubject[] = Array.from({ length: 20 }, (_, i) => ({
        binder_id: `b${i}`,
        binder_name: `Classeur avec un nom particulièrement long numéro ${i}`,
        retention_pct: 50,
        overdue_count: 0,
        trend_7d: 1,
      }))
      api.get.mockImplementation(
        makeApiGetMock({ focusRetention: () => Promise.resolve({ data: { by_subject: retention } }) }),
      )
      const { wrapper } = await mountAccueil()
      const names = wrapper.findAll('span.font-bold.text-ink.truncate')
      expect(names).toHaveLength(20)
      names.forEach((n) => expect(n.classes()).toContain('truncate'))
      expect(wrapper.find('.overflow-x-auto').exists()).toBe(true)
    })
  })
})
