<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBindersStore } from '../../stores/binders'
import examService from '../../services/examService'
import { ShieldAlert, Clock, Settings, Sparkles } from 'lucide-vue-next'

const router = useRouter()
const bindersStore = useBindersStore()

const binderId = ref<string | null>(null)
const durationMinutes = ref(30)
const includeFlashcards = ref(true)
const includeQcm = ref(true)
const questionLimit = ref(20)
const loading = ref(false)
const errorMsg = ref('')

onMounted(async () => {
  try {
    await bindersStore.fetchBinders()
    if (bindersStore.binders.length > 0) {
      binderId.value = bindersStore.binders[0].id
    }
  } catch (err) {
    console.error('Erreur au chargement des classeurs', err)
  }
})

async function handleStart() {
  if (!binderId.value) {
    errorMsg.value = 'Veuillez sélectionner un classeur.'
    return
  }
  if (!includeFlashcards.value && !includeQcm.value) {
    errorMsg.value = 'Veuillez sélectionner au moins un type de question (Cartes Mémoires ou QCM).'
    return
  }

  loading.value = true
  errorMsg.value = ''

  try {
    const session = await examService.startExam(
      binderId.value,
      durationMinutes.value,
      includeFlashcards.value,
      includeQcm.value,
      questionLimit.value
    )
    router.push(`/exam/${session.id}`)
  } catch (err: any) {
    console.error("Erreur de lancement de l'examen", err)
    errorMsg.value = err.response?.data?.error?.message || "Impossible de démarrer l'examen. Vérifiez que vous possédez assez de flashcards ou de QCM déjà créés pour ce classeur."
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-xl mx-auto py-8 px-4">
    <!-- Header -->
    <div class="text-center mb-8">
      <div class="inline-flex p-3 bg-primary-soft dark:bg-primary-soft rounded-2xl text-primary dark:text-primary mb-3 shadow-md shadow-elev-primary">
        <ShieldAlert class="w-8 h-8" />
      </div>
      <h1 class="text-2xl font-black text-ink dark:text-white">Simulateur de Mode Examen</h1>
      <p class="text-sm text-ink-muted dark:text-ink-subtle mt-2 leading-relaxed">
        Évaluez-vous dans des conditions réelles. Un mélange chronométré de vos cartes mémoires et de vos questions de QCM sans aucun accès aux fiches de révision.
      </p>
    </div>

    <!-- Form -->
    <div class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-8 shadow-sm space-y-6">
      
      <!-- Classeur cible -->
      <div>
        <label class="block text-xs font-bold text-ink-subtle dark:text-ink-muted uppercase tracking-widest mb-2">
          Classeur d'examen
        </label>
        <select
          v-model="binderId"
          class="w-full bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-xl px-4 py-3 text-sm text-ink dark:text-ink-subtle focus:outline-none focus:ring-1 focus:ring-primary"
        >
          <option v-for="b in bindersStore.binders" :key="b.id" :value="b.id">
            📁 {{ b.name }}
          </option>
        </select>
        <p class="text-[10px] text-ink-subtle dark:text-ink-muted mt-1.5">
          L'examen piochera dans ce classeur et l'ensemble de ses sous-classeurs.
        </p>
      </div>

      <!-- Durée & Limites -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-bold text-ink-subtle dark:text-ink-muted uppercase tracking-widest mb-2">
            Durée maximum
          </label>
          <div class="relative">
            <select
              v-model.number="durationMinutes"
              class="w-full bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-xl pl-9 pr-4 py-3 text-sm text-ink dark:text-ink-subtle focus:outline-none focus:ring-1 focus:ring-primary"
            >
              <option :value="15">15 min</option>
              <option :value="30">30 min</option>
              <option :value="45">45 min</option>
              <option :value="60">1 heure</option>
              <option :value="90">1h30</option>
              <option :value="120">2 heures</option>
            </select>
            <Clock class="w-4 h-4 text-primary absolute left-3 top-3.5" />
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold text-ink-subtle dark:text-ink-muted uppercase tracking-widest mb-2">
            Limite de questions
          </label>
          <div class="relative">
            <select
              v-model.number="questionLimit"
              class="w-full bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-xl pl-9 pr-4 py-3 text-sm text-ink dark:text-ink-subtle focus:outline-none focus:ring-1 focus:ring-primary"
            >
              <option :value="10">10 questions</option>
              <option :value="20">20 questions</option>
              <option :value="30">30 questions</option>
              <option :value="40">40 questions</option>
              <option :value="50">50 questions</option>
            </select>
            <Settings class="w-4 h-4 text-primary absolute left-3 top-3.5" />
          </div>
        </div>
      </div>

      <!-- Types de ressources -->
      <div>
        <span class="block text-xs font-bold text-ink-subtle dark:text-ink-muted uppercase tracking-widest mb-3">
          Ressources à inclure
        </span>
        <div class="space-y-3">
          <label class="flex items-center gap-3 p-3.5 rounded-xl border-2 transition-all cursor-pointer"
            :class="[includeFlashcards ? 'border-primary bg-primary-soft dark:bg-primary-soft' : 'border-line dark:border-line']"
          >
            <input 
              v-model="includeFlashcards" 
              type="checkbox"
              class="rounded border-line text-primary focus:ring-primary"
            />
            <div>
              <p class="text-sm font-bold text-ink dark:text-ink-subtle">Cartes Mémoires (Flashcards)</p>
              <p class="text-[11px] text-ink-subtle dark:text-ink-muted">Mélange de vos cartes dues ou prêtes du classeur</p>
            </div>
          </label>

          <label class="flex items-center gap-3 p-3.5 rounded-xl border-2 transition-all cursor-pointer"
            :class="[includeQcm ? 'border-primary bg-primary-soft dark:bg-primary-soft' : 'border-line dark:border-line']"
          >
            <input 
              v-model="includeQcm" 
              type="checkbox"
              class="rounded border-line text-primary focus:ring-primary"
            />
            <div>
              <p class="text-sm font-bold text-ink dark:text-ink-subtle">Questions de QCM (IA)</p>
              <p class="text-[11px] text-ink-subtle dark:text-ink-muted">Intègre les questions générées à partir de vos fiches de cours</p>
            </div>
          </label>
        </div>
      </div>

      <!-- Erreur -->
      <div v-if="errorMsg" class="p-4 bg-danger-soft dark:bg-danger-soft border border-danger dark:border-danger text-danger dark:text-danger rounded-2xl text-xs leading-relaxed">
        {{ errorMsg }}
      </div>

      <!-- Bouton Lancement -->
      <button
        @click="handleStart"
        :disabled="loading || !binderId"
        class="w-full inline-flex items-center justify-center gap-2 px-6 py-4 bg-primary hover:bg-primary-strong text-white rounded-2xl font-bold shadow-lg shadow-elev-primary disabled:opacity-50 disabled:pointer-events-none active:scale-98 transition-all"
      >
        <Sparkles class="w-5 h-5 animate-pulse" />
        Lancer la session d'examen
      </button>

    </div>
  </div>
</template>
