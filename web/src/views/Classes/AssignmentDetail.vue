<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import classService from '../../services/classService'
import type { Assignment, AssignmentProgress } from '../../services/classService'
import {
  ClipboardList, Calendar,
  BarChart3, Users, CheckCircle2, AlertCircle,
  ChevronLeft, Loader2, BookOpen, Clock, Award
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const classId = Number(route.params.classId)
const assignmentId = Number(route.params.asgnId)

const assignment = ref<Assignment | null>(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  loading.value = true
  try {
    assignment.value = await classService.getAssignment(classId, assignmentId)
  } catch (e: any) {
    error.value = e?.response?.data?.error?.message || "Impossible de charger les détails du devoir."
  } finally {
    loading.value = false
  }
})

// Stats calculations
const students = computed<AssignmentProgress[]>(() => {
  return assignment.value?.progress || []
})

const totalStudents = computed(() => students.value.length)

const completedStudentsCount = computed(() => {
  return students.value.filter(s => s.completed_at !== null || s.score_pct !== null).length
})

const completionRate = computed(() => {
  if (totalStudents.value === 0) return 0
  return Math.round((completedStudentsCount.value / totalStudents.value) * 100)
})

const averageScore = computed(() => {
  const graded = students.value.filter(s => s.score_pct !== null)
  if (graded.length === 0) return null
  const sum = graded.reduce((acc, curr) => acc + (curr.score_pct || 0), 0)
  return Math.round(sum / graded.length)
})

function formatDate(d: string | null) {
  if (!d) return 'Pas de date limite'
  return new Date(d).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatSimpleDate(d: string | null) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short'
  })
}

function getStudentStatus(student: AssignmentProgress) {
  if (student.completed_at !== null || student.score_pct !== null) return 'completed'
  if (student.cards_reviewed > 0) return 'in_progress'
  return 'not_started'
}

function getStatusLabel(status: string) {
  if (status === 'completed') return 'Terminé'
  if (status === 'in_progress') return 'En cours'
  return 'Non démarré'
}

function getStatusBadgeClass(status: string) {
  if (status === 'completed') return 'bg-green-50 text-green-700 border-green-200 dark:bg-green-950/20 dark:text-green-400 dark:border-green-900/30'
  if (status === 'in_progress') return 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/20 dark:text-blue-400 dark:border-blue-900/30'
  return 'bg-slate-50 text-slate-500 border-slate-200 dark:bg-slate-900/40 dark:text-slate-400 dark:border-slate-800'
}

function getScoreColorClass(score: number | null) {
  if (score === null) return 'text-slate-400'
  if (score >= 80) return 'text-green-600 dark:text-green-400'
  if (score >= 50) return 'text-amber-600 dark:text-amber-400'
  return 'text-red-500'
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-[#0B0F19] p-6">
    <!-- Navigation Back -->
    <div class="mb-6">
      <button
        @click="router.push('/classes/teacher')"
        class="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-650 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-slate-700 text-xs font-semibold shadow-sm transition"
      >
        <ChevronLeft class="w-4 h-4" />
        Retour à l'Espace Professeur
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-amber-505 animate-spin text-amber-500" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="p-6 bg-red-50 border border-red-150 rounded-2xl dark:bg-red-950/20 dark:border-red-900/30 text-red-600 dark:text-red-400">
      <p class="font-semibold flex items-center gap-2">
        <AlertCircle class="w-5 h-5" />
        {{ error }}
      </p>
    </div>

    <!-- Detail Content -->
    <div v-else-if="assignment" class="space-y-6">
      <!-- Info Header Card -->
      <div class="bg-white dark:bg-slate-800/60 rounded-3xl border border-slate-100 dark:border-slate-700/60 shadow-sm p-6 relative overflow-hidden">
        <div class="absolute -right-10 -top-10 w-36 h-36 bg-amber-500/5 dark:bg-amber-500/10 rounded-full blur-2xl pointer-events-none"></div>
        
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div class="space-y-3 max-w-2xl">
            <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-amber-50 text-amber-600 border border-amber-200 dark:bg-amber-950/30 dark:text-amber-400 dark:border-amber-900/30">
              <ClipboardList class="w-3 h-3" />
              Détails du Devoir
            </span>
            <h1 class="text-2xl font-bold text-slate-900 dark:text-white">{{ assignment.title }}</h1>
            <p v-if="assignment.description" class="text-sm text-slate-500 dark:text-slate-400">{{ assignment.description }}</p>
            
            <div class="flex flex-wrap gap-4 text-xs font-medium text-slate-400 pt-1">
              <span class="flex items-center gap-1.5">
                <BookOpen class="w-4 h-4 text-indigo-400" />
                Classeur : <strong class="text-slate-600 dark:text-slate-350">{{ assignment.binder_name }}</strong>
              </span>
              <span class="flex items-center gap-1.5">
                <Calendar class="w-4 h-4 text-amber-500" />
                Limite : <strong class="text-slate-600 dark:text-slate-350">{{ formatDate(assignment.due_date) }}</strong>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Card 1: Total Members -->
        <div class="bg-white dark:bg-slate-800/60 rounded-2xl border border-slate-100 dark:border-slate-700/60 p-5 shadow-sm flex items-center gap-4">
          <div class="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center text-blue-600 dark:text-blue-400 flex-shrink-0">
            <Users class="w-5 h-5" />
          </div>
          <div>
            <span class="text-slate-400 text-xs font-semibold uppercase tracking-wider">Total Élèves</span>
            <h4 class="text-2xl font-black mt-0.5 text-slate-800 dark:text-white">{{ totalStudents }}</h4>
          </div>
        </div>

        <!-- Card 2: Completed -->
        <div class="bg-white dark:bg-slate-800/60 rounded-2xl border border-slate-100 dark:border-slate-700/60 p-5 shadow-sm flex items-center gap-4">
          <div class="w-10 h-10 rounded-xl bg-green-50 dark:bg-green-900/20 flex items-center justify-center text-green-600 dark:text-green-400 flex-shrink-0">
            <CheckCircle2 class="w-5 h-5" />
          </div>
          <div>
            <span class="text-slate-400 text-xs font-semibold uppercase tracking-wider">Devoirs Remplis</span>
            <h4 class="text-2xl font-black mt-0.5 text-slate-800 dark:text-white">{{ completedStudentsCount }}</h4>
          </div>
        </div>

        <!-- Card 3: Completion Rate -->
        <div class="bg-white dark:bg-slate-800/60 rounded-2xl border border-slate-100 dark:border-slate-700/60 p-5 shadow-sm flex items-center gap-4">
          <div class="w-10 h-10 rounded-xl bg-amber-50 dark:bg-amber-900/20 flex items-center justify-center text-amber-600 dark:text-amber-400 flex-shrink-0">
            <BarChart3 class="w-5 h-5" />
          </div>
          <div>
            <span class="text-slate-400 text-xs font-semibold uppercase tracking-wider font-medium">Taux de Complétion</span>
            <h4 class="text-2xl font-black mt-0.5 text-slate-800 dark:text-white">{{ completionRate }}%</h4>
          </div>
        </div>

        <!-- Card 4: Average Score -->
        <div class="bg-white dark:bg-slate-800/60 rounded-2xl border border-slate-100 dark:border-slate-700/60 p-5 shadow-sm flex items-center gap-4">
          <div class="w-10 h-10 rounded-xl bg-purple-50 dark:bg-purple-900/20 flex items-center justify-center text-purple-600 dark:text-purple-400 flex-shrink-0">
            <Award class="w-5 h-5" />
          </div>
          <div>
            <span class="text-slate-400 text-xs font-semibold uppercase tracking-wider">Moyenne de Classe</span>
            <h4 class="text-2xl font-black mt-0.5 text-slate-800 dark:text-white">
              {{ averageScore !== null ? `${averageScore}%` : '—' }}
            </h4>
          </div>
        </div>
      </div>

      <!-- Students Progress Table -->
      <div class="bg-white dark:bg-slate-800/60 rounded-3xl border border-slate-100 dark:border-slate-700/60 shadow-sm p-6 overflow-hidden">
        <h3 class="font-bold text-slate-850 dark:text-white text-lg flex items-center gap-2 mb-6">
          <Users class="w-5 h-5 text-amber-500" />
          Progression Individuelle
        </h3>

        <div v-if="students.length === 0" class="text-center py-16 text-slate-400 dark:text-slate-650">
          <Users class="w-12 h-12 mx-auto mb-3 opacity-30" />
          Aucun élève n'a rejoint cette classe pour l'instant.
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b border-slate-100 dark:border-slate-700 text-xs font-bold uppercase tracking-wider text-slate-400">
                <th class="py-3 px-4">Élève</th>
                <th class="py-3 px-4">Statut</th>
                <th class="py-3 px-4">Cartes révisées</th>
                <th class="py-3 px-4">Score</th>
                <th class="py-3 px-4">Rendu le</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50 dark:divide-slate-700/50">
              <tr
                v-for="student in students"
                :key="student.user_id"
                class="hover:bg-slate-50/50 dark:hover:bg-slate-900/10 transition"
              >
                <!-- Name -->
                <td class="py-4 px-4 font-semibold text-sm text-slate-800 dark:text-white">
                  {{ student.username }}
                </td>

                <!-- Status -->
                <td class="py-4 px-4">
                  <span
                    class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-xl text-xs font-semibold border"
                    :class="getStatusBadgeClass(getStudentStatus(student))"
                  >
                    <span
                      class="w-1.5 h-1.5 rounded-full"
                      :class="[
                        getStudentStatus(student) === 'completed' ? 'bg-green-500' :
                        getStudentStatus(student) === 'in_progress' ? 'bg-blue-500' : 'bg-slate-400'
                      ]"
                    ></span>
                    {{ getStatusLabel(getStudentStatus(student)) }}
                  </span>
                </td>

                <!-- Cards Reviewed -->
                <td class="py-4 px-4 text-xs font-semibold text-slate-550 dark:text-slate-400">
                  <span class="flex items-center gap-1.5">
                    <BookOpen class="w-3.5 h-3.5 text-indigo-400" />
                    {{ student.cards_reviewed }} cartes
                  </span>
                </td>

                <!-- Score -->
                <td class="py-4 px-4">
                  <div class="flex items-center gap-2">
                    <span
                      class="text-sm font-bold"
                      :class="getScoreColorClass(student.score_pct)"
                    >
                      {{ student.score_pct !== null ? `${Math.round(student.score_pct)}%` : '—' }}
                    </span>
                    <!-- Miniature progress bar -->
                    <div v-if="student.score_pct !== null" class="w-16 h-1.5 rounded-full bg-slate-100 dark:bg-slate-700 overflow-hidden">
                      <div
                        class="h-full rounded-full transition-all"
                        :class="[
                          student.score_pct >= 80 ? 'bg-green-500' :
                          student.score_pct >= 50 ? 'bg-amber-500' : 'bg-red-500'
                        ]"
                        :style="{ width: student.score_pct + '%' }"
                      ></div>
                    </div>
                  </div>
                </td>

                <!-- Completed At -->
                <td class="py-4 px-4 text-xs font-semibold text-slate-450 dark:text-slate-400">
                  <span v-if="student.completed_at" class="flex items-center gap-1.5">
                    <Clock class="w-3.5 h-3.5 text-slate-400" />
                    {{ formatSimpleDate(student.completed_at) }}
                  </span>
                  <span v-else class="text-slate-350 dark:text-slate-600">—</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
