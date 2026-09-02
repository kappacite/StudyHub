import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseCard from '../../../../src/components/ui/base/BaseCard.vue'

describe('BaseCard', () => {
  it('rend le contenu du slot', () => {
    const wrapper = mount(BaseCard, { slots: { default: 'Contenu' } })
    expect(wrapper.text()).toContain('Contenu')
  })

  it('applique le rayon 8px et l\'ombre de carte par défaut', () => {
    const wrapper = mount(BaseCard)
    expect(wrapper.classes()).toContain('rounded-lg')
    expect(wrapper.classes()).toContain('shadow-elev-1')
  })

  it('applique le padding md par défaut', () => {
    const wrapper = mount(BaseCard)
    expect(wrapper.classes()).toContain('p-6')
  })

  it('applique le tag HTML donné via la prop as', () => {
    const wrapper = mount(BaseCard, { props: { as: 'article' } })
    expect(wrapper.element.tagName).toBe('ARTICLE')
  })

  it('ajoute les classes d\'interactivité seulement quand interactive est vrai', () => {
    const wrapper = mount(BaseCard, { props: { interactive: true } })
    expect(wrapper.classes()).toContain('hover:shadow-elev-2')
    const flat = mount(BaseCard)
    expect(flat.classes()).not.toContain('hover:shadow-elev-2')
  })

  // radius="bristol" (Task 4, bibliotheque-notes-listes) : rayon 4px des "bandeaux fiche
  // bristol" (skill design-system, § Rayons) -- BinderCard.vue en est le premier
  // consommateur. Défaut inchangé pour les 22 autres consommateurs de BaseCard.
  it('applique rounded-lg par défaut, rounded avec radius="bristol"', () => {
    const wrapper = mount(BaseCard)
    expect(wrapper.classes()).toContain('rounded-lg')

    const bristol = mount(BaseCard, { props: { radius: 'bristol' } })
    expect(bristol.classes()).toContain('rounded')
    expect(bristol.classes()).not.toContain('rounded-lg')
  })
})
