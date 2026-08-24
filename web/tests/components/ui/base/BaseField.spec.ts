import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseField from '../../../../src/components/ui/base/BaseField.vue'

describe('BaseField', () => {
  it('affiche le label en majuscules (fiche bristol) quand fourni', () => {
    const wrapper = mount(BaseField, { props: { label: 'Adresse email' } })
    const label = wrapper.find('label')
    expect(label.text()).toContain('Adresse email')
    expect(label.classes()).toContain('uppercase')
    expect(label.classes()).toContain('text-ink-muted')
  })

  it("n'affiche pas de label quand non fourni", () => {
    const wrapper = mount(BaseField)
    expect(wrapper.find('label').exists()).toBe(false)
  })

  it('affiche l\'astérisque quand required est vrai', () => {
    const wrapper = mount(BaseField, { props: { label: 'Nom', required: true } })
    expect(wrapper.find('label').text()).toContain('*')
  })

  it("affiche le message d'erreur en priorité sur l'indice", () => {
    const wrapper = mount(BaseField, { props: { error: 'Champ requis', hint: 'Indice' } })
    expect(wrapper.text()).toContain('Champ requis')
    expect(wrapper.text()).not.toContain('Indice')
  })

  it('affiche l\'indice quand seul hint est fourni', () => {
    const wrapper = mount(BaseField, { props: { hint: 'Format attendu : jj/mm/aaaa' } })
    expect(wrapper.text()).toContain('Format attendu')
  })

  it('rend le contenu du slot par défaut', () => {
    const wrapper = mount(BaseField, {
      slots: { default: '<input data-test="champ" />' },
    })
    expect(wrapper.find('[data-test="champ"]').exists()).toBe(true)
  })
})
