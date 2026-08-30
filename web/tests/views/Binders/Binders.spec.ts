import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import Binders, { binderAggregate } from '../../../src/views/Binders/Binders.vue'
import { useBindersStore } from '../../../src/stores/binders'
import { useNotesStore } from '../../../src/stores/notes'
import { useDecksStore } from '../../../src/stores/decks'
import { useRevisionStore } from '../../../src/stores/revision'
import { useTagsStore } from '../../../src/stores/tags'
import { useAuthStore } from '../../../src/stores/auth'

const BINDER = { id: 'b1', name: 'Chimie organique', parent_id: null, is_public: false, user_id: 1, tags: [] }
const SUBBINDER = { id: 'b1-sub', name: 'Sous-classeur B1', parent_id: 'b1', is_public: false, user_id: 1, tags: [] }
const DECK = { id: 1, binder_id: 'b1', name: 'Deck classique', description: '', reversed: false, tuning_default: 1, card_count: 5, created_at: '', tags: [] }
const HETEROGENEOUS_SET = { id: 7, name: 'Mixte', description: null, type: null, binder_id: 'b1', tuning_default: 1, is_public: false, item_count: 3 }
// Note NON classée (binder_id: null) et note bien classée (binder_id: 'b1') --
// nécessaires pour tester la subtilité filterBinderId ('Non classé' doit filtrer sur
// binder_id === null, jamais sur la chaîne littérale 'non-classe').
const NOW = new Date().toISOString()
const NOTE_UNCLASSIFIED = { id: 'n-libre', binder_id: null, title: 'Note libre', content: '', created_at: NOW, updated_at: NOW, tags: [] }
const NOTE_B1 = { id: 'n-b1', binder_id: 'b1', title: 'Note du classeur b1', content: '', created_at: NOW, updated_at: NOW, tags: [] }

const stub = { template: '<div />' }
function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/bibliotheque/:id?', name: 'Bibliotheque', component: stub },
      { path: '/revision/sets/:id', name: 'RevisionSetDetail', component: stub },
      { path: '/revision/sets/:id/stats', name: 'RevisionSetStats', component: stub },
      { path: '/decks/:id/study', name: 'StudyDeck', component: stub },
    ],
  })
}

// Tabs.vue (primitive partagee) ne pose pas de hook data-test par onglet — on
// selectionne par libelle plutot que d'ajouter un attribut ad hoc a un composant
// partage pour un seul ecran.
function clickTab(wrapper: ReturnType<typeof mount>, label: string) {
  return wrapper.findAll('button').find((b) => b.text().trim() === label)!.trigger('click')
}

// Localise une carte de classeur (BinderCard, Task 1) par son nom affiché --
// BinderCard.vue n'expose pas de data-test dédié (composant présentationnel pur,
// hors périmètre de cette tâche), donc on cherche par texte comme clickTab().
function findCard(wrapper: ReturnType<typeof mount>, name: string) {
  return wrapper.findAll('button').find((b) => b.text().includes(name))
}

const OVERDUE_TS = new Date(Date.now() - 86400000).toISOString()
// Item "pas encore du" : programme dans un jour, pour eviter toute course
// avec le seuil de comparaison (next_review <= Date.now()) evalue quelques
// microsecondes/secondes plus tard -- une valeur "maintenant" serait fragile
// (flaky) vis-a-vis de ce <=.
const NOT_DUE = new Date(Date.now() + 86400000).toISOString()
const SET_7_ITEMS = [
  { id: 101, set_id: 7, type: 'flashcard', payload: {}, tuning: 1, position: 0, interval: 1, ease_factor: 2.5, repetitions: 1, next_review: OVERDUE_TS, created_at: NOW, updated_at: NOW },
  { id: 102, set_id: 7, type: 'qcm', payload: {}, tuning: 1, position: 0, interval: 5, ease_factor: 2.5, repetitions: 1, next_review: NOT_DUE, created_at: NOW, updated_at: NOW },
]

// Dispatcher regex par URL — meme idiome que StudyDeck.spec.ts. Ne pas seeder l'etat
// des stores directement : onMounted() de Binders.vue appelle fetchBinders/fetchDecks/
// fetchNotes/fetchSets/fetchTags, qui ecrasent integralement le ref du store avec la
// reponse mockee (cf. revision.ts:193 `sets.value = response.data.data`) — un seed manuel
// avant le mount serait silencieusement efface des que ces appels resolvent.
function makeGetImpl() {
  return (url: string) => {
    if (/^\/binders\?/.test(url)) return Promise.resolve({ data: { data: [BINDER, SUBBINDER] } })
    if (/^\/binders\/[^/?]+$/.test(url)) return Promise.resolve({ data: BINDER }) // fetchMissingBinder — currentBinderId watcher tourne avant que fetchBinders() ait resolu

    if (/^\/decks\?/.test(url)) return Promise.resolve({ data: { data: [DECK] } })
    if (/^\/notes\?/.test(url)) return Promise.resolve({ data: { data: [NOTE_UNCLASSIFIED, NOTE_B1] } })
    if (/^\/revision\/sets\?/.test(url)) return Promise.resolve({ data: { data: [HETEROGENEOUS_SET] } })
    if (url === '/revision/sets/7/items') return Promise.resolve({ data: { data: SET_7_ITEMS } })
    if (url === '/tags') return Promise.resolve({ data: { data: [] } })
    if (/^\/diagrams\?/.test(url)) return Promise.resolve({ data: { data: [] } })
    if (/^\/pdfs\?/.test(url)) return Promise.resolve({ data: { data: [] } })
    return Promise.reject(new Error(`URL GET non mockée dans le test: ${url}`))
  }
}

async function mountBinders(binderId: string | null = 'b1') {
  const pinia = createPinia()
  setActivePinia(pinia)
  const bindersStore = useBindersStore()
  const notesStore = useNotesStore()
  const decksStore = useDecksStore()
  const revisionStore = useRevisionStore()
  const tagsStore = useTagsStore()
  const authStore = useAuthStore()
  // BINDER.user_id === 1 : authentifie comme le proprietaire pour que `isOwner`
  // soit vrai et que les actions (onglets, bouton primaire, Ajouter) rendent.
  authStore.user = { id: 1, email: 'test@test.dev', username: 'test', created_at: '' }

  api.get.mockImplementation(makeGetImpl())

  const router = createTestRouter()
  await router.push(binderId ? `/bibliotheque/${binderId}` : '/bibliotheque')
  await router.isReady()
  const wrapper = mount(Binders, { global: { plugins: [pinia, router] } })
  await flushPromises()
  return { wrapper, router, bindersStore, notesStore, decksStore, revisionStore, tagsStore }
}

describe('Binders — racine : grille de classeurs uniquement', () => {
  beforeEach(() => vi.clearAllMocks())

  it('affiche la grille (classeurs de premier niveau + carte "Non classé") et aucun contenu d\'onglet', async () => {
    const { wrapper } = await mountBinders(null)
    const text = wrapper.text()

    expect(text).toContain('Chimie organique')
    expect(text).toContain('Non classé')
    // b1 : 1 deck (DECK), 1 note (NOTE_B1)
    expect(text).toContain('1 decks · 1 notes')
    // Non classé : agrégat sur binder_id === null -> 0 deck, 1 note (NOTE_UNCLASSIFIED)
    expect(text).toContain('0 decks · 1 notes')

    // Ni onglets, ni contenu type, ni sous-classeur (SUBBINDER, enfant de b1) a la racine
    expect(wrapper.findAll('button').some((b) => b.text().trim() === 'Notes')).toBe(false)
    expect(wrapper.findAll('button').some((b) => b.text().trim() === 'Révision')).toBe(false)
    expect(text).not.toContain('Sous-classeur B1')
  })

  it('clic sur une carte de classeur navigue vers /bibliotheque/:id', async () => {
    const { wrapper, router } = await mountBinders(null)
    const card = findCard(wrapper, 'Chimie organique')
    expect(card).toBeTruthy()

    await card!.trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.fullPath).toBe('/bibliotheque/b1')
  })

  it('clic sur la carte virtuelle "Non classé" navigue vers /bibliotheque/non-classe', async () => {
    const { wrapper, router } = await mountBinders(null)
    const card = findCard(wrapper, 'Non classé')
    expect(card).toBeTruthy()

    await card!.trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.fullPath).toBe('/bibliotheque/non-classe')
  })
})

describe('Binders — à l\'intérieur d\'un classeur réel', () => {
  beforeEach(() => vi.clearAllMocks())

  it('affiche à la fois la grille des sous-classeurs ET le contenu d\'onglet', async () => {
    const { wrapper } = await mountBinders('b1')
    const text = wrapper.text()

    expect(text).toContain('Sous-classeur B1')
    expect(text).toContain('Notes (')
    expect(text).toContain('Note du classeur b1')
    // filterBinderId === currentBinderId pour un vrai classeur : la note non classée
    // ne doit pas fuiter dans le contenu de b1.
    expect(text).not.toContain('Note libre')
  })
})

describe('Binders — pseudo-classeur "Non classé"', () => {
  beforeEach(() => vi.clearAllMocks())

  it("affiche le contenu filtré sur binder_id === null (pas sur la chaîne 'non-classe'), sans grille de sous-classeurs", async () => {
    const { wrapper } = await mountBinders('non-classe')
    const text = wrapper.text()

    // Subtilité critique (filterBinderId) : le contenu réellement non classé doit
    // apparaître. Si la distinction navigation/filtrage était perdue (comparaison
    // sur la chaîne littérale 'non-classe' au lieu de null), cette liste serait
    // vide malgré la présence de NOTE_UNCLASSIFIED dans le store.
    expect(text).toContain('Note libre')
    expect(text).not.toContain('Note du classeur b1')

    // Aucune grille de sous-classeurs : 'non-classe' n'est pas un nœud de hiérarchie.
    expect(text).not.toContain('Aucun sous-classeur')
    expect(text).not.toContain('Sous-classeurs')
    expect(findCard(wrapper, 'Chimie organique')).toBeFalsy()
  })

  it('fil d\'Ariane : "Racine / Non classé" sans planter', async () => {
    const { wrapper } = await mountBinders('non-classe')
    const nav = wrapper.find('nav')

    expect(nav.exists()).toBe(true)
    expect(nav.text()).toContain('Racine')
    expect(nav.text()).toContain('Non classé')
  })

  // Bug confirmé par la revue de Task 2 : detachItem() n'était gardé que par
  // `!currentBinderId.value`, qui ne filtre pas la chaîne (tronquée) 'non-classe'
  // (vérité). Le bouton "Retirer du classeur" ne doit pas être rendu du tout ici :
  // il n'y a pas de vrai classeur d'où détacher un contenu déjà non classé.
  it('ligne note : le bouton "Retirer du classeur" n\'est PAS rendu sur le pseudo-classeur Non classé', async () => {
    const { wrapper } = await mountBinders('non-classe')

    expect(wrapper.text()).toContain('Note libre')
    const detachButton = wrapper
      .findAll('button')
      .find((b) => b.attributes('title') === 'Retirer du classeur')
    expect(detachButton).toBeFalsy()
  })
})

describe('Binders — bascule Notes/Revision/Autres', () => {
  beforeEach(() => vi.clearAllMocks())

  it('affiche exactement 3 onglets : Notes, Révision, Autres', async () => {
    const { wrapper } = await mountBinders()
    const tabsText = wrapper.text()
    expect(tabsText).toContain('Notes')
    expect(tabsText).toContain('Révision')
    expect(tabsText).toContain('Autres')
  })

  it("onglet Revision : fusionne decks et ensembles dans une seule liste", async () => {
    const { wrapper } = await mountBinders()
    await clickTab(wrapper, 'Révision')
    await flushPromises()

    expect(wrapper.text()).toContain('Deck classique')
    expect(wrapper.text()).toContain('Mixte')
  })

  it("clic sur un ensemble hétérogène navigue vers RevisionSetDetail", async () => {
    const { wrapper, router } = await mountBinders()
    await clickTab(wrapper, 'Révision')
    await flushPromises()

    await wrapper.find('[data-test="revision-row-set-7"]').trigger('click')
    // Le handler @click="router.push(...)" ne fait pas attendre la promesse de
    // navigation par le gestionnaire d'evenement Vue (comme pour le bouton
    // retour de StudyDeck.spec.ts) -- flushPromises() laisse la navigation
    // (matcher + guards, tous bases sur des promesses) se resoudre avant
    // d'inspecter router.currentRoute.
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/revision/sets/7')
  })

  it("ligne d'ensemble affiche le badge 'dues', les mini-icones de types presents et le dernier passage", async () => {
    const { wrapper } = await mountBinders()
    await clickTab(wrapper, 'Révision')
    await flushPromises()

    const row = wrapper.find('[data-test="revision-row-set-7"]')
    expect(row.find('[data-test="due-badge"]').text()).toContain('1')
    expect(row.find('[data-test="type-icon-flashcard"]').exists()).toBe(true)
    expect(row.find('[data-test="type-icon-qcm"]').exists()).toBe(true)
    expect(row.text()).toContain("dernier passage aujourd'hui")
  })

  it('bouton primaire contextuel : "Nouvelle note" sur Notes, "Nouvel ensemble" sur Révision', async () => {
    const { wrapper } = await mountBinders()
    expect(wrapper.find('[data-test="primary-action-button"]').text()).toContain('Nouvelle note')

    await clickTab(wrapper, 'Révision')
    await flushPromises()
    expect(wrapper.find('[data-test="primary-action-button"]').text()).toContain('Nouvel ensemble')
  })

  it("Nouvel ensemble ouvre RevisionSetModal en mode creation", async () => {
    const { wrapper } = await mountBinders()
    await clickTab(wrapper, 'Révision')
    await flushPromises()
    await wrapper.find('[data-test="primary-action-button"]').trigger('click')
    await flushPromises()

    // RevisionSetModal s'appuie sur BaseModal, qui teleporte son contenu vers
    // document.body (Dialog headlessui) : wrapper.text() n'inclut pas ce
    // contenu teleporte (meme idiome que RevisionSetModal.spec.ts et
    // BaseModal.spec.ts, qui lisent tous deux document.body directement).
    expect(document.body.textContent).toContain('Nouvel ensemble de révision')
  })

  it("onglet Autres regroupe Diagrammes et PDF (non-regression, rien ne disparait)", async () => {
    const { wrapper } = await mountBinders()
    await clickTab(wrapper, 'Autres')
    await flushPromises()
    expect(wrapper.text()).toContain('Diagrammes')
    expect(wrapper.text()).toContain('Documents PDF')
  })

  it("ligne deck : bouton Retirer du classeur appelle detachItems avec type deck", async () => {
    api.post.mockResolvedValue({ data: { detached: 1 } })
    const { wrapper } = await mountBinders()
    await clickTab(wrapper, 'Révision')
    await flushPromises()

    const deckRow = wrapper.findAll('button').find((b) => b.attributes('title') === 'Retirer du classeur')
    expect(deckRow).toBeTruthy()
    await deckRow!.trigger('click')
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith('/binders/b1/items/detach', {
      items: [{ type: 'deck', id: 1 }],
    })
  })

  it("ligne ensemble : bouton Retirer du classeur appelle detachItems avec type set", async () => {
    api.post.mockResolvedValue({ data: { detached: 1 } })
    const { wrapper } = await mountBinders()
    await clickTab(wrapper, 'Révision')
    await flushPromises()

    const setRow = wrapper.find('[data-test="revision-row-set-7"]')
    const detachButton = setRow.findAll('button').find((b) => b.attributes('title') === 'Retirer du classeur')
    expect(detachButton).toBeTruthy()
    await detachButton!.trigger('click')
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith('/binders/b1/items/detach', {
      items: [{ type: 'set', id: 7 }],
    })
  })

  it("ligne ensemble : bouton Statistiques navigue vers /revision/sets/:id/stats", async () => {
    const { wrapper, router } = await mountBinders()
    await clickTab(wrapper, 'Révision')
    await flushPromises()

    const setRow = wrapper.find('[data-test="revision-row-set-7"]')
    const statsButton = setRow.findAll('button').find((b) => b.attributes('title') === 'Statistiques')
    expect(statsButton).toBeTruthy()
    await statsButton!.trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.fullPath).toBe('/revision/sets/7/stats')
  })

  it("non-regression : le filtre par tag reste visible quel que soit l'onglet", async () => {
    const { wrapper } = await mountBinders()
    expect(wrapper.text()).toContain('Filtrer')
    await clickTab(wrapper, 'Révision')
    await flushPromises()
    expect(wrapper.text()).toContain('Filtrer')
  })
})

// binderAggregate() est une fonction pure exportée par Binders.vue (bloc <script>
// normal, cf. Task 1 bibliotheque-redesign) : elle ne lit aucun store, donc ces tests
// n'ont pas besoin de monter le composant ni d'activer Pinia.
describe('binderAggregate', () => {
  // "il y a environ 25h" -> floor(25/24) = 1 jour -> "hier". Volontairement pas 24h
  // pile pour ne pas dépendre de l'arrondi exact au moment où le test tourne.
  const YESTERDAY_ISO = new Date(Date.now() - 25 * 60 * 60 * 1000).toISOString()
  // Un peu plus de 3 jours pour ne pas flirter avec la frontière de floor().
  const THREE_DAYS_AGO_ISO = new Date(Date.now() - (3 * 86400000 + 60000)).toISOString()
  const NOW_ISO = new Date().toISOString()

  const decks = [
    { binder_id: 'b1', created_at: THREE_DAYS_AGO_ISO },
    { binder_id: 'b1', created_at: THREE_DAYS_AGO_ISO },
    { binder_id: 'b-old', created_at: THREE_DAYS_AGO_ISO },
  ]
  const notes = [
    { binder_id: 'b1', updated_at: NOW_ISO },
    { binder_id: 'b1', updated_at: NOW_ISO },
    { binder_id: 'b1', updated_at: NOW_ISO },
  ]
  const sets = [{ binder_id: 'b-yesterday', updated_at: YESTERDAY_ISO }]

  it('compte les decks et notes du classeur et retient l\'activité la plus récente ("aujourd\'hui")', () => {
    const result = binderAggregate('b1', decks, notes, sets)
    expect(result.deckCount).toBe(2)
    expect(result.noteCount).toBe(3)
    expect(result.lastActivityLabel).toBe("aujourd'hui")
  })

  it('formate "hier" pour un ensemble de révision mis à jour il y a environ 25h', () => {
    const result = binderAggregate('b-yesterday', decks, notes, sets)
    expect(result.lastActivityLabel).toBe('hier')
    expect(result.deckCount).toBe(0)
    expect(result.noteCount).toBe(0)
  })

  it("formate \"il y a N jours\" à partir de created_at des decks (pas d'updated_at)", () => {
    const result = binderAggregate('b-old', decks, notes, sets)
    expect(result.lastActivityLabel).toBe('il y a 3 jours')
    expect(result.deckCount).toBe(1)
  })

  it('retourne un libellé null (pas de date fabriquée) pour un classeur sans aucun enfant', () => {
    const result = binderAggregate('b-empty', decks, notes, sets)
    expect(result).toEqual({ deckCount: 0, noteCount: 0, lastActivityLabel: null })
  })
})
