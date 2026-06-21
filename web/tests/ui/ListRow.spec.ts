import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ListRow from '../../src/components/ui/base/ListRow.vue'

describe('ListRow', () => {
  it('affiche titre et sous-titre', () => {
    const wrapper = mount(ListRow, { props: { title: 'Chimie', subtitle: '12 cartes' } })
    expect(wrapper.text()).toContain('Chimie')
    expect(wrapper.text()).toContain('12 cartes')
  })

  it('rend un <button> quand as="button"', () => {
    const wrapper = mount(ListRow, { props: { as: 'button', title: 'X' } })
    expect(wrapper.element.tagName).toBe('BUTTON')
  })

  it('applique le style interactif (hover) quand interactive', () => {
    const wrapper = mount(ListRow, { props: { interactive: true, title: 'X' } })
    expect(wrapper.classes()).toContain('cursor-pointer')
  })

  it('rend les slots leading/trailing', () => {
    const wrapper = mount(ListRow, {
      slots: { leading: '<i class="lead" />', trailing: '<i class="trail" />' },
    })
    expect(wrapper.find('.lead').exists()).toBe(true)
    expect(wrapper.find('.trail').exists()).toBe(true)
  })
})
