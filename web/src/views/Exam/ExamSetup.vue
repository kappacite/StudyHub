<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBindersStore } from '../../stores/binders'
import examService from '../../services/examService'
import { ShieldAlert, Clock, Settings, Sparkles } from 'lucide-vue-next'

const router = useRouter()
const bindersStore = useBindersStore()

const binderId = ref<number | null>(null)
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
      <div class="inline-flex p-3 bg-indigo-50 dark:bg-indigo-950/45 rounded-2xl text-indigo-600 dark:text-indigo-400 mb-3 shadow-md shadow-indigo-500/5">
        <ShieldAlert class="w-8 h-8" />
      </div>
      <h1 class="text-2xl font-black text-slate-800 dark:text-white">Simulateur de Mode Examen</h1>
      <p class="text-sm text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
        Évaluez-vous dans des conditions réelles. Un mélange chronométré de vos cartes mémoires et de vos questions de QCM sans aucun accès aux fiches de révision.
      </p>
    </div>

    <!-- Form -->
    <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-8 shadow-sm space-y-6">
      
      <!-- Classeur cible -->
      <div>
        <label class="block text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-2">
          Classeur d'examen
        </label>
        <select
          v-model="binderId"
          class="w-full bg-slate-50 border border-slate-200 dark:bg-slate-950 dark:border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option v-for="b in bindersStore.binders" :key="b.id" :value="b.id">
            📁 {{ b.name }}
          </option>
        </select>
        <p class="text-[10px] text-slate-400 dark:text-slate-500 mt-1.5">
          L'examen piochera dans ce classeur et l'ensemble de ses sous-classeurs.
        </p>
      </div>

      <!-- Durée & Limites -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-2">
            Durée maximum
          </label>
          <div class="relative">
            <select
              v-model.number="durationMinutes"
              class="w-full bg-slate-50 border border-slate-200 dark:bg-slate-950 dark:border-slate-800 rounded-xl pl-9 pr-4 py-3 text-sm text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option :value="15">15 min</option>
              <option :value="30">30 min</option>
              <option :value="45">45 min</option>
              <option :value="60">1 heure</option>
              <option :value="90">1h30</option>
              <option :value="120">2 heures</option>
            </select>
            <Clock class="w-4 h-4 text-indigo-500 absolute left-3 top-3.5" />
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-2">
            Limite de questions
          </label>
          <div class="relative">
            <select
              v-model.number="questionLimit"
              class="w-full bg-slate-50 border border-slate-200 dark:bg-slate-950 dark:border-slate-800 rounded-xl pl-9 pr-4 py-3 text-sm text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option :value="10">10 questions</option>
              <option :value="20">20 questions</option>
              <option :value="30">30 questions</option>
              <option :value="40">40 questions</option>
              <option :value="50">50 questions</option>
            </select>
            <Settings class="w-4 h-4 text-indigo-500 absolute left-3 top-3.5" />
          </div>
        </div>
      </div>

      <!-- Types de ressources -->
      <div>
        <span class="block text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-3">
          Ressources à inclure
        </span>
        <div class="space-y-3">
          <label class="flex items-center gap-3 p-3.5 rounded-xl border-2 transition-all cursor-pointer"
            :class="[includeFlashcards ? 'border-indigo-500/30 bg-indigo-50/10 dark:bg-indigo-950/5' : 'border-slate-100 dark:border-slate-850']"
          >
            <input 
              v-model="includeFlashcards" 
              type="checkbox"
              class="rounded border-slate-350 text-indigo-600 focus:ring-indigo-500"
            />
            <div>
              <p class="text-sm font-bold text-slate-700 dark:text-slate-200">Cartes Mémoires (Flashcards)</p>
              <p class="text-[11px] text-slate-400 dark:text-slate-500">Mélange de vos cartes dues ou prêtes du classeur</p>
            </div>
          </label>

          <label class="flex items-center gap-3 p-3.5 rounded-xl border-2 transition-all cursor-pointer"
            :class="[includeQcm ? 'border-indigo-500/30 bg-indigo-50/10 dark:bg-indigo-950/5' : 'border-slate-100 dark:border-slate-850']"
          >
            <input 
              v-model="includeQcm" 
              type="checkbox"
              class="rounded border-slate-350 text-indigo-600 focus:ring-indigo-500"
            />
            <div>
              <p class="text-sm font-bold text-slate-700 dark:text-slate-200">Questions de QCM (IA)</p>
              <p class="text-[11px] text-slate-400 dark:text-slate-500">Intègre les questions générées à partir de vos fiches de cours</p>
            </div>
          </label>
        </div>
      </div>

      <!-- Erreur -->
      <div v-if="errorMsg" class="p-4 bg-rose-50/50 dark:bg-rose-950/10 border border-rose-250 dark:border-rose-950/20 text-rose-800 dark:text-rose-400 rounded-2xl text-xs leading-relaxed">
        {{ errorMsg }}
      </div>

      <!-- Bouton Lancement -->
      <button
        @click="handleStart"
        :disabled="loading || !binderId"
        class="w-full inline-flex items-center justify-center gap-2 px-6 py-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl font-bold shadow-lg shadow-indigo-600/15 disabled:opacity-50 disabled:pointer-events-none active:scale-98 transition-all"
      >
        <Sparkles class="w-5 h-5 animate-pulse" />
        Lancer la session d'examen
      </button>

    </div>
  </div>
</template>
