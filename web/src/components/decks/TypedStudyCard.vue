<template>
  <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 p-8 rounded-3xl min-h-[320px] flex flex-col">
    <span class="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">{{ typeLabel }}</span>

    <!-- QCM -->
    <template v-if="card.card_type === 'qcm'">
      <p class="text-lg font-bold text-slate-800 dark:text-slate-100 mt-3 mb-5">{{ card.payload?.question }}</p>
      <div class="space-y-2.5 flex-1">
        <button
          v-for="opt in card.payload?.options || []"
          :key="opt.id"
          type="button"
          :disabled="revealed"
          @click="selected = opt.id"
          class="w-full text-left px-4 py-3 rounded-xl border text-sm font-semibold transition-all disabled:cursor-default"
          :class="optionClass(opt.id, opt.correct)"
        >
          {{ opt.text }}
        </button>
      </div>
    </template>

    <!-- VF -->
    <template v-else-if="card.card_type === 'vf'">
      <p class="text-lg font-bold text-slate-800 dark:text-slate-100 mt-3 mb-5">{{ card.payload?.assertion }}</p>
      <div class="flex gap-3 flex-1 items-start">
        <button
          v-for="opt in [true, false]"
          :key="String(opt)"
          type="button"
          :disabled="revealed"
          @click="selectedBool = opt"
          class="flex-1 py-3 rounded-xl border text-sm font-bold transition-all disabled:cursor-default"
          :class="vfClass(opt)"
        >
          {{ opt ? 'Vrai' : 'Faux' }}
        </button>
      </div>
      <p v-if="revealed && card.payload?.justification" class="text-xs text-slate-500 dark:text-slate-400 mt-4">
        {{ card.payload.justification }}
      </p>
    </template>

    <!-- ORDRE -->
    <template v-else-if="card.card_type === 'ordre'">
      <p class="text-lg font-bold text-slate-800 dark:text-slate-100 mt-3 mb-2">{{ card.payload?.title }}</p>
      <p class="text-xs text-slate-400 mb-4">Remettez ces éléments dans le bon ordre (mentalement), puis révélez.</p>
      <div class="space-y-2 flex-1">
        <div
          v-for="(step, i) in displaySteps"
          :key="i"
          class="flex items-center gap-3 px-4 py-2.5 rounded-xl border text-sm font-semibold"
          :class="revealed ? 'border-emerald-200 bg-emerald-50/50 dark:border-emerald-900/30 dark:bg-emerald-950/20 text-emerald-700 dark:text-emerald-400' : 'border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200'"
        >
          <span class="text-xs font-bold text-slate-400 w-4">{{ revealed ? i + 1 : '•' }}</span>
          {{ step }}
        </div>
      </div>
    </template>

    <!-- ASSOC -->
    <template v-else-if="card.card_type === 'assoc'">
      <p class="text-lg font-bold text-slate-800 dark:text-slate-100 mt-3 mb-4">{{ card.payload?.title }}</p>
      <div class="space-y-2 flex-1">
        <div
          v-for="(p, i) in card.payload?.pairs || []"
          :key="i"
          class="flex items-center justify-between gap-3 px-4 py-2.5 rounded-xl border text-sm font-semibold border-slate-200 dark:border-slate-700"
        >
          <span class="text-slate-700 dark:text-slate-200">{{ p.left }}</span>
          <span class="text-slate-400">→</span>
          <span :class="revealed ? 'text-indigo-600 dark:text-indigo-400' : 'text-transparent bg-slate-200 dark:bg-slate-700 rounded select-none px-8'">
            {{ revealed ? p.right : '???' }}
          </span>
        </div>
      </div>
    </template>

    <button
      v-if="!revealed"
      type="button"
      @click="reveal"
      class="mt-6 w-full py-3 text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl active:scale-95 transition-all"
    >
      Révéler la réponse
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Flashcard } from '../../stores/decks'

const props = defineProps<{ card: Flashcard }>()
const emit = defineEmits<{ (e: 'revealed', isCorrect: boolean | null): void }>()

const revealed = ref(false)
const selected = ref<string | null>(null)
const selectedBool = ref<boolean | null>(null)

const typeLabel = computed(() => {
  const labels: Record<string, string> = {
    qcm: 'QCM', vf: 'Vrai ou Faux', ordre: "Remettre dans l'ordre", assoc: 'Associations',
  }
  return labels[props.card.card_type] || 'Question'
})

// Pour l'ordre : on présente les étapes mélangées tant qu'on n'a pas révélé.
const displaySteps = computed(() => {
  const steps = props.card.payload?.steps || []
  if (revealed.value) return steps
  return [...steps].sort(() => Math.random() - 0.5)
})

function optionClass(id: string, correct: boolean) {
  if (!revealed.value) {
    return selected.value === id
      ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-950/30 text-indigo-700 dark:text-indigo-300'
      : 'border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:border-indigo-300'
  }
  if (correct) return 'border-emerald-300 bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-400'
  if (selected.value === id) return 'border-rose-300 bg-rose-50 dark:bg-rose-950/30 text-rose-700 dark:text-rose-400'
  return 'border-slate-200 dark:border-slate-700 text-slate-400'
}

function vfClass(opt: boolean) {
  if (!revealed.value) {
    return selectedBool.value === opt
      ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-950/30 text-indigo-700 dark:text-indigo-300'
      : 'border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300'
  }
  if (props.card.payload?.correct === opt) return 'border-emerald-300 bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-400'
  if (selectedBool.value === opt) return 'border-rose-300 bg-rose-50 dark:bg-rose-950/30 text-rose-700 dark:text-rose-400'
  return 'border-slate-200 dark:border-slate-700 text-slate-400'
}

// Renvoie la justesse de la réponse (null si non auto-évaluable : ordre/assoc).
function computeCorrect(): boolean | null {
  if (props.card.card_type === 'qcm') {
    const opts = props.card.payload?.options || []
    const chosen = opts.find((o) => o.id === selected.value)
    return selected.value === null ? false : !!chosen?.correct
  }
  if (props.card.card_type === 'vf') {
    return selectedBool.value === null ? false : selectedBool.value === props.card.payload?.correct
  }
  return null
}

function reveal() {
  revealed.value = true
  emit('revealed', computeCorrect())
}
</script>
