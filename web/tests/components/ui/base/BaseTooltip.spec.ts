import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseTooltip from '../../../../src/components/ui/base/BaseTooltip.vue'

describe('BaseTooltip', () => {
  it('ne montre pas la bulle par défaut', () => {
    const wrapper = mount(BaseTooltip, { props: { content: 'Facteur de facilité' }, slots: { default: '<span>i</span>' } })
    expect(wrapper.find('[role="tooltip"]').exists()).toBe(false)
  })

  it('montre la bulle avec son contenu au survol', async () => {
    const wrapper = mount(BaseTooltip, { props: { content: 'Facteur de facilité' }, slots: { default: '<span>i</span>' } })
    await wrapper.trigger('mouseenter')
    const tooltip = wrapper.find('[role="tooltip"]')
    expect(tooltip.exists()).toBe(true)
    expect(tooltip.text()).toBe('Facteur de facilité')
  })

  it('masque la bulle quand la souris quitte', async () => {
    const wrapper = mount(BaseTooltip, { props: { content: 'X' }, slots: { default: '<span>i</span>' } })
    await wrapper.trigger('mouseenter')
    await wrapper.trigger('mouseleave')
    expect(wrapper.find('[role="tooltip"]').exists()).toBe(false)
  })

  it('montre la bulle au focus clavier et la masque au blur', async () => {
    const wrapper = mount(BaseTooltip, { props: { content: 'X' }, slots: { default: '<span tabindex="0">i</span>' } })
    await wrapper.trigger('focusin')
    expect(wrapper.find('[role="tooltip"]').exists()).toBe(true)
    await wrapper.trigger('focusout')
    expect(wrapper.find('[role="tooltip"]').exists()).toBe(false)
  })

  it('applique la classe de positionnement correspondant à placement="bottom"', async () => {
    const wrapper = mount(BaseTooltip, { props: { content: 'X', placement: 'bottom' }, slots: { default: '<span>i</span>' } })
    await wrapper.trigger('mouseenter')
    expect(wrapper.find('[role="tooltip"]').classes()).toContain('top-full')
  })
})
