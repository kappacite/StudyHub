import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Tabs from '../../../../src/components/ui/base/Tabs.vue'

const tabs = [
  { key: 'teacher', label: 'Enseignant' },
  { key: 'groups', label: 'Groupes', badge: 3 },
]

describe('Tabs', () => {
  it('affiche tous les onglets fournis', () => {
    const wrapper = mount(Tabs, { props: { modelValue: 'teacher', tabs } })
    expect(wrapper.text()).toContain('Enseignant')
    expect(wrapper.text()).toContain('Groupes')
  })

  it('marque l\'onglet actif en pilule pleine indigo (fond primary, texte primary-ink)', () => {
    const wrapper = mount(Tabs, { props: { modelValue: 'teacher', tabs } })
    const buttons = wrapper.findAll('button')
    expect(buttons[0].classes()).toContain('bg-primary')
    expect(buttons[0].classes()).toContain('text-primary-ink')
    expect(buttons[0].classes()).toContain('rounded-full')
    expect(buttons[1].classes()).not.toContain('bg-primary')
  })

  it('émet update:modelValue avec la clé au clic', async () => {
    const wrapper = mount(Tabs, { props: { modelValue: 'teacher', tabs } })
    await wrapper.findAll('button')[1].trigger('click')
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['groups'])
  })

  it('affiche le badge avec le token text-tiny quand fourni et non vide', () => {
    const wrapper = mount(Tabs, { props: { modelValue: 'teacher', tabs } })
    const badge = wrapper.findAll('button')[1].find('span')
    expect(badge.exists()).toBe(true)
    expect(badge.text()).toBe('3')
    expect(badge.classes()).toContain('text-tiny')
  })

  it('masque le badge quand il vaut null/undefined/chaîne vide', () => {
    const wrapper = mount(Tabs, { props: { modelValue: 'teacher', tabs: [{ key: 'a', label: 'A' }] } })
    expect(wrapper.find('button span').exists()).toBe(false)
  })
})
