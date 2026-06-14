<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationsStore } from '../../stores/notifications'
import { Bell, Check, Loader2 } from 'lucide-vue-next'

const store = useNotificationsStore()
const router = useRouter()
const open = ref(false)
let poll: ReturnType<typeof setInterval> | null = null

async function toggle() {
  open.value = !open.value
  if (open.value) await store.fetchAll()
}

async function onClickNotification(id: number, link: string | null) {
  await store.markRead(id)
  open.value = false
  if (link) router.push(link)
}

function timeAgo(iso: string): string {
  const diff = (Date.now() - new Date(iso).getTime()) / 60000
  if (diff < 1) return "à l'instant"
  if (diff < 60) return `il y a ${Math.round(diff)} min`
  if (diff < 1440) return `il y a ${Math.round(diff / 60)} h`
  return `il y a ${Math.round(diff / 1440)} j`
}

onMounted(() => {
  store.fetchUnreadCount()
  // Rafraîchit le compteur périodiquement (léger).
  poll = setInterval(() => store.fetchUnreadCount(), 60000)
})

onUnmounted(() => {
  if (poll) clearInterval(poll)
})
</script>

<template>
  <div class="relative">
    <button
      @click="toggle"
      class="relative p-2 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 dark:hover:text-slate-100 transition-colors"
      title="Notifications"
    >
      <Bell class="w-5 h-5" />
      <span
        v-if="store.unreadCount > 0"
        class="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 flex items-center justify-center rounded-full bg-rose-500 text-white text-[10px] font-bold"
      >
        {{ store.unreadCount > 9 ? '9+' : store.unreadCount }}
      </span>
    </button>

    <!-- Backdrop -->
    <div v-if="open" class="fixed inset-0 z-40" @click="open = false"></div>

    <!-- Dropdown -->
    <div
      v-if="open"
      class="absolute right-0 mt-2 w-80 max-h-96 overflow-y-auto z-50 bg-white dark:bg-slate-800 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-700"
    >
      <div class="flex items-center justify-between px-4 py-3 border-b border-slate-100 dark:border-slate-700">
        <span class="font-bold text-sm text-slate-800 dark:text-white">Notifications</span>
        <button
          v-if="store.unreadCount > 0"
          @click="store.markAllRead()"
          class="text-[11px] font-semibold text-indigo-500 hover:text-indigo-600 flex items-center gap-1"
        >
          <Check class="w-3 h-3" /> Tout lire
        </button>
      </div>

      <div v-if="store.loading" class="flex items-center justify-center py-6">
        <Loader2 class="w-5 h-5 text-indigo-500 animate-spin" />
      </div>
      <div v-else-if="store.items.length === 0" class="px-4 py-8 text-center text-xs text-slate-400">
        Aucune notification.
      </div>
      <ul v-else class="divide-y divide-slate-50 dark:divide-slate-700/50">
        <li
          v-for="n in store.items"
          :key="n.id"
          @click="onClickNotification(n.id, n.link)"
          class="px-4 py-3 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-900/40 transition-colors"
          :class="{ 'bg-indigo-50/40 dark:bg-indigo-950/10': !n.read }"
        >
          <div class="flex items-start gap-2">
            <span v-if="!n.read" class="mt-1.5 w-2 h-2 rounded-full bg-indigo-500 flex-shrink-0"></span>
            <span v-else class="mt-1.5 w-2 h-2 flex-shrink-0"></span>
            <div class="min-w-0">
              <p class="text-xs font-semibold text-slate-800 dark:text-white truncate">{{ n.title }}</p>
              <p v-if="n.body" class="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2">{{ n.body }}</p>
              <p class="text-[10px] text-slate-400 mt-0.5">{{ timeAgo(n.created_at) }}</p>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>
