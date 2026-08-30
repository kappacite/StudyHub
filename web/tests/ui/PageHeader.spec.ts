import { describe, it, expect } from 'vitest'
import { mount, RouterLinkStub } from '@vue/test-utils'
import PageHeader from '../../src/components/ui/base/PageHeader.vue'

const global = { stubs: { 'router-link': RouterLinkStub } }

describe('PageHeader', () => {
  it('affiche titre et sous-titre', () => {
    const wrapper = mount(PageHeader, { props: { title: 'Réviser', subtitle: 'Tout en un' }, global })
    expect(wrapper.find('h1').text()).toBe('Réviser')
    expect(wrapper.text()).toContain('Tout en un')
  })

  it('rend le fil d’Ariane avec un lien sur les éléments non terminaux', () => {
    const wrapper = mount(PageHeader, {
      props: {
        title: 'Sous-dossier',
        breadcrumbs: [
          { label: 'Bibliothèque', to: '/bibliotheque' },
          { label: 'Sciences' },
        ],
      },
      global,
    })
    const links = wrapper.findAllComponents(RouterLinkStub)
    expect(links).toHaveLength(1)
    expect(links[0].props('to')).toBe('/bibliotheque')
    expect(wrapper.text()).toContain('Sciences')
  })

  it('rend les slots actions et tabs', () => {
    const wrapper = mount(PageHeader, {
      props: { title: 'X' },
      slots: { actions: '<button class="cta">Go</button>', tabs: '<div class="tabz" />' },
      global,
    })
    expect(wrapper.find('.cta').exists()).toBe(true)
    expect(wrapper.find('.tabz').exists()).toBe(true)
  })

  it('permet aux actions de passer à la ligne sur mobile plutôt que de déborder', () => {
    const wrapper = mount(PageHeader, {
      props: { title: 'Classeur' },
      slots: {
        actions: `
          <button class="a1">Stats</button>
          <button class="a2">Partager</button>
          <button class="a3">Classe</button>
          <button class="a4">Réviser ce dossier</button>
          <button class="a5">Ajouter</button>
          <button class="a6">Supprimer</button>
        `,
      },
      global,
    })
    const actionsContainer = wrapper.find('.a1').element.parentElement as HTMLElement
    expect(actionsContainer.className).toContain('flex-wrap')
  })
})
