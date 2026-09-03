import { describe, it, expect, vi, beforeEach } from 'vitest'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }))
vi.mock('../../src/services/api', () => ({ default: api }))

import planningService from '../../src/services/planningService'

describe('planningService — notes-ia-planning-corrections Task 2 (kind deck/revision_set)', () => {
  beforeEach(() => vi.clearAllMocks())

  it('advanceReview("deck", ...) poste deck_id', async () => {
    api.post.mockResolvedValue({ data: [] })
    await planningService.advanceReview('deck', 5, [1, 2], '2026-09-10')
    expect(api.post).toHaveBeenCalledWith('/planning/advance', {
      deck_id: 5,
      set_id: null,
      card_ids: [1, 2],
      date: '2026-09-10',
    })
  })

  it('advanceReview("revision_set", ...) poste set_id', async () => {
    api.post.mockResolvedValue({ data: [] })
    await planningService.advanceReview('revision_set', 7, [3], null)
    expect(api.post).toHaveBeenCalledWith('/planning/advance', {
      deck_id: null,
      set_id: 7,
      card_ids: [3],
      date: null,
    })
  })
})
