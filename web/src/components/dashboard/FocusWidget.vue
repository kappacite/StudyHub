<template>
  <div class="relative overflow-hidden bg-gradient-to-br from-primary via-primary to-accent text-white rounded-3xl p-6 shadow-xl shadow-elev-primary dark:shadow-none animate-fade-in group">
    <!-- Background patterns for premium aesthetics -->
    <div class="absolute -right-10 -top-10 w-40 h-40 bg-surface/5 rounded-full blur-2xl group-hover:scale-125 transition-transform duration-500 pointer-events-none"></div>
    <div class="absolute -left-10 -bottom-10 w-48 h-48 bg-accent rounded-full blur-3xl pointer-events-none"></div>

    <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
      <!-- Left side: counts & status -->
      <div class="space-y-4">
        <div>
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-surface/10 backdrop-blur-md text-primary">
            <span class="w-1.5 h-1.5 rounded-full bg-success animate-ping"></span>
            Espace Focus
          </span>
          <h2 class="text-3xl font-black tracking-tight mt-2 flex items-baseline gap-2">
            {{ focusStore.totalDue }}
            <span class="text-xs font-semibold text-primary">tâches requises aujourd'hui</span>
          </h2>
        </div>

        <!-- Badges Grid -->
        <div class="flex flex-wrap gap-2 text-xs font-bold uppercase tracking-wider">
          <span 
            v-if="focusStore.lateCount > 0"
            class="px-2.5 py-1 rounded-xl bg-danger text-danger border border-danger flex items-center gap-1"
          >
            <Flame class="w-3.5 h-3.5" />
            {{ focusStore.lateCount }} en retard
          </span>
          <span class="px-2.5 py-1 rounded-xl bg-surface/5 text-primary border border-white/5">
            {{ focusStore.flashcardCount }} cartes
          </span>
          <span class="px-2.5 py-1 rounded-xl bg-surface/5 text-primary border border-white/5">
            {{ focusStore.blurtingCount }} feuilles blanches
          </span>
          <span v-if="focusStore.assignmentCount > 0" class="px-2.5 py-1 rounded-xl bg-surface/5 text-primary border border-white/5">
            {{ focusStore.assignmentCount }} devoirs
          </span>
        </div>
      </div>

      <!-- Center: 7-day sparkline -->
      <div class="flex flex-col items-center md:items-end gap-1.5 bg-surface/5 backdrop-blur-sm border border-white/10 rounded-2xl p-4 min-w-[160px]">
        <span class="text-[9px] font-black text-primary uppercase tracking-widest">Prévisions 7 jours</span>
        
        <!-- Inline SVG Sparkline -->
        <svg class="w-32 h-10 text-primary stroke-2 overflow-visible" viewBox="0 0 100 30" fill="none">
          <!-- Sparkline Path -->
          <path 
            :d="sparklinePath" 
            stroke="currentColor" 
            stroke-linecap="round" 
            stroke-linejoin="round"
          />
          <!-- Grid/Reference dots -->
          <circle 
            v-for="(point, idx) in sparklinePoints" 
            :key="idx"
            :cx="point.x" 
            :cy="point.y" 
            r="2" 
            class="fill-white stroke-primary stroke-[1px] hover:scale-150 transition-transform duration-100 cursor-pointer"
            :title="`${point.count} cartes`"
          />
        </svg>
        
        <span class="text-[8px] text-primary font-semibold uppercase tracking-wider">Total prévu : {{ forecastTotal }} cartes</span>
      </div>

      <!-- Right side: CTAs -->
      <div class="flex sm:flex-row md:flex-col gap-3 min-w-[150px] w-full sm:w-auto">
        <button 
          @click="startStudy"
          class="flex-1 px-5 py-3 rounded-2xl text-xs font-bold text-primary bg-surface hover:bg-primary-soft active:scale-95 transition-all text-center shadow-lg shadow-black/5 flex items-center justify-center gap-1.5"
          :disabled="focusStore.totalDue === 0"
          :class="focusStore.totalDue === 0 ? 'opacity-50 cursor-not-allowed' : ''"
        >
          <Flame class="w-4 h-4 fill-primary" />
          Lancer la révision
        </button>
        <button 
          @click="goToFocusPage"
          class="flex-1 px-5 py-3 rounded-2xl text-xs font-bold text-white bg-primary hover:bg-primary-strong border border-white/10 active:scale-95 transition-all text-center"
        >
          Voir le détail
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFocusStore } from '../../stores/focus'
import { Flame } from '@lucide/vue'

const focusStore = useFocusStore()
const router = useRouter()

onMounted(async () => {
  await focusStore.loadFocusData()
})

const forecastTotal = computed(() => {
  return focusStore.forecast.slice(0, 7).reduce((acc, curr) => acc + curr.count, 0)
})

// Generate SVG points for a 7-day sparkline
const sparklinePoints = computed(() => {
  const data = focusStore.forecast.slice(0, 7)
  if (data.length === 0) return []
  
  const width = 100
  const height = 24 // Keep padding for dots (total SVG height is 30)
  const maxCount = Math.max(...data.map(d => d.count), 5) // Avoid division by zero, min maxCount is 5
  
  return data.map((d, index) => {
    const x = (index / (data.length - 1)) * width
    // Flip Y-axis so higher count is near the top
    const y = 3 + height - (d.count / maxCount) * height
    return { x, y, count: d.count }
  })
})

const sparklinePath = computed(() => {
  const points = sparklinePoints.value
  if (points.length === 0) return ''
  return points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
})

function startStudy() {
  const firstItem = focusStore.startUnifiedReview()
  if (firstItem) {
    if (firstItem.type === 'deck') {
      router.push(`/decks/${firstItem.id}/study?focus=true`)
    } else if (firstItem.type === 'note') {
      router.push(`/notes/${firstItem.id}/blurting?focus=true&from=focus`)
    } else if (firstItem.type === 'assignment') {
      router.push(`/binders/${firstItem.id}`)
    }
  }
}

function goToFocusPage() {
  router.push('/focus')
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
