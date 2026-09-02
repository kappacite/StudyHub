<template>
  <BaseModal :open="visible" size="sm" @close="$emit('cancel')">
    <div class="flex flex-col items-center text-center mb-3">
      <div
        class="w-10 h-10 bg-primary-soft dark:bg-primary-soft rounded-2xl flex items-center justify-center text-primary dark:text-primary mb-2 border border-primary dark:border-primary"
      >
        <Sparkles class="w-5 h-5 animate-pulse" />
      </div>
      <h3 class="font-extrabold text-ink dark:text-white text-lg leading-tight">
        C'était facile ?
      </h3>
      <p class="text-xs text-ink-muted dark:text-ink-subtle leading-snug mt-1">
        Évaluez votre niveau de rappel pour l'algorithme d'apprentissage.
      </p>
    </div>

    <div class="grid grid-cols-2 gap-2.5">
      <button
        v-for="btn in evaluationButtons"
        :key="btn.val"
        type="button"
        :disabled="isEvaluating"
        class="flex flex-col items-center gap-0.5 min-h-11 py-2.5 px-2 border-2 rounded-2xl transition-all hover:scale-[1.02] active:scale-95 disabled:opacity-50 disabled:pointer-events-none"
        :class="btn.class"
        @click="$emit('evaluate', btn.val)"
      >
        <span class="text-2xl leading-none">{{ btn.emoji }}</span>
        <span class="text-xs font-bold leading-none">{{ btn.label }}</span>
        <span class="text-tiny opacity-60 leading-none">{{ btn.desc }}</span>
      </button>
    </div>

    <template #footer>
      <button
        type="button"
        class="w-full min-h-11 py-2 border border-line dark:border-line rounded-xl text-xs font-bold text-ink-muted hover:bg-surface-soft dark:hover:bg-surface-soft transition-all"
        @click="$emit('cancel')"
      >
        Passer sans évaluer
      </button>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
// Modale d'évaluation SM-2 affichée pendant la lecture active (grille de boutons de
// notation Encore/Difficile/Correct/Facile). Composant purement présentationnel : il ne
// connaît ni l'algorithme SM-2 ni l'appel réseau qui enregistre la note (ceux-ci restent
// dans NoteEdit.vue, dans submitSm2Evaluation) — il se contente d'afficher la grille et
// d'émettre la note choisie, ou l'annulation, vers le parent qui reste seul propriétaire
// de l'état métier.
import { Sparkles } from '@lucide/vue'
import { BaseModal } from '../ui/base'

withDefaults(
  defineProps<{
    visible: boolean
    isEvaluating?: boolean
  }>(),
  {
    isEvaluating: false,
  },
)

defineEmits<{
  evaluate: [score: number]
  cancel: []
}>()

const evaluationButtons = [
  {
    val: 1,
    label: 'À revoir',
    emoji: '🔁',
    desc: 'Pas retenu',
    class:
      'border-rose-100 dark:border-rose-950/40 bg-rose-50 hover:bg-rose-100 dark:bg-rose-950/20 text-rose-600 dark:text-rose-400 hover:border-rose-350',
  },
  {
    val: 2,
    label: 'Difficile',
    emoji: '😕',
    desc: 'Gros effort',
    class:
      'border-amber-100 dark:border-amber-950/40 bg-amber-50 hover:bg-amber-100 dark:bg-amber-950/20 text-amber-600 dark:text-amber-400 hover:border-amber-350',
  },
  {
    val: 3,
    label: 'Correct',
    emoji: '🙂',
    desc: 'Rappel normal',
    class:
      'border-emerald-100 dark:border-emerald-950/40 bg-emerald-50 hover:bg-emerald-100 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400 hover:border-emerald-350',
  },
  {
    val: 5,
    label: 'Facile',
    emoji: '😎',
    desc: 'Aucun effort',
    class:
      'border-blue-100 dark:border-blue-950/40 bg-blue-50 hover:bg-blue-100 dark:bg-blue-950/20 text-blue-600 dark:text-blue-400 hover:border-blue-350',
  },
]
</script>
