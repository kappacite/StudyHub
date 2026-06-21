<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNotesStore } from '../../stores/notes'
import { useDecksStore } from '../../stores/decks'
import quizService from '../../services/quizService'
import type { Quiz, QuizQuestion } from '../../services/quizService'
import {
  ChevronLeft,
  Sparkles,
  BookOpen,
  ArrowRight,
  RotateCcw,
  CheckCircle2,
  XCircle,
  Trophy,
  HelpCircle,
  Plus,
  Check,
  Loader
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const notesStore = useNotesStore()
const decksStore = useDecksStore()

const noteId = route.params.id as string

// États généraux
const noteTitle = ref('')
const step = ref<'setup' | 'loading' | 'playing' | 'results'>('setup')
const questionCount = ref(7)
const quiz = ref<Quiz | null>(null)
const currentQuestionIndex = ref(0)
const loadingMessage = ref('Préparation de vos questions...')

// Flashcards des erreurs
const targetDeckId = ref<number | null>(null)
const selectedWrongQuestions = ref<number[]>([])
const flashcardsCreated = ref(false)
const flashcardsLoading = ref(false)

// Messages d'attente animés
const tips = [
  "L'IA extrait les concepts clés de votre note pour concevoir des questions ciblées.",
  "Les mauvaises réponses proposées sont conçues pour tester vos nuances de compréhension.",
  "À la fin du QCM, vous pourrez transformer vos erreurs en flashcards de révision !",
  "Prenez le temps de bien lire chaque question et chaque option."
]
const currentTipIndex = ref(0)
let tipInterval: any = null

const currentQuestion = computed<QuizQuestion | null>(() => {
  if (!quiz.value || !quiz.value.questions || quiz.value.questions.length === 0) return null
  return quiz.value.questions[currentQuestionIndex.value]
})

const isLastQuestion = computed(() => {
  if (!quiz.value) return false
  return currentQuestionIndex.value === quiz.value.questions.length - 1
})

// Récupérer les questions fausses du quiz complété
const wrongQuestions = computed(() => {
  if (!quiz.value || step.value !== 'results') return []
  return quiz.value.questions.filter(q => {
    const correctOpt = q.options.find(o => o.correct)
    return q.user_answer_id !== (correctOpt ? correctOpt.id : null)
  })
})

onMounted(async () => {
  try {
    const note = await notesStore.fetchNoteById(noteId)
    if (note) {
      noteTitle.value = note.title
    }
    await decksStore.fetchDecks()
    if (decksStore.decks.length > 0) {
      targetDeckId.value = decksStore.decks[0].id
    }
  } catch (err) {
    console.error('Erreur au chargement initial', err)
  }
})

function startTipInterval() {
  currentTipIndex.value = 0
  tipInterval = setInterval(() => {
    currentTipIndex.value = (currentTipIndex.value + 1) % tips.length
  }, 5000)
}

function stopTipInterval() {
  if (tipInterval) {
    clearInterval(tipInterval)
    tipInterval = null
  }
}

async function handleGenerate() {
  step.value = 'loading'
  loadingMessage.value = "Génération de votre QCM par l'IA..."
  startTipInterval()
  
  try {
    const generated = await quizService.generateQuiz(noteId, questionCount.value)
    quiz.value = generated
    currentQuestionIndex.value = 0
    step.value = 'playing'
  } catch (err) {
    console.error('Erreur de génération du QCM', err)
    alert("Impossible de générer le QCM. Avez-vous configuré GEMINI_API_KEY ? Le quota horaire est limité à 10 générations.")
    step.value = 'setup'
  } finally {
    stopTipInterval()
  }
}

async function selectOption(optionId: string) {
  if (!quiz.value || !currentQuestion.value) return
  
  // Si déjà répondu, on ne fait rien
  if (currentQuestion.value.user_answer_id !== null) return

  const question = currentQuestion.value
  question.user_answer_id = optionId
  
  try {
    await quizService.answerQuestion(quiz.value.id, question.id, optionId)
  } catch (err) {
    console.error('Erreur lors de la sauvegarde de la réponse', err)
  }
}

function nextQuestion() {
  if (isLastQuestion.value) {
    handleComplete()
  } else {
    currentQuestionIndex.value++
  }
}

async function handleComplete() {
  if (!quiz.value) return
  step.value = 'loading'
  loadingMessage.value = "Calcul de vos résultats et de votre score..."
  
  try {
    const completed = await quizService.completeQuiz(quiz.value.id)
    quiz.value = completed
    
    // Pré-sélectionner toutes les mauvaises réponses pour la création de flashcards
    selectedWrongQuestions.value = wrongQuestions.value.map(q => q.id)
    
    step.value = 'results'
  } catch (err) {
    console.error('Erreur de complétion du QCM', err)
    step.value = 'playing'
  }
}

async function handleCreateFlashcards() {
  if (!quiz.value || !targetDeckId.value || selectedWrongQuestions.value.length === 0) return
  
  flashcardsLoading.value = true
  try {
    await quizService.createFlashcards(
      quiz.value.id,
      targetDeckId.value,
      selectedWrongQuestions.value
    )
    flashcardsCreated.value = true
    // Rafraîchir les decks pour mettre à jour le nombre de cartes
    await decksStore.fetchDecks()
  } catch (err) {
    console.error('Erreur lors de la création des flashcards', err)
    alert("Erreur lors de la génération des flashcards.")
  } finally {
    flashcardsLoading.value = false
  }
}

function toggleWrongQuestionSelection(questionId: number) {
  const idx = selectedWrongQuestions.value.indexOf(questionId)
  if (idx > -1) {
    selectedWrongQuestions.value.splice(idx, 1)
  } else {
    selectedWrongQuestions.value.push(questionId)
  }
}

function getOptionClass(option: any, question: QuizQuestion) {
  const isSelected = question.user_answer_id === option.id
  const hasAnswered = question.user_answer_id !== null

  if (!hasAnswered) {
    return 'bg-surface dark:bg-surface-soft border-line dark:border-line hover:border-primary hover:bg-surface-soft dark:hover:bg-surface-soft text-ink dark:text-ink-subtle'
  }

  // Si répondu : on affiche immédiatement si c'est correct
  if (option.correct) {
    return 'bg-success-soft dark:bg-success-soft border-success text-success dark:text-success font-medium'
  }
  if (isSelected && !option.correct) {
    return 'bg-danger-soft dark:bg-danger-soft border-danger text-danger dark:text-danger font-medium'
  }

  return 'bg-surface dark:bg-surface-soft border-line dark:border-line opacity-60 text-ink-subtle dark:text-ink-muted cursor-not-allowed'
}

function goBack() {
  router.push(`/notes/${noteId}`)
}

function resetSession() {
  step.value = 'setup'
  quiz.value = null
  currentQuestionIndex.value = 0
  flashcardsCreated.value = false
  selectedWrongQuestions.value = []
}
</script>

<template>
  <div class="min-h-screen bg-surface-soft dark:bg-[#070913] flex flex-col">
    <!-- Header -->
    <header class="bg-surface dark:bg-surface-soft border-b border-line dark:border-line px-6 py-4 sticky top-0 z-30">
      <div class="max-w-4xl mx-auto flex items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <button 
            @click="goBack"
            class="p-2 text-ink-subtle hover:text-ink-muted dark:hover:text-ink-subtle rounded-xl hover:bg-surface-soft dark:hover:bg-surface-soft transition-all"
            title="Retour à la note"
          >
            <ChevronLeft class="w-5 h-5" />
          </button>
          <div>
            <span class="text-[10px] font-bold text-primary uppercase tracking-wider">Générateur de QCM IA</span>
            <h1 class="text-base font-bold text-ink dark:text-white line-clamp-1">
              {{ noteTitle || 'Chargement de la note...' }}
            </h1>
          </div>
        </div>

        <button
          v-if="step === 'playing' || step === 'results'"
          @click="resetSession"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 border border-line dark:border-line hover:bg-surface-soft dark:hover:bg-surface-soft rounded-lg text-xs font-bold transition-all text-ink-muted dark:text-ink-subtle"
        >
          <RotateCcw class="w-3.5 h-3.5" />
          Quitter / Réinitialiser
        </button>
      </div>
    </header>

    <!-- Zone principale -->
    <main class="flex-1 max-w-4xl mx-auto w-full p-6 flex flex-col justify-center">
      
      <!-- ÉTAPE 1 : CONFIGURATION (SETUP) -->
      <div v-if="step === 'setup'" class="w-full max-w-xl mx-auto bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-8 shadow-sm">
        <div class="text-center mb-6">
          <div class="inline-flex p-3 bg-primary-soft dark:bg-primary-soft rounded-2xl text-primary dark:text-primary mb-4">
            <HelpCircle class="w-8 h-8" />
          </div>
          <h2 class="text-xl font-bold text-ink dark:text-white">Générer un QCM d'entraînement</h2>
          <p class="text-sm text-ink-muted dark:text-ink-subtle mt-2">
            Testez vos connaissances de manière interactive grâce à notre IA. Renseignez le nombre de questions souhaité pour lancer la génération.
          </p>
        </div>

        <div class="space-y-6">
          <div>
            <div class="flex justify-between items-center mb-2">
              <label class="text-sm font-bold text-ink dark:text-ink-subtle">Nombre de questions</label>
              <span class="text-sm font-mono font-bold text-primary dark:text-primary">{{ questionCount }} questions</span>
            </div>
            <input 
              v-model.number="questionCount" 
              type="range" 
              min="5" 
              max="15" 
              step="1"
              class="w-full h-2 bg-line dark:bg-surface-soft rounded-lg appearance-none cursor-pointer accent-primary"
            />
            <div class="flex justify-between text-[10px] text-ink-subtle mt-1">
              <span>5 questions</span>
              <span>10 questions</span>
              <span>15 questions</span>
            </div>
          </div>

          <button
            @click="handleGenerate"
            class="w-full inline-flex items-center justify-center gap-2 px-6 py-3.5 bg-primary hover:bg-primary-strong text-white rounded-2xl font-bold shadow-lg shadow-elev-primary active:scale-98 transition-all"
          >
            <Sparkles class="w-5 h-5" />
            Générer le QCM avec Gemini
          </button>
        </div>
      </div>

      <!-- ÉTAPE 2 : CHARGEMENT (LOADING) -->
      <div v-else-if="step === 'loading'" class="w-full max-w-md mx-auto text-center py-12">
        <div class="relative inline-flex items-center justify-center mb-6">
          <div class="w-16 h-16 border-4 border-primary/30 border-t-primary rounded-full animate-spin"></div>
          <Sparkles class="w-6 h-6 text-primary absolute animate-pulse" />
        </div>
        <h3 class="text-lg font-bold text-ink dark:text-white">{{ loadingMessage }}</h3>
        
        <div class="mt-8 bg-primary-soft dark:bg-primary-soft border border-primary dark:border-primary rounded-2xl p-6 text-left max-w-sm mx-auto">
          <span class="text-[10px] font-bold text-primary dark:text-primary uppercase tracking-widest block mb-1">Le saviez-vous ?</span>
          <p class="text-xs text-ink-muted dark:text-ink-subtle leading-relaxed">
            {{ tips[currentTipIndex] }}
          </p>
        </div>
      </div>

      <!-- ÉTAPE 3 : JEU (PLAYING) -->
      <div v-else-if="step === 'playing' && currentQuestion" class="w-full max-w-2xl mx-auto space-y-6">
        <!-- Barre de progression -->
        <div class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-2xl p-4 flex items-center justify-between shadow-sm">
          <div class="flex items-center gap-3">
            <span class="text-xs font-bold text-ink-muted dark:text-ink-subtle">
              Progression : {{ currentQuestionIndex + 1 }} / {{ quiz?.questions.length }}
            </span>
          </div>
          <div class="w-48 bg-surface-soft dark:bg-surface-soft h-2 rounded-full overflow-hidden">
            <div 
              class="bg-primary h-full transition-all duration-300"
              :style="{ width: `${((currentQuestionIndex + 1) / (quiz?.questions.length || 1)) * 100}%` }"
            ></div>
          </div>
        </div>

        <!-- Carte Question -->
        <div class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-8 shadow-sm space-y-6">
          <div class="inline-flex px-3 py-1 bg-primary-soft dark:bg-primary-soft rounded-xl text-xs font-bold text-primary dark:text-primary">
            Question {{ currentQuestionIndex + 1 }}
          </div>
          
          <h3 class="text-lg font-bold text-ink dark:text-white leading-relaxed">
            {{ currentQuestion.question_text }}
          </h3>

          <div class="grid grid-cols-1 gap-3.5 pt-2">
            <button
              v-for="opt in currentQuestion.options"
              :key="opt.id"
              @click="selectOption(opt.id)"
              :disabled="currentQuestion.user_answer_id !== null"
              class="w-full text-left px-5 py-4 border-2 rounded-2xl text-sm transition-all duration-200 flex items-center justify-between"
              :class="getOptionClass(opt, currentQuestion)"
            >
              <div class="flex items-start gap-3">
                <span class="w-6 h-6 rounded-lg bg-surface-soft dark:bg-surface-soft text-ink-muted dark:text-ink-subtle flex items-center justify-center font-bold text-xs uppercase shrink-0">
                  {{ opt.id }}
                </span>
                <span class="leading-relaxed">{{ opt.text }}</span>
              </div>
              
              <!-- Icône de validation de réponse -->
              <span v-if="currentQuestion.user_answer_id !== null && opt.correct" class="text-success shrink-0 ml-2">
                <CheckCircle2 class="w-5 h-5" />
              </span>
              <span v-else-if="currentQuestion.user_answer_id === opt.id && !opt.correct" class="text-danger shrink-0 ml-2">
                <XCircle class="w-5 h-5" />
              </span>
            </button>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-end">
          <button
            @click="nextQuestion"
            :disabled="currentQuestion.user_answer_id === null"
            class="inline-flex items-center gap-2 px-6 py-3 bg-primary hover:bg-primary-strong text-white rounded-2xl font-bold shadow-lg shadow-elev-primary disabled:opacity-50 disabled:pointer-events-none active:scale-95 transition-all"
          >
            {{ isLastQuestion ? 'Voir les résultats' : 'Question suivante' }}
            <ArrowRight class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- ÉTAPE 4 : RÉSULTATS (RESULTS) -->
      <div v-else-if="step === 'results' && quiz" class="w-full max-w-3xl mx-auto space-y-8 animate-fade-in">
        
        <!-- Score Card -->
        <div class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-8 shadow-sm text-center relative overflow-hidden">
          <div class="absolute -top-12 -left-12 w-36 h-36 bg-primary dark:bg-primary rounded-full blur-2xl"></div>
          <div class="absolute -bottom-12 -right-12 w-36 h-36 bg-success dark:bg-success rounded-full blur-2xl"></div>

          <div class="relative z-10 space-y-4">
            <div class="inline-flex p-4 bg-primary-soft dark:bg-primary-soft rounded-full text-primary dark:text-primary mb-2">
              <Trophy class="w-10 h-10 animate-bounce" />
            </div>
            
            <h2 class="text-2xl font-black text-ink dark:text-white">QCM Terminé !</h2>
            
            <div class="py-2">
              <span class="text-5xl font-black font-mono text-primary dark:text-primary">
                {{ Math.round(quiz.score_pct || 0) }}%
              </span>
              <p class="text-sm font-bold text-ink-muted dark:text-ink-muted mt-1">
                Score de réussite
              </p>
            </div>

            <p class="text-xs text-ink-muted dark:text-ink-subtle max-w-md mx-auto leading-relaxed">
              {{ (quiz.score_pct || 0) >= 80 ? 'Excellent travail ! Vous maîtrisez parfaitement les notions abordées dans cette note.' :
                 (quiz.score_pct || 0) >= 50 ? 'Bon effort ! Cependant, certaines notions nécessitent encore un peu de révision.' :
                 'Continuez vos efforts. Nous vous conseillons de relire la note attentivement et de réviser avec des flashcards.' }}
            </p>
            
            <div class="pt-2">
              <button 
                @click="resetSession"
                class="inline-flex items-center gap-2 px-5 py-2.5 bg-surface-soft hover:bg-line dark:bg-surface-soft dark:hover:bg-line text-ink dark:text-ink-subtle rounded-xl text-xs font-bold transition-all"
              >
                <RotateCcw class="w-4 h-4" />
                Refaire un QCM
              </button>
            </div>
          </div>
        </div>

        <!-- Section Flashcards d'erreurs (Seulement si des erreurs existent) -->
        <div v-if="wrongQuestions.length > 0" class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-8 shadow-sm space-y-6">
          <div class="flex items-center gap-3">
            <div class="p-2 bg-primary-soft dark:bg-primary-soft rounded-xl text-primary dark:text-primary">
              <Plus class="w-5 h-5" />
            </div>
            <div>
              <h3 class="text-base font-bold text-ink dark:text-white">Créer des cartes mémoires depuis vos erreurs</h3>
              <p class="text-xs text-ink-subtle dark:text-ink-muted">Transformez instantanément vos lacunes en cartes flash pour réviser à intervalle régulier.</p>
            </div>
          </div>

          <div v-if="!flashcardsCreated" class="space-y-4">
            <!-- Liste des erreurs avec checkboxes -->
            <div class="border border-line dark:border-line rounded-2xl overflow-hidden divide-y divide-line dark:divide-line">
              <div 
                v-for="q in wrongQuestions" 
                :key="q.id"
                @click="toggleWrongQuestionSelection(q.id)"
                class="p-4 flex items-start gap-3 hover:bg-surface-soft dark:hover:bg-surface-soft cursor-pointer transition-colors"
              >
                <input 
                  type="checkbox"
                  :checked="selectedWrongQuestions.includes(q.id)"
                  @click.stop="toggleWrongQuestionSelection(q.id)"
                  class="mt-1 rounded border-line dark:border-line text-primary focus:ring-primary"
                />
                <div class="text-xs">
                  <p class="font-bold text-ink dark:text-ink-subtle">{{ q.question_text }}</p>
                  <p class="text-ink-subtle dark:text-ink-muted mt-1">
                    Bonne réponse : 
                    <span class="text-success dark:text-success font-medium">
                      {{ q.options.find(o => o.correct)?.text }}
                    </span>
                  </p>
                </div>
              </div>
            </div>

            <!-- Choix du deck et bouton de création -->
            <div class="flex flex-col sm:flex-row gap-4 items-end sm:items-center justify-between bg-surface-soft dark:bg-surface-soft p-4 rounded-2xl border border-line dark:border-line">
              <div class="w-full sm:w-auto flex-1">
                <label class="block text-[10px] font-bold text-ink-subtle dark:text-ink-muted uppercase tracking-widest mb-1.5">Deck cible</label>
                <select
                  v-model="targetDeckId"
                  class="w-full sm:w-64 bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-xl px-3 py-2 text-xs text-ink dark:text-ink-subtle focus:outline-none focus:ring-1 focus:ring-primary"
                >
                  <option v-for="d in decksStore.decks" :key="d.id" :value="d.id">
                    {{ d.name }} ({{ d.card_count }} cartes)
                  </option>
                </select>
              </div>

              <button
                @click="handleCreateFlashcards"
                :disabled="selectedWrongQuestions.length === 0 || flashcardsLoading || !targetDeckId"
                class="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-primary hover:bg-primary-strong text-white rounded-xl text-xs font-bold disabled:opacity-50 disabled:pointer-events-none active:scale-95 transition-all shadow-sm"
              >
                <Loader v-if="flashcardsLoading" class="w-3.5 h-3.5 animate-spin" />
                <Plus v-else class="w-3.5 h-3.5" />
                Générer {{ selectedWrongQuestions.length }} flashcard(s)
              </button>
            </div>
          </div>

          <!-- Succès de création -->
          <div v-else class="bg-success-soft dark:bg-success-soft border border-success dark:border-success text-success dark:text-success p-5 rounded-2xl text-center space-y-2">
            <div class="inline-flex p-2 bg-success-soft dark:bg-success-soft rounded-full text-success dark:text-success">
              <Check class="w-5 h-5" />
            </div>
            <h4 class="text-sm font-bold">Flashcards importées avec succès !</h4>
            <p class="text-xs opacity-80">Vos erreurs ont été ajoutées dans le deck sélectionné. Vous pourrez les réviser via la répétition espacée.</p>
          </div>
        </div>

        <!-- Correction Détaillée -->
        <div class="space-y-4">
          <h3 class="text-base font-bold text-ink dark:text-white flex items-center gap-2">
            <BookOpen class="w-4 h-4 text-primary" />
            Correction détaillée
          </h3>

          <div class="space-y-4">
            <div 
              v-for="(q, idx) in quiz.questions" 
              :key="q.id"
              class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-2xl p-6 shadow-xs space-y-4"
            >
              <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-ink-subtle">Question {{ idx + 1 }}</span>
                <span 
                  v-if="q.user_answer_id === q.options.find(o => o.correct)?.id" 
                  class="inline-flex items-center gap-1 text-success dark:text-success font-bold text-xs"
                >
                  <CheckCircle2 class="w-3.5 h-3.5" />
                  Correct
                </span>
                <span 
                  v-else 
                  class="inline-flex items-center gap-1 text-danger dark:text-danger font-bold text-xs"
                >
                  <XCircle class="w-3.5 h-3.5" />
                  Incorrect
                </span>
              </div>

              <p class="text-sm font-bold text-ink dark:text-white leading-relaxed">
                {{ q.question_text }}
              </p>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                <div 
                  v-for="opt in q.options" 
                  :key="opt.id"
                  class="p-3 border rounded-xl flex items-center gap-2.5"
                  :class="[
                    opt.correct 
                      ? 'bg-success-soft dark:bg-success-soft border-success dark:border-success text-success dark:text-success font-medium' 
                      : q.user_answer_id === opt.id 
                        ? 'bg-danger-soft dark:bg-danger-soft border-danger dark:border-danger text-danger dark:text-danger' 
                        : 'bg-surface-soft dark:bg-surface-soft border-line dark:border-line text-ink-muted dark:text-ink-subtle'
                  ]"
                >
                  <span class="w-5 h-5 rounded-md bg-surface-soft dark:bg-surface-soft text-[10px] uppercase font-bold text-ink-subtle dark:text-ink-muted flex items-center justify-center shrink-0">
                    {{ opt.id }}
                  </span>
                  <span>{{ opt.text }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>

    </main>
  </div>
</template>
