import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), put: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import RevisionItemModal from '../../../src/components/decks/RevisionItemModal.vue'

describe('RevisionItemModal — ajout a un ensemble heterogene existant', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    api.get.mockResolvedValue({ data: { data: [] } })
  })

  it('affiche 6 types avec lockedSetId, "Carte" (Deck) exclu, "Flashcards" inclus', async () => {
    const wrapper = mount(RevisionItemModal, {
      props: { binderId: null, decks: [], lockedSetId: 7 },
    })
    await flushPromises()

    const labels = wrapper.findAll('button').map((b) => b.text()).filter((t) =>
      ['Carte', 'QCM', 'Vrai / Faux', 'Définition', 'Ordre', 'Association', 'Flashcards'].includes(t),
    )
    expect(labels).toEqual(['QCM', 'Vrai / Faux', 'Définition', 'Ordre', 'Association', 'Flashcards'])
  })

  it("poste le type choisi et l'id de l'ensemble verrouille (pas de selecteur de cible)", async () => {
    api.post.mockResolvedValue({
      data: { id: 30, set_id: 7, type: 'vf', payload: { assertion: 'x', correct: true }, tuning: 1, position: 0, interval: 0, ease_factor: 2.5, repetitions: 0, next_review: '', created_at: '', updated_at: '' },
    })
    const wrapper = mount(RevisionItemModal, {
      props: { binderId: null, decks: [], lockedSetId: 7 },
    })
    await flushPromises()

    await wrapper.findAll('button').find((b) => b.text() === 'Vrai / Faux')!.trigger('click')
    await wrapper.find('textarea').setValue('Le ciel est bleu.')
    await wrapper.findAll('button').find((b) => b.text() === 'Vrai')!.trigger('click')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith('/revision/sets/7/items', {
      payload: { assertion: 'Le ciel est bleu.', correct: true },
      type: 'vf',
      tuning: 1.0,
    })
    expect(wrapper.emitted('created')).toBeTruthy()
  })

  it("poste un item flashcard (front/back) a l'ensemble verrouille", async () => {
    api.post.mockResolvedValue({
      data: { id: 31, set_id: 7, type: 'flashcard', payload: { front: 'Chat', back: 'Cat' }, tuning: 1, position: 0, interval: 0, ease_factor: 2.5, repetitions: 0, next_review: '', created_at: '', updated_at: '' },
    })
    const wrapper = mount(RevisionItemModal, {
      props: { binderId: null, decks: [], lockedSetId: 7 },
    })
    await flushPromises()

    await wrapper.findAll('button').find((b) => b.text() === 'Flashcards')!.trigger('click')
    const textareas = wrapper.findAll('textarea')
    await textareas[0].setValue('Chat')
    await textareas[1].setValue('Cat')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith('/revision/sets/7/items', {
      payload: { front: 'Chat', back: 'Cat' },
      type: 'flashcard',
      tuning: 1.0,
    })
    expect(wrapper.emitted('created')).toBeTruthy()
  })

  it('respecte toujours lockedType quand fourni (retrocompat RevisionSetManage)', async () => {
    const wrapper = mount(RevisionItemModal, {
      props: { binderId: null, decks: [], lockedSetId: 7, lockedType: 'qcm' },
    })
    await flushPromises()

    const typeButtons = wrapper.findAll('button').filter((b) => b.text() === 'QCM')
    expect(typeButtons).toHaveLength(0) // pas de selecteur : le seul champ visible est le formulaire QCM
    expect(wrapper.text()).toContain('Question')
  })

  it('sans lockedSetId (creation depuis Reviews.vue) : "Carte" (Deck) reste disponible, non-regression', async () => {
    const wrapper = mount(RevisionItemModal, {
      props: { binderId: null, decks: [{ id: 1, binder_id: null, name: 'Mon deck', description: '', reversed: false, tuning_default: 1, card_count: 0, created_at: '', tags: [] }] },
    })
    await flushPromises()

    const labels = wrapper.findAll('button').map((b) => b.text()).filter((t) =>
      ['Carte', 'QCM', 'Vrai / Faux', 'Définition', 'Ordre', 'Association', 'Flashcards'].includes(t),
    )
    expect(labels).toEqual(['Carte', 'QCM', 'Vrai / Faux', 'Définition', 'Ordre', 'Association', 'Flashcards'])
  })

  it('nouvel ensemble a la volee avec type flashcard : le SET nait heterogene (type: null), pas type: flashcard', async () => {
    api.get.mockResolvedValue({ data: { data: [] } }) // fetchSets() au mount, aucun ensemble existant
    api.post
      .mockResolvedValueOnce({ data: { id: 40, name: 'Nouveau', description: null, type: null, binder_id: null, tuning_default: 1, is_public: false, item_count: 0 } })
      .mockResolvedValueOnce({ data: { id: 41, set_id: 40, type: 'flashcard', payload: { front: 'Chat', back: 'Cat' }, tuning: 1, position: 0, interval: 0, ease_factor: 2.5, repetitions: 0, next_review: '', created_at: '', updated_at: '' } })
    const wrapper = mount(RevisionItemModal, { props: { binderId: null, decks: [] } })
    await flushPromises()

    await wrapper.findAll('button').find((b) => b.text() === 'Flashcards')!.trigger('click')
    await flushPromises()
    await wrapper.find('input[placeholder="Nom de l\'ensemble"]').setValue('Nouveau')
    const textareas = wrapper.findAll('textarea')
    await textareas[0].setValue('Chat')
    await textareas[1].setValue('Cat')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(api.post).toHaveBeenNthCalledWith(1, '/revision/sets', {
      name: 'Nouveau', type: null, description: null, binder_id: null, tuning_default: 1.0,
    })
    expect(api.post).toHaveBeenNthCalledWith(2, '/revision/sets/40/items', {
      payload: { front: 'Chat', back: 'Cat' },
      type: 'flashcard',
      tuning: 1.0,
    })
  })
})
