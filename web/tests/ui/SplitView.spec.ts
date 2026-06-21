import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SplitView from '../../src/components/ui/base/SplitView.vue'

describe('SplitView', () => {
  it('rend les colonnes left et right', () => {
    const wrapper = mount(SplitView, {
      slots: { left: '<nav class="tree" />', right: '<main class="content" />' },
    })
    expect(wrapper.find('.tree').exists()).toBe(true)
    expect(wrapper.find('.content').exists()).toBe(true)
  })

  it('applique la largeur de colonne gauche par défaut (lg:w-72)', () => {
    const wrapper = mount(SplitView)
    expect(wrapper.find('aside').classes()).toContain('lg:w-72')
  })

  it('respecte la prop leftWidth', () => {
    const wrapper = mount(SplitView, { props: { leftWidth: 'lg:w-80' } })
    expect(wrapper.find('aside').classes()).toContain('lg:w-80')
  })
})
