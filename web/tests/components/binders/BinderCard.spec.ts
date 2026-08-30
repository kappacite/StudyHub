import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BinderCard from '../../../src/components/binders/BinderCard.vue'
import type { Tag } from '../../../src/stores/tags'

const BINDER = { id: 'b1', name: 'Chimie organique' }
const TAG_URGENT: Tag = { id: 1, name: 'Urgent', color: '#4F46E5', created_at: '' }

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

  it('rend un <button> avec le chrome BaseCard (rounded-lg, bordure, ombre)', () => {
    const wrapper = mount(BinderCard, {
      props: { binder: BINDER, deckCount: 1, noteCount: 1, lastActivityLabel: null },
    })

    expect(wrapper.element.tagName).toBe('BUTTON')
    expect(wrapper.attributes('type')).toBe('button')
    expect(wrapper.classes()).toContain('rounded-lg')
    expect(wrapper.classes()).toContain('border-line')
    expect(wrapper.classes()).toContain('shadow-elev-1')
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

  it('affiche un TagBadge par tag quand des tags sont passés', () => {
    const wrapper = mount(BinderCard, {
      props: {
        binder: BINDER,
        deckCount: 1,
        noteCount: 1,
        lastActivityLabel: null,
        tags: [TAG_URGENT],
      },
    })

    expect(wrapper.text()).toContain('Urgent')
  })

  it("n'affiche rien de lié aux tags quand tags est omis ou vide", () => {
    const withoutProp = mount(BinderCard, {
      props: { binder: BINDER, deckCount: 1, noteCount: 1, lastActivityLabel: null },
    })
    const withEmptyArray = mount(BinderCard, {
      props: { binder: BINDER, deckCount: 1, noteCount: 1, lastActivityLabel: null, tags: [] },
    })

    expect(withoutProp.text()).not.toContain('Urgent')
    expect(withEmptyArray.text()).not.toContain('Urgent')
  })
})
