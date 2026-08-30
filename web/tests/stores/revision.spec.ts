import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

const api = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
}))
vi.mock('../../src/services/api', () => ({ default: api }))

import { useRevisionStore } from '../../src/stores/revision'

describe('revision store — ensembles typés (D3c)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('createSet envoie name/type/binder_id/tuning_default', async () => {
    api.post.mockResolvedValue({
      data: {
        id: 5,
        name: 'QCM',
        type: 'qcm',
        binder_id: null,
        tuning_default: 1,
        is_public: false,
        item_count: 0,
      },
    })
    const store = useRevisionStore()

    await store.createSet('QCM', 'qcm', null)

    expect(api.post).toHaveBeenCalledWith('/revision/sets', {
      name: 'QCM',
      type: 'qcm',
      description: null,
      binder_id: null,
      tuning_default: 1.0,
    })
    expect(store.sets).toHaveLength(1)
  })

  it('createItem poste le payload structuré et incrémente item_count', async () => {
    api.post
      .mockResolvedValueOnce({
        data: {
          id: 5,
          name: 'QCM',
          type: 'qcm',
          binder_id: null,
          tuning_default: 1,
          is_public: false,
          item_count: 0,
        },
      })
      .mockResolvedValueOnce({
        data: {
          id: 9,
          set_id: 5,
          payload: {},
          tuning: 1,
          position: 0,
          interval: 0,
          ease_factor: 2.5,
          repetitions: 0,
          next_review: '',
        },
      })
    const store = useRevisionStore()
    const set = await store.createSet('QCM', 'qcm', null)

    const payload = {
      question: 'Capitale ?',
      options: [
        { id: 'a', text: 'Lyon', correct: false },
        { id: 'b', text: 'Paris', correct: true },
      ],
    }
    await store.createItem(set.id, payload)

    expect(api.post).toHaveBeenLastCalledWith('/revision/sets/5/items', { payload, tuning: 1.0 })
    expect(store.sets[0].item_count).toBe(1)
  })

  it('updateItem envoie le payload modifié (PUT items/:id)', async () => {
    api.put.mockResolvedValue({
      data: {
        id: 9,
        set_id: 5,
        payload: {},
        tuning: 1,
        position: 0,
        interval: 0,
        ease_factor: 2.5,
        repetitions: 0,
        next_review: '',
      },
    })
    const store = useRevisionStore()

    const payload = {
      question: 'Modifiée ?',
      options: [
        { id: 'a', text: 'x', correct: true },
        { id: 'b', text: 'y', correct: false },
      ],
    }
    await store.updateItem(5, 9, payload)

    expect(api.put).toHaveBeenCalledWith('/revision/sets/5/items/9', { payload })
  })

  it('updateItem inclut tuning si fourni', async () => {
    api.put.mockResolvedValue({ data: { id: 9 } })
    const store = useRevisionStore()
    await store.updateItem(5, 9, { term: 't', definition: 'd' }, 1.5)
    expect(api.put).toHaveBeenCalledWith('/revision/sets/5/items/9', {
      payload: { term: 't', definition: 'd' },
      tuning: 1.5,
    })
  })

  it('deleteItem supprime et décrémente item_count', async () => {
    api.post
      .mockResolvedValueOnce({
        data: {
          id: 5,
          name: 'QCM',
          type: 'qcm',
          binder_id: null,
          tuning_default: 1,
          is_public: false,
          item_count: 0,
        },
      })
      .mockResolvedValueOnce({
        data: {
          id: 9,
          set_id: 5,
          payload: {},
          tuning: 1,
          position: 0,
          interval: 0,
          ease_factor: 2.5,
          repetitions: 0,
          next_review: '',
        },
      })
    api.delete.mockResolvedValue({ data: {} })
    const store = useRevisionStore()
    const set = await store.createSet('QCM', 'qcm', null)
    await store.createItem(set.id, {
      question: 'q',
      options: [
        { id: 'a', text: 'x', correct: true },
        { id: 'b', text: 'y', correct: false },
      ],
    })
    expect(store.sets[0].item_count).toBe(1)

    await store.deleteItem(5, 9)

    expect(api.delete).toHaveBeenCalledWith('/revision/sets/5/items/9')
    expect(store.sets[0].item_count).toBe(0)
  })

  it('checkQcmAnswer poste les options selectionnees et renvoie la correction, sans effet de bord (Task 6)', async () => {
    const checkResult = { correct: true, earned: 2, points: 2, correct_option_ids: ['b'] }
    api.post.mockResolvedValue({ data: checkResult })
    const store = useRevisionStore()

    const res = await store.checkQcmAnswer(5, 9, ['b'])

    expect(api.post).toHaveBeenCalledWith('/revision/sets/5/study/qcm-check/9', {
      selected_option_ids: ['b'],
    })
    expect(res).toEqual(checkResult)
  })

  it("answerQcmItem poste les options, le score choisi et la duree, et renvoie l'item mis a jour (Task 6)", async () => {
    const answerResult = {
      correct: true,
      earned: 2,
      points: 2,
      correct_option_ids: ['b'],
      item: { id: 9, set_id: 5 },
    }
    api.post.mockResolvedValue({ data: answerResult })
    const store = useRevisionStore()

    const res = await store.answerQcmItem(5, 9, ['b'], 5, 12)

    expect(api.post).toHaveBeenCalledWith('/revision/sets/5/study/qcm-answer/9', {
      selected_option_ids: ['b'],
      score: 5,
      duration_seconds: 12,
    })
    expect(res).toEqual(answerResult)
  })

  it('answerQcmItem utilise duration_seconds=0 par defaut quand non fourni', async () => {
    api.post.mockResolvedValue({
      data: { correct: false, earned: 0, points: 2, correct_option_ids: ['b'], item: { id: 9 } },
    })
    const store = useRevisionStore()

    await store.answerQcmItem(5, 9, [], 1)

    expect(api.post).toHaveBeenCalledWith('/revision/sets/5/study/qcm-answer/9', {
      selected_option_ids: [],
      score: 1,
      duration_seconds: 0,
    })
  })

  it('fetchStudyItems appelle /study sans parametre par defaut', async () => {
    api.get.mockResolvedValue({ data: [] })
    const store = useRevisionStore()

    await store.fetchStudyItems(5)

    expect(api.get).toHaveBeenCalledWith('/revision/sets/5/study')
  })

  it('fetchStudyItems ajoute ?include_not_due=true quand demande (Task 6)', async () => {
    api.get.mockResolvedValue({ data: [] })
    const store = useRevisionStore()

    await store.fetchStudyItems(5, true)

    expect(api.get).toHaveBeenCalledWith('/revision/sets/5/study?include_not_due=true')
  })

  it('checkItemAnswer poste la réponse et renvoie uniquement la correction, sans effet de bord (Task 5)', async () => {
    api.post.mockResolvedValue({ data: { correct: true } })
    const store = useRevisionStore()

    const res = await store.checkItemAnswer(5, 9, { value: false })

    expect(api.post).toHaveBeenCalledWith('/revision/sets/5/study/check/9', {
      answer: { value: false },
    })
    expect(res).toEqual({ correct: true })
  })

  it('gradeItem poste la réponse typée et le score choisi (obligatoire), et renvoie la correction (Task 5)', async () => {
    api.post.mockResolvedValue({ data: { correct: true, item: { id: 9 } } })
    const store = useRevisionStore()

    const res = await store.gradeItem(5, 9, { value: false }, 4)

    expect(api.post).toHaveBeenCalledWith('/revision/sets/5/study/grade/9', {
      answer: { value: false },
      score: 4,
      duration_seconds: 0,
    })
    expect(res.correct).toBe(true)
  })

  it('gradeItem inclut la duree postee quand elle est fournie (Task 9)', async () => {
    api.post.mockResolvedValue({ data: { correct: true, item: { id: 9 } } })
    const store = useRevisionStore()

    await store.gradeItem(5, 9, { value: false }, 4, 17)

    expect(api.post).toHaveBeenCalledWith('/revision/sets/5/study/grade/9', {
      answer: { value: false },
      score: 4,
      duration_seconds: 17,
    })
  })

  it('answerItem inclut la duree postee (0 par defaut, Task 9)', async () => {
    api.post.mockResolvedValue({ data: { id: 9 } })
    const store = useRevisionStore()

    await store.answerItem(5, 9, 5)

    expect(api.post).toHaveBeenCalledWith('/revision/sets/5/study/answer/9', {
      score: 5,
      duration_seconds: 0,
    })

    await store.answerItem(5, 9, 5, 30)

    expect(api.post).toHaveBeenCalledWith('/revision/sets/5/study/answer/9', {
      score: 5,
      duration_seconds: 30,
    })
  })

  it('fetchSetStats et fetchItemStats interrogent les endpoints stats', async () => {
    const store = useRevisionStore()
    api.get.mockResolvedValueOnce({ data: { set_id: 5, items: [], verdicts: [] } })
    await store.fetchSetStats(5)
    expect(api.get).toHaveBeenCalledWith('/stats/sets/5')

    api.get.mockResolvedValueOnce({ data: { item_id: 9, history: [] } })
    await store.fetchItemStats(9)
    expect(api.get).toHaveBeenCalledWith('/stats/items/9')
  })

  it('updateSet transmet name/tuning_default/binder_id (gestion C2)', async () => {
    api.post.mockResolvedValue({
      data: {
        id: 5,
        name: 'S',
        type: 'qcm',
        binder_id: null,
        tuning_default: 1,
        is_public: false,
        item_count: 0,
      },
    })
    const store = useRevisionStore()
    await store.createSet('S', 'qcm', null)

    api.put.mockResolvedValue({
      data: {
        id: 5,
        name: 'Renommé',
        type: 'qcm',
        binder_id: 'b1',
        tuning_default: 1.5,
        is_public: false,
        item_count: 0,
      },
    })
    await store.updateSet(5, { name: 'Renommé', tuning_default: 1.5, binder_id: 'b1' })

    expect(api.put).toHaveBeenCalledWith('/revision/sets/5', {
      name: 'Renommé',
      tuning_default: 1.5,
      binder_id: 'b1',
    })
    expect(store.sets[0].name).toBe('Renommé')
  })

  it('fetchBinderStats interroge le bon endpoint (avec/sans sous-arbre)', async () => {
    const store = useRevisionStore()
    api.get.mockResolvedValue({
      data: { binder_id: 'abc', sets: [], by_type: [], weakest_sets: [], verdicts: [] },
    })

    await store.fetchBinderStats('abc')
    expect(api.get).toHaveBeenCalledWith('/stats/binders/abc')

    await store.fetchBinderStats('abc', false)
    expect(api.get).toHaveBeenCalledWith('/stats/binders/abc?descendants=false')
  })

  it('createSet accepte type: null et transmet description (ensemble heterogene)', async () => {
    api.post.mockResolvedValue({
      data: {
        id: 7,
        name: 'Mixte',
        description: 'desc',
        type: null,
        binder_id: null,
        tuning_default: 1,
        is_public: false,
        item_count: 0,
      },
    })
    const store = useRevisionStore()

    await store.createSet('Mixte', null, 'desc')

    expect(api.post).toHaveBeenCalledWith('/revision/sets', {
      name: 'Mixte',
      type: null,
      description: 'desc',
      binder_id: null,
      tuning_default: 1.0,
    })
    expect(store.sets[0].type).toBeNull()
  })

  it('createItem transmet le type explicite quand fourni (ensemble heterogene)', async () => {
    api.post
      .mockResolvedValueOnce({
        data: {
          id: 7,
          name: 'Mixte',
          description: null,
          type: null,
          binder_id: null,
          tuning_default: 1,
          is_public: false,
          item_count: 0,
        },
      })
      .mockResolvedValueOnce({
        data: {
          id: 20,
          set_id: 7,
          type: 'flashcard',
          payload: { front: 'Chat', back: 'Cat' },
          tuning: 1,
          position: 0,
          interval: 0,
          ease_factor: 2.5,
          repetitions: 0,
          next_review: '',
          created_at: '2026-08-28T00:00:00Z',
          updated_at: '2026-08-28T00:00:00Z',
        },
      })
    const store = useRevisionStore()
    const set = await store.createSet('Mixte', null)

    await store.createItem(set.id, { front: 'Chat', back: 'Cat' }, 'flashcard')

    expect(api.post).toHaveBeenLastCalledWith('/revision/sets/7/items', {
      payload: { front: 'Chat', back: 'Cat' },
      type: 'flashcard',
      tuning: 1.0,
    })
  })

  it('createItem omet type quand absent (retrocompatibilite existante)', async () => {
    api.post
      .mockResolvedValueOnce({
        data: {
          id: 8,
          name: 'QCM',
          description: null,
          type: 'qcm',
          binder_id: null,
          tuning_default: 1,
          is_public: false,
          item_count: 0,
        },
      })
      .mockResolvedValueOnce({
        data: {
          id: 21,
          set_id: 8,
          type: 'qcm',
          payload: {},
          tuning: 1,
          position: 0,
          interval: 0,
          ease_factor: 2.5,
          repetitions: 0,
          next_review: '',
          created_at: '',
          updated_at: '',
        },
      })
    const store = useRevisionStore()
    const set = await store.createSet('QCM', 'qcm')

    await store.createItem(set.id, { question: 'q', options: [] })

    expect(api.post).toHaveBeenLastCalledWith('/revision/sets/8/items', {
      payload: { question: 'q', options: [] },
      tuning: 1.0,
    })
  })
})
