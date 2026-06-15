import { describe, it, expect, vi, beforeEach } from 'vitest'

const api = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
}))
vi.mock('../../src/services/api', () => ({ default: api }))

import classService from '../../src/services/classService'

describe('classService — questions (Q&A, B4)', () => {
  beforeEach(() => vi.clearAllMocks())

  it('listQuestions interroge le bon endpoint', async () => {
    api.get.mockResolvedValue({ data: [] })
    await classService.listQuestions(7)
    expect(api.get).toHaveBeenCalledWith('/classes/7/questions')
  })

  it('postQuestion envoie le corps de la question', async () => {
    api.post.mockResolvedValue({ data: { id: 1, body: 'Q', status: 'open' } })
    await classService.postQuestion(7, 'Pourquoi ?')
    expect(api.post).toHaveBeenCalledWith('/classes/7/questions', { body: 'Pourquoi ?' })
  })

  it('answerQuestion poste la réponse vers le bon endpoint', async () => {
    api.post.mockResolvedValue({ data: { id: 1, body: 'Q', answer: 'A', status: 'answered' } })
    await classService.answerQuestion(7, 1, 'Parce que')
    expect(api.post).toHaveBeenCalledWith('/classes/7/questions/1/answer', { body: 'Parce que' })
  })
})
