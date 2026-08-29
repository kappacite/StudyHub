<template>
  <PageContainer>
    <div
      v-if="loading"
      class="py-20 text-center text-sm font-semibold text-ink-subtle uppercase tracking-widest"
    >
      Chargement des statistiques…
    </div>

    <template v-else-if="stats">
      <!-- En-tête -->
      <div class="flex items-end justify-between gap-5 flex-wrap">
        <div class="min-w-0">
          <p class="font-mono text-[11px] tracking-wide text-ink-subtle uppercase mb-1.5">
            Réviser · Statistiques
          </p>
          <div class="flex items-center gap-2 flex-wrap">
            <h1 class="font-display text-display-lg text-ink truncate">{{ stats.name }}</h1>
            <span
              data-test="set-type-badge"
              class="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-surface-soft text-ink-muted shrink-0"
            >
              {{ setTypeLabel }}
            </span>
          </div>
          <p class="text-sm text-ink-muted mt-1.5">{{ subtitleText }}</p>
        </div>
        <BaseButton data-test="study-set-button" @click="studySet">
          <template #icon><Play class="w-4 h-4" /></template>
          Réviser cette série
        </BaseButton>
      </div>

      <!-- Grille principale : réussite + progression -->
      <div class="grid grid-cols-1 lg:grid-cols-[1fr_1.4fr] gap-6 items-start">
        <!-- Taux de réussite global -->
        <BaseCard padding="lg" class="flex flex-col gap-5">
          <h3 class="text-xs font-bold uppercase tracking-wide text-ink-subtle">
            Taux de réussite global
          </h3>
          <div class="flex items-baseline gap-2">
            <span class="font-display font-mono text-5xl font-bold text-primary leading-none">{{
              Math.round(stats.avg_success_rate)
            }}</span>
            <span class="font-display text-2xl font-bold text-primary">%</span>
          </div>
          <p class="text-xs text-ink-muted leading-relaxed">
            Sur {{ stats.reviewed_items }}/{{ stats.items_count }} élément(s) révisé(s). Difficulté
            moyenne : <span class="font-mono">{{ stats.avg_difficulty }}/10</span>.
          </p>

          <div class="border-t border-dashed border-line pt-4">
            <p class="text-[11px] font-bold uppercase tracking-wide text-ink-subtle mb-2.5">
              Par notation SM2
            </p>
            <div class="flex items-end gap-2 h-16">
              <div
                v-for="bar in gradeBars"
                :key="bar.key"
                data-test="grade-bar"
                class="w-5 rounded-sm"
                :class="bar.colorClass"
                :style="{ height: bar.heightPct + '%' }"
              />
            </div>
            <div class="flex gap-2 mt-1.5 font-mono text-[9px] text-ink-subtle">
              <span v-for="bar in gradeBars" :key="bar.key" class="w-5 text-center">{{
                bar.label
              }}</span>
            </div>
          </div>
        </BaseCard>

        <!-- Progression dans le temps -->
        <BaseCard padding="lg">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-xs font-bold uppercase tracking-wide text-ink-subtle">
              Progression dans le temps
            </h3>
            <span class="font-mono text-[11px] text-ink-subtle">6 dernières semaines</span>
          </div>
          <div class="flex items-end gap-2.5 h-28">
            <div
              v-for="(week, i) in stats.weekly_progression"
              :key="i"
              data-test="week-bar"
              class="w-6 rounded-sm"
              :class="weekBarColorClass(week)"
              :style="{ height: weekBarHeight(week) + '%' }"
            />
          </div>
          <div class="flex gap-2.5 mt-2 font-mono text-[9px] text-ink-subtle">
            <span v-for="(_, i) in stats.weekly_progression" :key="i" class="w-6 text-center"
              >S{{ i + 1 }}</span
            >
          </div>

          <div class="border-t border-dashed border-line mt-5 pt-4 grid grid-cols-2 gap-4">
            <div>
              <p class="font-mono text-xl font-bold text-primary">
                {{ stats.mastered_count }}/{{ stats.items_count }}
              </p>
              <p class="text-xs text-ink-muted">Cartes mûres</p>
            </div>
            <div>
              <p class="font-mono text-xl font-bold text-primary">{{ totalReviews }}</p>
              <p class="text-xs text-ink-muted">Révisions totales</p>
            </div>
          </div>
        </BaseCard>
      </div>

      <!-- Verdicts actionnables -->
      <BaseCard v-if="stats.verdicts.length" padding="lg" class="space-y-2">
        <p class="text-[10px] font-bold text-ink-subtle uppercase tracking-widest">À retenir</p>
        <ul class="space-y-1.5">
          <li
            v-for="(v, i) in stats.verdicts"
            :key="i"
            class="flex items-start gap-2 text-sm text-ink dark:text-ink-subtle"
          >
            <span class="text-primary mt-0.5">›</span>{{ v }}
          </li>
        </ul>
      </BaseCard>

      <!-- Historique des sessions -->
      <BaseCard padding="lg">
        <h3 class="font-display text-base font-bold text-ink mb-4">Historique des sessions</h3>
        <p
          v-if="stats.session_history.length === 0"
          class="text-center py-6 text-xs text-ink-subtle uppercase tracking-wider"
        >
          Aucune session enregistrée.
        </p>
        <div v-else class="flex flex-col">
          <div class="grid grid-cols-3 gap-3.5 pb-2.5 border-b border-line">
            <span class="font-mono text-[10px] uppercase tracking-wide text-ink-subtle">Date</span>
            <span class="font-mono text-[10px] uppercase tracking-wide text-ink-subtle"
              >Cartes vues</span
            >
            <span class="font-mono text-[10px] uppercase tracking-wide text-ink-subtle">Score</span>
          </div>
          <div
            v-for="day in stats.session_history"
            :key="day.date"
            data-test="session-history-row"
            class="grid grid-cols-3 gap-3.5 items-center py-3 border-b border-dashed border-line last:border-0"
          >
            <span class="text-sm text-ink">{{ formatDay(day.date) }}</span>
            <span class="font-mono text-sm text-ink-muted">{{ day.reviews }}</span>
            <span
              data-test="session-score"
              class="font-mono text-sm font-bold"
              :class="successRateTextClass(day.success_rate)"
              >{{ day.success_rate }}%</span
            >
          </div>
        </div>
      </BaseCard>
    </template>
  </PageContainer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useRevisionStore } from '../../stores/revision'
import type {
  SetStats,
  RevisionSet,
  GradeDistribution,
  WeeklyProgressionPoint,
} from '../../stores/revision'
import PageContainer from '../../components/ui/base/PageContainer.vue'
import BaseCard from '../../components/ui/base/BaseCard.vue'
import BaseButton from '../../components/ui/base/BaseButton.vue'
import { Play } from 'lucide-vue-next'
import { REVISION_ITEM_TYPE_META } from '../../utils/revisionItemTypeMeta'
import { successRateTextClass, successRateBgClass } from '../../utils/successRate'

const router = useRouter()
const route = useRoute()
const revisionStore = useRevisionStore()

const setId = Number(route.params.id)
const loading = ref(true)
const stats = ref<SetStats | null>(null)

// Description de l'ensemble (sous-titre uniquement -- l'edition des elements
// vit desormais sur RevisionSetDetail.vue / RevisionSetTypeItems.vue, pas ici :
// cette page reconstruit RevisionSetStats.dc.html a l'identique, qui ne
// montre aucune liste d'elements).
const setMeta = ref<RevisionSet | null>(null)
const setTypeLabel = computed(() => {
  const t = stats.value?.type
  return t ? REVISION_ITEM_TYPE_META[t].label : 'Mixte'
})

const subtitleText = computed(() => {
  const s = stats.value
  if (!s) return ''
  const count = `${s.items_count} élément${s.items_count > 1 ? 's' : ''}`
  const desc = setMeta.value?.description
  return desc ? `Série de ${count} · ${desc}` : `Série de ${count}`
})

// Par notation SM2 (0-5, cf. invariants-sm2) : encore/difficile/bien/facile.
// Mêmes tokens sémantiques que le reste du design system (cf. skill
// design-system : primary = « Bien », accent = « Difficile », success =
// « Facile », danger = « Encore »).
const GRADE_BAR_META = [
  { key: 'again', label: 'Enc.', colorClass: 'bg-danger' },
  { key: 'hard', label: 'Diff.', colorClass: 'bg-accent' },
  { key: 'good', label: 'Bien', colorClass: 'bg-primary' },
  { key: 'easy', label: 'Fac.', colorClass: 'bg-success' },
] as const

const gradeBars = computed(() => {
  const dist = stats.value?.grade_distribution
  if (!dist) return []
  const counts = GRADE_BAR_META.map((m) => dist[m.key as keyof GradeDistribution])
  const max = Math.max(1, ...counts)
  return GRADE_BAR_META.map((m, i) => ({
    ...m,
    count: counts[i],
    heightPct: counts[i] ? Math.max(8, Math.round((counts[i] / max) * 100)) : 0,
  }))
})

const totalReviews = computed(() => {
  const d = stats.value?.grade_distribution
  if (!d) return 0
  return d.again + d.hard + d.good + d.easy
})

function weekBarHeight(week: WeeklyProgressionPoint): number {
  if (!week.reviews) return 0
  return Math.max(8, Math.round(week.success_rate))
}

// Banding taux de reussite/maitrise : seuil unique partage via utils/successRate.ts
// (cf. sa doc -- evite qu'une nouvelle vue reinvente un troisieme seuil).
function weekBarColorClass(week: WeeklyProgressionPoint): string {
  if (!week.reviews) return 'bg-line'
  return successRateBgClass(week.success_rate)
}

function formatDay(iso: string): string {
  const d = new Date(`${iso}T00:00:00`)
  return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
}

function studySet() {
  router.push(`/revision/sets/${setId}/study`)
}

onMounted(async () => {
  try {
    stats.value = await revisionStore.fetchSetStats(setId)
    try {
      setMeta.value = await revisionStore.fetchSet(setId)
    } catch (e) {
      console.error("Erreur de chargement de l'ensemble", e)
    }
  } catch (e) {
    console.error('Erreur de chargement des stats', e)
  } finally {
    loading.value = false
  }
})
</script>
