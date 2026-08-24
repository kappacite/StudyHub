import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseModal from '../../../../src/components/ui/base/BaseModal.vue'

describe('BaseModal', () => {
  it("n'affiche pas le dialogue quand open est faux", () => {
    const wrapper = mount(BaseModal, { props: { open: false } })
    expect(wrapper.find('[role="dialog"]').exists()).toBe(false)
  })

  it('affiche le dialogue et le titre en police display quand open est vrai', async () => {
    const wrapper = mount(BaseModal, { props: { open: true, title: 'Confirmer la suppression' } })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('[role="dialog"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Confirmer la suppression')
    expect(wrapper.html()).toContain('font-display')
  })

  it('émet close au clic sur le bouton de fermeture', async () => {
    const wrapper = mount(BaseModal, { props: { open: true, title: 'X' } })
    await wrapper.vm.$nextTick()
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('applique la classe de taille correspondant à la prop size', async () => {
    const wrapper = mount(BaseModal, { props: { open: true, size: 'lg' } })
    await wrapper.vm.$nextTick()
    expect(wrapper.html()).toContain('max-w-lg')
  })

  it('affiche le pied de page quand le slot footer est fourni', async () => {
    const wrapper = mount(BaseModal, {
      props: { open: true },
      slots: { footer: '<button>OK</button>' },
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('OK')
  })
})
