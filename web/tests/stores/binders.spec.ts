import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

const api = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
}))
vi.mock('../../src/services/api', () => ({ default: api }))

import { useBindersStore } from '../../src/stores/binders'

describe('binders store — rattacher/détacher des éléments (C1)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('attachItems poste les éléments et renvoie le nombre rattaché', async () => {
    api.post.mockResolvedValue({ data: { attached: 2 } })
    const store = useBindersStore()

    const items = [{ type: 'note' as const, id: 'abc' }, { type: 'deck' as const, id: 5 }]
    const n = await store.attachItems('binder-uuid', items)

    expect(api.post).toHaveBeenCalledWith('/binders/binder-uuid/items', { items })
    expect(n).toBe(2)
  })

  it('detachItems poste vers le bon endpoint et renvoie le nombre détaché', async () => {
    api.post.mockResolvedValue({ data: { detached: 1 } })
    const store = useBindersStore()

    const items = [{ type: 'set' as const, id: 9 }]
    const n = await store.detachItems('binder-uuid', items)

    expect(api.post).toHaveBeenCalledWith('/binders/binder-uuid/items/detach', { items })
    expect(n).toBe(1)
  })
})
