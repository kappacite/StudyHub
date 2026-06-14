import api from './api'

export interface AppNotification {
  id: number
  type: string
  title: string
  body: string | null
  link: string | null
  read: boolean
  created_at: string
}

const notificationService = {
  async list(unreadOnly = false): Promise<AppNotification[]> {
    const resp = await api.get<AppNotification[]>('/notifications', {
      params: unreadOnly ? { unread: 1 } : {},
    })
    return resp.data
  },

  async unreadCount(): Promise<number> {
    const resp = await api.get<{ count: number }>('/notifications/unread-count')
    return resp.data.count
  },

  async markRead(id: number): Promise<void> {
    await api.patch(`/notifications/${id}/read`)
  },

  async markAllRead(): Promise<void> {
    await api.post('/notifications/read-all')
  },
}

export default notificationService
