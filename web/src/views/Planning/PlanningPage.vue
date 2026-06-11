<template>
  <div class="space-y-8 animate-fade-in">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
      <div>
        <h1 class="text-xl font-bold">Planning des révisions</h1>
        <p class="text-xs text-slate-400 dark:text-slate-500 mt-1">
          Consultez la charge de vos révisions à venir et lissez votre travail grâce aux révisions anticipées.
        </p>
      </div>

      <!-- View Toggle & Date Navigation -->
      <div class="flex flex-wrap items-center gap-3">
        <!-- Week/Month Toggle -->
        <div class="bg-slate-100 dark:bg-slate-800 p-0.5 rounded-xl flex">
          <button 
            @click="setViewMode('week')"
            class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all"
            :class="viewMode === 'week' ? 'bg-white dark:bg-slate-700 shadow-sm text-indigo-600 dark:text-indigo-400' : 'text-slate-500 dark:text-slate-450 hover:text-slate-700'"
          >
            Semaine
          </button>
          <button 
            @click="setViewMode('month')"
            class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all"
            :class="viewMode === 'month' ? 'bg-white dark:bg-slate-700 shadow-sm text-indigo-600 dark:text-indigo-400' : 'text-slate-500 dark:text-slate-450 hover:text-slate-700'"
          >
            Mois
          </button>
        </div>

        <!-- Today Button -->
        <button 
          @click="goToToday"
          class="px-3 py-1.5 bg-slate-50 border border-slate-200 dark:bg-slate-800 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-750 text-xs font-bold rounded-xl active:scale-95 transition-all"
        >
          Aujourd'hui
        </button>

        <!-- Navigation Buttons -->
        <div class="flex items-center border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden bg-white dark:bg-slate-900">
          <button 
            @click="navigatePeriod(-1)"
            class="p-2 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 transition-colors"
            title="Précédent"
          >
            <ChevronLeft class="w-4 h-4" />
          </button>
          <div class="px-3 text-xs font-bold text-slate-700 dark:text-slate-300 border-x border-slate-200 dark:border-slate-700 min-w-[120px] text-center">
            {{ dateLabel }}
          </div>
          <button 
            @click="navigatePeriod(1)"
            class="p-2 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 transition-colors"
            title="Suivant"
          >
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      <!-- Calendar Area (9 columns) -->
      <div class="lg:col-span-9 space-y-6">
        <div v-if="planningStore.loading" class="flex flex-col items-center justify-center py-24 gap-3 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl shadow-sm">
          <svg class="animate-spin h-8 w-8 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span class="text-sm font-semibold text-slate-400 uppercase tracking-widest">Calcul de votre charge d'étude...</span>
        </div>

        <div v-else-if="planningStore.error" class="p-6 bg-rose-50 border border-rose-100 rounded-3xl dark:bg-rose-950/20 dark:border-rose-900/30 text-rose-600 dark:text-rose-400">
          <p class="font-semibold">{{ planningStore.error }}</p>
        </div>

        <div v-else>
          <WeekCalendar 
            v-if="viewMode === 'week'"
            :days="planningStore.calendarDays"
            @select-day="openAdvanceReviewModal"
          />
          <MonthCalendar 
            v-else
            :days="planningStore.calendarDays"
            @select-day="openAdvanceReviewModal"
          />
        </div>
      </div>

      <!-- Stats & Summary Sidebar (3 columns) -->
      <div class="lg:col-span-3 space-y-6">
        <!-- Range Summary Card -->
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm space-y-6">
          <h3 class="font-bold text-sm text-slate-800 dark:text-white uppercase tracking-wider flex items-center gap-2">
            <BarChart3 class="w-4 h-4 text-indigo-500" />
            Résumé de la période
          </h3>

          <div class="space-y-4">
            <!-- Total count metric -->
            <div class="p-4 bg-slate-50/50 dark:bg-slate-800/30 rounded-2xl border border-slate-100/50 dark:border-slate-800/30">
              <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Total à réviser</span>
              <span class="text-2xl font-black text-slate-800 dark:text-white mt-1 block">
                {{ totalPeriodCards }} <span class="text-xs font-semibold text-slate-400">cartes</span>
              </span>
            </div>

            <!-- Peak load day metric -->
            <div class="p-4 bg-slate-50/50 dark:bg-slate-800/30 rounded-2xl border border-slate-100/50 dark:border-slate-800/30">
              <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Jour de pic maximal</span>
              <span class="text-sm font-black text-slate-850 dark:text-slate-200 mt-1.5 block truncate" v-if="peakDay">
                {{ formatPeakDayDate(peakDay.date) }}
              </span>
              <span class="text-xs font-semibold text-rose-500 mt-0.5 block" v-if="peakDay">
                {{ peakDay.total_due }} cartes prévues
              </span>
              <span class="text-xs font-semibold text-slate-450 dark:text-slate-550 block mt-1" v-else>
                Aucune carte prévue
              </span>
            </div>
          </div>
        </div>

        <!-- Info/Guide Card -->
        <div class="bg-gradient-to-tr from-indigo-500 to-purple-600 text-white rounded-3xl p-6 shadow-lg shadow-indigo-500/15 space-y-4">
          <div class="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center">
            <Flame class="w-5 h-5 fill-white" />
          </div>
          <div>
            <h4 class="font-extrabold text-sm uppercase tracking-wider">Révisions Anticipées</h4>
            <p class="text-[11px] leading-relaxed text-indigo-100 mt-2">
              L'algorithme SM-2 calcule vos rappels de façon optimale. Cependant, si vous prévoyez une journée chargée (examens, déplacements), vous pouvez anticiper et étudier vos cartes en avance.
            </p>
            <p class="text-[11px] leading-relaxed text-indigo-100 mt-2 font-semibold italic">
              Remarque : Réviser en avance réinitialisera l'intervalle d'apprentissage à partir d'aujourd'hui.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Advance Review Popup Modal -->
    <transition name="fade-modal">
      <div 
        v-if="selectedDayForModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/40 backdrop-blur-sm"
        @click="closeAdvanceReviewModal"
      >
        <div 
          class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl w-full max-w-md p-6 shadow-2xl relative animate-scale-up"
          @click.stop
        >
          <!-- Close button -->
          <button 
            @click="closeAdvanceReviewModal"
            class="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 transition-all"
          >
            <X class="w-5 h-5" />
          </button>

          <!-- Modal Header -->
          <div class="space-y-1 pr-8">
            <span class="text-[10px] font-bold text-indigo-500 uppercase tracking-widest">Révision Anticipée</span>
            <h3 class="text-base font-black text-slate-800 dark:text-white">
              {{ formatModalDate(selectedDayForModal.date) }}
            </h3>
            <p class="text-[11px] text-slate-400 dark:text-slate-500">
              Sélectionnez un deck ci-dessous pour étudier en avance les cartes prévues ce jour-là.
            </p>
          </div>

          <!-- Decks list -->
          <div class="mt-6 space-y-3 max-h-[260px] overflow-y-auto pr-1">
            <div 
              v-for="item in selectedDayForModal.breakdown" 
              :key="item.deck_id"
              class="flex items-center justify-between p-3 border border-slate-100 dark:border-slate-800 rounded-2xl hover:border-slate-200 dark:hover:border-slate-700/80 transition-all"
            >
              <div class="min-w-0">
                <p class="font-bold text-xs text-slate-800 dark:text-white truncate">
                  {{ item.deck_name }}
                </p>
                <p class="text-[10px] text-slate-450 dark:text-slate-500 mt-0.5">
                  {{ item.count }} carte(s) prévue(s)
                </p>
              </div>
              <button 
                @click="studyDeckAdvance(item.deck_id, selectedDayForModal!.date)"
                class="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-[10px] font-bold active:scale-95 transition-all shadow-md shadow-indigo-600/10 flex items-center gap-1"
              >
                <span>Réviser</span>
                <ArrowRight class="w-3 h-3 text-white" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePlanningStore } from '../../stores/planning'
import type { PlanningDay } from '../../services/planningService'
import WeekCalendar from '../../components/planning/WeekCalendar.vue'
import MonthCalendar from '../../components/planning/MonthCalendar.vue'
import { 
  ChevronLeft, 
  ChevronRight, 
  BarChart3, 
  Flame, 
  X, 
  ArrowRight 
} from '@lucide/vue'

const planningStore = usePlanningStore()
const router = useRouter()

const viewMode = ref<'week' | 'month'>('week')
const baseDate = ref(new Date())

const selectedDayForModal = ref<PlanningDay | null>(null)

// Format standard date helper
function formatDateForApi(dateObj: Date): string {
  const y = dateObj.getFullYear()
  const m = String(dateObj.getMonth() + 1).padStart(2, '0')
  const d = String(dateObj.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

// Calculate Sunday/Monday for Week view
function getMonday(d: Date): Date {
  const dateObj = new Date(d)
  const day = dateObj.getDay()
  // diff: if day is sunday(0), subtract 6, otherwise subtract day-1
  const diff = dateObj.getDate() - day + (day === 0 ? -6 : 1)
  const monday = new Date(dateObj.setDate(diff))
  monday.setHours(0, 0, 0, 0)
  return monday
}

// Get the date range for queries
const currentRange = computed(() => {
  if (viewMode.value === 'week') {
    const monday = getMonday(baseDate.value)
    const sunday = new Date(monday)
    sunday.setDate(monday.getDate() + 6)
    sunday.setHours(23, 59, 59, 999)
    return { from: monday, to: sunday }
  } else {
    const from = new Date(baseDate.value.getFullYear(), baseDate.value.getMonth(), 1)
    const to = new Date(baseDate.value.getFullYear(), baseDate.value.getMonth() + 1, 0)
    to.setHours(23, 59, 59, 999)
    return { from, to }
  }
})

// Visual label for period navigation
const dateLabel = computed(() => {
  const { from, to } = currentRange.value
  if (viewMode.value === 'week') {
    const options: Intl.DateTimeFormatOptions = { day: 'numeric', month: 'short' }
    return `${from.toLocaleDateString('fr-FR', options)} - ${to.toLocaleDateString('fr-FR', options)}`
  } else {
    return from.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })
  }
})

// Period calculations
const totalPeriodCards = computed(() => {
  return planningStore.calendarDays.reduce((acc, curr) => acc + curr.total_due, 0)
})

const peakDay = computed(() => {
  if (planningStore.calendarDays.length === 0) return null
  return planningStore.calendarDays.reduce((max, day) => day.total_due > max.total_due ? day : max, planningStore.calendarDays[0])
})

async function loadPlanning() {
  const { from, to } = currentRange.value
  await planningStore.fetchCalendar(formatDateForApi(from), formatDateForApi(to))
}

onMounted(async () => {
  await loadPlanning()
})

// UI Interaction methods
async function setViewMode(mode: 'week' | 'month') {
  viewMode.value = mode
  await loadPlanning()
}

async function goToToday() {
  baseDate.value = new Date()
  await loadPlanning()
}

async function navigatePeriod(direction: number) {
  const dateObj = new Date(baseDate.value)
  if (viewMode.value === 'week') {
    dateObj.setDate(dateObj.getDate() + (direction * 7))
  } else {
    dateObj.setMonth(dateObj.getMonth() + direction)
  }
  baseDate.value = dateObj
  await loadPlanning()
}

// Modal management
function openAdvanceReviewModal(day: PlanningDay) {
  selectedDayForModal.value = day
}

function closeAdvanceReviewModal() {
  selectedDayForModal.value = null
}

async function studyDeckAdvance(deckId: number, dateStr: string) {
  try {
    await planningStore.prepareAdvanceReview(deckId, dateStr)
    // Close modal and navigate
    closeAdvanceReviewModal()
    router.push(`/decks/${deckId}/study?advance=true`)
  } catch (err) {
    alert('Erreur lors de la préparation de la révision anticipée.')
  }
}

// Modal/Label formating
function formatPeakDayDate(dateStr: string): string {
  const options: Intl.DateTimeFormatOptions = { weekday: 'short', day: 'numeric', month: 'long' }
  return new Date(dateStr).toLocaleDateString('fr-FR', options)
}

function formatModalDate(dateStr: string): string {
  const options: Intl.DateTimeFormatOptions = { weekday: 'long', day: 'numeric', month: 'long' }
  return new Date(dateStr).toLocaleDateString('fr-FR', options)
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

/* Modal animation */
.fade-modal-enter-active,
.fade-modal-leave-active {
  transition: opacity 0.25s ease;
}

.fade-modal-enter-from,
.fade-modal-leave-to {
  opacity: 0;
}

.animate-scale-up {
  animation: scaleUp 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

@keyframes scaleUp {
  from { transform: scale(0.9) translateY(10px); opacity: 0; }
  to { transform: scale(1) translateY(0); opacity: 1; }
}
</style>
