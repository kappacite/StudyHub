import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseEmptyState from '../../../../src/components/ui/base/BaseEmptyState.vue'

describe('BaseEmptyState', () => {
  it('affiche le titre en police display', () => {
    const wrapper = mount(BaseEmptyState, { props: { title: 'Aucune fiche à réviser' } })
    expect(wrapper.text()).toContain('Aucune fiche à réviser')
    expect(wrapper.html()).toContain('font-display')
  })

  it('affiche la description quand fournie', () => {
    const wrapper = mount(BaseEmptyState, { props: { title: 'X', description: 'Ajoutez votre premier deck.' } })
    expect(wrapper.text()).toContain('Ajoutez votre premier deck.')
  })

  it('affiche l\'icône dans un cercle en pointillés quand le slot icon est fourni', () => {
    const wrapper = mount(BaseEmptyState, {
      props: { title: 'X' },
      slots: { icon: '<svg data-test="icone" />' },
    })
    const holder = wrapper.find('[data-test="icone"]').element.parentElement
    expect(holder?.className).toContain('rounded-full')
    expect(holder?.className).toContain('border-dashed')
  })

  it('masque le conteneur d\'icône quand le slot icon est absent', () => {
    const wrapper = mount(BaseEmptyState, { props: { title: 'X' } })
    expect(wrapper.find('.border-dashed').exists()).toBe(false)
  })

  it('affiche les actions quand le slot actions est fourni', () => {
    const wrapper = mount(BaseEmptyState, {
      props: { title: 'X' },
      slots: { actions: '<button>Créer un deck</button>' },
    })
    expect(wrapper.text()).toContain('Créer un deck')
  })
})
