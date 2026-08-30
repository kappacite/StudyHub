<template>
  <div class="grid grid-cols-3 gap-2">
    <button
      data-test="self-eval-a-revoir"
      :disabled="disabled"
      class="min-h-11 py-2.5 rounded-xl text-xs font-bold border border-danger text-danger hover:bg-danger-soft dark:border-danger dark:bg-danger-soft disabled:opacity-50"
      @click="emit('select', 1)"
    >
      À revoir
    </button>
    <button
      data-test="self-eval-moyen"
      :disabled="disabled"
      class="min-h-11 py-2.5 rounded-xl text-xs font-bold border border-warning text-warning hover:bg-warning-soft dark:border-warning dark:bg-warning-soft disabled:opacity-50"
      @click="emit('select', 3)"
    >
      Moyen
    </button>
    <button
      data-test="self-eval-acquis"
      :disabled="disabled"
      class="min-h-11 py-2.5 rounded-xl text-xs font-bold border border-success text-success hover:bg-success-soft dark:border-success dark:bg-success-soft disabled:opacity-50"
      @click="emit('select', 5)"
    >
      Acquis
    </button>
  </div>
</template>

<script setup lang="ts">
// Bloc d'auto-evaluation manuelle (1/3/5), factorise (Task 5) : reutilise par
// les 5 types notes en auto-evaluation (flashcard, definition, et desormais
// vf/association/ordre apres verification de leur reponse objective).
withDefaults(defineProps<{ disabled?: boolean }>(), { disabled: false })
const emit = defineEmits<{ select: [score: number] }>()
</script>
