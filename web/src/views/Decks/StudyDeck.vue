<template>
  <div class="space-y-6 max-w-xl mx-auto animate-fade-in">
    <!-- Header/Breadcrumb -->
    <div class="flex items-center justify-between text-sm font-semibold">
      <button 
        @click="router.push('/decks')" 
        class="text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400 flex items-center gap-1"
      >
        <ChevronLeft class="w-4 h-4" />
        Retour aux decks
      </button>
      <span class="text-xs font-bold text-indigo-500 bg-indigo-50 dark:bg-indigo-950/40 dark:text-indigo-400 px-2.5 py-1 rounded-lg uppercase tracking-wider">
        {{ deckName }}
      </span>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 gap-3">
      <svg class="animate-spin h-8 w-8 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="text-sm font-semibold text-slate-400 uppercase tracking-widest">Préparation de la session...</span>
    </div>

    <!-- Completed State -->
    <div 
      v-else-if="studyCards.length === 0" 
      class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-10 shadow-sm text-center space-y-6"
    >
      <div class="mx-auto w-16 h-16 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-500 flex items-center justify-center">
        <Sparkles class="w-8 h-8 animate-pulse" />
      </div>
      <div>
        <h2 class="text-xl font-bold text-slate-800 dark:text-white">Session terminée ! 🎉</h2>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-2">Félicitations, vous avez révisé toutes les cartes prévues pour aujourd'hui dans ce deck.</p>
      </div>
      <button 
        @click="router.push('/decks')"
        class="w-full px-4 py-3 text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl transition-all shadow-md shadow-indigo-600/10"
      >
        Retour à la liste
      </button>
    </div>

    <!-- Active Review State -->
    <div v-else class="space-y-8">
      <!-- Session progress -->
      <div class="space-y-2">
        <div class="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-400">
          <span>Carte {{ currentIndex + 1 }} sur {{ totalCards }}</span>
          <span>{{ Math.round(((currentIndex) / totalCards) * 100) }}% complété</span>
        </div>
        <div class="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
          <div 
            class="bg-indigo-600 h-full rounded-full transition-all duration-300"
            :style="{ width: `${((currentIndex) / totalCards) * 100}%` }"
          ></div>
        </div>
      </div>

      <!-- Card container (3D Flip Effect) -->
      <div 
        class="perspective-1000 w-full min-h-[320px] cursor-pointer"
        @click="flipCard"
      >
        <div 
          class="relative w-full h-full min-h-[320px] duration-500 transform-style-3d shadow-md hover:shadow-lg transition-all rounded-3xl"
          :class="[isFlipped ? 'rotate-y-180' : '']"
        >
          <!-- Front Face -->
          <div class="absolute inset-0 w-full h-full backface-hidden bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 p-8 rounded-3xl flex flex-col justify-between">
            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Question / Terme</span>
            <div class="flex-1 flex items-center justify-center text-center">
              <p class="text-xl font-bold leading-normal text-slate-800 dark:text-slate-100">{{ currentCard.front }}</p>
            </div>
            <p class="text-center text-xs text-slate-400 dark:text-slate-500 font-semibold uppercase tracking-wider mt-4">Cliquer sur la carte pour révéler la réponse</p>
          </div>

          <!-- Back Face -->
          <div class="absolute inset-0 w-full h-full backface-hidden rotate-y-180 bg-white dark:bg-slate-900 border border-indigo-500/20 dark:border-indigo-500/10 p-8 rounded-3xl flex flex-col justify-between shadow-indigo-500/5">
            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Réponse / Définition</span>
            <div class="flex-1 flex items-center justify-center text-center px-4">
              <p class="text-lg font-medium leading-relaxed text-slate-700 dark:text-slate-300">{{ currentCard.back }}</p>
            </div>
            <p class="text-center text-xs text-slate-400 dark:text-slate-500 font-semibold uppercase tracking-wider mt-4">Vous connaissiez la réponse ? Évaluez-vous ci-dessous</p>
          </div>
        </div>
      </div>

      <!-- Rating controls (shown when answer is revealed) -->
      <transition name="slide-up">
        <div v-if="isFlipped" class="space-y-4">
          <h3 class="text-center text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Qualité de réponse (Algorithme SM-2)</h3>
          
          <div class="grid grid-cols-3 sm:grid-cols-6 gap-2.5">
            <button 
              v-for="score in ratingButtons" 
              :key="score.value"
              @click.stop="rateCard(score.value)"
              class="flex flex-col items-center justify-center p-3 rounded-xl border transition-all text-center group active:scale-95"
              :class="score.class"
            >
              <span class="text-base font-bold leading-none">{{ score.value }}</span>
              <span class="text-[9px] font-bold uppercase tracking-wider mt-1.5 leading-none opacity-80">{{ score.label }}</span>
            </button>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDecksStore } from '../../stores/decks'
import type { Flashcard } from '../../stores/decks'
import { ChevronLeft, Sparkles } from '@lucide/vue'

const decksStore = useDecksStore()
const router = useRouter()
const route = useRoute()

const deckId = Number(route.params.id)
const deckName = ref('Deck')
const loading = ref(true)
const isFlipped = ref(false)

const studyCards = ref<Flashcard[]>([])
const currentIndex = ref(0)
const totalCards = ref(0)

const currentCard = computed(() => {
  return studyCards.value[currentIndex.value] || {} as Flashcard
})

const ratingButtons = [
  { value: 0, label: 'Oubli', class: 'bg-rose-50 border-rose-100 hover:bg-rose-100/50 text-rose-600 dark:bg-rose-950/20 dark:border-rose-900/30 dark:text-rose-400' },
  { value: 1, label: 'Flou', class: 'bg-rose-50/50 border-rose-100/50 hover:bg-rose-100/30 text-rose-500 dark:bg-rose-950/10 dark:border-rose-900/20 dark:text-rose-400' },
  { value: 2, label: 'Difficile', class: 'bg-amber-50 border-amber-100 hover:bg-amber-100/50 text-amber-600 dark:bg-amber-950/20 dark:border-amber-900/30 dark:text-amber-400' },
  { value: 3, label: 'Correct', class: 'bg-indigo-50 border-indigo-100 hover:bg-indigo-100/50 text-indigo-600 dark:bg-indigo-950/20 dark:border-indigo-900/30 dark:text-indigo-400' },
  { value: 4, label: 'Bien', class: 'bg-emerald-50/50 border-emerald-100/50 hover:bg-emerald-100/30 text-emerald-500 dark:bg-emerald-950/10 dark:border-emerald-900/20 dark:text-emerald-400' },
  { value: 5, label: 'Facile', class: 'bg-emerald-50 border-emerald-100 hover:bg-emerald-100/50 text-emerald-600 dark:bg-emerald-950/20 dark:border-emerald-900/30 dark:text-emerald-400' }
]

onMounted(async () => {
  try {
    const deck = await decksStore.fetchDeckById(deckId)
    if (deck) {
      deckName.value = deck.name
    }
    
    // Fetch cards scheduled for study today
    studyCards.value = await decksStore.fetchStudyCards(deckId)
    totalCards.value = studyCards.value.length
  } catch (error) {
    console.error('Erreur lors du chargement de la session d\'étude :', error)
  } finally {
    loading.value = false
  }
})

function flipCard() {
  isFlipped.value = !isFlipped.value
}

async function rateCard(score: number) {
  if (!deckId || !currentCard.value?.id) {
    console.error('Identifiants manquants pour la notation :', { deckId, cardId: currentCard.value?.id })
    return
  }

  loading.value = true
  try {
    // Submit score to trigger SM-2 recalculations
    await decksStore.answerCard(deckId, currentCard.value.id, score)
    
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
  transition: opacity 0.3s ease, transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
