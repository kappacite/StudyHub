import { describe, it, expect, afterEach } from 'vitest'
import { mount, type VueWrapper } from '@vue/test-utils'
import { nextTick } from 'vue'
import { BookOpen } from '@lucide/vue'

import NoteInputModal, { type ModalField } from '../../../src/components/notes/NoteInputModal.vue'

describe('NoteInputModal', () => {
  let wrapper: VueWrapper | undefined

  afterEach(() => {
    wrapper?.unmount()
    wrapper = undefined
  })

  function textFields(): ModalField[] {
    return [
      { type: 'text', label: 'Définition', value: '', placeholder: 'Entrez la définition...' },
    ]
  }

  it('affiche le titre, la description et le champ texte fourni en props', async () => {
    wrapper = mount(NoteInputModal, {
      attachTo: document.body,
      props: {
        visible: true,
        title: 'Définition info-bulle',
        description: 'Associer une définition au terme sélectionné : « photosynthèse »',
        icon: BookOpen,
        iconBg: 'bg-emerald-500',
        confirmLabel: 'Ajouter la définition',
        fields: textFields(),
      },
    })
    await nextTick()

    expect(document.body.textContent).toContain('Définition info-bulle')
    expect(document.body.textContent).toContain(
      'Associer une définition au terme sélectionné : « photosynthèse »',
    )
    expect(document.body.textContent).toContain('Définition')
    const input = document.body.querySelector('input[placeholder="Entrez la définition..."]')
    expect(input).toBeTruthy()
  })

  it('émet update:fields avec la nouvelle valeur lors de la saisie dans un champ texte', async () => {
    wrapper = mount(NoteInputModal, {
      attachTo: document.body,
      props: {
        visible: true,
        title: 'Définition info-bulle',
        icon: BookOpen,
        fields: textFields(),
      },
    })
    await nextTick()

    const input = document.body.querySelector('input') as HTMLInputElement
    input.value = 'Processus de conversion de la lumière en énergie chimique'
    input.dispatchEvent(new Event('input'))
    await nextTick()

    const emitted = wrapper.emitted('update:fields')
    expect(emitted).toBeTruthy()
    const lastPayload = emitted![emitted!.length - 1][0] as ModalField[]
    expect(lastPayload[0].value).toBe('Processus de conversion de la lumière en énergie chimique')
  })

  it('émet confirm sur Entrée et cancel sur Échap depuis le champ texte', async () => {
    wrapper = mount(NoteInputModal, {
      attachTo: document.body,
      props: {
        visible: true,
        title: 'Définition info-bulle',
        icon: BookOpen,
        fields: textFields(),
      },
    })
    await nextTick()

    const input = document.body.querySelector('input') as HTMLInputElement
    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }))
    await nextTick()
    expect(wrapper.emitted('confirm')).toBeTruthy()

    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    await nextTick()
    expect(wrapper.emitted('cancel')).toBeTruthy()
  })

  it('affiche un champ booléen et émet la valeur choisie au clic', async () => {
    wrapper = mount(NoteInputModal, {
      attachTo: document.body,
      props: {
        visible: true,
        title: 'Vrai / Faux',
        icon: BookOpen,
        fields: [{ type: 'bool', label: 'Cette assertion est...', value: true }] as ModalField[],
      },
    })
    await nextTick()

    const buttons = Array.from(document.body.querySelectorAll('button'))
    const faux = buttons.find((b) => b.textContent?.trim() === '✗ Faux') as HTMLButtonElement
    faux.click()
    await nextTick()

    const emitted = wrapper.emitted('update:fields')
    expect(emitted).toBeTruthy()
    const lastPayload = emitted![emitted!.length - 1][0] as ModalField[]
    expect(lastPayload[0].value).toBe(false)
  })

  it('affiche un champ select et préserve le type numérique de la valeur choisie', async () => {
    wrapper = mount(NoteInputModal, {
      attachTo: document.body,
      props: {
        visible: true,
        title: 'Insérer un diagramme',
        icon: BookOpen,
        fields: [
          {
            type: 'select',
            label: 'Diagramme',
            value: 1,
            options: [
              { value: 1, label: 'Anatomie du cœur' },
              { value: 2, label: 'Cycle de Krebs' },
            ],
          },
        ] as ModalField[],
      },
    })
    await nextTick()

    const select = document.body.querySelector('select') as HTMLSelectElement
    select.value = '2'
    select.dispatchEvent(new Event('change'))
    await nextTick()

    const emitted = wrapper.emitted('update:fields')
    expect(emitted).toBeTruthy()
    const lastPayload = emitted![emitted!.length - 1][0] as ModalField[]
    expect(lastPayload[0].value).toBe(2)
    expect(typeof lastPayload[0].value).toBe('number')
  })

  it('émet cancel au clic sur "Annuler" et confirm au clic sur le bouton de confirmation', async () => {
    wrapper = mount(NoteInputModal, {
      attachTo: document.body,
      props: {
        visible: true,
        title: 'Créer un QCM',
        icon: BookOpen,
        confirmLabel: 'Créer le QCM',
        fields: textFields(),
      },
    })
    await nextTick()

    const buttons = Array.from(document.body.querySelectorAll('button'))
    const cancelButton = buttons.find(
      (b) => b.textContent?.trim() === 'Annuler',
    ) as HTMLButtonElement
    cancelButton.click()
    await nextTick()
    expect(wrapper.emitted('cancel')).toBeTruthy()

    const confirmButton = buttons.find(
      (b) => b.textContent?.trim() === 'Créer le QCM',
    ) as HTMLButtonElement
    confirmButton.click()
    await nextTick()
    expect(wrapper.emitted('confirm')).toBeTruthy()
  })

  it('utilise le libellé de confirmation par défaut "Confirmer" si non fourni', async () => {
    wrapper = mount(NoteInputModal, {
      attachTo: document.body,
      props: {
        visible: true,
        title: 'Sélection requise',
        icon: BookOpen,
        fields: [],
      },
    })
    await nextTick()

    expect(document.body.textContent).toContain('Confirmer')
  })

  it('n’affiche rien lorsque visible est false', async () => {
    wrapper = mount(NoteInputModal, {
      attachTo: document.body,
      props: {
        visible: false,
        title: 'Créer un QCM',
        icon: BookOpen,
        fields: textFields(),
      },
    })
    await nextTick()

    expect(document.body.querySelector('[role="dialog"]')).toBeFalsy()
  })
})
