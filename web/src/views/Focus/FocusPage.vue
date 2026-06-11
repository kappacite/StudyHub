<template>
  <div class="space-y-8 animate-fade-in">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl font-bold">Mon Espace Focus</h1>
        <p class="text-xs text-slate-400 dark:text-slate-500 mt-1">
          Concentrez-vous sur l'essentiel : révisions prioritaires, prévisions de charge et taux de rétention.
        </p>
      </div>

      <button
        @click="startAllReviews"
        :disabled="focusStore.totalDue === 0"
        class="inline-flex items-center gap-2 px-5 py-2.5 border border-transparent rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition-all shadow-lg shadow-indigo-600/15 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Flame class="w-4 h-4 fill-white" />
        Tout réviser ({{ focusStore.totalDue }})
      </button>
    </div>

    <!-- Loading / Error States -->
    <div v-if="focusStore.loading" class="flex flex-col items-center justify-center py-20 gap-3">
      <svg class="animate-spin h-8 w-8 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="text-sm font-semibold text-slate-400 uppercase tracking-widest">Chargement de votre espace focus...</span>
    </div>

    <div v-else-if="focusStore.error" class="p-6 bg-rose-50 border border-rose-100 rounded-3xl dark:bg-rose-950/20 dark:border-rose-900/30 text-rose-600 dark:text-rose-400">
      <p class="font-semibold">{{ focusStore.error }}</p>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      <!-- 1. ZONE MAINTENANT (8 cols) -->
      <div class="lg:col-span-8 space-y-6">
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm">
          <h3 class="font-bold text-slate-800 dark:text-white flex items-center gap-2 mb-6">
            <Clock class="w-5 h-5 text-indigo-500" />
            À réviser maintenant
          </h3>

          <div class="space-y-4">
            <div 
              v-for="item in focusStore.items" 
              :key="`${item.type}-${item.id}`"
              class="flex items-center justify-between p-4 rounded-2xl border transition-all duration-200 group"
              :class="getItemClasses(item)"
            >
              <div class="flex items-center gap-4 min-w-0">
                <!-- Icon indicator -->
                <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0" :class="getItemIconBg(item)">
                  <component :is="getItemIcon(item)" class="w-5 h-5" :class="getItemIconColor(item)" />
                </div>
                <div class="min-w-0">
                  <h4 class="font-bold text-sm text-slate-800 dark:text-white truncate flex items-center gap-2">
                    {{ item.title }}
                    <span 
                      v-if="item.is_late"
                      class="px-2 py-0.5 rounded-lg text-[9px] font-bold uppercase tracking-wider bg-rose-500/10 text-rose-500 border border-rose-500/20"
                    >
                      En retard
                    </span>
                  </h4>
                  <p class="text-[11px] text-slate-400 mt-0.5">
                    {{ getItemSummary(item) }}
                  </p>
                </div>
              </div>

              <div class="flex items-center gap-3">
                <span class="text-xs font-semibold text-slate-450 dark:text-slate-500" v-if="item.last_session_ago_days !== null">
                  Dernière étude il y a {{ item.last_session_ago_days }}j
                </span>
                <button 
                  @click="studyItem(item)"
                  class="px-4 py-2 border border-slate-200 dark:border-slate-800 rounded-xl text-xs font-bold text-slate-700 hover:bg-slate-50 dark:text-slate-200 dark:hover:bg-slate-850 transition-all active:scale-95 flex items-center gap-1.5"
                >
                  Réviser
                  <ArrowRight class="w-3.5 h-3.5 text-indigo-500" />
                </button>
              </div>
            </div>

            <div 
              v-if="focusStore.items.length === 0" 
              class="border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-3xl p-12 flex flex-col items-center justify-center text-center text-slate-400"
            >
              <CheckCircle2 class="w-12 h-12 text-emerald-400 mb-3" />
              <h4 class="font-bold text-slate-800 dark:text-slate-200">Tout est à jour !</h4>
              <p class="text-xs mt-1">Vous n'avez aucune révision en attente. Profitez-en pour vous reposer ou explorer de nouveaux cours.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 2. FORECAST & RETENTION (4 cols) -->
      <div class="lg:col-span-4 space-y-6">
        <!-- Forecast (Charge 14 jours) -->
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm">
          <h3 class="font-bold text-slate-800 dark:text-white flex items-center gap-2 mb-4">
            <Calendar class="w-5 h-5 text-indigo-500" />
            Charge à venir (14j)
          </h3>
          
          <div class="h-32 flex items-end justify-between gap-1 border-b border-slate-100 dark:border-slate-800 pb-1 relative mt-6">
            <div 
              v-for="item in focusStore.forecast" 
              :key="item.date" 
              class="flex-1 flex flex-col items-center group cursor-pointer relative"
            >
              <!-- Popover value on hover -->
              <span class="opacity-0 group-hover:opacity-100 transition-opacity bg-slate-950 dark:bg-slate-800 text-white dark:text-slate-200 text-[8px] font-bold px-1.5 py-0.5 rounded -translate-y-5 z-10 whitespace-nowrap shadow absolute">
                {{ item.count }} cartes
              </span>
              <!-- Bar -->
              <div 
                class="w-full rounded-t-md transition-all duration-500 group-hover:brightness-110"
                :class="getLoadBarClass(item.load_level)"
                :style="{ height: getForecastBarHeight(item.count) + 'px' }"
              ></div>
              <!-- Label -->
              <span class="text-[7px] font-black text-slate-400 dark:text-slate-500 mt-1.5 rotate-45 origin-left whitespace-nowrap">
                {{ formatForecastDate(item.date) }}
              </span>
            </div>
          </div>
          
          <!-- Legend -->
          <div class="flex items-center justify-between mt-8 pt-4 border-t border-slate-50 dark:border-slate-800/50 text-[10px] font-bold uppercase tracking-wider text-slate-400">
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-sm bg-emerald-500/20 border border-emerald-500/30"></span> Bas</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-sm bg-amber-500/20 border border-amber-500/30"></span> Moyen</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-sm bg-rose-500/20 border border-rose-500/30"></span> Fort</span>
          </div>
        </div>

        <!-- Rétention par matière -->
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm">
          <h3 class="font-bold text-slate-800 dark:text-white flex items-center gap-2 mb-6">
            <Activity class="w-5 h-5 text-indigo-500" />
            Rétention par matière
          </h3>

          <div class="space-y-4">
            <div 
              v-for="sub in focusStore.retention" 
              :key="sub.binder_id"
              class="space-y-2"
            >
              <div class="flex items-center justify-between text-xs">
                <span class="font-bold text-slate-700 dark:text-slate-350">{{ sub.binder_name }}</span>
                <div class="flex items-center gap-2 font-semibold">
                  <span class="text-slate-800 dark:text-white">{{ sub.retention_pct }}%</span>
                  
                  <!-- Trend badge -->
                  <span 
                    v-if="sub.trend_7d !== 0"
                    class="inline-flex items-center text-[9px] px-1 py-0.5 rounded-md"
                    :class="sub.trend_7d > 0 ? 'text-emerald-600 bg-emerald-50 dark:text-emerald-400 dark:bg-emerald-950/20' : 'text-rose-600 bg-rose-50 dark:text-rose-400 dark:bg-rose-950/20'"
                  >
                    {{ sub.trend_7d > 0 ? '▲' : '▼' }} {{ Math.abs(sub.trend_7d) }}%
                  </span>
                </div>
              </div>
              <div class="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden flex">
                <div 
                  class="h-full rounded-full transition-all duration-500"
                  :class="getRetentionBarClass(sub.retention_pct)"
                  :style="{ width: sub.retention_pct + '%' }"
                ></div>
              </div>
              <div class="flex items-center justify-between text-[9px] text-slate-400 font-bold uppercase tracking-wider">
                <span>Rétention 30j</span>
                <span v-if="sub.overdue_count > 0" class="text-rose-500">{{ sub.overdue_count }} en attente</span>
                <span v-else class="text-emerald-500">À jour</span>
              </div>
            </div>

            <div v-if="focusStore.retention.length === 0" class="text-center py-4 text-slate-455 text-xs italic">
              Aucun classeur créé.
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFocusStore } from '../../stores/focus'
import type { FocusItem } from '../../services/focusService'
import { 
  Flame, 
  Clock, 
  Layers, 
  FileText, 
  CheckCircle2, 
  Calendar, 
  Activity, 
  ArrowRight,
  GraduationCap
} from '@lucide/vue'

const focusStore = useFocusStore()
const router = useRouter()

onMounted(async () => {
  await focusStore.loadFocusData()
})

// Item styling helper methods
function getItemClasses(item: FocusItem) {
  if (item.is_late) {
    return 'border-rose-100 bg-rose-50/10 hover:bg-rose-50/20 dark:border-rose-900/30'
  }
  if (item.type === 'note') {
    return 'border-purple-100 bg-purple-50/10 hover:bg-purple-50/20 dark:border-purple-900/30'
  }
  if (item.type === 'assignment') {
    return 'border-sky-100 bg-sky-50/10 hover:bg-sky-50/20 dark:border-sky-900/30'
  }
  return 'border-slate-100 bg-slate-50/20 hover:bg-slate-50/40 dark:border-slate-800/80 dark:hover:bg-slate-800/60'
}

function getItemIconBg(item: FocusItem) {
  if (item.is_late) return 'bg-rose-50 dark:bg-rose-950/30'
  if (item.type === 'note') return 'bg-purple-50 dark:bg-purple-950/30'
  if (item.type === 'assignment') return 'bg-sky-50 dark:bg-sky-950/30'
  return 'bg-indigo-50 dark:bg-indigo-950/30'
}

function getItemIcon(item: FocusItem) {
  if (item.type === 'deck') return Layers
  if (item.type === 'note') return FileText
  return GraduationCap
}

function getItemIconColor(item: FocusItem) {
  if (item.is_late) return 'text-rose-500'
  if (item.type === 'note') return 'text-purple-500'
  if (item.type === 'assignment') return 'text-sky-500'
  return 'text-indigo-500'
}

function getItemSummary(item: FocusItem) {
  if (item.type === 'deck') {
    return `${item.count} carte(s) mémoire à réviser`
  }
  if (item.type === 'note') {
    return 'Feuille blanche à restituer (Blurting)'
  }
  return item.due_date ? `Devoir à terminer avant le ${new Date(item.due_date).toLocaleDateString('fr-FR')}` : 'Devoir sans date limite'
}

function studyItem(item: FocusItem) {
  if (item.type === 'deck') {
    router.push(`/decks/${item.id}/study?focus=true`)
  } else if (item.type === 'note') {
    router.push(`/notes/${item.id}/blurting?focus=true&from=focus`)
  } else if (item.type === 'assignment') {
    router.push(`/binders/${item.id}`)
  }
}

function startAllReviews() {
  const firstItem = focusStore.startUnifiedReview()
  if (firstItem) {
    studyItem(firstItem)
  }
}

// Forecast helper methods
function getLoadBarClass(level: 'low' | 'medium' | 'high') {
  if (level === 'low') return 'bg-emerald-500/30 border border-emerald-500/20 text-emerald-500'
  if (level === 'medium') return 'bg-amber-500/30 border border-amber-500/20 text-amber-500'
  return 'bg-rose-500/30 border border-rose-500/20 text-rose-500'
}

function getForecastBarHeight(count: number): number {
  const max = Math.max(...focusStore.forecast.map(f => f.count), 5)
  return Math.max(4, Math.round((count / max) * 110)) // Max height 110px
}

function formatForecastDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric' })
}

// Retention helper methods
function getRetentionBarClass(pct: number) {
  if (pct < 50) return 'bg-rose-500'
  if (pct < 75) return 'bg-amber-500'
  return 'bg-emerald-500'
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
