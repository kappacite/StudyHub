import { describe, it, expect, afterEach } from 'vitest'
import { mount, type VueWrapper } from '@vue/test-utils'

import NoteEditHelpModal from '../../../src/components/notes/NoteEditHelpModal.vue'

describe('NoteEditHelpModal', () => {
  let wrapper: VueWrapper | undefined

  afterEach(() => {
    wrapper?.unmount()
    wrapper = undefined
  })

  it("affiche le titre du guide et le contenu d'aide (placeholders, split-screen)", async () => {
    wrapper = mount(NoteEditHelpModal, { attachTo: document.body })
    await wrapper.vm.$nextTick()

    expect(document.body.textContent).toContain("Guide d'utilisation StudyHub")
    expect(document.body.textContent).toContain('Syntaxes de Révision Intégrée')
    expect(document.body.textContent).toContain('Écran Partagé & Liaisons PDF')
    expect(document.body.textContent).toContain("Masques d'Image (Occlusion)")
    expect(document.body.textContent).toContain('Tableaux & sauts de ligne')
  })

  it('emet close au clic sur le bouton de fermeture (croix du header)', async () => {
    wrapper = mount(NoteEditHelpModal, { attachTo: document.body })
    await wrapper.vm.$nextTick()

    const closeButton = document.body.querySelector(
      '[role="dialog"] button:not([aria-hidden])',
    ) as HTMLButtonElement
    closeButton?.click()
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('emet close au clic sur le bouton "Compris !"', async () => {
    wrapper = mount(NoteEditHelpModal, { attachTo: document.body })
    await wrapper.vm.$nextTick()

    const buttons = Array.from(document.body.querySelectorAll('button'))
    const confirmButton = buttons.find((b) => b.textContent?.trim() === 'Compris !')
    confirmButton?.click()
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('close')).toBeTruthy()
  })
})
