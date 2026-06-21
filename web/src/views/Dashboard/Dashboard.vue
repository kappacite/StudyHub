<template>
  <div>
    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-40 gap-3">
      <svg class="animate-spin h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="text-sm font-semibold text-ink-subtle uppercase tracking-widest">Chargement du tableau de bord...</span>
    </div>

    <div v-else class="space-y-8">
      <!-- Welcome section -->
      <div v-motion="fadeUp" class="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 bg-gradient-to-r from-primary/10 via-primary/5 to-transparent border border-primary/10 rounded-3xl">
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-ink">Ravi de te revoir, {{ authStore.user?.username }} ! 👋</h1>
          <p class="text-sm text-ink-muted mt-1">Prêt pour une nouvelle session d'apprentissage aujourd'hui ?</p>
        </div>
        <div class="flex items-center gap-3">
          <!-- Streak display -->
          <div class="flex items-center gap-2 px-4 py-2 bg-accent-soft border border-accent/20 rounded-2xl">
            <Flame class="w-5 h-5 text-accent fill-accent animate-pulse" />
            <div>
              <p class="text-xs font-semibold uppercase tracking-wider text-accent">Série d'étude</p>
              <p class="text-sm font-bold leading-none text-ink">{{ streak }} Jour(s) de suite</p>
            </div>
          </div>
        </div>
      </div>

    <!-- Focus Summary Widget -->
    <FocusWidget />

    <!-- Quick stats widgets -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatCard
        v-for="(stat, i) in stats"
        :key="stat.title"
        v-motion="listItem(i)"
        :label="stat.title"
        :value="stat.value"
        :accent="stat.accent"
      >
        <template #icon><component :is="stat.icon" class="w-5 h-5" /></template>
      </StatCard>
    </div>

    <!-- Main Dashboard Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Heatmap / Goal Tracker (Left & Middle columns) -->
      <div class="lg:col-span-2 space-y-8">
        <!-- Heatmap -->
        <BaseCard>
          <div class="flex items-center justify-between mb-6">
            <h3 class="font-bold text-ink flex items-center gap-2">
              <Calendar class="w-5 h-5 text-primary" />
              Activité d'étude (365 jours)
            </h3>
            <span class="text-xs font-semibold text-ink-subtle">Total : {{ totalSessionsCount }} sessions</span>
          </div>

          <!-- Heatmap grid simulation -->
          <div class="overflow-x-auto pb-2">
            <div class="flex flex-col gap-1 min-w-[620px]">
              <div class="flex gap-1" v-for="row in 7" :key="row">
                <!-- Row header (day name) -->
                <div class="w-8 text-[10px] text-ink-subtle flex items-center font-medium">
                  {{ dayNames[row - 1] }}
                </div>
                <!-- Box cells -->
                <div
                  v-for="col in 52"
                  :key="col"
                  class="w-3.5 h-3.5 rounded-sm transition-colors duration-200 hover:scale-125 cursor-pointer"
                  :class="getCellColor(row, col)"
                  :title="getTooltipText(row, col)"
                ></div>
              </div>
            </div>
            <div class="flex items-center justify-end gap-1.5 mt-4 text-[10px] text-ink-subtle font-semibold uppercase tracking-wider">
              <span>Moins</span>
              <div class="w-3 h-3 rounded-sm bg-surface-soft"></div>
              <div class="w-3 h-3 rounded-sm bg-primary/30"></div>
              <div class="w-3 h-3 rounded-sm bg-primary/60"></div>
              <div class="w-3 h-3 rounded-sm bg-primary"></div>
              <span>Plus</span>
            </div>
          </div>
        </BaseCard>

        <!-- Weekly goals -->
        <BaseCard>
          <h3 class="font-bold text-ink flex items-center gap-2 mb-6">
            <Sparkles class="w-5 h-5 text-primary" />
            Objectif Hebdomadaire
          </h3>
          <div class="space-y-4">
            <div class="flex items-center justify-between text-sm">
              <span class="font-semibold text-ink">Temps d'étude hebdo</span>
              <span class="text-ink-muted font-medium">{{ weeklyStudyHoursFormatted }} / {{ weeklyGoalHours }}h</span>
            </div>
            <div class="w-full bg-surface-soft rounded-full h-3 overflow-hidden">
              <div class="bg-primary h-full rounded-full transition-all duration-500" :style="{ width: weeklyGoalPercent + '%' }"></div>
            </div>
            <p class="text-xs text-ink-subtle">{{ weeklyGoalStatusText }}</p>
          </div>
        </BaseCard>

        <!-- Section de Statistiques de Cartes (Maturité & Prévisions) -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Maturity Distribution -->
          <BaseCard>
            <h3 class="font-bold text-ink flex items-center gap-2 mb-6">
              <Layers class="w-5 h-5 text-primary" />
              Maturité des Cartes
            </h3>
            <div class="space-y-4">
              <!-- Horizonal stacked bar -->
              <div class="w-full bg-surface-soft rounded-full h-4 overflow-hidden flex">
                <div
                  v-if="maturityLearningPercent > 0"
                  class="bg-accent h-full transition-all duration-300"
                  :style="{ width: maturityLearningPercent + '%' }"
                  title="En cours d'apprentissage"
                ></div>
                <div
                  v-if="maturityYoungPercent > 0"
                  class="bg-primary h-full transition-all duration-300"
                  :style="{ width: maturityYoungPercent + '%' }"
                  title="Jeunes cartes"
                ></div>
                <div
                  v-if="maturityMaturePercent > 0"
                  class="bg-success h-full transition-all duration-300"
                  :style="{ width: maturityMaturePercent + '%' }"
                  title="Cartes matures"
                ></div>
              </div>

              <!-- Legend and counts -->
              <div class="grid grid-cols-3 gap-2 text-center mt-2">
                <div class="p-2 bg-accent-soft rounded-2xl">
                  <span class="block text-[10px] font-bold text-accent">Appr.</span>
                  <span class="block text-sm font-black text-ink mt-0.5">{{ dashboardData?.maturity_distribution?.learning || 0 }}</span>
                </div>
                <div class="p-2 bg-primary-soft rounded-2xl">
                  <span class="block text-[10px] font-bold text-primary">Jeunes</span>
                  <span class="block text-sm font-black text-ink mt-0.5">{{ dashboardData?.maturity_distribution?.young || 0 }}</span>
                </div>
                <div class="p-2 bg-success-soft rounded-2xl">
                  <span class="block text-[10px] font-bold text-success">Matures</span>
                  <span class="block text-sm font-black text-ink mt-0.5">{{ dashboardData?.maturity_distribution?.mature || 0 }}</span>
                </div>
              </div>
            </div>
          </BaseCard>

          <!-- 7-day Forecast -->
          <BaseCard>
            <h3 class="font-bold text-ink flex items-center gap-2 mb-6">
              <Calendar class="w-5 h-5 text-primary" />
              Prévisions (7j)
            </h3>
            <div class="h-28 flex items-end justify-between gap-1.5 border-b border-line pb-1 relative">
              <div
                v-for="item in forecastList"
                :key="item.date"
                class="flex-1 flex flex-col items-center group cursor-pointer relative"
              >
                <!-- Popover value on hover -->
                <span class="opacity-0 group-hover:opacity-100 transition-opacity bg-ink text-app text-[8px] font-bold px-1 py-0.5 rounded -translate-y-5 z-10 whitespace-nowrap shadow absolute">
                  {{ item.count }}
                </span>
                <!-- Bar -->
                <div
                  class="w-full bg-primary rounded-t-md transition-all duration-500 group-hover:brightness-110"
                  :style="{ height: getForecastBarHeight(item.count) + 'px' }"
                ></div>
                <!-- Label -->
                <span class="text-[8px] font-bold text-ink-subtle mt-1">
                  {{ formatForecastDate(item.date) }}
                </span>
              </div>
            </div>
            <div v-if="forecastList.length === 0" class="text-center py-4 text-ink-subtle text-[10px] italic">
              Aucune prévision.
            </div>
          </BaseCard>
        </div>
      </div>

      <!-- Quick actions / Recent Decks (Right column) -->
      <div class="space-y-8">
        <!-- Quick Actions -->
        <BaseCard>
          <h3 class="font-bold text-ink flex items-center gap-2 mb-6">
            <Activity class="w-5 h-5 text-primary" />
            Actions rapides
          </h3>
          <div class="grid grid-cols-2 gap-4">
            <button
              v-for="action in quickActions"
              :key="action.label"
              @click="router.push(action.to)"
              class="flex flex-col items-center justify-center p-4 bg-surface-soft hover:bg-primary-soft border border-line rounded-2xl text-center transition-colors group"
            >
              <component :is="action.icon" class="w-6 h-6 text-primary group-hover:scale-110 transition-transform" />
              <span class="text-xs font-semibold mt-2 text-ink">{{ action.label }}</span>
            </button>
          </div>
        </BaseCard>

        <!-- Recent review / Decks Study list -->
        <BaseCard>
          <h3 class="font-bold text-ink flex items-center gap-2 mb-4">
            <Layers class="w-5 h-5 text-primary" />
            Révisions requises
          </h3>

          <div class="space-y-4">
            <div
              v-for="deck in dueDecks"
              :key="deck.id"
              class="flex items-center justify-between p-3 rounded-2xl bg-surface-soft border border-line"
            >
              <div>
                <p class="text-sm font-bold truncate max-w-[140px] text-ink">{{ deck.name }}</p>
                <p class="text-[11px] text-primary font-semibold uppercase tracking-wider mt-0.5">
                  {{ deck.due_count }} carte(s) à réviser
                </p>
              </div>
              <BaseButton size="sm" @click="router.push(`/decks/${deck.id}/study`)">Réviser</BaseButton>
            </div>

            <div v-if="dueDecks.length === 0" class="text-center py-6 text-ink-subtle text-xs font-semibold uppercase tracking-wider">
              Tout est à jour ! 🎉
            </div>
          </div>
        </BaseCard>
      </div>
    </div>
  </div>
</div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useDecksStore } from '../../stores/decks'
import FocusWidget from '../../components/dashboard/FocusWidget.vue'
import { BaseCard, BaseButton, StatCard } from '../../components/ui/base'
import { fadeUp, listItem } from '../../composables/useMotionPresets'
import api from '../../services/api'
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

const loading = ref(true)
const dashboardData = ref<any>(null)

// Reactive statistics from backend
const totalReviewed = ref(0)
const totalCorrect = ref(0)
const totalTimeSeconds = ref(0)
const streak = ref(0)

const successRate = computed(() => {
  if (totalReviewed.value === 0) return '0%'
  return Math.round((totalCorrect.value / totalReviewed.value) * 100) + '%'
})

const formattedStudyTime = computed(() => {
  const totalMinutes = Math.floor(totalTimeSeconds.value / 60)
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  
  if (hours === 0) {
    return `${minutes}m`
  }
  return `${hours}h ${minutes}m`
})

const stats = computed(() => [
  { title: 'Cartes révisées', value: totalReviewed.value.toString(), icon: CheckCircle2, accent: 'success' as const },
  { title: 'Taux de réussite', value: successRate.value, icon: Sparkles, accent: 'primary' as const },
  { title: 'Temps d\'étude', value: formattedStudyTime.value, icon: Clock, accent: 'info' as const },
  { title: 'Decks actifs', value: decksStore.decks.length.toString(), icon: Layers, accent: 'accent' as const }
])

const quickActions = [
  { label: 'Créer Note', to: '/notes', icon: FileText },
  { label: 'Réviser Deck', to: '/decks', icon: Layers },
  { label: 'Importer PDF', to: '/pdfs', icon: FileDown },
  { label: 'Nouveau Schéma', to: '/diagrams', icon: Activity },
]

// Weekly goals connection
const weeklyStudySeconds = ref(0)
const weeklyGoalHours = ref(5)

const weeklyStudyHoursFormatted = computed(() => {
  const hours = (weeklyStudySeconds.value / 3600).toFixed(1)
  return `${hours}h`
})

const weeklyGoalPercent = computed(() => {
  const targetSeconds = weeklyGoalHours.value * 3600
  if (targetSeconds === 0) return 0
  return Math.min(100, Math.round((weeklyStudySeconds.value / targetSeconds) * 100))
})

const weeklyGoalStatusText = computed(() => {
  const targetSeconds = weeklyGoalHours.value * 3600
  const remainingSeconds = targetSeconds - weeklyStudySeconds.value
  if (remainingSeconds <= 0) {
    return "Objectif atteint pour cette semaine ! Félicitations ! 🎉"
  }
  const remainingHours = (remainingSeconds / 3600).toFixed(1)
  return `Plus que ${remainingHours}h pour atteindre ton objectif de la semaine ! Tu y es presque.`
})

// Due Decks connection
const dueCounts = ref<Record<number, number>>({})

const dueDecks = computed(() => {
  return decksStore.decks.map(deck => {
    const count = dueCounts.value[deck.id] !== undefined ? dueCounts.value[deck.id] : 0
    return {
      ...deck,
      due_count: count
    }
  }).filter(d => d.due_count > 0)
})

async function fetchDecksStats() {
  const promises = decksStore.decks.map(async (deck) => {
    try {
      const response = await api.get(`/stats/decks/${deck.id}`)
      dueCounts.value[deck.id] = response.data.cards_to_review
    } catch (error) {
      console.error(`Erreur de fetch stats pour deck ${deck.id}`, error)
      dueCounts.value[deck.id] = 0
    }
  })
  await Promise.all(promises)
}

// Heatmap connection
const heatmapData = ref<Record<string, { duration: number, count: number }>>({})
const totalSessionsCount = ref(0)

const gridStartDate = computed(() => {
  const today = new Date()
  const dayOfWeek = today.getDay()
  const currentWeekSunday = new Date(today)
  currentWeekSunday.setDate(today.getDate() - dayOfWeek)
  currentWeekSunday.setHours(0, 0, 0, 0)
  
  const start = new Date(currentWeekSunday)
  start.setDate(currentWeekSunday.getDate() - 51 * 7)
  return start
})

function getCellDateStr(row: number, col: number): string {
  const date = new Date(gridStartDate.value)
  date.setDate(gridStartDate.value.getDate() + (col - 1) * 7 + row)
  const yyyy = date.getFullYear()
  const mm = String(date.getMonth() + 1).padStart(2, '0')
  const dd = String(date.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

function getCellColor(row: number, col: number) {
  const dateStr = getCellDateStr(row, col)
  const data = heatmapData.value[dateStr]
  const val = data ? data.count : 0
  
  if (val <= 0) return 'bg-surface-soft'
  if (val === 1) return 'bg-primary/30'
  if (val === 2) return 'bg-primary/50'
  if (val === 3) return 'bg-primary/75'
  return 'bg-primary'
}

function getTooltipText(row: number, col: number): string {
  const dateStr = getCellDateStr(row, col)
  const data = heatmapData.value[dateStr]
  const count = data ? data.count : 0
  
  const dateObj = new Date(dateStr)
  const formattedDate = dateObj.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
  
  if (count === 0) {
    return `${formattedDate} : Aucune session`
  }
  return `${formattedDate} : ${count} session(s) (${Math.round(data.duration / 60)} min)`
}

function getStartAndEndOfWeek() {
  const now = new Date()
  const day = now.getDay()
  const diff = now.getDate() - day + (day === 0 ? -6 : 1)
  const startOfWeek = new Date(now.setDate(diff))
  startOfWeek.setHours(0, 0, 0, 0)
  
  const endOfWeek = new Date(startOfWeek)
  endOfWeek.setDate(startOfWeek.getDate() + 6)
  endOfWeek.setHours(23, 59, 59, 999)
  
  return {
    from: startOfWeek.toISOString().replace('Z', '+00:00'),
    to: endOfWeek.toISOString().replace('Z', '+00:00')
  }
}

const maturityTotal = computed(() => {
  const dist = dashboardData.value?.maturity_distribution
  if (!dist) return 0
  return (dist.learning || 0) + (dist.young || 0) + (dist.mature || 0)
})

const maturityLearningPercent = computed(() => {
  if (maturityTotal.value === 0) return 0
  return Math.round((dashboardData.value.maturity_distribution.learning / maturityTotal.value) * 100)
})

const maturityYoungPercent = computed(() => {
  if (maturityTotal.value === 0) return 0
  return Math.round((dashboardData.value.maturity_distribution.young / maturityTotal.value) * 100)
})

const maturityMaturePercent = computed(() => {
  if (maturityTotal.value === 0) return 0
  return Math.round((dashboardData.value.maturity_distribution.mature / maturityTotal.value) * 100)
})

const forecastList = computed(() => {
  const forecast = dashboardData.value?.forecast_7_days
  if (!forecast) return []
  return Object.keys(forecast).sort().map(date => ({
    date,
    count: forecast[date]
  }))
})

function getForecastBarHeight(count: number): number {
  const counts = forecastList.value.map(i => i.count)
  const max = Math.max(...counts, 0)
  if (max === 0) return 4
  return Math.max(4, Math.round((count / max) * 100)) // Max height 100px
}

function formatForecastDate(dateStr: string): string {
  const dateObj = new Date(dateStr)
  return dateObj.toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric' })
}

onMounted(async () => {
  loading.value = true
  try {
    // 1. Fetch decks first to compute counts
    await decksStore.fetchDecks()
    
    const weekParams = getStartAndEndOfWeek()
    
    // 2. Fetch stats in parallel
    await Promise.all([
      api.get('/stats/overview').then(res => {
        totalReviewed.value = res.data.total_reviewed
        totalCorrect.value = res.data.total_correct
        totalTimeSeconds.value = res.data.total_time_seconds
        streak.value = res.data.streak
      }),
      api.get('/stats/heatmap').then(res => {
        const map: Record<string, { duration: number, count: number }> = {}
        let total = 0
        res.data.forEach((item: any) => {
          map[item.date] = {
            duration: item.duration,
            count: item.count
          }
          total += item.count
        })
        heatmapData.value = map
        totalSessionsCount.value = total
      }),
      api.get('/stats/sessions', {
        params: {
          from: weekParams.from,
          to: weekParams.to
        }
      }).then(res => {
        const totalSec = res.data.reduce((acc: number, item: any) => acc + item.duration_seconds, 0)
        weeklyStudySeconds.value = totalSec
      }),
      api.get('/stats/dashboard').then(res => {
        dashboardData.value = res.data
      }),
      fetchDecksStats()
    ])
  } catch (err) {
    console.error('Erreur lors du chargement des données du tableau de bord', err)
  } finally {
    loading.value = false
  }
})
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
