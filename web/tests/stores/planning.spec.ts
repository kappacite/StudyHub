import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }))
vi.mock('../../src/services/api', () => ({ default: api }))

import { usePlanningStore } from '../../src/stores/planning'

describe('planning store — notes-ia-planning-corrections Task 2 (kind deck/revision_set)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('prepareAdvanceReview("revision_set", id) poste set_id via planningService, ne remplit pas advanceReviewCards (deck-only)', async () => {
    api.post.mockResolvedValue({ data: [{ id: 1 }] })
    const store = usePlanningStore()
    const items = await store.prepareAdvanceReview('revision_set', 9, '2026-09-10')
    expect(items).toEqual([{ id: 1 }])
    expect(store.advanceReviewCards).toEqual([])
    expect(api.post).toHaveBeenCalledWith('/planning/advance', {
      deck_id: null,
      set_id: 9,
      card_ids: [],
      date: '2026-09-10',
    })
  })

  it('prepareAdvanceReview propage l\'erreur en err instanceof Error, pas any', async () => {
    api.post.mockRejectedValue(new Error('boom'))
    const store = usePlanningStore()
    await expect(store.prepareAdvanceReview('deck', 4)).rejects.toThrow('boom')
    expect(store.error).toBe('boom')
  })

  it('prepareAdvanceReview("deck", id) poste deck_id (non-regression)', async () => {
    api.post.mockResolvedValue({ data: [{ id: 2 }] })
    const store = usePlanningStore()
    await store.prepareAdvanceReview('deck', 4, '2026-09-10')
    expect(api.post).toHaveBeenCalledWith('/planning/advance', {
      deck_id: 4,
      set_id: null,
      card_ids: [],
      date: '2026-09-10',
    })
  })
})
