<script setup lang="ts">
import { ref, computed } from 'vue'
import classService from '../../services/classService'
import type { Assignment, AssignmentTaskInput, TaskType } from '../../services/classService'
import {
  ClipboardList, Plus, Trash2, Loader2, AlertCircle,
  Layers, FileQuestion, GraduationCap, PenLine, BookOpen, ListChecks,
} from 'lucide-vue-next'

const props = defineProps<{
  classId: number
  binders: Array<{ id: string; name: string }>
  notes: Array<{ id: string; title: string }>
  sets?: Array<{ id: number; name: string }>
}>()

const emit = defineEmits<{
  (e: 'created', assignment: Assignment): void
  (e: 'close'): void
}>()

interface DraftTask {
  task_type: TaskType
  ref: string
  min_cards?: number | null
  min_score?: number | null
  min_items?: number | null
}

const title = ref('')
const description = ref('')
const dueDate = ref('')
const tasks = ref<DraftTask[]>([{ task_type: 'flashcards', ref: '' }])
const creating = ref(false)
const error = ref('')

// Métadonnées par type : libellé, icône, et nature de la cible (classeur, note ou ensemble de révision).
const TASK_META: Record<TaskType, { label: string; icon: unknown; target: 'binder' | 'note' | 'set' }> = {
  flashcards: { label: 'Flashcards', icon: Layers, target: 'binder' },
  quiz: { label: 'QCM (note)', icon: FileQuestion, target: 'note' },
  exam: { label: 'Examen blanc', icon: GraduationCap, target: 'binder' },
  blurting: { label: 'Blurting (feuille blanche)', icon: PenLine, target: 'note' },
  read: { label: 'Lecture', icon: BookOpen, target: 'note' },
  revision: { label: 'Ensemble de révision', icon: ListChecks, target: 'set' },
}

const taskTypes = Object.keys(TASK_META) as TaskType[]

function targetOptions(type: TaskType): Array<{ id: string; name: string }> {
  const target = TASK_META[type].target
  if (target === 'binder') return props.binders
  if (target === 'set') return (props.sets ?? []).map(s => ({ id: String(s.id), name: s.name }))
  return props.notes.map(n => ({ id: n.id, name: n.title }))
}

function targetPlaceholder(type: TaskType): string {
  const target = TASK_META[type].target
  if (target === 'binder') return 'Choisir un classeur…'
  if (target === 'set') return 'Choisir un ensemble de révision…'
  return 'Choisir une note…'
}

function addTask() {
  tasks.value.push({ task_type: 'flashcards', ref: '' })
}

function removeTask(idx: number) {
  tasks.value.splice(idx, 1)
}

function onTypeChange(t: DraftTask) {
  // Le changement de type invalide la cible précédente (classeur vs note vs ensemble).
  t.ref = ''
  t.min_cards = null
  t.min_score = null
  t.min_items = null
}

const canSubmit = computed(() =>
  title.value.trim().length > 0 &&
  tasks.value.length > 0 &&
  tasks.value.every(t => t.ref)
)

async function submit() {
  if (!canSubmit.value) return
  creating.value = true
  error.value = ''
  try {
    const payloadTasks: AssignmentTaskInput[] = tasks.value.map(t => {
      const goal: Record<string, number> = {}
      if (t.task_type === 'flashcards') {
        if (t.min_cards) goal.min_cards = Number(t.min_cards)
        if (t.min_score) goal.min_score = Number(t.min_score)
      } else if (t.task_type === 'revision') {
        if (t.min_items) goal.min_items = Number(t.min_items)
        if (t.min_score) goal.min_score = Number(t.min_score)
      }
      return {
        task_type: t.task_type,
        ref: t.ref,
        ...(Object.keys(goal).length ? { goal } : {}),
      }
    })
    const assignment = await classService.createAssignment(props.classId, {
      title: title.value.trim(),
      description: description.value.trim() || undefined,
      due_date: dueDate.value || undefined,
      tasks: payloadTasks,
    })
    emit('created', assignment)
  } catch (e: unknown) {
    const err = e as { response?: { data?: { error?: { message?: string } } } }
    error.value = err?.response?.data?.error?.message || 'Erreur lors de la création du devoir.'
  } finally {
    creating.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" @click.self="emit('close')">
      <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-lg border border-slate-200 dark:border-slate-700 max-h-[90vh] flex flex-col">
        <div class="p-6 border-b border-slate-100 dark:border-slate-700 flex-shrink-0">
          <h2 class="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <ClipboardList class="w-5 h-5 text-amber-500" />
            Nouveau devoir
          </h2>
          <p class="text-xs text-slate-400 mt-1">Composez un devoir avec une ou plusieurs activités.</p>
        </div>

        <div class="p-6 space-y-4 overflow-y-auto">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Titre <span class="text-red-500">*</span></label>
            <input v-model="title" type="text" placeholder="Ex : Chapitre 3 — Mitose"
              class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 transition" />
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Consignes (optionnel)</label>
            <textarea v-model="description" placeholder="Chapitres concernés, attentes…" rows="2"
              class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 transition resize-none" />
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Date limite (optionnel)</label>
            <input v-model="dueDate" type="datetime-local"
              class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-amber-500 transition" />
          </div>

          <!-- Tâches -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <label class="block text-sm font-bold text-slate-800 dark:text-slate-200">Activités <span class="text-red-500">*</span></label>
              <button type="button" @click="addTask"
                class="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 text-xs font-semibold hover:bg-amber-100 transition">
                <Plus class="w-3.5 h-3.5" /> Ajouter
              </button>
            </div>

            <div class="space-y-3">
              <div v-for="(t, idx) in tasks" :key="idx"
                class="rounded-xl border border-slate-150 dark:border-slate-700/60 bg-slate-50/60 dark:bg-slate-900/30 p-3 space-y-2">
                <div class="flex items-center gap-2">
                  <component :is="TASK_META[t.task_type].icon" class="w-4 h-4 text-amber-500 flex-shrink-0" />
                  <select v-model="t.task_type" @change="onTypeChange(t)"
                    class="flex-1 px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-amber-500">
                    <option v-for="tt in taskTypes" :key="tt" :value="tt">{{ TASK_META[tt].label }}</option>
                  </select>
                  <button v-if="tasks.length > 1" type="button" @click="removeTask(idx)"
                    class="p-1.5 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition">
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>

                <select v-model="t.ref"
                  class="w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-amber-500">
                  <option value="" disabled>{{ targetPlaceholder(t.task_type) }}</option>
                  <option v-for="opt in targetOptions(t.task_type)" :key="opt.id" :value="opt.id">{{ opt.name }}</option>
                </select>

                <!-- Objectif pour les flashcards -->
                <div v-if="t.task_type === 'flashcards'" class="flex gap-2">
                  <input v-model.number="t.min_cards" type="number" min="1" placeholder="Cartes min."
                    class="w-1/2 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white text-xs focus:outline-none focus:ring-2 focus:ring-amber-500" />
                  <input v-model.number="t.min_score" type="number" min="1" max="100" placeholder="Score min. %"
                    class="w-1/2 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white text-xs focus:outline-none focus:ring-2 focus:ring-amber-500" />
                </div>

                <!-- Objectif pour un ensemble de révision -->
                <div v-if="t.task_type === 'revision'" class="flex gap-2">
                  <input v-model.number="t.min_items" type="number" min="1" placeholder="Items min."
                    class="w-1/2 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white text-xs focus:outline-none focus:ring-2 focus:ring-amber-500" />
                  <input v-model.number="t.min_score" type="number" min="1" max="100" placeholder="Score min. %"
                    class="w-1/2 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white text-xs focus:outline-none focus:ring-2 focus:ring-amber-500" />
                </div>
              </div>
            </div>
          </div>

          <div v-if="error" class="flex items-center gap-2 text-red-500 text-sm"><AlertCircle class="w-4 h-4 flex-shrink-0" />{{ error }}</div>
        </div>

        <div class="p-6 pt-4 flex gap-3 border-t border-slate-100 dark:border-slate-700 flex-shrink-0">
          <button @click="emit('close')" class="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition text-sm font-medium">Annuler</button>
          <button @click="submit" :disabled="!canSubmit || creating"
            class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-white font-medium text-sm transition">
            <Loader2 v-if="creating" class="w-4 h-4 animate-spin" />
            <Plus v-else class="w-4 h-4" />
            Créer le devoir
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
