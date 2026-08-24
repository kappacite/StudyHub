import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseToast from '../../../../src/components/ui/base/BaseToast.vue'

type Variant = 'info' | 'success' | 'warning' | 'danger'

describe('BaseToast', () => {
  it('affiche le message fourni en prop', () => {
    const wrapper = mount(BaseToast, { props: { message: 'Deck enregistré.' } })
    expect(wrapper.text()).toContain('Deck enregistré.')
  })

  it('affiche le titre quand fourni', () => {
    const wrapper = mount(BaseToast, { props: { title: 'Enregistré', message: 'Deck mis à jour.' } })
    expect(wrapper.text()).toContain('Enregistré')
  })

  it.each<[Variant, string]>([
    ['info', 'bg-info-soft'],
    ['success', 'bg-success-soft'],
    ['warning', 'bg-warning-soft'],
    ['danger', 'bg-danger-soft'],
  ])('applique la classe de fond pour la variante %s', (variant, expectedClass) => {
    const wrapper = mount(BaseToast, { props: { variant, message: 'X' } })
    expect(wrapper.classes()).toContain(expectedClass)
  })

  it('utilise info comme variante par défaut', () => {
    const wrapper = mount(BaseToast, { props: { message: 'X' } })
    expect(wrapper.classes()).toContain('bg-info-soft')
  })

  it('affiche le bouton de fermeture par défaut et émet close au clic', async () => {
    const wrapper = mount(BaseToast, { props: { message: 'X' } })
    const closeBtn = wrapper.find('button[aria-label="Fermer"]')
    expect(closeBtn.exists()).toBe(true)
    await closeBtn.trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('masque le bouton de fermeture quand closable est faux', () => {
    const wrapper = mount(BaseToast, { props: { message: 'X', closable: false } })
    expect(wrapper.find('button[aria-label="Fermer"]').exists()).toBe(false)
  })

  it('expose role="status" pour l\'accessibilité', () => {
    const wrapper = mount(BaseToast, { props: { message: 'X' } })
    expect(wrapper.attributes('role')).toBe('status')
  })
})
