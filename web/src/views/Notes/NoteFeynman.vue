<template>
  <div class="min-h-screen bg-surface-soft dark:bg-[#070913] flex flex-col animate-fade-in">
    <!-- Header de la session -->
    <header
      class="bg-surface dark:bg-surface-soft border-b border-line dark:border-line px-6 py-4 sticky top-0 z-30"
    >
      <div class="max-w-4xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <button
            class="p-2 text-ink-subtle hover:text-ink-muted dark:hover:text-ink-subtle rounded-xl hover:bg-surface-soft dark:hover:bg-surface-soft transition-all"
            title="Retour à la note"
            @click="goBack"
          >
            <ChevronLeft class="w-5 h-5" />
          </button>
          <div>
            <span class="text-[10px] font-bold text-primary uppercase tracking-wider"
              >Méthode Feynman (IA)</span
            >
            <h1 class="text-base font-bold text-ink dark:text-white line-clamp-1">
              {{ noteTitle || 'Chargement de la note...' }}
            </h1>
          </div>
        </div>

        <!-- Chronomètre et état -->
        <div class="flex items-center gap-4">
          <div
            class="flex items-center gap-2 bg-surface-soft dark:bg-surface-soft px-4 py-2 rounded-2xl border border-line dark:border-line"
          >
            <Clock class="w-4.5 h-4.5 text-primary" :class="{ 'animate-pulse': step === 'work' }" />
            <span class="text-sm font-mono font-bold text-ink dark:text-ink-subtle">
              {{ formatTimer(feynmanTimer) }}
            </span>
          </div>

          <button
            v-if="step === 'results'"
            class="inline-flex items-center gap-2 px-5 py-2.5 border border-line dark:border-line hover:bg-surface-soft dark:hover:bg-surface-soft rounded-xl text-sm font-bold transition-all text-ink dark:text-ink-subtle"
            @click="resetSession"
          >
            <RotateCcw class="w-4 h-4" />
            Recommencer
          </button>
        </div>
      </div>
    </header>

    <!-- Zone principale -->
    <main class="flex-1 max-w-4xl mx-auto w-full p-6 flex flex-col">
      <!-- ÉTAPE 1 : RÉDACTION -->
      <div v-if="step === 'work'" class="flex-1 flex flex-col gap-6">
        <div
          class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-6 shadow-sm"
        >
          <h2 class="text-sm font-bold text-ink dark:text-ink-subtle flex items-center gap-2">
            <Sparkles class="w-4 h-4 text-primary" />
            Expliquez simplement, comme à un enfant de 10 ans
          </h2>
          <p class="text-xs text-ink-muted dark:text-ink-subtle mt-2 leading-relaxed">
            La meilleure façon de comprendre un concept est de l'expliquer le plus simplement
            possible. Décrivez <strong>{{ noteTitle }}</strong> avec vos propres mots en évitant les
            termes techniques trop complexes. Soyez clair, concis et illustrez votre explication par
            une métaphore ou un exemple simple.
          </p>
        </div>

        <!-- Zone de saisie -->
        <div
          class="flex-1 bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-6 shadow-lg shadow-soft-lg dark:shadow-none flex flex-col"
        >
          <textarea
            v-model="feynmanDraft"
            placeholder="Tapez votre explication simplifiée ici..."
            rows="10"
            :disabled="feynmanAnalyzing"
            class="flex-1 w-full p-4 bg-transparent outline-none border-0 focus:ring-0 text-base leading-relaxed text-ink dark:text-ink-subtle resize-none font-sans"
          ></textarea>

          <div
            class="flex items-center justify-between border-t border-line dark:border-line pt-4 mt-4 text-xs font-semibold text-ink-subtle"
          >
            <span>{{ feynmanWordCount }} mots rédigés</span>
          </div>
        </div>

        <p
          v-if="feynmanError"
          class="text-xs font-semibold text-danger bg-danger-soft border border-danger/30 rounded-xl px-4 py-3"
        >
          {{ feynmanError }}
        </p>

        <div class="flex gap-4">
          <button
            :disabled="feynmanAnalyzing"
            class="px-5 py-2.5 text-xs font-bold text-ink-muted hover:text-ink dark:text-ink-subtle dark:hover:text-ink-subtle disabled:opacity-50"
            @click="goBack"
          >
            Abandonner
          </button>
          <button
            :disabled="!feynmanDraft.trim() || feynmanAnalyzing"
            class="flex-1 py-3 text-xs font-bold text-white bg-primary hover:bg-primary-strong disabled:opacity-50 rounded-xl transition-all shadow-md active:scale-95 flex items-center justify-center gap-2"
            @click="evaluateFeynman"
          >
            <Sparkles v-if="!feynmanAnalyzing" class="w-4 h-4" />
            {{
              feynmanAnalyzing
                ? "L'IA analyse votre explication…"
                : "Analyser mon explication avec l'IA"
            }}
          </button>
        </div>
      </div>

      <!-- ÉTAPE 2 : RÉSULTATS -->
      <div
        v-else-if="step === 'results'"
        class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-6 shadow-sm space-y-8"
      >
        <div
          class="flex flex-col md:flex-row md:items-center justify-between border-b border-line dark:border-line pb-6 gap-6"
        >
          <div>
            <span class="text-[10px] font-bold text-accent uppercase tracking-wider"
              >Analyse Feynman</span
            >
            <h2 class="text-lg font-bold">{{ noteTitle }}</h2>
            <p class="text-xs text-ink-subtle mt-1">Soumis en {{ formatTimer(feynmanTimer) }}.</p>
          </div>

          <!-- Feynman Score -->
          <div class="flex items-center gap-4">
            <div
              class="relative w-16 h-16 rounded-full flex items-center justify-center bg-accent-soft dark:bg-accent-soft text-accent dark:text-accent font-extrabold text-lg border border-accent"
            >
              {{ feynmanResult.score }}%
            </div>
            <div>
              <p class="text-xs font-bold text-ink-subtle uppercase tracking-wider">
                Score de clarté
              </p>
              <p class="text-xs text-ink-muted dark:text-ink-subtle mt-0.5">
                Évalué par l'IA : simplicité, exactitude et couverture.
              </p>
            </div>
          </div>
        </div>

        <!-- Bilan IA -->
        <div
          v-if="feynmanResult.feedback"
          class="p-5 rounded-2xl bg-primary-soft/60 border border-primary/20 dark:bg-primary-soft dark:border-primary"
        >
          <h4
            class="text-xs font-bold text-primary dark:text-primary uppercase tracking-wider flex items-center gap-1.5 mb-2"
          >
            <Sparkles class="w-4 h-4" />
            Bilan de l'IA
          </h4>
          <p class="text-sm text-ink dark:text-ink-subtle leading-relaxed whitespace-pre-line">
            {{ feynmanResult.feedback }}
          </p>
        </div>

        <!-- Evaluation Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- Jargon alert -->
          <div
            class="p-5 rounded-2xl border space-y-2"
            :class="[
              feynmanResult.jargon.length > 0
                ? 'bg-warning-soft border-warning dark:bg-warning-soft dark:border-warning'
                : 'bg-success-soft border-success dark:bg-success-soft dark:border-success',
            ]"
          >
            <h4
              class="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5"
              :class="[
                feynmanResult.jargon.length > 0
                  ? 'text-warning dark:text-warning'
                  : 'text-success dark:text-success',
              ]"
            >
              <Compass class="w-4.5 h-4.5" />
              Jargon à simplifier
            </h4>
            <p class="text-xs text-ink-subtle">
              Termes techniques employés sans être vulgarisés (à reformuler simplement).
            </p>
            <div v-if="feynmanResult.jargon.length > 0" class="flex flex-wrap gap-1 mt-2">
              <span
                v-for="w in feynmanResult.jargon"
                :key="w"
                class="px-2 py-0.5 bg-warning-soft dark:bg-warning-soft text-warning text-[10px] font-semibold rounded-lg"
                >{{ w }}</span
              >
            </div>
            <p v-else class="text-xs font-semibold text-success mt-2">
              Aucun jargon : votre explication reste accessible.
            </p>
          </div>

          <!-- Gaps / lacunes -->
          <div
            class="p-5 rounded-2xl border space-y-2"
            :class="[
              feynmanResult.gaps.length > 0
                ? 'bg-danger-soft border-danger/40 dark:bg-danger-soft dark:border-danger'
                : 'bg-success-soft border-success dark:bg-success-soft dark:border-success',
            ]"
          >
            <h4
              class="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5"
              :class="[
                feynmanResult.gaps.length > 0
                  ? 'text-danger dark:text-danger'
                  : 'text-success dark:text-success',
              ]"
            >
              <Clock class="w-4.5 h-4.5" />
              Points à approfondir
            </h4>
            <p class="text-xs text-ink-subtle">
              Concepts essentiels manquants, incomplets ou erronés vs la note.
            </p>
            <ul v-if="feynmanResult.gaps.length > 0" class="space-y-1.5 mt-2">
              <li v-for="(g, i) in feynmanResult.gaps" :key="i" class="text-xs">
                <span class="font-bold text-ink dark:text-white">{{ g.concept }}</span>
                <span class="text-ink-muted dark:text-ink-subtle"> — {{ g.issue }}</span>
              </li>
            </ul>
            <p v-else class="text-xs font-semibold text-success mt-2">
              Tous les concepts clés sont couverts.
            </p>
          </div>

          <!-- Suggestions -->
          <div
            class="p-5 rounded-2xl bg-surface-soft border border-line dark:bg-surface-soft dark:border-line space-y-2"
          >
            <h4
              class="text-xs font-bold text-ink-muted dark:text-ink-subtle uppercase tracking-wider flex items-center gap-1.5"
            >
              <Sparkles class="w-4.5 h-4.5 text-primary" />
              Suggestion
            </h4>
            <p class="text-xs text-ink-muted dark:text-ink-subtle leading-relaxed mt-2">
              {{
                feynmanResult.suggestion ||
                "Continuez ainsi : reprenez l'exercice sur un autre concept."
              }}
            </p>
          </div>
        </div>

        <button
          class="px-6 py-2.5 text-xs font-bold text-white bg-primary hover:bg-primary-strong rounded-xl transition-all shadow-md active:scale-95"
          @click="resetSession"
        >
          Faire une autre révision
        </button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'
import { ChevronLeft, Clock, Sparkles, RotateCcw, Compass } from '@lucide/vue'

const route = useRoute()
const router = useRouter()

const noteId = ref(route.params.id as string)
const noteTitle = ref('')

const step = ref<'work' | 'results'>('work')
const feynmanDraft = ref('')
const feynmanTimer = ref(0)
let timerInterval: any = null

const feynmanWordCount = computed(() => {
  if (!feynmanDraft.value.trim()) return 0
  return feynmanDraft.value.trim().split(/\s+/).length
})

interface FeynmanGap {
  concept: string
  issue: string
}
const feynmanResult = ref({
  score: 0,
  jargon: [] as string[],
  gaps: [] as FeynmanGap[],
  feedback: '',
  suggestion: '',
})
const feynmanAnalyzing = ref(false)
const feynmanError = ref('')

// Formatage chronomètre mm:ss
function formatTimer(sec: number): string {
  const m = Math.floor(sec / 60)
    .toString()
    .padStart(2, '0')
  const s = (sec % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

function startTimer() {
  feynmanTimer.value = 0
  timerInterval = setInterval(() => {
    feynmanTimer.value++
  }, 1000)
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

async function loadNote() {
  try {
    const res = await api.get(`/notes/${noteId.value}`)
    noteTitle.value = res.data.title
  } catch (err) {
    console.error('Erreur lors du chargement de la note', err)
  }
}

onMounted(async () => {
  startTimer()
  await loadNote()
})

onBeforeUnmount(() => {
  stopTimer()
})

function goBack() {
  router.push(`/notes/${noteId.value}`)
}

function resetSession() {
  feynmanDraft.value = ''
  feynmanError.value = ''
  step.value = 'work'
  startTimer()
}

// Analyse par l'IA (Gemini) : compare l'explication à la note de référence.
// Flux asynchrone (Celery + polling), avec repli synchrone côté serveur.
async function evaluateFeynman() {
  if (!feynmanDraft.value.trim() || feynmanAnalyzing.value) return

  stopTimer()
  feynmanError.value = ''
  feynmanAnalyzing.value = true

  try {
    const response = await api.post('/feynman/analyze', {
      note_id: noteId.value,
      user_explanation: feynmanDraft.value,
      duration_seconds: feynmanTimer.value,
    })

    if (response.data.status === 'SUCCESS' && response.data.result) {
      applyFeynmanResult(response.data.result)
      return
    }

    const { task_id } = response.data
    if (!task_id) throw new Error("L'API n'a pas retourné d'identifiant de tâche (task_id).")

    let finished = false
    let attempts = 0
    const maxAttempts = 60 // ~2 min (60 × 2 s)
    while (!finished && attempts < maxAttempts) {
      attempts++
      await new Promise((resolve) => setTimeout(resolve, 2000))
      const poll = await api.get(`/feynman/tasks/${task_id}`)
      const status = poll.data.status
      if (status === 'SUCCESS') {
        finished = true
        applyFeynmanResult(poll.data.result)
      } else if (status === 'FAILURE' || poll.data.error) {
        finished = true
        throw new Error(poll.data.error?.message || "L'analyse a échoué.")
      }
    }
    if (!finished) throw new Error("L'analyse a mis trop de temps. Veuillez réessayer.")
  } catch (err) {
    feynmanError.value = err instanceof Error ? err.message : "L'analyse IA a échoué."
    console.error('Erreur analyse Feynman', err)
  } finally {
    feynmanAnalyzing.value = false
  }
}

function applyFeynmanResult(result: {
  clarity_score?: number
  jargon?: string[]
  gaps?: FeynmanGap[]
  feedback?: string
  suggestion?: string
}) {
  feynmanResult.value = {
    score: Math.max(0, Math.min(100, Math.round(result.clarity_score ?? 0))),
    jargon: Array.isArray(result.jargon) ? result.jargon : [],
    gaps: Array.isArray(result.gaps) ? result.gaps : [],
    feedback: result.feedback || '',
    suggestion: result.suggestion || '',
  }
  step.value = 'results'
}
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
