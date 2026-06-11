<template>
  <div class="grid grid-cols-1 md:grid-cols-7 gap-4">
    <div 
      v-for="day in days" 
      :key="day.date"
      class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-2xl p-4 flex flex-col min-h-[300px] shadow-sm hover:shadow-md transition-all duration-200"
    >
      <!-- Date header -->
      <div class="text-center pb-3 border-b border-slate-50 dark:border-slate-800/50">
        <p class="text-[10px] font-bold text-slate-400 dark:text-slate-550 uppercase tracking-widest">
          {{ formatDayName(day.date) }}
        </p>
        <p class="text-lg font-black text-slate-800 dark:text-white mt-0.5">
          {{ formatDateNum(day.date) }}
        </p>
      </div>

      <!-- Load indicator bar -->
      <div class="mt-4">
        <div class="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">
          <span>Charge</span>
          <span :class="getLoadTextColor(day.total_due)">{{ day.total_due }} carte(s)</span>
        </div>
        <div class="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden flex">
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
          class="flex items-center justify-between text-xs p-2 rounded-xl bg-slate-50/50 dark:bg-slate-800/40 border border-slate-100/50 dark:border-slate-800/30 group hover:bg-slate-50 dark:hover:bg-slate-800/60 transition-all"
        >
          <span class="font-bold text-slate-700 dark:text-slate-300 truncate max-w-[80px]" :title="item.deck_name">
            {{ item.deck_name }}
          </span>
          <span class="px-1.5 py-0.5 rounded-lg text-[9px] font-bold bg-indigo-50 dark:bg-indigo-950/40 text-indigo-500 dark:text-indigo-400 border border-indigo-150/10 dark:border-indigo-400/10">
            {{ item.count }}
          </span>
        </div>

        <div 
          v-if="day.breakdown.length === 0" 
          class="flex flex-col items-center justify-center h-28 text-center text-slate-350 dark:text-slate-650"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6 opacity-60">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 0 1-1.043 3.296 3.745 3.745 0 0 1-3.296 1.043A3.745 3.745 0 0 1 12 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 0 1-3.296-1.043 3.745 3.745 0 0 1-1.043-3.296A3.745 3.745 0 0 1 3 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 0 1 1.043-3.296 3.746 3.746 0 0 1 3.296-1.043A3.746 3.746 0 0 1 12 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 0 1 3.296 1.043 3.746 3.746 0 0 1 1.043 3.296A3.745 3.745 0 0 1 21 12Z" />
          </svg>
          <span class="text-[9px] font-bold uppercase tracking-wider mt-1">Libre</span>
        </div>
      </div>

      <!-- Action button for advance review (only if day is future and has cards) -->
      <div class="mt-4 pt-2 border-t border-slate-50 dark:border-slate-800/40" v-if="day.total_due > 0 && isFutureDay(day.date)">
        <button 
          @click="$emit('select-day', day)"
          class="w-full py-1.5 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:text-slate-350 dark:hover:bg-slate-850 rounded-xl text-[10px] font-bold text-slate-700 active:scale-95 transition-all flex items-center justify-center gap-1"
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
  if (count === 0) return 'text-slate-400 dark:text-slate-500'
  if (count < 10) return 'text-emerald-500'
  if (count <= 25) return 'text-amber-500'
  return 'text-rose-500'
}

function getLoadBarColor(count: number): string {
  if (count === 0) return 'bg-slate-200 dark:bg-slate-700'
  if (count < 10) return 'bg-emerald-500'
  if (count <= 25) return 'bg-amber-500'
  return 'bg-rose-500'
}
</script>
