<template>
  <div class="space-y-6 max-w-2xl mx-auto animate-fade-in">
    <div class="flex items-center justify-between text-sm font-semibold">
      <button
        class="text-ink-muted hover:text-primary dark:text-ink-subtle flex items-center gap-1"
        @click="goBack"
      >
        <ChevronLeft class="w-4 h-4" /> Retour
      </button>
      <span
        class="text-xs font-bold text-primary bg-primary-soft dark:bg-primary-soft dark:text-primary px-2.5 py-1 rounded-lg uppercase tracking-wider"
      >
        QCM · {{ setName }}
      </span>
    </div>

    <div
      v-if="loading"
      class="py-20 text-center text-sm font-semibold text-ink-subtle uppercase tracking-widest"
    >
      Chargement du QCM…
    </div>

    <!-- Empty -->
    <div
      v-else-if="questions.length === 0"
      class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-10 text-center space-y-3"
    >
      <p class="text-sm text-ink-muted dark:text-ink-subtle">
        Aucune question à réviser pour l'instant.
      </p>
      <div class="flex items-center justify-center gap-3">
        <button
          class="px-4 py-2 text-sm font-bold text-white bg-primary hover:bg-primary-strong rounded-xl"
          @click="goBack"
        >
          Retour
        </button>
        <button
          class="px-4 py-2 text-sm font-bold text-primary border border-primary hover:bg-primary-soft dark:hover:bg-primary-soft rounded-xl"
          @click="reviewAnyway"
        >
          Réviser quand même
        </button>
      </div>
    </div>

    <!-- Result -->
    <div v-else-if="done" class="space-y-6">
      <div
        class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-8 text-center space-y-3"
      >
        <h2 class="text-2xl font-bold text-ink dark:text-white">
          {{ finalScore.score }} / {{ finalScore.maxScore }} points
        </h2>
        <div class="w-full bg-surface-soft dark:bg-surface-soft rounded-full h-3 overflow-hidden">
          <div
            class="h-full rounded-full transition-all"
            :class="finalScore.percentage >= 50 ? 'bg-success' : 'bg-danger'"
            :style="{ width: `${finalScore.percentage}%` }"
          ></div>
        </div>
        <p
          class="text-sm font-bold"
          :class="finalScore.percentage >= 50 ? 'text-success' : 'text-danger'"
        >
          {{ finalScore.percentage }} %
        </p>
      </div>

      <div
        v-for="(q, i) in questions"
        :key="q.id"
        class="bg-surface dark:bg-surface-soft border rounded-2xl p-5"
        :class="
          resultFor(q.id)?.correct
            ? 'border-success dark:border-success'
            : 'border-danger dark:border-danger'
        "
      >
        <div class="flex items-start justify-between gap-3">
          <p class="text-sm font-bold text-ink dark:text-ink-subtle">
            {{ i + 1 }}. {{ q.payload.question }}
          </p>
          <span
            class="text-xs font-bold shrink-0"
            :class="resultFor(q.id)?.correct ? 'text-success' : 'text-danger'"
          >
            {{ resultFor(q.id)?.earned }}/{{ resultFor(q.id)?.points }}
          </span>
        </div>
        <ul class="mt-3 space-y-1.5">
          <li
            v-for="opt in q.payload.options || []"
            :key="opt.id"
            class="flex items-center gap-2 text-sm"
          >
            <span class="w-4 shrink-0 text-center">
              <span v-if="opt.correct" class="text-success">✓</span>
              <span v-else-if="selections[q.id]?.includes(opt.id)" class="text-danger">✕</span>
            </span>
            <span
              :class="
                opt.correct
                  ? 'text-success dark:text-success font-semibold'
                  : 'text-ink-muted dark:text-ink-subtle'
              "
              >{{ opt.text }}</span
            >
          </li>
        </ul>
      </div>

      <button
        class="w-full px-4 py-3 text-sm font-bold text-white bg-primary hover:bg-primary-strong rounded-xl"
        @click="goBack"
      >
        Terminer
      </button>
    </div>

    <!-- Question courante -->
    <template v-else>
      <div class="space-y-2">
        <div
          class="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-ink-subtle"
        >
          <span>{{ index + 1 }} / {{ questions.length }}</span>
        </div>
        <div class="w-full bg-surface-soft dark:bg-surface-soft rounded-full h-2 overflow-hidden">
          <div
            class="bg-primary h-full rounded-full transition-all"
            :style="{ width: `${(index / questions.length) * 100}%` }"
          ></div>
        </div>
      </div>

      <div
        class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-2xl p-5 space-y-4"
      >
        <div>
          <p class="text-sm font-bold text-ink dark:text-ink-subtle mb-1">
            {{ current.payload.question }}
          </p>
          <p class="text-[10px] text-ink-subtle">
            {{ current.payload.points || 1 }} point{{
              (current.payload.points || 1) > 1 ? 's' : ''
            }}
            · cochez la/les bonne(s) réponse(s)
          </p>
        </div>

        <!-- Phase answer : selection des options -->
        <template v-if="phase === 'answer'">
          <div class="space-y-2">
            <label
              v-for="opt in current.payload.options || []"
              :key="opt.id"
              class="flex items-center gap-3 p-2.5 rounded-xl border cursor-pointer transition-colors"
              :class="
                selected.includes(opt.id)
                  ? 'border-primary bg-primary-soft dark:bg-primary-soft'
                  : 'border-line dark:border-line'
              "
            >
              <input
                v-model="selected"
                type="checkbox"
                :value="opt.id"
                class="accent-primary shrink-0"
              />
              <span class="text-sm text-ink dark:text-ink-subtle">{{ opt.text }}</span>
            </label>
          </div>
          <button
            class="w-full px-4 py-3 text-sm font-bold text-white bg-primary hover:bg-primary-strong rounded-xl"
            @click="checkCurrent"
          >
            Valider
          </button>
        </template>

        <!-- Phase self-eval / feedback : correction de CETTE question -->
        <template v-else>
          <p
            class="text-sm font-bold"
            :class="checkResult?.correct ? 'text-success' : 'text-danger'"
          >
            {{ checkResult?.correct ? 'Correct !' : 'Incorrect.' }}
            {{ checkResult?.earned }}/{{ checkResult?.points }} point(s)
          </p>
          <ul class="space-y-1.5">
            <li
              v-for="opt in current.payload.options || []"
              :key="opt.id"
              class="flex items-center gap-2 text-sm"
            >
              <span class="w-4 shrink-0 text-center">
                <span v-if="opt.correct" class="text-success">✓</span>
                <span v-else-if="selected.includes(opt.id)" class="text-danger">✕</span>
              </span>
              <span
                :class="
                  opt.correct
                    ? 'text-success dark:text-success font-semibold'
                    : 'text-ink-muted dark:text-ink-subtle'
                "
                >{{ opt.text }}</span
              >
            </li>
          </ul>

          <template v-if="phase === 'self-eval'">
            <p class="text-center text-[10px] font-bold text-ink-subtle uppercase tracking-widest">
              Votre auto-évaluation
            </p>
            <SelfEvalButtons @select="chooseScore" />
          </template>

          <button
            v-else
            class="w-full px-4 py-3 text-sm font-bold text-white bg-primary hover:bg-primary-strong rounded-xl"
            @click="next"
          >
            {{ index + 1 < questions.length ? 'Suivant' : 'Terminer' }}
          </button>
        </template>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useRevisionStore } from '../../stores/revision'
import type { RevisionItem, QcmCheckResult, QcmAnswerResult } from '../../stores/revision'
import { ChevronLeft } from 'lucide-vue-next'
import SelfEvalButtons from '../../components/revision/SelfEvalButtons.vue'

const router = useRouter()
const route = useRoute()
const revisionStore = useRevisionStore()

const setId = Number(route.params.id)
const setName = ref('')
const loading = ref(true)
const questions = ref<RevisionItem[]>([])
const index = ref(0)
const phase = ref<'answer' | 'self-eval' | 'feedback'>('answer')
const selected = ref<string[]>([])
const checkResult = ref<QcmCheckResult | null>(null)
// Resultats accumules localement, question par question (Task 6) : plus de
// reponse batch a consommer depuis le backend (route /run supprimee) --
// score/max_score/percentage finaux reconstruits a partir de cette liste.
const results = ref<QcmAnswerResult[]>([])
// Options selectionnees par question deja repondue, conservees a part de
// `results` (qui reflete tel quel le contrat backend QcmAnswerResult, sans
// selected_option_ids) -- uniquement pour reafficher les croix rouges sur les
// mauvaises reponses cochees dans le recap final.
const selections = reactive<Record<number, string[]>>({})

const current = computed(
  () => questions.value[index.value] || ({ type: 'qcm', payload: {} } as RevisionItem),
)
const done = computed(() => questions.value.length > 0 && index.value >= questions.value.length)

const finalScore = computed(() => {
  const score = results.value.reduce((sum, r) => sum + r.earned, 0)
  const maxScore = results.value.reduce((sum, r) => sum + r.points, 0)
  const percentage = maxScore > 0 ? Math.round((score / maxScore) * 100) : 0
  return { score, maxScore, percentage }
})

function resultFor(itemId: number) {
  return results.value.find((r) => r.item.id === itemId)
}

// Duree de revision reelle (Task 9, reprise Task 6) : chrono redemarre a
// chaque setupItem() (premier item comme suivants) -- elapsedSeconds() donne
// la duree ecoulee sur la question courante au moment de la soumission.
const itemStartedAt = ref(Date.now())

function elapsedSeconds(): number {
  return Math.max(0, Math.round((Date.now() - itemStartedAt.value) / 1000))
}

function setupItem() {
  itemStartedAt.value = Date.now()
  phase.value = 'answer'
  selected.value = []
  checkResult.value = null
}

async function loadQuestions(includeNotDue = false) {
  loading.value = true
  try {
    questions.value = await revisionStore.fetchStudyItems(setId, includeNotDue)
    index.value = 0
    results.value = []
    Object.keys(selections).forEach((k) => delete selections[Number(k)])
    if (questions.value.length) setupItem()
  } catch (e) {
    console.error('Erreur de chargement du QCM', e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const set = await revisionStore.fetchSet(setId)
    setName.value = set.name
    await loadQuestions()
  } catch (e) {
    console.error('Erreur de chargement du QCM', e)
    loading.value = false
  }
})

// Revision libre (Task 6) : sur liste vide, relance le chargement en incluant
// les questions non dues (couvre aussi le rejeu d'une question deja repondue,
// get_by_set ne filtrant deja plus par echeance -- Task 3).
async function reviewAnyway() {
  await loadQuestions(true)
}

async function checkCurrent() {
  const res = await revisionStore.checkQcmAnswer(setId, current.value.id, [...selected.value])
  checkResult.value = res
  phase.value = 'self-eval'
}

async function chooseScore(score: number) {
  const res = await revisionStore.answerQcmItem(
    setId,
    current.value.id,
    [...selected.value],
    score,
    elapsedSeconds(),
  )
  results.value.push(res)
  selections[current.value.id] = [...selected.value]
  phase.value = 'feedback'
}

function next() {
  index.value++
  if (index.value < questions.value.length) setupItem()
}

function goBack() {
  router.back()
}
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
