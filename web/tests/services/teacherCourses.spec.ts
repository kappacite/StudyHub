import { describe, it, expect, vi, beforeEach } from 'vitest'

const api = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
}))
vi.mock('../../src/services/api', () => ({ default: api }))

import classService from '../../src/services/classService'

describe('classService — dépôt de cours (B1)', () => {
  beforeEach(() => vi.clearAllMocks())

  it('getCourseBinder résout/crée le classeur de cours de la classe', async () => {
    api.post.mockResolvedValue({ data: { binder_id: 'uuid-cours', name: 'Cours — Bio', created: true } })
    const res = await classService.getCourseBinder(42)
    expect(api.post).toHaveBeenCalledWith('/classes/42/course-binder')
    expect(res.binder_id).toBe('uuid-cours')
    expect(res.created).toBe(true)
  })
})
