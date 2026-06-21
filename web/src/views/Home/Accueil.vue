<template>
  <PageContainer>
    <PageHeader title="Accueil" :subtitle="greeting">
      <template #actions>
        <BaseButton
          :disabled="focusStore.totalDue === 0"
          @click="continueReview"
        >
          <template #icon><Flame class="w-4 h-4 fill-white" /></template>
          {{ focusStore.totalDue > 0 ? `Continuer à réviser (${focusStore.totalDue})` : 'Tout est à jour' }}
        </BaseButton>
      </template>
    </PageHeader>

    <!-- Loading -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-32 gap-3">
      <svg class="animate-spin h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="text-sm font-semibold text-ink-subtle uppercase tracking-widest">Chargement de votre accueil...</span>
    </div>

    <template v-else>
      <!-- Hero : série + résumé du jour -->
      <BaseCard
        v-motion="fadeUp"
        class="!bg-gradient-to-r from-primary/10 via-primary-soft/40 to-transparent border-primary/15"
      >
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div class="min-w-0">
            <h2 class="text-xl font-bold text-ink">Prêt·e à apprendre, {{ authStore.user?.username }} ? 👋</h2>
            <p class="text-sm text-ink-muted mt-1">{{ todaySummary }}</p>
          </div>
          <div class="flex items-center gap-2 px-4 py-2 bg-accent-soft border border-accent/20 rounded-2xl shrink-0">
            <Flame class="w-5 h-5 text-accent fill-accent animate-pulse" />
            <div>
              <p class="text-xs font-semibold uppercase tracking-wider text-accent">Série d'étude</p>
              <p class="text-sm font-bold leading-none text-ink">{{ streak }} jour(s) de suite</p>
            </div>
          </div>
        </div>
      </BaseCard>

      <!-- À réviser maintenant (gauche) + Aujourd'hui (droite) -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        <!-- File de révision -->
        <BaseCard class="lg:col-span-2">
          <h3 class="font-bold text-ink flex items-center gap-2 mb-4">
            <Clock class="w-5 h-5 text-primary" />
            À réviser maintenant
          </h3>

          <div class="space-y-2">
            <ListRow
              v-for="item in focusStore.items"
              :key="`${item.type}-${item.id}`"
              :title="item.title"
              :subtitle="getItemSummary(item)"
            >
              <template #leading>
                <div class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0" :class="item.is_late ? 'bg-danger-soft' : 'bg-primary-soft'">
                  <component :is="getItemIcon(item)" class="w-5 h-5" :class="item.is_late ? 'text-danger' : 'text-primary'" />
                </div>
              </template>
              <template #trailing>
                <div class="flex items-center gap-3">
                  <span
                    v-if="item.is_late"
                    class="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider bg-danger-soft text-danger"
                  >En retard</span>
                  <BaseButton variant="secondary" size="sm" @click="studyItem(item)">
                    Réviser
                    <template #icon><ArrowRight class="w-3.5 h-3.5" /></template>
                  </BaseButton>
                </div>
              </template>
            </ListRow>

            <BaseEmptyState
              v-if="focusStore.items.length === 0"
              title="Tout est à jour !"
              description="Aucune révision en attente. Profitez-en pour explorer de nouveaux cours."
            >
              <template #icon><CheckCircle2 class="w-12 h-12 text-success" /></template>
            </BaseEmptyState>
          </div>
        </BaseCard>

        <!-- Aujourd'hui : compteurs + charge à venir -->
        <div class="space-y-6">
          <BaseCard>
            <h3 class="font-bold text-ink flex items-center gap-2 mb-4">
              <Sparkles class="w-5 h-5 text-primary" />
              Aujourd'hui
            </h3>
            <div class="space-y-2">
              <div
                v-for="c in todayCounters"
                :key="c.label"
                class="flex items-center justify-between px-3 py-2 rounded-xl bg-surface-soft"
              >
                <span class="flex items-center gap-2 text-sm text-ink-muted">
                  <component :is="c.icon" class="w-4 h-4" :class="c.color" />
                  {{ c.label }}
                </span>
                <span class="text-sm font-bold text-ink">{{ c.value }}</span>
              </div>
            </div>
          </BaseCard>

          <!-- Charge à venir (14j) -->
          <BaseCard>
            <h3 class="font-bold text-ink flex items-center gap-2 mb-4">
              <Calendar class="w-5 h-5 text-primary" />
              Charge à venir (14j)
            </h3>
            <div class="h-28 flex items-end justify-between gap-1 border-b border-line pb-1">
              <div
                v-for="item in focusStore.forecast"
                :key="item.date"
                class="flex-1 flex flex-col items-center group cursor-pointer relative"
              >
                <span class="opacity-0 group-hover:opacity-100 transition-opacity bg-ink text-app text-[8px] font-bold px-1.5 py-0.5 rounded -translate-y-5 z-10 whitespace-nowrap shadow absolute">
                  {{ item.count }}
                </span>
                <div
                  class="w-full rounded-t-md transition-all duration-500 group-hover:brightness-110"
                  :class="getLoadBarClass(item.load_level)"
                  :style="{ height: getForecastBarHeight(item.count) + 'px' }"
                ></div>
              </div>
            </div>
            <div class="flex items-center justify-between mt-4 text-[10px] font-bold uppercase tracking-wider text-ink-subtle">
              <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-sm bg-success/40"></span> Bas</span>
              <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-sm bg-warning/50"></span> Moyen</span>
              <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-sm bg-danger/50"></span> Fort</span>
            </div>
          </BaseCard>
        </div>
      </div>

      <!-- Progression -->
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

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        <!-- Heatmap (gauche large) -->
        <BaseCard class="lg:col-span-2">
          <div class="flex items-center justify-between mb-6">
            <h3 class="font-bold text-ink flex items-center gap-2">
              <Calendar class="w-5 h-5 text-primary" />
              Activité d'étude (365 jours)
            </h3>
            <span class="text-xs font-semibold text-ink-subtle">Total : {{ totalSessionsCount }} sessions</span>
          </div>
          <div class="overflow-x-auto pb-2">
            <div class="flex flex-col gap-1 min-w-[620px]">
              <div class="flex gap-1" v-for="row in 7" :key="row">
                <div class="w-8 text-[10px] text-ink-subtle flex items-center font-medium">{{ dayNames[row - 1] }}</div>
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

        <!-- Objectif hebdo + Rétention (droite) -->
        <div class="space-y-6">
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

          <BaseCard>
            <h3 class="font-bold text-ink flex items-center gap-2 mb-6">
              <Activity class="w-5 h-5 text-primary" />
              Rétention par matière
            </h3>
            <div class="space-y-4">
              <div v-for="sub in focusStore.retention" :key="sub.binder_id" class="space-y-1.5">
                <div class="flex items-center justify-between text-xs">
                  <span class="font-bold text-ink truncate">{{ sub.binder_name }}</span>
                  <div class="flex items-center gap-2 font-semibold">
                    <span class="text-ink">{{ sub.retention_pct }}%</span>
                    <span
                      v-if="sub.trend_7d !== 0"
                      class="inline-flex items-center text-[9px] px-1 py-0.5 rounded-md"
                      :class="sub.trend_7d > 0 ? 'text-success bg-success-soft' : 'text-danger bg-danger-soft'"
                    >{{ sub.trend_7d > 0 ? '▲' : '▼' }} {{ Math.abs(sub.trend_7d) }}%</span>
                  </div>
                </div>
                <div class="w-full bg-surface-soft rounded-full h-2 overflow-hidden">
                  <div class="h-full rounded-full transition-all duration-500" :class="getRetentionBarClass(sub.retention_pct)" :style="{ width: sub.retention_pct + '%' }"></div>
                </div>
              </div>
              <div v-if="focusStore.retention.length === 0" class="text-center py-4 text-ink-subtle text-xs italic">
                Aucun classeur créé.
              </div>
            </div>
          </BaseCard>
        </div>
      </div>
    </template>
  </PageContainer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useDecksStore } from '../../stores/decks'
import { useFocusStore } from '../../stores/focus'
import type { FocusItem } from '../../services/focusService'
import { PageContainer, PageHeader, BaseCard, BaseButton, BaseEmptyState, StatCard, ListRow } from '../../components/ui/base'
import { fadeUp, listItem } from '../../composables/useMotionPresets'
import api from '../../services/api'
import {
  Flame, Clock, CheckCircle2, Layers, Calendar, Sparkles, Activity,
  ArrowRight, FileText, GraduationCap
} from '@lucide/vue'

const authStore = useAuthStore()
const decksStore = useDecksStore()
const focusStore = useFocusStore()
const router = useRouter()

const dayNames = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam']
const loading = ref(true)

const totalReviewed = ref(0)
const totalCorrect = ref(0)
const totalTimeSeconds = ref(0)
const streak = ref(0)

const greeting = computed(() => 'Vos priorités du jour, en un coup d\'œil.')

const todaySummary = computed(() => {
  if (focusStore.totalDue === 0) return 'Aucune révision en attente aujourd\'hui — beau travail !'
  const late = focusStore.lateCount > 0 ? ` (dont ${focusStore.lateCount} en retard)` : ''
  return `${focusStore.totalDue} élément(s) à réviser aujourd'hui${late}.`
})

const successRate = computed(() => {
  if (totalReviewed.value === 0) return '0%'
  return Math.round((totalCorrect.value / totalReviewed.value) * 100) + '%'
})

const formattedStudyTime = computed(() => {
  const totalMinutes = Math.floor(totalTimeSeconds.value / 60)
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  return hours === 0 ? `${minutes}m` : `${hours}h ${minutes}m`
})

const stats = computed(() => [
  { title: 'Cartes révisées', value: totalReviewed.value.toString(), icon: CheckCircle2, accent: 'success' as const },
  { title: 'Taux de réussite', value: successRate.value, icon: Sparkles, accent: 'primary' as const },
  { title: 'Temps d\'étude', value: formattedStudyTime.value, icon: Clock, accent: 'info' as const },
  { title: 'Decks actifs', value: decksStore.decks.length.toString(), icon: Layers, accent: 'accent' as const },
])

const todayCounters = computed(() => [
  { label: 'À réviser', value: focusStore.totalDue, icon: Clock, color: 'text-primary' },
  { label: 'En retard', value: focusStore.lateCount, icon: Flame, color: 'text-danger' },
  { label: 'Flashcards', value: focusStore.flashcardCount, icon: Layers, color: 'text-primary' },
  { label: 'Feuilles blanches', value: focusStore.blurtingCount, icon: FileText, color: 'text-primary' },
  { label: 'Devoirs', value: focusStore.assignmentCount, icon: GraduationCap, color: 'text-info' },
])

// ─── File de révision ──────────────────────────────────────────────────────
function getItemIcon(item: FocusItem) {
  if (item.type === 'deck') return Layers
  if (item.type === 'note') return FileText
  return GraduationCap
}

function getItemSummary(item: FocusItem) {
  if (item.type === 'deck') return `${item.count} carte(s) mémoire à réviser`
  if (item.type === 'note') return 'Feuille blanche à restituer (Blurting)'
  return item.due_date ? `Devoir à terminer avant le ${new Date(item.due_date).toLocaleDateString('fr-FR')}` : 'Devoir sans date limite'
}

function studyItem(item: FocusItem) {
  if (item.type === 'deck') router.push(`/decks/${item.id}/study?focus=true`)
  else if (item.type === 'note') router.push(`/notes/${item.id}/blurting?focus=true&from=focus`)
  else if (item.type === 'assignment') router.push(`/bibliotheque/${item.id}`)
}

function continueReview() {
  const first = focusStore.startUnifiedReview()
  if (first) studyItem(first)
}

// ─── Charge à venir ────────────────────────────────────────────────────────
function getLoadBarClass(level: 'low' | 'medium' | 'high') {
  if (level === 'low') return 'bg-success/40'
  if (level === 'medium') return 'bg-warning/50'
  return 'bg-danger/50'
}

function getForecastBarHeight(count: number): number {
  const max = Math.max(...focusStore.forecast.map(f => f.count), 5)
  return Math.max(4, Math.round((count / max) * 100))
}

function getRetentionBarClass(pct: number) {
  if (pct < 50) return 'bg-danger'
  if (pct < 75) return 'bg-warning'
  return 'bg-success'
}

// ─── Objectif hebdomadaire ─────────────────────────────────────────────────
const weeklyStudySeconds = ref(0)
const weeklyGoalHours = ref(5)
const weeklyStudyHoursFormatted = computed(() => `${(weeklyStudySeconds.value / 3600).toFixed(1)}h`)
const weeklyGoalPercent = computed(() => {
  const target = weeklyGoalHours.value * 3600
  return target === 0 ? 0 : Math.min(100, Math.round((weeklyStudySeconds.value / target) * 100))
})
const weeklyGoalStatusText = computed(() => {
  const remaining = weeklyGoalHours.value * 3600 - weeklyStudySeconds.value
  if (remaining <= 0) return 'Objectif atteint pour cette semaine ! 🎉'
  return `Plus que ${(remaining / 3600).toFixed(1)}h pour atteindre votre objectif.`
})

function getStartAndEndOfWeek() {
  const now = new Date()
  const day = now.getDay()
  const diff = now.getDate() - day + (day === 0 ? -6 : 1)
  const startOfWeek = new Date(now.setDate(diff))
  startOfWeek.setHours(0, 0, 0, 0)
  const endOfWeek = new Date(startOfWeek)
  endOfWeek.setDate(startOfWeek.getDate() + 6)
  endOfWeek.setHours(23, 59, 59, 999)
  return { from: startOfWeek.toISOString().replace('Z', '+00:00'), to: endOfWeek.toISOString().replace('Z', '+00:00') }
}

// ─── Heatmap ───────────────────────────────────────────────────────────────
const heatmapData = ref<Record<string, { duration: number, count: number }>>({})
const totalSessionsCount = ref(0)

const gridStartDate = computed(() => {
  const today = new Date()
  const currentWeekSunday = new Date(today)
  currentWeekSunday.setDate(today.getDate() - today.getDay())
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
  const data = heatmapData.value[getCellDateStr(row, col)]
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
  const formattedDate = new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
  if (count === 0) return `${formattedDate} : Aucune session`
  return `${formattedDate} : ${count} session(s) (${Math.round(data.duration / 60)} min)`
}

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      focusStore.loadFocusData(),
      decksStore.fetchDecks(),
    ])
    const weekParams = getStartAndEndOfWeek()
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
          map[item.date] = { duration: item.duration, count: item.count }
          total += item.count
        })
        heatmapData.value = map
        totalSessionsCount.value = total
      }),
      api.get('/stats/sessions', { params: { from: weekParams.from, to: weekParams.to } }).then(res => {
        weeklyStudySeconds.value = res.data.reduce((acc: number, item: any) => acc + item.duration_seconds, 0)
      }),
    ])
  } catch (err) {
    console.error('Erreur lors du chargement de l\'accueil', err)
  } finally {
    loading.value = false
  }
})
</script>
