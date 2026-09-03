import { describe, it, expect, vi, beforeEach } from 'vitest'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }))
vi.mock('../../src/services/api', () => ({ default: api }))

import notationService from '../../src/services/notationService'

describe('notationService — notes-ia-planning-corrections Task 5', () => {
  beforeEach(() => vi.clearAllMocks())

  it('grade(noteId) poste note_id vers /notation/grade', async () => {
    api.post.mockResolvedValue({ data: { status: 'SUCCESS', result: { score: 82 } } })
    const res = await notationService.grade('42')
    expect(api.post).toHaveBeenCalledWith('/notation/grade', { note_id: '42' })
    expect(res.result?.score).toBe(82)
  })

  it('pollTask(taskId) interroge /notation/tasks/:id', async () => {
    api.get.mockResolvedValue({ data: { status: 'PENDING' } })
    const res = await notationService.pollTask('t-1')
    expect(api.get).toHaveBeenCalledWith('/notation/tasks/t-1')
    expect(res.status).toBe('PENDING')
  })
})
