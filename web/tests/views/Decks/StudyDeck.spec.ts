// Suite TDD écran 3 (Session de révision flashcards) — voir ETAT.md
// « Écran 3 — Session de révision flashcards » pour l'inventaire complet et le
// comportement attendu état par état (skill migration-ecran).
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router, type RouteLocationRaw } from 'vue-router'

const api = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}))
vi.mock('../../../src/services/api', () => ({ default: api }))

import StudyDeck from '../../../src/views/Decks/StudyDeck.vue'
import { BaseButton, BaseEmptyState, BaseToast } from '../../../src/components/ui/base'
import { useDecksStore } from '../../../src/stores/decks'
import type { Deck, Flashcard } from '../../../src/stores/decks'
import { useFocusStore } from '../../../src/stores/focus'
import { usePlanningStore } from '../../../src/stores/planning'
import { useRevisionStore } from '../../../src/stores/revision'

// ─── Fixtures par défaut ─────────────────────────────────────────────────────

const DECK: Deck = {
  id: 1,
  binder_id: 'b1',
  name: 'Chimie organique',
  description: '',
  reversed: false,
  tuning_default: 1,
  card_count: 2,
  created_at: '2026-01-01T00:00:00Z',
  tags: [],
}

function makeCard(id: number, deckId: number, overrides: Partial<Flashcard> = {}): Flashcard {
  return {
    id,
    deck_id: deckId,
    front: `Recto ${id}`,
    back: `Verso ${id}`,
    tuning: 1,
    reverse_of_id: null,
    interval: 1,
    ease_factor: 2.5,
    repetitions: 0,
    next_review: '2026-08-25T00:00:00Z',
    ...overrides,
  }
}

const CARD_A = makeCard(100, 1, {
  front: "Quel est le groupe fonctionnel caractéristique d'un acide carboxylique ?",
  back: 'Le groupe carboxyle -COOH.',
})
const CARD_B = makeCard(101, 1, { front: 'Autre question', back: 'Autre réponse' })

interface ApiOverrides {
  deck?: () => Promise<unknown>
  studyCards?: () => Promise<unknown>
  binderStudy?: () => Promise<unknown>
  answer?: () => Promise<unknown>
  revisionSets?: () => Promise<unknown>
}

function makeGetImpl(over: ApiOverrides = {}) {
  return (url: string) => {
    if (/^\/decks\/\d+\/study$/.test(url)) {
      return (over.studyCards ?? (() => Promise.resolve({ data: [CARD_A, CARD_B] })))()
    }
    if (/^\/decks\/\d+$/.test(url)) {
      return (over.deck ?? (() => Promise.resolve({ data: DECK })))()
    }
    if (/^\/binders\/.+\/study$/.test(url)) {
      return (over.binderStudy ?? (() => Promise.resolve({ data: [CARD_A, CARD_B] })))()
    }
    if (/^\/revision\/sets\?/.test(url)) {
      return (over.revisionSets ?? (() => Promise.resolve({ data: { data: [] } })))()
    }
    return Promise.reject(new Error(`URL GET non mockée dans le test: ${url}`))
  }
}

function makePostImpl(over: ApiOverrides = {}) {
  return (url: string, body: unknown) => {
    if (/^\/decks\/\d+\/study\/answer\/\d+$/.test(url)) {
      return (over.answer ?? (() => Promise.resolve({ data: { ...CARD_A, ...(body as object) } })))()
    }
    return Promise.reject(new Error(`URL POST non mockée dans le test: ${url}`))
  }
}

function wait(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

// Après un clic de notation réussi, la progression a lieu dans un setTimeout(350ms).
async function settleRating() {
  await flushPromises()
  await wait(360)
  await flushPromises()
}

function backButton(wrapper: ReturnType<typeof mount>) {
  return wrapper.findAll('button').find((b) => b.text().startsWith('Retour'))!
}

function ratingButton(wrapper: ReturnType<typeof mount>, label: string) {
  return wrapper.findAll('button').find((b) => b.text().includes(label))!
}

const stub = { template: '<div />' }

function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/decks', name: 'Decks', component: stub },
      { path: '/decks/:id/study', name: 'StudyDeck', component: stub },
      { path: '/bibliotheque/:id?', name: 'Bibliotheque', component: stub },
      { path: '/bibliotheque/:id/reviser', name: 'StudyBinder', component: stub },
      { path: '/planning', name: 'Planning', component: stub },
      { path: '/focus', name: 'Focus', component: stub },
      { path: '/revision/sets/:id/study', name: 'RevisionStudy', component: stub },
      { path: '/revision/sets/:id/run', name: 'QcmRun', component: stub },
    ],
  })
}

async function mountStudyDeck(
  opts: {
    to?: RouteLocationRaw
    flush?: boolean
    setup?: (stores: {
      decksStore: ReturnType<typeof useDecksStore>
      focusStore: ReturnType<typeof useFocusStore>
      planningStore: ReturnType<typeof usePlanningStore>
      revisionStore: ReturnType<typeof useRevisionStore>
    }) => void
  } = {},
) {
  const { to = '/decks/1/study', flush = true, setup } = opts

  const pinia = createPinia()
  setActivePinia(pinia)
  const decksStore = useDecksStore()
  const focusStore = useFocusStore()
  const planningStore = usePlanningStore()
  const revisionStore = useRevisionStore()
  setup?.({ decksStore, focusStore, planningStore, revisionStore })

  const router = createTestRouter()
  await router.push(to)
  await router.isReady()

  const wrapper = mount(StudyDeck, {
    global: { plugins: [pinia, router] },
  })

  if (flush) await flushPromises()

  return { wrapper, router, decksStore, focusStore, planningStore, revisionStore }
}

describe('StudyDeck', () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.get.mockImplementation(makeGetImpl())
    api.post.mockImplementation(makePostImpl())
  })

  // ── 4 modes d'entrée ──────────────────────────────────────────────────
  describe('mode deck simple (/decks/:id/study)', () => {
    it('charge le deck et les cartes dues via decksStore', async () => {
      const { wrapper } = await mountStudyDeck({ to: '/decks/1/study' })
      expect(api.get).toHaveBeenCalledWith('/decks/1')
      expect(api.get).toHaveBeenCalledWith('/decks/1/study')
      expect(wrapper.text()).toContain('Chimie organique')
    })

    it('le bouton retour navigue vers /decks', async () => {
      const { wrapper, router } = await mountStudyDeck({ to: '/decks/1/study' })
      await backButton(wrapper).trigger('click')
      await flushPromises()
      expect(router.currentRoute.value.fullPath).toBe('/decks')
    })
  })

  describe('mode dossier (StudyBinder, bibliotheque/:id/reviser)', () => {
    it('charge les cartes agrégées via GET /binders/:id/study et affiche le nom depuis la query', async () => {
      const { wrapper } = await mountStudyDeck({
        to: { path: '/bibliotheque/binder-1/reviser', query: { name: 'Classeur Chimie' } },
      })
      expect(api.get).toHaveBeenCalledWith('/binders/binder-1/study')
      expect(wrapper.text()).toContain('Classeur Chimie')
    })

    it('le bouton retour navigue vers /bibliotheque/:id', async () => {
      const { wrapper, router } = await mountStudyDeck({
        to: { path: '/bibliotheque/binder-1/reviser', query: { name: 'Classeur Chimie' } },
      })
      await backButton(wrapper).trigger('click')
      await flushPromises()
      expect(router.currentRoute.value.fullPath).toBe('/bibliotheque/binder-1')
    })
  })

  describe('mode focus (?focus=true)', () => {
    it('charge les cartes du deck comme en mode simple', async () => {
      const { wrapper } = await mountStudyDeck({ to: '/decks/1/study?focus=true' })
      expect(api.get).toHaveBeenCalledWith('/decks/1')
      expect(api.get).toHaveBeenCalledWith('/decks/1/study')
      expect(wrapper.text()).toContain('Retour au Focus')
    })

    it('le bouton retour navigue vers /focus', async () => {
      const { wrapper, router } = await mountStudyDeck({ to: '/decks/1/study?focus=true' })
      await backButton(wrapper).trigger('click')
      await flushPromises()
      expect(router.currentRoute.value.fullPath).toBe('/focus')
    })
  })

  describe('mode révision anticipée (?advance=true)', () => {
    it('charge les cartes depuis planningStore.advanceReviewCards, sans appeler /decks/:id/study', async () => {
      const { wrapper } = await mountStudyDeck({
        to: '/decks/1/study?advance=true',
        setup: ({ planningStore }) => {
          planningStore.advanceReviewCards = [CARD_A, CARD_B]
        },
      })
      expect(api.get).toHaveBeenCalledWith('/decks/1')
      expect(api.get).not.toHaveBeenCalledWith('/decks/1/study')
      expect(wrapper.text()).toContain(CARD_A.front)
    })

    it('le bouton retour navigue vers /planning', async () => {
      const { wrapper, router } = await mountStudyDeck({
        to: '/decks/1/study?advance=true',
        setup: ({ planningStore }) => {
          planningStore.advanceReviewCards = [CARD_A]
        },
      })
      await backButton(wrapper).trigger('click')
      await flushPromises()
      expect(router.currentRoute.value.fullPath).toBe('/planning')
    })
  })

  // ── Carte recto/verso ─────────────────────────────────────────────────
  describe('carte recto/verso', () => {
    it('affiche le recto par défaut avec le libellé "Recto" et l\'indice', async () => {
      const { wrapper } = await mountStudyDeck()
      expect(wrapper.text()).toContain('Recto')
      expect(wrapper.text()).toContain('Cliquer sur la fiche pour retourner')
      expect(wrapper.text()).toContain(CARD_A.front)
      // Les deux faces coexistent dans le DOM (effet 3D par transform CSS) : c'est
      // la classe de retournement, pas la présence du texte "Verso", qui distingue
      // l'état recto de l'état verso.
      expect(wrapper.get('[data-testid="flashcard"] > div').classes()).not.toContain('rotate-y-180')
    })

    it('retourne la carte au clic et applique la classe de retournement (verso visible)', async () => {
      const { wrapper } = await mountStudyDeck()
      await wrapper.get('[data-testid="flashcard"]').trigger('click')
      expect(wrapper.get('[data-testid="flashcard"] > div').classes()).toContain('rotate-y-180')
      expect(wrapper.text()).toContain('Verso')
      expect(wrapper.text()).toContain(CARD_A.back)
    })

    it('affiche les contrôles de notation seulement une fois la carte retournée', async () => {
      const { wrapper } = await mountStudyDeck()
      expect(wrapper.text()).not.toContain('Encore')
      await wrapper.get('[data-testid="flashcard"]').trigger('click')
      expect(wrapper.text()).toContain('Encore')
      expect(wrapper.text()).toContain('Difficile')
      expect(wrapper.text()).toContain('Bien')
      expect(wrapper.text()).toContain('Facile')
    })
  })

  // ── Barre de progression ──────────────────────────────────────────────
  describe('barre de progression', () => {
    it('affiche "Carte 1 sur 2" et "0% complété"', async () => {
      const { wrapper } = await mountStudyDeck()
      expect(wrapper.text()).toContain('Carte 1 sur 2')
      expect(wrapper.text()).toContain('0% complété')
    })
  })

  // ── Notation — mapping exact des 4 boutons ────────────────────────────
  describe('notation — mapping des 4 boutons', () => {
    it.each([
      ['Encore', 0],
      ['Difficile', 3],
      ['Bien', 4],
      ['Facile', 5],
    ] as const)('le bouton "%s" appelle decksStore.answerCard avec le score %i', async (label, score) => {
      const { wrapper, decksStore } = await mountStudyDeck()
      const spy = vi.spyOn(decksStore, 'answerCard')
      await wrapper.get('[data-testid="flashcard"]').trigger('click')
      await ratingButton(wrapper, label).trigger('click')
      await flushPromises()
      expect(spy).toHaveBeenCalledWith(1, 100, score)
    })

    it('remet la carte en fin de file quand le score est < 3 (Encore)', async () => {
      const { wrapper } = await mountStudyDeck()
      await wrapper.get('[data-testid="flashcard"]').trigger('click')
      await ratingButton(wrapper, 'Encore').trigger('click')
      await settleRating()
      expect(wrapper.text()).toContain('Carte 2 sur 3')
      expect(wrapper.text()).toContain(CARD_B.front)
    })

    it('avance sans remettre la carte en file quand le score est >= 3 (Bien)', async () => {
      const { wrapper } = await mountStudyDeck()
      await wrapper.get('[data-testid="flashcard"]').trigger('click')
      await ratingButton(wrapper, 'Bien').trigger('click')
      await settleRating()
      expect(wrapper.text()).toContain('Carte 2 sur 2')
      expect(wrapper.text()).toContain(CARD_B.front)
    })
  })

  // ── Raccourci clavier 1-4 ──────────────────────────────────────────────
  describe('raccourci clavier 1-4', () => {
    it.each([
      ['1', 0],
      ['2', 3],
      ['3', 4],
      ['4', 5],
    ] as const)('la touche "%s" note avec le score %i quand la carte est retournée', async (key, score) => {
      const { wrapper, decksStore } = await mountStudyDeck()
      const spy = vi.spyOn(decksStore, 'answerCard')
      await wrapper.get('[data-testid="flashcard"]').trigger('click')
      window.dispatchEvent(new KeyboardEvent('keydown', { key }))
      await flushPromises()
      expect(spy).toHaveBeenCalledWith(1, 100, score)
    })

    it("n'a aucun effet tant que la carte n'est pas retournée", async () => {
      const { decksStore } = await mountStudyDeck()
      const spy = vi.spyOn(decksStore, 'answerCard')
      window.dispatchEvent(new KeyboardEvent('keydown', { key: '1' }))
      await flushPromises()
      expect(spy).not.toHaveBeenCalled()
    })

    it("retire l'écouteur clavier au démontage", async () => {
      const { wrapper } = await mountStudyDeck()
      const removeSpy = vi.spyOn(window, 'removeEventListener')
      wrapper.unmount()
      expect(removeSpy.mock.calls.map((c) => c[0])).toContain('keydown')
    })
  })

  // ── État vide vs état complet ─────────────────────────────────────────
  describe('état vide — jamais eu de carte', () => {
    it('affiche "Rien à réviser ici pour le moment." quand aucune carte n\'a jamais été due', async () => {
      api.get.mockImplementation(makeGetImpl({ studyCards: () => Promise.resolve({ data: [] }) }))
      const { wrapper } = await mountStudyDeck()
      const empty = wrapper.findComponent(BaseEmptyState)
      expect(empty.exists()).toBe(true)
      expect(empty.props('title')).toBe('Rien à réviser ici pour le moment.')
    })
  })

  describe('état complet — session terminée après révision', () => {
    it('affiche "Session terminée !" une fois toutes les cartes notées (distinct du cas jamais-eu-de-carte)', async () => {
      api.get.mockImplementation(
        makeGetImpl({ studyCards: () => Promise.resolve({ data: [CARD_A] }) }),
      )
      const { wrapper } = await mountStudyDeck()
      await wrapper.get('[data-testid="flashcard"]').trigger('click')
      await ratingButton(wrapper, 'Bien').trigger('click')
      await settleRating()
      const empty = wrapper.findComponent(BaseEmptyState)
      expect(empty.exists()).toBe(true)
      expect(empty.props('title')).toContain('Session terminée')
      expect(empty.props('title')).not.toBe('Rien à réviser ici pour le moment.')
    })
  })

  // ── État chargement ────────────────────────────────────────────────────
  describe('état chargement', () => {
    it('affiche le spinner pendant le chargement initial', async () => {
      let resolveStudy!: (v: unknown) => void
      const pending = new Promise((resolve) => {
        resolveStudy = resolve
      })
      api.get.mockImplementation(makeGetImpl({ studyCards: () => pending as Promise<unknown> }))
      const { wrapper } = await mountStudyDeck({ flush: false })
      expect(wrapper.text()).toContain('Préparation de la session')

      resolveStudy({ data: [CARD_A] })
      await flushPromises()
      expect(wrapper.text()).not.toContain('Préparation de la session')
    })
  })

  // ── État erreur — chargement initial ───────────────────────────────────
  describe('état erreur — chargement initial', () => {
    it('remplace le contenu par un BaseEmptyState + "Réessayer" quand le chargement échoue', async () => {
      api.get.mockImplementation(
        makeGetImpl({ studyCards: () => Promise.reject(new Error('network down')) }),
      )
      const { wrapper } = await mountStudyDeck()
      const empty = wrapper.findComponent(BaseEmptyState)
      expect(empty.exists()).toBe(true)
      expect(empty.props('title')).toBe('Le chargement a échoué')
      expect(wrapper.text()).not.toContain('Préparation de la session')
    })

    it('le bouton "Réessayer" relance loadSession et affiche la session en cas de succès', async () => {
      api.get.mockImplementation(
        makeGetImpl({ studyCards: () => Promise.reject(new Error('network down')) }),
      )
      const { wrapper } = await mountStudyDeck()
      expect(wrapper.findComponent(BaseEmptyState).props('title')).toBe('Le chargement a échoué')

      api.get.mockImplementation(makeGetImpl())
      const retryButton = wrapper.findComponent(BaseEmptyState).findComponent(BaseButton)
      await retryButton.trigger('click')
      await flushPromises()

      expect(wrapper.findComponent(BaseEmptyState).exists()).toBe(false)
      expect(wrapper.text()).toContain('Recto')
    })
  })

  // ── État erreur — notation en cours de session ─────────────────────────
  describe('état erreur — notation en cours de session', () => {
    it('affiche un BaseToast d\'erreur quand la notation échoue, la carte reste en place', async () => {
      api.post.mockImplementation(makePostImpl({ answer: () => Promise.reject(new Error('down')) }))
      const { wrapper } = await mountStudyDeck()
      await wrapper.get('[data-testid="flashcard"]').trigger('click')
      await ratingButton(wrapper, 'Bien').trigger('click')
      await flushPromises()

      const toast = wrapper.findComponent(BaseToast)
      expect(toast.exists()).toBe(true)
      expect(toast.props('variant')).toBe('danger')
      expect(toast.props('message')).toBe("La notation n'a pas été enregistrée. Réessayez.")
      // La carte reste retournée, les contrôles de notation restent affichés.
      expect(wrapper.text()).toContain('Verso')
      expect(wrapper.text()).toContain('Bien')
    })

    it("une nouvelle tentative réussie fait disparaître le toast d'erreur", async () => {
      api.post.mockImplementation(makePostImpl({ answer: () => Promise.reject(new Error('down')) }))
      const { wrapper } = await mountStudyDeck()
      await wrapper.get('[data-testid="flashcard"]').trigger('click')
      await ratingButton(wrapper, 'Bien').trigger('click')
      await flushPromises()
      expect(wrapper.findComponent(BaseToast).exists()).toBe(true)

      api.post.mockImplementation(makePostImpl())
      await ratingButton(wrapper, 'Bien').trigger('click')
      await settleRating()

      expect(wrapper.findComponent(BaseToast).exists()).toBe(false)
    })
  })

  // ── État dense ──────────────────────────────────────────────────────────
  describe('état dense', () => {
    it('affiche un texte recto/verso long entièrement, sans troncature', async () => {
      const longFront = 'Q'.repeat(400)
      const longBack = 'R'.repeat(400)
      api.get.mockImplementation(
        makeGetImpl({
          studyCards: () =>
            Promise.resolve({ data: [makeCard(200, 1, { front: longFront, back: longBack })] }),
        }),
      )
      const { wrapper } = await mountStudyDeck()
      expect(wrapper.text()).toContain(longFront)
      await wrapper.get('[data-testid="flashcard"]').trigger('click')
      expect(wrapper.text()).toContain(longBack)
    })
  })

  // ── 3 CTA de fin de session selon le mode ──────────────────────────────
  describe('CTA de fin de session selon le mode', () => {
    it('mode focus, file non vide : "Continuer les révisions" avance dans la file focus', async () => {
      api.get.mockImplementation(makeGetImpl({ studyCards: () => Promise.resolve({ data: [] }) }))
      const { wrapper, router } = await mountStudyDeck({
        to: '/decks/1/study?focus=true',
        setup: ({ focusStore }) => {
          focusStore.reviewQueue = [
            { type: 'deck', id: 5, title: 'Deck suivant', count: 3, is_late: false, last_session_ago_days: null },
          ]
        },
      })
      const cta = wrapper
        .findAllComponents(BaseButton)
        .find((b) => b.text().includes('Continuer les révisions'))!
      await cta.trigger('click')
      await flushPromises()
      expect(router.currentRoute.value.fullPath).toBe('/decks/5/study?focus=true')
    })

    it('mode focus, prochain item = ensemble QCM homogene : avance vers /revision/sets/:id/run', async () => {
      api.get.mockImplementation(
        makeGetImpl({
          studyCards: () => Promise.resolve({ data: [] }),
          revisionSets: () =>
            Promise.resolve({
              data: {
                data: [
                  {
                    id: 7,
                    name: 'Série QCM',
                    description: null,
                    type: 'qcm',
                    binder_id: null,
                    tuning_default: 1,
                    is_public: false,
                    item_count: 10,
                    read_only: false,
                  },
                ],
              },
            }),
        }),
      )
      const { wrapper, router } = await mountStudyDeck({
        to: '/decks/1/study?focus=true',
        setup: ({ focusStore }) => {
          focusStore.reviewQueue = [
            { type: 'revision_set', id: 7, title: 'Série QCM', count: 10, is_late: false, last_session_ago_days: null },
          ]
        },
      })
      const cta = wrapper
        .findAllComponents(BaseButton)
        .find((b) => b.text().includes('Continuer les révisions'))!
      await cta.trigger('click')
      await flushPromises()
      expect(router.currentRoute.value.fullPath).toBe('/revision/sets/7/run')
    })

    it('mode focus, prochain item = ensemble heterogene/inconnu : avance vers /revision/sets/:id/study', async () => {
      api.get.mockImplementation(makeGetImpl({ studyCards: () => Promise.resolve({ data: [] }) }))
      const { wrapper, router } = await mountStudyDeck({
        to: '/decks/1/study?focus=true',
        setup: ({ focusStore }) => {
          focusStore.reviewQueue = [
            { type: 'revision_set', id: 8, title: 'Série inconnue', count: 4, is_late: false, last_session_ago_days: null },
          ]
        },
      })
      const cta = wrapper
        .findAllComponents(BaseButton)
        .find((b) => b.text().includes('Continuer les révisions'))!
      await cta.trigger('click')
      await flushPromises()
      expect(router.currentRoute.value.fullPath).toBe('/revision/sets/8/study')
    })

    it('mode focus, file vide : "Retour au Focus"', async () => {
      api.get.mockImplementation(makeGetImpl({ studyCards: () => Promise.resolve({ data: [] }) }))
      const { wrapper, router } = await mountStudyDeck({ to: '/decks/1/study?focus=true' })
      const cta = wrapper.findAllComponents(BaseButton).find((b) => b.text().includes('Retour au Focus'))!
      await cta.trigger('click')
      await flushPromises()
      expect(router.currentRoute.value.fullPath).toBe('/focus')
    })

    it('mode révision anticipée : "Retour au Planning"', async () => {
      const { wrapper, router } = await mountStudyDeck({ to: '/decks/1/study?advance=true' })
      const cta = wrapper.findAllComponents(BaseButton).find((b) => b.text().includes('Retour au Planning'))!
      await cta.trigger('click')
      await flushPromises()
      expect(router.currentRoute.value.fullPath).toBe('/planning')
    })

    it('mode simple : "Retour à la liste"', async () => {
      api.get.mockImplementation(makeGetImpl({ studyCards: () => Promise.resolve({ data: [] }) }))
      const { wrapper, router } = await mountStudyDeck()
      const cta = wrapper.findAllComponents(BaseButton).find((b) => b.text().includes('Retour à la liste'))!
      await cta.trigger('click')
      await flushPromises()
      expect(router.currentRoute.value.fullPath).toBe('/decks')
    })
  })

  // ── Rechargement SPA au changement de deck/dossier ─────────────────────
  describe('rechargement SPA au changement de route.params.id', () => {
    it('recharge la session sans démonter le composant quand le deckId change', async () => {
      const { wrapper, router } = await mountStudyDeck({ to: '/decks/1/study' })
      expect(api.get).toHaveBeenCalledWith('/decks/1/study')

      api.get.mockClear()
      await router.push('/decks/2/study')
      await flushPromises()

      expect(api.get).toHaveBeenCalledWith('/decks/2')
      expect(api.get).toHaveBeenCalledWith('/decks/2/study')
      expect(wrapper.exists()).toBe(true)
    })
  })
})
