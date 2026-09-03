<template>
  <BaseModal :open="open" size="md" title="Notation de la note" @close="$emit('close')">
    <!-- notes-ia-planning-corrections, Task 12 : une notation existe deja -- propose un
    choix plutot que d'ecraser silencieusement ou de rappeler l'IA a chaque clic. -->
    <div v-if="choice" class="space-y-4">
      <p class="text-sm text-ink-muted dark:text-ink-subtle">
        Cette note a déjà été notée
        <template v-if="result?.updated_at">le {{ formattedDate }}</template
        >.
      </p>
      <div class="flex flex-col sm:flex-row gap-3">
        <button
          type="button"
          class="flex-1 px-4 py-3 text-sm font-bold text-accent dark:text-accent border border-accent dark:border-accent rounded-xl hover:bg-accent-soft dark:hover:bg-accent-soft transition-all"
          @click="$emit('view-existing')"
        >
          Voir la notation existante
        </button>
        <button
          type="button"
          class="flex-1 px-4 py-3 text-sm font-bold text-white bg-primary hover:bg-primary-strong rounded-xl transition-all"
          @click="$emit('reevaluate')"
        >
          Réévaluer
        </button>
      </div>
    </div>

    <div v-else-if="loading" class="flex flex-col items-center justify-center py-10 gap-3">
      <svg
        class="animate-spin h-8 w-8 text-primary"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        ></circle>
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
      <span class="text-sm font-semibold text-ink-subtle uppercase tracking-widest">
        Notation en cours…
      </span>
    </div>

    <div
      v-else-if="error"
      class="p-4 bg-danger-soft border border-danger/30 rounded-2xl text-danger text-sm"
    >
      {{ error }}
    </div>

    <div v-else-if="result" class="space-y-5">
      <div class="flex items-center gap-4 border-b border-line dark:border-line pb-4">
        <div
          class="w-16 h-16 rounded-full flex items-center justify-center bg-accent-soft dark:bg-accent-soft text-accent dark:text-accent font-extrabold text-lg border border-accent shrink-0"
        >
          {{ formattedScore }}
        </div>
        <p class="text-sm text-ink dark:text-ink-subtle leading-relaxed">{{ result.verdict }}</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="space-y-2">
          <h4 class="text-xs font-bold text-success uppercase tracking-wider">Points forts</h4>
          <ul v-if="(result.points_forts?.length ?? 0) > 0" class="space-y-1.5">
            <li
              v-for="(item, i) in result.points_forts"
              :key="i"
              class="text-xs text-ink-muted dark:text-ink-subtle"
            >
              {{ item }}
            </li>
          </ul>
          <p v-else class="text-xs text-ink-subtle italic">Aucun point fort particulier relevé.</p>
        </div>

        <div class="space-y-2">
          <h4 class="text-xs font-bold text-warning uppercase tracking-wider">Améliorations</h4>
          <ul v-if="(result.ameliorations?.length ?? 0) > 0" class="space-y-1.5">
            <li
              v-for="(item, i) in result.ameliorations"
              :key="i"
              class="text-xs text-ink-muted dark:text-ink-subtle"
            >
              {{ item }}
            </li>
          </ul>
          <p v-else class="text-xs text-ink-subtle italic">Rien à améliorer, excellent travail.</p>
        </div>
      </div>

      <div
        v-if="result.suggestions"
        class="p-4 rounded-2xl bg-surface-soft border border-line dark:border-line"
      >
        <h4
          class="text-xs font-bold text-ink-muted dark:text-ink-subtle uppercase tracking-wider mb-1.5"
        >
          Suggestions
        </h4>
        <p class="text-xs text-ink-muted dark:text-ink-subtle leading-relaxed">
          {{ result.suggestions }}
        </p>
      </div>
    </div>

    <template #footer>
      <button
        type="button"
        class="px-4 py-2 text-xs font-bold text-ink-muted hover:text-ink dark:text-ink-subtle border border-line dark:border-line rounded-xl transition-all"
        @click="$emit('close')"
      >
        Fermer
      </button>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { BaseModal } from '../ui/base'
import type { NotationResult } from '../../services/notationService'

const props = withDefaults(
  defineProps<{
    open: boolean
    loading: boolean
    error: string | null
    result: NotationResult | null
    choice?: boolean
  }>(),
  { choice: false },
)

defineEmits<{ close: []; 'view-existing': []; reevaluate: [] }>()

const formattedDate = computed(() => {
  const updatedAt = props.result?.updated_at
  if (!updatedAt) return ''
  return new Date(updatedAt).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
})

// Score renvoyé par le backend sur 100, réaffiché /10 à une décimale (convention
// partagée avec Blurting/Feynman -- cf. canevas Direction A).
const formattedScore = computed(() => {
  const score = props.result?.score
  if (score === undefined) return '—'
  return (score / 10).toLocaleString('fr-FR', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  })
})
</script>
