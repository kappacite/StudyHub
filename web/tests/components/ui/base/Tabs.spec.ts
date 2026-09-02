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

  // Variante "segmented" (Task 1, bibliotheque-notes-listes) : bascule 2 positions de
  // `Notes.dc.html` -- conteneur surélevé qui porte le fond et l'ombre, thumb à angles
  // adoucis à l'intérieur. La variante par défaut ("pills") ne bouge pas : Tabs est
  // partagé par ClassesLanding, TeacherDashboard, GroupDetail et DesignSystemDemo.
  describe('variante segmented', () => {
    it("pose le conteneur surélevé (fond, ombre, rayon 10px) au lieu du conteneur nu", () => {
      const wrapper = mount(Tabs, { props: { modelValue: 'teacher', tabs, variant: 'segmented' } })
      const root = wrapper.find('div')
      expect(root.classes()).toContain('bg-surface')
      expect(root.classes()).toContain('shadow-elev-1')
      expect(root.classes()).toContain('rounded-btn-primary')
    })

    it('rend des onglets à angles adoucis, pas des pilules', () => {
      const wrapper = mount(Tabs, { props: { modelValue: 'teacher', tabs, variant: 'segmented' } })
      const buttons = wrapper.findAll('button')
      expect(buttons[0].classes()).toContain('rounded-lg')
      expect(buttons[0].classes()).not.toContain('rounded-full')
    })

    it("marque l'onglet actif comme thumb plein et laisse l'inactif transparent", () => {
      const wrapper = mount(Tabs, { props: { modelValue: 'teacher', tabs, variant: 'segmented' } })
      const buttons = wrapper.findAll('button')
      expect(buttons[0].classes()).toContain('bg-primary')
      expect(buttons[0].classes()).toContain('text-primary-ink')
      expect(buttons[1].classes()).not.toContain('bg-primary')
    })

    it('respecte la cible tactile minimale de 44px', () => {
      const wrapper = mount(Tabs, { props: { modelValue: 'teacher', tabs, variant: 'segmented' } })
      expect(wrapper.findAll('button')[0].classes()).toContain('min-h-11')
    })

    it('émet toujours update:modelValue au clic', async () => {
      const wrapper = mount(Tabs, { props: { modelValue: 'teacher', tabs, variant: 'segmented' } })
      await wrapper.findAll('button')[1].trigger('click')
      expect(wrapper.emitted('update:modelValue')![0]).toEqual(['groups'])
    })
  })

  it("garde le conteneur nu sur la variante par défaut (non-régression des 4 autres écrans)", () => {
    const wrapper = mount(Tabs, { props: { modelValue: 'teacher', tabs } })
    const root = wrapper.find('div')
    expect(root.classes()).not.toContain('bg-surface')
    expect(root.classes()).not.toContain('shadow-elev-1')
  })
})
