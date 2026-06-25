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
    api.post.mockResolvedValue({ data: { id: 5, name: 'QCM', type: 'qcm', binder_id: null, tuning_default: 1, is_public: false, item_count: 0 } })
    const store = useRevisionStore()

    await store.createSet('QCM', 'qcm', null)

    expect(api.post).toHaveBeenCalledWith('/revision/sets', {
      name: 'QCM',
      type: 'qcm',
      binder_id: null,
      tuning_default: 1.0,
    })
    expect(store.sets).toHaveLength(1)
  })

  it('createItem poste le payload structuré et incrémente item_count', async () => {
    api.post
      .mockResolvedValueOnce({ data: { id: 5, name: 'QCM', type: 'qcm', binder_id: null, tuning_default: 1, is_public: false, item_count: 0 } })
      .mockResolvedValueOnce({ data: { id: 9, set_id: 5, payload: {}, tuning: 1, position: 0, interval: 0, ease_factor: 2.5, repetitions: 0, next_review: '' } })
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
    api.put.mockResolvedValue({ data: { id: 9, set_id: 5, payload: {}, tuning: 1, position: 0, interval: 0, ease_factor: 2.5, repetitions: 0, next_review: '' } })
    const store = useRevisionStore()

    const payload = { question: 'Modifiée ?', options: [{ id: 'a', text: 'x', correct: true }, { id: 'b', text: 'y', correct: false }] }
    await store.updateItem(5, 9, payload)

    expect(api.put).toHaveBeenCalledWith('/revision/sets/5/items/9', { payload })
  })

  it('updateItem inclut tuning si fourni', async () => {
    api.put.mockResolvedValue({ data: { id: 9 } })
    const store = useRevisionStore()
    await store.updateItem(5, 9, { term: 't', definition: 'd' }, 1.5)
    expect(api.put).toHaveBeenCalledWith('/revision/sets/5/items/9', { payload: { term: 't', definition: 'd' }, tuning: 1.5 })
  })

  it('deleteItem supprime et décrémente item_count', async () => {
    api.post
      .mockResolvedValueOnce({ data: { id: 5, name: 'QCM', type: 'qcm', binder_id: null, tuning_default: 1, is_public: false, item_count: 0 } })
      .mockResolvedValueOnce({ data: { id: 9, set_id: 5, payload: {}, tuning: 1, position: 0, interval: 0, ease_factor: 2.5, repetitions: 0, next_review: '' } })
    api.delete.mockResolvedValue({ data: {} })
    const store = useRevisionStore()
    const set = await store.createSet('QCM', 'qcm', null)
    await store.createItem(set.id, { question: 'q', options: [{ id: 'a', text: 'x', correct: true }, { id: 'b', text: 'y', correct: false }] })
    expect(store.sets[0].item_count).toBe(1)

    await store.deleteItem(5, 9)

    expect(api.delete).toHaveBeenCalledWith('/revision/sets/5/items/9')
    expect(store.sets[0].item_count).toBe(0)
  })

  it('runQcm poste les réponses et renvoie le score pondéré', async () => {
    const runResult = { score: 3, max_score: 4, percentage: 75, results: [] }
    api.post.mockResolvedValue({ data: runResult })
    const store = useRevisionStore()

    const answers = [{ item_id: 9, selected_option_ids: ['b'] }]
    const res = await store.runQcm(5, answers)

    expect(api.post).toHaveBeenCalledWith('/revision/sets/5/run', { answers })
    expect(res).toEqual(runResult)
  })

  it('gradeItem poste la réponse typée et renvoie la correction', async () => {
    api.post.mockResolvedValue({ data: { correct: true, item: { id: 9 } } })
    const store = useRevisionStore()

    const res = await store.gradeItem(5, 9, { value: false })

    expect(api.post).toHaveBeenCalledWith('/revision/sets/5/study/grade/9', { answer: { value: false } })
    expect(res.correct).toBe(true)
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
    api.post.mockResolvedValue({ data: { id: 5, name: 'S', type: 'qcm', binder_id: null, tuning_default: 1, is_public: false, item_count: 0 } })
    const store = useRevisionStore()
    await store.createSet('S', 'qcm', null)

    api.put.mockResolvedValue({ data: { id: 5, name: 'Renommé', type: 'qcm', binder_id: 'b1', tuning_default: 1.5, is_public: false, item_count: 0 } })
    await store.updateSet(5, { name: 'Renommé', tuning_default: 1.5, binder_id: 'b1' })

    expect(api.put).toHaveBeenCalledWith('/revision/sets/5', { name: 'Renommé', tuning_default: 1.5, binder_id: 'b1' })
    expect(store.sets[0].name).toBe('Renommé')
  })

  it('fetchBinderStats interroge le bon endpoint (avec/sans sous-arbre)', async () => {
    const store = useRevisionStore()
    api.get.mockResolvedValue({ data: { binder_id: 'abc', sets: [], by_type: [], weakest_sets: [], verdicts: [] } })

    await store.fetchBinderStats('abc')
    expect(api.get).toHaveBeenCalledWith('/stats/binders/abc')

    await store.fetchBinderStats('abc', false)
    expect(api.get).toHaveBeenCalledWith('/stats/binders/abc?descendants=false')
  })
})
