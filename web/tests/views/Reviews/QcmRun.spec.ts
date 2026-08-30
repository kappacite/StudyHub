import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import QcmRun from '../../../src/views/Reviews/QcmRun.vue'

const SET = {
  id: 7,
  name: 'QCM Histoire',
  description: null,
  type: 'qcm',
  binder_id: null,
  tuning_default: 1,
  is_public: false,
  item_count: 1,
}

function question(id: number, overrides: Record<string, unknown> = {}) {
  return {
    id,
    set_id: 7,
    type: 'qcm',
    payload: {
      question: 'Capitale de la France ?',
      points: 2,
      options: [
        { id: 'a', text: 'Lyon', correct: false },
        { id: 'b', text: 'Paris', correct: true },
      ],
    },
    tuning: 1,
    position: 0,
    interval: 0,
    ease_factor: 2.5,
    repetitions: 0,
    next_review: '',
    created_at: '',
    updated_at: '',
    ...overrides,
  }
}

const stub = { template: '<div />' }
function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/revision/sets/:id/run', name: 'QcmRun', component: stub }],
  })
}

async function mountQcmRun(items: unknown[]) {
  const pinia = createPinia()
  setActivePinia(pinia)
  api.get.mockImplementation((url: string) => {
    if (/\/revision\/sets\/\d+$/.test(url)) return Promise.resolve({ data: SET })
    if (/\/revision\/sets\/\d+\/study(\?.*)?$/.test(url)) return Promise.resolve({ data: items })
    return Promise.reject(new Error(`non mocké: ${url}`))
  })
  const router = createTestRouter()
  await router.push('/revision/sets/7/run')
  await router.isReady()
  const wrapper = mount(QcmRun, { global: { plugins: [pinia, router] } })
  await flushPromises()
  return wrapper
}

function findButtonByText(wrapper: ReturnType<typeof mount>, text: string) {
  return wrapper.findAll('button').find((b) => b.text() === text)
}

describe('QcmRun — navigation question par question (Task 6)', () => {
  beforeEach(() => vi.clearAllMocks())

  it('affiche une seule question a la fois en phase answer, pas tout le lot', async () => {
    const items = [
      question(1, {
        payload: { question: 'Q1 ?', points: 1, options: [{ id: 'a', text: 'A', correct: true }] },
      }),
      question(2, {
        payload: { question: 'Q2 ?', points: 1, options: [{ id: 'a', text: 'A', correct: true }] },
      }),
    ]
    const wrapper = await mountQcmRun(items)

    expect(wrapper.text()).toContain('Q1 ?')
    expect(wrapper.text()).not.toContain('Q2 ?')
  })

  it('valider une question appelle checkQcmAnswer (qcm-check) et affiche la correction + boutons de notation, pas encore Suivant', async () => {
    api.post.mockImplementation((url: string) => {
      if (url === '/revision/sets/7/study/qcm-check/1') {
        return Promise.resolve({
          data: { correct: true, earned: 2, points: 2, correct_option_ids: ['b'] },
        })
      }
      return Promise.reject(new Error(`non mocké: ${url}`))
    })
    const wrapper = await mountQcmRun([question(1)])

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    await checkboxes[1].setValue(true) // option "b", correcte
    await findButtonByText(wrapper, 'Valider')!.trigger('click')
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith('/revision/sets/7/study/qcm-check/1', {
      selected_option_ids: ['b'],
    })
    expect(wrapper.find('[data-test="self-eval-a-revoir"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="self-eval-moyen"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="self-eval-acquis"]').exists()).toBe(true)
    expect(findButtonByText(wrapper, 'Suivant')).toBeUndefined()
    expect(findButtonByText(wrapper, 'Terminer')).toBeUndefined()
  })

  it('choisir une note appelle answerQcmItem (qcm-answer) avec le score choisi, puis affiche Suivant', async () => {
    api.post.mockImplementation((url: string) => {
      if (url === '/revision/sets/7/study/qcm-check/1') {
        return Promise.resolve({
          data: { correct: true, earned: 2, points: 2, correct_option_ids: ['b'] },
        })
      }
      if (url === '/revision/sets/7/study/qcm-answer/1') {
        return Promise.resolve({
          data: { correct: true, earned: 2, points: 2, correct_option_ids: ['b'], item: { id: 1 } },
        })
      }
      return Promise.reject(new Error(`non mocké: ${url}`))
    })
    const items = [question(1), question(2)]
    const wrapper = await mountQcmRun(items)

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    await checkboxes[1].setValue(true)
    await findButtonByText(wrapper, 'Valider')!.trigger('click')
    await flushPromises()

    await wrapper.find('[data-test="self-eval-acquis"]').trigger('click')
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith('/revision/sets/7/study/qcm-answer/1', {
      selected_option_ids: ['b'],
      score: 5,
      duration_seconds: expect.any(Number),
    })
    expect(findButtonByText(wrapper, 'Suivant')).toBeDefined()
  })

  it('cliquer Suivant avance a la question suivante, encore en phase answer', async () => {
    api.post.mockImplementation((url: string) => {
      if (url === '/revision/sets/7/study/qcm-check/1') {
        return Promise.resolve({
          data: { correct: true, earned: 2, points: 2, correct_option_ids: ['b'] },
        })
      }
      if (url === '/revision/sets/7/study/qcm-answer/1') {
        return Promise.resolve({
          data: { correct: true, earned: 2, points: 2, correct_option_ids: ['b'], item: { id: 1 } },
        })
      }
      return Promise.reject(new Error(`non mocké: ${url}`))
    })
    const items = [
      question(1, {
        payload: {
          question: 'Q1 ?',
          points: 2,
          options: [
            { id: 'a', text: 'Lyon', correct: false },
            { id: 'b', text: 'Paris', correct: true },
          ],
        },
      }),
      question(2, {
        payload: { question: 'Q2 ?', points: 1, options: [{ id: 'a', text: 'A', correct: true }] },
      }),
    ]
    const wrapper = await mountQcmRun(items)

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    await checkboxes[1].setValue(true)
    await findButtonByText(wrapper, 'Valider')!.trigger('click')
    await flushPromises()
    await wrapper.find('[data-test="self-eval-acquis"]').trigger('click')
    await flushPromises()
    await findButtonByText(wrapper, 'Suivant')!.trigger('click')

    expect(wrapper.text()).toContain('Q2 ?')
    expect(wrapper.text()).not.toContain('Q1 ?')
    expect(findButtonByText(wrapper, 'Valider')).toBeDefined()
  })

  it('agrege correctement le score final sur plusieurs questions avec des points differents', async () => {
    api.post.mockImplementation((url: string) => {
      if (url === '/revision/sets/7/study/qcm-check/1') {
        return Promise.resolve({
          data: { correct: true, earned: 2, points: 2, correct_option_ids: ['b'] },
        })
      }
      if (url === '/revision/sets/7/study/qcm-answer/1') {
        return Promise.resolve({
          data: { correct: true, earned: 2, points: 2, correct_option_ids: ['b'], item: { id: 1 } },
        })
      }
      if (url === '/revision/sets/7/study/qcm-check/2') {
        return Promise.resolve({
          data: { correct: false, earned: 0, points: 3, correct_option_ids: ['x'] },
        })
      }
      if (url === '/revision/sets/7/study/qcm-answer/2') {
        return Promise.resolve({
          data: {
            correct: false,
            earned: 0,
            points: 3,
            correct_option_ids: ['x'],
            item: { id: 2 },
          },
        })
      }
      return Promise.reject(new Error(`non mocké: ${url}`))
    })
    const items = [
      question(1, {
        payload: {
          question: 'Q1 ?',
          points: 2,
          options: [
            { id: 'a', text: 'Lyon', correct: false },
            { id: 'b', text: 'Paris', correct: true },
          ],
        },
      }),
      question(2, {
        payload: {
          question: 'Q2 ?',
          points: 3,
          options: [
            { id: 'x', text: 'X', correct: true },
            { id: 'y', text: 'Y', correct: false },
          ],
        },
      }),
    ]
    const wrapper = await mountQcmRun(items)

    // Q1 : reponse correcte
    let checkboxes = wrapper.findAll('input[type="checkbox"]')
    await checkboxes[1].setValue(true)
    await findButtonByText(wrapper, 'Valider')!.trigger('click')
    await flushPromises()
    await wrapper.find('[data-test="self-eval-acquis"]').trigger('click')
    await flushPromises()
    await findButtonByText(wrapper, 'Suivant')!.trigger('click')

    // Q2 : reponse incorrecte (case "y" cochee)
    checkboxes = wrapper.findAll('input[type="checkbox"]')
    await checkboxes[1].setValue(true)
    await findButtonByText(wrapper, 'Valider')!.trigger('click')
    await flushPromises()
    await wrapper.find('[data-test="self-eval-a-revoir"]').trigger('click')
    await flushPromises()
    await findButtonByText(wrapper, 'Terminer')!.trigger('click')

    expect(wrapper.text()).toContain('2 / 5 points')
    expect(wrapper.text()).toContain('40 %')
  })
})

describe('QcmRun — garde anti double-soumission (revue finale de branche)', () => {
  beforeEach(() => vi.clearAllMocks())

  it("un double-clic sur \"Valider\" pendant l'appel qcm-check en cours n'appelle checkQcmAnswer qu'une seule fois", async () => {
    let resolveCheck!: (v: unknown) => void
    const pending = new Promise((resolve) => {
      resolveCheck = resolve
    })
    api.post.mockImplementation((url: string) => {
      if (url === '/revision/sets/7/study/qcm-check/1') return pending
      return Promise.reject(new Error(`non mocké: ${url}`))
    })
    const wrapper = await mountQcmRun([question(1)])

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    await checkboxes[1].setValue(true)
    const validerBtn = findButtonByText(wrapper, 'Valider')!
    await validerBtn.trigger('click')
    await validerBtn.trigger('click')
    resolveCheck({ data: { correct: true, earned: 2, points: 2, correct_option_ids: ['b'] } })
    await flushPromises()

    expect(api.post).toHaveBeenCalledTimes(1)
  })

  it("un double-clic sur un bouton de notation pendant l'appel qcm-answer en cours n'appelle answerQcmItem qu'une seule fois", async () => {
    let resolveAnswer!: (v: unknown) => void
    const pending = new Promise((resolve) => {
      resolveAnswer = resolve
    })
    api.post.mockImplementation((url: string) => {
      if (url === '/revision/sets/7/study/qcm-check/1') {
        return Promise.resolve({
          data: { correct: true, earned: 2, points: 2, correct_option_ids: ['b'] },
        })
      }
      if (url === '/revision/sets/7/study/qcm-answer/1') return pending
      return Promise.reject(new Error(`non mocké: ${url}`))
    })
    const wrapper = await mountQcmRun([question(1)])

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    await checkboxes[1].setValue(true)
    await findButtonByText(wrapper, 'Valider')!.trigger('click')
    await flushPromises()

    const acquisBtn = wrapper.find('[data-test="self-eval-acquis"]')
    await acquisBtn.trigger('click')
    await acquisBtn.trigger('click')
    resolveAnswer({
      data: { correct: true, earned: 2, points: 2, correct_option_ids: ['b'], item: { id: 1 } },
    })
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith('/revision/sets/7/study/qcm-answer/1', expect.anything())
    expect(api.post).toHaveBeenCalledTimes(2) // 1x qcm-check + 1x qcm-answer (pas 2x)
  })
})

describe('QcmRun — revision libre sur liste vide (Task 6)', () => {
  beforeEach(() => vi.clearAllMocks())

  it('etat vide : bouton "Reviser quand meme" relance fetchStudyItems avec include_not_due=true et affiche les questions', async () => {
    const wrapper = await mountQcmRun([])
    expect(wrapper.text()).toContain("Aucune question à réviser pour l'instant")

    const alreadyAnswered = question(9, {
      next_review: '2099-01-01T00:00:00Z',
      payload: {
        question: 'Deja repondue ?',
        points: 1,
        options: [{ id: 'a', text: 'A', correct: true }],
      },
    })
    api.get.mockImplementation((url: string) => {
      if (/\/revision\/sets\/\d+$/.test(url)) return Promise.resolve({ data: SET })
      if (url === '/revision/sets/7/study?include_not_due=true') {
        return Promise.resolve({ data: [alreadyAnswered] })
      }
      if (/\/revision\/sets\/\d+\/study$/.test(url)) return Promise.resolve({ data: [] })
      return Promise.reject(new Error(`non mocké: ${url}`))
    })

    await findButtonByText(wrapper, 'Réviser quand même')!.trigger('click')
    await flushPromises()

    expect(api.get).toHaveBeenCalledWith('/revision/sets/7/study?include_not_due=true')
    expect(wrapper.text()).toContain('Deja repondue ?')
  })
})
