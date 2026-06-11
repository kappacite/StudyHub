<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import classService from '../../services/classService'
import type { AssignmentSummary } from '../../services/classService'
import {
  ClipboardList, Calendar, CheckCircle2, Clock, AlertTriangle,
  Loader2, BookOpen, ArrowRight, GraduationCap
} from 'lucide-vue-next'

const router = useRouter()

const assignments = ref<AssignmentSummary[]>([])
const loading = ref(true)
const filterStatus = ref<'all' | 'todo' | 'in_progress' | 'done' | 'late'>('all')

onMounted(async () => {
  loading.value = true
  assignments.value = await classService.getMyAssignments().catch(() => [])
  loading.value = false
})

const filtered = computed(() => {
  if (filterStatus.value === 'all') return assignments.value
  return assignments.value.filter(a => a.status === filterStatus.value)
})

const statusCounts = computed(() => ({
  all: assignments.value.length,
  todo: assignments.value.filter(a => a.status === 'todo').length,
  in_progress: assignments.value.filter(a => a.status === 'in_progress').length,
  late: assignments.value.filter(a => a.status === 'late').length,
  done: assignments.value.filter(a => a.status === 'done').length
}))

function formatDate(d: string | null) {
  if (!d) return 'Pas de deadline'
  return new Date(d).toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric', month: 'long' })
}

function daysUntil(d: string | null): string {
  if (!d) return ''
  const diff = Math.round((new Date(d).getTime() - Date.now()) / 86400000)
  if (diff < 0) return `${Math.abs(diff)}j de retard`
  if (diff === 0) return 'Aujourd\'hui !'
  if (diff === 1) return 'Demain'
  return `Dans ${diff} jours`
}

function statusLabel(s: string) {
  return { todo: 'À faire', in_progress: 'En cours', done: 'Terminé', late: 'En retard' }[s] ?? s
}

function statusBadgeClass(s: string) {
  return {
    todo: 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300',
    in_progress: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
    done: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    late: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
  }[s] ?? ''
}

function statusIcon(s: string) {
  return { todo: Clock, in_progress: ArrowRight, done: CheckCircle2, late: AlertTriangle }[s] ?? Clock
}

function cardBorderClass(s: string) {
  return {
    todo: 'border-slate-100 dark:border-slate-700/60',
    in_progress: 'border-blue-100 dark:border-blue-800/40',
    done: 'border-green-100 dark:border-green-800/40',
    late: 'border-red-100 dark:border-red-800/40'
  }[s] ?? ''
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-[#0B0F19] p-6">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
        <span class="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-blue-600 text-white shadow-lg shadow-sky-500/30">
          <GraduationCap class="w-5 h-5" />
        </span>
        Mes Devoirs
      </h1>
      <p class="mt-1 text-slate-500 dark:text-slate-400 text-sm">
        Suivez vos devoirs assignés par vos professeurs.
      </p>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap gap-2 mb-6">
      <button
        v-for="tab in [
          { id: 'all', label: `Tous (${statusCounts.all})` },
          { id: 'late', label: `En retard (${statusCounts.late})` },
          { id: 'todo', label: `À faire (${statusCounts.todo})` },
          { id: 'in_progress', label: `En cours (${statusCounts.in_progress})` },
          { id: 'done', label: `Terminés (${statusCounts.done})` }
        ]"
        :key="tab.id"
        @click="filterStatus = tab.id as typeof filterStatus"
        :class="[
          'px-4 py-2 rounded-xl text-sm font-medium transition-all',
          filterStatus === tab.id
            ? 'bg-sky-600 text-white shadow-sm'
            : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:border-sky-300'
        ]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-sky-500 animate-spin" />
    </div>

    <!-- Empty -->
    <div v-else-if="filtered.length === 0" class="text-center py-20">
      <ClipboardList class="w-12 h-12 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
      <p class="text-slate-500 dark:text-slate-400">
        {{ filterStatus === 'all' ? 'Aucun devoir assigné pour l\'instant.' : 'Aucun devoir dans cette catégorie.' }}
      </p>
    </div>

    <!-- Assignments list -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <article
        v-for="asgn in filtered"
        :key="asgn.id"
        class="bg-white dark:bg-slate-800/60 rounded-2xl border shadow-sm hover:shadow-md transition-all duration-300"
        :class="cardBorderClass(asgn.status)"
      >
        <!-- Top accent bar -->
        <div :class="[
          'h-1.5 rounded-t-2xl',
          asgn.status === 'done' ? 'bg-green-500' : asgn.status === 'late' ? 'bg-red-500' : asgn.status === 'in_progress' ? 'bg-blue-500' : 'bg-slate-300 dark:bg-slate-600'
        ]"></div>

        <div class="p-5">
          <!-- Class name -->
          <div class="flex items-center gap-1.5 text-xs text-slate-400 mb-2">
            <GraduationCap class="w-3 h-3" />
            {{ asgn.group_name }}
          </div>

          <!-- Title & status -->
          <div class="flex items-start justify-between gap-2 mb-3">
            <h3 class="font-bold text-slate-900 dark:text-white text-base leading-snug">{{ asgn.title }}</h3>
            <span :class="['flex items-center gap-1 px-2 py-0.5 rounded-lg text-xs font-medium flex-shrink-0', statusBadgeClass(asgn.status)]">
              <component :is="statusIcon(asgn.status)" class="w-3 h-3" />
              {{ statusLabel(asgn.status) }}
            </span>
          </div>

          <!-- Binder -->
          <div class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-3">
            <BookOpen class="w-4 h-4 flex-shrink-0" />
            <span class="truncate">{{ asgn.binder_name }}</span>
          </div>

          <!-- Due date -->
          <div :class="[
            'flex items-center justify-between text-xs rounded-xl px-3 py-2 mb-4',
            asgn.status === 'late' ? 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400' : 'bg-slate-50 dark:bg-slate-900/40 text-slate-500 dark:text-slate-400'
          ]">
            <span class="flex items-center gap-1.5">
              <Calendar class="w-3.5 h-3.5" />
              {{ formatDate(asgn.due_date) }}
            </span>
            <span v-if="asgn.due_date" class="font-medium">{{ daysUntil(asgn.due_date) }}</span>
          </div>

          <!-- Progress -->
          <div v-if="asgn.my_cards_reviewed > 0" class="mb-4">
            <div class="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span>{{ asgn.my_cards_reviewed }} cartes révisées</span>
              <span v-if="asgn.my_score_pct !== null" class="font-medium" :class="asgn.my_score_pct >= 80 ? 'text-green-600' : 'text-amber-600'">
                {{ Math.round(asgn.my_score_pct) }}%
              </span>
            </div>
          </div>

          <!-- CTA -->
          <button
            @click="router.push(`/binders/${asgn.binder_id}`)"
            :disabled="asgn.status === 'done'"
            :class="[
              'w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium transition-all',
              asgn.status === 'done'
                ? 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 cursor-default'
                : 'bg-sky-600 hover:bg-sky-500 text-white shadow-sm'
            ]"
          >
            <CheckCircle2 v-if="asgn.status === 'done'" class="w-4 h-4" />
            <BookOpen v-else class="w-4 h-4" />
            {{ asgn.status === 'done' ? 'Terminé ✓' : 'Ouvrir le classeur' }}
          </button>
        </div>
      </article>
    </div>
  </div>
</template>
