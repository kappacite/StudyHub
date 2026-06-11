<template>
  <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm space-y-6">
    <!-- Grid Header -->
    <div class="grid grid-cols-7 gap-2 text-center text-xs font-black text-slate-400 dark:text-slate-550 uppercase tracking-widest pb-2 border-b border-slate-50 dark:border-slate-800/40">
      <span>Lun</span>
      <span>Mar</span>
      <span>Mer</span>
      <span>Jeu</span>
      <span>Ven</span>
      <span>Sam</span>
      <span>Dim</span>
    </div>

    <!-- Calendar Grid -->
    <div class="grid grid-cols-7 gap-2.5">
      <!-- Padded cells before the first day -->
      <div 
        v-for="p in paddingCells" 
        :key="`pad-${p}`"
        class="aspect-square bg-slate-50/30 dark:bg-slate-800/10 rounded-2xl border border-dashed border-slate-100/50 dark:border-slate-800/10 opacity-30"
      ></div>

      <!-- Real day cells -->
      <div 
        v-for="day in days" 
        :key="day.date"
        class="aspect-square relative flex flex-col justify-between p-2 rounded-2xl border transition-all duration-200 group cursor-pointer"
        :class="[
          isToday(day.date) 
            ? 'border-indigo-500 bg-indigo-500/5 dark:bg-indigo-500/10' 
            : 'border-slate-100 dark:border-slate-800/60 bg-slate-50/10 dark:bg-slate-900',
          day.total_due > 0 ? 'hover:shadow-md' : 'hover:bg-slate-50 dark:hover:bg-slate-800/30'
        ]"
      >
        <!-- Day number -->
        <span 
          class="text-xs font-bold self-end"
          :class="isToday(day.date) ? 'text-indigo-600 dark:text-indigo-400 font-black' : 'text-slate-500 dark:text-slate-400'"
        >
          {{ formatDateNum(day.date) }}
        </span>

        <!-- Heatmap Circle Indicator -->
        <div class="flex justify-center items-center flex-1">
          <div 
            v-if="day.total_due > 0"
            class="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-black shadow-sm transform group-hover:scale-110 transition-all duration-200"
            :class="getLoadClasses(day.total_due)"
          >
            {{ day.total_due }}
          </div>
        </div>

        <!-- Tooltip/Popover on hover -->
        <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-52 bg-slate-950/90 dark:bg-slate-855/95 backdrop-blur-md text-white rounded-2xl p-3 shadow-xl opacity-0 pointer-events-none group-hover:opacity-100 transition-all duration-200 z-30 scale-95 group-hover:scale-100 origin-bottom">
          <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5">
            {{ formatFullDate(day.date) }}
          </p>
          <div class="space-y-1">
            <div 
              v-for="item in day.breakdown" 
              :key="item.deck_id"
              class="flex items-center justify-between text-[11px]"
            >
              <span class="truncate max-w-[120px] font-semibold text-slate-200">{{ item.deck_name }}</span>
              <span class="font-bold text-indigo-400">{{ item.count }} cartes</span>
            </div>
            <div v-if="day.breakdown.length === 0" class="text-[10px] italic text-slate-550">
              Aucune révision prévue.
            </div>
          </div>
          <!-- Tiny footer text inside popover if applicable -->
          <div 
            v-if="day.total_due > 0 && isFutureDay(day.date)" 
            class="mt-2 pt-1.5 border-t border-slate-800 text-[9px] text-indigo-400 font-bold text-center uppercase tracking-wider"
          >
            Cliquer pour réviser tôt
          </div>
        </div>

        <!-- Hidden trigger for click events (selects day if it has cards and is future) -->
        <button 
          v-if="day.total_due > 0 && isFutureDay(day.date)"
          class="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
          @click="$emit('select-day', day)"
        ></button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { PlanningDay } from '../../services/planningService'

const props = defineProps<{
  days: PlanningDay[]
}>()

defineEmits<{
  (e: 'select-day', day: PlanningDay): void
}>()

// Calculate padding cells based on the weekday of the first day in our calendar
const paddingCells = computed(() => {
  if (props.days.length === 0) return 0
  const firstDate = new Date(props.days[0].date)
  // getDay(): 0 is Sunday, 1 is Monday ... 6 is Saturday
  // We want Monday (1) to be index 0, Tuesday (2) to be 1, ..., Sunday (0) to be 6
  const day = firstDate.getDay()
  return day === 0 ? 6 : day - 1
})

function isToday(dateStr: string): boolean {
  const today = new Date().toISOString().split('T')[0]
  return dateStr === today
}

function isFutureDay(dateStr: string): boolean {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const queryDate = new Date(dateStr)
  return queryDate > today
}

function formatDateNum(dateStr: string): string {
  return String(new Date(dateStr).getDate())
}

function formatFullDate(dateStr: string): string {
  const options: Intl.DateTimeFormatOptions = { weekday: 'long', day: 'numeric', month: 'long' }
  return new Date(dateStr).toLocaleDateString('fr-FR', options)
}

// Heatmap colors based on study load
function getLoadClasses(count: number): string {
  if (count < 10) {
    return 'bg-emerald-500/20 text-emerald-600 border border-emerald-500/30 dark:bg-emerald-950/40 dark:text-emerald-400 dark:border-emerald-500/10'
  }
  if (count <= 25) {
    return 'bg-amber-500/20 text-amber-600 border border-amber-500/30 dark:bg-amber-950/40 dark:text-amber-400 dark:border-amber-500/10'
  }
  return 'bg-rose-500/20 text-rose-600 border border-rose-500/30 dark:bg-rose-950/40 dark:text-rose-450 dark:border-rose-500/10'
}
</script>
