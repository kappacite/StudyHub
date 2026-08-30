<template>
  <button
    type="button"
    class="w-full text-left flex flex-col gap-4 p-6 rounded bg-surface shadow-elev-1 border-l-4 transition-shadow hover:shadow-elev-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
    :class="highlighted ? 'border-l-accent' : 'border-l-line'"
    @click="emit('click')"
  >
    <div class="w-10 h-10 rounded-lg bg-accent-soft flex items-center justify-center shrink-0">
      <Book class="w-5 h-5 text-accent" :stroke-width="1.8" />
    </div>
    <div class="min-w-0">
      <p class="font-display text-display-md text-ink truncate">{{ binder.name }}</p>
      <span v-if="binder.readOnly" class="text-tiny font-bold uppercase tracking-wide text-warning"
        >Cours</span
      >
      <p class="font-mono text-xs text-ink-muted mt-1">
        {{ deckCount }} decks · {{ noteCount }} notes
      </p>
    </div>
    <p v-if="lastActivityLabel" class="text-xs text-ink-muted">
      Dernière activité : {{ lastActivityLabel }}
    </p>
  </button>
</template>

<script setup lang="ts">
// Carte de classeur (Bibliothèque, Task 1 bibliotheque-redesign) -- présentationnelle
// pure : aucun appel API/store, tout vient des props. Le calcul des compteurs et du
// libellé d'activité vit dans Binders.vue (binderAggregate) ; le choix de mettre en
// avant une carte (bordure accent vs neutre) appartient au parent (Task 2), pas à ce
// composant.
import { Book } from 'lucide-vue-next'

export interface BinderCardBinder {
  id: string
  name: string
  readOnly?: boolean
}

withDefaults(
  defineProps<{
    binder: BinderCardBinder
    deckCount: number
    noteCount: number
    lastActivityLabel: string | null
    highlighted?: boolean
  }>(),
  {
    highlighted: false,
  },
)

const emit = defineEmits<{ click: [] }>()
</script>
