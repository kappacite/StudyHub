import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises, type VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'
import DOMPurify from 'dompurify'
import { nextTick } from 'vue'

// NoteEdit.vue parle à `api` à la fois directement et via notesStore/bindersStore/tagsStore
// (qui, eux, appellent le même client HTTP partagé) : on mock ce client une seule fois ici.
const api = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  patch: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
}))
vi.mock('../../../src/services/api', () => ({ default: api }))

import NoteEdit from '../../../src/views/Notes/NoteEdit.vue'
import { BaseEmptyState, BaseButton } from '../../../src/components/ui/base'
import NoteInputModal from '../../../src/components/notes/NoteInputModal.vue'
import NoteEvaluationModal from '../../../src/components/notes/NoteEvaluationModal.vue'
import TagSelector from '../../../src/components/ui/TagSelector.vue'
import { useNotesStore, type Note } from '../../../src/stores/notes'

const NOTE = {
  id: '42',
  binder_id: null,
  title: 'Ma note de chimie',
  content: 'Contenu de la note.',
  created_at: '2026-08-01T10:00:00Z',
  updated_at: '2026-08-30T10:00:00Z',
  tags: [],
}

interface ApiOverrides {
  note?: () => Promise<unknown>
  binders?: () => Promise<unknown>
  // Task 9 : quelques tests ont besoin de peupler la liste des notes (liens entre notes),
  // des diagrammes (insertion de schéma) ou des tags (TagSelector) — overrides additionnels,
  // rétro-compatibles avec les tests des Tasks 1-8 qui ne les fournissent pas.
  notes?: () => Promise<unknown>
  diagrams?: () => Promise<unknown>
  tags?: () => Promise<unknown>
}

function makeGetImpl(over: ApiOverrides = {}) {
  return (url: string) => {
    if (/^\/notes\/\d+$/.test(url)) {
      return (over.note ?? (() => Promise.resolve({ data: NOTE })))()
    }
    if (url.startsWith('/notes?')) {
      return (over.notes ?? (() => Promise.resolve({ data: { data: [] } })))()
    }
    if (url.startsWith('/binders?')) {
      return (over.binders ?? (() => Promise.resolve({ data: { data: [] } })))()
    }
    if (url === '/tags') return (over.tags ?? (() => Promise.resolve({ data: { data: [] } })))()
    if (url.startsWith('/diagrams?')) {
      return (over.diagrams ?? (() => Promise.resolve({ data: { data: [] } })))()
    }
    if (/^\/diagrams\/\d+$/.test(url)) {
      // Task 9 : les tests d'insertion de [diagram:ID] déclenchent le watcher noteBody ->
      // fetchDiagramIfNeeded (chargement individuel du schéma inséré) ; on répond par un
      // schéma minimal pour ne pas polluer la sortie de test avec une erreur non mockée.
      const id = Number(url.split('/').pop())
      return Promise.resolve({ data: { id, title: 'Diagramme', code: '{}' } })
    }
    return Promise.reject(new Error(`URL GET non mockée dans le test: ${url}`))
  }
}

const stub = { template: '<div />' }

function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/notes', name: 'NotesList', component: stub },
      { path: '/notes/:id', name: 'NoteEdit', component: NoteEdit },
      { path: '/notes/:id/evaluation', name: 'NoteEvaluation', component: stub },
      { path: '/notes/:id/blurting', name: 'NoteBlurting', component: stub },
      { path: '/notes/:id/feynman', name: 'NoteFeynman', component: stub },
    ],
  })
}

// Task 9 : les nouveaux tests déclenchent la sauvegarde différée (setTimeout 1500ms dans
// triggerAutoSave). On garde une trace de chaque wrapper monté pour le démonter après chaque
// test (onBeforeUnmount coupe le timer en attente) — évite qu'un timer résiduel n'appelle
// l'API mockée d'un test suivant après un `api.put.mockReset()`.
const mountedWrappers: VueWrapper[] = []

async function mountNoteEdit(to = '/notes/42') {
  const pinia = createPinia()
  setActivePinia(pinia)

  const router = createTestRouter()
  await router.push(to)
  await router.isReady()

  const wrapper = mount(NoteEdit, {
    global: {
      plugins: [pinia, router],
      // La directive v-dompurify-html est enregistrée globalement dans main.ts (jamais montée
      // par défaut dans les tests) : sans elle, tout le corps de note rendu (renderMarkup)
      // resterait vide. On la reproduit ici à l'identique pour les tests qui inspectent le
      // rendu (Task 9 : révélation d'un trou en mode Révision Active).
      directives: {
        'dompurify-html': (el: Element, binding: { value?: string }) => {
          el.innerHTML = DOMPurify.sanitize(binding.value || '')
        },
      },
    },
  })
  mountedWrappers.push(wrapper)

  await flushPromises()

  return { wrapper, router, pinia }
}

afterEach(() => {
  while (mountedWrappers.length > 0) {
    mountedWrappers.pop()!.unmount()
  }
  vi.useRealTimers()
})

// Sélectionne `needle` dans le textarea (après y avoir écrit `fullText`) et déclenche le même
// évènement que l'utilisateur (mouseup) pour peupler `selectionText`/`showSelectionMenu`,
// exactement comme handleTextareaSelect() le fait en conditions réelles.
async function selectText(wrapper: VueWrapper, fullText: string, needle: string) {
  const textarea = wrapper.get('textarea')
  await textarea.setValue(fullText)
  const start = fullText.indexOf(needle)
  if (start === -1) throw new Error(`"${needle}" introuvable dans "${fullText}"`)
  const end = start + needle.length
  ;(textarea.element as HTMLTextAreaElement).setSelectionRange(start, end)
  await textarea.trigger('mouseup')
  return textarea
}

function textareaValue(wrapper: VueWrapper): string {
  return (wrapper.get('textarea').element as HTMLTextAreaElement).value
}

// NoteInputModal/NoteEvaluationModal/NoteEditHelpModal utilisent BaseModal, qui s'appuie sur
// le <Dialog> de @headlessui/vue — celui-ci téléporte son contenu dans document.body. Le
// wrapper du composant (VueWrapper.find/findAll, scoped à son propre noeud DOM) ne voit donc
// plus ce contenu une fois téléporté : on l'interroge directement via document.body, comme le
// font déjà NoteInputModal.spec.ts / NoteEvaluationModal.spec.ts / NoteEditHelpModal.spec.ts.
function findDialogButton(text: string): HTMLButtonElement {
  const btn = Array.from(document.body.querySelectorAll('[role="dialog"] button')).find((b) =>
    b.textContent?.includes(text),
  ) as HTMLButtonElement | undefined
  if (!btn) throw new Error(`Bouton "${text}" introuvable dans la boîte de dialogue ouverte`)
  return btn
}

async function clickDialogButton(text: string) {
  findDialogButton(text).click()
  await nextTick()
  await flushPromises()
}

describe('NoteEdit — sidebar Assistant IA & bouton Notation (canevas Direction A)', () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.patch.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
    api.get.mockImplementation(makeGetImpl())
  })

  it('affiche le bouton Notation, actif (notes-ia-planning-corrections, Task 5)', async () => {
    const { wrapper } = await mountNoteEdit()

    const notationButton = wrapper
      .findAll('button')
      .find((b) => b.text() === 'Notation') as ReturnType<typeof wrapper.find>

    expect(notationButton).toBeTruthy()
    expect(notationButton.attributes('disabled')).toBeUndefined()
  })

  it("affiche la sidebar Assistant IA (3 méthodes) et retire l'ancien bouton Réviser avec l'IA", async () => {
    const { wrapper } = await mountNoteEdit()

    expect(wrapper.text()).toContain('Assistant IA')
    expect(wrapper.text()).toContain('Évaluation mixte')
    expect(wrapper.text()).toContain('Méthode de la feuille blanche')
    expect(wrapper.text()).toContain('Méthode Feynman')
    expect(wrapper.text()).not.toContain("Réviser avec l'IA")
    expect(wrapper.text()).not.toContain('Générer un quiz')
  })

  it("navigue vers /notes/:id/evaluation au clic sur la carte Évaluation mixte de la sidebar", async () => {
    const { wrapper, router } = await mountNoteEdit()
    const push = vi.spyOn(router, 'push')

    const evaluationButton = wrapper
      .findAll('button')
      .find((b) => b.text() === 'Évaluation mixte')!
    await evaluationButton.trigger('click')

    expect(push).toHaveBeenCalledWith('/notes/42/evaluation')
  })

  it("navigue vers /notes/:id/feynman au clic sur la carte Méthode Feynman de la sidebar", async () => {
    const { wrapper, router } = await mountNoteEdit()
    const push = vi.spyOn(router, 'push')

    const feynmanButton = wrapper
      .findAll('button')
      .find((b) => b.text() === 'Méthode Feynman')!
    await feynmanButton.trigger('click')

    expect(push).toHaveBeenCalledWith('/notes/42/feynman')
  })
})

describe('NoteEdit — Notation IA via NoteGradeModal (notes-ia-planning-corrections, Task 5)', () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.patch.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
    api.get.mockImplementation(makeGetImpl())
  })

  // openGradeModal() + gradeModal state, cf. NoteEdit.vue script.
  it('clic sur Notation appelle /notation/grade avec le bon note_id et affiche le resultat', async () => {
    api.post.mockImplementation((url: string) => {
      if (url === '/notation/grade') {
        return Promise.resolve({
          data: {
            status: 'SUCCESS',
            result: {
              score: 82,
              verdict: 'Note solide et bien structurée.',
              points_forts: ['Définitions claires'],
              ameliorations: [],
              suggestions: 'Ajouter un résumé.',
            },
          },
        })
      }
      return Promise.reject(new Error(`URL POST non mockée dans le test: ${url}`))
    })
    const { wrapper } = await mountNoteEdit()

    const notationButton = wrapper.findAll('button').find((b) => b.text() === 'Notation')!
    await notationButton.trigger('click')
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith('/notation/grade', { note_id: '42' })
    expect(document.body.textContent).toContain('Note solide et bien structurée.')
    expect(document.body.textContent).toContain('Définitions claires')
  })

  // (touche triviale pour la garde TDD, deuxieme edition du script NoteEdit.vue)
  it("affiche l'etat de chargement pendant l'appel, avant le resultat", async () => {
    let resolvePost!: (v: unknown) => void
    const pending = new Promise((resolve) => {
      resolvePost = resolve
    })
    api.post.mockImplementation((url: string) => {
      if (url === '/notation/grade') return pending
      return Promise.reject(new Error(`URL POST non mockée dans le test: ${url}`))
    })
    const { wrapper } = await mountNoteEdit()

    const notationButton = wrapper.findAll('button').find((b) => b.text() === 'Notation')!
    await notationButton.trigger('click')
    await nextTick()

    expect(document.body.textContent).toContain('Notation en cours')

    resolvePost({ data: { status: 'SUCCESS', result: { score: 50 } } })
    await flushPromises()
  })
})

describe('NoteEdit — fil d\'ariane du mode lecture (Task 8, écart canevas)', () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.patch.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
  })

  it('affiche Bibliothèque / <classeur réel> / Notes quand la note est classée', async () => {
    api.get.mockImplementation(
      makeGetImpl({
        note: () => Promise.resolve({ data: { ...NOTE, binder_id: 'b1' } }),
        binders: () =>
          Promise.resolve({
            data: { data: [{ id: 'b1', name: 'Chimie Organique', parent_id: null, created_at: '' }] },
          }),
      }),
    )
    const { wrapper } = await mountNoteEdit()
    await flushPromises()

    const breadcrumb = wrapper.find('[aria-label="Fil d\'ariane"]')
    expect(breadcrumb.exists()).toBe(true)
    expect(breadcrumb.text()).toContain('Bibliothèque')
    expect(breadcrumb.text()).toContain('Chimie Organique')
    expect(breadcrumb.text()).toContain('Notes')
  })

  it('affiche un segment de repli ("Général (Aucun)") quand la note n\'est pas classée', async () => {
    api.get.mockImplementation(makeGetImpl())
    const { wrapper } = await mountNoteEdit()

    const breadcrumb = wrapper.find('[aria-label="Fil d\'ariane"]')
    expect(breadcrumb.exists()).toBe(true)
    expect(breadcrumb.text()).toContain('Général (Aucun)')
  })
})

describe("NoteEdit — état d'erreur de chargement (Task 8, échec silencieux corrigé)", () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.patch.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
  })

  it('remplace le contenu par un BaseEmptyState + "Réessayer" quand le chargement de la note échoue', async () => {
    api.get.mockImplementation(
      makeGetImpl({ note: () => Promise.reject(new Error('network down')) }),
    )
    const { wrapper } = await mountNoteEdit()

    const empty = wrapper.findComponent(BaseEmptyState)
    expect(empty.exists()).toBe(true)
    expect(empty.props('title')).toBe('Le chargement a échoué')
    expect(wrapper.text()).not.toContain('Ma note de chimie')
  })

  it('le bouton "Réessayer" relance loadNoteDetails et affiche la note en cas de succès', async () => {
    api.get.mockImplementation(
      makeGetImpl({ note: () => Promise.reject(new Error('network down')) }),
    )
    const { wrapper } = await mountNoteEdit()
    expect(wrapper.findComponent(BaseEmptyState).props('title')).toBe('Le chargement a échoué')

    api.get.mockImplementation(makeGetImpl())
    const retryButton = wrapper.findComponent(BaseEmptyState).findComponent(BaseButton)
    await retryButton.trigger('click')
    await flushPromises()

    expect(wrapper.findComponent(BaseEmptyState).exists()).toBe(false)
    expect(wrapper.text()).toContain('Ma note de chimie')
  })
})

// ============================================================================================
// Task 9 — inventaire complémentaire (chargement, édition/lecture, autosave, transformations de
// sélection, export PDF, liens, révision active, partage, tiroir/aperçu/sidebar/guide,
// classeur/tags, note en lecture seule, interactions de révision + évaluation SM-2).
// ============================================================================================

describe('NoteEdit — chargement (Task 9)', () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.patch.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
  })

  it('affiche le spinner pendant le chargement puis le contenu une fois la note résolue', async () => {
    let resolveNote: (value: unknown) => void = () => {}
    const pending = new Promise((resolve) => {
      resolveNote = resolve
    })
    api.get.mockImplementation(makeGetImpl({ note: () => pending }))

    const { wrapper } = await mountNoteEdit()

    expect(wrapper.text()).toContain('Ouverture de la note...')
    expect(wrapper.text()).not.toContain('Ma note de chimie')

    resolveNote({ data: NOTE })
    await flushPromises()

    expect(wrapper.text()).not.toContain('Ouverture de la note...')
    expect(wrapper.text()).toContain('Ma note de chimie')
  })
})

describe('NoteEdit — bascule édition / lecture (Task 9)', () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.patch.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
    api.get.mockImplementation(makeGetImpl())
  })

  it("ouvre en mode édition par défaut quand le titre vaut 'Note sans titre'", async () => {
    api.get.mockImplementation(
      makeGetImpl({ note: () => Promise.resolve({ data: { ...NOTE, title: 'Note sans titre' } }) }),
    )
    const { wrapper } = await mountNoteEdit('/notes/42')

    expect(wrapper.find('textarea').exists()).toBe(true)
    expect(wrapper.text()).toContain('Visualiser')
  })

  it("ouvre en mode lecture par défaut sinon, et bascule vers édition via 'Modifier la fiche' sans sauvegarder", async () => {
    const { wrapper } = await mountNoteEdit('/notes/42')

    expect(wrapper.find('textarea').exists()).toBe(false)
    const editBtn = wrapper.findAll('button').find((b) => b.text() === 'Modifier la fiche')!
    await editBtn.trigger('click')
    await flushPromises()

    expect(wrapper.find('textarea').exists()).toBe(true)
    expect(api.put).not.toHaveBeenCalled()
  })

  it("bascule de édition vers lecture via 'Visualiser', ce qui sauvegarde la note au passage", async () => {
    api.put.mockResolvedValue({ data: { ...NOTE, flashcards: [] } })
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')

    const viewBtn = wrapper.findAll('button').find((b) => b.text() === 'Visualiser')!
    await viewBtn.trigger('click')
    await flushPromises()

    expect(api.put).toHaveBeenCalledWith(
      '/notes/42',
      expect.objectContaining({ title: 'Ma note de chimie' }),
    )
    expect(wrapper.find('textarea').exists()).toBe(false)
    expect(wrapper.text()).toContain('Modifier la fiche')
  })

  it("la barre d'actions du mode lecture peut passer à la ligne (pas de débordement horizontal à 375px)", async () => {
    // Bug réel trouvé en vérification visuelle Task 10 : à 375px, cette rangée
    // (Retour aux notes / Lecture-Révision Active à gauche, Modifier la fiche / Guide /
    // Exporter en PDF à droite) n'avait pas `flex-wrap` — mesuré en navigateur réel, les
    // boutons "Guide" et "Exporter en PDF" se retrouvaient positionnés hors du viewport
    // (x=416 et x=525 sur 375px de large) et donc inatteignables, alors même que la page
    // ne scrolle pas horizontalement (clippés silencieusement). Le même fichier utilise déjà
    // `flex-wrap` pour la rangée équivalente du mode édition (Row 1, ligne ~106) : même
    // correctif appliqué ici pour cohérence.
    const { wrapper } = await mountNoteEdit('/notes/42')

    const backBtn = wrapper.findAll('button').find((b) => b.text().includes('Retour aux notes'))!
    const actionsRow = backBtn.element.closest('.max-w-4xl.mx-auto.flex.items-center.justify-between')
    expect(actionsRow).not.toBeNull()
    expect(actionsRow!.className).toContain('flex-wrap')
  })

  it("'Retour aux notes' sauvegarde la note puis navigue vers /notes", async () => {
    api.put.mockResolvedValue({ data: { ...NOTE, flashcards: [] } })
    const { wrapper, router } = await mountNoteEdit('/notes/42')
    const push = vi.spyOn(router, 'push')

    const backBtn = wrapper.findAll('button').find((b) => b.text().includes('Retour aux notes'))!
    await backBtn.trigger('click')
    await flushPromises()

    expect(api.put).toHaveBeenCalled()
    expect(push).toHaveBeenCalledWith('/notes')
  })
})

describe('NoteEdit — sauvegarde automatique différée (Task 9)', () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.patch.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
    api.get.mockImplementation(makeGetImpl())
  })

  it("une modification du titre programme une sauvegarde après 1.5s et met à jour l'indicateur d'état", async () => {
    api.put.mockResolvedValue({ data: { ...NOTE, title: 'Titre modifié', flashcards: [] } })
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')

    vi.useFakeTimers()
    const titleInput = wrapper.get('input[placeholder="Titre de la note..."]')
    await titleInput.setValue('Titre modifié')

    expect(wrapper.text()).toContain('Modifications...')
    expect(api.put).not.toHaveBeenCalled()

    await vi.advanceTimersByTimeAsync(1600)

    expect(api.put).toHaveBeenCalledWith(
      '/notes/42',
      expect.objectContaining({ title: 'Titre modifié' }),
    )
    expect(wrapper.text()).toContain('Sauvegardé')
  })
})

describe('NoteEdit — barre de formatage (Row 2) en mode édition (Task 9)', () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.patch.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
    api.get.mockImplementation(makeGetImpl())
  })

  it("un bouton de formatage (Titre H1) insère son préfixe au point de curseur (mécanisme insertText partagé par les boutons Format/LaTeX/Code)", async () => {
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')
    const textarea = wrapper.get('textarea')
    await textarea.setValue('Chapitre un')
    ;(textarea.element as HTMLTextAreaElement).setSelectionRange(0, 0)

    await wrapper.get('[title="Titre H1"]').trigger('click')

    expect(textareaValue(wrapper)).toBe('# Chapitre un')
  })

  it("le sélecteur 'Insérer un diagramme...' insère un tag [diagram:ID] au point de curseur", async () => {
    api.get.mockImplementation(
      makeGetImpl({ diagrams: () => Promise.resolve({ data: { data: [{ id: 7, title: 'Anatomie' }] } }) }),
    )
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')
    await flushPromises()

    const textarea = wrapper.get('textarea')
    await textarea.setValue('')
    ;(textarea.element as HTMLTextAreaElement).setSelectionRange(0, 0)

    const diagramSelect = wrapper
      .findAll('select')
      .find((s) => s.text().includes('Insérer un diagramme...'))!
    await diagramSelect.setValue('7')

    expect(textareaValue(wrapper)).toBe('[diagram:7]')
  })

  it("le bouton 'Définition (Info-bulle)' exige une sélection, puis (sélection faite) ouvre la modale et insère [terme]{def:...}", async () => {
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')

    const defBtn = wrapper.findAll('button').find((b) => b.text() === 'Définition (Info-bulle)')!
    await defBtn.trigger('click')
    await flushPromises()

    let modal = wrapper.findComponent(NoteInputModal)
    expect(modal.props('visible')).toBe(true)
    expect(modal.props('title')).toBe('Sélection requise')
    await clickDialogButton('Compris')
    expect(modal.props('visible')).toBe(false)

    const textareaEl = wrapper.get('textarea').element as HTMLTextAreaElement
    const start = textareaEl.value.indexOf('note')
    textareaEl.setSelectionRange(start, start + 'note'.length)

    await defBtn.trigger('click')
    await flushPromises()

    modal = wrapper.findComponent(NoteInputModal)
    expect(modal.props('title')).toBe('Définition info-bulle')
    const input = document.body.querySelector('[role="dialog"] input') as HTMLInputElement
    input.value = 'Explication du terme'
    input.dispatchEvent(new Event('input'))
    await nextTick()
    await clickDialogButton('Ajouter la définition')

    expect(textareaValue(wrapper)).toContain('[note]{def:Explication du terme}')
  })
})

describe('NoteEdit — barre flottante de sélection : transformations (Task 9)', () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.patch.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
    api.get.mockImplementation(makeGetImpl())
  })

  it("le bouton 'Trou' entoure la sélection de {{trou::...}}", async () => {
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')
    await selectText(wrapper, 'La capitale de la France est Paris.', 'Paris')

    await wrapper.get('[title="Trou (Cloze)"]').trigger('click')

    expect(textareaValue(wrapper)).toBe('La capitale de la France est {{trou::Paris}}.')
  })

  it("le bouton 'Définition' de la barre flottante ouvre la modale puis insère [terme]{def:...}", async () => {
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')
    await selectText(wrapper, 'La photosynthèse transforme la lumière.', 'photosynthèse')

    await wrapper.get('[title="Définition info-bulle"]').trigger('click')
    await flushPromises()

    const modal = wrapper.findComponent(NoteInputModal)
    expect(modal.props('visible')).toBe(true)
    expect(modal.props('title')).toBe('Définition info-bulle')

    await clickDialogButton('Ajouter la définition')

    expect(modal.props('visible')).toBe(false)
    expect(textareaValue(wrapper)).toBe(
      'La [photosynthèse]{def:Définition...} transforme la lumière.',
    )
  })

  it("le bouton 'QCM' ouvre la modale puis insère {{qcm::...}} avec la sélection comme bonne réponse", async () => {
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')
    await selectText(wrapper, 'Le mitochondrie est la centrale énergétique.', 'mitochondrie')

    await wrapper.get('[title="QCM (Choix multiples)"]').trigger('click')
    await flushPromises()

    const modal = wrapper.findComponent(NoteInputModal)
    expect(modal.props('title')).toBe('Créer un QCM')
    await clickDialogButton('Créer le QCM')

    expect(textareaValue(wrapper)).toBe(
      'Le {{qcm::Question ?::|*mitochondrie*|}} est la centrale énergétique.',
    )
  })

  it("le bouton 'Ordre' ouvre la modale puis insère {{ordre::...}} avec la sélection comme première étape", async () => {
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')
    await selectText(wrapper, 'Étapes : Germination puis croissance.', 'Germination')

    await wrapper.get('[title="Séquence (Ordre)"]').trigger('click')
    await flushPromises()

    const modal = wrapper.findComponent(NoteInputModal)
    expect(modal.props('title')).toBe('Séquence ordonnée')
    await clickDialogButton('Créer la séquence')

    expect(textareaValue(wrapper)).toBe('Étapes : {{ordre::Ordre::Germination > }} puis croissance.')
  })

  it("le bouton 'Assoc' ouvre la modale puis insère {{assoc::...}} avec la sélection comme clé", async () => {
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')
    await selectText(wrapper, 'Capitale : Paris est en France.', 'Paris')

    await wrapper.get('[title="Association"]').trigger('click')
    await flushPromises()

    const modal = wrapper.findComponent(NoteInputModal)
    expect(modal.props('title')).toBe('Créer une association')
    await clickDialogButton('Créer l’association')

    expect(textareaValue(wrapper)).toBe('Capitale : {{assoc::Relations::Paris = }} est en France.')
  })

  it("le bouton 'V/F' ouvre la modale puis insère {{vf::...}} avec la sélection comme assertion", async () => {
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')
    await selectText(wrapper, 'Fait : Paris est la capitale.', 'Paris est la capitale')

    await wrapper.get('[title="Vrai / Faux"]').trigger('click')
    await flushPromises()

    const modal = wrapper.findComponent(NoteInputModal)
    expect(modal.props('title')).toBe('Vrai / Faux')
    await clickDialogButton('Créer la question')

    expect(textareaValue(wrapper)).toBe(
      'Fait : {{vf::Paris est la capitale::Vrai::Justification...}}.',
    )
  })

  it("le bouton 'Schéma' (diagramme disponible) ouvre la modale de sélection puis insère [diagram:ID]", async () => {
    api.get.mockImplementation(
      makeGetImpl({
        diagrams: () => Promise.resolve({ data: { data: [{ id: 5, title: 'Cycle de Krebs' }] } }),
      }),
    )
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')
    await flushPromises()
    await selectText(wrapper, 'Voir le schéma joint.', 'schéma')

    await wrapper.get('[title="Insérer un diagramme / schéma"]').trigger('click')
    await flushPromises()

    const modal = wrapper.findComponent(NoteInputModal)
    expect(modal.props('title')).toBe('Insérer un diagramme')
    await clickDialogButton('Insérer')

    expect(textareaValue(wrapper)).toBe('Voir le [diagram:5] joint.')
  })

  it("le bouton 'Schéma' sans diagramme disponible affiche une modale d'information, sans rien insérer", async () => {
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')
    const original = 'Voir le schéma joint.'
    await selectText(wrapper, original, 'schéma')

    await wrapper.get('[title="Insérer un diagramme / schéma"]').trigger('click')
    await flushPromises()

    const modal = wrapper.findComponent(NoteInputModal)
    expect(modal.props('visible')).toBe(true)
    expect(modal.props('title')).toBe('Aucun diagramme')
    await clickDialogButton('Compris')

    expect(modal.props('visible')).toBe(false)
    expect(textareaValue(wrapper)).toBe(original)
  })

  it('les transformations textuelles simples (gras/italique/code en ligne/bloc de code/math bloc/math ligne) enveloppent la sélection sans passer par une modale', async () => {
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')
    const base = 'Un mot important ici.'

    // "Gras" et "Italique" partagent le même attribut title avec les boutons Row 2
    // (mêmes libellés) : on distingue le bouton de la barre flottante par son contenu
    // court ("G" / "I" en gras/italique) plutôt que par le mot complet du bouton Row 2.
    await selectText(wrapper, base, 'mot')
    const grasBtn = wrapper.findAll('[title="Gras"]').find((b) => b.text() === 'G')!
    await grasBtn.trigger('click')
    expect(textareaValue(wrapper)).toBe('Un **mot** important ici.')

    await selectText(wrapper, base, 'mot')
    const italiqueBtn = wrapper.findAll('[title="Italique"]').find((b) => b.text() === 'I')!
    await italiqueBtn.trigger('click')
    expect(textareaValue(wrapper)).toBe('Un *mot* important ici.')

    await selectText(wrapper, base, 'mot')
    await wrapper.get('[title="Code en ligne"]').trigger('click')
    expect(textareaValue(wrapper)).toBe('Un `mot` important ici.')

    await selectText(wrapper, base, 'mot')
    await wrapper.get('[title="Bloc de code"]').trigger('click')
    expect(textareaValue(wrapper)).toBe('Un ```\nmot\n``` important ici.')

    await selectText(wrapper, base, 'mot')
    await wrapper.get('[title="Math Bloc (LaTeX)"]').trigger('click')
    expect(textareaValue(wrapper)).toBe('Un $$\nmot\n$$ important ici.')

    await selectText(wrapper, base, 'mot')
    await wrapper.get('[title="Math Ligne (LaTeX)"]').trigger('click')
    expect(textareaValue(wrapper)).toBe('Un $mot$ important ici.')
  })
})

describe('NoteEdit — raccourcis clavier du textarea (Task 9)', () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.patch.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
    api.get.mockImplementation(makeGetImpl())
  })

  it('Tab insère deux espaces au point de curseur au lieu de déplacer le focus', async () => {
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')
    const textarea = wrapper.get('textarea')
    await textarea.setValue('Ligne')
    ;(textarea.element as HTMLTextAreaElement).setSelectionRange(5, 5)

    await textarea.trigger('keydown', { key: 'Tab' })

    expect(textareaValue(wrapper)).toBe('Ligne  ')
  })

  it('Maj+Entrée insère un saut de ligne souple, ou un <br> dans une ligne de tableau Markdown', async () => {
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')
    const textarea = wrapper.get('textarea')

    await textarea.setValue('Texte simple')
    ;(textarea.element as HTMLTextAreaElement).setSelectionRange(12, 12)
    await textarea.trigger('keydown', { key: 'Enter', shiftKey: true })
    expect(textareaValue(wrapper)).toBe('Texte simple\n')

    await textarea.setValue('| a | b |')
    ;(textarea.element as HTMLTextAreaElement).setSelectionRange(9, 9)
    await textarea.trigger('keydown', { key: 'Enter', shiftKey: true })
    expect(textareaValue(wrapper)).toBe('| a | b |<br>')
  })
})

describe("NoteEdit — export PDF (Task 9)", () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.patch.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
    api.get.mockImplementation(makeGetImpl())
  })

  it("'Exporter en PDF' ouvre la modale d'export avec le titre de la note", async () => {
    const { wrapper } = await mountNoteEdit('/notes/42')

    const trigger = wrapper.findAll('button').find((b) => b.text() === 'Exporter en PDF')!
    await trigger.trigger('click')

    expect(wrapper.text()).toContain('Exportation PDF & Impression')
    expect(wrapper.text()).toContain('Ma note de chimie')
  })

  it("confirmer l'export imprime le document (après un court délai) et referme la modale", async () => {
    const originalPrint = window.print
    window.print = vi.fn()
    try {
      const { wrapper } = await mountNoteEdit('/notes/42')
      const trigger = wrapper.findAll('button').find((b) => b.text() === 'Exporter en PDF')!
      await trigger.trigger('click')

      vi.useFakeTimers()
      const confirmExport = wrapper
        .findAll('button')
        .find((b) => b.text().includes("Lancer l'exportation PDF"))!
      await confirmExport.trigger('click')

      expect(wrapper.text()).not.toContain('Exportation PDF & Impression')
      expect(window.print).not.toHaveBeenCalled()

      await vi.advanceTimersByTimeAsync(200)

      expect(window.print).toHaveBeenCalledTimes(1)
    } finally {
      window.print = originalPrint
    }
  })

  it("'Annuler' dans la modale d'export la referme sans imprimer", async () => {
    const originalPrint = window.print
    window.print = vi.fn()
    try {
      const { wrapper } = await mountNoteEdit('/notes/42')
      const trigger = wrapper.findAll('button').find((b) => b.text() === 'Exporter en PDF')!
      await trigger.trigger('click')

      const cancelBtn = wrapper.findAll('button').find((b) => b.text() === 'Annuler')!
      await cancelBtn.trigger('click')

      expect(wrapper.text()).not.toContain('Exportation PDF & Impression')
      expect(window.print).not.toHaveBeenCalled()
    } finally {
      window.print = originalPrint
    }
  })
})

describe('NoteEdit — liens entre notes (Task 9)', () => {
  const OTHER_NOTE: Note = {
    id: '9',
    binder_id: null,
    title: 'Autre note',
    content: '',
    created_at: '',
    updated_at: '',
    tags: [],
  }
  const LINKED_NOTE: Note = {
    id: '7',
    binder_id: null,
    title: 'Note cible',
    content: '',
    created_at: '',
    updated_at: '',
    tags: [],
  }

  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.patch.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
  })

  it('ajoute un lien vers une autre note depuis le tiroir Contexte / Liens, puis le retire via le badge', async () => {
    api.get.mockImplementation(
      makeGetImpl({ notes: () => Promise.resolve({ data: { data: [OTHER_NOTE] } }) }),
    )
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')
    await flushPromises()

    const settingsBtn = wrapper.findAll('button').find((b) => b.text() === 'Contexte / Liens')!
    await settingsBtn.trigger('click')

    const linkSelect = wrapper
      .findAll('select')
      .find((s) => s.text().includes('Sélectionner une note...'))!
    await linkSelect.setValue('9')

    const linkBtn = wrapper.findAll('button').find((b) => b.text() === 'Lier')!
    await linkBtn.trigger('click')

    expect(wrapper.text()).toContain('Autre note')

    const removeBtn = wrapper.findAll('button').find((b) => b.text() === '✕')!
    await removeBtn.trigger('click')

    expect(wrapper.findAll('button').find((b) => b.text() === '✕')).toBeUndefined()
  })

  it('navigue vers la note liée au clic sur son badge, en mode lecture', async () => {
    api.get.mockImplementation(
      makeGetImpl({
        note: () =>
          Promise.resolve({
            data: {
              ...NOTE,
              content:
                '<!-- LINKED_NOTES: 7 -->\n<!-- SECTION_BODY -->\nCorps.\n<!-- END_SECTION_BODY -->',
            },
          }),
        notes: () => Promise.resolve({ data: { data: [LINKED_NOTE] } }),
      }),
    )
    const { wrapper, router } = await mountNoteEdit('/notes/42')
    await flushPromises()
    const push = vi.spyOn(router, 'push')

    const linkedBadge = wrapper.findAll('button').find((b) => b.text().includes('Note cible'))!
    await linkedBadge.trigger('click')

    expect(push).toHaveBeenCalledWith('/notes/7')
  })
})

describe('NoteEdit — bascule Lecture / Révision Active (Task 9)', () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.patch.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
    api.get.mockImplementation(makeGetImpl())
  })

  it('le sélecteur Lecture / Révision Active bascule notesStore.isReviewModeActive', async () => {
    const { wrapper, pinia } = await mountNoteEdit('/notes/42')
    const notesStore = useNotesStore(pinia)
    expect(notesStore.isReviewModeActive).toBe(false)

    const revisionBtn = wrapper.findAll('button').find((b) => b.text().includes('Révision Active'))!
    await revisionBtn.trigger('click')
    expect(notesStore.isReviewModeActive).toBe(true)

    const lectureBtn = wrapper.findAll('button').find((b) => b.text().trim() === 'Lecture')!
    await lectureBtn.trigger('click')
    expect(notesStore.isReviewModeActive).toBe(false)
  })
})

describe('NoteEdit — partage / visibilité (Task 9)', () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.patch.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
    api.get.mockImplementation(makeGetImpl())
  })

  it('rend la note publique (popup + lien), copie le lien, puis la rend privée à nouveau', async () => {
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText: vi.fn().mockResolvedValue(undefined) },
      configurable: true,
    })
    api.patch.mockImplementation((_url: string, body: { is_public: boolean }) => {
      if (body.is_public) {
        return Promise.resolve({ data: { is_public: true, share_token: 'tok-123' } })
      }
      return Promise.resolve({ data: { is_public: false, share_token: null } })
    })

    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')

    const shareBtn = wrapper.findAll('button').find((b) => b.text() === 'Privé')!
    await shareBtn.trigger('click')
    await flushPromises()

    expect(api.patch).toHaveBeenCalledWith('/notes/42/visibility', { is_public: true })
    expect(wrapper.text()).toContain('Public')
    expect(wrapper.text()).toContain('Note publique')

    const copyBtn = wrapper.findAll('button').find((b) => b.text() === 'Copier')!
    await copyBtn.trigger('click')
    await flushPromises()

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      `${window.location.origin}/notes/public/tok-123`,
    )
    expect(wrapper.text()).toContain('Copié !')

    const makePrivateBtn = wrapper.findAll('button').find((b) => b.text() === 'Rendre privée')!
    await makePrivateBtn.trigger('click')
    await flushPromises()

    expect(api.patch).toHaveBeenLastCalledWith('/notes/42/visibility', { is_public: false })
    expect(wrapper.text()).toContain('Privé')
  })
})

describe('NoteEdit — tiroir Contexte/Liens, aperçu live, sidebar de raccourcis et guide (Task 9)', () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.patch.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
    api.get.mockImplementation(makeGetImpl())
  })

  it("le bouton 'Contexte / Liens' ouvre puis referme le tiroir contextuel", async () => {
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')
    expect(wrapper.find('textarea[placeholder*="Historique"]').exists()).toBe(false)

    const settingsBtn = wrapper.findAll('button').find((b) => b.text() === 'Contexte / Liens')!
    await settingsBtn.trigger('click')
    expect(wrapper.find('textarea[placeholder*="Historique"]').exists()).toBe(true)

    await settingsBtn.trigger('click')
    expect(wrapper.find('textarea[placeholder*="Historique"]').exists()).toBe(false)
  })

  it("le bouton 'Aperçu' affiche puis masque le panneau de prévisualisation en temps réel", async () => {
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')
    expect(wrapper.text()).not.toContain('Aperçu en temps réel')

    const previewBtn = wrapper.findAll('button').find((b) => b.text() === 'Aperçu')!
    await previewBtn.trigger('click')
    expect(wrapper.text()).toContain('Aperçu en temps réel')

    await previewBtn.trigger('click')
    expect(wrapper.text()).not.toContain('Aperçu en temps réel')
  })

  it("le bouton de la barre latérale de raccourcis émet l'évènement studyhub:toggle-sidebar sur window", async () => {
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')
    const handler = vi.fn()
    window.addEventListener('studyhub:toggle-sidebar', handler)

    try {
      await wrapper.get('[title="Afficher la barre de raccourcis"]').trigger('click')
      expect(handler).toHaveBeenCalledTimes(1)
    } finally {
      window.removeEventListener('studyhub:toggle-sidebar', handler)
    }
  })

  it("le bouton 'Guide' ouvre la modale d'aide, en mode édition comme en mode lecture", async () => {
    // NoteEditHelpModal s'appuie sur BaseModal (Dialog headlessui, téléporté dans
    // document.body) : on vérifie le contenu affiché via document.body, pas wrapper.text().
    const edit = await mountNoteEdit('/notes/42?edit=true')
    const editGuideBtn = edit.wrapper.findAll('button').find((b) => b.text() === 'Guide')!
    await editGuideBtn.trigger('click')
    await flushPromises()
    expect(document.body.textContent).toContain("Guide d'utilisation StudyHub")
    edit.wrapper.unmount()
    const editIdx = mountedWrappers.indexOf(edit.wrapper)
    if (editIdx !== -1) mountedWrappers.splice(editIdx, 1)

    const read = await mountNoteEdit('/notes/42')
    const readGuideBtn = read.wrapper.findAll('button').find((b) => b.text() === 'Guide')!
    await readGuideBtn.trigger('click')
    await flushPromises()
    expect(document.body.textContent).toContain("Guide d'utilisation StudyHub")
  })
})

describe('NoteEdit — classeur & tags (Task 9)', () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.patch.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
  })

  it('changer le classeur sélectionné déclenche une sauvegarde différée avec le nouveau binder_id', async () => {
    api.get.mockImplementation(
      makeGetImpl({
        binders: () =>
          Promise.resolve({
            data: { data: [{ id: 'b2', name: 'Maths', parent_id: null, created_at: '' }] },
          }),
      }),
    )
    api.put.mockResolvedValue({ data: { ...NOTE, binder_id: 'b2', flashcards: [] } })
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')
    await flushPromises()

    vi.useFakeTimers()
    const binderSelect = wrapper.findAll('select').find((s) => s.text().includes('Général (Aucun)'))!
    await binderSelect.setValue('b2')

    await vi.advanceTimersByTimeAsync(1600)

    expect(api.put).toHaveBeenCalledWith('/notes/42', expect.objectContaining({ binder_id: 'b2' }))
  })

  it("le TagSelector émet change -> saveNoteTags met à jour les tags de la note via l'API", async () => {
    api.get.mockImplementation(
      makeGetImpl({
        tags: () =>
          Promise.resolve({ data: { data: [{ id: 1, name: 'Chimie', color: null, created_at: '' }] } }),
      }),
    )
    api.post.mockResolvedValue({
      data: { data: [{ id: 1, name: 'Chimie', color: null, created_at: '' }] },
    })
    const { wrapper } = await mountNoteEdit('/notes/42?edit=true')
    await flushPromises()

    const tagSelector = wrapper.findComponent(TagSelector)
    await tagSelector.get('button').trigger('click')
    const select = tagSelector.get('select')
    await select.setValue('1')
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith('/notes/42/tags', { tag_ids: [1] })
    expect(tagSelector.props('modelValue')).toEqual([
      { id: 1, name: 'Chimie', color: null, created_at: '' },
    ])
  })
})

describe('NoteEdit — note en lecture seule partagée par un cours (Task 9)', () => {
  const READONLY_NOTE = { ...NOTE, read_only: true }

  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.patch.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
    api.get.mockImplementation(makeGetImpl({ note: () => Promise.resolve({ data: READONLY_NOTE }) }))
  })

  it("affiche la bannière lecture seule et 'Cacher' masque la note puis redirige vers /notes", async () => {
    api.post.mockResolvedValue({ data: {} })
    const { wrapper, router } = await mountNoteEdit('/notes/42')
    const push = vi.spyOn(router, 'push')

    expect(wrapper.text()).toContain('Note partagée par un cours — lecture seule.')

    const hideBtn = wrapper.findAll('button').find((b) => b.text() === 'Cacher')!
    await hideBtn.trigger('click')
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith('/notes/42/hide')
    expect(push).toHaveBeenCalledWith('/notes')
  })

  it("'Copier pour modifier' crée une copie personnelle et navigue vers son édition", async () => {
    api.post.mockResolvedValue({
      data: {
        id: '99',
        binder_id: null,
        title: 'Ma note de chimie',
        content: '',
        created_at: '',
        updated_at: '',
        tags: [],
      },
    })
    const { wrapper, router } = await mountNoteEdit('/notes/42')
    const push = vi.spyOn(router, 'push')

    const copyBtn = wrapper.findAll('button').find((b) => b.text() === 'Copier pour modifier')!
    await copyBtn.trigger('click')
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith('/notes/42/copy')
    expect(push).toHaveBeenCalledWith('/notes/99?edit=true')
  })
})

describe('NoteEdit — révision active : trou révélé et évaluation SM-2 (Task 9)', () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.patch.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
  })

  it("révéler un trou lié à une flashcard ouvre (après un court délai) la modale d'évaluation SM-2 ; soumettre une note appelle l'API et referme la modale", async () => {
    api.get.mockImplementation(
      makeGetImpl({
        note: () =>
          Promise.resolve({
            data: {
              ...NOTE,
              content:
                '<!-- SECTION_BODY -->\nUn terme important : {{trou::motcache}}.\n<!-- END_SECTION_BODY -->',
              flashcards: [{ id: 99, original_text: '{{trou::motcache}}' }],
            },
          }),
      }),
    )
    api.patch.mockResolvedValue({ data: {} })

    const { wrapper } = await mountNoteEdit('/notes/42')

    const revisionBtn = wrapper.findAll('button').find((b) => b.text().includes('Révision Active'))!
    await revisionBtn.trigger('click')
    await flushPromises()

    const revealEl = wrapper.get('[data-action="reveal"]')

    vi.useFakeTimers()
    await revealEl.trigger('click')
    await vi.advanceTimersByTimeAsync(800)

    const evalModal = wrapper.findComponent(NoteEvaluationModal)
    expect(evalModal.props('visible')).toBe(true)

    vi.useRealTimers()
    await clickDialogButton('Facile')

    expect(api.patch).toHaveBeenCalledWith('/flashcards/99/review', { score: 5 })
    expect(wrapper.findComponent(NoteEvaluationModal).props('visible')).toBe(false)
  })
})

// Fix round 1 (revue Task 9) : le "trou révélé" ci-dessus n'exerçait que la branche `reveal` de
// `handlePlaceholderInteraction` — partagée par toutes les variantes uniquement pour le
// déclenchement différé de la modale d'évaluation SM-2 (NoteEdit.vue:2474-2489). La logique de
// mutation d'état propre à chaque variante (qcm-select/vf-select/order-move/order-validate/
// assoc-key-select/assoc-value-select/assoc-remove/assoc-validate, NoteEdit.vue:2413-2451) n'était
// couverte nulle part. Aucune de ces notes n'a de flashcard associée (`flashcards` omis dans la
// réponse `/notes/:id` mockée) : `noteFlashcards` reste vide, donc `cardId` est `null` pour ces
// placeholders et la modale d'évaluation ne se déclenche jamais (NoteEdit.vue:2482-2489,
// `isActionRequiringEvaluation && cardId && ...`) — pas besoin de la danse des timers factices
// pour ces tests, qui portent uniquement sur la mutation d'état/le nouveau rendu.
describe('NoteEdit — révision active : variantes de handlePlaceholderInteraction (Fix round 1)', () => {
  beforeEach(() => {
    api.get.mockReset()
    api.post.mockReset()
    api.patch.mockReset()
    api.put.mockReset()
    api.delete.mockReset()
  })

  async function enterReviewMode(wrapper: VueWrapper) {
    const revisionBtn = wrapper
      .findAll('button')
      .find((b) => b.text().includes('Révision Active'))!
    await revisionBtn.trigger('click')
    await flushPromises()
  }

  // Lit le texte de l'étape affichée à l'index `idx` de la séquence "ordre" en passant par le
  // bouton "monter" de cette rangée (toujours présent tant que la séquence n'est pas validée) :
  // NoteEdit.vue:1786-1804, structure `<div><span>{{step}}</span><div>▲▼</div></div>`.
  function stepTextAt(wrapper: VueWrapper, idx: number): string {
    const upBtn = wrapper.get(`[data-action="order-move"][data-dir="up"][data-index="${idx}"]`)
    const row = (upBtn.element as HTMLElement).parentElement!.parentElement!
    return row.querySelector('span')?.textContent?.trim() ?? ''
  }

  it('qcm-select : choisir la bonne option la marque correcte et désactive/estompe les autres (NoteEdit.vue:1642-1661)', async () => {
    api.get.mockImplementation(
      makeGetImpl({
        note: () =>
          Promise.resolve({
            data: {
              ...NOTE,
              content:
                '<!-- SECTION_BODY -->\n{{qcm::La capitale de la France ?::Lyon|*Paris*|Marseille}}\n<!-- END_SECTION_BODY -->',
            },
          }),
      }),
    )

    const { wrapper } = await mountNoteEdit('/notes/42')
    await enterReviewMode(wrapper)

    const correctBefore = wrapper.get('[data-action="qcm-select"][data-option="Paris"]')
    expect(correctBefore.attributes('disabled')).toBeUndefined()

    await correctBefore.trigger('click')
    await flushPromises()

    const correctAfter = wrapper.get('[data-action="qcm-select"][data-option="Paris"]')
    expect(correctAfter.attributes('disabled')).toBeDefined()
    expect(correctAfter.classes()).toContain('bg-success-soft')

    const wrongAfter = wrapper.get('[data-action="qcm-select"][data-option="Lyon"]')
    expect(wrongAfter.attributes('disabled')).toBeDefined()
    expect(wrongAfter.classes()).toContain('opacity-40')

    const otherWrongAfter = wrapper.get('[data-action="qcm-select"][data-option="Marseille"]')
    expect(otherWrongAfter.attributes('disabled')).toBeDefined()
    expect(otherWrongAfter.classes()).toContain('opacity-40')
  })

  it('vf-select : choisir la mauvaise réponse la marque en échec, révèle la bonne réponse et la justification (NoteEdit.vue:1708-1749)', async () => {
    api.get.mockImplementation(
      makeGetImpl({
        note: () =>
          Promise.resolve({
            data: {
              ...NOTE,
              content:
                '<!-- SECTION_BODY -->\n{{vf::Le soleil est une étoile::Vrai::Le soleil est une naine jaune.}}\n<!-- END_SECTION_BODY -->',
            },
          }),
      }),
    )

    const { wrapper } = await mountNoteEdit('/notes/42')
    await enterReviewMode(wrapper)

    const fauxBefore = wrapper.get('[data-action="vf-select"][data-value="Faux"]')
    expect(fauxBefore.attributes('disabled')).toBeUndefined()
    expect(wrapper.text()).not.toContain('Le soleil est une naine jaune.')

    await fauxBefore.trigger('click')
    await flushPromises()

    const fauxAfter = wrapper.get('[data-action="vf-select"][data-value="Faux"]')
    const vraiAfter = wrapper.get('[data-action="vf-select"][data-value="Vrai"]')
    expect(fauxAfter.classes()).toContain('bg-danger-soft')
    expect(fauxAfter.attributes('disabled')).toBeDefined()
    expect(vraiAfter.classes()).toContain('bg-success-soft')
    expect(vraiAfter.attributes('disabled')).toBeDefined()
    expect(wrapper.text()).toContain('Le soleil est une naine jaune.')
  })

  it("order-move : aucun effet en butée (haut du 1er, bas du dernier), permutation réelle sur un mouvement valide ; order-validate verrouille l'ordre (NoteEdit.vue:2421-2437)", async () => {
    api.get.mockImplementation(
      makeGetImpl({
        note: () =>
          Promise.resolve({
            data: {
              ...NOTE,
              content:
                "<!-- SECTION_BODY -->\n{{ordre::Étapes de la photosynthèse::Absorption de lumière > Production de glucose > Libération d'oxygène}}\n<!-- END_SECTION_BODY -->",
            },
          }),
      }),
    )

    const { wrapper } = await mountNoteEdit('/notes/42')
    await enterReviewMode(wrapper)

    const before = [0, 1, 2].map((i) => stepTextAt(wrapper, i))
    expect(new Set(before).size).toBe(3) // les 3 étapes sont bien distinctes

    // Butée haute : monter le premier élément est un no-op (NoteEdit.vue:2426, `idx > 0`).
    await wrapper
      .get('[data-action="order-move"][data-dir="up"][data-index="0"]')
      .trigger('click')
    await flushPromises()
    expect([0, 1, 2].map((i) => stepTextAt(wrapper, i))).toEqual(before)

    // Butée basse : descendre le dernier élément est un no-op (NoteEdit.vue:2430, `idx < length-1`).
    await wrapper
      .get('[data-action="order-move"][data-dir="down"][data-index="2"]')
      .trigger('click')
    await flushPromises()
    expect([0, 1, 2].map((i) => stepTextAt(wrapper, i))).toEqual(before)

    // Mouvement valide : monter l'élément d'index 1 permute réellement les positions 0 et 1.
    await wrapper
      .get('[data-action="order-move"][data-dir="up"][data-index="1"]')
      .trigger('click')
    await flushPromises()
    const after = [0, 1, 2].map((i) => stepTextAt(wrapper, i))
    expect(after[0]).toBe(before[1])
    expect(after[1]).toBe(before[0])
    expect(after[2]).toBe(before[2])

    // order-validate : verrouille l'ordre (state.answered = true), les boutons ▲▼ disparaissent
    // et l'ordre attendu est révélé.
    await wrapper.get('[data-action="order-validate"]').trigger('click')
    await flushPromises()
    expect(wrapper.find('[data-action="order-move"]').exists()).toBe(false)
    expect(wrapper.text()).toContain('Ordre attendu')
  })

  it('association : assoc-key-select puis assoc-value-select créent une liaison, assoc-remove l’efface, assoc-validate verrouille (NoteEdit.vue:1874-1963, 2438-2451)', async () => {
    api.get.mockImplementation(
      makeGetImpl({
        note: () =>
          Promise.resolve({
            data: {
              ...NOTE,
              content:
                '<!-- SECTION_BODY -->\n{{assoc::Capitales::France=Paris | Espagne=Madrid | Italie=Rome}}\n<!-- END_SECTION_BODY -->',
            },
          }),
      }),
    )

    const { wrapper } = await mountNoteEdit('/notes/42')
    await enterReviewMode(wrapper)

    // Avant toute sélection de clé, tous les boutons "valeur" sont désactivés
    // (NoteEdit.vue:1920, `!state.selectedKey`).
    for (const btn of wrapper.findAll('[data-action="assoc-value-select"]')) {
      expect(btn.attributes('disabled')).toBeDefined()
    }

    // assoc-key-select : sélectionner "France" l'active visuellement et déverrouille les valeurs.
    await wrapper
      .get('[data-action="assoc-key-select"][data-key="France"]')
      .trigger('click')
    await flushPromises()

    expect(
      wrapper.get('[data-action="assoc-key-select"][data-key="France"]').classes(),
    ).toContain('border-primary')
    expect(
      wrapper.get('[data-action="assoc-value-select"][data-value="Paris"]').attributes('disabled'),
    ).toBeUndefined()

    // assoc-value-select : choisir "Paris" enregistre la liaison France -> Paris et réinitialise
    // la clé sélectionnée (NoteEdit.vue:2441-2446).
    await wrapper
      .get('[data-action="assoc-value-select"][data-value="Paris"]')
      .trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Liaisons créées')
    expect(wrapper.text()).toContain('France')
    expect(wrapper.text()).toContain('Paris')
    expect(
      wrapper.get('[data-action="assoc-key-select"][data-key="France"]').attributes('disabled'),
    ).toBeDefined()
    expect(
      wrapper.get('[data-action="assoc-value-select"][data-value="Paris"]').attributes('disabled'),
    ).toBeDefined()

    // assoc-remove : retirer la liaison France -> Paris la fait disparaître et réactive la clé
    // (NoteEdit.vue:2447-2449). Le bouton "valeur" reste désactivé : aucune clé n'est sélectionnée
    // à ce stade (`!state.selectedKey`, NoteEdit.vue:1920) — il ne se réactive qu'après un nouveau
    // assoc-key-select, vérifié juste après.
    await wrapper.get('[data-action="assoc-remove"][data-key="France"]').trigger('click')
    await flushPromises()

    expect(wrapper.text()).not.toContain('Liaisons créées')
    expect(
      wrapper.get('[data-action="assoc-key-select"][data-key="France"]').attributes('disabled'),
    ).toBeUndefined()
    expect(
      wrapper.get('[data-action="assoc-value-select"][data-value="Paris"]').attributes('disabled'),
    ).toBeDefined()

    // Reconstitue les 3 liaisons pour débloquer assoc-validate (désactivé tant que
    // Object.keys(matches).length !== keysList.length, NoteEdit.vue:1946).
    const pairs: Array<[string, string]> = [
      ['France', 'Paris'],
      ['Espagne', 'Madrid'],
      ['Italie', 'Rome'],
    ]
    for (const [key, value] of pairs) {
      await wrapper.get(`[data-action="assoc-key-select"][data-key="${key}"]`).trigger('click')
      await flushPromises()
      await wrapper
        .get(`[data-action="assoc-value-select"][data-value="${value}"]`)
        .trigger('click')
      await flushPromises()
    }

    const validateBtn = wrapper.get('[data-action="assoc-validate"]')
    expect(validateBtn.attributes('disabled')).toBeUndefined()

    await validateBtn.trigger('click')
    await flushPromises()

    expect(wrapper.find('[data-action="assoc-validate"]').exists()).toBe(false)
    expect(wrapper.text()).toContain('Associations attendues')
  })
})
