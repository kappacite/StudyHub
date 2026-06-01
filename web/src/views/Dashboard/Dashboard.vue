<template>
  <div class="space-y-8 animate-fade-in">
    <!-- Welcome section -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 bg-gradient-to-r from-indigo-500/10 via-purple-500/5 to-transparent border border-indigo-500/10 rounded-3xl dark:from-indigo-950/20 dark:border-indigo-900/30">
      <div>
        <h1 class="text-2xl font-bold tracking-tight">Ravi de te revoir, {{ authStore.user?.username }} ! 👋</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Prêt pour une nouvelle session d'apprentissage aujourd'hui ?</p>
      </div>
      <div class="flex items-center gap-3">
        <!-- Streak display -->
        <div class="flex items-center gap-2 px-4 py-2 bg-amber-50 dark:bg-amber-950/30 border border-amber-100 dark:border-amber-900/50 rounded-2xl">
          <Flame class="w-5 h-5 text-amber-500 fill-amber-500 animate-pulse" />
          <div>
            <p class="text-xs font-semibold uppercase tracking-wider text-amber-600 dark:text-amber-400">Série d'étude</p>
            <p class="text-sm font-bold leading-none">5 Jours de suite</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick stats widgets -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <div 
        v-for="stat in stats" 
        :key="stat.title"
        class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-2xl p-5 shadow-sm flex items-center gap-4 transition-transform hover:-translate-y-1 duration-200"
      >
        <div class="w-12 h-12 rounded-xl flex items-center justify-center" :class="stat.bg">
          <component :is="stat.icon" class="w-6 h-6" :class="stat.color" />
        </div>
        <div>
          <p class="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">{{ stat.title }}</p>
          <p class="text-xl font-bold mt-0.5">{{ stat.value }}</p>
        </div>
      </div>
    </div>

    <!-- Main Dashboard Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Heatmap / Goal Tracker (Left & Middle columns) -->
      <div class="lg:col-span-2 space-y-8">
        <!-- Heatmap -->
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm">
          <div class="flex items-center justify-between mb-6">
            <h3 class="font-bold text-slate-800 dark:text-white flex items-center gap-2">
              <Calendar class="w-5 h-5 text-indigo-500" />
              Activité d'étude (365 jours)
            </h3>
            <span class="text-xs font-semibold text-slate-400">Total : 142 sessions</span>
          </div>
          
          <!-- Heatmap grid simulation -->
          <div class="overflow-x-auto pb-2">
            <div class="flex flex-col gap-1 min-w-[620px]">
              <div class="flex gap-1" v-for="row in 7" :key="row">
                <!-- Row header (day name) -->
                <div class="w-8 text-[10px] text-slate-400 dark:text-slate-500 flex items-center font-medium">
                  {{ dayNames[row - 1] }}
                </div>
                <!-- Box cells -->
                <div 
                  v-for="col in 52" 
                  :key="col" 
                  class="w-3.5 h-3.5 rounded-sm transition-colors duration-200 hover:scale-125 cursor-pointer"
                  :class="getCellColor(row, col)"
                  :title="`Jour ${col}, Valeur: ${getCellValue(row, col)} sessions`"
                ></div>
              </div>
            </div>
            <div class="flex items-center justify-end gap-1.5 mt-4 text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
              <span>Moins</span>
              <div class="w-3 h-3 rounded-sm bg-slate-100 dark:bg-slate-800"></div>
              <div class="w-3 h-3 rounded-sm bg-indigo-200 dark:bg-indigo-900/50"></div>
              <div class="w-3 h-3 rounded-sm bg-indigo-400 dark:bg-indigo-700"></div>
              <div class="w-3 h-3 rounded-sm bg-indigo-600 dark:bg-indigo-500"></div>
              <span>Plus</span>
            </div>
          </div>
        </div>

        <!-- Weekly goals -->
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm">
          <h3 class="font-bold text-slate-800 dark:text-white flex items-center gap-2 mb-6">
            <Sparkles class="w-5 h-5 text-indigo-500" />
            Objectif Hebdomadaire
          </h3>
          <div class="space-y-4">
            <div class="flex items-center justify-between text-sm">
              <span class="font-semibold">Temps d'étude hebdo</span>
              <span class="text-slate-500 dark:text-slate-400 font-medium">3.5h / 5h</span>
            </div>
            <div class="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-3 overflow-hidden">
              <div class="bg-gradient-to-r from-indigo-500 to-purple-600 h-full rounded-full" style="width: 70%"></div>
            </div>
            <p class="text-xs text-slate-400">Plus que 1.5h pour atteindre ton objectif de la semaine ! Tu y es presque.</p>
          </div>
        </div>
      </div>

      <!-- Quick actions / Recent Decks (Right column) -->
      <div class="space-y-8">
        <!-- Quick Actions -->
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm">
          <h3 class="font-bold text-slate-800 dark:text-white flex items-center gap-2 mb-6">
            <Activity class="w-5 h-5 text-indigo-500" />
            Actions rapides
          </h3>
          <div class="grid grid-cols-2 gap-4">
            <button 
              @click="router.push('/notes')" 
              class="flex flex-col items-center justify-center p-4 bg-slate-50 hover:bg-indigo-50/50 dark:bg-slate-800/40 dark:hover:bg-indigo-950/20 border border-slate-100 dark:border-slate-800 rounded-2xl text-center transition-colors group"
            >
              <FileText class="w-6 h-6 text-indigo-500 group-hover:scale-110 transition-transform" />
              <span class="text-xs font-semibold mt-2">Créer Note</span>
            </button>
            <button 
              @click="router.push('/decks')" 
              class="flex flex-col items-center justify-center p-4 bg-slate-50 hover:bg-indigo-50/50 dark:bg-slate-800/40 dark:hover:bg-indigo-950/20 border border-slate-100 dark:border-slate-800 rounded-2xl text-center transition-colors group"
            >
              <Layers class="w-6 h-6 text-indigo-500 group-hover:scale-110 transition-transform" />
              <span class="text-xs font-semibold mt-2">Réviser Deck</span>
            </button>
            <button 
              @click="router.push('/pdfs')" 
              class="flex flex-col items-center justify-center p-4 bg-slate-50 hover:bg-indigo-50/50 dark:bg-slate-800/40 dark:hover:bg-indigo-950/20 border border-slate-100 dark:border-slate-800 rounded-2xl text-center transition-colors group"
            >
              <FileDown class="w-6 h-6 text-indigo-500 group-hover:scale-110 transition-transform" />
              <span class="text-xs font-semibold mt-2">Importer PDF</span>
            </button>
            <button 
              @click="router.push('/diagrams')" 
              class="flex flex-col items-center justify-center p-4 bg-slate-50 hover:bg-indigo-50/50 dark:bg-slate-800/40 dark:hover:bg-indigo-950/20 border border-slate-100 dark:border-slate-800 rounded-2xl text-center transition-colors group"
            >
              <Activity class="w-6 h-6 text-indigo-500 group-hover:scale-110 transition-transform" />
              <span class="text-xs font-semibold mt-2">Nouveau Schéma</span>
            </button>
          </div>
        </div>

        <!-- Recent review / Decks Study list -->
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm">
          <h3 class="font-bold text-slate-800 dark:text-white flex items-center gap-2 mb-4">
            <Layers class="w-5 h-5 text-indigo-500" />
            Révisions requises
          </h3>
          
          <div class="space-y-4">
            <div 
              v-for="deck in dueDecks" 
              :key="deck.id"
              class="flex items-center justify-between p-3 rounded-2xl bg-slate-50 dark:bg-slate-800/30 border border-slate-100 dark:border-slate-800"
            >
              <div>
                <p class="text-sm font-bold truncate max-w-[140px]">{{ deck.name }}</p>
                <p class="text-[11px] text-indigo-500 dark:text-indigo-400 font-semibold uppercase tracking-wider mt-0.5">
                  {{ deck.due_count }} carte(s) à réviser
                </p>
              </div>
              <button 
                @click="router.push(`/decks/${deck.id}/study`)"
                class="px-3.5 py-1.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl transition-all"
              >
                Réviser
              </button>
            </div>
            
            <div v-if="dueDecks.length === 0" class="text-center py-6 text-slate-400 text-xs font-semibold uppercase tracking-wider">
              Tout est à jour ! 🎉
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useDecksStore } from '../../stores/decks'
import { 
  Flame, 
  Clock, 
  CheckCircle2, 
  Layers, 
  Calendar, 
  Sparkles, 
  Activity, 
  FileText, 
  FileDown 
} from '@lucide/vue'

const authStore = useAuthStore()
const decksStore = useDecksStore()
const router = useRouter()

const dayNames = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam']

const stats = [
  { title: 'Cartes révisées', value: '42', icon: CheckCircle2, bg: 'bg-emerald-50 dark:bg-emerald-950/20', color: 'text-emerald-500' },
  { title: 'Taux de réussite', value: '91%', icon: Sparkles, bg: 'bg-indigo-50 dark:bg-indigo-950/20', color: 'text-indigo-500' },
  { title: 'Temps d\'étude', value: '18h 45m', icon: Clock, bg: 'bg-purple-50 dark:bg-purple-950/20', color: 'text-purple-500' },
  { title: 'Decks actifs', value: computed(() => decksStore.decks.length.toString()), icon: Layers, bg: 'bg-amber-50 dark:bg-amber-950/20', color: 'text-amber-500' }
]

// Simulate due decks count
const dueDecks = computed(() => {
  return decksStore.decks.map(deck => {
    // Simulated count
    const count = deck.id === 1 ? 2 : deck.id === 2 ? 2 : 1
    return {
      ...deck,
      due_count: count
    }
  }).filter(d => d.due_count > 0)
})

// Simulated cell data for heatmap (value from 0 to 4)
const heatmapData = ref<Record<string, number>>({})

function getCellColor(row: number, col: number) {
  const hash = `${row}-${col}`
  if (!heatmapData.value[hash]) {
    // Generate static values based on row/col for illustration
    heatmapData.value[hash] = Math.floor(Math.sin((row * col) / 10) * 2.5 + 2)
  }
  
  const val = heatmapData.value[hash]
  if (val <= 0) return 'bg-slate-100 dark:bg-slate-800'
  if (val === 1) return 'bg-indigo-100 dark:bg-indigo-950/40 text-indigo-400'
  if (val === 2) return 'bg-indigo-300 dark:bg-indigo-800 text-indigo-300'
  if (val === 3) return 'bg-indigo-500 dark:bg-indigo-600 text-indigo-100'
  return 'bg-indigo-700 dark:bg-indigo-400 text-white'
}

function getCellValue(row: number, col: number) {
  const hash = `${row}-${col}`
  return heatmapData.value[hash] || 0
}
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
