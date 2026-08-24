import { describe, it, expect, afterEach } from 'vitest'
import { mount, type VueWrapper } from '@vue/test-utils'
import BaseModal from '../../../../src/components/ui/base/BaseModal.vue'

let wrapper: VueWrapper<any> | undefined

afterEach(() => {
  wrapper?.unmount()
  wrapper = undefined
})

describe('BaseModal', () => {
  it("n'affiche pas le dialogue quand open est faux", () => {
    wrapper = mount(BaseModal, { props: { open: false }, attachTo: document.body })
    expect(document.body.querySelector('[role="dialog"]')).toBeNull()
  })

  it('affiche le dialogue et le titre en police display quand open est vrai', async () => {
    wrapper = mount(BaseModal, {
      props: { open: true, title: 'Confirmer la suppression' },
      attachTo: document.body,
    })
    await wrapper.vm.$nextTick()
    expect(document.body.querySelector('[role="dialog"]')).not.toBeNull()
    expect(document.body.textContent).toContain('Confirmer la suppression')
    expect(document.body.querySelector('.font-display')).not.toBeNull()
  })

  it('émet close au clic sur le bouton de fermeture', async () => {
    wrapper = mount(BaseModal, { props: { open: true, title: 'X' }, attachTo: document.body })
    await wrapper.vm.$nextTick()
    const closeButton = document.body.querySelector('[role="dialog"] button')
    closeButton?.click()
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('applique la classe de taille correspondant à la prop size', async () => {
    wrapper = mount(BaseModal, { props: { open: true, size: 'lg' }, attachTo: document.body })
    await wrapper.vm.$nextTick()
    expect(document.body.querySelector('.max-w-lg')).not.toBeNull()
  })

  it('affiche le pied de page quand le slot footer est fourni', async () => {
    wrapper = mount(BaseModal, {
      props: { open: true },
      slots: { footer: '<button>OK</button>' },
      attachTo: document.body,
    })
    await wrapper.vm.$nextTick()
    expect(document.body.textContent).toContain('OK')
  })
})
