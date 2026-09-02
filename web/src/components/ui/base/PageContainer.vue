<template>
  <div class="mx-auto w-full space-y-6" :class="sizeClass">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// 'content' (Task 7, bibliotheque-notes-listes) : colonne de lecture étroite
// (Notes.dc.html, liste de contenu à l'intérieur d'un classeur) -- max-w-4xl, valeur la
// plus proche de la cible de la maquette dans l'échelle Tailwind par défaut.
type Size = 'default' | 'narrow' | 'wide' | 'content'

const props = withDefaults(
  defineProps<{
    size?: Size
  }>(),
  {
    size: 'default',
  },
)

const sizeClass = computed(
  () =>
    ({
      default: 'max-w-6xl',
      narrow: 'max-w-3xl',
      wide: 'max-w-7xl',
      content: 'max-w-4xl',
    })[props.size],
)
</script>
