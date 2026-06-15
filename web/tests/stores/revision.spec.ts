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

  it('runQcm poste les réponses et renvoie le score pondéré', async () => {
    const runResult = { score: 3, max_score: 4, percentage: 75, results: [] }
    api.post.mockResolvedValue({ data: runResult })
    const store = useRevisionStore()

    const answers = [{ item_id: 9, selected_option_ids: ['b'] }]
    const res = await store.runQcm(5, answers)

    expect(api.post).toHaveBeenCalledWith('/revision/sets/5/run', { answers })
    expect(res).toEqual(runResult)
  })
})
