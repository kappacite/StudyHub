<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import classService from '../../services/classService'
import type { AssignmentSummary, AssignmentTask, TaskType, ClassInfo, ClassQuestion } from '../../services/classService'
import api from '../../services/api'
import { taskLaunchRoute } from '../../services/assignmentTasks'
import { useClassNotifications } from '../../composables/useClassNotifications'
import {
  ClipboardList, Calendar, CheckCircle2, Clock, AlertTriangle,
  Loader2, BookOpen, ArrowRight, GraduationCap,
  Layers, FileQuestion, PenLine, Check, ListChecks, MessageCircleQuestion, Send
} from 'lucide-vue-next'

const router = useRouter()

const assignments = ref<AssignmentSummary[]>([])
const loading = ref(true)
const filterStatus = ref<'all' | 'todo' | 'in_progress' | 'done' | 'late'>('all')

const { scheduleDueReminders } = useClassNotifications()

// ─── Tableau de bord élève : ses propres stats (globales) ──────────────────────
interface MyStats { streak: number; total_time_seconds: number; total_reviewed: number; total_correct: number }
const myStats = ref<MyStats | null>(null)
const myStudyMinutes = computed(() => myStats.value ? Math.round(myStats.value.total_time_seconds / 60) : 0)
const mySuccessRate = computed(() =>
  myStats.value && myStats.value.total_reviewed > 0
    ? Math.round((myStats.value.total_correct / myStats.value.total_reviewed) * 100)
    : 0,
)
const myDoneCount = computed(() => assignments.value.filter(a => a.status === 'done').length)

// Classes où l'utilisateur est inscrit comme élève (member/follower) — celles
// qu'il anime sont dans l'Espace Professeur.
const enrolledClasses = computed(() =>
  myClasses.value.filter(c => c.my_role === 'member' || c.my_role === 'follower'),
)

function askInClass(classId: number) {
  qaClassId.value = classId
  loadQuestions()
}

// ─── Q&A (B4) ─────────────────────────────────────────────────────────────────
const myClasses = ref<ClassInfo[]>([])
const qaClassId = ref<number | null>(null)
const questions = ref<ClassQuestion[]>([])
const newQuestion = ref('')
const postingQuestion = ref(false)

async function loadQuestions() {
  if (qaClassId.value === null) { questions.value = []; return }
  questions.value = await classService.listQuestions(qaClassId.value).catch(() => [])
}

async function askQuestion() {
  if (qaClassId.value === null || !newQuestion.value.trim()) return
  postingQuestion.value = true
  try {
    await classService.postQuestion(qaClassId.value, newQuestion.value.trim())
    newQuestion.value = ''
    await loadQuestions()
  } catch {
    // silencieux
  } finally {
    postingQuestion.value = false
  }
}

onMounted(async () => {
  loading.value = true
  assignments.value = await classService.getMyAssignments().catch(() => [])
  myClasses.value = await classService.getMyClasses().catch(() => [])
  myStats.value = await api.get('/stats/overview').then(r => r.data).catch(() => null)
  qaClassId.value = myClasses.value[0]?.id ?? null
  await loadQuestions()
  loading.value = false
  // Programme des rappels locaux (mobile) pour les deadlines à venir.
  scheduleDueReminders(assignments.value)
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
    todo: 'bg-surface-soft text-ink-muted',
    in_progress: 'bg-info-soft text-info',
    done: 'bg-success-soft text-success',
    late: 'bg-danger-soft text-danger'
  }[s] ?? ''
}

function statusIcon(s: string) {
  return { todo: Clock, in_progress: ArrowRight, done: CheckCircle2, late: AlertTriangle }[s] ?? Clock
}

function cardBorderClass(s: string) {
  return {
    todo: 'border-line',
    in_progress: 'border-info/30',
    done: 'border-success/30',
    late: 'border-danger/30'
  }[s] ?? ''
}

function accentBarClass(s: string) {
  return {
    todo: 'bg-line',
    in_progress: 'bg-info',
    done: 'bg-success',
    late: 'bg-danger'
  }[s] ?? 'bg-line'
}

// ─── Tâches ──────────────────────────────────────────────────────────────────

const TASK_META: Record<TaskType, { label: string; cta: string; icon: unknown }> = {
  flashcards: { label: 'Flashcards', cta: 'Réviser', icon: Layers },
  quiz: { label: 'QCM', cta: 'Passer le QCM', icon: FileQuestion },
  exam: { label: 'Examen blanc', cta: "Lancer l'examen", icon: GraduationCap },
  blurting: { label: 'Blurting', cta: 'Feuille blanche', icon: PenLine },
  read: { label: 'Lecture', cta: 'Ouvrir', icon: BookOpen },
  revision: { label: 'Ensemble de révision', cta: 'Réviser', icon: ListChecks },
}

function launchTask(task: AssignmentTask) {
  router.push(taskLaunchRoute(task))
}

const validating = ref<number | null>(null)

async function validateTask(asgn: AssignmentSummary, task: AssignmentTask) {
  validating.value = task.id
  try {
    await classService.submitTask(asgn.group_id, asgn.id, task.id)
    assignments.value = await classService.getMyAssignments()
  } catch {
    // silencieux : l'élève peut réessayer
  } finally {
    validating.value = null
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Sous-en-tête -->
    <div class="flex items-center gap-3">
      <span class="flex items-center justify-center w-10 h-10 rounded-xl bg-primary text-white shadow-elev-primary">
        <GraduationCap class="w-5 h-5" />
      </span>
      <div>
        <h2 class="text-lg font-bold text-ink">Mes Classes</h2>
        <p class="text-xs text-ink-muted">Vos classes, leurs cours partagés et les devoirs assignés par vos professeurs.</p>
      </div>
    </div>

    <!-- Tableau de bord élève : mes propres statistiques -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
      <div class="bg-surface border border-line rounded-2xl p-4">
        <p class="text-[10px] font-bold uppercase tracking-wider text-ink-subtle">Série</p>
        <p class="text-2xl font-bold text-ink mt-1">{{ myStats?.streak ?? 0 }} j</p>
      </div>
      <div class="bg-surface border border-line rounded-2xl p-4">
        <p class="text-[10px] font-bold uppercase tracking-wider text-ink-subtle">Temps de révision</p>
        <p class="text-2xl font-bold text-ink mt-1">{{ myStudyMinutes }} min</p>
      </div>
      <div class="bg-surface border border-line rounded-2xl p-4">
        <p class="text-[10px] font-bold uppercase tracking-wider text-ink-subtle">Réussite révisions</p>
        <p class="text-2xl font-bold text-ink mt-1">{{ mySuccessRate }}%</p>
      </div>
      <div class="bg-surface border border-line rounded-2xl p-4">
        <p class="text-[10px] font-bold uppercase tracking-wider text-ink-subtle">Devoirs terminés</p>
        <p class="text-2xl font-bold text-ink mt-1">{{ myDoneCount }}</p>
      </div>
    </div>

    <!-- Mes classes (inscrit comme élève) -->
    <div v-if="enrolledClasses.length">
      <h2 class="text-base font-bold text-ink flex items-center gap-2 mb-3">
        <GraduationCap class="w-4 h-4 text-primary" />
        Mes classes ({{ enrolledClasses.length }})
      </h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        <div
          v-for="c in enrolledClasses"
          :key="c.id"
          class="bg-surface border border-line rounded-2xl p-4 flex items-center justify-between gap-3"
        >
          <div class="min-w-0">
            <p class="font-bold text-sm text-ink truncate">{{ c.name }}</p>
            <p class="text-[11px] text-ink-subtle mt-0.5">{{ c.members_count }} membre(s)</p>
            <p class="text-[10px] text-ink-subtle mt-1">Cours & révisions partagés : voir Classeurs / Révisions.</p>
          </div>
          <button
            @click="askInClass(c.id)"
            class="shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold text-primary border border-primary/30 hover:bg-primary-soft transition-colors"
            title="Poser une question dans cette classe"
          >
            <MessageCircleQuestion class="w-3.5 h-3.5" />
            Question
          </button>
        </div>
      </div>
    </div>

    <!-- Devoirs -->
    <h2 class="text-base font-bold text-ink flex items-center gap-2">
      <ClipboardList class="w-4 h-4 text-primary" />
      Mes devoirs
    </h2>

    <!-- Filtres -->
    <div class="flex flex-wrap gap-2">
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
          'px-4 py-2 rounded-full text-sm font-medium transition-colors',
          filterStatus === tab.id
            ? 'bg-primary text-white shadow-elev-primary'
            : 'bg-surface text-ink-muted border border-line hover:text-ink'
        ]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <Loader2 class="w-8 h-8 text-primary animate-spin" />
    </div>

    <!-- Empty -->
    <div v-else-if="filtered.length === 0" class="text-center py-20">
      <ClipboardList class="w-12 h-12 text-ink-subtle mx-auto mb-3" />
      <p class="text-ink-muted">
        {{ filterStatus === 'all' ? 'Aucun devoir assigné pour l\'instant.' : 'Aucun devoir dans cette catégorie.' }}
      </p>
    </div>

    <!-- Liste des devoirs -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <article
        v-for="asgn in filtered"
        :key="asgn.id"
        class="bg-surface rounded-2xl border shadow-elev-1 hover:shadow-elev-2 transition-all duration-200"
        :class="cardBorderClass(asgn.status)"
      >
        <!-- Barre d'accent -->
        <div :class="['h-1.5 rounded-t-2xl', accentBarClass(asgn.status)]"></div>

        <div class="p-5">
          <!-- Nom de classe -->
          <div class="flex items-center gap-1.5 text-xs text-ink-subtle mb-2">
            <GraduationCap class="w-3 h-3" />
            {{ asgn.group_name }}
          </div>

          <!-- Titre & statut -->
          <div class="flex items-start justify-between gap-2 mb-3">
            <h3 class="font-bold text-ink text-base leading-snug">{{ asgn.title }}</h3>
            <span :class="['flex items-center gap-1 px-2 py-0.5 rounded-lg text-xs font-medium flex-shrink-0', statusBadgeClass(asgn.status)]">
              <component :is="statusIcon(asgn.status)" class="w-3 h-3" />
              {{ statusLabel(asgn.status) }}
            </span>
          </div>

          <!-- Échéance -->
          <div :class="[
            'flex items-center justify-between text-xs rounded-xl px-3 py-2 mb-4',
            asgn.status === 'late' ? 'bg-danger-soft text-danger' : 'bg-surface-soft text-ink-muted'
          ]">
            <span class="flex items-center gap-1.5">
              <Calendar class="w-3.5 h-3.5" />
              {{ formatDate(asgn.due_date) }}
            </span>
            <span v-if="asgn.due_date" class="font-medium">{{ daysUntil(asgn.due_date) }}</span>
          </div>

          <!-- Tâches -->
          <div class="space-y-2">
            <div
              v-for="task in asgn.tasks"
              :key="task.id"
              class="flex items-center gap-2 rounded-xl border border-line bg-surface-soft px-3 py-2"
            >
              <component :is="TASK_META[task.task_type].icon" class="w-4 h-4 flex-shrink-0 text-primary" />
              <div class="min-w-0 flex-1">
                <p class="text-xs font-semibold text-ink">{{ TASK_META[task.task_type].label }}</p>
                <p class="text-[11px] text-ink-subtle truncate">{{ task.ref_label }}</p>
              </div>
              <CheckCircle2 v-if="task.my_status === 'done'" class="w-5 h-5 text-success flex-shrink-0" />
              <template v-else>
                <button
                  @click="launchTask(task)"
                  class="px-2.5 py-1 rounded-lg bg-primary hover:bg-primary-strong text-white text-[11px] font-medium transition flex-shrink-0"
                >
                  {{ TASK_META[task.task_type].cta }}
                </button>
                <button
                  @click="validateTask(asgn, task)"
                  :disabled="validating === task.id"
                  :title="task.task_type === 'read' ? 'Marquer comme lu' : 'Vérifier la progression'"
                  class="p-1.5 rounded-lg text-ink-subtle hover:text-success hover:bg-success-soft transition flex-shrink-0"
                >
                  <Loader2 v-if="validating === task.id" class="w-4 h-4 animate-spin" />
                  <Check v-else class="w-4 h-4" />
                </button>
              </template>
            </div>
          </div>
        </div>
      </article>
    </div>

    <!-- Q&A : poser une question au professeur (B4) -->
    <section v-if="myClasses.length" class="bg-surface border border-line rounded-2xl p-5">
      <h2 class="text-base font-bold text-ink flex items-center gap-2 mb-3">
        <MessageCircleQuestion class="w-5 h-5 text-primary" /> Poser une question
      </h2>
      <div class="flex flex-col sm:flex-row gap-2 mb-3">
        <select v-model="qaClassId" @change="loadQuestions"
          class="sm:w-56 px-3 py-2 rounded-xl border border-line bg-surface-soft text-ink text-sm">
          <option v-for="c in myClasses" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <div class="flex-1 flex gap-2">
          <input v-model="newQuestion" type="text" placeholder="Votre question au professeur…" @keyup.enter="askQuestion"
            class="flex-1 px-3 py-2 rounded-xl border border-line bg-surface-soft text-ink placeholder:text-ink-subtle text-sm" />
          <button @click="askQuestion" :disabled="postingQuestion || !newQuestion.trim()"
            class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-primary hover:bg-primary-strong disabled:opacity-50 text-white text-sm font-semibold transition">
            <Loader2 v-if="postingQuestion" class="w-4 h-4 animate-spin" /><Send v-else class="w-4 h-4" /> Envoyer
          </button>
        </div>
      </div>

      <div v-if="questions.length" class="space-y-2">
        <div v-for="q in questions" :key="q.id" class="border border-line rounded-xl p-3">
          <p class="text-sm text-ink">{{ q.body }}</p>
          <div v-if="q.answer" class="mt-2 pl-3 border-l-2 border-primary">
            <p class="text-[10px] font-bold text-primary uppercase tracking-wider">Réponse{{ q.answered_by_username ? ` · ${q.answered_by_username}` : '' }}</p>
            <p class="text-sm text-ink-muted">{{ q.answer }}</p>
          </div>
          <p v-else class="text-[11px] text-warning font-semibold mt-1">En attente de réponse…</p>
        </div>
      </div>
      <p v-else class="text-xs text-ink-subtle text-center py-4">Aucune question pour le moment.</p>
    </section>
  </div>
</template>
