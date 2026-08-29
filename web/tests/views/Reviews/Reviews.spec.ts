// Suite TDD — Reviews.vue reconstruit en flux unifie des elements dus
// (maquette Direction A « Reviser » : bandeau resume + En retard / Aujourd'hui / A venir).
// Les anciens onglets (Classiques / IA) et la section de gestion des decks
// ont ete supprimes : ils sont couverts par la Bibliotheque, Decks.vue et
// les ecrans dedies (NoteFeynman.vue, Blurting.vue).
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import Reviews from '../../../src/views/Reviews/Reviews.vue'

// ─── Fixtures ───────────────────────────────────────────────────────────────

const QCM_SET = {
  id: 1,
  name: 'Grands arrets du Conseil constitutionnel',
  description: null,
  type: 'qcm',
  binder_id: null,
  tuning_default: 1,
  is_public: false,
  item_count: 12,
  read_only: false,
}
const MIXED_SET = {
  id: 2,
  name: 'Ensemble mixte',
  description: null,
  type: null,
  binder_id: null,
  tuning_default: 1,
  is_public: false,
  item_count: 5,
  read_only: false,
}

const LATE_DECK = {
  type: 'deck',
  id: '10',
  title: 'Vocabulaire espagnol B2',
  count: 6,
  is_late: true,
  last_session_ago_days: 4,
}
const TODAY_DECK = {
  type: 'deck',
  id: '11',
  title: 'Chimie organique Ch4',
  count: 14,
  is_late: false,
  last_session_ago_days: 3,
}
const TODAY_QCM_SET = {
  type: 'revision_set',
  id: '1',
  title: 'Grands arrets du Conseil constitutionnel',
  count: 12,
  is_late: false,
  last_session_ago_days: null,
}
const TODAY_MIXED_SET = {
  type: 'revision_set',
  id: '2',
  title: 'Ensemble mixte',
  count: 5,
  is_late: false,
  last_session_ago_days: null,
}
// Ensemble absent de revisionStore.sets (ex. partage/hors page) : le rendu doit
// rester correct et la navigation retomber sur /study (jamais /run par defaut).
const TODAY_UNKNOWN_SET = {
  type: 'revision_set',
  id: '99',
  title: 'Ensemble inconnu',
  count: 3,
  is_late: false,
  last_session_ago_days: null,
}
const TODAY_NOTE = {
  type: 'note',
  id: 'n1',
  title: 'Anatomie systeme nerveux central',
  count: 1,
  is_late: false,
  last_session_ago_days: 1,
}

const DEFAULT_ITEMS = [
  LATE_DECK,
  TODAY_DECK,
  TODAY_QCM_SET,
  TODAY_MIXED_SET,
  TODAY_UNKNOWN_SET,
  TODAY_NOTE,
]

/** Date locale ISO (YYYY-MM-DD) decalee de `offset` jours — meme convention que la vue. */
function localIso(offset: number): string {
  const d = new Date()
  d.setHours(0, 0, 0, 0)
  d.setDate(d.getDate() + offset)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const DEFAULT_FORECAST = [
  { date: localIso(0), count: 23, load_level: 'medium' },
  { date: localIso(1), count: 21, load_level: 'medium' },
  { date: localIso(2), count: 0, load_level: 'low' },
  { date: localIso(3), count: 8, load_level: 'low' },
]

const stub = { template: '<div />' }
function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/reviser', name: 'Reviser', component: stub },
      { path: '/decks/:id/study', name: 'DeckStudy', component: stub },
      { path: '/notes/:id/blurting', name: 'Blurting', component: stub },
      { path: '/revision/sets/:id/study', name: 'RevisionStudy', component: stub },
      { path: '/revision/sets/:id/run', name: 'QcmRun', component: stub },
      { path: '/bibliotheque/:id', name: 'BinderDetail', component: stub },
      { path: '/exam/setup', name: 'ExamSetup', component: stub },
    ],
  })
}

interface MountOverrides {
  items?: Record<string, unknown>[]
  forecast?: Record<string, unknown>[]
  sets?: Record<string, unknown>[]
  lateCount?: number
}

async function mountReviews(overrides: MountOverrides = {}) {
  const items = overrides.items ?? DEFAULT_ITEMS
  const forecast = overrides.forecast ?? DEFAULT_FORECAST
  const sets = overrides.sets ?? [QCM_SET, MIXED_SET]
  const lateItems = items.filter((i) => i.is_late)

  const pinia = createPinia()
  setActivePinia(pinia)
  api.get.mockImplementation((url: string) => {
    if (/^\/revision\/sets\?/.test(url)) return Promise.resolve({ data: { data: sets } })
    if (/^\/focus\/today/.test(url)) {
      return Promise.resolve({
        data: {
          total_due: items.reduce((acc, i) => acc + (i.count as number), 0),
          late_count: overrides.lateCount ?? lateItems.reduce((a, i) => a + (i.count as number), 0),
          flashcard_count: items
            .filter((i) => i.type === 'deck')
            .reduce((a, i) => a + (i.count as number), 0),
          blurting_count: items.filter((i) => i.type === 'note').length,
          assignment_count: 0,
          items,
        },
      })
    }
    if (/^\/focus\/forecast/.test(url)) return Promise.resolve({ data: { forecast } })
    if (/^\/focus\/retention/.test(url)) return Promise.resolve({ data: { by_subject: [] } })
    return Promise.reject(new Error(`URL non mockee: ${url}`))
  })

  const router = createTestRouter()
  await router.push('/reviser')
  await router.isReady()
  const wrapper = mount(Reviews, { global: { plugins: [pinia, router] } })
  await flushPromises()
  return { wrapper, router }
}

// ─── Tests ──────────────────────────────────────────────────────────────────

describe('Reviews — flux unifie des elements dus', () => {
  beforeEach(() => vi.clearAllMocks())

  it('repartit les elements dus entre « En retard » et « Aujourd\'hui »', async () => {
    const { wrapper } = await mountReviews()

    const late = wrapper.get('[data-test="section-late"]')
    expect(late.text()).toContain('Vocabulaire espagnol B2')
    expect(late.text()).not.toContain('Chimie organique Ch4')

    const today = wrapper.get('[data-test="section-today"]')
    expect(today.text()).toContain('Chimie organique Ch4')
    expect(today.text()).toContain('Grands arrets du Conseil constitutionnel')
    expect(today.text()).toContain('Ensemble mixte')
    expect(today.text()).toContain('Anatomie systeme nerveux central')
    expect(today.text()).not.toContain('Vocabulaire espagnol B2')
  })

  it('affiche un badge de type par source (deck, serie typee, serie mixte, feuille blanche)', async () => {
    const { wrapper } = await mountReviews()

    expect(wrapper.get('[data-test="badge-deck-10"]').text()).toBe('Deck')
    expect(wrapper.get('[data-test="badge-revision_set-1"]').text()).toBe('Série QCM')
    expect(wrapper.get('[data-test="badge-revision_set-2"]').text()).toBe('Série mixte')
    expect(wrapper.get('[data-test="badge-revision_set-99"]').text()).toBe('Série')
    expect(wrapper.get('[data-test="badge-note-n1"]').text()).toBe('Feuille blanche')
  })

  it('le bouton Reviser d\'un deck ouvre la revision du deck', async () => {
    const { wrapper, router } = await mountReviews()
    await wrapper.get('[data-test="review-deck-11"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/decks/11/study')
  })

  it('le bouton Reviser d\'un ensemble QCM homogene navigue vers /run', async () => {
    const { wrapper, router } = await mountReviews()
    await wrapper.get('[data-test="review-revision_set-1"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/revision/sets/1/run')
  })

  it('le bouton Reviser d\'un ensemble heterogene navigue vers /study', async () => {
    const { wrapper, router } = await mountReviews()
    await wrapper.get('[data-test="review-revision_set-2"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/revision/sets/2/study')
  })

  it('un ensemble absent du store retombe sur /study (jamais /run par defaut)', async () => {
    const { wrapper, router } = await mountReviews()
    await wrapper.get('[data-test="review-revision_set-99"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/revision/sets/99/study')
  })

  it('le bouton Reviser d\'une note ouvre la feuille blanche', async () => {
    const { wrapper, router } = await mountReviews()
    await wrapper.get('[data-test="review-note-n1"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/notes/n1/blurting')
  })

  it('« Tout reviser » lance la file unifiee sur le premier element en retard', async () => {
    const { wrapper, router } = await mountReviews()
    await wrapper.get('[data-test="review-all"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/decks/10/study')
  })

  it('la section « A venir » liste les jours a charge non nulle, sans bouton Reviser', async () => {
    const { wrapper } = await mountReviews()

    const upcoming = wrapper.get('[data-test="section-upcoming"]')
    expect(upcoming.text()).toContain('DEMAIN')
    expect(upcoming.text()).toContain('21')
    expect(upcoming.text()).toContain('3 JOURS')
    expect(upcoming.text()).toContain('8')
    // Le jour meme n'est pas « a venir », et un jour a charge nulle n'est pas liste.
    expect(upcoming.findAll('[data-test^="upcoming-row-"]')).toHaveLength(2)
    expect(upcoming.findAll('button')).toHaveLength(0)
  })

  it('masque « En retard » et « A venir » quand il n\'y a rien a y mettre', async () => {
    const { wrapper } = await mountReviews({
      items: [TODAY_DECK],
      forecast: [{ date: localIso(0), count: 4, load_level: 'low' }],
      lateCount: 0,
    })
    expect(wrapper.find('[data-test="section-late"]').exists()).toBe(false)
    expect(wrapper.find('[data-test="section-upcoming"]').exists()).toBe(false)
    expect(wrapper.find('[data-test="section-today"]').exists()).toBe(true)
  })

  it('affiche un etat vide quand plus rien n\'est du', async () => {
    const { wrapper } = await mountReviews({ items: [], forecast: [], lateCount: 0 })
    expect(wrapper.text()).toContain('Tout est à jour')
    expect(wrapper.findAll('[data-test^="due-row-"]')).toHaveLength(0)
  })

  it('les onglets, les outils IA et la gestion des decks ont disparu de l\'écran', async () => {
    const { wrapper } = await mountReviews()
    const text = wrapper.text()

    // Libellés exacts de l'ancien hub à onglets (supprimés par ce chantier).
    expect(text).not.toContain('Méthode Feynman')
    expect(text).not.toContain("Feuille d'évaluation IA")
    expect(text).not.toContain('Générateur de Quiz Interactif')
    expect(text).not.toContain('Decks de Répétition Espacée')
    expect(text).not.toContain('Générer depuis Notes / Classeurs')
    expect(text).not.toContain('Nouvelle carte')
    expect(text).not.toContain('Classiques')
    expect(wrapper.findAll('[data-test^="tab-"]')).toHaveLength(0)
    expect(wrapper.findAll('[data-test^="manage-set-"]')).toHaveLength(0)
  })
})
