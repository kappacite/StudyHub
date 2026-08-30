<template>
  <BaseCard
    as="button"
    type="button"
    padding="md"
    interactive
    class="w-full text-left flex flex-col gap-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
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
    <div v-if="tags && tags.length" class="flex flex-wrap gap-1.5">
      <TagBadge v-for="tag in tags" :key="tag.id" :tag="tag" />
    </div>
    <p v-if="lastActivityLabel" class="text-xs text-ink-muted">
      Dernière activité : {{ lastActivityLabel }}
    </p>
  </BaseCard>
</template>

<script setup lang="ts">
// Carte de classeur (Bibliothèque, Task 1 bibliotheque-redesign) -- présentationnelle
// pure : aucun appel API/store, tout vient des props. Le calcul des compteurs et du
// libellé d'activité vit dans Binders.vue (binderAggregate) ; le choix de mettre en
// avant une carte (bordure accent vs neutre) appartient au parent (Task 2), pas à ce
// composant. Compose BaseCard (chrome carte partagé) plutôt que de recopier
// rounded/bg-surface/shadow/border à la main (fix revue finale, item 4+5) --
// l'ancienne bordure gauche accentuée (`highlighted`) est retirée avec, elle
// n'était jamais utilisée par Binders.vue.
import { Book } from 'lucide-vue-next'
import TagBadge from '../ui/TagBadge.vue'
import BaseCard from '../ui/base/BaseCard.vue'
import type { Tag } from '../../stores/tags'

export interface BinderCardBinder {
  id: string
  name: string
  readOnly?: boolean
  tags?: Tag[]
}

defineProps<{
  binder: BinderCardBinder
  deckCount: number
  noteCount: number
  lastActivityLabel: string | null
  tags?: Tag[]
}>()

const emit = defineEmits<{ click: [] }>()
</script>
