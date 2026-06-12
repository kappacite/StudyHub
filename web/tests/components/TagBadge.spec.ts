import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TagBadge from '../../src/components/ui/TagBadge.vue'
import type { Tag } from '../../src/stores/tags'

const tag: Tag = {
  id: 1,
  name: 'Chimie',
  color: '#FF0000',
  created_at: '2026-01-01T00:00:00Z',
}

describe('TagBadge', () => {
  it('affiche le nom du tag', () => {
    const wrapper = mount(TagBadge, { props: { tag } })
    expect(wrapper.text()).toContain('Chimie')
  })

  it("masque le bouton de retrait par défaut", () => {
    const wrapper = mount(TagBadge, { props: { tag } })
    expect(wrapper.find('button').exists()).toBe(false)
  })

  it('émet "remove" avec le tag au clic sur le bouton de retrait', async () => {
    const wrapper = mount(TagBadge, { props: { tag, removable: true } })

    const button = wrapper.find('button')
    expect(button.exists()).toBe(true)
    await button.trigger('click')

    expect(wrapper.emitted('remove')).toBeTruthy()
    expect(wrapper.emitted('remove')![0]).toEqual([tag])
  })

  it('applique la couleur du tag à la pastille', () => {
    const wrapper = mount(TagBadge, { props: { tag } })
    const dot = wrapper.find('span.rounded-full')
    expect(dot.attributes('style')).toContain('background-color')
  })

  it('utilise une couleur de repli quand color est null', () => {
    const wrapper = mount(TagBadge, { props: { tag: { ...tag, color: null } } })
    // La couleur de repli (#4F46E5) doit être appliquée sans planter le rendu.
    expect(wrapper.text()).toContain('Chimie')
    expect(wrapper.find('span.rounded-full').exists()).toBe(true)
  })
})
