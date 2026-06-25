<template>
  <div class="space-y-6 max-w-3xl mx-auto animate-fade-in">
    <div class="flex items-center justify-between text-sm font-semibold">
      <button @click="goBack" class="text-ink-muted hover:text-primary dark:text-ink-subtle flex items-center gap-1">
        <ChevronLeft class="w-4 h-4" /> Retour
      </button>
      <span v-if="stats" class="text-xs font-bold text-primary bg-primary-soft dark:bg-primary-soft dark:text-primary px-2.5 py-1 rounded-lg uppercase tracking-wider">
        Stats · {{ stats.name }}
      </span>
    </div>

    <div v-if="loading" class="py-20 text-center text-sm font-semibold text-ink-subtle uppercase tracking-widest">Chargement des statistiques…</div>

    <template v-else-if="stats">
      <!-- KPIs -->
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <div v-for="kpi in kpis" :key="kpi.label" class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-2xl p-4">
          <p class="text-[10px] font-bold text-ink-subtle uppercase tracking-widest">{{ kpi.label }}</p>
          <p class="text-xl font-bold mt-1" :class="kpi.class || 'text-ink dark:text-white'">{{ kpi.value }}</p>
          <p v-if="kpi.hint" class="text-[10px] text-ink-subtle mt-0.5">{{ kpi.hint }}</p>
        </div>
      </div>

      <!-- Verdicts actionnables -->
      <div v-if="stats.verdicts.length" class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-2xl p-5 space-y-2">
        <p class="text-[10px] font-bold text-ink-subtle uppercase tracking-widest">À retenir</p>
        <ul class="space-y-1.5">
          <li v-for="(v, i) in stats.verdicts" :key="i" class="flex items-start gap-2 text-sm text-ink dark:text-ink-subtle">
            <span class="text-primary mt-0.5">›</span>{{ v }}
          </li>
        </ul>
      </div>

      <!-- Items -->
      <div class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-2xl p-5">
        <p class="text-[10px] font-bold text-ink-subtle uppercase tracking-widest mb-3">Éléments ({{ stats.items.length }})</p>
        <div class="space-y-2">
          <div v-for="it in stats.items" :key="it.item_id" class="border border-line dark:border-line rounded-xl">
            <div class="flex items-center gap-1 pr-2">
              <button @click="toggle(it.item_id)" class="flex-1 min-w-0 flex items-center justify-between gap-3 p-3 text-left">
                <span class="min-w-0 flex-1">
                  <span class="text-sm font-semibold text-ink dark:text-ink-subtle truncate block">{{ it.label }}</span>
                  <span class="flex flex-wrap gap-1.5 mt-1">
                    <span v-if="it.is_leech" class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-danger-soft text-danger dark:bg-danger-soft dark:text-danger">Sangsue</span>
                    <span v-if="it.is_mature" class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-success-soft text-success dark:bg-success-soft dark:text-success">Mûr</span>
                    <span v-if="it.due" class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-warning-soft text-warning dark:bg-warning-soft dark:text-warning">À réviser</span>
                  </span>
                </span>
                <span class="shrink-0 text-right">
                  <span class="text-xs font-bold" :class="it.success_rate >= 70 ? 'text-success' : it.reviews ? 'text-danger' : 'text-ink-subtle'">
                    {{ it.reviews ? `${it.success_rate}%` : '—' }}
                  </span>
                  <span class="block text-[10px] text-ink-subtle">D {{ it.difficulty }} · R {{ Math.round(it.retrievability * 100) }}%</span>
                </span>
              </button>
              <template v-if="canEdit">
                <button @click="openEdit(it.item_id)" class="shrink-0 p-1.5 text-ink-subtle hover:text-primary rounded-lg hover:bg-primary-soft transition-all" title="Modifier l'élément">
                  <Pencil class="w-4 h-4" />
                </button>
                <button @click="confirmDeleteItem(it.item_id)" class="shrink-0 p-1.5 text-ink-subtle hover:text-danger rounded-lg hover:bg-danger-soft transition-all" title="Supprimer l'élément">
                  <Trash2 class="w-4 h-4" />
                </button>
              </template>
            </div>

            <!-- Détail / courbe -->
            <div v-if="expanded === it.item_id" class="px-3 pb-3 border-t border-line-soft dark:border-line pt-3">
              <div v-if="detailLoading" class="text-xs text-ink-subtle text-center py-3">Chargement…</div>
              <div v-else-if="detail" class="space-y-3">
                <svg v-if="curvePoints.length" viewBox="0 0 300 70" class="w-full h-16 text-primary" preserveAspectRatio="none">
                  <line x1="0" :y1="yFor(3)" x2="300" :y2="yFor(3)" stroke="currentColor" class="text-ink-subtle dark:text-ink" stroke-width="1" stroke-dasharray="3 3" />
                  <polyline :points="polyline" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" />
                  <circle v-for="(p, i) in curvePoints" :key="i" :cx="p.x" :cy="p.y" r="3" :class="(detail.history[i].grade ?? 0) >= 3 ? 'text-success' : 'text-danger'" fill="currentColor" />
                </svg>
                <p v-else class="text-xs text-ink-subtle italic text-center py-2">Aucune révision enregistrée.</p>
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
                  <div><p class="text-[10px] text-ink-subtle uppercase">Révisions</p><p class="text-sm font-bold">{{ detail.reviews }}</p></div>
                  <div><p class="text-[10px] text-ink-subtle uppercase">Stabilité</p><p class="text-sm font-bold">{{ detail.stability_days }} j</p></div>
                  <div><p class="text-[10px] text-ink-subtle uppercase">Échecs</p><p class="text-sm font-bold">{{ detail.lapses }}</p></div>
                  <div><p class="text-[10px] text-ink-subtle uppercase">Maîtrise</p><p class="text-sm font-bold">{{ masteryText }}</p></div>
                </div>
              </div>
            </div>
          </div>

          <p v-if="stats.items.length === 0" class="text-center py-6 text-xs text-ink-subtle uppercase tracking-wider">Aucun élément dans cet ensemble.</p>
        </div>
      </div>
    </template>

    <RevisionItemModal
      v-if="showEditModal && editingItem"
      :binder-id="null"
      :decks="[]"
      :edit-item="editingItem"
      :locked-set-id="setId"
      :locked-type="stats?.type"
      @close="showEditModal = false"
      @updated="onItemSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useRevisionStore } from '../../stores/revision'
import type { SetStats, ItemStats, RevisionItem, RevisionSet } from '../../stores/revision'
import RevisionItemModal from '../../components/decks/RevisionItemModal.vue'
import { ChevronLeft, Pencil, Trash2 } from 'lucide-vue-next'

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
      console.error('Erreur de chargement de l\'ensemble', e)
    }
    await loadItems()
  } catch (e) {
    console.error('Erreur de chargement des stats', e)
  } finally {
    loading.value = false
  }
})

function openEdit(itemId: number) {
  const found = items.value.find(i => i.id === itemId)
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
    console.error('Erreur lors de la suppression de l\'élément', e)
    alert('Impossible de supprimer cet élément.')
  }
}

const kpis = computed(() => {
  const s = stats.value
  if (!s) return []
  return [
    { label: 'Maîtrise', value: `${s.mastery_rate}%`, hint: `${s.mastered_count}/${s.items_count} mûrs` },
    { label: 'Rétention réelle', value: `${s.true_retention}%`, class: s.true_retention && s.true_retention < 85 ? 'text-rose-500' : 'text-emerald-600', hint: 'cible 85%' },
    { label: 'Réussite moy.', value: `${s.avg_success_rate}%` },
    { label: 'À réviser', value: String(s.due_count), class: s.due_count ? 'text-amber-600' : undefined },
    { label: 'Sangsues', value: String(s.leeches_count), class: s.leeches_count ? 'text-rose-500' : undefined },
    { label: 'Difficulté moy.', value: `${s.avg_difficulty}/10` },
  ]
})

async function toggle(itemId: number) {
  if (expanded.value === itemId) { expanded.value = null; return }
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
const polyline = computed(() => curvePoints.value.map(p => `${p.x},${p.y}`).join(' '))

const masteryText = computed(() => {
  const d = detail.value
  if (!d) return '—'
  if (d.mastered) return 'Acquis'
  if (d.mastery_date) return new Date(d.mastery_date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })
  return '—'
})

function goBack() {
  router.back()
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.4s ease-out forwards; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
