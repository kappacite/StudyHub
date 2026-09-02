import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ListRow from '../../src/components/ui/base/ListRow.vue'

describe('ListRow', () => {
  it('affiche titre et sous-titre', () => {
    const wrapper = mount(ListRow, { props: { title: 'Chimie', subtitle: '12 cartes' } })
    expect(wrapper.text()).toContain('Chimie')
    expect(wrapper.text()).toContain('12 cartes')
  })

  it('rend un <button> quand as="button"', () => {
    const wrapper = mount(ListRow, { props: { as: 'button', title: 'X' } })
    expect(wrapper.element.tagName).toBe('BUTTON')
  })

  it('applique le style interactif (hover) quand interactive', () => {
    const wrapper = mount(ListRow, { props: { interactive: true, title: 'X' } })
    expect(wrapper.classes()).toContain('cursor-pointer')
  })

  it('rend les slots leading/trailing', () => {
    const wrapper = mount(ListRow, {
      slots: { leading: '<i class="lead" />', trailing: '<i class="trail" />' },
    })
    expect(wrapper.find('.lead').exists()).toBe(true)
    expect(wrapper.find('.trail').exists()).toBe(true)
  })

  // padding="cozy" (Task 5, bibliotheque-notes-listes) : lignes plus aérées, sans indent
  // horizontal (Notes.dc.html -- le retrait vient du padding de la carte englobante, pas
  // de la ligne elle-même). Défaut inchangé pour les autres consommateurs (ListRow.vue,
  // Accueil.vue, RevisionSetDetail.vue).
  it('applique px-3 py-2.5 par défaut, px-0 py-4 avec padding="cozy"', () => {
    const wrapper = mount(ListRow, { props: { title: 'X' } })
    expect(wrapper.classes()).toContain('px-3')
    expect(wrapper.classes()).toContain('py-2.5')

    const cozy = mount(ListRow, { props: { title: 'X', padding: 'cozy' } })
    expect(cozy.classes()).toContain('px-0')
    expect(cozy.classes()).toContain('py-4')
    expect(cozy.classes()).not.toContain('px-3')
    expect(cozy.classes()).not.toContain('py-2.5')
  })
})
