import { describe, it, expect, afterEach } from 'vitest'
import { mount, type VueWrapper } from '@vue/test-utils'
import { nextTick } from 'vue'

import NoteEvaluationModal from '../../../src/components/notes/NoteEvaluationModal.vue'

describe('NoteEvaluationModal', () => {
  let wrapper: VueWrapper | undefined

  afterEach(() => {
    wrapper?.unmount()
    wrapper = undefined
  })

  it('affiche le titre et les 4 boutons de notation SM-2 lorsque visible', async () => {
    wrapper = mount(NoteEvaluationModal, {
      attachTo: document.body,
      props: { visible: true },
    })
    await nextTick()

    expect(document.body.textContent).toContain("C'était facile ?")
    expect(document.body.textContent).toContain('À revoir')
    expect(document.body.textContent).toContain('Difficile')
    expect(document.body.textContent).toContain('Correct')
    expect(document.body.textContent).toContain('Facile')
  })

  it("n'affiche rien lorsque visible est false", async () => {
    wrapper = mount(NoteEvaluationModal, {
      attachTo: document.body,
      props: { visible: false },
    })
    await nextTick()

    expect(document.body.querySelector('[role="dialog"]')).toBeFalsy()
  })

  it('émet evaluate avec la note (score SM-2) correspondant au bouton cliqué', async () => {
    wrapper = mount(NoteEvaluationModal, {
      attachTo: document.body,
      props: { visible: true },
    })
    await nextTick()

    const buttons = Array.from(document.body.querySelectorAll('button'))
    const facile = buttons.find((b) => b.textContent?.includes('Facile')) as HTMLButtonElement
    facile.click()
    await nextTick()

    expect(wrapper.emitted('evaluate')).toBeTruthy()
    expect(wrapper.emitted('evaluate')![0]).toEqual([5])
  })

  it('émet cancel au clic sur "Passer sans évaluer"', async () => {
    wrapper = mount(NoteEvaluationModal, {
      attachTo: document.body,
      props: { visible: true },
    })
    await nextTick()

    const buttons = Array.from(document.body.querySelectorAll('button'))
    const passer = buttons.find((b) => b.textContent?.trim() === 'Passer sans évaluer')
    passer?.click()
    await nextTick()

    expect(wrapper.emitted('cancel')).toBeTruthy()
  })

  it('désactive les boutons de notation lorsque isEvaluating est vrai', async () => {
    wrapper = mount(NoteEvaluationModal, {
      attachTo: document.body,
      props: { visible: true, isEvaluating: true },
    })
    await nextTick()

    const buttons = Array.from(document.body.querySelectorAll('button'))
    const facile = buttons.find((b) => b.textContent?.includes('Facile')) as HTMLButtonElement
    expect(facile.disabled).toBe(true)
  })
})
