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

  it('affiche le selecteur de type meme avec lockedSetId (ensemble heterogene)', async () => {
    const wrapper = mount(RevisionItemModal, {
      props: { binderId: null, decks: [], lockedSetId: 7 },
    })
    await flushPromises()

    const typeButtons = wrapper.findAll('button').filter((b) =>
      ['Carte', 'QCM', 'Vrai / Faux', 'Définition', 'Ordre', 'Association'].includes(b.text()),
    )
    expect(typeButtons).toHaveLength(6)
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

  it('respecte toujours lockedType quand fourni (retrocompat RevisionSetManage)', async () => {
    const wrapper = mount(RevisionItemModal, {
      props: { binderId: null, decks: [], lockedSetId: 7, lockedType: 'qcm' },
    })
    await flushPromises()

    const typeButtons = wrapper.findAll('button').filter((b) => b.text() === 'QCM')
    expect(typeButtons).toHaveLength(0) // pas de selecteur : le seul champ visible est le formulaire QCM
    expect(wrapper.text()).toContain('Question')
  })
})
