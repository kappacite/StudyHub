import { defineStore } from 'pinia'
import { ref } from 'vue'
import notificationService, { type AppNotification } from '../services/notificationService'

export const useNotificationsStore = defineStore('notifications', () => {
  const items = ref<AppNotification[]>([])
  const unreadCount = ref(0)
  const loading = ref(false)

  async function fetchUnreadCount() {
    try {
      unreadCount.value = await notificationService.unreadCount()
    } catch {
      // silencieux : la cloche ne doit jamais bloquer l'UI
    }
  }

  async function fetchAll() {
    loading.value = true
    try {
      items.value = await notificationService.list()
      unreadCount.value = items.value.filter(n => !n.read).length
    } catch {
      items.value = []
    } finally {
      loading.value = false
    }
  }

  async function markRead(id: number) {
    const n = items.value.find(i => i.id === id)
    if (n && !n.read) {
      n.read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
      await notificationService.markRead(id)
    }
  }

  async function markAllRead() {
    items.value.forEach(n => (n.read = true))
    unreadCount.value = 0
    await notificationService.markAllRead()
  }

  return { items, unreadCount, loading, fetchUnreadCount, fetchAll, markRead, markAllRead }
})
