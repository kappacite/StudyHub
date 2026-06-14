import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

const api = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  patch: vi.fn(),
}))
vi.mock('../../src/services/api', () => ({ default: api }))

import { useNotificationsStore } from '../../src/stores/notifications'

describe('notifications store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetchAll charge les notifications et calcule le nombre de non lues', async () => {
    api.get.mockResolvedValueOnce({
      data: [
        { id: 1, type: 'announcement', title: 'A', body: null, link: null, read: false, created_at: '' },
        { id: 2, type: 'new_assignment', title: 'B', body: null, link: null, read: true, created_at: '' },
      ],
    })
    const store = useNotificationsStore()
    await store.fetchAll()
    expect(store.items).toHaveLength(2)
    expect(store.unreadCount).toBe(1)
  })

  it('markRead marque localement et décrémente le compteur', async () => {
    api.get.mockResolvedValueOnce({
      data: [{ id: 1, type: 'announcement', title: 'A', body: null, link: null, read: false, created_at: '' }],
    })
    api.patch.mockResolvedValueOnce({})
    const store = useNotificationsStore()
    await store.fetchAll()
    expect(store.unreadCount).toBe(1)

    await store.markRead(1)
    expect(store.items[0].read).toBe(true)
    expect(store.unreadCount).toBe(0)
    expect(api.patch).toHaveBeenCalledWith('/notifications/1/read')
  })

  it('markAllRead remet le compteur à zéro', async () => {
    api.get.mockResolvedValueOnce({
      data: [
        { id: 1, type: 'a', title: 'A', body: null, link: null, read: false, created_at: '' },
        { id: 2, type: 'a', title: 'B', body: null, link: null, read: false, created_at: '' },
      ],
    })
    api.post.mockResolvedValueOnce({})
    const store = useNotificationsStore()
    await store.fetchAll()
    expect(store.unreadCount).toBe(2)

    await store.markAllRead()
    expect(store.unreadCount).toBe(0)
    expect(store.items.every(n => n.read)).toBe(true)
    expect(api.post).toHaveBeenCalledWith('/notifications/read-all')
  })
})
