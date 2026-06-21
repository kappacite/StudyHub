<template>
  <div class="min-h-screen bg-surface-soft dark:bg-[#070913] flex flex-col animate-fade-in">
    <!-- Header de la session -->
    <header class="bg-surface dark:bg-surface-soft border-b border-line dark:border-line px-6 py-4 sticky top-0 z-30">
      <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <button 
            @click="goBack"
            class="p-2 text-ink-subtle hover:text-ink-muted dark:hover:text-ink-subtle rounded-xl hover:bg-surface-soft dark:hover:bg-surface-soft transition-all"
            :title="isFocusMode ? 'Retour au Focus' : 'Retour à la note'"
          >
            <ChevronLeft class="w-5 h-5" />
          </button>
          <div>
            <span class="text-[10px] font-bold text-primary uppercase tracking-wider">Méthode de la page blanche (IA)</span>
            <h1 class="text-base font-bold text-ink dark:text-white line-clamp-1">
              {{ noteTitle || 'Chargement de la note...' }}
            </h1>
          </div>
        </div>

        <!-- Chronomètre et état -->
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2 bg-surface-soft dark:bg-surface-soft px-4 py-2 rounded-2xl border border-line dark:border-line">
            <Clock class="w-4.5 h-4.5 text-primary" :class="{ 'animate-pulse': step === 'writing' }" />
            <span class="text-sm font-mono font-bold text-ink dark:text-ink-subtle">
              {{ formatTime(timerSeconds) }}
            </span>
          </div>

          <button
            v-if="step === 'writing'"
            @click="submitForAnalysis"
            :disabled="!blurtingText.trim() || analyzing"
            class="inline-flex items-center gap-2 px-5 py-2.5 bg-primary hover:bg-primary-strong text-white rounded-xl text-sm font-bold shadow-lg shadow-elev-primary disabled:opacity-50 disabled:pointer-events-none active:scale-95 transition-all"
          >
            <Sparkles class="w-4 h-4" />
            Lancer l'analyse IA
          </button>

          <button
            v-if="step === 'results'"
            @click="resetSession"
            class="inline-flex items-center gap-2 px-5 py-2.5 border border-line dark:border-line hover:bg-surface-soft dark:hover:bg-surface-soft rounded-xl text-sm font-bold transition-all text-ink dark:text-ink-subtle"
          >
            <RotateCcw class="w-4 h-4" />
            Recommencer
          </button>

          <button
            v-if="step === 'results' && isFocusMode"
            @click="handleNextFocusItem"
            class="inline-flex items-center gap-2 px-5 py-2.5 bg-primary hover:bg-primary-strong text-white rounded-xl text-sm font-bold shadow-lg shadow-elev-primary active:scale-95 transition-all"
          >
            {{ focusStore.reviewQueue.length > 0 ? 'Continuer' : 'Terminer' }}
            <ArrowRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>

    <!-- Zone principale -->
    <main class="flex-1 max-w-7xl mx-auto w-full p-6 flex flex-col">
      <!-- ÉTAPE 1 : RÉDACTION (PAGE BLANCHE) -->
      <div v-if="step === 'writing'" class="flex-1 flex flex-col gap-6">
        <div class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-6 shadow-sm">
          <h2 class="text-sm font-bold text-ink dark:text-ink-subtle flex items-center gap-2">
            <BookOpen class="w-4 h-4 text-primary" />
            Consignes de l'exercice
          </h2>
          <p class="text-xs text-ink-muted dark:text-ink-subtle mt-2 leading-relaxed">
            Fermez vos yeux, respirez un grand coup et essayez de rédiger ci-dessous tout ce dont vous vous souvenez de votre cours
            <strong>{{ noteTitle }}</strong>. Pas besoin de faire de belles phrases ni d'ordonner parfaitement vos propos. L'IA se chargera
            d'extraire et de cartographier vos connaissances, de repérer vos lacunes, et de générer des flashcards d'apprentissage ciblées.
          </p>
        </div>

        <!-- Zone de saisie plein écran -->
        <div class="flex-1 bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-6 shadow-lg shadow-soft-lg dark:shadow-none flex flex-col">
          <textarea
            v-model="blurtingText"
            placeholder="Écrivez ici de mémoire tout ce que vous avez retenu de votre note de cours..."
            class="flex-1 w-full p-4 bg-transparent outline-none border-0 focus:ring-0 text-base leading-relaxed text-ink dark:text-ink-subtle resize-none font-sans"
            :disabled="analyzing"
          ></textarea>
          
          <div class="flex items-center justify-between border-t border-line dark:border-line pt-4 mt-4 text-xs font-semibold text-ink-subtle">
            <span>{{ wordCount }} mots rédigés</span>
            <div v-if="analyzing" class="text-primary flex flex-col items-end gap-1 text-right animate-pulse">
              <span class="flex items-center gap-2">
                <Sparkles class="w-4 h-4 animate-spin" />
                Analyse de votre mémoire en cours...
              </span>
              <span class="text-[10px] text-ink-subtle dark:text-ink-muted italic font-medium max-w-md transition-all duration-500">
                {{ tips[currentTipIndex] }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- ÉTAPE 2 : ANALYSE ET RÉSULTATS (IA) -->
      <div v-else-if="step === 'results'" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Colonne Gauche : Score & Feedback & Concepts -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Bilan de rétention -->
          <div class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-8 shadow-sm flex flex-col md:flex-row items-center gap-8">
            <!-- Jauge Circulaire Animée -->
            <div class="relative w-36 h-36 flex items-center justify-center">
              <svg class="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" stroke="currentColor" stroke-width="8" class="text-ink-subtle dark:text-ink" fill="transparent" />
                <circle 
                  cx="50" 
                  cy="50" 
                  r="40" 
                  stroke="currentColor" 
                  stroke-width="8" 
                  :class="scoreColorClass"
                  fill="transparent" 
                  :stroke-dasharray="2 * Math.PI * 40"
                  :stroke-dashoffset="2 * Math.PI * 40 * (1 - resultData.retention_score / 100)"
                  class="transition-all duration-1000 ease-out"
                />
              </svg>
              <div class="absolute flex flex-col items-center">
                <span class="text-3xl font-extrabold text-ink dark:text-white">{{ resultData.retention_score }}%</span>
                <span class="text-[10px] text-ink-subtle font-bold uppercase tracking-wider">Rétention</span>
              </div>
            </div>

            <!-- Feedback de l'IA -->
            <div class="flex-1 space-y-2">
              <h2 class="text-lg font-extrabold text-ink dark:text-white flex items-center gap-2">
                <Brain class="w-5 h-5 text-primary" />
                Bilan de votre tuteur
              </h2>
              <p class="text-sm text-ink-muted dark:text-ink-subtle leading-relaxed italic">
                " {{ resultData.general_feedback }} "
              </p>
            </div>
          </div>

          <!-- Concepts clés -->
          <div class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-6 shadow-sm space-y-4">
            <h2 class="text-sm font-bold text-ink dark:text-ink-subtle uppercase tracking-wider">Cartographie des concepts du cours</h2>
            
            <div class="divide-y divide-line dark:divide-line">
              <div 
                v-for="(concept, i) in resultData.concepts" 
                :key="i"
                class="py-4 first:pt-0 last:pb-0 flex items-start gap-4"
              >
                <!-- Statut de mémorisation -->
                <span class="mt-1 flex-shrink-0">
                  <CheckCircle2 v-if="concept.status === 'mastered'" class="w-5 h-5 text-success" />
                  <AlertTriangle v-else-if="concept.status === 'incorrect'" class="w-5 h-5 text-warning" />
                  <XCircle v-else class="w-5 h-5 text-danger" />
                </span>

                <div class="space-y-1">
                  <div class="flex items-center gap-2 flex-wrap">
                    <h3 class="text-sm font-bold text-ink dark:text-white">{{ concept.name }}</h3>
                    <span 
                      class="text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded"
                      :class="getStatusBadgeClass(concept.status)"
                    >
                      {{ getStatusText(concept.status) }}
                    </span>
                  </div>
                  <p class="text-xs text-ink-muted dark:text-ink-subtle leading-relaxed">
                    {{ concept.explanation }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Colonne Droite : Génération de Flashcards -->
        <div class="space-y-6">
          <div class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-6 shadow-sm flex flex-col gap-6 sticky top-28">
            <div class="space-y-2">
              <h2 class="text-sm font-bold text-ink dark:text-white uppercase tracking-wider flex items-center gap-2">
                <Sparkles class="w-4 h-4 text-success" />
                Flashcards suggérées
              </h2>
              <p class="text-xs text-ink-subtle dark:text-ink-muted">
                L'IA a généré ces cartes basées sur vos lacunes pour vous aider à les surmonter.
              </p>
            </div>

            <!-- Liste des cartes -->
            <div class="space-y-3 max-h-[300px] overflow-y-auto pr-1">
              <div 
                v-for="(card, index) in resultData.suggested_flashcards" 
                :key="index"
                class="p-3 border border-line dark:border-line rounded-2xl flex items-start gap-3 hover:border-line dark:hover:border-line transition-colors"
              >
                <input 
                  type="checkbox" 
                  v-model="selectedCards[index]"
                  class="mt-1 h-4.5 w-4.5 rounded border-line text-primary focus:ring-primary"
                />
                <div class="text-xs space-y-1">
                  <div class="font-bold text-ink dark:text-ink-subtle">Recto : {{ card.front }}</div>
                  <div class="text-ink-muted dark:text-ink-muted italic">Verso : {{ card.back }}</div>
                </div>
              </div>

              <div v-if="resultData.suggested_flashcards.length === 0" class="text-center py-6 text-xs text-ink-subtle italic">
                Aucune flashcard suggérée (Félicitations, vous maîtrisez tout le cours !)
              </div>
            </div>

            <!-- Sélecteur de deck d'intégration -->
            <div class="border-t border-line dark:border-line pt-4 space-y-4">
              <div class="space-y-2">
                <label class="text-xs font-bold text-ink-muted uppercase tracking-wider">Importer dans un deck</label>
                
                <div class="flex flex-col gap-2">
                  <select 
                    v-model="targetDeckId"
                    class="w-full px-3 py-2 bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-xs font-semibold"
                  >
                    <option :value="null" disabled>Sélectionner un deck...</option>
                    <option v-for="deck in decksStore.decks" :key="deck.id" :value="deck.id">
                      {{ deck.name }} ({{ deck.card_count }} cartes)
                    </option>
                  </select>

                  <div class="flex items-center gap-2">
                    <span class="text-[10px] text-ink-subtle font-bold uppercase">Ou</span>
                    <hr class="flex-1 border-line dark:border-line" />
                  </div>

                  <!-- Option de création rapide de deck -->
                  <div class="flex gap-2">
                    <input 
                      type="text" 
                      v-model="newDeckName"
                      placeholder="Nouveau deck..."
                      class="flex-1 px-3 py-1.5 bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-xs"
                    />
                    <button 
                      @click="createNewDeck"
                      :disabled="!newDeckName.trim() || creatingDeck"
                      class="px-3 py-1.5 bg-surface-soft hover:bg-line dark:bg-surface-soft dark:hover:bg-line text-ink dark:text-ink-subtle text-xs font-bold rounded-xl active:scale-95 transition-all"
                    >
                      Créer
                    </button>
                  </div>
                </div>
              </div>

              <!-- Bouton d'action final -->
              <button 
                @click="importFlashcards"
                :disabled="selectedCardsCount === 0 || !targetDeckId || importing"
                class="w-full inline-flex items-center justify-center gap-2 px-5 py-3 bg-success hover:bg-success text-white rounded-2xl text-xs font-extrabold disabled:opacity-50 disabled:pointer-events-none active:scale-95 transition-all shadow-md shadow-soft-lg"
              >
                <Plus v-if="!importing" class="w-4 h-4" />
                <svg v-else class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Importer {{ selectedCardsCount }} flashcard(s)
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'
import { useDecksStore } from '../../stores/decks'
import { useFocusStore } from '../../stores/focus'
import { 
  ChevronLeft, 
  Clock, 
  Sparkles, 
  Brain, 
  BookOpen, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Plus, 
  RotateCcw,
  ArrowRight
} from '@lucide/vue'

const route = useRoute()
const router = useRouter()
const decksStore = useDecksStore()
const focusStore = useFocusStore()

const noteId = ref(route.params.id as string)
const noteTitle = ref('')
const noteContent = ref('')

const isFocusMode = computed(() => route.query.focus === 'true')

const step = ref<'writing' | 'results'>('writing')
const blurtingText = ref('')
const analyzing = ref(false)

// Chronomètre
const timerSeconds = ref(0)
let timerInterval: any = null

// Résultats IA
const resultData = ref<{
  retention_score: number
  concepts: Array<{
    name: string
    status: 'mastered' | 'missed' | 'incorrect'
    explanation: string
  }>
  suggested_flashcards: Array<{
    front: string
    back: string
  }>
  general_feedback: string
}>({
  retention_score: 0,
  concepts: [],
  suggested_flashcards: [],
  general_feedback: ''
})

// Gestion import cartes
const selectedCards = ref<Record<number, boolean>>({})
const targetDeckId = ref<number | null>(null)
const newDeckName = ref('')
const creatingDeck = ref(false)
const importing = ref(false)

// Conseils d'apprentissage pour faire patienter l'utilisateur
const tips = [
  "La répétition espacée (SM-2) multiplie par 5 la rétention des connaissances à long terme.",
  "Relire passivement son cours est inefficace. Se forcer à s'en souvenir (rappel actif) ancre la mémoire.",
  "Faire des schémas ou cartes mentales crée des connexions sémantiques fortes dans le cerveau.",
  "L'exercice de la page blanche fonctionne mieux si vous le faites 1 à 2 jours après avoir lu le cours.",
  "Consolidez vos lacunes ce soir en relisant vos fiches juste avant de vous endormir.",
  "La création de vos propres flashcards est déjà une étape active d'apprentissage très efficace."
]
const currentTipIndex = ref(0)
let tipInterval: any = null

function startTipRotation() {
  currentTipIndex.value = Math.floor(Math.random() * tips.length)
  tipInterval = setInterval(() => {
    currentTipIndex.value = (currentTipIndex.value + 1) % tips.length
  }, 4000)
}

function stopTipRotation() {
  if (tipInterval) {
    clearInterval(tipInterval)
    tipInterval = null
  }
}

// Compteur de mots
const wordCount = computed(() => {
  const text = blurtingText.value.trim()
  if (!text) return 0
  return text.split(/\s+/).length
})

const selectedCardsCount = computed(() => {
  return Object.values(selectedCards.value).filter(Boolean).length
})

const scoreColorClass = computed(() => {
  const score = resultData.value.retention_score
  if (score >= 80) return 'text-emerald-500'
  if (score >= 50) return 'text-amber-500'
  return 'text-rose-500'
})

// Formatage chronomètre mm:ss
function formatTime(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  const pad = (num: number) => String(num).padStart(2, '0')
  return `${pad(minutes)}:${pad(seconds)}`
}

function startTimer() {
  timerSeconds.value = 0
  timerInterval = setInterval(() => {
    timerSeconds.value++
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
    noteContent.value = res.data.content
  } catch (err) {
    console.error('Erreur lors du chargement de la note', err)
    alert('Impossible de charger la note.')
    goBack()
  }
}

onMounted(async () => {
  startTimer()
  await loadNote()

  // Charger les decks de l'utilisateur
  try {
    await decksStore.fetchDecks()
  } catch (err) {
    console.error('Erreur de chargement des decks', err)
  }
})

watch(() => route.params.id, (newId) => {
  if (route.name === 'Blurting') {
    noteId.value = newId as string
    resetSession()
    loadNote()
  }
})

onBeforeUnmount(() => {
  stopTimer()
})

function goBack() {
  if (isFocusMode.value) {
    router.push('/focus')
  } else if (route.query.from === 'reviews') {
    router.push('/reviews')
  } else {
    router.push(`/notes/${noteId.value}`)
  }
}

function handleNextFocusItem() {
  const nextItem = focusStore.nextQueueItem()
  if (nextItem) {
    if (nextItem.type === 'deck') {
      router.push(`/decks/${nextItem.id}/study?focus=true`)
    } else if (nextItem.type === 'note') {
      noteId.value = String(nextItem.id)
      resetSession()
      loadNote()
    }
  } else {
    router.push('/focus')
  }
}

async function submitForAnalysis() {
  if (!blurtingText.value.trim()) return
  
  stopTimer()
  analyzing.value = true
  startTipRotation()
  
  try {
    const response = await api.post('/blurting/analyze', {
      note_id: noteId.value,
      user_blurting: blurtingText.value,
      duration_seconds: timerSeconds.value
    })
    
    // Repli synchrone côté serveur (broker Redis indisponible) : résultat déjà prêt.
    if (response.data.status === 'SUCCESS' && response.data.result) {
      resultData.value = response.data.result
      selectedCards.value = {}
      resultData.value.suggested_flashcards.forEach((_, idx) => {
        selectedCards.value[idx] = true
      })
      step.value = 'results'
      return
    }

    const { task_id } = response.data
    if (!task_id) {
      throw new Error("L'API n'a pas retourné de identifiant de tâche (task_id).")
    }

    // Polling loop
    let finished = false
    let attempts = 0
    const maxAttempts = 60 // 2 minutes max (60 * 2 secondes)
    
    while (!finished && attempts < maxAttempts) {
      attempts++
      // Attendre 2 secondes avant la prochaine requête
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const pollResponse = await api.get(`/blurting/tasks/${task_id}`)
      const status = pollResponse.data.status
      
      if (status === 'SUCCESS') {
        finished = true
        resultData.value = pollResponse.data.result
        
        // Sélectionner toutes les cartes générées par défaut
        selectedCards.value = {}
        resultData.value.suggested_flashcards.forEach((_, idx) => {
          selectedCards.value[idx] = true
        })
        
        step.value = 'results'
      } else if (status === 'FAILURE' || pollResponse.data.error) {
        finished = true
        const errorMsg = pollResponse.data.error?.message || "L'analyse a échoué."
        throw new Error(errorMsg)
      }
    }
    
    if (!finished) {
      throw new Error("L'analyse a mis trop de temps à s'exécuter. Veuillez réessayer.")
    }
    
  } catch (err: any) {
    console.error('Erreur lors de l\'analyse par l\'IA', err)
    const errMsg = err.response?.data?.error?.message || err.message || 'Une erreur inconnue est survenue.'
    alert(`Erreur d'analyse IA : ${errMsg}\n\nAssurez-vous que la clé d'API Gemini est correctement configurée et valide.`)
    // Reprendre le chrono si l'analyse échoue
    startTimer()
  } finally {
    analyzing.value = false
    stopTipRotation()
  }
}


function resetSession() {
  blurtingText.value = ''
  resultData.value = {
    retention_score: 0,
    concepts: [],
    suggested_flashcards: [],
    general_feedback: ''
  }
  selectedCards.value = {}
  newDeckName.value = ''
  step.value = 'writing'
  timerSeconds.value = 0
  startTimer()
}

// Couleurs des badges
function getStatusBadgeClass(status: string) {
  if (status === 'mastered') return 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-450'
  if (status === 'incorrect') return 'bg-amber-50 text-amber-700 dark:bg-amber-950/30 dark:text-amber-450'
  return 'bg-rose-50 text-rose-700 dark:bg-rose-950/30 dark:text-rose-450'
}

function getStatusText(status: string) {
  if (status === 'mastered') return 'Maîtrisé'
  if (status === 'incorrect') return 'À revoir'
  return 'Oublié'
}

// Actions d'intégration
async function createNewDeck() {
  if (!newDeckName.value.trim()) return
  creatingDeck.value = true
  try {
    const created = await decksStore.createDeck(newDeckName.value.trim(), `Deck créé depuis la page blanche de la note: ${noteTitle.value}`)
    targetDeckId.value = created.id
    newDeckName.value = ''
    alert('Nouveau deck créé avec succès !')
  } catch (err) {
    console.error(err)
    alert('Erreur lors de la création du deck.')
  } finally {
    creatingDeck.value = false
  }
}

async function importFlashcards() {
  if (!targetDeckId.value || selectedCardsCount.value === 0) return
  
  importing.value = true
  
  // Récupérer les cartes cochées
  const cardsToImport = resultData.value.suggested_flashcards.filter((_, idx) => selectedCards.value[idx])
  
  try {
    const res = await api.post('/blurting/create-flashcards', {
      deck_id: targetDeckId.value,
      flashcards: cardsToImport
    })
    
    alert(`${res.data.created_count} flashcard(s) importée(s) avec succès !`)
    
    // Mettre à jour les données du store local de decks
    await decksStore.fetchDecks()
    
    // Désélectionner les cartes importées pour éviter le double import
    selectedCards.value = {}
  } catch (err) {
    console.error('Erreur lors de l\'import des flashcards', err)
    alert('Une erreur est survenue lors de l\'importation des cartes.')
  } finally {
    importing.value = false
  }
}
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
