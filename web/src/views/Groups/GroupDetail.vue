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
    owner: 'bg-accent-soft text-accent',
    admin: 'bg-info-soft text-info',
    member: 'bg-surface-soft text-ink-muted',
    follower: 'bg-primary-soft text-primary'
  }[role] ?? ''
}

function rankBadgeClass(idx: number) {
  if (idx === 0) return 'bg-accent text-white'
  if (idx === 1) return 'bg-ink-subtle text-white'
  if (idx === 2) return 'bg-warning text-white'
  return 'bg-surface-soft text-ink-muted'
}

// Classeurs disponibles (non encore partagés)
const availableBinders = computed(() => {
  const sharedIds = group.value?.binders.map(b => b.binder_id) ?? []
  return bindersStore.binders.filter(b => !sharedIds.includes(b.id))
})
</script>

<template>
  <div class="min-h-screen bg-app">
    <!-- Loading -->
    <div v-if="groupsStore.loading && !group" class="flex items-center justify-center py-32">
      <Loader2 class="w-8 h-8 text-primary animate-spin" />
    </div>

    <!-- Error -->
    <div v-else-if="groupsStore.error && !group" class="flex flex-col items-center justify-center py-32 gap-4">
      <AlertCircle class="w-12 h-12 text-danger" />
      <p class="text-ink-muted">{{ groupsStore.error }}</p>
      <button @click="router.push('/groups')" class="text-primary hover:underline text-sm">← Retour aux groupes</button>
    </div>

    <template v-else-if="group">
      <!-- Header -->
      <div class="bg-surface border-b border-line">
        <div class="max-w-6xl mx-auto px-6 py-5">
          <button
            @click="router.push('/groups')"
            class="flex items-center gap-1.5 text-sm text-ink-muted hover:text-primary transition mb-4"
          >
            <ArrowLeft class="w-4 h-4" />
            Mes groupes
          </button>

          <div class="flex items-start justify-between gap-4">
            <div class="flex items-center gap-4">
              <div class="flex items-center justify-center w-14 h-14 rounded-2xl bg-primary text-white shadow-elev-primary text-2xl font-bold flex-shrink-0">
                {{ group.name.charAt(0).toUpperCase() }}
              </div>
              <div>
                <h1 class="text-2xl font-bold text-ink">{{ group.name }}</h1>
                <p v-if="group.description" class="text-sm text-ink-muted mt-0.5">{{ group.description }}</p>
                <div class="flex items-center gap-3 mt-1.5 text-xs text-ink-subtle">
                  <span class="flex items-center gap-1"><Users class="w-3 h-3" />{{ group.members.length }} membres</span>
                  <span class="flex items-center gap-1"><BookOpen class="w-3 h-3" />{{ group.binders.length }} classeurs</span>
                </div>
              </div>
            </div>

            <div class="flex items-center gap-2 flex-shrink-0">
              <!-- Code d'invitation -->
              <div class="flex items-center gap-2 bg-surface-soft border border-line rounded-xl px-3 py-2">
                <span class="text-xs font-mono text-ink-muted tracking-widest">{{ group.invite_code }}</span>
                <button @click="copyCode" class="p-1 rounded-md hover:bg-surface transition" title="Copier le code">
                  <Check v-if="codeCopied" class="w-3.5 h-3.5 text-success" />
                  <Copy v-else class="w-3.5 h-3.5 text-ink-subtle" />
                </button>
              </div>
              <button
                @click="leaveGroup"
                class="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-danger/30 text-danger hover:bg-danger-soft text-xs font-medium transition"
              >
                <UserMinus class="w-3.5 h-3.5" />
                Quitter
              </button>
            </div>
          </div>

          <!-- Tabs -->
          <div class="flex gap-1 mt-5 border-b border-line -mb-px">
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
                  ? 'border-primary text-primary'
                  : 'border-transparent text-ink-muted hover:text-ink'
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
            <h2 class="text-lg font-semibold text-ink">Classeurs partagés</h2>
            <button
              v-if="canManageGroup"
              @click="showShareModal = true; shareError = ''"
              class="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary hover:bg-primary-strong text-white text-sm font-medium transition shadow-elev-primary"
            >
              <Share2 class="w-4 h-4" />
              Partager un classeur
            </button>
          </div>

          <div v-if="group.binders.length === 0" class="text-center py-16">
            <BookOpen class="w-12 h-12 text-ink-subtle mx-auto mb-3" />
            <p class="text-ink-muted text-sm">Aucun classeur partagé pour l'instant.</p>
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div
              v-for="b in group.binders"
              :key="b.binder_id"
              class="flex items-center justify-between gap-3 bg-surface border border-line rounded-xl p-4 cursor-pointer hover:border-primary/30 transition-all duration-200"
              @click="router.push(`/bibliotheque/${b.binder_id}`)"
            >
              <div class="flex items-center gap-3 min-w-0">
                <div class="flex items-center justify-center w-9 h-9 rounded-lg bg-primary-soft flex-shrink-0">
                  <BookMarked class="w-4 h-4 text-primary" />
                </div>
                <div class="min-w-0">
                  <p class="font-bold text-ink text-sm truncate hover:text-primary transition-colors">{{ b.binder_name }}</p>
                  <div class="flex items-center gap-2 mt-0.5">
                    <span :class="[
                      'flex items-center gap-1 text-xs font-medium px-1.5 py-0.5 rounded-md',
                      b.permission === 'write'
                        ? 'bg-success-soft text-success'
                        : 'bg-surface-soft text-ink-muted'
                    ]">
                      <Eye v-if="b.permission === 'read'" class="w-3 h-3" />
                      <Lock v-else class="w-3 h-3" />
                      {{ b.permission === 'read' ? 'Lecture' : 'Écriture' }}
                    </span>
                    <span class="text-xs text-ink-subtle">{{ formatDate(b.added_at) }}</span>
                  </div>
                </div>
              </div>
              <button
                v-if="canManageGroup"
                @click.stop="removeBinder(b.binder_id)"
                class="p-1.5 rounded-lg text-ink-subtle hover:text-danger hover:bg-danger-soft transition"
                title="Retirer du groupe"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        <!-- TAB: Activité -->
        <div v-else-if="activeTab === 'activity'">
          <h2 class="text-lg font-semibold text-ink mb-4">Fil d'activité</h2>
          <div v-if="groupsStore.activities.length === 0" class="text-center py-16">
            <Activity class="w-12 h-12 text-ink-subtle mx-auto mb-3" />
            <p class="text-ink-muted text-sm">Pas encore d'activité dans ce groupe.</p>
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="act in groupsStore.activities"
              :key="act.id"
              class="flex items-center gap-4 bg-surface border border-line rounded-xl px-4 py-3"
            >
              <span class="text-2xl flex-shrink-0">{{ activityIcon(act.type) }}</span>
              <div class="flex-1 min-w-0">
                <p class="text-sm text-ink-muted truncate">{{ activityLabel(act) }}</p>
              </div>
              <span class="text-xs text-ink-subtle flex-shrink-0">{{ formatDate(act.created_at) }}</span>
            </div>
          </div>
        </div>

        <!-- TAB: Membres -->
        <div v-else-if="activeTab === 'members'">
          <h2 class="text-lg font-semibold text-ink mb-4">Membres ({{ group.members.length }})</h2>
          <div class="space-y-2">
            <div
              v-for="m in group.members"
              :key="m.user_id"
              class="flex items-center justify-between gap-3 bg-surface border border-line rounded-xl px-4 py-3"
            >
              <div class="flex items-center gap-3">
                <div class="flex items-center justify-center w-9 h-9 rounded-full bg-primary-soft text-primary font-bold text-sm flex-shrink-0">
                  {{ m.username.substring(0, 2).toUpperCase() }}
                </div>
                <div>
                  <p class="font-medium text-ink text-sm">
                    {{ m.username }}
                    <span v-if="m.user_id === currentUserId" class="text-xs text-ink-subtle ml-1">(vous)</span>
                  </p>
                  <p class="text-xs text-ink-subtle">Rejoint le {{ formatDate(m.joined_at) }}</p>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <span :class="['px-2 py-0.5 rounded-md text-xs font-medium', roleBadgeClass(m.role)]">
                  {{ roleLabel(m.role) }}
                </span>
                <!-- Actions admin (propriétaire uniquement) -->
                <template v-if="isOwner && m.user_id !== currentUserId && m.role !== 'owner'">
                  <select
                    :value="m.role"
                    @change="updateRole(m.user_id, ($event.target as HTMLSelectElement).value as 'admin' | 'member')"
                    class="text-xs bg-surface-soft border border-line rounded-lg px-2 py-1 text-ink cursor-pointer"
                  >
                    <option value="admin">Admin</option>
                    <option value="member">Membre</option>
                  </select>
                  <button
                    @click="excludeMember(m.user_id, m.username)"
                    class="p-1.5 rounded-lg text-ink-subtle hover:text-danger hover:bg-danger-soft transition"
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
          <h2 class="text-lg font-semibold text-ink mb-1">Progression (7 derniers jours)</h2>
          <p class="text-sm text-ink-subtle mb-4">Données agrégées uniquement – le contenu des révisions reste privé.</p>

          <div v-if="groupsStore.membersProgress.length === 0" class="text-center py-16">
            <BarChart3 class="w-12 h-12 text-ink-subtle mx-auto mb-3" />
            <p class="text-ink-muted text-sm">Aucune donnée de progression disponible.</p>
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="(prog, idx) in groupsStore.membersProgress"
              :key="prog.user_id"
              class="bg-surface border border-line rounded-xl p-4"
            >
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-3">
                  <span :class="['flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold', rankBadgeClass(idx)]">{{ idx + 1 }}</span>
                  <span class="font-medium text-ink text-sm">
                    {{ prog.username }}
                    <span v-if="prog.user_id === currentUserId" class="text-xs text-ink-subtle ml-1">(vous)</span>
                  </span>
                </div>
                <span class="flex items-center gap-1 text-xs text-primary font-medium">
                  <Clock class="w-3.5 h-3.5" />
                  {{ formatTime(prog.total_time_seconds) }}
                </span>
              </div>

              <div class="flex items-center gap-6 text-xs text-ink-muted">
                <span class="flex items-center gap-1.5">
                  <TrendingUp class="w-3.5 h-3.5 text-info" />
                  {{ prog.cards_reviewed }} cartes révisées
                </span>
                <span class="flex items-center gap-1.5">
                  <CheckCircle2 class="w-3.5 h-3.5 text-success" />
                  {{ prog.cards_correct }} correctes
                </span>
                <span v-if="prog.cards_reviewed > 0" class="flex items-center gap-1.5 font-medium" :class="(prog.cards_correct / prog.cards_reviewed) >= 0.8 ? 'text-success' : 'text-warning'">
                  {{ Math.round((prog.cards_correct / prog.cards_reviewed) * 100) }}% réussite
                </span>
              </div>

              <!-- Barre de progression -->
              <div v-if="prog.cards_reviewed > 0" class="mt-3 h-1.5 rounded-full bg-surface-soft overflow-hidden">
                <div
                  class="h-full rounded-full bg-primary transition-all"
                  :style="{ width: Math.round((prog.cards_correct / prog.cards_reviewed) * 100) + '%' }"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Modale : partager un classeur -->
    <Teleport to="body">
      <div
        v-if="showShareModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
        @click.self="showShareModal = false"
      >
        <div class="bg-surface rounded-2xl shadow-elev-3 w-full max-w-md border border-line">
          <div class="p-6 border-b border-line">
            <h2 class="text-xl font-bold text-ink flex items-center gap-2">
              <Share2 class="w-5 h-5 text-primary" />
              Partager un classeur
            </h2>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-ink-muted mb-1.5">Classeur</label>
              <select
                v-model="shareBinderId"
                class="w-full px-4 py-2.5 rounded-xl border border-line bg-surface-soft text-ink focus:outline-none focus:ring-2 focus:ring-primary/40 transition"
              >
                <option :value="null" disabled>Choisir un classeur…</option>
                <option v-for="b in availableBinders" :key="b.id" :value="b.id">{{ b.name }}</option>
              </select>
              <p v-if="availableBinders.length === 0" class="mt-2 text-xs text-ink-subtle">
                Tous vos classeurs sont déjà partagés dans ce groupe.
              </p>
            </div>
            <div>
              <label class="block text-sm font-medium text-ink-muted mb-1.5">Permission</label>
              <div class="grid grid-cols-2 gap-2">
                <button
                  v-for="perm in [{ val: 'read', label: 'Lecture seule', icon: Eye }, { val: 'write', label: 'Lecture + Écriture', icon: Lock }]"
                  :key="perm.val"
                  @click="sharePermission = perm.val as 'read' | 'write'"
                  :class="[
                    'flex flex-col items-center gap-2 p-3 rounded-xl border-2 text-sm font-medium transition',
                    sharePermission === perm.val
                      ? 'border-primary bg-primary-soft text-primary'
                      : 'border-line text-ink-muted hover:border-primary/40'
                  ]"
                >
                  <component :is="perm.icon" class="w-4 h-4" />
                  {{ perm.label }}
                </button>
              </div>
            </div>
            <div v-if="shareError" class="flex items-center gap-2 text-danger text-sm">
              <AlertCircle class="w-4 h-4 flex-shrink-0" />
              {{ shareError }}
            </div>
          </div>
          <div class="p-6 pt-0 flex gap-3">
            <button @click="showShareModal = false" class="flex-1 px-4 py-2.5 rounded-xl border border-line text-ink-muted hover:bg-surface-soft transition text-sm font-medium">
              Annuler
            </button>
            <button
              @click="shareBinder"
              :disabled="!shareBinderId || sharing"
              class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-primary hover:bg-primary-strong disabled:opacity-50 text-white font-medium text-sm transition"
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
