import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import Binders from '../../../src/views/Binders/Binders.vue'
import { useBindersStore } from '../../../src/stores/binders'
import { useNotesStore } from '../../../src/stores/notes'
import { useDecksStore } from '../../../src/stores/decks'
import { useRevisionStore } from '../../../src/stores/revision'
import { useTagsStore } from '../../../src/stores/tags'
import { useAuthStore } from '../../../src/stores/auth'

const BINDER = { id: 'b1', name: 'Chimie organique', parent_id: null, is_public: false, user_id: 1, tags: [] }
const DECK = { id: 1, binder_id: 'b1', name: 'Deck classique', description: '', reversed: false, tuning_default: 1, card_count: 5, created_at: '', tags: [] }
const HETEROGENEOUS_SET = { id: 7, name: 'Mixte', description: null, type: null, binder_id: 'b1', tuning_default: 1, is_public: false, item_count: 3 }

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

const NOW = new Date().toISOString()
const OVERDUE = new Date(Date.now() - 86400000).toISOString()
// Item "pas encore du" : programme dans un jour, pour eviter toute course
// avec le seuil de comparaison (next_review <= Date.now()) evalue quelques
// microsecondes/secondes plus tard -- une valeur "maintenant" serait fragile
// (flaky) vis-a-vis de ce <=.
const NOT_DUE = new Date(Date.now() + 86400000).toISOString()
const SET_7_ITEMS = [
  { id: 101, set_id: 7, type: 'flashcard', payload: {}, tuning: 1, position: 0, interval: 1, ease_factor: 2.5, repetitions: 1, next_review: OVERDUE, created_at: NOW, updated_at: NOW },
  { id: 102, set_id: 7, type: 'qcm', payload: {}, tuning: 1, position: 0, interval: 5, ease_factor: 2.5, repetitions: 1, next_review: NOT_DUE, created_at: NOW, updated_at: NOW },
]

// Dispatcher regex par URL — meme idiome que StudyDeck.spec.ts. Ne pas seeder l'etat
// des stores directement : onMounted() de Binders.vue appelle fetchBinders/fetchDecks/
// fetchNotes/fetchSets/fetchTags, qui ecrasent integralement le ref du store avec la
// reponse mockee (cf. revision.ts:193 `sets.value = response.data.data`) — un seed manuel
// avant le mount serait silencieusement efface des que ces appels resolvent.
function makeGetImpl() {
  return (url: string) => {
    if (/^\/binders\?/.test(url)) return Promise.resolve({ data: { data: [BINDER] } })
    if (/^\/binders\/[^/?]+$/.test(url)) return Promise.resolve({ data: BINDER }) // fetchMissingBinder — currentBinderId watcher tourne avant que fetchBinders() ait resolu

    if (/^\/decks\?/.test(url)) return Promise.resolve({ data: { data: [DECK] } })
    if (/^\/notes\?/.test(url)) return Promise.resolve({ data: { data: [] } })
    if (/^\/revision\/sets\?/.test(url)) return Promise.resolve({ data: { data: [HETEROGENEOUS_SET] } })
    if (url === '/revision/sets/7/items') return Promise.resolve({ data: { data: SET_7_ITEMS } })
    if (url === '/tags') return Promise.resolve({ data: { data: [] } })
    if (/^\/diagrams\?/.test(url)) return Promise.resolve({ data: { data: [] } })
    if (/^\/pdfs\?/.test(url)) return Promise.resolve({ data: { data: [] } })
    return Promise.reject(new Error(`URL GET non mockée dans le test: ${url}`))
  }
}

async function mountBinders(binderId = 'b1') {
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
  await router.push(`/bibliotheque/${binderId}`)
  await router.isReady()
  const wrapper = mount(Binders, { global: { plugins: [pinia, router] } })
  await flushPromises()
  return { wrapper, router, bindersStore, notesStore, decksStore, revisionStore, tagsStore }
}

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

  it("non-regression : colonne Dossiers et filtre par tag restent visibles quel que soit l'onglet", async () => {
    const { wrapper } = await mountBinders()
    expect(wrapper.text()).toContain('Dossiers')
    expect(wrapper.text()).toContain('Filtrer')
    await clickTab(wrapper, 'Révision')
    await flushPromises()
    expect(wrapper.text()).toContain('Dossiers')
  })
})
