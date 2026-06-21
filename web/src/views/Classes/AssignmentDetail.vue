<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import classService from '../../services/classService'
import type { Assignment, AssignmentProgress } from '../../services/classService'
import {
  ClipboardList, Calendar,
  BarChart3, Users, CheckCircle2, AlertCircle,
  ChevronLeft, Loader2, BookOpen, Clock, Award, Check
} from 'lucide-vue-next'

// Notation par élève (saisie locale + sauvegarde)
const grading = ref<Record<number, { score: number | null; feedback: string }>>({})
const savingId = ref<number | null>(null)

function gradeFor(userId: number) {
  if (!grading.value[userId]) grading.value[userId] = { score: null, feedback: '' }
  return grading.value[userId]
}

async function saveGrade(student: AssignmentProgress) {
  const g = gradeFor(student.user_id)
  savingId.value = student.user_id
  try {
    const updated = await classService.gradeSubmission(classId, assignmentId, student.user_id, {
      teacher_score: g.score ?? undefined,
      teacher_feedback: g.feedback || undefined,
    })
    // Refléter la note dans la ligne
    student.teacher_score = updated.teacher_score
    student.teacher_feedback = updated.teacher_feedback
    student.graded_at = updated.graded_at
  } catch (e) {
    console.error(e)
  } finally {
    savingId.value = null
  }
}

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
    for (const p of assignment.value?.progress || []) {
      grading.value[p.user_id] = {
        score: p.teacher_score ?? null,
        feedback: p.teacher_feedback ?? '',
      }
    }
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
  if (status === 'completed') return 'bg-success-soft text-success border-success/30'
  if (status === 'in_progress') return 'bg-info-soft text-info border-info/30'
  return 'bg-surface-soft text-ink-muted border-line'
}

function getStatusDotClass(status: string) {
  if (status === 'completed') return 'bg-success'
  if (status === 'in_progress') return 'bg-info'
  return 'bg-ink-subtle'
}

function getScoreColorClass(score: number | null) {
  if (score === null) return 'text-ink-subtle'
  if (score >= 80) return 'text-success'
  if (score >= 50) return 'text-warning'
  return 'text-danger'
}

function getScoreBarClass(score: number) {
  if (score >= 80) return 'bg-success'
  if (score >= 50) return 'bg-warning'
  return 'bg-danger'
}
</script>

<template>
  <div class="min-h-screen bg-app p-6">
    <!-- Retour -->
    <div class="mb-6">
      <button
        @click="router.push('/classes?tab=teacher')"
        class="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl border border-line bg-surface text-ink-muted hover:bg-surface-soft text-xs font-semibold shadow-elev-1 transition"
      >
        <ChevronLeft class="w-4 h-4" />
        Retour à l'Espace Professeur
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-primary animate-spin" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="p-6 bg-danger-soft border border-danger/30 rounded-2xl text-danger">
      <p class="font-semibold flex items-center gap-2">
        <AlertCircle class="w-5 h-5" />
        {{ error }}
      </p>
    </div>

    <!-- Contenu -->
    <div v-else-if="assignment" class="space-y-6">
      <!-- Carte d'en-tête -->
      <div class="bg-surface rounded-3xl border border-line shadow-elev-1 p-6 relative overflow-hidden">
        <div class="absolute -right-10 -top-10 w-36 h-36 bg-primary/5 rounded-full blur-2xl pointer-events-none"></div>

        <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div class="space-y-3 max-w-2xl">
            <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-accent-soft text-accent border border-accent/30">
              <ClipboardList class="w-3 h-3" />
              Détails du Devoir
            </span>
            <h1 class="text-2xl font-bold text-ink">{{ assignment.title }}</h1>
            <p v-if="assignment.description" class="text-sm text-ink-muted">{{ assignment.description }}</p>

            <div class="flex flex-wrap gap-4 text-xs font-medium text-ink-subtle pt-1">
              <span class="flex items-center gap-1.5">
                <BookOpen class="w-4 h-4 text-primary" />
                Classeur : <strong class="text-ink-muted">{{ assignment.binder_name }}</strong>
              </span>
              <span class="flex items-center gap-1.5">
                <Calendar class="w-4 h-4 text-accent" />
                Limite : <strong class="text-ink-muted">{{ formatDate(assignment.due_date) }}</strong>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Grille de stats -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-surface rounded-2xl border border-line p-5 shadow-elev-1 flex items-center gap-4">
          <div class="w-10 h-10 rounded-xl bg-info-soft flex items-center justify-center text-info flex-shrink-0">
            <Users class="w-5 h-5" />
          </div>
          <div>
            <span class="text-ink-subtle text-xs font-semibold uppercase tracking-wider">Total Élèves</span>
            <h4 class="text-2xl font-black mt-0.5 text-ink">{{ totalStudents }}</h4>
          </div>
        </div>

        <div class="bg-surface rounded-2xl border border-line p-5 shadow-elev-1 flex items-center gap-4">
          <div class="w-10 h-10 rounded-xl bg-success-soft flex items-center justify-center text-success flex-shrink-0">
            <CheckCircle2 class="w-5 h-5" />
          </div>
          <div>
            <span class="text-ink-subtle text-xs font-semibold uppercase tracking-wider">Devoirs Remplis</span>
            <h4 class="text-2xl font-black mt-0.5 text-ink">{{ completedStudentsCount }}</h4>
          </div>
        </div>

        <div class="bg-surface rounded-2xl border border-line p-5 shadow-elev-1 flex items-center gap-4">
          <div class="w-10 h-10 rounded-xl bg-accent-soft flex items-center justify-center text-accent flex-shrink-0">
            <BarChart3 class="w-5 h-5" />
          </div>
          <div>
            <span class="text-ink-subtle text-xs font-semibold uppercase tracking-wider">Taux de Complétion</span>
            <h4 class="text-2xl font-black mt-0.5 text-ink">{{ completionRate }}%</h4>
          </div>
        </div>

        <div class="bg-surface rounded-2xl border border-line p-5 shadow-elev-1 flex items-center gap-4">
          <div class="w-10 h-10 rounded-xl bg-primary-soft flex items-center justify-center text-primary flex-shrink-0">
            <Award class="w-5 h-5" />
          </div>
          <div>
            <span class="text-ink-subtle text-xs font-semibold uppercase tracking-wider">Moyenne de Classe</span>
            <h4 class="text-2xl font-black mt-0.5 text-ink">
              {{ averageScore !== null ? `${averageScore}%` : '—' }}
            </h4>
          </div>
        </div>
      </div>

      <!-- Table de progression -->
      <div class="bg-surface rounded-3xl border border-line shadow-elev-1 p-6 overflow-hidden">
        <h3 class="font-bold text-ink text-lg flex items-center gap-2 mb-6">
          <Users class="w-5 h-5 text-primary" />
          Progression Individuelle
        </h3>

        <div v-if="students.length === 0" class="text-center py-16 text-ink-subtle">
          <Users class="w-12 h-12 mx-auto mb-3 opacity-30" />
          Aucun élève n'a rejoint cette classe pour l'instant.
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b border-line text-xs font-bold uppercase tracking-wider text-ink-subtle">
                <th class="py-3 px-4">Élève</th>
                <th class="py-3 px-4">Statut</th>
                <th class="py-3 px-4">Cartes révisées</th>
                <th class="py-3 px-4">Score</th>
                <th class="py-3 px-4">Note (prof)</th>
                <th class="py-3 px-4">Rendu le</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-line-soft">
              <tr
                v-for="student in students"
                :key="student.user_id"
                class="hover:bg-surface-soft transition"
              >
                <!-- Nom -->
                <td class="py-4 px-4 font-semibold text-sm text-ink">
                  {{ student.username }}
                </td>

                <!-- Statut -->
                <td class="py-4 px-4">
                  <span
                    class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-xl text-xs font-semibold border"
                    :class="getStatusBadgeClass(getStudentStatus(student))"
                  >
                    <span class="w-1.5 h-1.5 rounded-full" :class="getStatusDotClass(getStudentStatus(student))"></span>
                    {{ getStatusLabel(getStudentStatus(student)) }}
                  </span>
                </td>

                <!-- Cartes révisées -->
                <td class="py-4 px-4 text-xs font-semibold text-ink-muted">
                  <span class="flex items-center gap-1.5">
                    <BookOpen class="w-3.5 h-3.5 text-primary" />
                    {{ student.cards_reviewed }} cartes
                  </span>
                </td>

                <!-- Score -->
                <td class="py-4 px-4">
                  <div class="flex items-center gap-2">
                    <span class="text-sm font-bold" :class="getScoreColorClass(student.score_pct)">
                      {{ student.score_pct !== null ? `${Math.round(student.score_pct)}%` : '—' }}
                    </span>
                    <div v-if="student.score_pct !== null" class="w-16 h-1.5 rounded-full bg-surface-soft overflow-hidden">
                      <div
                        class="h-full rounded-full transition-all"
                        :class="getScoreBarClass(student.score_pct)"
                        :style="{ width: student.score_pct + '%' }"
                      ></div>
                    </div>
                  </div>
                </td>

                <!-- Note prof -->
                <td class="py-4 px-4">
                  <div class="flex items-center gap-1.5">
                    <input
                      v-model.number="gradeFor(student.user_id).score"
                      type="number" min="0" max="100" placeholder="—"
                      class="w-16 px-2 py-1 rounded-lg border border-line bg-surface-soft text-ink text-xs focus:outline-none focus:ring-2 focus:ring-primary/40"
                    />
                    <input
                      v-model="gradeFor(student.user_id).feedback"
                      type="text" placeholder="Commentaire…"
                      class="w-28 px-2 py-1 rounded-lg border border-line bg-surface-soft text-ink text-xs focus:outline-none focus:ring-2 focus:ring-primary/40"
                    />
                    <button
                      @click="saveGrade(student)" :disabled="savingId === student.user_id"
                      class="p-1.5 rounded-lg text-ink-subtle hover:text-success hover:bg-success-soft transition flex-shrink-0"
                      :title="student.graded_at ? 'Note enregistrée' : 'Enregistrer la note'"
                    >
                      <Loader2 v-if="savingId === student.user_id" class="w-4 h-4 animate-spin" />
                      <Check v-else class="w-4 h-4" :class="student.graded_at ? 'text-success' : ''" />
                    </button>
                  </div>
                </td>

                <!-- Rendu le -->
                <td class="py-4 px-4 text-xs font-semibold text-ink-subtle">
                  <span v-if="student.completed_at" class="flex items-center gap-1.5">
                    <Clock class="w-3.5 h-3.5 text-ink-subtle" />
                    {{ formatSimpleDate(student.completed_at) }}
                  </span>
                  <span v-else class="text-ink-subtle">—</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
