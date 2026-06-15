<template>
  <div class="space-y-6 max-w-3xl mx-auto animate-fade-in">
    <div class="flex items-center justify-between text-sm font-semibold">
      <button @click="goBack" class="text-slate-500 hover:text-indigo-600 dark:text-slate-400 flex items-center gap-1">
        <ChevronLeft class="w-4 h-4" /> Retour
      </button>
      <span v-if="stats" class="text-xs font-bold text-indigo-500 bg-indigo-50 dark:bg-indigo-950/40 dark:text-indigo-400 px-2.5 py-1 rounded-lg uppercase tracking-wider">
        Stats classeur · {{ stats.name }}
      </span>
    </div>

    <div v-if="loading" class="py-20 text-center text-sm font-semibold text-slate-400 uppercase tracking-widest">Chargement des statistiques…</div>

    <template v-else-if="stats">
      <!-- Inclure le sous-arbre -->
      <label class="flex items-center gap-2 text-xs font-semibold text-slate-500 dark:text-slate-400 cursor-pointer">
        <input type="checkbox" v-model="includeDescendants" @change="reload" class="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
        Inclure les sous-classeurs
      </label>

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

      <!-- Répartition par type -->
      <div v-if="stats.by_type.length" class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-2xl p-5">
        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3">Répartition par type</p>
        <div class="space-y-2">
          <div v-for="bt in stats.by_type" :key="bt.type" class="flex items-center gap-3">
            <span class="w-24 shrink-0 text-xs font-semibold text-slate-600 dark:text-slate-300">{{ typeLabel(bt.type) }}</span>
            <div class="flex-1 h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
              <div class="h-full bg-indigo-500 rounded-full" :style="{ width: `${bt.mastery_rate}%` }"></div>
            </div>
            <span class="shrink-0 text-[11px] text-slate-400 w-28 text-right">{{ bt.mastered_count }}/{{ bt.items_count }} mûrs · {{ bt.sets_count }} ens.</span>
          </div>
        </div>
      </div>

      <!-- Ensembles les plus à risque -->
      <div v-if="stats.weakest_sets.length" class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-2xl p-5">
        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3">À surveiller en priorité</p>
        <div class="space-y-2">
          <button v-for="s in stats.weakest_sets" :key="s.set_id" @click="openSet(s.set_id)"
                  class="w-full flex items-center justify-between gap-3 p-3 text-left border border-slate-100 dark:border-slate-800 rounded-xl hover:border-indigo-300 dark:hover:border-indigo-700 transition-colors">
            <span class="min-w-0 flex-1">
              <span class="text-sm font-semibold text-slate-800 dark:text-slate-200 truncate block">{{ s.name }}</span>
              <span class="flex flex-wrap gap-1.5 mt-1">
                <span v-if="s.leeches_count" class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-rose-50 text-rose-600 dark:bg-rose-950/30 dark:text-rose-400">{{ s.leeches_count }} sangsue(s)</span>
                <span v-if="s.due_count" class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-amber-50 text-amber-600 dark:bg-amber-950/30 dark:text-amber-400">{{ s.due_count }} à réviser</span>
                <span class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400">{{ typeLabel(s.type) }}</span>
              </span>
            </span>
            <span class="shrink-0 text-right">
              <span class="text-xs font-bold" :class="s.mastery_rate >= 70 ? 'text-emerald-600' : 'text-rose-500'">{{ s.mastery_rate }}%</span>
              <span class="block text-[10px] text-slate-400">maîtrise</span>
            </span>
          </button>
        </div>
      </div>

      <!-- Tous les ensembles -->
      <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-2xl p-5">
        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3">Ensembles ({{ stats.sets.length }})</p>
        <div class="space-y-2">
          <button v-for="s in stats.sets" :key="s.set_id" @click="openSet(s.set_id)"
                  class="w-full flex items-center justify-between gap-3 p-3 text-left border border-slate-100 dark:border-slate-800 rounded-xl hover:border-indigo-300 dark:hover:border-indigo-700 transition-colors">
            <span class="min-w-0 flex-1">
              <span class="text-sm font-semibold text-slate-800 dark:text-slate-200 truncate block">{{ s.name }}</span>
              <span class="text-[10px] text-slate-400">{{ typeLabel(s.type) }} · {{ s.items_count }} élément(s)</span>
            </span>
            <span class="shrink-0 text-right">
              <span class="text-xs font-bold" :class="s.reviewed_items ? (s.mastery_rate >= 70 ? 'text-emerald-600' : 'text-rose-500') : 'text-slate-400'">
                {{ s.reviewed_items ? `${s.mastery_rate}%` : '—' }}
              </span>
              <span class="block text-[10px] text-slate-400">maîtrise</span>
            </span>
          </button>

          <p v-if="stats.sets.length === 0" class="text-center py-6 text-xs text-slate-400 uppercase tracking-wider">Aucun ensemble de révision dans ce classeur.</p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useRevisionStore } from '../../stores/revision'
import type { BinderStats, RevisionType } from '../../stores/revision'
import { ChevronLeft } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const revisionStore = useRevisionStore()

const binderId = String(route.params.id)
const loading = ref(true)
const stats = ref<BinderStats | null>(null)
const includeDescendants = ref(true)

const TYPE_LABELS: Record<RevisionType, string> = {
  qcm: 'QCM', vf: 'Vrai/Faux', association: 'Association', definition: 'Définition', ordre: 'Ordre',
}
function typeLabel(t: RevisionType): string {
  return TYPE_LABELS[t] || t
}

async function reload() {
  loading.value = true
  try {
    stats.value = await revisionStore.fetchBinderStats(binderId, includeDescendants.value)
  } catch (e) {
    console.error('Erreur de chargement des stats du classeur', e)
  } finally {
    loading.value = false
  }
}

onMounted(reload)

const kpis = computed(() => {
  const s = stats.value
  if (!s) return []
  return [
    { label: 'Maîtrise', value: `${s.mastery_rate}%`, hint: `${s.mastered_count}/${s.items_count} mûrs` },
    { label: 'Rétention réelle', value: `${s.true_retention}%`, class: s.true_retention && s.true_retention < 85 ? 'text-rose-500' : 'text-emerald-600', hint: 'cible 85%' },
    { label: 'Réussite moy.', value: `${s.avg_success_rate}%` },
    { label: 'Ensembles', value: String(s.sets_count), hint: `${s.items_count} élément(s)` },
    { label: 'À réviser', value: String(s.due_count), class: s.due_count ? 'text-amber-600' : undefined },
    { label: 'Sangsues', value: String(s.leeches_count), class: s.leeches_count ? 'text-rose-500' : undefined },
  ]
})

function openSet(setId: number) {
  router.push(`/revision/sets/${setId}/stats`)
}

function goBack() {
  router.back()
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.4s ease-out forwards; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
