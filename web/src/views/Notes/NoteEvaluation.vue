<template>
  <div class="max-w-3xl mx-auto py-8 px-4 animate-fade-in">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <button
        @click="goBack"
        class="text-sm font-semibold text-ink-muted hover:text-ink dark:text-ink-subtle dark:hover:text-ink-subtle"
      >
        ← Retour à la note
      </button>
      <span class="inline-flex items-center gap-1.5 text-xs font-bold text-primary dark:text-primary uppercase tracking-wider">
        <Sparkles class="w-4 h-4 text-warning" />
        Évaluation IA
      </span>
    </div>

    <!-- GENERATING -->
    <div v-if="step === 'generating'" class="text-center py-20 bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl">
      <svg class="animate-spin h-8 w-8 text-primary mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
      </svg>
      <h2 class="text-lg font-bold text-ink dark:text-white">Génération de votre évaluation…</h2>
      <p class="text-sm text-ink-subtle mt-1">L'IA conçoit des questions variées à partir de votre note. Cela peut prendre quelques secondes.</p>
    </div>

    <!-- ERROR -->
    <div v-else-if="step === 'error'" class="text-center py-16 bg-surface dark:bg-surface-soft border border-danger dark:border-danger rounded-3xl">
      <p class="text-sm font-semibold text-danger dark:text-danger">{{ errorMsg }}</p>
      <div class="flex gap-3 justify-center mt-6">
        <button @click="goBack" class="px-4 py-2 text-xs font-bold text-ink-muted hover:text-ink">Retour</button>
        <button @click="start" class="px-5 py-2 text-xs font-bold text-white bg-primary hover:bg-primary-strong rounded-xl">Réessayer</button>
      </div>
    </div>

    <!-- WORK -->
    <div v-else-if="step === 'work' && evaluation" class="space-y-6">
      <div class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-6">
        <h1 class="text-lg font-bold text-ink dark:text-white">Répondez aux questions</h1>
        <p class="text-xs text-ink-subtle mt-1">{{ evaluation.items.length }} question(s). À la fin, des flashcards vous seront proposées pour vos lacunes.</p>
      </div>

      <div
        v-for="(item, idx) in evaluation.items"
        :key="item.id"
        class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-6 space-y-4"
      >
        <div class="flex items-start gap-3">
          <span class="shrink-0 w-7 h-7 rounded-full bg-primary-soft dark:bg-primary-soft text-primary dark:text-primary text-xs font-bold flex items-center justify-center">{{ idx + 1 }}</span>
          <h3 class="font-bold text-sm text-ink dark:text-ink-subtle leading-relaxed">{{ questionLabel(item) }}</h3>
        </div>

        <!-- QCM -->
        <div v-if="item.type === 'qcm'" class="grid gap-2.5 pl-10">
          <button
            v-for="opt in item.payload.options || []"
            :key="opt.id"
            @click="qcmAnswers[item.id] = opt.id"
            class="text-left px-4 py-3 rounded-xl border text-xs font-semibold transition-all"
            :class="qcmAnswers[item.id] === opt.id
              ? 'border-primary bg-primary-soft text-primary dark:border-primary dark:bg-primary-soft dark:text-primary'
              : 'border-line hover:bg-surface-soft dark:border-line dark:hover:bg-surface-soft text-ink dark:text-ink-subtle'"
          >
            {{ opt.text }}
          </button>
        </div>

        <!-- VF -->
        <div v-else-if="item.type === 'vf'" class="flex gap-3 pl-10">
          <button
            v-for="val in [true, false]"
            :key="String(val)"
            @click="vfAnswers[item.id] = val"
            class="px-6 py-2.5 rounded-xl border text-xs font-bold transition-all"
            :class="vfAnswers[item.id] === val
              ? 'border-primary bg-primary-soft text-primary dark:border-primary dark:bg-primary-soft dark:text-primary'
              : 'border-line hover:bg-surface-soft dark:border-line text-ink dark:text-ink-subtle'"
          >
            {{ val ? 'Vrai' : 'Faux' }}
          </button>
        </div>

        <!-- TROU -->
        <div v-else-if="item.type === 'trou'" class="pl-10">
          <input
            v-model="trouAnswers[item.id]"
            type="text"
            placeholder="Votre réponse…"
            class="w-full px-4 py-2.5 bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        <!-- OPEN -->
        <div v-else-if="item.type === 'open'" class="pl-10 space-y-3">
          <textarea
            v-model="openAnswers[item.id]"
            rows="3"
            :disabled="!!openRevealed[item.id]"
            placeholder="Répondez de mémoire avec vos propres mots…"
            class="w-full px-4 py-3 bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary resize-none disabled:opacity-70"
          ></textarea>

          <button
            v-if="!openRevealed[item.id]"
            @click="revealOpen(item)"
            class="px-4 py-2 text-xs font-bold text-primary border border-primary dark:border-primary rounded-xl hover:bg-primary-soft dark:hover:bg-primary-soft"
          >
            Voir la réponse attendue
          </button>

          <div v-else class="space-y-3">
            <div class="p-4 bg-primary-soft border-l-4 border-primary rounded-r-xl dark:bg-primary-soft dark:border-primary text-xs leading-relaxed text-ink dark:text-ink-subtle">
              <p class="font-bold text-primary dark:text-primary mb-1">Réponse attendue</p>
              {{ openRevealed[item.id].model_answer }}
              <ul v-if="(openRevealed[item.id].key_points || []).length" class="list-disc list-inside mt-2 text-ink-muted dark:text-ink-subtle">
                <li v-for="(kp, i) in openRevealed[item.id].key_points || []" :key="i">{{ kp }}</li>
              </ul>
            </div>
            <div>
              <p class="text-[11px] font-bold text-ink-subtle uppercase tracking-wider mb-2">Votre auto-évaluation</p>
              <div class="flex gap-2">
                <button
                  v-for="g in selfGradeOptions"
                  :key="g.value"
                  @click="setSelfGrade(item, g.value)"
                  class="px-3 py-1.5 rounded-lg border text-[11px] font-bold transition-all"
                  :class="openSelfGrade[item.id] === g.value ? g.activeClass : 'border-line dark:border-line text-ink-muted hover:bg-surface-soft dark:hover:bg-surface-soft'"
                >
                  {{ g.label }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="flex gap-4 sticky bottom-4 bg-surface/80 dark:bg-surface-soft backdrop-blur p-4 rounded-2xl border border-line dark:border-line">
        <button @click="goBack" class="px-5 py-2.5 text-xs font-bold text-ink-muted hover:text-ink">Abandonner</button>
        <button
          @click="finish"
          :disabled="!canFinish || submitting"
          class="flex-1 py-3 text-xs font-bold text-white bg-primary hover:bg-primary-strong disabled:opacity-50 rounded-xl transition-all shadow-md active:scale-95"
        >
          {{ submitting ? 'Correction…' : 'Terminer l\'évaluation' }}
        </button>
      </div>
    </div>

    <!-- RESULTS -->
    <div v-else-if="step === 'results' && result" class="space-y-6">
      <div class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-6 flex items-center justify-between">
        <div>
          <span class="text-[10px] font-bold text-success uppercase tracking-wider">Résultats</span>
          <h1 class="text-lg font-bold text-ink dark:text-white">Score : {{ Math.round(result.score_pct || 0) }}%</h1>
          <p class="text-xs text-ink-subtle mt-1">{{ correctCount }} / {{ result.items.length }} réussi(s).</p>
        </div>
        <div class="relative w-16 h-16 rounded-full flex items-center justify-center bg-primary-soft dark:bg-primary-soft text-primary dark:text-primary font-extrabold text-base border border-primary">
          {{ Math.round(result.score_pct || 0) }}%
        </div>
      </div>

      <div
        v-for="(item, idx) in result.items"
        :key="item.id"
        class="bg-surface dark:bg-surface-soft border rounded-3xl p-5 space-y-2"
        :class="item.is_correct ? 'border-success dark:border-success' : 'border-danger dark:border-danger'"
      >
        <div class="flex items-start justify-between gap-3">
          <h3 class="font-bold text-sm text-ink dark:text-ink-subtle">{{ idx + 1 }}. {{ questionLabel(item) }}</h3>
          <span
            class="shrink-0 px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider"
            :class="item.is_correct ? 'bg-success-soft text-success dark:bg-success-soft dark:text-success' : 'bg-danger-soft text-danger dark:bg-danger-soft dark:text-danger'"
          >
            {{ item.is_correct ? 'Réussi' : 'À revoir' }}
          </span>
        </div>
        <p class="text-xs text-ink-muted dark:text-ink-subtle">
          <span class="font-semibold">Réponse attendue :</span> {{ expectedAnswer(item) }}
        </p>
      </div>

      <!-- Proposition opt-in de cartes pour les lacunes -->
      <div
        v-if="result.proposed_cards.length && !cardsAdded"
        class="bg-surface dark:bg-surface-soft border border-primary dark:border-primary rounded-3xl p-6 space-y-4"
      >
        <div>
          <span class="text-[10px] font-bold text-primary uppercase tracking-wider">Réviser vos lacunes</span>
          <h2 class="text-base font-bold text-ink dark:text-white">Créer des flashcards pour les thèmes ratés</h2>
          <p class="text-xs text-ink-subtle mt-1">Sélectionnez les cartes à ajouter, puis choisissez un deck. Rien n'est ajouté sans votre accord.</p>
        </div>

        <label
          v-for="card in result.proposed_cards"
          :key="card.item_id"
          class="flex items-start gap-3 p-3 rounded-xl border border-line dark:border-line cursor-pointer hover:bg-surface-soft dark:hover:bg-surface-soft"
        >
          <input
            type="checkbox"
            :value="card.item_id"
            v-model="selectedItemIds"
            class="mt-1 accent-primary"
          />
          <div class="min-w-0">
            <p class="text-xs font-semibold text-ink dark:text-ink-subtle">{{ card.front }}</p>
            <p class="text-xs text-ink-subtle mt-0.5">{{ card.back }}</p>
          </div>
        </label>

        <div class="flex flex-col sm:flex-row gap-3 sm:items-end">
          <div class="flex-1">
            <label class="block text-[10px] font-bold text-ink-subtle uppercase tracking-wider mb-1">Deck de destination</label>
            <select
              v-model="selectedDeckId"
              class="w-full px-3 py-2 text-xs rounded-xl border border-line dark:border-line bg-surface dark:bg-surface-soft text-ink dark:text-ink-subtle"
            >
              <option :value="NEW_DECK">➕ Nouveau deck…</option>
              <option v-for="d in decks" :key="d.id" :value="d.id">{{ d.name }}</option>
            </select>
          </div>
          <input
            v-if="selectedDeckId === NEW_DECK"
            v-model="newDeckName"
            type="text"
            placeholder="Nom du nouveau deck"
            class="flex-1 px-3 py-2 text-xs rounded-xl border border-line dark:border-line bg-surface dark:bg-surface-soft text-ink dark:text-ink-subtle"
          />
        </div>

        <p v-if="addError" class="text-xs text-danger">{{ addError }}</p>

        <div class="flex gap-3">
          <button @click="goBack" class="px-5 py-2.5 text-xs font-bold text-ink-muted hover:text-ink">Non merci</button>
          <button
            @click="addSelectedCards"
            :disabled="!canAddCards || addingCards"
            class="flex-1 py-3 text-xs font-bold text-white bg-primary hover:bg-primary-strong rounded-xl shadow-md active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ addingCards ? 'Ajout…' : `Ajouter ${selectedItemIds.length} carte(s) au deck` }}
          </button>
        </div>
      </div>

      <!-- Confirmation après ajout -->
      <div
        v-else-if="cardsAdded"
        class="bg-surface dark:bg-surface-soft border border-success dark:border-success rounded-3xl p-6 flex items-center justify-between gap-4"
      >
        <p class="text-xs font-semibold text-success dark:text-success">{{ cardsAdded }} carte(s) ajoutée(s) à votre deck.</p>
        <button
          v-if="addedDeckId"
          @click="router.push(`/decks/${addedDeckId}`)"
          class="px-4 py-2.5 text-xs font-bold text-white bg-primary hover:bg-primary-strong rounded-xl shadow-md active:scale-95"
        >
          Voir le deck
        </button>
      </div>

      <div class="flex gap-4">
        <button @click="goBack" class="flex-1 py-3 text-xs font-bold text-ink-muted hover:text-ink border border-line dark:border-line rounded-xl">Retour à la note</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Sparkles } from '@lucide/vue'
import api from '../../services/api'
import evaluationService from '../../services/evaluationService'
import type { Evaluation, EvalItem, EvalCorrection, SelfGrade } from '../../services/evaluationService'
import { useDecksStore } from '../../stores/decks'

const route = useRoute()
const router = useRouter()
const noteId = route.params.id as string
const decksStore = useDecksStore()

type Step = 'generating' | 'work' | 'results' | 'error'
const step = ref<Step>('generating')
const errorMsg = ref('')
const evaluation = ref<Evaluation | null>(null)
const result = ref<Evaluation | null>(null)
const submitting = ref(false)

// Réponses par type (typage strict, pas de any)
const qcmAnswers = ref<Record<number, string>>({})
const vfAnswers = ref<Record<number, boolean>>({})
const trouAnswers = ref<Record<number, string>>({})
const openAnswers = ref<Record<number, string>>({})
const openRevealed = ref<Record<number, EvalCorrection>>({})
const openSelfGrade = ref<Record<number, SelfGrade>>({})

// Ajout opt-in de flashcards pour les lacunes
const NEW_DECK = '__new__' as const
const decks = computed(() => decksStore.decks)
const selectedItemIds = ref<number[]>([])
const selectedDeckId = ref<number | typeof NEW_DECK>(NEW_DECK)
const newDeckName = ref('')
const addingCards = ref(false)
const addError = ref('')
const cardsAdded = ref(0)
const addedDeckId = ref<number | null>(null)

const canAddCards = computed(() => {
  if (selectedItemIds.value.length === 0) return false
  if (selectedDeckId.value === NEW_DECK) return newDeckName.value.trim().length > 0
  return true
})

const selfGradeOptions: { value: SelfGrade; label: string; activeClass: string }[] = [
  { value: 'acquired', label: 'Acquis', activeClass: 'border-emerald-500 bg-emerald-50 text-emerald-600 dark:bg-emerald-950/30 dark:text-emerald-400' },
  { value: 'partial', label: 'Partiel', activeClass: 'border-amber-500 bg-amber-50 text-amber-600 dark:bg-amber-950/30 dark:text-amber-400' },
  { value: 'missed', label: 'À revoir', activeClass: 'border-rose-500 bg-rose-50 text-rose-600 dark:bg-rose-950/30 dark:text-rose-400' },
]

function questionLabel(item: EvalItem): string {
  if (item.type === 'vf') return `Vrai ou Faux : ${item.payload.assertion || ''}`
  if (item.type === 'trou') return item.payload.text_with_blank || ''
  return item.payload.question || ''
}

const canFinish = computed(() => {
  const items = evaluation.value?.items || []
  return items.every((item) => {
    if (item.type === 'qcm') return qcmAnswers.value[item.id] !== undefined
    if (item.type === 'vf') return vfAnswers.value[item.id] !== undefined
    if (item.type === 'trou') return (trouAnswers.value[item.id] || '').trim().length > 0
    if (item.type === 'open') return openSelfGrade.value[item.id] !== undefined
    return true
  })
})

const correctCount = computed(() => (result.value?.items || []).filter((i) => i.is_correct).length)

async function start() {
  step.value = 'generating'
  try {
    evaluation.value = await evaluationService.generate(noteId)
    step.value = 'work'
  } catch (err) {
    errorMsg.value = err instanceof Error ? err.message : "La génération a échoué."
    step.value = 'error'
  }
}

async function revealOpen(item: EvalItem) {
  if (!evaluation.value) return
  try {
    const res = await evaluationService.answer(evaluation.value.id, item.id, openAnswers.value[item.id] || '')
    openRevealed.value[item.id] = res.correction
  } catch (err) {
    errorMsg.value = err instanceof Error ? err.message : 'Erreur lors de la vérification.'
  }
}

async function setSelfGrade(item: EvalItem, grade: SelfGrade) {
  if (!evaluation.value) return
  openSelfGrade.value[item.id] = grade
  try {
    await evaluationService.answer(evaluation.value.id, item.id, openAnswers.value[item.id] || '', grade)
  } catch (err) {
    errorMsg.value = err instanceof Error ? err.message : "Erreur lors de l'enregistrement."
  }
}

async function finish() {
  if (!evaluation.value || !canFinish.value) return
  submitting.value = true
  try {
    const evalId = evaluation.value.id
    // Soumettre les items fermés en parallèle (les ouverts sont déjà enregistrés
    // via l'auto-évaluation pendant la phase de travail).
    const submissions = evaluation.value.items
      .filter((item) => item.type !== 'open')
      .map((item) => {
        if (item.type === 'qcm') return evaluationService.answer(evalId, item.id, qcmAnswers.value[item.id])
        if (item.type === 'vf') return evaluationService.answer(evalId, item.id, vfAnswers.value[item.id])
        return evaluationService.answer(evalId, item.id, trouAnswers.value[item.id])
      })
    await Promise.all(submissions)
    result.value = await evaluationService.complete(evalId)
    step.value = 'results'

    // Préparer la proposition de cartes : tout coché par défaut, decks chargés.
    if (result.value.proposed_cards.length) {
      selectedItemIds.value = result.value.proposed_cards.map((c) => c.item_id)
      try {
        await decksStore.fetchDecks()
        if (decks.value.length) selectedDeckId.value = decks.value[0].id
      } catch {
        // chargement non bloquant : l'option « Nouveau deck » reste disponible
      }
    }

    try {
      await api.post('/stats/sessions', {
        module: 'note',
        duration_seconds: 0,
        cards_reviewed: result.value.items.length,
        cards_correct: result.value.items.filter((i) => i.is_correct).length,
      })
    } catch {
      // log non bloquant
    }
  } catch (err) {
    errorMsg.value = err instanceof Error ? err.message : 'Erreur lors de la correction.'
    step.value = 'error'
  } finally {
    submitting.value = false
  }
}

function expectedAnswer(item: EvalItem): string {
  const p = item.payload
  if (item.type === 'qcm') return (p.options || []).find((o) => o.correct)?.text || ''
  if (item.type === 'vf') return p.correct ? 'Vrai' : 'Faux'
  if (item.type === 'trou') return p.answer || ''
  return p.model_answer || ''
}

async function addSelectedCards() {
  if (!result.value || !canAddCards.value || addingCards.value) return
  addingCards.value = true
  addError.value = ''
  try {
    let deckId: number
    if (selectedDeckId.value === NEW_DECK) {
      const deck = await decksStore.createDeck(
        newDeckName.value.trim(),
        `Révisions issues de l'évaluation de la note`,
      )
      deckId = deck.id
    } else {
      deckId = selectedDeckId.value
    }
    const created = await evaluationService.addFlashcards(
      result.value.id,
      deckId,
      selectedItemIds.value,
    )
    cardsAdded.value = created
    addedDeckId.value = deckId
  } catch (err) {
    addError.value = err instanceof Error ? err.message : "Impossible d'ajouter les cartes."
  } finally {
    addingCards.value = false
  }
}

function goBack() {
  router.push(`/notes/${noteId}`)
}

onMounted(start)
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
