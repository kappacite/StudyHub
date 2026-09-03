import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import Blurting from '../../../src/views/Notes/Blurting.vue'

const stub = { template: '<div />' }
function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/notes/:id', name: 'NoteEdit', component: stub },
      { path: '/notes/:id/blurting', name: 'NoteBlurting', component: Blurting },
      { path: '/reviews', name: 'Reviews', component: stub },
      { path: '/focus', name: 'Focus', component: stub },
    ],
  })
}

async function mountBlurting() {
  const pinia = createPinia()
  setActivePinia(pinia)
  api.get.mockImplementation((url: string) => {
    if (/^\/notes\/\d+$/.test(url)) {
      return Promise.resolve({ data: { title: 'Chimie organique', content: 'Contenu' } })
    }
    if (url.startsWith('/decks?')) return Promise.resolve({ data: { data: [] } })
    return Promise.reject(new Error(`URL GET non mockée: ${url}`))
  })
  const router = createTestRouter()
  await router.push('/notes/1/blurting')
  await router.isReady()
  const wrapper = mount(Blurting, { global: { plugins: [pinia, router] } })
  await flushPromises()
  return { wrapper, router }
}

// script setup : Brain retire, formattedScore ajoute. getStatusBadgeClass a suivre (tokens).
describe('Blurting — refonte selon le canevas Blurting.dc.html (notes-ia-planning-corrections, Task 6)', () => {
  beforeEach(() => vi.clearAllMocks())

  it('étape rédaction : zone de texte libre et bouton "Lancer l\'analyse IA" (non-régression)', async () => {
    const { wrapper } = await mountBlurting()
    expect(wrapper.find('textarea').exists()).toBe(true)
    expect(wrapper.text()).toContain("Lancer l'analyse IA")
  })

  it('étape résultats : score affiché /10 à une décimale (harmonisé avec Notation/Feynman, plus de %)', async () => {
    api.post.mockResolvedValue({
      data: {
        status: 'SUCCESS',
        result: {
          retention_score: 76,
          concepts: [],
          suggested_flashcards: [],
          general_feedback: 'Bon travail global.',
        },
      },
    })
    const { wrapper } = await mountBlurting()
    await wrapper.find('textarea').setValue('Ma restitution de mémoire.')
    await wrapper.find('[data-test="submit-analysis"]').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('7,6')
    expect(wrapper.text()).not.toContain('76%')
    expect(wrapper.text()).toContain('Bon travail global.')
  })

  it('conserve la cartographie des concepts (fonctionnalité existante, absente du canevas mais non supprimée)', async () => {
    api.post.mockResolvedValue({
      data: {
        status: 'SUCCESS',
        result: {
          retention_score: 60,
          concepts: [{ name: 'SN2', status: 'mastered', explanation: 'Bien acquis.' }],
          suggested_flashcards: [],
          general_feedback: 'Correct.',
        },
      },
    })
    const { wrapper } = await mountBlurting()
    await wrapper.find('textarea').setValue('Restitution.')
    await wrapper.find('[data-test="submit-analysis"]').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('SN2')
    expect(wrapper.text()).toContain('Bien acquis.')
  })

  it('conserve la génération et import de flashcards suggérées (fonctionnalité existante, absente du canevas mais non supprimée)', async () => {
    api.post.mockResolvedValue({
      data: {
        status: 'SUCCESS',
        result: {
          retention_score: 40,
          concepts: [],
          suggested_flashcards: [{ front: 'Q1', back: 'R1' }],
          general_feedback: 'À revoir.',
        },
      },
    })
    const { wrapper } = await mountBlurting()
    await wrapper.find('textarea').setValue('Restitution.')
    await wrapper.find('[data-test="submit-analysis"]').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Flashcards suggérées')
    expect(wrapper.text()).toContain('Q1')
  })

  it("n'utilise plus de couleurs Tailwind brutes pour le score (tokens semantiques)", async () => {
    api.post.mockResolvedValue({
      data: {
        status: 'SUCCESS',
        result: { retention_score: 90, concepts: [], suggested_flashcards: [], general_feedback: 'Excellent.' },
      },
    })
    const { wrapper } = await mountBlurting()
    await wrapper.find('textarea').setValue('Restitution.')
    await wrapper.find('[data-test="submit-analysis"]').trigger('click')
    await flushPromises()

    expect(wrapper.html()).not.toContain('emerald')
    expect(wrapper.html()).not.toContain('rose-')
    expect(wrapper.html()).not.toContain('amber-')
  })
})
