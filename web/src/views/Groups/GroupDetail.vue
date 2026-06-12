<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGroupsStore } from '../../stores/groups'
import { useAuthStore } from '../../stores/auth'
import { useBindersStore } from '../../stores/binders'
import {
  Users, BookOpen, Activity, BarChart3, ArrowLeft,
  Copy, Check, Loader2, AlertCircle, Trash2,
  Share2, Clock, UserMinus, Lock, Eye,
  TrendingUp, BookMarked, CheckCircle2
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const groupsStore = useGroupsStore()
const authStore = useAuthStore()
const bindersStore = useBindersStore()

const groupId = computed(() => Number(route.params.id))
const activeTab = ref<'binders' | 'activity' | 'members' | 'progress'>('binders')
const codeCopied = ref(false)
const showShareModal = ref(false)
const shareBinderId = ref<string | null>(null)
const sharePermission = ref<'read' | 'write'>('read')
const sharing = ref(false)
const shareError = ref('')

const currentUserId = computed(() => authStore.user?.id)
const group = computed(() => groupsStore.currentGroup)
const myRole = computed(() => {
  if (!group.value || !currentUserId.value) return null
  return group.value.members.find(m => m.user_id === currentUserId.value)?.role ?? null
})
const isOwner = computed(() => myRole.value === 'owner')
const canManageGroup = computed(() => myRole.value === 'owner' || myRole.value === 'admin')

onMounted(async () => {
  await groupsStore.fetchGroupDetail(groupId.value)
  await groupsStore.fetchGroupActivity(groupId.value)
  await groupsStore.fetchMembersProgress(groupId.value)
  await bindersStore.fetchBinders()
})

watch(() => route.params.id, async (newId) => {
  if (newId) {
    await groupsStore.fetchGroupDetail(Number(newId))
    await groupsStore.fetchGroupActivity(Number(newId))
    await groupsStore.fetchMembersProgress(Number(newId))
  }
})

async function copyCode() {
  if (!group.value) return
  await navigator.clipboard.writeText(group.value.invite_code)
  codeCopied.value = true
  setTimeout(() => { codeCopied.value = false }, 2000)
}

async function shareBinder() {
  if (!shareBinderId.value) return
  sharing.value = true
  shareError.value = ''
  try {
    await groupsStore.shareBinder(groupId.value, shareBinderId.value, sharePermission.value)
    showShareModal.value = false
    shareBinderId.value = null
  } catch (e: unknown) {
    const err = e as { response?: { data?: { error?: { message?: string } } } }
    shareError.value = err?.response?.data?.error?.message || 'Erreur lors du partage.'
  } finally {
    sharing.value = false
  }
}

async function removeBinder(binderId: string) {
  if (!confirm('Retirer ce classeur du groupe ?')) return
  await groupsStore.unshareBinder(groupId.value, binderId)
}

async function updateRole(userId: number, role: 'admin' | 'member') {
  await groupsStore.updateMemberRole(groupId.value, userId, role)
}

async function excludeMember(userId: number, username: string) {
  if (!confirm(`Exclure ${username} du groupe ?`)) return
  await groupsStore.excludeMember(groupId.value, userId)
}

async function leaveGroup() {
  if (!confirm('Quitter ce groupe ?')) return
  if (!currentUserId.value) return
  await groupsStore.leaveGroup(groupId.value, currentUserId.value)
  router.push('/groups')
}

function activityIcon(type: string) {
  const icons: Record<string, string> = {
    joined: '👋',
    shared_binder: '📚',
    completed_session: '✅',
    posted_note: '📝'
  }
  return icons[type] || '📌'
}

function activityLabel(act: { type: string; username: string; payload: Record<string, unknown> | null }) {
  switch (act.type) {
    case 'joined': return `${act.username} a rejoint le groupe`
    case 'shared_binder': return `${act.username} a partagé le classeur "${act.payload?.binder_name}"`
    case 'completed_session': return `${act.username} a terminé une session (${act.payload?.module} · ${Math.round((act.payload?.duration_seconds as number || 0) / 60)} min)`
    case 'posted_note': return `${act.username} a publié une note`
    default: return `${act.username} — ${act.type}`
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

function formatTime(seconds: number) {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  if (h > 0) return `${h}h ${m}m`
  return `${m} min`
}

function roleLabel(role: string) {
  return { owner: 'Propriétaire', admin: 'Admin', member: 'Membre', follower: 'Élève (Abonné)' }[role] ?? role
}

function roleBadgeClass(role: string) {
  return {
    owner: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
    admin: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
    member: 'bg-slate-100 text-slate-655 dark:bg-slate-700 dark:text-slate-300',
    follower: 'bg-sky-100 text-sky-700 dark:bg-sky-900/30 dark:text-sky-400'
  }[role] ?? ''
}

// Classeurs disponibles (non encore partagés)
const availableBinders = computed(() => {
  const sharedIds = group.value?.binders.map(b => b.binder_id) ?? []
  return bindersStore.binders.filter(b => !sharedIds.includes(b.id))
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-[#0B0F19]">
    <!-- Loading -->
    <div v-if="groupsStore.loading && !group" class="flex items-center justify-center py-32">
      <Loader2 class="w-8 h-8 text-violet-500 animate-spin" />
    </div>

    <!-- Error -->
    <div v-else-if="groupsStore.error && !group" class="flex flex-col items-center justify-center py-32 gap-4">
      <AlertCircle class="w-12 h-12 text-red-400" />
      <p class="text-slate-600 dark:text-slate-400">{{ groupsStore.error }}</p>
      <button @click="router.push('/groups')" class="text-violet-600 hover:underline text-sm">← Retour aux groupes</button>
    </div>

    <template v-else-if="group">
      <!-- Header -->
      <div class="bg-white dark:bg-slate-800/80 border-b border-slate-200 dark:border-slate-700">
        <div class="max-w-6xl mx-auto px-6 py-5">
          <button
            @click="router.push('/groups')"
            class="flex items-center gap-1.5 text-sm text-slate-500 hover:text-violet-600 dark:hover:text-violet-400 transition mb-4"
          >
            <ArrowLeft class="w-4 h-4" />
            Mes groupes
          </button>

          <div class="flex items-start justify-between gap-4">
            <div class="flex items-center gap-4">
              <div class="flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-violet-500 to-purple-600 text-white shadow-lg shadow-violet-500/30 text-2xl font-bold flex-shrink-0">
                {{ group.name.charAt(0).toUpperCase() }}
              </div>
              <div>
                <h1 class="text-2xl font-bold text-slate-900 dark:text-white">{{ group.name }}</h1>
                <p v-if="group.description" class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">{{ group.description }}</p>
                <div class="flex items-center gap-3 mt-1.5 text-xs text-slate-400">
                  <span class="flex items-center gap-1"><Users class="w-3 h-3" />{{ group.members.length }} membres</span>
                  <span class="flex items-center gap-1"><BookOpen class="w-3 h-3" />{{ group.binders.length }} classeurs</span>
                </div>
              </div>
            </div>

            <div class="flex items-center gap-2 flex-shrink-0">
              <!-- Invite code badge -->
              <div class="flex items-center gap-2 bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2">
                <span class="text-xs font-mono text-slate-600 dark:text-slate-300 tracking-widest">{{ group.invite_code }}</span>
                <button @click="copyCode" class="p-1 rounded-md hover:bg-slate-200 dark:hover:bg-slate-700 transition" title="Copier le code">
                  <Check v-if="codeCopied" class="w-3.5 h-3.5 text-green-500" />
                  <Copy v-else class="w-3.5 h-3.5 text-slate-400" />
                </button>
              </div>
              <button
                @click="leaveGroup"
                class="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-red-200 dark:border-red-800/50 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 text-xs font-medium transition"
              >
                <UserMinus class="w-3.5 h-3.5" />
                Quitter
              </button>
            </div>
          </div>

          <!-- Tabs -->
          <div class="flex gap-1 mt-5 border-b border-slate-200 dark:border-slate-700 -mb-px">
            <button
              v-for="tab in [
                { id: 'binders', label: 'Classeurs partagés', icon: BookOpen },
                { id: 'activity', label: 'Activité', icon: Activity },
                { id: 'members', label: 'Membres', icon: Users },
                { id: 'progress', label: 'Progression', icon: BarChart3 }
              ]"
              :key="tab.id"
              @click="activeTab = tab.id as typeof activeTab"
              :class="[
                'flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition',
                activeTab === tab.id
                  ? 'border-violet-600 text-violet-600 dark:border-violet-400 dark:text-violet-400'
                  : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
              ]"
            >
              <component :is="tab.icon" class="w-4 h-4" />
              {{ tab.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Content -->
      <div class="max-w-6xl mx-auto px-6 py-6">
        <!-- TAB: Classeurs partagés -->
        <div v-if="activeTab === 'binders'">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Classeurs partagés</h2>
            <button
              v-if="canManageGroup"
              @click="showShareModal = true; shareError = ''"
              class="flex items-center gap-2 px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium transition shadow-sm"
            >
              <Share2 class="w-4 h-4" />
              Partager un classeur
            </button>
          </div>

          <div v-if="group.binders.length === 0" class="text-center py-16">
            <BookOpen class="w-12 h-12 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
            <p class="text-slate-500 dark:text-slate-400 text-sm">Aucun classeur partagé pour l'instant.</p>
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div
              v-for="b in group.binders"
              :key="b.binder_id"
              class="flex items-center justify-between gap-3 bg-white dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60 rounded-xl p-4 cursor-pointer hover:border-violet-500/30 transition-all duration-200"
              @click="router.push(`/binders/${b.binder_id}`)"
            >
              <div class="flex items-center gap-3 min-w-0">
                <div class="flex items-center justify-center w-9 h-9 rounded-lg bg-violet-50 dark:bg-violet-900/20 flex-shrink-0">
                  <BookMarked class="w-4 h-4 text-violet-500" />
                </div>
                <div class="min-w-0">
                  <p class="font-bold text-slate-900 dark:text-white text-sm truncate hover:text-violet-600 transition-colors">{{ b.binder_name }}</p>
                  <div class="flex items-center gap-2 mt-0.5">
                    <span :class="[
                      'flex items-center gap-1 text-xs font-medium px-1.5 py-0.5 rounded-md',
                      b.permission === 'write'
                        ? 'bg-green-50 text-green-600 dark:bg-green-900/20 dark:text-green-400'
                        : 'bg-slate-50 text-slate-500 dark:bg-slate-700 dark:text-slate-400'
                    ]">
                      <Eye v-if="b.permission === 'read'" class="w-3 h-3" />
                      <Lock v-else class="w-3 h-3" />
                      {{ b.permission === 'read' ? 'Lecture' : 'Écriture' }}
                    </span>
                    <span class="text-xs text-slate-400">{{ formatDate(b.added_at) }}</span>
                  </div>
                </div>
              </div>
              <button
                v-if="canManageGroup"
                @click.stop="removeBinder(b.binder_id)"
                class="p-1.5 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition"
                title="Retirer du groupe"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        <!-- TAB: Activité -->
        <div v-else-if="activeTab === 'activity'">
          <h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">Fil d'activité</h2>
          <div v-if="groupsStore.activities.length === 0" class="text-center py-16">
            <Activity class="w-12 h-12 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
            <p class="text-slate-500 dark:text-slate-400 text-sm">Pas encore d'activité dans ce groupe.</p>
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="act in groupsStore.activities"
              :key="act.id"
              class="flex items-center gap-4 bg-white dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60 rounded-xl px-4 py-3"
            >
              <span class="text-2xl flex-shrink-0">{{ activityIcon(act.type) }}</span>
              <div class="flex-1 min-w-0">
                <p class="text-sm text-slate-700 dark:text-slate-300 truncate">{{ activityLabel(act) }}</p>
              </div>
              <span class="text-xs text-slate-400 flex-shrink-0">{{ formatDate(act.created_at) }}</span>
            </div>
          </div>
        </div>

        <!-- TAB: Membres -->
        <div v-else-if="activeTab === 'members'">
          <h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">Membres ({{ group.members.length }})</h2>
          <div class="space-y-2">
            <div
              v-for="m in group.members"
              :key="m.user_id"
              class="flex items-center justify-between gap-3 bg-white dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60 rounded-xl px-4 py-3"
            >
              <div class="flex items-center gap-3">
                <div class="flex items-center justify-center w-9 h-9 rounded-full bg-violet-100 dark:bg-violet-900/30 text-violet-600 dark:text-violet-400 font-bold text-sm flex-shrink-0">
                  {{ m.username.substring(0, 2).toUpperCase() }}
                </div>
                <div>
                  <p class="font-medium text-slate-900 dark:text-white text-sm">
                    {{ m.username }}
                    <span v-if="m.user_id === currentUserId" class="text-xs text-slate-400 ml-1">(vous)</span>
                  </p>
                  <p class="text-xs text-slate-400">Rejoint le {{ formatDate(m.joined_at) }}</p>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <span :class="['px-2 py-0.5 rounded-md text-xs font-medium', roleBadgeClass(m.role)]">
                  {{ roleLabel(m.role) }}
                </span>
                <!-- Admin actions (visible owner only) -->
                <template v-if="isOwner && m.user_id !== currentUserId && m.role !== 'owner'">
                  <select
                    :value="m.role"
                    @change="updateRole(m.user_id, ($event.target as HTMLSelectElement).value as 'admin' | 'member')"
                    class="text-xs bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-2 py-1 text-slate-700 dark:text-slate-200 cursor-pointer"
                  >
                    <option value="admin">Admin</option>
                    <option value="member">Membre</option>
                  </select>
                  <button
                    @click="excludeMember(m.user_id, m.username)"
                    class="p-1.5 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition"
                    title="Exclure"
                  >
                    <UserMinus class="w-4 h-4" />
                  </button>
                </template>
              </div>
            </div>
          </div>
        </div>

        <!-- TAB: Progression -->
        <div v-else-if="activeTab === 'progress'">
          <h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-1">Progression (7 derniers jours)</h2>
          <p class="text-sm text-slate-400 dark:text-slate-500 mb-4">Données agrégées uniquement – le contenu des révisions reste privé.</p>

          <div v-if="groupsStore.membersProgress.length === 0" class="text-center py-16">
            <BarChart3 class="w-12 h-12 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
            <p class="text-slate-500 dark:text-slate-400 text-sm">Aucune donnée de progression disponible.</p>
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="(prog, idx) in groupsStore.membersProgress"
              :key="prog.user_id"
              class="bg-white dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/60 rounded-xl p-4"
            >
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-3">
                  <span :class="[
                    'flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold text-white',
                    idx === 0 ? 'bg-amber-500' : idx === 1 ? 'bg-slate-400' : idx === 2 ? 'bg-orange-400' : 'bg-slate-200 text-slate-600'
                  ]">{{ idx + 1 }}</span>
                  <span class="font-medium text-slate-900 dark:text-white text-sm">
                    {{ prog.username }}
                    <span v-if="prog.user_id === currentUserId" class="text-xs text-slate-400 ml-1">(vous)</span>
                  </span>
                </div>
                <span class="flex items-center gap-1 text-xs text-violet-600 dark:text-violet-400 font-medium">
                  <Clock class="w-3.5 h-3.5" />
                  {{ formatTime(prog.total_time_seconds) }}
                </span>
              </div>

              <div class="flex items-center gap-6 text-xs text-slate-500 dark:text-slate-400">
                <span class="flex items-center gap-1.5">
                  <TrendingUp class="w-3.5 h-3.5 text-blue-400" />
                  {{ prog.cards_reviewed }} cartes révisées
                </span>
                <span class="flex items-center gap-1.5">
                  <CheckCircle2 class="w-3.5 h-3.5 text-green-500" />
                  {{ prog.cards_correct }} correctes
                </span>
                <span v-if="prog.cards_reviewed > 0" class="flex items-center gap-1.5 font-medium" :class="(prog.cards_correct / prog.cards_reviewed) >= 0.8 ? 'text-green-600 dark:text-green-400' : 'text-amber-600 dark:text-amber-400'">
                  {{ Math.round((prog.cards_correct / prog.cards_reviewed) * 100) }}% réussite
                </span>
              </div>

              <!-- Progress bar -->
              <div v-if="prog.cards_reviewed > 0" class="mt-3 h-1.5 rounded-full bg-slate-100 dark:bg-slate-700 overflow-hidden">
                <div
                  class="h-full rounded-full bg-gradient-to-r from-violet-500 to-purple-500 transition-all"
                  :style="{ width: Math.round((prog.cards_correct / prog.cards_reviewed) * 100) + '%' }"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Share Binder Modal -->
    <Teleport to="body">
      <div
        v-if="showShareModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
        @click.self="showShareModal = false"
      >
        <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-md border border-slate-200 dark:border-slate-700">
          <div class="p-6 border-b border-slate-100 dark:border-slate-700">
            <h2 class="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Share2 class="w-5 h-5 text-violet-500" />
              Partager un classeur
            </h2>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Classeur</label>
              <select
                v-model="shareBinderId"
                class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500 transition"
              >
                <option :value="null" disabled>Choisir un classeur…</option>
                <option v-for="b in availableBinders" :key="b.id" :value="b.id">{{ b.name }}</option>
              </select>
              <p v-if="availableBinders.length === 0" class="mt-2 text-xs text-slate-400">
                Tous vos classeurs sont déjà partagés dans ce groupe.
              </p>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Permission</label>
              <div class="grid grid-cols-2 gap-2">
                <button
                  v-for="perm in [{ val: 'read', label: 'Lecture seule', icon: Eye }, { val: 'write', label: 'Lecture + Écriture', icon: Lock }]"
                  :key="perm.val"
                  @click="sharePermission = perm.val as 'read' | 'write'"
                  :class="[
                    'flex flex-col items-center gap-2 p-3 rounded-xl border-2 text-sm font-medium transition',
                    sharePermission === perm.val
                      ? 'border-violet-600 bg-violet-50 text-violet-700 dark:bg-violet-900/20 dark:text-violet-400 dark:border-violet-500'
                      : 'border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:border-slate-300'
                  ]"
                >
                  <component :is="perm.icon" class="w-4 h-4" />
                  {{ perm.label }}
                </button>
              </div>
            </div>
            <div v-if="shareError" class="flex items-center gap-2 text-red-500 text-sm">
              <AlertCircle class="w-4 h-4 flex-shrink-0" />
              {{ shareError }}
            </div>
          </div>
          <div class="p-6 pt-0 flex gap-3">
            <button @click="showShareModal = false" class="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition text-sm font-medium">
              Annuler
            </button>
            <button
              @click="shareBinder"
              :disabled="!shareBinderId || sharing"
              class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-medium text-sm transition"
            >
              <Loader2 v-if="sharing" class="w-4 h-4 animate-spin" />
              <Share2 v-else class="w-4 h-4" />
              Partager
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
