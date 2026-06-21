<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGroupsStore } from '../../stores/groups'
import { BaseButton, BaseCard, BaseModal, BaseField, BaseInput } from '../../components/ui/base'
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
  <div class="space-y-6">
    <!-- Sous-en-tête (monté dans ClassesLanding) -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div class="flex items-center gap-3">
        <span class="flex items-center justify-center w-10 h-10 rounded-xl bg-primary text-white shadow-elev-primary">
          <Users class="w-5 h-5" />
        </span>
        <div>
          <h2 class="text-lg font-bold text-ink">Mes Groupes</h2>
          <p class="text-xs text-ink-muted">Collaborez avec vos camarades de façon asynchrone</p>
        </div>
      </div>
      <div class="flex gap-2">
        <BaseButton variant="secondary" size="sm" @click="showJoinModal = true">
          <template #icon><LogIn class="w-4 h-4" /></template>
          Rejoindre avec un code
        </BaseButton>
        <BaseButton size="sm" @click="showCreateModal = true">
          <template #icon><Plus class="w-4 h-4" /></template>
          Créer un groupe
        </BaseButton>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="groupsStore.loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-primary animate-spin" />
    </div>

    <!-- Empty -->
    <div v-else-if="groupsStore.groups.length === 0" class="text-center py-20">
      <div class="flex items-center justify-center w-20 h-20 rounded-2xl bg-primary-soft mx-auto mb-5">
        <Users class="w-10 h-10 text-primary" />
      </div>
      <h3 class="text-xl font-semibold text-ink mb-2">Aucun groupe pour l'instant</h3>
      <p class="text-ink-muted mb-6 max-w-md mx-auto">
        Créez votre premier groupe d'étude ou rejoignez-en un avec un code d'invitation.
      </p>
      <div class="flex gap-2 justify-center">
        <BaseButton size="sm" @click="showCreateModal = true">
          <template #icon><Plus class="w-4 h-4" /></template>
          Créer un groupe
        </BaseButton>
        <BaseButton variant="secondary" size="sm" @click="showJoinModal = true">
          <template #icon><LogIn class="w-4 h-4" /></template>
          Rejoindre
        </BaseButton>
      </div>
    </div>

    <!-- Grille -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <BaseCard
        v-for="group in groupsStore.groups"
        :key="group.id"
        padding="none"
        interactive
        class="group overflow-hidden cursor-pointer"
        @click="router.push(`/groups/${group.id}`)"
      >
        <div class="h-2 bg-primary"></div>
        <div class="p-5">
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1 min-w-0">
              <h3 class="font-semibold text-ink text-lg truncate group-hover:text-primary transition-colors">
                {{ group.name }}
              </h3>
              <p v-if="group.description" class="text-sm text-ink-muted mt-0.5 line-clamp-2">
                {{ group.description }}
              </p>
            </div>
            <ArrowRight class="w-5 h-5 text-ink-subtle group-hover:text-primary transition-colors flex-shrink-0 ml-3 mt-0.5" />
          </div>

          <div class="flex items-center gap-4 text-sm text-ink-muted mb-4">
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

          <div class="flex items-center gap-2 bg-surface-soft rounded-lg p-2.5">
            <span class="text-xs font-mono text-ink-muted flex-1 tracking-widest">
              {{ group.invite_code }}
            </span>
            <button
              @click.stop="copyCode(group.id, group.invite_code)"
              class="p-1.5 rounded-md hover:bg-surface transition-colors"
              title="Copier le code d'invitation"
            >
              <Check v-if="copiedId === group.id" class="w-3.5 h-3.5 text-success" />
              <Copy v-else class="w-3.5 h-3.5 text-ink-subtle" />
            </button>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Modale : créer un groupe -->
    <BaseModal :open="showCreateModal" title="Créer un groupe" @close="closeModals">
      <form @submit.prevent="createGroup" class="space-y-4">
        <BaseField label="Nom du groupe" required for-id="grp-name">
          <BaseInput id="grp-name" v-model="newGroupName" placeholder="Ex : PACES 2025 – Pharmacologie" />
        </BaseField>
        <BaseField label="Description (optionnel)" for-id="grp-desc">
          <textarea
            id="grp-desc"
            v-model="newGroupDesc"
            placeholder="Décrivez l'objectif du groupe…"
            rows="3"
            class="w-full px-4 py-2.5 rounded-xl border border-line bg-surface-soft text-sm text-ink placeholder:text-ink-subtle focus:outline-none focus:ring-2 focus:ring-primary/40 resize-none"
          />
        </BaseField>
        <div v-if="errorMsg" class="flex items-center gap-2 text-danger text-sm">
          <AlertCircle class="w-4 h-4 flex-shrink-0" />
          {{ errorMsg }}
        </div>
        <div class="flex items-center justify-end gap-2 pt-1">
          <BaseButton type="button" variant="ghost" @click="closeModals">Annuler</BaseButton>
          <BaseButton type="submit" :disabled="!newGroupName.trim()" :loading="creating">Créer</BaseButton>
        </div>
      </form>
    </BaseModal>

    <!-- Modale : rejoindre un groupe -->
    <BaseModal :open="showJoinModal" title="Rejoindre un groupe" size="sm" @close="closeModals">
      <form @submit.prevent="joinGroup" class="space-y-4">
        <BaseField label="Code d'invitation (8 caractères)" for-id="grp-code">
          <input
            id="grp-code"
            v-model="joinCode"
            type="text"
            placeholder="EX: ABCD1234"
            maxlength="8"
            class="w-full px-4 py-2.5 rounded-xl border border-line bg-surface-soft text-ink placeholder:text-ink-subtle font-mono tracking-widest text-center uppercase focus:outline-none focus:ring-2 focus:ring-primary/40"
          />
        </BaseField>
        <div v-if="errorMsg" class="flex items-center gap-2 text-danger text-sm">
          <AlertCircle class="w-4 h-4 flex-shrink-0" />
          {{ errorMsg }}
        </div>
        <div class="flex items-center justify-end gap-2 pt-1">
          <BaseButton type="button" variant="ghost" @click="closeModals">Annuler</BaseButton>
          <BaseButton type="submit" :disabled="joinCode.trim().length !== 8" :loading="joining">Rejoindre</BaseButton>
        </div>
      </form>
    </BaseModal>
  </div>
</template>
