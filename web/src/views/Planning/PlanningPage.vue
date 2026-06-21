<template>
  <PageContainer size="wide">
    <PageHeader
      title="Planning des révisions"
      subtitle="Consultez la charge de vos révisions à venir et lissez votre travail grâce aux révisions anticipées."
    >
      <template #actions>
        <div class="flex flex-wrap items-center gap-2">
          <!-- Bascule Semaine / Mois -->
          <div class="flex p-1 bg-surface-soft border border-line rounded-full gap-1">
            <button
              @click="setViewMode('week')"
              class="px-4 py-1.5 rounded-full text-xs font-bold transition-colors"
              :class="viewMode === 'week' ? 'bg-primary text-white shadow-elev-primary' : 'text-ink-muted hover:text-ink'"
            >Semaine</button>
            <button
              @click="setViewMode('month')"
              class="px-4 py-1.5 rounded-full text-xs font-bold transition-colors"
              :class="viewMode === 'month' ? 'bg-primary text-white shadow-elev-primary' : 'text-ink-muted hover:text-ink'"
            >Mois</button>
          </div>

          <BaseButton variant="secondary" size="sm" @click="goToToday">Aujourd'hui</BaseButton>

          <!-- Navigation période -->
          <div class="flex items-center border border-line rounded-full overflow-hidden bg-surface">
            <button @click="navigatePeriod(-1)" class="p-2 hover:bg-surface-soft text-ink-muted transition-colors" title="Précédent">
              <ChevronLeft class="w-4 h-4" />
            </button>
            <div class="px-3 text-xs font-bold text-ink border-x border-line min-w-[120px] text-center">{{ dateLabel }}</div>
            <button @click="navigatePeriod(1)" class="p-2 hover:bg-surface-soft text-ink-muted transition-colors" title="Suivant">
              <ChevronRight class="w-4 h-4" />
            </button>
          </div>
        </div>
      </template>
    </PageHeader>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      <!-- Calendrier (9 colonnes) -->
      <div class="lg:col-span-9 space-y-6">
        <BaseCard v-if="planningStore.loading" class="flex flex-col items-center justify-center py-24 gap-3">
          <svg class="animate-spin h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span class="text-sm font-semibold text-ink-subtle uppercase tracking-widest">Calcul de votre charge d'étude...</span>
        </BaseCard>

        <div v-else-if="planningStore.error" class="p-6 bg-danger-soft border border-danger/30 rounded-3xl text-danger">
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

      <!-- Résumé & guide (3 colonnes) -->
      <div class="lg:col-span-3 space-y-6">
        <BaseCard class="space-y-6">
          <h3 class="font-bold text-sm text-ink uppercase tracking-wider flex items-center gap-2">
            <BarChart3 class="w-4 h-4 text-primary" />
            Résumé de la période
          </h3>

          <div class="space-y-4">
            <div class="p-4 bg-surface-soft rounded-2xl border border-line">
              <span class="text-[10px] font-bold text-ink-subtle uppercase tracking-wider block">Total à réviser</span>
              <span class="text-2xl font-black text-ink mt-1 block">
                {{ totalPeriodCards }} <span class="text-xs font-semibold text-ink-subtle">cartes</span>
              </span>
            </div>

            <div class="p-4 bg-surface-soft rounded-2xl border border-line">
              <span class="text-[10px] font-bold text-ink-subtle uppercase tracking-wider block">Jour de pic maximal</span>
              <span class="text-sm font-black text-ink mt-1.5 block truncate" v-if="peakDay">
                {{ formatPeakDayDate(peakDay.date) }}
              </span>
              <span class="text-xs font-semibold text-danger mt-0.5 block" v-if="peakDay">
                {{ peakDay.total_due }} cartes prévues
              </span>
              <span class="text-xs font-semibold text-ink-subtle block mt-1" v-else>
                Aucune carte prévue
              </span>
            </div>
          </div>
        </BaseCard>

        <div class="bg-gradient-to-tr from-primary to-primary-strong text-white rounded-3xl p-6 shadow-elev-primary space-y-4">
          <div class="w-10 h-10 bg-white/15 rounded-xl flex items-center justify-center">
            <Flame class="w-5 h-5 fill-white" />
          </div>
          <div>
            <h4 class="font-extrabold text-sm uppercase tracking-wider">Révisions Anticipées</h4>
            <p class="text-[11px] leading-relaxed text-white/85 mt-2">
              L'algorithme SM-2 calcule vos rappels de façon optimale. Cependant, si vous prévoyez une journée chargée (examens, déplacements), vous pouvez anticiper et étudier vos cartes en avance.
            </p>
            <p class="text-[11px] leading-relaxed text-white/85 mt-2 font-semibold italic">
              Remarque : Réviser en avance réinitialisera l'intervalle d'apprentissage à partir d'aujourd'hui.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Modale : révision anticipée -->
    <BaseModal
      :open="!!selectedDayForModal"
      :title="selectedDayForModal ? formatModalDate(selectedDayForModal.date) : ''"
      @close="closeAdvanceReviewModal"
    >
      <template v-if="selectedDayForModal">
        <p class="text-[10px] font-bold text-primary uppercase tracking-widest -mt-2">Révision Anticipée</p>
        <p class="text-[11px] text-ink-subtle mt-1 mb-4">
          Sélectionnez un deck ci-dessous pour étudier en avance les cartes prévues ce jour-là.
        </p>
        <div class="space-y-3 max-h-[260px] overflow-y-auto pr-1">
          <div
            v-for="item in selectedDayForModal.breakdown"
            :key="item.deck_id"
            class="flex items-center justify-between p-3 border border-line rounded-2xl hover:bg-surface-soft transition-colors"
          >
            <div class="min-w-0">
              <p class="font-bold text-xs text-ink truncate">{{ item.deck_name }}</p>
              <p class="text-[10px] text-ink-subtle mt-0.5">{{ item.count }} carte(s) prévue(s)</p>
            </div>
            <BaseButton size="sm" @click="studyDeckAdvance(item.deck_id, selectedDayForModal!.date)">
              Réviser
              <ArrowRight class="w-3 h-3" />
            </BaseButton>
          </div>
        </div>
      </template>
    </BaseModal>
  </PageContainer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePlanningStore } from '../../stores/planning'
import type { PlanningDay } from '../../services/planningService'
import WeekCalendar from '../../components/planning/WeekCalendar.vue'
import MonthCalendar from '../../components/planning/MonthCalendar.vue'
import { PageContainer, PageHeader, BaseButton, BaseCard, BaseModal } from '../../components/ui/base'
import {
  ChevronLeft,
  ChevronRight,
  BarChart3,
  Flame,
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
