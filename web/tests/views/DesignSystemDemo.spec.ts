import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DesignSystemDemo from '../../src/views/Dev/DesignSystemDemo.vue'

describe('DesignSystemDemo', () => {
  it('bascule la classe "dark" sur <html> au clic sur le bouton de thème', async () => {
    document.documentElement.classList.remove('dark')
    const wrapper = mount(DesignSystemDemo)
    const toggle = wrapper.find('[data-test="toggle-theme"]')
    expect(toggle.exists()).toBe(true)

    await toggle.trigger('click')
    expect(document.documentElement.classList.contains('dark')).toBe(true)

    await toggle.trigger('click')
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('affiche au moins un exemple de chacune des 10 primitives de la checklist phase 3', () => {
    const wrapper = mount(DesignSystemDemo)
    // Un marqueur data-demo par section suffit à garantir qu'aucune n'a été oubliée.
    for (const name of ['bouton', 'champ', 'carte', 'modale', 'onglet', 'badge', 'info-bulle', 'etat-vide', 'squelette', 'toast']) {
      expect(wrapper.find(`[data-demo="${name}"]`).exists()).toBe(true)
    }
  })
})
