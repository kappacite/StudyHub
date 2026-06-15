import { describe, it, expect, vi, beforeEach } from 'vitest'

const api = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
}))
vi.mock('../../src/services/api', () => ({ default: api }))

import groupService from '../../src/services/groupService'

describe('groupService — partage classeur à la classe (B2)', () => {
  beforeEach(() => vi.clearAllMocks())

  it('getBinderClasses interroge le bon endpoint (indicateur « partagé »)', async () => {
    api.get.mockResolvedValue({ data: [{ id: 3, name: 'Classe SVT', permission: 'read' }] })
    const res = await groupService.getBinderClasses('abc-uuid')
    expect(api.get).toHaveBeenCalledWith('/groups/binders/abc-uuid/classes')
    expect(res[0].name).toBe('Classe SVT')
  })

  it('shareBinder partage par référence en lecture seule', async () => {
    api.post.mockResolvedValue({ data: {} })
    await groupService.shareBinder(3, 'abc-uuid', 'read')
    expect(api.post).toHaveBeenCalledWith('/groups/3/binders', {
      binder_id: 'abc-uuid',
      permission: 'read',
    })
  })

  it('unshareBinder retire le partage de la classe', async () => {
    api.delete.mockResolvedValue({})
    await groupService.unshareBinder(3, 'abc-uuid')
    expect(api.delete).toHaveBeenCalledWith('/groups/3/binders/abc-uuid')
  })
})
