import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseSkeleton from '../../../../src/components/ui/base/BaseSkeleton.vue'

describe('BaseSkeleton', () => {
  it('applique le rayon 8px par défaut (cohérent avec les cartes)', () => {
    const wrapper = mount(BaseSkeleton)
    expect(wrapper.classes()).toContain('rounded-lg')
  })

  it('applique le rayon fourni via la prop rounded', () => {
    const wrapper = mount(BaseSkeleton, { props: { rounded: 'rounded-full' } })
    expect(wrapper.classes()).toContain('rounded-full')
    expect(wrapper.classes()).not.toContain('rounded-lg')
  })

  it('applique la classe de taille par défaut', () => {
    const wrapper = mount(BaseSkeleton)
    expect(wrapper.classes()).toContain('h-4')
    expect(wrapper.classes()).toContain('w-full')
  })

  it('applique la classe de taille fournie via customClass', () => {
    const wrapper = mount(BaseSkeleton, { props: { customClass: 'h-10 w-10' } })
    expect(wrapper.classes()).toContain('h-10')
    expect(wrapper.classes()).toContain('w-10')
  })

  it('porte l\'animation de pulsation', () => {
    const wrapper = mount(BaseSkeleton)
    expect(wrapper.classes()).toContain('animate-pulse')
  })
})
