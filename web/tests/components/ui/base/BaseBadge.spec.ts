import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseBadge from '../../../../src/components/ui/base/BaseBadge.vue'

type Variant = 'neutral' | 'primary' | 'accent' | 'success' | 'warning' | 'danger' | 'info'

describe('BaseBadge', () => {
  it('rend le contenu du slot', () => {
    const wrapper = mount(BaseBadge, { slots: { default: 'Nouveau' } })
    expect(wrapper.text()).toContain('Nouveau')
  })

  it('est une pilule (rayon 999px)', () => {
    const wrapper = mount(BaseBadge)
    expect(wrapper.classes()).toContain('rounded-full')
  })

  it('utilise le token text-tiny (pas de classe Tailwind arbitraire) pour la taille sm', () => {
    const wrapper = mount(BaseBadge, { props: { size: 'sm' } })
    expect(wrapper.classes()).toContain('text-tiny')
    expect(wrapper.classes().some(c => c.includes('['))).toBe(false)
  })

  it.each<[Variant, string]>([
    ['neutral', 'bg-surface-soft'],
    ['primary', 'bg-primary-soft'],
    ['accent', 'bg-accent-soft'],
    ['success', 'bg-success-soft'],
    ['warning', 'bg-warning-soft'],
    ['danger', 'bg-danger-soft'],
    ['info', 'bg-info-soft'],
  ])('applique la classe de fond pour la variante %s', (variant, expectedClass) => {
    const wrapper = mount(BaseBadge, { props: { variant } })
    expect(wrapper.classes()).toContain(expectedClass)
  })
})
