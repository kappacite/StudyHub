import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PageContainer from '../../src/components/ui/base/PageContainer.vue'

describe('PageContainer', () => {
  it('rend le contenu projeté', () => {
    const wrapper = mount(PageContainer, { slots: { default: '<p class="c">Hello</p>' } })
    expect(wrapper.find('.c').exists()).toBe(true)
  })

  it('utilise la largeur par défaut max-w-6xl', () => {
    const wrapper = mount(PageContainer)
    expect(wrapper.classes()).toContain('max-w-6xl')
  })

  it('applique la largeur narrow/wide', () => {
    expect(mount(PageContainer, { props: { size: 'narrow' } }).classes()).toContain('max-w-3xl')
    expect(mount(PageContainer, { props: { size: 'wide' } }).classes()).toContain('max-w-7xl')
  })
})
