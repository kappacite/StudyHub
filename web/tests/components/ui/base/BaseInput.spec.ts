import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseInput from '../../../../src/components/ui/base/BaseInput.vue'

describe('BaseInput', () => {
  it('applique la valeur modelValue', () => {
    const wrapper = mount(BaseInput, { props: { modelValue: 'Chimie' } })
    expect((wrapper.find('input').element as HTMLInputElement).value).toBe('Chimie')
  })

  it('émet update:modelValue à la saisie', async () => {
    const wrapper = mount(BaseInput)
    await wrapper.find('input').setValue('Droit constitutionnel')
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['Droit constitutionnel'])
  })

  it('applique le rayon 8px et le fond surface (pas surface-soft)', () => {
    const wrapper = mount(BaseInput)
    const input = wrapper.find('input')
    expect(input.classes()).toContain('rounded-lg')
    expect(input.classes()).toContain('bg-surface')
  })

  it('décale le padding et affiche l\'icône quand le slot icon est fourni', () => {
    const wrapper = mount(BaseInput, { slots: { icon: '<svg data-test="icone" />' } })
    expect(wrapper.find('[data-test="icone"]').exists()).toBe(true)
    expect(wrapper.find('input').classes()).toContain('pl-11')
  })

  it('désactive l\'input quand disabled est vrai', () => {
    const wrapper = mount(BaseInput, { props: { disabled: true } })
    expect(wrapper.find('input').attributes('disabled')).toBeDefined()
  })

  it('utilise "text" comme type par défaut', () => {
    const wrapper = mount(BaseInput)
    expect(wrapper.find('input').attributes('type')).toBe('text')
  })
})
