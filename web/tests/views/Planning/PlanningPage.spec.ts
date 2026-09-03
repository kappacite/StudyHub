import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import PlanningPage from '../../../src/views/Planning/PlanningPage.vue'

const stub = { template: '<div />' }
function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/planning', name: 'Planning', component: stub },
      { path: '/decks/:id/study', name: 'StudyDeck', component: stub },
      { path: '/revision/sets/:id/study', name: 'RevisionStudy', component: stub },
    ],
  })
}

async function mountPage(calendarResponse: unknown) {
  const pinia = createPinia()
  setActivePinia(pinia)
  api.get.mockImplementation((url: string) => {
    if (url.startsWith('/planning/calendar')) return Promise.resolve({ data: calendarResponse })
    return Promise.reject(new Error(`non mocké: ${url}`))
  })
  const router = createTestRouter()
  await router.push('/planning')
  await router.isReady()
  // attachTo: document.body -- BaseModal (headlessui Dialog) teleporte son contenu hors de
  // l'arbre du wrapper, meme idiome que RevisionSetModal.spec.ts/Binders.spec.ts.
  const wrapper = mount(PlanningPage, { global: { plugins: [pinia, router] }, attachTo: document.body })
  await flushPromises()
  return { wrapper, router }
}

describe('PlanningPage — notes-ia-planning-corrections Task 2 : routage deck vs revision_set', () => {
  beforeEach(() => vi.clearAllMocks())

  // BreakdownItem importe dans PlanningPage.vue pour typer studyItemAdvance(item).
  function tomorrow(): string {
    const d = new Date()
    d.setDate(d.getDate() + 1)
    return d.toISOString().slice(0, 10)
  }

  it('un jour avec un ensemble de revision route vers /revision/sets/:id/study au clic Reviser', async () => {
    const calendar = {
      days: [
        {
          date: tomorrow(),
          total_due: 1,
          breakdown: [{ kind: 'revision_set', id: 42, name: 'Chimie', count: 1 }],
        },
      ],
    }
    const { wrapper, router } = await mountPage(calendar)

    const openModalBtn = wrapper.findAll('button').find((b) => b.text().includes('Révision anticipée'))
    expect(openModalBtn).toBeDefined()
    await openModalBtn!.trigger('click')
    await flushPromises()

    // BaseModal teleporte vers document.body (headlessui Dialog).
    const reviserBtn = Array.from(document.body.querySelectorAll('button')).find(
      (b) => b.textContent?.trim() === 'Réviser',
    )
    expect(reviserBtn).toBeDefined()
    reviserBtn!.click()
    await flushPromises()

    expect(router.currentRoute.value.fullPath).toBe('/revision/sets/42/study?include_not_due=true')
    wrapper.unmount()
  })

  it('un jour avec un deck appelle prepareAdvanceReview puis route vers /decks/:id/study?advance=true (non-regression)', async () => {
    const calendar = {
      days: [
        {
          date: tomorrow(),
          total_due: 1,
          breakdown: [{ kind: 'deck', id: 7, name: 'Bio', count: 1 }],
        },
      ],
    }
    api.post.mockResolvedValue({ data: [] })
    const { wrapper, router } = await mountPage(calendar)

    const openModalBtn = wrapper.findAll('button').find((b) => b.text().includes('Révision anticipée'))
    await openModalBtn!.trigger('click')
    await flushPromises()

    const reviserBtn = Array.from(document.body.querySelectorAll('button')).find(
      (b) => b.textContent?.trim() === 'Réviser',
    )
    reviserBtn!.click()
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith('/planning/advance', expect.objectContaining({ deck_id: 7 }))
    expect(router.currentRoute.value.fullPath).toBe('/decks/7/study?advance=true')
    wrapper.unmount()
  })
})
