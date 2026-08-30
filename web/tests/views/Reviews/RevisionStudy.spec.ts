import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import RevisionStudy from '../../../src/views/Reviews/RevisionStudy.vue'

const HETEROGENEOUS_SET = { id: 7, name: 'Mixte', description: null, type: null, binder_id: null, tuning_default: 1, is_public: false, item_count: 2 }

function item(id: number, type: string, payload: Record<string, unknown>) {
  return { id, set_id: 7, type, payload, tuning: 1, position: 0, interval: 0, ease_factor: 2.5, repetitions: 0, next_review: '', created_at: '', updated_at: '' }
}

const stub = { template: '<div />' }
function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/revision/sets/:id/study', name: 'RevisionStudy', component: stub },
      { path: '/revision/sets/:id/run', name: 'QcmRun', component: stub },
    ],
  })
}

async function mountStudy(path: string, setResponse = HETEROGENEOUS_SET, items: unknown[] = []) {
  const pinia = createPinia()
  setActivePinia(pinia)
  api.get.mockImplementation((url: string) => {
    if (/\/revision\/sets\/\d+$/.test(url)) return Promise.resolve({ data: setResponse })
    if (/\/revision\/sets\/\d+\/study$/.test(url)) return Promise.resolve({ data: items })
    return Promise.reject(new Error(`non mocké: ${url}`))
  })
  const router = createTestRouter()
  await router.push(path)
  await router.isReady()
  const wrapper = mount(RevisionStudy, { global: { plugins: [pinia, router] } })
  await flushPromises()
  return { wrapper, router }
}

describe('RevisionStudy — dispatch par item.type (ensembles heterogenes)', () => {
  beforeEach(() => vi.clearAllMocks())

  it('rend le bon gabarit pour chaque item selon son propre type, dans une session mixte', async () => {
    const items = [item(1, 'vf', { assertion: 'Le ciel est bleu.', correct: true }), item(2, 'flashcard', { front: 'Chat', back: 'Cat' })]
    const { wrapper } = await mountStudy('/revision/sets/7/study', HETEROGENEOUS_SET, items)

    expect(wrapper.text()).toContain('Le ciel est bleu.')
    expect(wrapper.text()).not.toContain('Chat')
  })

  it('branche flashcard : recto, revele le verso, auto-evaluation 1/3/5', async () => {
    api.post.mockResolvedValue({ data: { id: 2, set_id: 7 } })
    const items = [item(2, 'flashcard', { front: 'Chat', back: 'Cat' })]
    const { wrapper } = await mountStudy('/revision/sets/7/study', HETEROGENEOUS_SET, items)

    expect(wrapper.text()).toContain('Chat')
    expect(wrapper.text()).not.toContain('Cat')
    await wrapper.find('[data-test="reveal-flashcard-button"]').trigger('click')
    expect(wrapper.text()).toContain('Cat')

    await wrapper.find('[data-test="self-eval-acquis"]').trigger('click')
    await flushPromises()
    expect(api.post).toHaveBeenCalledWith('/revision/sets/7/study/answer/2', {
      score: 5,
      duration_seconds: expect.any(Number),
    })
  })

  it('inclut la duree reelle ecoulee (Date.now) dans le payload de soumission (Task 9)', async () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-01-01T00:00:00.000Z'))
    try {
      api.post.mockResolvedValue({ data: { id: 2, set_id: 7 } })
      const items = [item(2, 'flashcard', { front: 'Chat', back: 'Cat' })]
      const { wrapper } = await mountStudy('/revision/sets/7/study', HETEROGENEOUS_SET, items)

      // Le chrono demarre au setupItem() de l'item courant -- on avance le
      // temps de 7s avant de reveler puis de soumettre l'auto-evaluation.
      vi.setSystemTime(new Date('2026-01-01T00:00:07.000Z'))
      await wrapper.find('[data-test="reveal-flashcard-button"]').trigger('click')
      await wrapper.find('[data-test="self-eval-acquis"]').trigger('click')
      await flushPromises()

      expect(api.post).toHaveBeenCalledWith('/revision/sets/7/study/answer/2', {
        score: 5,
        duration_seconds: 7,
      })
    } finally {
      vi.useRealTimers()
    }
  })

  it('filtre la session par type quand ?type= est present', async () => {
    const items = [item(1, 'vf', { assertion: 'A', correct: true }), item(2, 'flashcard', { front: 'B', back: 'C' })]
    const { wrapper } = await mountStudy('/revision/sets/7/study?type=vf', HETEROGENEOUS_SET, items)

    expect(wrapper.text()).toContain('A')
    expect(wrapper.text()).not.toContain('B')
  })

  it('non-regression : branche vf existante fonctionne toujours sur un ensemble homogene', async () => {
    const homogeneous = { ...HETEROGENEOUS_SET, type: 'vf' }
    const items = [item(1, 'vf', { assertion: 'Le ciel est bleu.', correct: true })]
    const { wrapper } = await mountStudy('/revision/sets/7/study', homogeneous, items)
    expect(wrapper.text()).toContain('Le ciel est bleu.')
  })

  it('exclut les items qcm d\'une session mixte : aucune carte vide, les autres types restent normaux', async () => {
    // Le qcm est place EN PREMIER : sans exclusion, l'ecran ouvrirait sur une carte
    // vide (aucune branche du template ne matche 'qcm') et resterait bloque dessus.
    const items = [
      item(3, 'qcm', { question: 'Capitale de la France ?', options: [{ id: 'a', text: 'Paris', correct: true }] }),
      item(1, 'vf', { assertion: 'Le ciel est bleu.', correct: true }),
    ]
    const { wrapper } = await mountStudy('/revision/sets/7/study', HETEROGENEOUS_SET, items)

    // La question du qcm n'est jamais rendue...
    expect(wrapper.text()).not.toContain('Capitale de la France ?')
    // ...et la session ne compte que l'item vf, affiche immediatement avec ses boutons.
    expect(wrapper.text()).toContain('1 / 1')
    expect(wrapper.text()).toContain('Le ciel est bleu.')
    const labels = wrapper.findAll('button').map((b) => b.text())
    expect(labels).toContain('Vrai')
    expect(labels).toContain('Faux')
  })

  it('?type=qcm : message dedie, distinct de l\'etat vide generique', async () => {
    const items = [item(3, 'qcm', { question: 'Capitale de la France ?' })]
    const { wrapper } = await mountStudy('/revision/sets/7/study?type=qcm', HETEROGENEOUS_SET, items)

    expect(wrapper.text()).toContain('ne se révisent pas encore individuellement')
    expect(wrapper.text()).not.toContain("Rien à réviser pour l'instant")
  })

  it('etat vide reel (aucun item du tout) : conserve le message generique', async () => {
    const { wrapper } = await mountStudy('/revision/sets/7/study', HETEROGENEOUS_SET, [])
    expect(wrapper.text()).toContain("Rien à réviser pour l'instant")
    expect(wrapper.text()).not.toContain('ne se révisent pas encore individuellement')
  })

  it('non-regression : redirige toujours vers /run pour un ensemble QCM homogene sans filtre', async () => {
    const qcmSet = { ...HETEROGENEOUS_SET, type: 'qcm' }
    const { router } = await mountStudy('/revision/sets/7/study', qcmSet, [])
    expect(router.currentRoute.value.fullPath).toBe('/revision/sets/7/run')
  })

  // ── Task 7 : meme principe que QcmRun.vue (Task 6) -- l'etat vide generique
  // propose de relancer la session en incluant les items non dus.
  it('etat vide generique : bouton "Reviser quand meme" relance fetchStudyItems avec include_not_due=true et affiche les items', async () => {
    const { wrapper } = await mountStudy('/revision/sets/7/study', HETEROGENEOUS_SET, [])
    expect(wrapper.text()).toContain("Rien à réviser pour l'instant")

    const notDueItem = item(5, 'vf', { assertion: 'Deja revisee.', correct: true })
    api.get.mockImplementation((url: string) => {
      if (/\/revision\/sets\/\d+$/.test(url)) return Promise.resolve({ data: HETEROGENEOUS_SET })
      if (url === '/revision/sets/7/study?include_not_due=true') {
        return Promise.resolve({ data: [notDueItem] })
      }
      if (/\/revision\/sets\/\d+\/study$/.test(url)) return Promise.resolve({ data: [] })
      return Promise.reject(new Error(`non mocké: ${url}`))
    })

    await findButtonByText(wrapper, 'Réviser quand même')!.trigger('click')
    await flushPromises()

    expect(api.get).toHaveBeenCalledWith('/revision/sets/7/study?include_not_due=true')
    expect(wrapper.text()).toContain('Deja revisee.')
  })

  it('?type=qcm : pas de bouton "Reviser quand meme" (le message qcm redirige deja ailleurs)', async () => {
    const items = [item(3, 'qcm', { question: 'Capitale de la France ?' })]
    const { wrapper } = await mountStudy('/revision/sets/7/study?type=qcm', HETEROGENEOUS_SET, items)
    expect(findButtonByText(wrapper, 'Réviser quand même')).toBeUndefined()
  })
})

function findButtonByText(wrapper: ReturnType<typeof mount>, text: string) {
  return wrapper.findAll('button').find((b) => b.text() === text)
}

describe('RevisionStudy — notation manuelle vf/association/ordre apres check (Task 5)', () => {
  beforeEach(() => vi.clearAllMocks())

  it('vf : soumettre une reponse appelle check (pas grade), affiche la correction et les boutons de notation, pas le bouton Suivant', async () => {
    api.post.mockImplementation((url: string) => {
      if (url === '/revision/sets/7/study/check/1') return Promise.resolve({ data: { correct: true } })
      return Promise.reject(new Error(`non mocké: ${url}`))
    })
    const items = [item(1, 'vf', { assertion: 'Le ciel est bleu.', correct: true })]
    const { wrapper } = await mountStudy('/revision/sets/7/study', HETEROGENEOUS_SET, items)

    await findButtonByText(wrapper, 'Vrai')!.trigger('click')
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith('/revision/sets/7/study/check/1', { answer: { value: true } })
    expect(api.post).not.toHaveBeenCalledWith(expect.stringContaining('/grade/'), expect.anything())
    expect(wrapper.text()).toContain('Correct !')
    expect(wrapper.find('[data-test="self-eval-a-revoir"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="self-eval-moyen"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="self-eval-acquis"]').exists()).toBe(true)
    expect(findButtonByText(wrapper, 'Terminer')).toBeUndefined()
    expect(findButtonByText(wrapper, 'Suivant')).toBeUndefined()
  })

  it('vf : cliquer un bouton de notation appelle gradeItem avec le score choisi ET la reponse initialement soumise, puis affiche Suivant', async () => {
    api.post.mockImplementation((url: string) => {
      if (url === '/revision/sets/7/study/check/1') return Promise.resolve({ data: { correct: true } })
      if (url === '/revision/sets/7/study/grade/1') return Promise.resolve({ data: { correct: true, item: { id: 1 } } })
      return Promise.reject(new Error(`non mocké: ${url}`))
    })
    const items = [
      item(1, 'vf', { assertion: 'Le ciel est bleu.', correct: true }),
      item(2, 'vf', { assertion: 'Autre.', correct: true }),
    ]
    const { wrapper } = await mountStudy('/revision/sets/7/study', HETEROGENEOUS_SET, items)

    await findButtonByText(wrapper, 'Faux')!.trigger('click')
    await flushPromises()
    await wrapper.find('[data-test="self-eval-moyen"]').trigger('click')
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith('/revision/sets/7/study/grade/1', {
      answer: { value: false },
      score: 3,
      duration_seconds: expect.any(Number),
    })
    expect(findButtonByText(wrapper, 'Suivant')).toBeDefined()
  })

  it('vf : correctCount reflete la correction reelle du check, independamment du score choisi ensuite', async () => {
    api.post.mockImplementation((url: string) => {
      // Reponse "value: false" jugee incorrecte par le backend, meme si
      // l'utilisateur se note ensuite "Acquis" (score 5) par erreur/exces de confiance.
      if (url === '/revision/sets/7/study/check/1') return Promise.resolve({ data: { correct: false } })
      if (url === '/revision/sets/7/study/grade/1') return Promise.resolve({ data: { correct: false, item: { id: 1 } } })
      return Promise.reject(new Error(`non mocké: ${url}`))
    })
    const items = [item(1, 'vf', { assertion: 'Le ciel est bleu.', correct: true })]
    const { wrapper } = await mountStudy('/revision/sets/7/study', HETEROGENEOUS_SET, items)

    await findButtonByText(wrapper, 'Faux')!.trigger('click')
    await flushPromises()
    await wrapper.find('[data-test="self-eval-acquis"]').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('0 bonne(s)')
  })

  it('association : check puis notation manuelle avant Suivant', async () => {
    api.post.mockImplementation((url: string) => {
      if (url === '/revision/sets/7/study/check/4') return Promise.resolve({ data: { correct: true } })
      if (url === '/revision/sets/7/study/grade/4') return Promise.resolve({ data: { correct: true, item: { id: 4 } } })
      return Promise.reject(new Error(`non mocké: ${url}`))
    })
    const items = [item(4, 'association', { pairs: [{ left: 'Chat', right: 'Cat' }] })]
    const { wrapper } = await mountStudy('/revision/sets/7/study', HETEROGENEOUS_SET, items)

    await wrapper.find('select').setValue('Cat')
    await findButtonByText(wrapper, 'Valider')!.trigger('click')
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith('/revision/sets/7/study/check/4', {
      answer: { matches: { Chat: 'Cat' } },
    })
    expect(wrapper.find('[data-test="self-eval-acquis"]').exists()).toBe(true)

    await wrapper.find('[data-test="self-eval-acquis"]').trigger('click')
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith('/revision/sets/7/study/grade/4', {
      answer: { matches: { Chat: 'Cat' } },
      score: 5,
      duration_seconds: expect.any(Number),
    })
    expect(findButtonByText(wrapper, 'Terminer')).toBeDefined()
  })

  it('ordre : check puis notation manuelle avant Suivant', async () => {
    api.post.mockImplementation((url: string) => {
      if (url === '/revision/sets/7/study/check/6') return Promise.resolve({ data: { correct: false } })
      if (url === '/revision/sets/7/study/grade/6') return Promise.resolve({ data: { correct: false, item: { id: 6 } } })
      return Promise.reject(new Error(`non mocké: ${url}`))
    })
    const items = [item(6, 'ordre', { steps: ['un', 'deux'] })]
    const { wrapper } = await mountStudy('/revision/sets/7/study', HETEROGENEOUS_SET, items)

    await findButtonByText(wrapper, 'Valider')!.trigger('click')
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith(
      '/revision/sets/7/study/check/6',
      expect.objectContaining({ answer: expect.objectContaining({ order: expect.any(Array) }) }),
    )
    expect(wrapper.find('[data-test="self-eval-a-revoir"]').exists()).toBe(true)

    await wrapper.find('[data-test="self-eval-a-revoir"]').trigger('click')
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith(
      '/revision/sets/7/study/grade/6',
      expect.objectContaining({ score: 1 }),
    )
    expect(findButtonByText(wrapper, 'Terminer')).toBeDefined()
  })
})
