import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Tabs from '../../src/components/ui/base/Tabs.vue'

const tabs = [
  { key: 'a', label: 'Alpha' },
  { key: 'b', label: 'Beta', badge: 3 },
]

describe('Tabs', () => {
  it('affiche tous les onglets et leur badge', () => {
    const wrapper = mount(Tabs, { props: { modelValue: 'a', tabs } })
    expect(wrapper.text()).toContain('Alpha')
    expect(wrapper.text()).toContain('Beta')
    expect(wrapper.text()).toContain('3')
  })

  it("marque l'onglet actif avec la surface élevée", () => {
    const wrapper = mount(Tabs, { props: { modelValue: 'a', tabs } })
    const active = wrapper.findAll('button')[0]
    expect(active.classes()).toContain('bg-surface')
    expect(active.classes()).toContain('text-primary')
  })

  it("émet update:modelValue avec la clé au clic", async () => {
    const wrapper = mount(Tabs, { props: { modelValue: 'a', tabs } })
    await wrapper.findAll('button')[1].trigger('click')
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['b'])
  })
})
