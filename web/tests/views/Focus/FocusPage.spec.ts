// Suite de test ciblée pour FocusPage.vue — couvre le correctif « revue de branche
// reviser-hub » finding #1 : le type `revision_set` de FocusItem n'était pas géré
// dans studyItem/getItemIcon/getItemSummary (seul Reviews.vue, la référence, le
// traitait). Pas de suite pré-existante pour cet écran ; cette suite reste focalisée
// sur le comportement corrigé plutôt que de retro-couvrir tout l'écran.
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import FocusPage from '../../../src/views/Focus/FocusPage.vue'

const QCM_SET = {
  id: 1,
  name: 'Série QCM',
  description: null,
  type: 'qcm',
  binder_id: null,
  tuning_default: 1,
  is_public: false,
  item_count: 10,
  read_only: false,
}
const MIXED_SET = {
  id: 2,
  name: 'Série mixte',
  description: null,
  type: null,
  binder_id: null,
  tuning_default: 1,
  is_public: false,
  item_count: 5,
  read_only: false,
}

const TODAY_QCM_SET = {
  type: 'revision_set',
  id: 1,
  title: 'Série QCM',
  count: 10,
  is_late: false,
  last_session_ago_days: null,
}
const TODAY_MIXED_SET = {
  type: 'revision_set',
  id: 2,
  title: 'Série mixte',
  count: 5,
  is_late: false,
  last_session_ago_days: null,
}
const TODAY_UNKNOWN_SET = {
  type: 'revision_set',
  id: 99,
  title: 'Ensemble inconnu',
  count: 3,
  is_late: false,
  last_session_ago_days: null,
}

const stub = { template: '<div />' }
function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/focus', name: 'Focus', component: stub },
      { path: '/revision/sets/:id/study', name: 'RevisionStudy', component: stub },
      { path: '/revision/sets/:id/run', name: 'QcmRun', component: stub },
    ],
  })
}

interface MountOverrides {
  items?: Record<string, unknown>[]
  sets?: Record<string, unknown>[]
}

async function mountFocusPage(overrides: MountOverrides = {}) {
  const items = overrides.items ?? [TODAY_QCM_SET, TODAY_MIXED_SET, TODAY_UNKNOWN_SET]
  const sets = overrides.sets ?? [QCM_SET, MIXED_SET]

  const pinia = createPinia()
  setActivePinia(pinia)
  api.get.mockImplementation((url: string) => {
    if (/^\/revision\/sets\?/.test(url)) return Promise.resolve({ data: { data: sets } })
    if (/^\/focus\/today/.test(url)) {
      return Promise.resolve({
        data: {
          total_due: items.reduce((acc, i) => acc + (i.count as number), 0),
          late_count: 0,
          flashcard_count: 0,
          blurting_count: 0,
          assignment_count: 0,
          items,
        },
      })
    }
    if (/^\/focus\/forecast/.test(url)) return Promise.resolve({ data: { forecast: [] } })
    if (/^\/focus\/retention/.test(url)) return Promise.resolve({ data: { by_subject: [] } })
    return Promise.reject(new Error(`URL non mockée: ${url}`))
  })

  const router = createTestRouter()
  await router.push('/focus')
  await router.isReady()
  const wrapper = mount(FocusPage, { global: { plugins: [pinia, router] } })
  await flushPromises()
  return { wrapper, router }
}

describe('FocusPage — routage des ensembles de révision (FocusItem.type === "revision_set")', () => {
  beforeEach(() => vi.clearAllMocks())

  it('affiche un résumé dédié pour un ensemble de révision dû (pas le libellé "Devoir")', async () => {
    const { wrapper } = await mountFocusPage()
    expect(wrapper.text()).toContain('10 élément(s) de la série à revoir')
    expect(wrapper.text()).not.toContain('Devoir sans date limite')
  })

  it('le bouton Réviser d\'un ensemble QCM homogène navigue vers /run', async () => {
    const { wrapper, router } = await mountFocusPage()
    const buttons = wrapper.findAll('button').filter((b) => b.text().includes('Réviser'))
    await buttons[0].trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/revision/sets/1/run')
  })

  it('le bouton Réviser d\'un ensemble hétérogène navigue vers /study', async () => {
    const { wrapper, router } = await mountFocusPage()
    const buttons = wrapper.findAll('button').filter((b) => b.text().includes('Réviser'))
    await buttons[1].trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/revision/sets/2/study')
  })

  it('un ensemble absent du store retombe sur /study (jamais /run par défaut)', async () => {
    const { wrapper, router } = await mountFocusPage()
    const buttons = wrapper.findAll('button').filter((b) => b.text().includes('Réviser'))
    await buttons[2].trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/revision/sets/99/study')
  })
})
