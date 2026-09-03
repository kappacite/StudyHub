import { describe, it, expect, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import NoteGradeModal from '../../../src/components/notes/NoteGradeModal.vue'

describe('NoteGradeModal — notes-ia-planning-corrections Task 5', () => {
  // BaseModal (headlessui Dialog/TransitionRoot) rend son contenu teleporte
  // (document.body) de façon asynchrone -- un nextTick est necessaire apres mount,
  // meme idiome que RevisionSetModal.spec.ts. Vidage explicite entre tests pour
  // eviter qu'un test lise le contenu teleporte d'un test precedent.
  afterEach(() => {
    document.body.innerHTML = ''
  })

  it('affiche un etat de chargement quand loading=true', async () => {
    const wrapper = mount(NoteGradeModal, {
      props: { open: true, loading: true, error: null, result: null },
      attachTo: document.body,
    })
    await wrapper.vm.$nextTick()
    expect(document.body.textContent).toContain('Notation en cours')
    wrapper.unmount()
  })

  it('affiche le score /10 (une decimale), le verdict, points forts/ameliorations et les suggestions', async () => {
    const wrapper = mount(NoteGradeModal, {
      props: {
        open: true,
        loading: false,
        error: null,
        result: {
          score: 82,
          verdict: 'Note solide et bien structurée.',
          points_forts: ['Définitions claires', 'Exemples pertinents'],
          ameliorations: ['Manque un schéma récapitulatif'],
          suggestions: 'Ajouter un résumé en tête de note.',
        },
      },
      attachTo: document.body,
    })
    await wrapper.vm.$nextTick()
    expect(document.body.textContent).toContain('8,2')
    expect(document.body.textContent).toContain('Note solide et bien structurée.')
    expect(document.body.textContent).toContain('Définitions claires')
    expect(document.body.textContent).toContain('Manque un schéma récapitulatif')
    expect(document.body.textContent).toContain('Ajouter un résumé en tête de note.')
    wrapper.unmount()
  })

  it("affiche un message d'erreur si error est renseigne", async () => {
    const wrapper = mount(NoteGradeModal, {
      props: { open: true, loading: false, error: 'Clé Gemini manquante.', result: null },
      attachTo: document.body,
    })
    await wrapper.vm.$nextTick()
    expect(document.body.textContent).toContain('Clé Gemini manquante.')
    wrapper.unmount()
  })

  it('emet close au clic sur le bouton de fermeture', async () => {
    const wrapper = mount(NoteGradeModal, {
      props: { open: true, loading: false, error: null, result: null },
      attachTo: document.body,
    })
    await wrapper.vm.$nextTick()
    const closeBtn = Array.from(document.body.querySelectorAll('button')).find(
      (b) => b.textContent?.trim() === 'Fermer',
    )
    closeBtn!.click()
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('close')).toBeTruthy()
    wrapper.unmount()
  })
})
