<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useBindersStore } from '../../stores/binders'
import { useNotesStore } from '../../stores/notes'
import { useDecksStore } from '../../stores/decks'
import { useRevisionStore } from '../../stores/revision'
import classService from '../../services/classService'
import type { Assignment, StudentMaterialsProgress, ClassOverview, ClassInsight, Leaderboard, RosterEntry, ClassQuestion } from '../../services/classService'
import groupService from '../../services/groupService'
import type { GroupBinder } from '../../services/groupService'
import AssignmentBuilder from '../../components/classes/AssignmentBuilder.vue'
import {
  GraduationCap, Plus, Users, ClipboardList,
  Loader2, AlertCircle, Calendar, BookOpen, Clock,
  BarChart3, Trash2, Eye, RefreshCw, UserMinus, Send
} from 'lucide-vue-next'

const router = useRouter()
const bindersStore = useBindersStore()
const notesStore = useNotesStore()
const decksStore = useDecksStore()
const revisionStore = useRevisionStore()

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
const newClassIsPublic = ref(false)

// Notes disponibles comme cibles de tâches (QCM, blurting, lecture)
const noteOptions = computed(() => notesStore.notes.map(n => ({ id: n.id, title: n.title })))
const binderOptions = computed(() => bindersStore.binders.map(b => ({ id: b.id, name: b.name })))
const setOptions = computed(() => revisionStore.sets.map(s => ({ id: s.id, name: `${s.name} (${s.type.toUpperCase()})` })))

// Associate binder state
const showAssociateModal = ref(false)
const associateClassId = ref<number | null>(null)
const associateBinderId = ref<string | null>(null)

// Extra class details state
const classDetails = ref<Record<number, {
  binders: GroupBinder[];
  progress: StudentMaterialsProgress[];
  overview: ClassOverview | null;
  insights: ClassInsight | null;
  leaderboard: Leaderboard | null;
  analyzing: boolean;
  loading: boolean;
  roster: RosterEntry[];
  questions: ClassQuestion[];
  activeTab: 'assignments' | 'resources' | 'progress' | 'analytics' | 'roster' | 'questions';
}>>({})

// Q&A — brouillons de réponse par question.
const answerDrafts = ref<Record<number, string>>({})
const answering = ref<number | null>(null)

// Annonce
const showAnnounceModal = ref(false)
const announceClassId = ref<number | null>(null)
const announceTitle = ref('')
const announceBody = ref('')

function openAnnounce(classId: number) {
  announceClassId.value = classId
  announceTitle.value = ''
  announceBody.value = ''
  showAnnounceModal.value = true
}

async function postAnnounce() {
  if (!announceClassId.value || !announceTitle.value.trim()) return
  creating.value = true
  try {
    await classService.postAnnouncement(announceClassId.value, {
      title: announceTitle.value.trim(),
      body: announceBody.value.trim() || undefined,
    })
    showAnnounceModal.value = false
  } catch (e) {
    console.error(e)
  } finally {
    creating.value = false
  }
}

const availableBindersToAssociate = computed(() => {
  if (!associateClassId.value) return []
  const sharedIds = classDetails.value[associateClassId.value]?.binders.map(b => b.binder_id) || []
  return bindersStore.binders.filter(b => !sharedIds.includes(b.id))
})

async function selectClassTab(classId: number, tab: 'assignments' | 'resources' | 'progress' | 'analytics' | 'roster' | 'questions') {
  if (!classDetails.value[classId]) {
    classDetails.value[classId] = {
      binders: [],
      progress: [],
      overview: null,
      insights: null,
      leaderboard: null,
      roster: [],
      questions: [],
      analyzing: false,
      loading: false,
      activeTab: 'assignments'
    }
  }

  classDetails.value[classId].activeTab = tab

  if (tab === 'assignments') return

  classDetails.value[classId].loading = true
  try {
    if (tab === 'resources') {
      const detail = await groupService.getGroupDetail(classId)
      classDetails.value[classId].binders = detail.binders
    } else if (tab === 'progress') {
      const [detail, prog] = await Promise.all([
        groupService.getGroupDetail(classId),
        classService.getClassMaterialsProgress(classId)
      ])
      classDetails.value[classId].binders = detail.binders
      classDetails.value[classId].progress = prog
    } else if (tab === 'analytics') {
      const [overview, insights, leaderboard] = await Promise.all([
        classService.getClassAnalytics(classId),
        classService.getClassInsights(classId),
        classService.getLeaderboard(classId)
      ])
      classDetails.value[classId].overview = overview
      classDetails.value[classId].insights = insights
      classDetails.value[classId].leaderboard = leaderboard
    } else if (tab === 'roster') {
      classDetails.value[classId].roster = await classService.getRoster(classId)
    } else if (tab === 'questions') {
      classDetails.value[classId].questions = await classService.listQuestions(classId)
    }
  } catch (e) {
    console.error(e)
  } finally {
    classDetails.value[classId].loading = false
  }
}

async function answerQuestion(classId: number, questionId: number) {
  const body = (answerDrafts.value[questionId] || '').trim()
  if (!body) return
  answering.value = questionId
  try {
    await classService.answerQuestion(classId, questionId, body)
    delete answerDrafts.value[questionId]
    classDetails.value[classId].questions = await classService.listQuestions(classId)
  } catch (e) {
    console.error(e)
  } finally {
    answering.value = null
  }
}

async function removeMember(classId: number, userId: number) {
  if (!confirm("Retirer cet élève de la classe ?")) return
  try {
    await classService.removeMember(classId, userId)
    const d = classDetails.value[classId]
    if (d) d.roster = d.roster.filter(r => r.user_id !== userId)
    // Mettre à jour le compteur d'élèves de la classe.
    const c = classes.value.find(c => c.id === classId)
    if (c && c.members_count > 0) c.members_count -= 1
  } catch (e) {
    alert("Impossible de retirer cet élève.")
  }
}

async function regenerateInvite(classId: number) {
  if (!confirm("Régénérer le code d'invitation ? L'ancien code ne fonctionnera plus.")) return
  try {
    const { invite_code } = await classService.regenerateInvite(classId)
    const c = classes.value.find(c => c.id === classId)
    if (c) c.invite_code = invite_code
  } catch (e) {
    alert("Impossible de régénérer le code.")
  }
}

const distributingId = ref<string | null>(null)

async function distributeBinder(classId: number, binderId: string) {
  if (!confirm("Distribuer une copie de ce classeur à chaque élève ?")) return
  distributingId.value = binderId
  try {
    const res = await classService.distributeBinder(classId, binderId)
    alert(`Copie distribuée à ${res.distributed} élève(s).`)
  } catch (e) {
    alert("Impossible de distribuer ce classeur.")
  } finally {
    distributingId.value = null
  }
}

async function analyzeGaps(classId: number) {
  const d = classDetails.value[classId]
  if (!d) return
  d.analyzing = true
  try {
    await classService.refreshClassInsights(classId)
    // En mode async, le résultat peut arriver après un court délai ; on relit le cache.
    d.insights = await classService.getClassInsights(classId)
  } catch (e) {
    console.error(e)
  } finally {
    d.analyzing = false
  }
}

async function associateBinder() {
  if (!associateClassId.value || !associateBinderId.value) return
  creating.value = true
  try {
    await groupService.shareBinder(associateClassId.value, associateBinderId.value, 'read')
    await selectClassTab(associateClassId.value, 'resources')
    showAssociateModal.value = false
    associateBinderId.value = null
  } catch (e) {
    alert("Impossible d'associer ce classeur.")
  } finally {
    creating.value = false
  }
}

async function dissociateBinder(classId: number, binderId: string) {
  if (!confirm("Retirer ce classeur de la classe ? Les élèves n'y auront plus accès.")) return
  try {
    await groupService.unshareBinder(classId, binderId)
    if (classDetails.value[classId]) {
      await selectClassTab(classId, classDetails.value[classId].activeTab)
    }
  } catch (e) {
    alert("Impossible de retirer ce classeur.")
  }
}

function openAssociateBinder(classId: number) {
  associateClassId.value = classId
  showAssociateModal.value = true
  associateBinderId.value = null
}

function getBinderStats(binderId: string) {
  const directNotes = notesStore.notes.filter(n => n.binder_id === binderId).length
  const directDecks = decksStore.decks.filter(d => d.binder_id === binderId).length
  return { notes: directNotes, decks: directDecks }
}

async function loadClasses() {
  const [myClasses, _, _2, _3] = await Promise.all([
    classService.getMyClasses(),
    bindersStore.fetchBinders(),
    notesStore.fetchNotes(),
    decksStore.fetchDecks(),
    revisionStore.fetchSets()
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
    await classService.createClass(
      newClassName.value.trim(),
      newClassDesc.value.trim() || undefined,
      newClassIsPublic.value
    )
    await loadClasses()
    showCreateClassModal.value = false
    newClassName.value = ''
    newClassDesc.value = ''
    newClassIsPublic.value = false
  } catch (e: unknown) {
    const err = e as { response?: { data?: { error?: { message?: string } } } }
    error.value = err?.response?.data?.error?.message || 'Erreur lors de la création.'
  } finally {
    creating.value = false
  }
}

async function onAssignmentCreated() {
  if (!selectedClassId.value) return
  const updated = [...classes.value]
  const idx = updated.findIndex(c => c.id === selectedClassId.value)
  if (idx !== -1) {
    updated[idx].assignments = await classService.listAssignments(selectedClassId.value)
  }
  classes.value = updated
  showCreateAssignmentModal.value = false
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
                  <button @click="regenerateInvite(cls.id)" title="Régénérer le code d'invitation"
                    class="text-slate-400 hover:text-amber-500 transition">
                    <RefreshCw class="w-3 h-3" />
                  </button>
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
                @click="openAnnounce(cls.id)"
                class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 text-xs font-medium transition"
              >
                <ClipboardList class="w-3.5 h-3.5" />
                Annoncer
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

          <!-- Tabs inside Class Card -->
          <div class="flex border-b border-slate-100 dark:border-slate-700/60 mb-4 px-1 -mx-5">
            <button
              v-for="tab in [
                { id: 'assignments', label: 'Devoirs' },
                { id: 'resources', label: 'Cours & Classeurs' },
                { id: 'progress', label: 'Suivi Révisions' },
                { id: 'analytics', label: 'Tableau de bord' },
                { id: 'roster', label: 'Élèves' },
                { id: 'questions', label: 'Questions' }
              ]"
              :key="tab.id"
              @click="selectClassTab(cls.id, tab.id)"
              :class="[
                'px-5 py-2.5 text-xs font-bold border-b-2 -mb-px transition-all',
                (classDetails[cls.id]?.activeTab || 'assignments') === tab.id
                  ? 'border-amber-500 text-amber-600 dark:border-amber-400 dark:text-amber-400'
                  : 'border-transparent text-slate-400 hover:text-slate-600 dark:hover:text-slate-350'
              ]"
            >
              {{ tab.label }}
            </button>
          </div>

          <!-- TAB 1: Assignments -->
          <div v-if="(classDetails[cls.id]?.activeTab || 'assignments') === 'assignments'" class="space-y-2">
            <div v-if="cls.assignments.length === 0" class="text-center py-8 text-slate-400 dark:text-slate-655 text-sm">
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
                    <p class="text-xs text-slate-400 mt-0.5">
                      <span v-if="asgn.tasks && asgn.tasks.length">{{ asgn.tasks.length }} activité{{ asgn.tasks.length > 1 ? 's' : '' }}</span>
                      <span v-else>{{ asgn.binder_name }}</span>
                    </p>
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

          <!-- TAB 2: Resources -->
          <div v-else-if="classDetails[cls.id]?.activeTab === 'resources'">
            <div v-if="classDetails[cls.id]?.loading" class="flex items-center justify-center py-8">
              <Loader2 class="w-6 h-6 text-amber-500 animate-spin" />
            </div>
            <div v-else>
              <div class="flex items-center justify-between gap-4 mb-4">
                <span class="text-xs text-slate-400">Classeurs, cours & révisions associés à la classe</span>
                <button
                  @click="openAssociateBinder(cls.id)"
                  class="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-amber-50 border border-amber-200 dark:border-amber-900/50 hover:bg-amber-100 text-amber-600 dark:text-amber-400 text-xs font-semibold transition"
                >
                  <Plus class="w-3.5 h-3.5" />
                  Associer un classeur
                </button>
              </div>

              <div v-if="!classDetails[cls.id]?.binders || classDetails[cls.id].binders.length === 0" class="text-center py-8 text-slate-400 dark:text-slate-655 text-sm border-2 border-dashed border-slate-100 dark:border-slate-800 rounded-xl">
                <BookOpen class="w-8 h-8 mx-auto mb-2 opacity-50" />
                Aucun cours ou classeur associé.
              </div>
              <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div
                  v-for="b in classDetails[cls.id].binders"
                  :key="b.binder_id"
                  class="flex items-center justify-between gap-3 bg-slate-50 dark:bg-slate-900/40 rounded-xl px-4 py-3 cursor-pointer hover:border-amber-500/20 border border-transparent transition-all"
                  @click="router.push(`/binders/${b.binder_id}`)"
                >
                  <div class="flex items-center gap-3 min-w-0">
                    <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-amber-50 dark:bg-amber-950/20 text-amber-500 flex-shrink-0">
                      <BookOpen class="w-4 h-4" />
                    </div>
                    <div class="min-w-0">
                      <p class="font-bold text-slate-800 dark:text-white text-xs truncate hover:text-amber-600 transition-colors">{{ b.binder_name }}</p>
                      <p class="text-[10px] text-slate-455 mt-0.5 flex items-center gap-1.5">
                        <span>{{ getBinderStats(b.binder_id).notes }} cours</span>
                        <span class="w-1 h-1 rounded-full bg-slate-350 dark:bg-slate-700"></span>
                        <span>{{ getBinderStats(b.binder_id).decks }} révisions</span>
                      </p>
                    </div>
                  </div>
                  <div class="flex items-center gap-1 flex-shrink-0">
                    <button
                      @click.stop="distributeBinder(cls.id, b.binder_id)"
                      :disabled="distributingId === b.binder_id"
                      class="p-1.5 rounded-lg text-slate-400 hover:text-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition"
                      title="Distribuer une copie à chaque élève"
                    >
                      <Loader2 v-if="distributingId === b.binder_id" class="w-3.5 h-3.5 animate-spin" />
                      <Send v-else class="w-3.5 h-3.5" />
                    </button>
                    <button
                      @click.stop="dissociateBinder(cls.id, b.binder_id)"
                      class="p-1.5 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition"
                      title="Dissocier"
                    >
                      <Trash2 class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- TAB 3: Student Revisions & Scores Progress -->
          <div v-else-if="classDetails[cls.id]?.activeTab === 'progress'">
            <div v-if="classDetails[cls.id]?.loading" class="flex items-center justify-center py-8">
              <Loader2 class="w-6 h-6 text-amber-500 animate-spin" />
            </div>
            <div v-else>
              <div v-if="!classDetails[cls.id]?.binders || classDetails[cls.id].binders.length === 0" class="text-center py-8 text-slate-400 dark:text-slate-655 text-sm">
                Aucun classeur ou cours n'est associé à cette classe. Associez-en un pour suivre le travail des élèves.
              </div>
              <div v-else-if="!classDetails[cls.id]?.progress || classDetails[cls.id].progress.length === 0" class="text-center py-8 text-slate-400 dark:text-slate-655 text-sm">
                Aucun élève dans cette classe.
              </div>
              <div v-else class="space-y-4">
                <div v-for="student in classDetails[cls.id].progress" :key="student.user_id" class="border border-slate-105 dark:border-slate-750/60 rounded-xl p-4 bg-slate-50/50 dark:bg-slate-900/10">
                  <div class="flex items-center justify-between border-b border-slate-105 dark:border-slate-700/60 pb-2 mb-3">
                    <span class="font-bold text-slate-800 dark:text-white text-sm">{{ student.username }}</span>
                    <span class="text-[10px] text-slate-455">Révisions par classeur</span>
                  </div>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div v-for="bp in student.binders_progress" :key="bp.binder_id" class="bg-white dark:bg-slate-800/40 border border-slate-105 dark:border-slate-700/40 rounded-lg p-3 flex flex-col justify-between">
                      <div>
                        <div class="flex items-center justify-between gap-2 mb-1">
                          <span class="font-bold text-xs text-slate-750 dark:text-slate-200 truncate">{{ bp.binder_name }}</span>
                          <span :class="[
                            'text-[10px] font-extrabold px-1.5 py-0.5 rounded-full uppercase tracking-wider',
                            bp.cards_reviewed === 0 ? 'bg-slate-100 text-slate-500' :
                            bp.cards_reviewed >= bp.total_cards ? 'bg-green-50 text-green-650 dark:bg-green-950/20 dark:text-green-400' :
                            'bg-blue-50 text-blue-650 dark:bg-blue-950/20 dark:text-blue-400'
                          ]">
                            {{ bp.cards_reviewed === 0 ? 'Non commencé' : bp.cards_reviewed >= bp.total_cards ? 'Terminé' : 'En cours' }}
                          </span>
                        </div>
                        <div class="flex items-center justify-between text-[11px] text-slate-455 dark:text-slate-400 mt-1">
                          <span>{{ bp.cards_reviewed }} / {{ bp.total_cards }} cartes</span>
                          <span v-if="bp.cards_reviewed > 0" :class="[
                            'font-bold',
                            bp.score_pct >= 80 ? 'text-green-600' : bp.score_pct >= 50 ? 'text-amber-600' : 'text-red-500'
                          ]">{{ Math.round(bp.score_pct) }}% réussite</span>
                        </div>
                      </div>
                      
                      <!-- Progress Bar -->
                      <div class="mt-2 h-1.5 rounded-full bg-slate-100 dark:bg-slate-700 overflow-hidden">
                        <div
                          class="h-full rounded-full transition-all"
                          :class="[
                            bp.cards_reviewed >= bp.total_cards ? 'bg-green-500' : 'bg-amber-500'
                          ]"
                          :style="{ width: (bp.total_cards > 0 ? (bp.cards_reviewed / bp.total_cards * 100) : 0) + '%' }"
                        ></div>
                      </div>
                      
                      <div v-if="bp.last_reviewed_at" class="text-[9px] text-slate-400 mt-2 flex items-center gap-1">
                        <Clock class="w-3 h-3 text-slate-400" />
                        Dernière révision : {{ formatDate(bp.last_reviewed_at) }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <!-- TAB 4: Analytics dashboard -->
          <div v-else-if="classDetails[cls.id]?.activeTab === 'analytics'">
            <div v-if="classDetails[cls.id]?.loading" class="flex items-center justify-center py-8">
              <Loader2 class="w-6 h-6 text-amber-500 animate-spin" />
            </div>
            <div v-else-if="classDetails[cls.id]?.overview">
              <!-- KPI cards -->
              <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
                <div class="rounded-xl bg-slate-50 dark:bg-slate-900/40 p-3">
                  <p class="text-[10px] uppercase tracking-wider text-slate-400 font-bold">Élèves</p>
                  <p class="text-2xl font-bold text-slate-800 dark:text-white">{{ classDetails[cls.id].overview!.students_count }}</p>
                </div>
                <div class="rounded-xl bg-slate-50 dark:bg-slate-900/40 p-3">
                  <p class="text-[10px] uppercase tracking-wider text-slate-400 font-bold">Actifs (7j)</p>
                  <p class="text-2xl font-bold text-slate-800 dark:text-white">{{ classDetails[cls.id].overview!.active_students_7d }}</p>
                </div>
                <div class="rounded-xl bg-slate-50 dark:bg-slate-900/40 p-3">
                  <p class="text-[10px] uppercase tracking-wider text-slate-400 font-bold">Complétion</p>
                  <p class="text-2xl font-bold text-amber-600 dark:text-amber-400">{{ Math.round(classDetails[cls.id].overview!.completion_rate) }}%</p>
                </div>
                <div class="rounded-xl bg-slate-50 dark:bg-slate-900/40 p-3">
                  <p class="text-[10px] uppercase tracking-wider text-slate-400 font-bold">Score moyen</p>
                  <p class="text-2xl font-bold text-slate-800 dark:text-white">
                    {{ classDetails[cls.id].overview!.avg_score !== null ? Math.round(classDetails[cls.id].overview!.avg_score!) + '%' : '—' }}
                  </p>
                </div>
                <div class="rounded-xl bg-slate-50 dark:bg-slate-900/40 p-3">
                  <p class="text-[10px] uppercase tracking-wider text-slate-400 font-bold">Révision moy.</p>
                  <p class="text-2xl font-bold text-slate-800 dark:text-white">{{ Math.round(classDetails[cls.id].overview!.avg_study_minutes) }} min</p>
                </div>
                <div class="rounded-xl bg-slate-50 dark:bg-slate-900/40 p-3">
                  <p class="text-[10px] uppercase tracking-wider text-slate-400 font-bold">Réussite révisions</p>
                  <p class="text-2xl font-bold text-slate-800 dark:text-white">
                    {{ classDetails[cls.id].overview!.study_success_rate !== null ? Math.round(classDetails[cls.id].overview!.study_success_rate!) + '%' : '—' }}
                  </p>
                </div>
              </div>

              <!-- Avancement par élève (B5) -->
              <div v-if="classDetails[cls.id].overview!.students.length" class="mb-6">
                <p class="text-xs font-bold text-slate-500 dark:text-slate-400 mb-2">Avancement par élève</p>
                <div class="overflow-x-auto">
                  <table class="w-full text-xs">
                    <thead>
                      <tr class="text-left text-slate-400 border-b border-slate-100 dark:border-slate-700/60">
                        <th class="py-1.5 pr-2 font-semibold">Élève</th>
                        <th class="py-1.5 px-2 font-semibold text-right">Devoirs faits</th>
                        <th class="py-1.5 px-2 font-semibold text-right">Score moy.</th>
                        <th class="py-1.5 px-2 font-semibold text-right">Révision</th>
                        <th class="py-1.5 pl-2 font-semibold text-right">Réussite</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="s in classDetails[cls.id].overview!.students" :key="s.user_id"
                        class="border-b border-slate-50 dark:border-slate-800/40">
                        <td class="py-1.5 pr-2 font-semibold text-slate-700 dark:text-slate-200 truncate max-w-[160px]">{{ s.username }}</td>
                        <td class="py-1.5 px-2 text-right text-slate-600 dark:text-slate-300">{{ s.completed_assignments }}</td>
                        <td class="py-1.5 px-2 text-right text-slate-600 dark:text-slate-300">{{ s.avg_score !== null ? Math.round(s.avg_score) + '%' : '—' }}</td>
                        <td class="py-1.5 px-2 text-right text-slate-600 dark:text-slate-300">{{ s.study_minutes }} min</td>
                        <td class="py-1.5 pl-2 text-right text-slate-600 dark:text-slate-300">{{ s.success_rate !== null ? Math.round(s.success_rate) + '%' : '—' }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Per-assignment completion -->
              <div v-if="classDetails[cls.id].overview!.assignments.length" class="space-y-2 mb-6">
                <p class="text-xs font-bold text-slate-500 dark:text-slate-400 mb-1">Complétion par devoir</p>
                <div v-for="a in classDetails[cls.id].overview!.assignments" :key="a.id" class="flex items-center gap-3">
                  <span class="text-xs text-slate-600 dark:text-slate-300 w-40 truncate">{{ a.title }}</span>
                  <div class="flex-1 h-2 rounded-full bg-slate-100 dark:bg-slate-700 overflow-hidden">
                    <div class="h-full rounded-full bg-amber-500" :style="{ width: a.completion_rate + '%' }"></div>
                  </div>
                  <span class="text-[11px] text-slate-400 w-24 text-right">{{ a.completed_count }}/{{ a.submissions_count }} ({{ Math.round(a.completion_rate) }}%)</span>
                </div>
              </div>

              <!-- AI gaps -->
              <div class="rounded-xl border border-amber-100 dark:border-amber-900/40 bg-amber-50/50 dark:bg-amber-950/10 p-4">
                <div class="flex items-center justify-between mb-2">
                  <p class="text-sm font-bold text-slate-800 dark:text-slate-100 flex items-center gap-1.5">
                    <BarChart3 class="w-4 h-4 text-amber-500" /> Lacunes de la classe
                  </p>
                  <button @click="analyzeGaps(cls.id)" :disabled="classDetails[cls.id].analyzing"
                    class="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-white text-[11px] font-semibold transition">
                    <Loader2 v-if="classDetails[cls.id].analyzing" class="w-3.5 h-3.5 animate-spin" />
                    <BarChart3 v-else class="w-3.5 h-3.5" />
                    Analyser
                  </button>
                </div>
                <p v-if="classDetails[cls.id].insights?.summary" class="text-xs text-slate-600 dark:text-slate-300 mb-3">
                  {{ classDetails[cls.id].insights!.summary }}
                  <span v-if="classDetails[cls.id].insights!.ai" class="ml-1 text-[9px] uppercase tracking-wider text-amber-500 font-bold">IA</span>
                </p>
                <p v-else class="text-xs text-slate-400 mb-3">Aucune analyse pour l'instant. Lancez « Analyser » pour identifier les notions les plus ratées.</p>
                <div v-if="classDetails[cls.id].insights?.weak_topics?.length" class="space-y-1.5">
                  <div v-for="t in classDetails[cls.id].insights!.weak_topics" :key="t.note_id" class="flex items-center justify-between text-xs">
                    <span class="text-slate-700 dark:text-slate-200 truncate">{{ t.note_title }}</span>
                    <span class="font-bold" :class="t.error_rate >= 50 ? 'text-red-500' : 'text-amber-600'">{{ Math.round(t.error_rate) }}% d'erreurs</span>
                  </div>
                </div>
              </div>

              <!-- Leaderboard -->
              <div v-if="classDetails[cls.id].leaderboard?.enabled && classDetails[cls.id].leaderboard!.entries.length" class="mt-5 rounded-xl border border-slate-100 dark:border-slate-700/60 p-4">
                <p class="text-sm font-bold text-slate-800 dark:text-slate-100 mb-3">Classement</p>
                <div class="space-y-1.5">
                  <div v-for="(e, i) in classDetails[cls.id].leaderboard!.entries.slice(0, 10)" :key="e.user_id"
                    class="flex items-center gap-3 text-xs">
                    <span class="w-5 text-center font-bold" :class="i === 0 ? 'text-amber-500' : 'text-slate-400'">{{ i + 1 }}</span>
                    <span class="flex-1 truncate text-slate-700 dark:text-slate-200">{{ e.username }}</span>
                    <span v-for="b in e.badges.slice(0, 2)" :key="b" class="hidden sm:inline px-1.5 py-0.5 rounded-full bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 text-[9px] font-bold">{{ b }}</span>
                    <span v-if="e.streak > 0" class="text-orange-500 font-semibold">🔥{{ e.streak }}</span>
                    <span class="font-bold text-slate-800 dark:text-white w-12 text-right">{{ e.points }} pts</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-8 text-slate-400 text-sm">Aucune donnée analytique disponible.</div>
          </div>

          <!-- TAB 5: Roster -->
          <div v-else-if="classDetails[cls.id]?.activeTab === 'roster'">
            <div v-if="classDetails[cls.id]?.loading" class="flex items-center justify-center py-8">
              <Loader2 class="w-6 h-6 text-amber-500 animate-spin" />
            </div>
            <div v-else-if="!classDetails[cls.id]?.roster?.length" class="text-center py-8 text-slate-400 text-sm">
              Aucun membre.
            </div>
            <div v-else class="space-y-1.5">
              <div v-for="m in classDetails[cls.id].roster" :key="m.user_id"
                class="flex items-center gap-3 px-3 py-2 rounded-xl bg-slate-50/60 dark:bg-slate-900/30">
                <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-amber-50 dark:bg-amber-950/20 text-amber-600 dark:text-amber-400 text-xs font-bold flex-shrink-0">
                  {{ m.username.charAt(0).toUpperCase() }}
                </div>
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-semibold text-slate-800 dark:text-white truncate">{{ m.username }}</p>
                  <p class="text-[11px] text-slate-400">
                    {{ m.role === 'owner' || m.role === 'admin' ? 'Professeur' : 'Élève' }}
                    · {{ m.completed_assignments }} devoir(s) terminé(s)
                  </p>
                </div>
                <button
                  v-if="m.role !== 'owner' && m.role !== 'admin'"
                  @click="removeMember(cls.id, m.user_id)"
                  class="p-1.5 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition flex-shrink-0"
                  title="Retirer de la classe"
                >
                  <UserMinus class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          <!-- TAB: Questions des élèves (Q&A) -->
          <div v-else-if="classDetails[cls.id]?.activeTab === 'questions'">
            <div v-if="classDetails[cls.id]?.loading" class="flex items-center justify-center py-8">
              <Loader2 class="w-6 h-6 text-amber-500 animate-spin" />
            </div>
            <div v-else-if="!classDetails[cls.id]?.questions?.length" class="text-center py-8 text-slate-400 text-sm">
              Aucune question pour le moment.
            </div>
            <div v-else class="space-y-3">
              <div v-for="q in classDetails[cls.id].questions" :key="q.id"
                class="border border-slate-100 dark:border-slate-700/60 rounded-xl p-3">
                <div class="flex items-start justify-between gap-2">
                  <p class="text-sm text-slate-700 dark:text-slate-200">{{ q.body }}</p>
                  <span class="shrink-0 text-[9px] font-bold uppercase px-1.5 py-0.5 rounded"
                    :class="q.status === 'answered' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'">
                    {{ q.status === 'answered' ? 'Répondu' : 'En attente' }}
                  </span>
                </div>
                <p class="text-[11px] text-slate-400 mt-0.5">{{ q.author_username }}</p>

                <div v-if="q.answer" class="mt-2 pl-3 border-l-2 border-green-400">
                  <p class="text-sm text-slate-600 dark:text-slate-300">{{ q.answer }}</p>
                </div>
                <div v-else class="mt-2 flex gap-2">
                  <input v-model="answerDrafts[q.id]" type="text" placeholder="Votre réponse…" @keyup.enter="answerQuestion(cls.id, q.id)"
                    class="flex-1 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-sm" />
                  <button @click="answerQuestion(cls.id, q.id)" :disabled="answering === q.id || !(answerDrafts[q.id] || '').trim()"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-white text-xs font-semibold transition">
                    <Loader2 v-if="answering === q.id" class="w-3.5 h-3.5 animate-spin" /> Répondre
                  </button>
                </div>
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
            <div class="flex items-center justify-between py-2 border-t border-slate-100 dark:border-slate-700/60 mt-3 pt-3">
              <div>
                <label class="block text-sm font-bold text-slate-800 dark:text-slate-200">Cours public</label>
                <span class="text-xs text-slate-400">Si actif, le cours apparaîtra dans l'espace communautaire.</span>
              </div>
              <input v-model="newClassIsPublic" type="checkbox"
                class="w-5 h-5 text-amber-500 border-slate-300 rounded focus:ring-amber-500 cursor-pointer" />
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

    <!-- Create Assignment (builder multi-tâches) -->
    <AssignmentBuilder
      v-if="showCreateAssignmentModal && selectedClassId"
      :class-id="selectedClassId"
      :binders="binderOptions"
      :notes="noteOptions"
      :sets="setOptions"
      @created="onAssignmentCreated"
      @close="showCreateAssignmentModal = false"
    />

    <!-- Annonce -->
    <Teleport to="body">
      <div v-if="showAnnounceModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" @click.self="showAnnounceModal = false">
        <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-md border border-slate-200 dark:border-slate-700">
          <div class="p-6 border-b border-slate-100 dark:border-slate-700">
            <h2 class="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <ClipboardList class="w-5 h-5 text-amber-500" />
              Publier une annonce
            </h2>
            <p class="text-xs text-slate-400 mt-1">Les élèves recevront une notification.</p>
          </div>
          <div class="p-6 space-y-4">
            <input v-model="announceTitle" type="text" placeholder="Titre de l'annonce" maxlength="200"
              class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 transition" />
            <textarea v-model="announceBody" placeholder="Message (optionnel)…" rows="3"
              class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-amber-500 transition resize-none" />
          </div>
          <div class="p-6 pt-0 flex gap-3">
            <button @click="showAnnounceModal = false" class="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition text-sm font-medium">Annuler</button>
            <button @click="postAnnounce" :disabled="!announceTitle.trim() || creating"
              class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-white font-medium text-sm transition">
              <Loader2 v-if="creating" class="w-4 h-4 animate-spin" />
              Publier
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Associate Binder Modal -->
    <Teleport to="body">
      <div v-if="showAssociateModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" @click.self="showAssociateModal = false">
        <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-md border border-slate-200 dark:border-slate-700">
          <div class="p-6 border-b border-slate-100 dark:border-slate-700">
            <h2 class="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <BookOpen class="w-5 h-5 text-amber-500" />
              Associer un classeur
            </h2>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Classeur à associer <span class="text-red-500">*</span></label>
              <select v-model="associateBinderId"
                class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-amber-500 transition">
                <option :value="null" disabled>Choisir un classeur…</option>
                <option v-for="b in availableBindersToAssociate" :key="b.id" :value="b.id">{{ b.name }}</option>
              </select>
              <p v-if="availableBindersToAssociate.length === 0" class="text-xs text-slate-400 mt-1.5">
                Tous vos classeurs sont déjà associés à cette classe.
              </p>
            </div>
            <div v-if="error" class="flex items-center gap-2 text-red-500 text-sm"><AlertCircle class="w-4 h-4 flex-shrink-0" />{{ error }}</div>
          </div>
          <div class="p-6 pt-0 flex gap-3">
            <button @click="showAssociateModal = false" class="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-600 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition text-sm font-medium">Annuler</button>
            <button @click="associateBinder" :disabled="!associateBinderId || creating"
              class="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-white font-medium text-sm transition">
              <Loader2 v-if="creating" class="w-4 h-4 animate-spin" />
              <Plus v-else class="w-4 h-4" />
              Associer
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
