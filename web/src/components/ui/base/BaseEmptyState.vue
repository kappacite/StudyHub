<template>
  <div class="flex flex-col items-center justify-center text-center rounded-3xl border-2 border-dashed border-line p-12 gap-3">
    <div v-if="$slots.icon" class="flex items-center justify-center w-14 h-14 rounded-2xl bg-surface-soft text-ink-subtle mb-1">
      <slot name="icon" />
    </div>
    <h4 class="text-base font-bold text-ink">{{ title }}</h4>
    <p v-if="description" class="text-sm text-ink-muted max-w-sm">{{ description }}</p>
    <div v-if="$slots.actions" class="mt-2 flex items-center gap-2">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>
