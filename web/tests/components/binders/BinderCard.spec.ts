import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BinderCard from '../../../src/components/binders/BinderCard.vue'

const BINDER = { id: 'b1', name: 'Chimie organique' }

describe('BinderCard', () => {
  it('affiche le nom du classeur, les compteurs decks/notes et le libellé d\'activité', () => {
    const wrapper = mount(BinderCard, {
      props: {
        binder: BINDER,
        deckCount: 9,
        noteCount: 41,
        lastActivityLabel: "aujourd'hui",
      },
    })

    expect(wrapper.text()).toContain('Chimie organique')
    expect(wrapper.text()).toContain('9 decks · 41 notes')
    expect(wrapper.text()).toContain("Dernière activité : aujourd'hui")
  })

  it("n'affiche aucune ligne d'activité quand lastActivityLabel est null", () => {
    const wrapper = mount(BinderCard, {
      props: {
        binder: BINDER,
        deckCount: 0,
        noteCount: 0,
        lastActivityLabel: null,
      },
    })

    expect(wrapper.text()).not.toContain('Dernière activité')
  })

  it('émet click au clic sur la carte', async () => {
    const wrapper = mount(BinderCard, {
      props: {
        binder: BINDER,
        deckCount: 1,
        noteCount: 2,
        lastActivityLabel: 'hier',
      },
    })

    await wrapper.trigger('click')

    expect(wrapper.emitted('click')).toHaveLength(1)
  })

  it('applique une bordure gauche accentuée seulement quand highlighted est vrai', () => {
    const highlighted = mount(BinderCard, {
      props: { binder: BINDER, deckCount: 1, noteCount: 1, lastActivityLabel: null, highlighted: true },
    })
    const neutral = mount(BinderCard, {
      props: { binder: BINDER, deckCount: 1, noteCount: 1, lastActivityLabel: null },
    })

    expect(highlighted.classes()).toContain('border-l-accent')
    expect(neutral.classes()).not.toContain('border-l-accent')
    expect(neutral.classes()).toContain('border-l-line')
  })

  it('affiche un badge "Cours" quand le classeur est en lecture seule', () => {
    const wrapper = mount(BinderCard, {
      props: {
        binder: { id: 'b2', name: 'Droit constit', readOnly: true },
        deckCount: 1,
        noteCount: 1,
        lastActivityLabel: null,
      },
    })

    expect(wrapper.text()).toContain('Cours')
  })
})
