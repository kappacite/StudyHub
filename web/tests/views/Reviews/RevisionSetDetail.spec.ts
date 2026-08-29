import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import RevisionSetDetail from '../../../src/views/Reviews/RevisionSetDetail.vue'

const SET = { id: 7, name: 'Mécanismes SN1 / SN2', description: 'Flashcards, QCM et vrai/faux.', type: null, binder_id: 'b1', tuning_default: 1, is_public: false, item_count: 3 }

function item(id: number, type: string, overrides: Record<string, unknown> = {}) {
  return { id, set_id: 7, type, payload: {}, tuning: 1, position: 0, interval: 0, ease_factor: 2.5, repetitions: 0, next_review: '', created_at: '2026-08-20T00:00:00Z', updated_at: '2026-08-28T09:00:00Z', ...overrides }
}

const ITEMS = [
  item(101, 'flashcard', { updated_at: '2026-08-28T09:00:00Z' }),
  item(102, 'flashcard', { updated_at: '2026-08-27T09:00:00Z' }),
  item(103, 'qcm', { updated_at: '2026-08-25T09:00:00Z' }),
]

const stub = { template: '<div />' }
function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/revision/sets/:id', name: 'RevisionSetDetail', component: stub },
      { path: '/revision/sets/:id/study', name: 'RevisionStudy', component: stub },
      { path: '/revision/sets/:id/items/:type', name: 'RevisionSetTypeItems', component: stub },
      { path: '/bibliotheque/:id?', name: 'Bibliotheque', component: stub },
    ],
  })
}

async function mountDetail(setId = '7') {
  const pinia = createPinia()
  setActivePinia(pinia)
  api.get.mockImplementation((url: string) => {
    if (/\/revision\/sets\/\d+$/.test(url)) return Promise.resolve({ data: SET })
    if (/\/revision\/sets\/\d+\/items$/.test(url)) return Promise.resolve({ data: { data: ITEMS } })
    return Promise.reject(new Error(`URL non mockée: ${url}`))
  })
  const router = createTestRouter()
  await router.push(`/revision/sets/${setId}`)
  await router.isReady()
  const wrapper = mount(RevisionSetDetail, { global: { plugins: [pinia, router] } })
  await flushPromises()
  return { wrapper, router }
}

describe('RevisionSetDetail', () => {
  beforeEach(() => vi.clearAllMocks())

  it('affiche le nom, la description et une ligne par type present, avec le bon compte', async () => {
    const { wrapper } = await mountDetail()
    expect(wrapper.text()).toContain('Mécanismes SN1 / SN2')
    expect(wrapper.text()).toContain('Flashcards, QCM et vrai/faux.')
    expect(wrapper.text()).toContain('Flashcards')
    expect(wrapper.text()).toContain('2') // 2 flashcards
    expect(wrapper.text()).toContain('QCM')
    expect(wrapper.text()).toContain('1') // 1 qcm
    expect(wrapper.text()).not.toContain('Vrai / Faux') // absent de cet ensemble
  })

  it('le bouton Reviser l\'ensemble navigue vers /revision/sets/:id/study sans filtre', async () => {
    const { wrapper, router } = await mountDetail()
    await wrapper.find('[data-test="study-set-button"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/revision/sets/7/study')
  })

  it('Reviser sur une ligne de type navigue vers /study avec le filtre type', async () => {
    const { wrapper, router } = await mountDetail()
    await wrapper.find('[data-test="study-type-flashcard"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/revision/sets/7/study?type=flashcard')
  })

  it('Editer sur une ligne de type navigue vers RevisionSetTypeItems', async () => {
    const { wrapper, router } = await mountDetail()
    await wrapper.find('[data-test="edit-type-qcm"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/revision/sets/7/items/qcm')
  })

  it('Supprimer sur une ligne de type demande confirmation puis supprime tous les items de ce type', async () => {
    vi.stubGlobal('confirm', vi.fn(() => true))
    api.delete.mockResolvedValue({ data: {} })
    const { wrapper } = await mountDetail()

    await wrapper.find('[data-test="delete-type-flashcard"]').trigger('click')
    await flushPromises()

    expect(confirm).toHaveBeenCalledWith('Supprimer les 2 flashcards de cet ensemble ?')
    expect(api.delete).toHaveBeenCalledWith('/revision/sets/7/items/101')
    expect(api.delete).toHaveBeenCalledWith('/revision/sets/7/items/102')
    expect(api.delete).not.toHaveBeenCalledWith('/revision/sets/7/items/103')
    vi.unstubAllGlobals()
  })

  it('etat vide : aucun item, affiche BaseEmptyState avec action Ajouter un element', async () => {
    api.get.mockImplementation((url: string) => {
      if (/\/revision\/sets\/\d+$/.test(url)) return Promise.resolve({ data: SET })
      if (/\/revision\/sets\/\d+\/items$/.test(url)) return Promise.resolve({ data: { data: [] } })
      return Promise.reject(new Error('non mocké'))
    })
    const pinia = createPinia()
    setActivePinia(pinia)
    const router = createTestRouter()
    await router.push('/revision/sets/7')
    await router.isReady()
    const wrapper = mount(RevisionSetDetail, { global: { plugins: [pinia, router] } })
    await flushPromises()

    expect(wrapper.text()).toContain('Aucun élément')
  })

  it('etat erreur : echec du chargement des items affiche un retry', async () => {
    api.get.mockImplementation((url: string) => {
      if (/\/revision\/sets\/\d+$/.test(url)) return Promise.resolve({ data: SET })
      if (/\/revision\/sets\/\d+\/items$/.test(url)) return Promise.reject(new Error('network'))
      return Promise.reject(new Error('non mocké'))
    })
    const pinia = createPinia()
    setActivePinia(pinia)
    const router = createTestRouter()
    await router.push('/revision/sets/7')
    await router.isReady()
    const wrapper = mount(RevisionSetDetail, { global: { plugins: [pinia, router] } })
    await flushPromises()

    expect(wrapper.text()).toContain('Le chargement a échoué')
    expect(wrapper.find('[data-test="retry-button"]').exists()).toBe(true)
  })
})
