<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBindersStore } from '../../stores/binders'
import classService from '../../services/classService'
import type { Assignment } from '../../services/classService'
import {
  GraduationCap, Plus, Users, ClipboardList,
  Loader2, AlertCircle, Calendar,
  BarChart3, Trash2, Eye
} from 'lucide-vue-next'

const router = useRouter()
const bindersStore = useBindersStore()

// Classes = groups where is_class = true and user is teacher
const classes = ref<Array<{
  id: number; name: string; description: string | null;
  invite_code: string; members_count: number; created_at: string;
  assignments: Assignment[]
}>>([])
const loading = ref(true)
const showCreateClassModal = ref(false)
const showCreateAssignmentModal = ref(false)
const selectedClassId = ref<number | null>(null)
const creating = ref(false)
const error = ref('')

// Create class form
const newClassName = ref('')
const newClassDesc = ref('')

// Create assignment form
const newAsgTitle = ref('')
const newAsgDesc = ref('')
const newAsgBinderId = ref<number | null>(null)
const newAsgDueDate = ref('')

async function loadClasses() {
  const [myClasses, _] = await Promise.all([
    classService.getMyClasses(),
    bindersStore.fetchBinders()
  ])
  const results = await Promise.all(
    myClasses.map(async c => {
      const asgns = await classService.listAssignments(c.id).catch(() => [])
      return { ...c, assignments: asgns }
    })
  )
  classes.value = results
}

onMounted(async () => {
  loading.value = true
  try {
    await loadClasses()
  } catch (e: any) {
    error.value = "Impossible de charger les classes."
  } finally {
    loading.value = false
  }
})

async function createClass() {
  if (!newClassName.value.trim()) return
  creating.value = true
  error.value = ''
  try {
    await classService.createClass(newClassName.value.trim(), newClassDesc.value.trim() || undefined)
    await loadClasses()
    showCreateClassModal.value = false
    newClassName.value = ''
    newClassDesc.value = ''
  } catch (e: unknown) {
    const err = e as { response?: { data?: { error?: { message?: string } } } }
    error.value = err?.response?.data?.error?.message || 'Erreur lors de la création.'
  } finally {
    creating.value = false
  }
}

async function createAssignment() {
  if (!selectedClassId.value || !newAsgTitle.value.trim() || !newAsgBinderId.value) return
  creating.value = true
  error.value = ''
  try {
    await classService.createAssignment(selectedClassId.value, {
      binder_id: newAsgBinderId.value,
      title: newAsgTitle.value.trim(),
      description: newAsgDesc.value.trim() || undefined,
      due_date: newAsgDueDate.value || undefined
    })
    // Refresh assignments for this class
    const updated = [...classes.value]
    const idx = updated.findIndex(c => c.id === selectedClassId.value)
    if (idx !== -1) {
      updated[idx].assignments = await classService.listAssignments(selectedClassId.value)
    }
    classes.value = updated
    showCreateAssignmentModal.value = false
    newAsgTitle.value = ''
    newAsgDesc.value = ''
    newAsgBinderId.value = null
    newAsgDueDate.value = ''
  } catch (e: unknown) {
    const err = e as { response?: { data?: { error?: { message?: string } } } }
    error.value = err?.response?.data?.error?.message || 'Erreur lors de la création du devoir.'
  } finally {
    creating.value = false
  }
}

async function deleteAssignment(classId: number, assignmentId: number) {
  if (!confirm('Supprimer ce devoir ?')) return
  await classService.deleteAssignment(classId, assignmentId)
  const updated = [...classes.value]
  const idx = updated.findIndex(c => c.id === classId)
  if (idx !== -1) {
    updated[idx].assignments = updated[idx].assignments.filter(a => a.id !== assignmentId)
  }
  classes.value = updated
}

function openCreateAssignment(classId: number) {
  selectedClassId.value = classId
  showCreateAssignmentModal.value = true
  error.value = ''
}

function formatDate(d: string | null) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
}

function isDueSoon(d: string | null): boolean {
  if (!d) return false
  const days = (new Date(d).getTime() - Date.now()) / 86400000
  return days >= 0 && days <= 3
}

function isPast(d: string | null): boolean {
  if (!d) return false
  return new Date(d) < new Date()
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-[#0B0F19] p-6">
    <!-- Header -->
    <div class="mb-8 flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
          <span class="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-orange-600 text-white shadow-lg shadow-amber-500/30">
            <GraduationCap class="w-5 h-5" />
          </span>
          Espace Professeur
        </h1>
        <p class="mt-1 text-slate-500 dark:text-slate-400 text-sm">
          Gérez vos classes, publiez des devoirs et suivez la progression de vos élèves.
        </p>
      </div>
      <button
        @click="showCreateClassModal = true; error = ''"
        class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-white font-medium text-sm shadow-lg shadow-amber-500/25 transition-all"
      >
        <Plus class="w-4 h-4" />
        Créer une classe
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-amber-500 animate-spin" />
    </div>

    <!-- Empty state -->
    <div v-else-if="classes.length === 0" class="text-center py-24">
      <div class="flex items-center justify-center w-20 h-20 rounded-2xl bg-amber-50 dark:bg-amber-900/20 mx-auto mb-5">
        <GraduationCap class="w-10 h-10 text-amber-400" />
      </div>
      <h3 class="text-xl font-semibold text-slate-900 dark:text-white mb-2">Aucune classe pour l'instant</h3>
      <p class="text-slate-500 dark:text-slate-400 mb-6 max-w-md mx-auto text-sm">
        Créez votre premier espace de cours et invitez vos élèves avec un code d'invitation unique.
      </p>
      <button
        @click="showCreateClassModal = true"
        class="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-white font-medium text-sm transition-colors mx-auto"
      >
        <Plus class="w-4 h-4" />
        Créer une classe
      </button>
    </div>

    <!-- Classes list -->
    <div v-else class="space-y-6">
      <div
        v-for="cls in classes"
        :key="cls.id"
        class="bg-white dark:bg-slate-800/60 rounded-2xl border border-slate-100 dark:border-slate-700/60 shadow-sm overflow-hidden"
      >
        <!-- Class header -->
        <div class="h-1.5 bg-gradient-to-r from-amber-500 to-orange-500"></div>
        <div class="p-5">
          <div class="flex items-center justify-between gap-4 mb-4">
            <div class="flex items-center gap-3 min-w-0">
              <div class="flex items-center justify-center w-11 h-11 rounded-xl bg-gradient-to-tr from-amber-100 to-orange-100 dark:from-amber-900/30 dark:to-orange-900/20 flex-shrink-0">
                <GraduationCap class="w-5 h-5 text-amber-600 dark:text-amber-400" />
              </div>
              <div class="min-w-0">
                <h2 class="font-bold text-slate-900 dark:text-white text-lg truncate">{{ cls.name }}</h2>
                <div class="flex items-center gap-3 text-xs text-slate-400 mt-0.5">
                  <span class="flex items-center gap-1"><Users class="w-3 h-3" />{{ cls.members_count }} élèves</span>
                  <span class="flex items-center gap-1"><ClipboardList class="w-3 h-3" />{{ cls.assignments.length }} devoirs</span>
                  <span class="font-mono tracking-wider bg-slate-100 dark:bg-slate-700 px-2 py-0.5 rounded">{{ cls.invite_code }}</span>
                </div>
              </div>
            </div>
            <div class="flex gap-2">
              <button
                @click="router.push(`/groups/${cls.id}`)"
                class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 text-xs font-medium transition"
              >
                <Eye class="w-3.5 h-3.5" />
                Vue groupe
              </button>
              <button
                @click="openCreateAssignment(cls.id)"
                class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-white text-xs font-medium transition"
              >
                <Plus class="w-3.5 h-3.5" />
                Nouveau devoir
              </button>
            </div>
          </div>

          <!-- Assignments table -->
          <div v-if="cls.assignments.length === 0" class="text-center py-8 text-slate-400 dark:text-slate-600 text-sm">
            <ClipboardList class="w-8 h-8 mx-auto mb-2 opacity-50" />
            Aucun devoir assigné pour cette classe.
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="asgn in cls.assignments"
              :key="asgn.id"
              class="flex items-center justify-between gap-3 bg-slate-50 dark:bg-slate-900/40 rounded-xl px-4 py-3"
            >
              <div class="flex items-center gap-3 min-w-0">
                <div :class="[
                  'flex-shrink-0 w-2 h-2 rounded-full',
                  isPast(asgn.due_date) ? 'bg-red-500' : isDueSoon(asgn.due_date) ? 'bg-amber-500' : 'bg-green-500'
                ]"></div>
                <div class="min-w-0">
                  <p class="font-medium text-slate-800 dark:text-white text-sm truncate">{{ asgn.title }}</p>
                  <p class="text-xs text-slate-400 mt-0.5">{{ asgn.binder_name }}</p>
                </div>
              </div>
              <div class="flex items-center gap-3 flex-shrink-0">
                <span :class="[
                  'flex items-center gap-1 text-xs font-medium',
                  isPast(asgn.due_date) ? 'text-red-500' : isDueSoon(asgn.due_date) ? 'text-amber-500' : 'text-slate-500'
                ]">
                  <Calendar class="w-3.5 h-3.5" />
                  {{ formatDate(asgn.due_date) }}
                </span>
                <button
                  @click="router.push(`/classes/${cls.id}/assignments/${asgn.id}`)"
                  class="p-1.5 rounded-lg text-slate-400 hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition"
                  title="Voir la progression"
                >
                  <BarChart3 class="w-4 h-4" />
                </button>
                <button
                  @click="deleteAssignment(cls.id, asgn.id)"
                  class="p-1.5 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition"
                  title="Supprimer"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Class Modal -->
    <Teleport to="body">
      <div v-if="showCreateClassModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" @click.self="showCreateClassModal = false">
        <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-md border border-slate-200 dark:border-slate-700">
          <div class="p-6 border-b border-slate-100 dark:border-slate-700">
            <h2 class="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <GraduationCap class="w-5 h-5 text-amber-500" />
              Créer une classe
            </h2>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Nom de la classe <span class="text-red-500">*</span></label>
              <input v-model="newClassName" type="text" placeholder="Ex : PACES 2025 — Biologie cellulaire" maxlength="100"
                class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 transition"
                @keydown.enter="createClass" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Description (optionnel)</label>
              <textarea v-model="newClassDesc" placeholder="Objectifs du cours, niveau requis…" rows="3"
                class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 transition resize-none" />
            </div>
            <div v-if="error" class="flex items-center gap-2 text-red-500 text-sm"><AlertCircle class="w-4 h-4 flex-shrink-0" />{{ error }}</div>
          </div>
          <div class="p-6 pt-0 flex gap-3">
            <button @click="showCreateClassModal = false" class="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition text-sm font-medium">Annuler</button>
            <button @click="createClass" :disabled="!newClassName.trim() || creating"
              class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-white font-medium text-sm transition">
              <Loader2 v-if="creating" class="w-4 h-4 animate-spin" />
              <Plus v-else class="w-4 h-4" />
              Créer
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Create Assignment Modal -->
    <Teleport to="body">
      <div v-if="showCreateAssignmentModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" @click.self="showCreateAssignmentModal = false">
        <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-md border border-slate-200 dark:border-slate-700">
          <div class="p-6 border-b border-slate-100 dark:border-slate-700">
            <h2 class="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <ClipboardList class="w-5 h-5 text-amber-500" />
              Nouveau devoir
            </h2>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Titre <span class="text-red-500">*</span></label>
              <input v-model="newAsgTitle" type="text" placeholder="Ex : Chapitre 3 — Mitose"
                class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 transition" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Classeur associé <span class="text-red-500">*</span></label>
              <select v-model="newAsgBinderId"
                class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-amber-500 transition">
                <option :value="null" disabled>Choisir un classeur…</option>
                <option v-for="b in bindersStore.binders" :key="b.id" :value="b.id">{{ b.name }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Description (optionnel)</label>
              <textarea v-model="newAsgDesc" placeholder="Consignes, chapitres concernés…" rows="2"
                class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 transition resize-none" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Date limite (optionnel)</label>
              <input v-model="newAsgDueDate" type="datetime-local"
                class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-amber-500 transition" />
            </div>
            <div v-if="error" class="flex items-center gap-2 text-red-500 text-sm"><AlertCircle class="w-4 h-4 flex-shrink-0" />{{ error }}</div>
          </div>
          <div class="p-6 pt-0 flex gap-3">
            <button @click="showCreateAssignmentModal = false" class="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition text-sm font-medium">Annuler</button>
            <button @click="createAssignment" :disabled="!newAsgTitle.trim() || !newAsgBinderId || creating"
              class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-white font-medium text-sm transition">
              <Loader2 v-if="creating" class="w-4 h-4 animate-spin" />
              <Plus v-else class="w-4 h-4" />
              Créer le devoir
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
