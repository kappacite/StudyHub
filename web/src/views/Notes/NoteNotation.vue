<template>
  <div class="min-h-screen bg-surface-soft dark:bg-[#070913] flex flex-col animate-fade-in">
    <!-- Header (canevas Note — Notation (IA) : kicker = titre de la note, H1 = "Notation
    de la note" -- inversé par rapport à Feynman/Blurting où le kicker nomme la méthode). -->
    <header
      class="bg-surface dark:bg-surface-soft border-b border-line dark:border-line px-6 py-4 sticky top-0 z-30"
    >
      <div class="max-w-2xl mx-auto flex items-center justify-between gap-4">
        <div class="flex items-center gap-3 min-w-0">
          <button
            data-test="back-to-note"
            class="p-2 text-ink-subtle hover:text-ink-muted dark:hover:text-ink-subtle rounded-xl hover:bg-surface-soft dark:hover:bg-surface-soft transition-all shrink-0"
            title="Retour à la note"
            @click="goBack"
          >
            <ChevronLeft class="w-5 h-5" />
          </button>
          <div class="min-w-0">
            <span
              class="text-[10px] font-bold text-ink-subtle uppercase tracking-wider truncate block"
            >
              {{ noteTitle || 'Chargement de la note...' }}
            </span>
            <h1 class="text-base font-bold text-ink dark:text-white">Notation de la note</h1>
          </div>
        </div>

        <button
          v-if="!loading && !choice && (result || error)"
          class="inline-flex items-center gap-2 px-4 py-2 border border-line dark:border-line rounded-xl text-sm font-semibold hover:bg-surface-soft dark:hover:bg-surface-soft transition-all text-ink-muted dark:text-ink-subtle shrink-0"
          @click="reevaluate"
        >
          <RotateCcw class="w-4 h-4" />
          Réévaluer
        </button>
      </div>
    </header>

    <main class="flex-1 max-w-2xl mx-auto w-full p-6">
      <!-- Choix : une notation existe déjà -->
      <div
        v-if="choice"
        class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-6 shadow-sm space-y-4"
      >
        <p class="text-sm text-ink-muted dark:text-ink-subtle">
          Cette note a déjà été notée
          <template v-if="result?.updated_at">le {{ formattedDate }}</template
          >.
        </p>
        <div class="flex flex-col sm:flex-row gap-3">
          <button
            type="button"
            class="flex-1 px-4 py-3 text-sm font-bold text-accent dark:text-accent border border-accent dark:border-accent rounded-xl hover:bg-accent-soft dark:hover:bg-accent-soft transition-all"
            @click="viewExisting"
          >
            Voir la notation existante
          </button>
          <button
            type="button"
            class="flex-1 px-4 py-3 text-sm font-bold text-white bg-primary hover:bg-primary-strong rounded-xl transition-all"
            @click="reevaluate"
          >
            Réévaluer
          </button>
        </div>
      </div>

      <!-- Chargement -->
      <div v-else-if="loading" class="flex flex-col items-center justify-center py-20 gap-3">
        <svg
          class="animate-spin h-8 w-8 text-primary"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          ></circle>
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path>
        </svg>
        <span class="text-sm font-semibold text-ink-subtle uppercase tracking-widest">
          Notation en cours…
        </span>
      </div>

      <!-- Erreur -->
      <div
        v-else-if="error"
        class="p-4 bg-danger-soft border border-danger/30 rounded-2xl text-danger text-sm"
      >
        {{ error }}
      </div>

      <!-- Résultat (canevas : cercle score /10, verdict, Points forts / Améliorations, Suggestions) -->
      <div v-else-if="result" class="space-y-5">
        <div
          class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-6 shadow-sm space-y-2"
        >
          <div class="flex items-center gap-4">
            <div
              class="w-16 h-16 rounded-full flex items-center justify-center bg-accent-soft dark:bg-accent-soft text-accent dark:text-accent font-extrabold text-lg border border-accent shrink-0"
            >
              {{ formattedScore }}
            </div>
            <p class="flex-1 text-sm text-ink dark:text-ink-subtle leading-relaxed">
              {{ result.verdict }}
            </p>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div
            class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-2xl p-5 space-y-2"
          >
            <h4 class="text-xs font-bold text-success uppercase tracking-wider">Points forts</h4>
            <ul v-if="(result.points_forts?.length ?? 0) > 0" class="space-y-1.5">
              <li
                v-for="(item, i) in result.points_forts"
                :key="i"
                class="text-xs text-ink-muted dark:text-ink-subtle"
              >
                {{ item }}
              </li>
            </ul>
            <p v-else class="text-xs text-ink-subtle italic">
              Aucun point fort particulier relevé.
            </p>
          </div>

          <div
            class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-2xl p-5 space-y-2"
          >
            <h4 class="text-xs font-bold text-warning uppercase tracking-wider">Améliorations</h4>
            <ul v-if="(result.ameliorations?.length ?? 0) > 0" class="space-y-1.5">
              <li
                v-for="(item, i) in result.ameliorations"
                :key="i"
                class="text-xs text-ink-muted dark:text-ink-subtle"
              >
                {{ item }}
              </li>
            </ul>
            <p v-else class="text-xs text-ink-subtle italic">
              Rien à améliorer, excellent travail.
            </p>
          </div>
        </div>

        <div
          v-if="result.suggestions"
          class="p-4 rounded-2xl bg-surface-soft border border-line dark:border-line"
        >
          <h4
            class="text-xs font-bold text-ink-muted dark:text-ink-subtle uppercase tracking-wider mb-1.5"
          >
            Suggestions
          </h4>
          <p class="text-xs text-ink-muted dark:text-ink-subtle leading-relaxed">
            {{ result.suggestions }}
          </p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNotesStore } from '../../stores/notes'
import notationService from '../../services/notationService'
import type { NotationResult } from '../../services/notationService'
import { ChevronLeft, RotateCcw } from '@lucide/vue'

const route = useRoute()
const router = useRouter()
const notesStore = useNotesStore()

const noteId = ref(route.params.id as string)
const noteTitle = ref('')

const choice = ref(false)
const loading = ref(false)
const error = ref<string | null>(null)
const result = ref<NotationResult | null>(null)

const formattedScore = computed(() => {
  const score = result.value?.score
  if (score === undefined) return '—'
  return (score / 10).toLocaleString('fr-FR', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  })
})

const formattedDate = computed(() => {
  const updatedAt = result.value?.updated_at
  if (!updatedAt) return ''
  return new Date(updatedAt).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
})

async function loadNote() {
  try {
    const note = await notesStore.fetchNoteById(noteId.value)
    if (note) noteTitle.value = note.title
  } catch (err) {
    console.error('Erreur lors du chargement de la note', err)
  }
}

async function init() {
  loading.value = true
  try {
    const existing = await notationService.getExisting(noteId.value)
    if (existing) {
      result.value = existing
      choice.value = true
      loading.value = false
      return
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'La notation IA a échoué.'
    loading.value = false
    console.error('Erreur de vérification de la notation existante', err)
    return
  }
  await runGrading()
}

function viewExisting() {
  choice.value = false
}

async function reevaluate() {
  choice.value = false
  error.value = null
  await runGrading()
}

async function runGrading() {
  loading.value = true
  try {
    const res = await notationService.grade(noteId.value)
    if (res.status === 'SUCCESS' && res.result) {
      result.value = res.result
      loading.value = false
      return
    }
    const taskId = res.task_id
    if (!taskId) throw new Error("L'API n'a pas retourné d'identifiant de tâche (task_id).")

    let finished = false
    let attempts = 0
    const maxAttempts = 60
    while (!finished && attempts < maxAttempts) {
      attempts++
      await new Promise((resolve) => setTimeout(resolve, 2000))
      const poll = await notationService.pollTask(taskId)
      if (poll.status === 'SUCCESS') {
        finished = true
        result.value = poll.result ?? null
      } else if (poll.status === 'FAILURE' || poll.error) {
        finished = true
        throw new Error(poll.error?.message || 'La notation a échoué.')
      }
    }
    if (!finished) throw new Error('La notation a mis trop de temps. Veuillez réessayer.')
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'La notation IA a échoué.'
    console.error('Erreur de notation IA', err)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadNote()
  await init()
})

function goBack() {
  router.push(`/notes/${noteId.value}`)
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
