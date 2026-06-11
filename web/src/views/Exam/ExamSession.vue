<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import examService from '../../services/examService'
import type { ExamSession, ExamItem } from '../../services/examService'
import { Clock, ChevronLeft, ChevronRight, HelpCircle, FileText, Check, AlertTriangle, Eye, ShieldAlert } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const sessionId = Number(route.params.id)

// États réactifs
const session = ref<ExamSession | null>(null)
const currentItemIndex = ref(0)
const loading = ref(true)
const timeRemaining = ref(0)
const selectedOptionId = ref<string | null>(null)
const showFlashcardBack = ref(false)
const showExitModal = ref(false)
const showSubmitModal = ref(false)

let timerInterval: any = null

const currentItem = computed<ExamItem | null>(() => {
  if (!session.value || !session.value.items || session.value.items.length === 0) return null
  return session.value.items[currentItemIndex.value]
})

const progressPct = computed(() => {
  if (!session.value) return 0
  const answered = session.value.items.filter(item => item.user_answer !== null).length
  return (answered / session.value.items.length) * 100
})

const formattedTime = computed(() => {
  const mins = Math.floor(timeRemaining.value / 60)
  const secs = timeRemaining.value % 60
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
})

onMounted(async () => {
  try {
    const data = await examService.getExamSession(sessionId)
    if (data.completed_at) {
      router.push(`/exam/${sessionId}/results`)
      return
    }
    session.value = data
    
    // Calculer le temps restant
    const start = new Date(data.started_at).getTime()
    const now = new Date().getTime()
    const elapsed = Math.floor((now - start) / 1000)
    timeRemaining.value = Math.max(0, data.duration_seconds - elapsed)

    if (timeRemaining.value <= 0) {
      await handleAutoComplete()
      return
    }

    // Démarrer le chronomètre
    timerInterval = setInterval(() => {
      if (timeRemaining.value > 0) {
        timeRemaining.value--
      } else {
        clearInterval(timerInterval)
        handleAutoComplete()
      }
    }, 1000)

    // Initialiser la sélection de l'option si déjà répondu (QCM)
    loadCurrentAnswerState()

  } catch (err) {
    console.error("Erreur de récupération de l'examen", err)
    router.push('/exam/setup')
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})

function loadCurrentAnswerState() {
  showFlashcardBack.value = false
  if (currentItem.value && currentItem.value.item_type === 'qcm') {
    selectedOptionId.value = currentItem.value.user_answer || null
  } else {
    selectedOptionId.value = null
  }
}

async function selectQcmOption(optionId: string) {
  if (!session.value || !currentItem.value) return
  selectedOptionId.value = optionId
  
  // Sauvegarde immédiate en arrière-plan
  try {
    currentItem.value.user_answer = optionId
    await examService.submitAnswer(session.value.id, currentItem.value.id, optionId)
  } catch (err) {
    console.error('Erreur lors du choix de l\'option', err)
  }
}

async function submitFlashcard(correct: boolean) {
  if (!session.value || !currentItem.value) return
  const answerVal = correct ? 'correct' : 'incorrect'
  
  try {
    currentItem.value.user_answer = answerVal
    await examService.submitAnswer(session.value.id, currentItem.value.id, correct)
    
    // Passer automatiquement à la question suivante
    nextQuestion()
  } catch (err) {
    console.error('Erreur de sauvegarde flashcard', err)
  }
}

function nextQuestion() {
  if (!session.value) return
  if (currentItemIndex.value < session.value.items.length - 1) {
    currentItemIndex.value++
    loadCurrentAnswerState()
  }
}

function prevQuestion() {
  if (currentItemIndex.value > 0) {
    currentItemIndex.value--
    loadCurrentAnswerState()
  }
}

function selectQuestionDirectly(idx: number) {
  currentItemIndex.value = idx
  loadCurrentAnswerState()
}

async function handleAutoComplete() {
  if (timerInterval) clearInterval(timerInterval)
  alert("Temps écoulé ! Votre copie va être soumise automatiquement.")
  await completeAndRedirect()
}

async function completeAndRedirect() {
  try {
    await examService.completeExam(sessionId)
    router.push(`/exam/${sessionId}/results`)
  } catch (err) {
    console.error("Erreur de finalisation de l'examen", err)
  }
}

async function forceQuit() {
  router.push('/exam/setup')
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-[#070913] flex flex-col font-sans select-none">
    
    <!-- Bandeau Immersif Supérieur -->
    <header class="bg-white dark:bg-slate-900 border-b border-slate-150 dark:border-slate-800 px-6 py-4 flex items-center justify-between sticky top-0 z-30">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-indigo-50 dark:bg-indigo-950/45 text-indigo-600 dark:text-indigo-400 rounded-xl">
          <ShieldAlert class="w-5 h-5" />
        </div>
        <div>
          <span class="text-[10px] font-black text-indigo-500 uppercase tracking-widest block">Mode Examen Actif</span>
          <h1 class="text-sm font-black text-slate-800 dark:text-white">Ne fermez pas cette page</h1>
        </div>
      </div>

      <!-- Chronomètre & Actions -->
      <div class="flex items-center gap-4">
        <!-- Timer -->
        <div class="flex items-center gap-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 px-4 py-2 rounded-2xl shadow-inner"
          :class="[timeRemaining < 60 ? 'border-rose-500/30 text-rose-600 dark:text-rose-455 animate-pulse' : 'text-slate-700 dark:text-slate-300']"
        >
          <Clock class="w-4.5 h-4.5" :class="[timeRemaining < 60 ? 'text-rose-500' : 'text-indigo-500']" />
          <span class="font-mono font-black text-sm">{{ formattedTime }}</span>
        </div>

        <!-- Abandonner -->
        <button
          @click="showExitModal = true"
          class="px-4 py-2 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 text-xs font-bold rounded-xl transition-all"
        >
          Abandonner
        </button>

        <!-- Soumettre -->
        <button
          @click="showSubmitModal = true"
          class="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl shadow-md shadow-indigo-600/15 active:scale-95 transition-all"
        >
          Terminer l'examen
        </button>
      </div>
    </header>

    <!-- Zone principale -->
    <div v-if="!loading && session" class="flex-1 max-w-6xl mx-auto w-full p-6 grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
      
      <!-- Colonne centrale : Question active (span 3) -->
      <div class="lg:col-span-3 space-y-6">
        
        <!-- Barre de progression de la session -->
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-850 rounded-2xl p-4 flex items-center justify-between shadow-xs">
          <span class="text-xs font-bold text-slate-500 dark:text-slate-400">
            Avancement des réponses
          </span>
          <div class="w-64 bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
            <div 
              class="bg-indigo-600 h-full transition-all duration-300"
              :style="{ width: `${progressPct}%` }"
            ></div>
          </div>
        </div>

        <!-- Question Card -->
        <div v-if="currentItem" class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-850 rounded-3xl p-8 shadow-sm space-y-6 min-h-[350px] flex flex-col justify-between">
          <div class="space-y-6">
            <div class="flex items-center justify-between">
              <span class="inline-flex px-3 py-1 bg-indigo-50 dark:bg-indigo-950/35 rounded-xl text-xs font-black text-indigo-600 dark:text-indigo-400">
                Question {{ currentItemIndex + 1 }}
              </span>
              <span class="text-xs font-bold text-slate-400 flex items-center gap-1">
                <HelpCircle v-if="currentItem.item_type === 'qcm'" class="w-3.5 h-3.5 text-indigo-500" />
                <FileText v-else class="w-3.5 h-3.5 text-indigo-500" />
                {{ currentItem.item_type === 'qcm' ? 'Choix Multiple (QCM)' : 'Carte Mémoire (Flashcard)' }}
              </span>
            </div>

            <!-- Contenu textuel (Question / Recto) -->
            <div class="space-y-4">
              <h3 class="text-lg font-black text-slate-800 dark:text-white leading-relaxed">
                {{ currentItem.front }}
              </h3>
            </div>

            <!-- Réponses possibles / Choix -->
            <div class="pt-2">
              
              <!-- Cas QCM -->
              <div v-if="currentItem.item_type === 'qcm' && currentItem.options" class="grid grid-cols-1 gap-3">
                <button
                  v-for="opt in currentItem.options"
                  :key="opt.id"
                  @click="selectQcmOption(opt.id)"
                  class="w-full text-left px-5 py-4 border-2 rounded-2xl text-sm transition-all duration-150 flex items-center gap-3"
                  :class="[selectedOptionId === opt.id 
                    ? 'border-indigo-600 bg-indigo-50/10 dark:bg-indigo-950/20 text-indigo-600 dark:text-indigo-400 font-bold' 
                    : 'bg-white dark:bg-slate-900 border-slate-150 dark:border-slate-800 hover:border-slate-350 hover:bg-slate-50/50 dark:hover:bg-slate-800/40 text-slate-700 dark:text-slate-200'
                  ]"
                >
                  <span class="w-6 h-6 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 flex items-center justify-center font-bold text-xs uppercase shrink-0">
                    {{ opt.id }}
                  </span>
                  <span>{{ opt.text }}</span>
                </button>
              </div>

              <!-- Cas Flashcard (avec zone de révélation) -->
              <div v-else-if="currentItem.item_type === 'flashcard'" class="space-y-6 text-center py-4">
                
                <!-- Zone Verso (Cachée / Révélée) -->
                <div v-if="showFlashcardBack" class="p-6 bg-slate-50 dark:bg-slate-950/40 rounded-2xl border border-slate-150 dark:border-slate-800 text-left space-y-2 max-w-xl mx-auto">
                  <span class="text-[9px] font-bold text-indigo-500 uppercase tracking-widest block">Verso de la carte</span>
                  <p class="text-sm text-slate-750 dark:text-slate-250 leading-relaxed whitespace-pre-line">{{ currentItem.back }}</p>
                </div>

                <div v-else class="py-6">
                  <button
                    @click="showFlashcardBack = true"
                    class="inline-flex items-center gap-2 px-6 py-3 border-2 border-indigo-500/20 bg-indigo-50/5 dark:bg-indigo-950/5 hover:bg-indigo-50/20 dark:hover:bg-indigo-950/25 text-indigo-600 dark:text-indigo-400 rounded-2xl text-xs font-bold transition-all"
                  >
                    <Eye class="w-4 h-4" />
                    Révéler le verso pour s'auto-évaluer
                  </button>
                </div>

                <!-- Boutons d'auto-évaluation (Visibles uniquement après révélation) -->
                <div v-if="showFlashcardBack" class="flex items-center justify-center gap-4 pt-2">
                  <button
                    @click="submitFlashcard(false)"
                    class="px-6 py-3 border border-rose-500 text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/10 text-xs font-bold rounded-2xl transition-all"
                  >
                    Je ne savais pas ❌
                  </button>
                  <button
                    @click="submitFlashcard(true)"
                    class="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-2xl transition-all shadow-sm"
                  >
                    Je savais !  ✔️
                  </button>
                </div>
              </div>

            </div>
          </div>

          <!-- Boutons bas de page -->
          <div class="flex justify-between items-center border-t border-slate-100 dark:border-slate-800 pt-6 mt-4">
            <button
              @click="prevQuestion"
              :disabled="currentItemIndex === 0"
              class="inline-flex items-center gap-2 px-5 py-2.5 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-xl text-xs font-bold transition-all disabled:opacity-30 disabled:pointer-events-none text-slate-600 dark:text-slate-300"
            >
              <ChevronLeft class="w-4 h-4" />
              Précédente
            </button>

            <!-- Sauter / Suivant (pour QCM ou si déjà évalué) -->
            <button
              @click="nextQuestion"
              :disabled="currentItemIndex === session.items.length - 1"
              class="inline-flex items-center gap-2 px-5 py-2.5 bg-slate-800 hover:bg-slate-900 text-white dark:bg-slate-700 dark:hover:bg-slate-650 rounded-xl text-xs font-bold transition-all disabled:opacity-30 disabled:pointer-events-none"
            >
              Suivante
              <ChevronRight class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <!-- Grille latérale de navigation de l'examen (span 1) -->
      <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-850 rounded-3xl p-6 shadow-sm space-y-4">
        <h3 class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">
          Feuille de réponses
        </h3>
        
        <div class="grid grid-cols-4 gap-2.5">
          <button
            v-for="(item, idx) in session.items"
            :key="item.id"
            @click="selectQuestionDirectly(idx)"
            class="w-10 h-10 rounded-xl text-xs font-black flex items-center justify-center transition-all"
            :class="[
              currentItemIndex === idx
                ? 'ring-2 ring-indigo-500 ring-offset-2 dark:ring-offset-slate-900'
                : '',
              item.user_answer !== null
                ? 'bg-indigo-600 text-white font-bold'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 hover:bg-slate-200/50 dark:hover:bg-slate-700/50'
            ]"
          >
            {{ item.id }}
          </button>
        </div>

        <div class="pt-4 border-t border-slate-100 dark:border-slate-800 space-y-2.5 text-[10px] text-slate-400 font-semibold">
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded bg-indigo-600 block"></span>
            <span>Question répondue</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded bg-slate-100 dark:bg-slate-800 block"></span>
            <span>Non répondue</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded ring-2 ring-indigo-500 block"></span>
            <span>Question en cours</span>
          </div>
        </div>
      </div>

    </div>

    <!-- Modale d'abandon (Exit confirmation) -->
    <div v-if="showExitModal" class="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="bg-white dark:bg-slate-900 rounded-3xl p-6 max-w-sm w-full text-center space-y-4 shadow-xl">
        <div class="inline-flex p-3 bg-rose-50 dark:bg-rose-950/35 rounded-2xl text-rose-500 mb-2">
          <AlertTriangle class="w-6 h-6" />
        </div>
        <h4 class="text-base font-black text-slate-800 dark:text-white">Abandonner l'examen ?</h4>
        <p class="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
          Attention, si vous quittez la session maintenant, aucune de vos réponses ne sera enregistrée et votre score sera perdu.
        </p>
        <div class="flex items-center gap-3 pt-2">
          <button 
            @click="showExitModal = false"
            class="flex-1 py-2.5 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-xl text-xs font-bold transition-all text-slate-700 dark:text-slate-200"
          >
            Continuer l'examen
          </button>
          <button 
            @click="forceQuit"
            class="flex-1 py-2.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold transition-all"
          >
            Abandonner
          </button>
        </div>
      </div>
    </div>

    <!-- Modale de validation de copie -->
    <div v-if="showSubmitModal" class="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="bg-white dark:bg-slate-900 rounded-3xl p-6 max-w-sm w-full text-center space-y-4 shadow-xl">
        <div class="inline-flex p-3 bg-indigo-50 dark:bg-indigo-950/35 rounded-2xl text-indigo-500 mb-2">
          <Check class="w-6 h-6" />
        </div>
        <h4 class="text-base font-black text-slate-800 dark:text-white">Soumettre votre copie ?</h4>
        
        <!-- Alerte si des questions n'ont pas de réponse -->
        <div v-if="session && session.items.some(item => item.user_answer === null)" class="p-3 bg-amber-50 dark:bg-amber-950/15 border border-amber-250 dark:border-amber-950/25 text-amber-800 dark:text-amber-400 rounded-xl text-left text-[11px] leading-relaxed flex gap-2">
          <AlertTriangle class="w-4 h-4 shrink-0 mt-0.5" />
          <span>Certaines questions n'ont pas encore reçu de réponse. Soumettre tout de même ?</span>
        </div>

        <p class="text-xs text-slate-500 dark:text-slate-400 leading-relaxed" v-else>
          Êtes-vous sûr de vouloir finaliser votre examen ? Vos scores seront alors enregistrés.
        </p>

        <div class="flex items-center gap-3 pt-2">
          <button 
            @click="showSubmitModal = false"
            class="flex-1 py-2.5 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-xl text-xs font-bold transition-all text-slate-700 dark:text-slate-200"
          >
            Revenir aux questions
          </button>
          <button 
            @click="completeAndRedirect"
            class="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-all shadow-md shadow-indigo-600/10"
          >
            Soumettre la copie
          </button>
        </div>
      </div>
    </div>

  </div>
</template>
