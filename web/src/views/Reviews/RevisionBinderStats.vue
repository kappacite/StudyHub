<template>
  <div class="space-y-6 max-w-3xl mx-auto animate-fade-in">
    <div class="flex items-center justify-between text-sm font-semibold">
      <button @click="goBack" class="text-ink-muted hover:text-primary dark:text-ink-subtle flex items-center gap-1">
        <ChevronLeft class="w-4 h-4" /> Retour
      </button>
      <span v-if="stats" class="text-xs font-bold text-primary bg-primary-soft dark:bg-primary-soft dark:text-primary px-2.5 py-1 rounded-lg uppercase tracking-wider">
        Stats classeur · {{ stats.name }}
      </span>
    </div>

    <div v-if="loading" class="py-20 text-center text-sm font-semibold text-ink-subtle uppercase tracking-widest">Chargement des statistiques…</div>

    <template v-else-if="stats">
      <!-- Inclure le sous-arbre -->
      <label class="flex items-center gap-2 text-xs font-semibold text-ink-muted dark:text-ink-subtle cursor-pointer">
        <input type="checkbox" v-model="includeDescendants" @change="reload" class="rounded border-line text-primary focus:ring-primary" />
        Inclure les sous-classeurs
      </label>

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

      <!-- Répartition par type -->
      <div v-if="stats.by_type.length" class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-2xl p-5">
        <p class="text-[10px] font-bold text-ink-subtle uppercase tracking-widest mb-3">Répartition par type</p>
        <div class="space-y-2">
          <div v-for="bt in stats.by_type" :key="bt.type" class="flex items-center gap-3">
            <span class="w-24 shrink-0 text-xs font-semibold text-ink-muted dark:text-ink-subtle">{{ typeLabel(bt.type) }}</span>
            <div class="flex-1 h-2 rounded-full bg-surface-soft dark:bg-surface-soft overflow-hidden">
              <div class="h-full bg-primary rounded-full" :style="{ width: `${bt.mastery_rate}%` }"></div>
            </div>
            <span class="shrink-0 text-[11px] text-ink-subtle w-28 text-right">{{ bt.mastered_count }}/{{ bt.items_count }} mûrs · {{ bt.sets_count }} ens.</span>
          </div>
        </div>
      </div>

      <!-- Ensembles les plus à risque -->
      <div v-if="stats.weakest_sets.length" class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-2xl p-5">
        <p class="text-[10px] font-bold text-ink-subtle uppercase tracking-widest mb-3">À surveiller en priorité</p>
        <div class="space-y-2">
          <button v-for="s in stats.weakest_sets" :key="s.set_id" @click="openSet(s.set_id)"
                  class="w-full flex items-center justify-between gap-3 p-3 text-left border border-line dark:border-line rounded-xl hover:border-primary dark:hover:border-primary transition-colors">
            <span class="min-w-0 flex-1">
              <span class="text-sm font-semibold text-ink dark:text-ink-subtle truncate block">{{ s.name }}</span>
              <span class="flex flex-wrap gap-1.5 mt-1">
                <span v-if="s.leeches_count" class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-danger-soft text-danger dark:bg-danger-soft dark:text-danger">{{ s.leeches_count }} sangsue(s)</span>
                <span v-if="s.due_count" class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-warning-soft text-warning dark:bg-warning-soft dark:text-warning">{{ s.due_count }} à réviser</span>
                <span class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-surface-soft text-ink-muted dark:bg-surface-soft dark:text-ink-subtle">{{ typeLabel(s.type) }}</span>
              </span>
            </span>
            <span class="shrink-0 text-right">
              <span class="text-xs font-bold" :class="s.mastery_rate >= 70 ? 'text-success' : 'text-danger'">{{ s.mastery_rate }}%</span>
              <span class="block text-[10px] text-ink-subtle">maîtrise</span>
            </span>
          </button>
        </div>
      </div>

      <!-- Tous les ensembles -->
      <div class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-2xl p-5">
        <p class="text-[10px] font-bold text-ink-subtle uppercase tracking-widest mb-3">Ensembles ({{ stats.sets.length }})</p>
        <div class="space-y-2">
          <button v-for="s in stats.sets" :key="s.set_id" @click="openSet(s.set_id)"
                  class="w-full flex items-center justify-between gap-3 p-3 text-left border border-line dark:border-line rounded-xl hover:border-primary dark:hover:border-primary transition-colors">
            <span class="min-w-0 flex-1">
              <span class="text-sm font-semibold text-ink dark:text-ink-subtle truncate block">{{ s.name }}</span>
              <span class="text-[10px] text-ink-subtle">{{ typeLabel(s.type) }} · {{ s.items_count }} élément(s)</span>
            </span>
            <span class="shrink-0 text-right">
              <span class="text-xs font-bold" :class="s.reviewed_items ? (s.mastery_rate >= 70 ? 'text-success' : 'text-danger') : 'text-ink-subtle'">
                {{ s.reviewed_items ? `${s.mastery_rate}%` : '—' }}
              </span>
              <span class="block text-[10px] text-ink-subtle">maîtrise</span>
            </span>
          </button>

          <p v-if="stats.sets.length === 0" class="text-center py-6 text-xs text-ink-subtle uppercase tracking-wider">Aucun ensemble de révision dans ce classeur.</p>
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
