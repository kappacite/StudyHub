import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseButton from '../../../../src/components/ui/base/BaseButton.vue'

describe('BaseButton', () => {
  it('affiche le contenu du slot par défaut', () => {
    const wrapper = mount(BaseButton, { slots: { default: 'Valider' } })
    expect(wrapper.text()).toContain('Valider')
  })

  it('applique le rayon 10px et le fond indigo pour la variante primary par défaut', () => {
    const wrapper = mount(BaseButton, { slots: { default: 'OK' } })
    expect(wrapper.classes()).toContain('rounded-btn-primary')
    expect(wrapper.classes()).toContain('bg-primary')
    expect(wrapper.classes()).toContain('text-primary-ink')
  })

  it('applique un rayon de 8px et un contour transparent pour la variante danger', () => {
    const wrapper = mount(BaseButton, { props: { variant: 'danger' }, slots: { default: 'Supprimer' } })
    expect(wrapper.classes()).toContain('rounded-lg')
    expect(wrapper.classes()).toContain('border-danger')
    expect(wrapper.classes()).toContain('bg-transparent')
  })

  it('désactive le bouton quand disabled est vrai', () => {
    const wrapper = mount(BaseButton, { props: { disabled: true }, slots: { default: 'X' } })
    expect(wrapper.attributes('disabled')).toBeDefined()
  })

  it('désactive le bouton et affiche le spinner quand loading est vrai', () => {
    const wrapper = mount(BaseButton, { props: { loading: true }, slots: { default: 'X' } })
    expect(wrapper.attributes('disabled')).toBeDefined()
    expect(wrapper.find('svg.animate-spin').exists()).toBe(true)
  })

  it('applique la largeur pleine quand block est vrai', () => {
    const wrapper = mount(BaseButton, { props: { block: true }, slots: { default: 'X' } })
    expect(wrapper.classes()).toContain('w-full')
  })

  it('déclenche un click natif quand activé', async () => {
    const wrapper = mount(BaseButton, { slots: { default: 'X' } })
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })
})
