<template>
  <!-- Grille plafonnée à 4 colonnes : la semaine s'étale sur 2 rangées mais chaque
       carte est nettement plus large (≈1/4 vs 1/7) et donc lisible. -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
    <div
      v-for="day in days"
      :key="day.date"
      class="bg-surface border border-line rounded-2xl p-4 flex flex-col min-h-[300px] shadow-elev-1 hover:shadow-elev-2 transition-all duration-200"
    >
      <!-- Date header -->
      <div class="text-center pb-3 border-b border-line-soft">
        <p class="text-[10px] font-bold text-ink-subtle uppercase tracking-widest">
          {{ formatDayName(day.date) }}
        </p>
        <p class="text-lg font-black text-ink mt-0.5">
          {{ formatDateNum(day.date) }}
        </p>
      </div>

      <!-- Load indicator bar -->
      <div class="mt-4">
        <div class="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider text-ink-subtle mb-1">
          <span>Charge</span>
          <span :class="getLoadTextColor(day.total_due)">{{ day.total_due }} carte(s)</span>
        </div>
        <div class="w-full bg-surface-soft rounded-full h-2 overflow-hidden flex">
          <div
            class="h-full rounded-full transition-all duration-500"
            :class="getLoadBarColor(day.total_due)"
            :style="{ width: Math.min(100, (day.total_due / 35) * 100) + '%' }"
          ></div>
        </div>
      </div>

      <!-- Decks breakdown -->
      <div class="flex-1 mt-4 space-y-2.5 overflow-y-auto max-h-[160px] pr-1">
        <div
          v-for="item in day.breakdown"
          :key="item.deck_id"
          class="flex items-center justify-between text-xs p-2 rounded-xl bg-surface-soft border border-line group hover:bg-surface transition-all"
        >
          <span class="font-bold text-ink-muted truncate flex-1 min-w-0 mr-2" :title="item.deck_name">
            {{ item.deck_name }}
          </span>
          <span class="px-1.5 py-0.5 rounded-lg text-[9px] font-bold bg-primary-soft text-primary">
            {{ item.count }}
          </span>
        </div>

        <div
          v-if="day.breakdown.length === 0"
          class="flex flex-col items-center justify-center h-28 text-center text-ink-subtle"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6 opacity-60">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 0 1-1.043 3.296 3.745 3.745 0 0 1-3.296 1.043A3.745 3.745 0 0 1 12 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 0 1-3.296-1.043 3.745 3.745 0 0 1-1.043-3.296A3.745 3.745 0 0 1 3 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 0 1 1.043-3.296 3.746 3.746 0 0 1 3.296-1.043A3.746 3.746 0 0 1 12 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 0 1 3.296 1.043 3.746 3.746 0 0 1 1.043 3.296A3.745 3.745 0 0 1 21 12Z" />
          </svg>
          <span class="text-[9px] font-bold uppercase tracking-wider mt-1">Libre</span>
        </div>
      </div>

      <!-- Action button for advance review (only if day is future and has cards) -->
      <div class="mt-4 pt-2 border-t border-line-soft" v-if="day.total_due > 0 && isFutureDay(day.date)">
        <button
          @click="$emit('select-day', day)"
          class="w-full py-1.5 border border-line hover:bg-surface-soft rounded-xl text-[10px] font-bold text-ink-muted active:scale-95 transition-all flex items-center justify-center gap-1"
        >
          <span>Révision anticipée</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PlanningDay } from '../../services/planningService'

defineProps<{
  days: PlanningDay[]
}>()

defineEmits<{
  (e: 'select-day', day: PlanningDay): void
}>()

// Helper to check if a day is in the future
function isFutureDay(dateStr: string): boolean {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const queryDate = new Date(dateStr)
  return queryDate > today
}

// Formatting helpers
function formatDayName(dateStr: string): string {
  const date = new Date(dateStr)
  const name = date.toLocaleDateString('fr-FR', { weekday: 'short' })
  return name.replace('.', '')
}

function formatDateNum(dateStr: string): string {
  const date = new Date(dateStr)
  return String(date.getDate())
}

// Load level helpers
function getLoadTextColor(count: number): string {
  if (count === 0) return 'text-ink-subtle'
  if (count < 10) return 'text-success'
  if (count <= 25) return 'text-warning'
  return 'text-danger'
}

function getLoadBarColor(count: number): string {
  if (count === 0) return 'bg-line'
  if (count < 10) return 'bg-success'
  if (count <= 25) return 'bg-warning'
  return 'bg-danger'
}
</script>
