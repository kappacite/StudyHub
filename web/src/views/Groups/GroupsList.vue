<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGroupsStore } from '../../stores/groups'
import {
  Users, Plus, LogIn, Copy, Check, ArrowRight,
  BookOpen, Clock, Loader2, AlertCircle
} from 'lucide-vue-next'

const router = useRouter()
const groupsStore = useGroupsStore()

const showCreateModal = ref(false)
const showJoinModal = ref(false)
const newGroupName = ref('')
const newGroupDesc = ref('')
const joinCode = ref('')
const creating = ref(false)
const joining = ref(false)
const errorMsg = ref('')
const copiedId = ref<number | null>(null)

onMounted(() => groupsStore.fetchMyGroups())

async function createGroup() {
  if (!newGroupName.value.trim()) return
  creating.value = true
  errorMsg.value = ''
  try {
    const g = await groupsStore.createGroup(newGroupName.value.trim(), newGroupDesc.value.trim() || undefined)
    showCreateModal.value = false
    newGroupName.value = ''
    newGroupDesc.value = ''
    router.push(`/groups/${g.id}`)
  } catch (e: unknown) {
    const err = e as { response?: { data?: { error?: { message?: string } } } }
    errorMsg.value = err?.response?.data?.error?.message || 'Impossible de créer le groupe.'
  } finally {
    creating.value = false
  }
}

async function joinGroup() {
  if (joinCode.value.trim().length !== 8) {
    errorMsg.value = 'Le code doit comporter exactement 8 caractères.'
    return
  }
  joining.value = true
  errorMsg.value = ''
  try {
    const g = await groupsStore.joinGroup(joinCode.value.trim().toUpperCase())
    showJoinModal.value = false
    joinCode.value = ''
    router.push(`/groups/${g.id}`)
  } catch (e: unknown) {
    const err = e as { response?: { data?: { error?: { message?: string } } } }
    errorMsg.value = err?.response?.data?.error?.message || 'Code invalide ou groupe introuvable.'
  } finally {
    joining.value = false
  }
}

async function copyCode(groupId: number, code: string) {
  await navigator.clipboard.writeText(code)
  copiedId.value = groupId
  setTimeout(() => { copiedId.value = null }, 2000)
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })
}

function closeModals() {
  showCreateModal.value = false
  showJoinModal.value = false
  errorMsg.value = ''
  newGroupName.value = ''
  newGroupDesc.value = ''
  joinCode.value = ''
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-[#0B0F19] p-6">
    <!-- Header -->
    <div class="mb-8 flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
          <span class="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-500 to-purple-600 text-white shadow-lg shadow-violet-500/30">
            <Users class="w-5 h-5" />
          </span>
          Mes Groupes
        </h1>
        <p class="mt-1 text-slate-500 dark:text-slate-400 text-sm">
          Collaborez avec vos camarades de façon asynchrone
        </p>
      </div>
      <div class="flex gap-3">
        <button
          @click="showJoinModal = true"
          class="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700/60 transition-all text-sm font-medium shadow-sm"
        >
          <LogIn class="w-4 h-4" />
          Rejoindre avec un code
        </button>
        <button
          @click="showCreateModal = true"
          class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 text-white font-medium text-sm shadow-lg shadow-violet-500/25 transition-all"
        >
          <Plus class="w-4 h-4" />
          Créer un groupe
        </button>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="groupsStore.loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-violet-500 animate-spin" />
    </div>

    <!-- Empty state -->
    <div v-else-if="groupsStore.groups.length === 0" class="text-center py-24">
      <div class="flex items-center justify-center w-20 h-20 rounded-2xl bg-violet-50 dark:bg-violet-900/20 mx-auto mb-5">
        <Users class="w-10 h-10 text-violet-400" />
      </div>
      <h3 class="text-xl font-semibold text-slate-900 dark:text-white mb-2">Aucun groupe pour l'instant</h3>
      <p class="text-slate-500 dark:text-slate-400 mb-6 max-w-md mx-auto">
        Créez votre premier groupe d'étude ou rejoignez-en un avec un code d'invitation.
      </p>
      <div class="flex gap-3 justify-center">
        <button
          @click="showCreateModal = true"
          class="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-medium text-sm transition-colors"
        >
          <Plus class="w-4 h-4" />
          Créer un groupe
        </button>
        <button
          @click="showJoinModal = true"
          class="flex items-center gap-2 px-5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 font-medium text-sm transition-colors"
        >
          <LogIn class="w-4 h-4" />
          Rejoindre
        </button>
      </div>
    </div>

    <!-- Groups grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <article
        v-for="group in groupsStore.groups"
        :key="group.id"
        class="group bg-white dark:bg-slate-800/60 rounded-2xl border border-slate-100 dark:border-slate-700/60 shadow-sm hover:shadow-lg hover:border-violet-200 dark:hover:border-violet-700/50 transition-all duration-300 overflow-hidden cursor-pointer"
        @click="router.push(`/groups/${group.id}`)"
      >
        <!-- Card gradient header -->
        <div class="h-2 bg-gradient-to-r from-violet-500 to-purple-600"></div>

        <div class="p-5">
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1 min-w-0">
              <h3 class="font-semibold text-slate-900 dark:text-white text-lg truncate group-hover:text-violet-600 dark:group-hover:text-violet-400 transition-colors">
                {{ group.name }}
              </h3>
              <p v-if="group.description" class="text-sm text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">
                {{ group.description }}
              </p>
            </div>
            <ArrowRight class="w-5 h-5 text-slate-300 dark:text-slate-600 group-hover:text-violet-500 transition-colors flex-shrink-0 ml-3 mt-0.5" />
          </div>

          <!-- Stats row -->
          <div class="flex items-center gap-4 text-sm text-slate-500 dark:text-slate-400 mb-4">
            <span class="flex items-center gap-1.5">
              <Users class="w-3.5 h-3.5" />
              {{ group.members_count }} membre{{ group.members_count > 1 ? 's' : '' }}
            </span>
            <span class="flex items-center gap-1.5">
              <BookOpen class="w-3.5 h-3.5" />
              {{ group.binders_count }} classeur{{ group.binders_count > 1 ? 's' : '' }}
            </span>
            <span class="flex items-center gap-1.5">
              <Clock class="w-3.5 h-3.5" />
              {{ formatDate(group.created_at) }}
            </span>
          </div>

          <!-- Invite code -->
          <div class="flex items-center gap-2 bg-slate-50 dark:bg-slate-900/40 rounded-lg p-2.5">
            <span class="text-xs font-mono text-slate-600 dark:text-slate-300 flex-1 tracking-widest">
              {{ group.invite_code }}
            </span>
            <button
              @click.stop="copyCode(group.id, group.invite_code)"
              class="p-1.5 rounded-md hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
              title="Copier le code d'invitation"
            >
              <Check v-if="copiedId === group.id" class="w-3.5 h-3.5 text-green-500" />
              <Copy v-else class="w-3.5 h-3.5 text-slate-400" />
            </button>
          </div>
        </div>
      </article>
    </div>

    <!-- Create Group Modal -->
    <Teleport to="body">
      <div
        v-if="showCreateModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
        @click.self="closeModals"
      >
        <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-md border border-slate-200 dark:border-slate-700">
          <div class="p-6 border-b border-slate-100 dark:border-slate-700">
            <h2 class="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Plus class="w-5 h-5 text-violet-500" />
              Créer un groupe
            </h2>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                Nom du groupe <span class="text-red-500">*</span>
              </label>
              <input
                v-model="newGroupName"
                type="text"
                placeholder="Ex : PACES 2025 – Pharmacologie"
                maxlength="100"
                class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500 transition"
                @keydown.enter="createGroup"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                Description (optionnel)
              </label>
              <textarea
                v-model="newGroupDesc"
                placeholder="Décrivez l'objectif du groupe…"
                rows="3"
                class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500 transition resize-none"
              />
            </div>
            <div v-if="errorMsg" class="flex items-center gap-2 text-red-500 text-sm">
              <AlertCircle class="w-4 h-4 flex-shrink-0" />
              {{ errorMsg }}
            </div>
          </div>
          <div class="p-6 pt-0 flex gap-3">
            <button
              @click="closeModals"
              class="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition text-sm font-medium"
            >
              Annuler
            </button>
            <button
              @click="createGroup"
              :disabled="!newGroupName.trim() || creating"
              class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-medium text-sm transition"
            >
              <Loader2 v-if="creating" class="w-4 h-4 animate-spin" />
              <Plus v-else class="w-4 h-4" />
              Créer
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Join Group Modal -->
    <Teleport to="body">
      <div
        v-if="showJoinModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
        @click.self="closeModals"
      >
        <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-sm border border-slate-200 dark:border-slate-700">
          <div class="p-6 border-b border-slate-100 dark:border-slate-700">
            <h2 class="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <LogIn class="w-5 h-5 text-violet-500" />
              Rejoindre un groupe
            </h2>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                Code d'invitation (8 caractères)
              </label>
              <input
                v-model="joinCode"
                type="text"
                placeholder="EX: ABCD1234"
                maxlength="8"
                class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 font-mono tracking-widest text-center uppercase focus:outline-none focus:ring-2 focus:ring-violet-500 transition"
                @keydown.enter="joinGroup"
              />
            </div>
            <div v-if="errorMsg" class="flex items-center gap-2 text-red-500 text-sm">
              <AlertCircle class="w-4 h-4 flex-shrink-0" />
              {{ errorMsg }}
            </div>
          </div>
          <div class="p-6 pt-0 flex gap-3">
            <button
              @click="closeModals"
              class="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition text-sm font-medium"
            >
              Annuler
            </button>
            <button
              @click="joinGroup"
              :disabled="joinCode.trim().length !== 8 || joining"
              class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white font-medium text-sm transition"
            >
              <Loader2 v-if="joining" class="w-4 h-4 animate-spin" />
              <LogIn v-else class="w-4 h-4" />
              Rejoindre
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
