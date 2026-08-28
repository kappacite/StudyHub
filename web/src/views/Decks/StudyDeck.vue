<template>
  <div class="space-y-6 max-w-xl mx-auto animate-fade-up">
    <!-- Header/Breadcrumb -->
    <div class="flex items-center justify-between text-sm font-semibold">
      <button
        type="button"
        class="flex items-center gap-1 text-ink-muted hover:text-primary"
        @click="goBack"
      >
        <ChevronLeft class="w-4 h-4" />
        {{
          isFocusMode
            ? 'Retour au Focus'
            : $route.query.advance === 'true'
              ? 'Retour au Planning'
              : 'Retour aux decks'
        }}
      </button>
      <span
        class="text-xs font-bold text-primary bg-primary-soft px-2.5 py-1 rounded-lg uppercase tracking-wider"
      >
        {{ deckName }}
      </span>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 gap-3">
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
      <span class="text-sm font-semibold text-ink-subtle uppercase tracking-widest"
        >Préparation de la session...</span
      >
    </div>

    <!-- Error state — échec du chargement initial -->
    <BaseCard v-else-if="loadError" padding="none">
      <BaseEmptyState
        title="Le chargement a échoué"
        description="Vos données n'ont pas pu être récupérées. Vérifiez votre connexion et réessayez."
      >
        <template #icon><AlertCircle class="w-8 h-8 text-danger" /></template>
        <template #actions>
          <BaseButton @click="loadSession">Réessayer</BaseButton>
        </template>
      </BaseEmptyState>
    </BaseCard>

    <!-- État vide (jamais eu de carte) / état complet (session terminée) -->
    <BaseCard v-else-if="studyCards.length === 0" padding="none">
      <BaseEmptyState :title="completionTitle" :description="completionDescription">
        <template #icon>
          <component
            :is="neverHadCards ? Inbox : Sparkles"
            class="w-8 h-8"
            :class="neverHadCards ? 'text-ink-subtle' : 'text-success'"
          />
        </template>
        <template #actions>
          <BaseButton v-if="isFocusMode" block @click="handleNextFocusItem">
            {{ focusStore.reviewQueue.length > 0 ? 'Continuer les révisions' : 'Retour au Focus' }}
          </BaseButton>
          <BaseButton
            v-else-if="$route.query.advance === 'true'"
            block
            @click="router.push('/planning')"
          >
            Retour au Planning
          </BaseButton>
          <BaseButton v-else block @click="router.push('/decks')"> Retour à la liste </BaseButton>
        </template>
      </BaseEmptyState>
    </BaseCard>

    <!-- Active Review State -->
    <div v-else class="space-y-8">
      <!-- Session progress -->
      <div class="space-y-2">
        <div
          class="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-ink-subtle"
        >
          <span>Carte {{ currentIndex + 1 }} sur {{ totalCards }}</span>
          <span>{{ Math.round((currentIndex / totalCards) * 100) }}% complété</span>
        </div>
        <div class="w-full bg-surface-soft rounded-full h-2 overflow-hidden">
          <div
            class="bg-primary h-full rounded-full transition-all duration-300"
            :style="{ width: `${(currentIndex / totalCards) * 100}%` }"
          ></div>
        </div>
      </div>

      <!-- Card container (3D Flip Effect) — cartes recto/verso -->
      <div
        class="perspective-1000 w-full min-h-80 cursor-pointer"
        data-testid="flashcard"
        @click="flipCard"
      >
        <div
          class="relative w-full h-full min-h-80 duration-500 transform-style-3d shadow-md hover:shadow-lg transition-all rounded-3xl"
          :class="[isFlipped ? 'rotate-y-180' : '']"
        >
          <!-- Front Face -->
          <div
            class="absolute inset-0 w-full h-full backface-hidden bg-surface border border-line p-8 rounded-3xl flex flex-col justify-between"
          >
            <span class="text-tiny font-bold text-ink-subtle uppercase tracking-widest">Recto</span>
            <div class="flex-1 flex items-center justify-center text-center">
              <p class="text-xl font-bold leading-normal text-ink">{{ currentCard.front }}</p>
            </div>
            <p
              class="text-center text-xs text-ink-subtle font-semibold uppercase tracking-wider mt-4"
            >
              Cliquer sur la fiche pour retourner
            </p>
          </div>

          <!-- Back Face -->
          <div
            class="absolute inset-0 w-full h-full backface-hidden rotate-y-180 bg-surface border border-primary p-8 rounded-3xl flex flex-col justify-between shadow-elev-primary"
          >
            <span class="text-tiny font-bold text-ink-subtle uppercase tracking-widest">Verso</span>
            <div class="flex-1 flex items-center justify-center text-center px-4">
              <p class="text-lg font-medium leading-relaxed text-ink">{{ currentCard.back }}</p>
            </div>
            <p
              class="text-center text-xs text-ink-subtle font-semibold uppercase tracking-wider mt-4"
            >
              Vous connaissiez la réponse ? Évaluez-vous ci-dessous
            </p>
          </div>
        </div>
      </div>

      <!-- Rating controls (shown when answer is revealed) -->
      <transition name="slide-up">
        <div v-if="showRating" class="space-y-4">
          <h3 class="text-center text-xs font-semibold text-ink-subtle uppercase tracking-widest">
            Qualité de réponse (Algorithme SM-2)
          </h3>

          <BaseToast
            v-if="rateError"
            variant="danger"
            message="La notation n'a pas été enregistrée. Réessayez."
            @close="rateError = false"
          />

          <div class="grid grid-cols-4 gap-2.5">
            <button
              v-for="btn in ratingButtons"
              :key="btn.score"
              type="button"
              class="min-h-11 flex flex-col items-center justify-center gap-1 rounded-btn-primary px-2 py-3 text-tiny font-bold uppercase tracking-wider transition-all active:scale-95"
              :class="btn.class"
              @click.stop="rateCard(btn.score)"
            >
              <component :is="btn.icon" class="w-4 h-4" aria-hidden="true" />
              <span>{{ btn.label }}</span>
              <span
                class="hidden sm:inline-flex items-center justify-center rounded border px-1.5 py-0.5 font-mono text-tiny"
                :class="
                  btn.score === 4
                    ? 'border-primary-ink text-primary-ink opacity-80'
                    : 'border-line text-ink-subtle'
                "
                aria-hidden="true"
                >{{ btn.shortcut }}</span
              >
            </button>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, type Component } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDecksStore } from '../../stores/decks'
import type { Flashcard } from '../../stores/decks'
import { useFocusStore } from '../../stores/focus'
import { usePlanningStore } from '../../stores/planning'
import api from '../../services/api'
import { BaseCard, BaseButton, BaseEmptyState, BaseToast } from '../../components/ui/base'
import {
  ChevronLeft,
  Sparkles,
  Inbox,
  AlertCircle,
  X,
  ArrowRight,
  Check,
  CheckCheck,
} from '@lucide/vue'

const decksStore = useDecksStore()
const focusStore = useFocusStore()
const planningStore = usePlanningStore()
const router = useRouter()
const route = useRoute()

// Mode « dossier » : on révise toutes les cartes dues des decks d'un classeur.
// route.params.id est alors l'UUID du classeur (pas un id de deck numérique).
const isBinderMode = computed(() => route.name === 'StudyBinder')
const binderId = computed(() => String(route.params.id))

const deckId = ref(Number(route.params.id))
const deckName = ref('Deck')
const loading = ref(true)
const loadError = ref(false)
const isFlipped = ref(false)
const rateError = ref(false)

const showRating = computed(() => isFlipped.value)

const isFocusMode = computed(() => route.query.focus === 'true')

const studyCards = ref<Flashcard[]>([])
const currentIndex = ref(0)
const totalCards = ref(0)

const currentCard = computed(() => {
  return studyCards.value[currentIndex.value] || ({} as Flashcard)
})

// « Jamais eu de carte » (totalCards === 0 dès le chargement initial) se distingue
// de « session terminée après révision » (totalCards > 0, studyCards vidée en cours
// de route) : totalCards n'est jamais remis à 0 par la logique de progression.
const neverHadCards = computed(() => totalCards.value === 0)
const completionTitle = computed(() =>
  neverHadCards.value ? 'Rien à réviser ici pour le moment.' : 'Session terminée ! 🎉',
)
const completionDescription = computed(() =>
  neverHadCards.value
    ? "Aucune carte n'est due pour le moment dans ce deck."
    : "Félicitations, vous avez révisé toutes les cartes prévues pour aujourd'hui dans ce deck.",
)

interface RatingButton {
  score: number
  label: string
  shortcut: string
  icon: Component
  class: string
}

// Mapping validé avec l'utilisateur (voir ETAT.md, Écran 3) : 4 boutons au lieu des
// 6 historiques, vers calculate_sm2 (backend/app/services/spaced_repetition.py).
// Seul « Encore » (0) est < 3, donc seul lui redemande la carte dans la session —
// comportement inchangé.
const ratingButtons: RatingButton[] = [
  {
    score: 0,
    label: 'Encore',
    shortcut: '1',
    icon: X,
    class: 'border border-danger text-danger bg-transparent hover:bg-danger-soft',
  },
  {
    score: 3,
    label: 'Difficile',
    shortcut: '2',
    icon: ArrowRight,
    class: 'border border-accent text-accent bg-transparent hover:bg-accent-soft',
  },
  {
    score: 4,
    label: 'Bien',
    shortcut: '3',
    icon: Check,
    class: 'bg-primary text-primary-ink hover:bg-primary-strong',
  },
  {
    score: 5,
    label: 'Facile',
    shortcut: '4',
    icon: CheckCheck,
    class: 'border border-success text-success bg-transparent hover:bg-success-soft',
  },
]

const shortcutScoreMap: Record<string, number> = { '1': 0, '2': 3, '3': 4, '4': 5 }

async function loadSession() {
  loading.value = true
  loadError.value = false
  currentIndex.value = 0
  isFlipped.value = false
  rateError.value = false
  studyCards.value = []

  try {
    if (isBinderMode.value) {
      // Révision d'un dossier entier : cartes dues agrégées sur tous ses decks.
      deckName.value = (route.query.name as string) || 'Dossier'
      const res = await api.get<Flashcard[]>(`/binders/${binderId.value}/study`)
      studyCards.value = res.data
    } else {
      const deck = await decksStore.fetchDeckById(deckId.value)
      if (deck) {
        deckName.value = deck.name
      }

      if (route.query.advance === 'true') {
        studyCards.value = [...planningStore.advanceReviewCards]
      } else {
        // Fetch cards scheduled for study today
        studyCards.value = await decksStore.fetchStudyCards(deckId.value)
      }
    }
    totalCards.value = studyCards.value.length
  } catch (error) {
    console.error("Erreur lors du chargement de la session d'étude :", error)
    loadError.value = true
  } finally {
    loading.value = false
  }
}

function handleKeyDown(e: KeyboardEvent) {
  if (!showRating.value) return
  const score = shortcutScoreMap[e.key]
  if (score === undefined) return
  e.preventDefault()
  rateCard(score)
}

onMounted(async () => {
  window.addEventListener('keydown', handleKeyDown)
  await loadSession()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

watch(
  () => route.params.id,
  (newId) => {
    if (route.name === 'StudyDeck') {
      deckId.value = Number(newId)
      loadSession()
    } else if (route.name === 'StudyBinder') {
      loadSession()
    }
  },
)

function goBack() {
  if (isFocusMode.value) {
    router.push('/focus')
  } else if (route.query.advance === 'true') {
    router.push('/planning')
  } else if (isBinderMode.value) {
    router.push(`/bibliotheque/${binderId.value}`)
  } else {
    router.push('/decks')
  }
}

function handleNextFocusItem() {
  const nextItem = focusStore.nextQueueItem()
  if (nextItem) {
    if (nextItem.type === 'deck') {
      router.push(`/decks/${nextItem.id}/study?focus=true`)
    } else if (nextItem.type === 'note') {
      router.push(`/notes/${nextItem.id}/blurting?focus=true&from=focus`)
    }
  } else {
    router.push('/focus')
  }
}

function flipCard() {
  isFlipped.value = !isFlipped.value
  rateError.value = false
}

async function rateCard(score: number) {
  // On notifie le SM-2 sur le deck d'origine de la CARTE (et non un id de route) :
  // correct en mode deck, dossier (multi-decks) et révision anticipée.
  const card = currentCard.value
  if (!card?.id || !card?.deck_id) {
    console.error('Identifiants manquants pour la notation :', {
      cardId: card?.id,
      deckId: card?.deck_id,
    })
    return
  }

  rateError.value = false
  loading.value = true
  try {
    // Submit score to trigger SM-2 recalculations
    await decksStore.answerCard(card.deck_id, card.id, score)

    isFlipped.value = false

    // Wait a moment for flip animation back to normal
    setTimeout(() => {
      // If user failed, card stays in queue (re-added to the end or just retry later).
      // In our mock, if score < 3 we keep it in queue to learn it again during the session
      if (score < 3) {
        // Move to end of queue to see it again
        const card = studyCards.value[currentIndex.value]
        studyCards.value.push(card)
        totalCards.value = studyCards.value.length
      }

      // Progress
      currentIndex.value++

      // Check if session complete
      if (currentIndex.value >= studyCards.value.length) {
        studyCards.value = []
      }
      loading.value = false
    }, 350)
  } catch (error) {
    console.error('Erreur lors de la notation de la carte :', error)
    rateError.value = true
    loading.value = false
  }
}
</script>

<style scoped>
.perspective-1000 {
  perspective: 1000px;
}
.transform-style-3d {
  transform-style: preserve-3d;
}
.backface-hidden {
  backface-visibility: hidden;
}
.rotate-y-180 {
  transform: rotateY(180deg);
}

.slide-up-enter-active {
  transition:
    opacity 0.3s ease,
    transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
</style>
