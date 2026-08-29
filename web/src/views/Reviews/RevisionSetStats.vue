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
              >Révisions</span
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
            <span class="font-mono text-sm font-bold" :class="scoreClass(day.success_rate)"
              >{{ day.success_rate }}%</span
            >
          </div>
        </div>
      </BaseCard>

      <!-- Éléments (gestion) -->
      <BaseCard padding="lg">
        <p class="text-[10px] font-bold text-ink-subtle uppercase tracking-widest mb-3">
          Éléments ({{ stats.items.length }})
        </p>
        <div class="space-y-2">
          <div
            v-for="it in stats.items"
            :key="it.item_id"
            class="border border-line dark:border-line rounded-xl"
          >
            <div class="flex items-center gap-1 pr-2">
              <button
                class="flex-1 min-w-0 flex items-center justify-between gap-3 p-3 text-left"
                @click="toggle(it.item_id)"
              >
                <span class="min-w-0 flex-1">
                  <span
                    class="text-sm font-semibold text-ink dark:text-ink-subtle flex items-center gap-1.5"
                  >
                    <component
                      :is="REVISION_ITEM_TYPE_META[it.type].icon"
                      data-test="item-type-icon"
                      class="w-3.5 h-3.5 text-ink-subtle shrink-0"
                    />
                    <span class="truncate">{{ it.label }}</span>
                  </span>
                  <span class="flex flex-wrap gap-1.5 mt-1">
                    <span
                      v-if="it.is_leech"
                      class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-danger-soft text-danger"
                      >Sangsue</span
                    >
                    <span
                      v-if="it.is_mature"
                      class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-success-soft text-success"
                      >Mûr</span
                    >
                    <span
                      v-if="it.due"
                      class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-warning-soft text-warning"
                      >À réviser</span
                    >
                  </span>
                </span>
                <span class="shrink-0 text-right">
                  <span
                    class="text-xs font-bold"
                    :class="
                      it.success_rate >= 70
                        ? 'text-success'
                        : it.reviews
                          ? 'text-danger'
                          : 'text-ink-subtle'
                    "
                  >
                    {{ it.reviews ? `${it.success_rate}%` : '—' }}
                  </span>
                  <span class="block text-[10px] text-ink-subtle"
                    >D {{ it.difficulty }} · R {{ Math.round(it.retrievability * 100) }}%</span
                  >
                </span>
              </button>
              <template v-if="canEdit">
                <button
                  :data-test="`edit-item-${it.item_id}`"
                  class="shrink-0 p-1.5 text-ink-subtle hover:text-primary rounded-lg hover:bg-primary-soft transition-all"
                  title="Modifier l'élément"
                  @click="openEdit(it.item_id)"
                >
                  <Pencil class="w-4 h-4" />
                </button>
                <button
                  class="shrink-0 p-1.5 text-ink-subtle hover:text-danger rounded-lg hover:bg-danger-soft transition-all"
                  title="Supprimer l'élément"
                  @click="confirmDeleteItem(it.item_id)"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </template>
            </div>

            <!-- Détail / courbe -->
            <div
              v-if="expanded === it.item_id"
              class="px-3 pb-3 border-t border-line-soft dark:border-line pt-3"
            >
              <div v-if="detailLoading" class="text-xs text-ink-subtle text-center py-3">
                Chargement…
              </div>
              <div v-else-if="detail" class="space-y-3">
                <svg
                  v-if="curvePoints.length"
                  viewBox="0 0 300 70"
                  class="w-full h-16 text-primary"
                  preserveAspectRatio="none"
                >
                  <line
                    x1="0"
                    :y1="yFor(3)"
                    x2="300"
                    :y2="yFor(3)"
                    stroke="currentColor"
                    class="text-ink-subtle dark:text-ink"
                    stroke-width="1"
                    stroke-dasharray="3 3"
                  />
                  <polyline
                    :points="polyline"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linejoin="round"
                  />
                  <circle
                    v-for="(p, i) in curvePoints"
                    :key="i"
                    :cx="p.x"
                    :cy="p.y"
                    r="3"
                    :class="(detail.history[i].grade ?? 0) >= 3 ? 'text-success' : 'text-danger'"
                    fill="currentColor"
                  />
                </svg>
                <p v-else class="text-xs text-ink-subtle italic text-center py-2">
                  Aucune révision enregistrée.
                </p>
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
                  <div>
                    <p class="text-[10px] text-ink-subtle uppercase">Révisions</p>
                    <p class="text-sm font-bold">{{ detail.reviews }}</p>
                  </div>
                  <div>
                    <p class="text-[10px] text-ink-subtle uppercase">Stabilité</p>
                    <p class="text-sm font-bold">{{ detail.stability_days }} j</p>
                  </div>
                  <div>
                    <p class="text-[10px] text-ink-subtle uppercase">Échecs</p>
                    <p class="text-sm font-bold">{{ detail.lapses }}</p>
                  </div>
                  <div>
                    <p class="text-[10px] text-ink-subtle uppercase">Maîtrise</p>
                    <p class="text-sm font-bold">{{ masteryText }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <p
            v-if="stats.items.length === 0"
            class="text-center py-6 text-xs text-ink-subtle uppercase tracking-wider"
          >
            Aucun élément dans cet ensemble.
          </p>
        </div>
      </BaseCard>
    </template>

    <RevisionItemModal
      v-if="showEditModal && editingItem"
      :binder-id="null"
      :decks="[]"
      :edit-item="editingItem"
      :locked-set-id="setId"
      @close="showEditModal = false"
      @updated="onItemSaved"
    />
  </PageContainer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useRevisionStore } from '../../stores/revision'
import type {
  SetStats,
  ItemStats,
  RevisionItem,
  RevisionSet,
  GradeDistribution,
  WeeklyProgressionPoint,
} from '../../stores/revision'
import RevisionItemModal from '../../components/decks/RevisionItemModal.vue'
import PageContainer from '../../components/ui/base/PageContainer.vue'
import BaseCard from '../../components/ui/base/BaseCard.vue'
import BaseButton from '../../components/ui/base/BaseButton.vue'
import { Play, Pencil, Trash2 } from 'lucide-vue-next'
import { REVISION_ITEM_TYPE_META } from '../../utils/revisionItemTypeMeta'

const router = useRouter()
const route = useRoute()
const revisionStore = useRevisionStore()

const setId = Number(route.params.id)
const loading = ref(true)
const stats = ref<SetStats | null>(null)
const expanded = ref<number | null>(null)
const detail = ref<ItemStats | null>(null)
const detailLoading = ref(false)

// Édition des éléments (réservée aux ensembles éditables, càd non partagés).
const setMeta = ref<RevisionSet | null>(null)
const items = ref<RevisionItem[]>([])
const editingItem = ref<RevisionItem | null>(null)
const showEditModal = ref(false)
const canEdit = computed(() => !!setMeta.value && !setMeta.value.read_only)
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

function weekBarColorClass(week: WeeklyProgressionPoint): string {
  if (!week.reviews) return 'bg-line'
  if (week.success_rate >= 90) return 'bg-success'
  if (week.success_rate >= 75) return 'bg-primary'
  if (week.success_rate >= 50) return 'bg-accent'
  return 'bg-danger'
}

function formatDay(iso: string): string {
  const d = new Date(`${iso}T00:00:00`)
  return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
}

function scoreClass(rate: number): string {
  if (rate >= 85) return 'text-success'
  if (rate >= 60) return 'text-accent'
  return 'text-danger'
}

function studySet() {
  router.push(`/revision/sets/${setId}/study`)
}

async function loadItems() {
  if (canEdit.value) {
    try {
      items.value = await revisionStore.fetchItems(setId)
    } catch (e) {
      console.error('Erreur de chargement des éléments', e)
    }
  }
}

onMounted(async () => {
  try {
    stats.value = await revisionStore.fetchSetStats(setId)
    try {
      setMeta.value = await revisionStore.fetchSet(setId)
    } catch (e) {
      console.error("Erreur de chargement de l'ensemble", e)
    }
    await loadItems()
  } catch (e) {
    console.error('Erreur de chargement des stats', e)
  } finally {
    loading.value = false
  }
})

function openEdit(itemId: number) {
  const found = items.value.find((i) => i.id === itemId)
  if (!found) return
  editingItem.value = found
  showEditModal.value = true
}

async function onItemSaved() {
  showEditModal.value = false
  editingItem.value = null
  stats.value = await revisionStore.fetchSetStats(setId)
  await loadItems()
}

async function confirmDeleteItem(itemId: number) {
  if (!confirm('Supprimer cet élément de révision ? Cette action est définitive.')) return
  try {
    await revisionStore.deleteItem(setId, itemId)
    if (expanded.value === itemId) expanded.value = null
    stats.value = await revisionStore.fetchSetStats(setId)
    await loadItems()
  } catch (e) {
    console.error("Erreur lors de la suppression de l'élément", e)
    alert('Impossible de supprimer cet élément.')
  }
}

async function toggle(itemId: number) {
  if (expanded.value === itemId) {
    expanded.value = null
    return
  }
  expanded.value = itemId
  detail.value = null
  detailLoading.value = true
  try {
    detail.value = await revisionStore.fetchItemStats(itemId)
  } catch (e) {
    console.error('Erreur de chargement du détail', e)
  } finally {
    detailLoading.value = false
  }
}

function yFor(grade: number): number {
  return 8 + (1 - grade / 5) * (70 - 16)
}
const curvePoints = computed(() => {
  const h = detail.value?.history || []
  if (!h.length) return []
  return h.map((e, i) => ({
    x: h.length === 1 ? 150 : 8 + (i / (h.length - 1)) * (300 - 16),
    y: yFor(e.grade ?? 0),
  }))
})
const polyline = computed(() => curvePoints.value.map((p) => `${p.x},${p.y}`).join(' '))

const masteryText = computed(() => {
  const d = detail.value
  if (!d) return '—'
  if (d.mastered) return 'Acquis'
  if (d.mastery_date)
    return new Date(d.mastery_date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })
  return '—'
})
</script>
