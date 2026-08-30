<template>
  <div class="grid grid-cols-4 gap-2">
    <button
      data-test="self-eval-encore"
      :disabled="disabled"
      class="min-h-11 py-2.5 rounded-xl text-xs font-bold border border-danger text-danger hover:bg-danger-soft dark:border-danger dark:bg-danger-soft disabled:opacity-50"
      @click="emit('select', 1)"
    >
      Encore
    </button>
    <button
      data-test="self-eval-difficile"
      :disabled="disabled"
      class="min-h-11 py-2.5 rounded-xl text-xs font-bold border border-accent text-accent hover:bg-accent-soft dark:border-accent dark:bg-accent-soft disabled:opacity-50"
      @click="emit('select', 2)"
    >
      Difficile
    </button>
    <button
      data-test="self-eval-bien"
      :disabled="disabled"
      class="min-h-11 py-2.5 rounded-xl text-xs font-bold border border-primary text-primary hover:bg-primary-soft dark:border-primary dark:bg-primary-soft disabled:opacity-50"
      @click="emit('select', 4)"
    >
      Bien
    </button>
    <button
      data-test="self-eval-facile"
      :disabled="disabled"
      class="min-h-11 py-2.5 rounded-xl text-xs font-bold border border-success text-success hover:bg-success-soft dark:border-success dark:bg-success-soft disabled:opacity-50"
      @click="emit('select', 5)"
    >
      Facile
    </button>
  </div>
</template>

<script setup lang="ts">
// Bloc d'auto-evaluation manuelle, factorise (Task 5 revision-flexibilite) --
// reutilise par les 6 emplacements notes en auto-evaluation (flashcard,
// definition, vf/association/ordre apres verification de leur reponse
// objective, QCM apres correction). Les 4 paliers (Encore/Difficile/Bien/
// Facile, scores 1/2/4/5) et leurs couleurs correspondent exactement aux 4
// paliers du graphique "PAR NOTATION SM2" de RevisionSetStats.vue
// (GradeDistribution backend : again 0-1, hard 2, good 3-4, easy 5) --
// "Bien" soumet 4 (facteur de facilite SM-2 inchange), pas 3 (qui le
// ferait legerement baisser), decision actee en chat.
withDefaults(defineProps<{ disabled?: boolean }>(), { disabled: false })
const emit = defineEmits<{ select: [score: number] }>()
</script>
