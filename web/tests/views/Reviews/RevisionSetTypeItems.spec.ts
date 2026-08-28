import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import RevisionSetTypeItems from '../../../src/views/Reviews/RevisionSetTypeItems.vue'

const SET = { id: 7, name: 'Mécanismes SN1 / SN2', description: null, type: null, binder_id: 'b1', tuning_default: 1, is_public: false, item_count: 3 }

function item(id: number, type: string, payload: Record<string, unknown>) {
  return { id, set_id: 7, type, payload, tuning: 1, position: 0, interval: 0, ease_factor: 2.5, repetitions: 0, next_review: '', created_at: '', updated_at: '' }
}

const ITEMS = [
  item(101, 'flashcard', { front: 'Chat', back: 'Cat' }),
  item(102, 'flashcard', { front: 'Chien', back: 'Dog' }),
  item(103, 'qcm', { question: 'Capitale ?' }),
]

const stub = { template: '<div />' }
function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/revision/sets/:id', name: 'RevisionSetDetail', component: stub },
      { path: '/revision/sets/:id/items/:type', name: 'RevisionSetTypeItems', component: stub },
    ],
  })
}

async function mountView(type = 'flashcard') {
  const pinia = createPinia()
  setActivePinia(pinia)
  api.get.mockImplementation((url: string) => {
    if (/\/revision\/sets\/\d+$/.test(url)) return Promise.resolve({ data: SET })
    if (/\/revision\/sets\/\d+\/items$/.test(url)) return Promise.resolve({ data: { data: ITEMS } })
    return Promise.reject(new Error(`non mocké: ${url}`))
  })
  const router = createTestRouter()
  await router.push(`/revision/sets/7/items/${type}`)
  await router.isReady()
  const wrapper = mount(RevisionSetTypeItems, { global: { plugins: [pinia, router] } })
  await flushPromises()
  return { wrapper, router }
}

describe('RevisionSetTypeItems', () => {
  beforeEach(() => vi.clearAllMocks())

  it('liste uniquement les items du type demande', async () => {
    const { wrapper } = await mountView('flashcard')
    expect(wrapper.text()).toContain('Chat')
    expect(wrapper.text()).toContain('Chien')
    expect(wrapper.text()).not.toContain('Capitale ?')
  })

  it('supprime un item individuel', async () => {
    vi.stubGlobal('confirm', vi.fn(() => true))
    api.delete.mockResolvedValue({ data: {} })
    const { wrapper } = await mountView('flashcard')

    await wrapper.findAll('[data-test="delete-item-button"]')[0].trigger('click')
    await flushPromises()

    expect(api.delete).toHaveBeenCalledWith('/revision/sets/7/items/101')
    vi.unstubAllGlobals()
  })

  it('etat erreur : echec du chargement affiche un retry, distinct de l\'etat vide', async () => {
    api.get.mockImplementation((url: string) => {
      if (/\/revision\/sets\/\d+$/.test(url)) return Promise.resolve({ data: SET })
      if (/\/revision\/sets\/\d+\/items$/.test(url)) return Promise.reject(new Error('network'))
      return Promise.reject(new Error('non mocké'))
    })
    const pinia = createPinia()
    setActivePinia(pinia)
    const router = createTestRouter()
    await router.push('/revision/sets/7/items/flashcard')
    await router.isReady()
    const wrapper = mount(RevisionSetTypeItems, { global: { plugins: [pinia, router] } })
    await flushPromises()

    expect(wrapper.text()).toContain('Le chargement a échoué')
    expect(wrapper.text()).not.toContain('Aucun élément de ce type.')
    const retry = wrapper.find('[data-test="retry-button"]')
    expect(retry.exists()).toBe(true)

    // Le retry relance reellement le chargement : cette fois il aboutit.
    api.get.mockImplementation((url: string) => {
      if (/\/revision\/sets\/\d+$/.test(url)) return Promise.resolve({ data: SET })
      if (/\/revision\/sets\/\d+\/items$/.test(url)) return Promise.resolve({ data: { data: ITEMS } })
      return Promise.reject(new Error('non mocké'))
    })
    await retry.trigger('click')
    await flushPromises()

    expect(wrapper.text()).not.toContain('Le chargement a échoué')
    expect(wrapper.text()).toContain('Chat')
  })

  it('le fil d\'ariane retourne vers RevisionSetDetail', async () => {
    const { wrapper, router } = await mountView('flashcard')
    await wrapper.find('[data-test="back-to-set-link"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/revision/sets/7')
  })
})
