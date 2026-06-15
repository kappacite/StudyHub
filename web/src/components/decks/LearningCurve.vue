<template>
  <div class="space-y-2">
    <div class="flex items-center justify-between">
      <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Courbe d'apprentissage</span>
      <span class="text-[10px] text-slate-400">{{ points.length }} révision{{ points.length > 1 ? 's' : '' }}</span>
    </div>

    <div v-if="points.length === 0" class="text-xs text-slate-400 italic py-3 text-center">
      Aucune révision pour l'instant.
    </div>

    <svg v-else :viewBox="`0 0 ${W} ${H}`" class="w-full h-24" preserveAspectRatio="none">
      <!-- Seuil de réussite (grade 3) -->
      <line :x1="0" :y1="yFor(3)" :x2="W" :y2="yFor(3)" stroke="currentColor" class="text-slate-200 dark:text-slate-700" stroke-width="1" stroke-dasharray="3 3" />
      <!-- Ligne de progression -->
      <polyline
        :points="polyline"
        fill="none"
        stroke="currentColor"
        class="text-indigo-500"
        stroke-width="2"
        stroke-linejoin="round"
        stroke-linecap="round"
      />
      <!-- Points (vert si réussi ≥ 3, rose sinon) -->
      <circle
        v-for="(p, i) in coords"
        :key="i"
        :cx="p.x"
        :cy="p.y"
        r="3"
        :class="(points[i].grade ?? 0) >= 3 ? 'text-emerald-500' : 'text-rose-500'"
        fill="currentColor"
      />
    </svg>

    <div v-if="points.length" class="flex items-center justify-between text-[10px] text-slate-400">
      <span>Échelle SM-2 : 0 (oubli) → 5 (facile)</span>
      <span>Réussite moyenne : {{ averageGrade }}/5</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CardHistoryEntry } from '../../stores/decks'

const props = defineProps<{ entries: CardHistoryEntry[] }>()

const W = 300
const H = 80
const PAD = 8

// On ne garde que les révisions notées.
const points = computed(() => props.entries.filter(e => e.grade !== null && e.grade !== undefined))

function yFor(grade: number): number {
  // grade 0..5 mappé sur la hauteur (5 en haut, 0 en bas).
  return PAD + (1 - grade / 5) * (H - 2 * PAD)
}

const coords = computed(() => {
  const n = points.value.length
  if (n === 0) return []
  return points.value.map((e, i) => ({
    x: n === 1 ? W / 2 : PAD + (i / (n - 1)) * (W - 2 * PAD),
    y: yFor(e.grade ?? 0),
  }))
})

const polyline = computed(() => coords.value.map(p => `${p.x},${p.y}`).join(' '))

const averageGrade = computed(() => {
  if (points.value.length === 0) return '0'
  const sum = points.value.reduce((acc, e) => acc + (e.grade ?? 0), 0)
  return (sum / points.value.length).toFixed(1)
})
</script>
