<template>
  <div class="space-y-6 max-w-3xl mx-auto animate-fade-in">
    <div class="flex items-center justify-between text-sm font-semibold">
      <button @click="goBack" class="text-slate-500 hover:text-indigo-600 dark:text-slate-400 flex items-center gap-1">
        <ChevronLeft class="w-4 h-4" /> Retour
      </button>
      <span v-if="stats" class="text-xs font-bold text-indigo-500 bg-indigo-50 dark:bg-indigo-950/40 dark:text-indigo-400 px-2.5 py-1 rounded-lg uppercase tracking-wider">
        Stats · {{ stats.name }}
      </span>
    </div>

    <div v-if="loading" class="py-20 text-center text-sm font-semibold text-slate-400 uppercase tracking-widest">Chargement des statistiques…</div>

    <template v-else-if="stats">
      <!-- KPIs -->
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <div v-for="kpi in kpis" :key="kpi.label" class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-2xl p-4">
          <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{{ kpi.label }}</p>
          <p class="text-xl font-bold mt-1" :class="kpi.class || 'text-slate-800 dark:text-white'">{{ kpi.value }}</p>
          <p v-if="kpi.hint" class="text-[10px] text-slate-400 mt-0.5">{{ kpi.hint }}</p>
        </div>
      </div>

      <!-- Verdicts actionnables -->
      <div v-if="stats.verdicts.length" class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-2xl p-5 space-y-2">
        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">À retenir</p>
        <ul class="space-y-1.5">
          <li v-for="(v, i) in stats.verdicts" :key="i" class="flex items-start gap-2 text-sm text-slate-700 dark:text-slate-300">
            <span class="text-indigo-500 mt-0.5">›</span>{{ v }}
          </li>
        </ul>
      </div>

      <!-- Items -->
      <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-2xl p-5">
        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3">Éléments ({{ stats.items.length }})</p>
        <div class="space-y-2">
          <div v-for="it in stats.items" :key="it.item_id" class="border border-slate-100 dark:border-slate-800 rounded-xl">
            <button @click="toggle(it.item_id)" class="w-full flex items-center justify-between gap-3 p-3 text-left">
              <span class="min-w-0 flex-1">
                <span class="text-sm font-semibold text-slate-800 dark:text-slate-200 truncate block">{{ it.label }}</span>
                <span class="flex flex-wrap gap-1.5 mt-1">
                  <span v-if="it.is_leech" class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-rose-50 text-rose-600 dark:bg-rose-950/30 dark:text-rose-400">Sangsue</span>
                  <span v-if="it.is_mature" class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-600 dark:bg-emerald-950/30 dark:text-emerald-400">Mûr</span>
                  <span v-if="it.due" class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-amber-50 text-amber-600 dark:bg-amber-950/30 dark:text-amber-400">À réviser</span>
                </span>
              </span>
              <span class="shrink-0 text-right">
                <span class="text-xs font-bold" :class="it.success_rate >= 70 ? 'text-emerald-600' : it.reviews ? 'text-rose-500' : 'text-slate-400'">
                  {{ it.reviews ? `${it.success_rate}%` : '—' }}
                </span>
                <span class="block text-[10px] text-slate-400">D {{ it.difficulty }} · R {{ Math.round(it.retrievability * 100) }}%</span>
              </span>
            </button>

            <!-- Détail / courbe -->
            <div v-if="expanded === it.item_id" class="px-3 pb-3 border-t border-slate-50 dark:border-slate-800/60 pt-3">
              <div v-if="detailLoading" class="text-xs text-slate-400 text-center py-3">Chargement…</div>
              <div v-else-if="detail" class="space-y-3">
                <svg v-if="curvePoints.length" viewBox="0 0 300 70" class="w-full h-16 text-indigo-500" preserveAspectRatio="none">
                  <line x1="0" :y1="yFor(3)" x2="300" :y2="yFor(3)" stroke="currentColor" class="text-slate-200 dark:text-slate-700" stroke-width="1" stroke-dasharray="3 3" />
                  <polyline :points="polyline" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" />
                  <circle v-for="(p, i) in curvePoints" :key="i" :cx="p.x" :cy="p.y" r="3" :class="(detail.history[i].grade ?? 0) >= 3 ? 'text-emerald-500' : 'text-rose-500'" fill="currentColor" />
                </svg>
                <p v-else class="text-xs text-slate-400 italic text-center py-2">Aucune révision enregistrée.</p>
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
                  <div><p class="text-[10px] text-slate-400 uppercase">Révisions</p><p class="text-sm font-bold">{{ detail.reviews }}</p></div>
                  <div><p class="text-[10px] text-slate-400 uppercase">Stabilité</p><p class="text-sm font-bold">{{ detail.stability_days }} j</p></div>
                  <div><p class="text-[10px] text-slate-400 uppercase">Échecs</p><p class="text-sm font-bold">{{ detail.lapses }}</p></div>
                  <div><p class="text-[10px] text-slate-400 uppercase">Maîtrise</p><p class="text-sm font-bold">{{ masteryText }}</p></div>
                </div>
              </div>
            </div>
          </div>

          <p v-if="stats.items.length === 0" class="text-center py-6 text-xs text-slate-400 uppercase tracking-wider">Aucun élément dans cet ensemble.</p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useRevisionStore } from '../../stores/revision'
import type { SetStats, ItemStats } from '../../stores/revision'
import { ChevronLeft } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const revisionStore = useRevisionStore()

const setId = Number(route.params.id)
const loading = ref(true)
const stats = ref<SetStats | null>(null)
const expanded = ref<number | null>(null)
const detail = ref<ItemStats | null>(null)
const detailLoading = ref(false)

onMounted(async () => {
  try {
    stats.value = await revisionStore.fetchSetStats(setId)
  } catch (e) {
    console.error('Erreur de chargement des stats', e)
  } finally {
    loading.value = false
  }
})

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
