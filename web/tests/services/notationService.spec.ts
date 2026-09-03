import { describe, it, expect, vi, beforeEach } from 'vitest'
import { AxiosError, AxiosHeaders } from 'axios'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }))
vi.mock('../../src/services/api', () => ({ default: api }))

import notationService from '../../src/services/notationService'

function notFoundError() {
  return new AxiosError('Not Found', '404', undefined, undefined, {
    status: 404, statusText: 'Not Found', data: {}, headers: {}, config: { headers: new AxiosHeaders() },
  })
}

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

  // notes-ia-planning-corrections, Task 12 : persistance -- getExisting() permet au
  // frontend de proposer voir/reevaluer plutot que de relancer l'IA a chaque clic.
  // (import axios + champ updated_at ajoutes dans notationService.ts)
  it('getExisting(noteId) renvoie la notation deja enregistree', async () => {
    api.get.mockResolvedValue({ data: { score: 82, verdict: 'Bien.' } })
    const res = await notationService.getExisting('42')
    expect(api.get).toHaveBeenCalledWith('/notation/42')
    expect(res?.score).toBe(82)
  })

  it("getExisting(noteId) renvoie null (pas d'erreur) quand aucune notation n'existe (404)", async () => {
    api.get.mockRejectedValue(notFoundError())
    const res = await notationService.getExisting('42')
    expect(res).toBeNull()
  })

  it('getExisting(noteId) propage les erreurs autres que 404', async () => {
    api.get.mockRejectedValue(new Error('network down'))
    await expect(notationService.getExisting('42')).rejects.toThrow('network down')
  })
})
