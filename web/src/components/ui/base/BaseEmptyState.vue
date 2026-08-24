<template>
  <div class="flex flex-col items-center text-center gap-3.5 py-14 px-6">
    <div
      v-if="$slots.icon"
      class="flex items-center justify-center w-14 h-14 rounded-full border-2 border-dashed border-line text-ink-subtle"
    >
      <slot name="icon" />
    </div>
    <div>
      <p class="font-display font-bold text-base text-ink mb-1">{{ title }}</p>
      <p v-if="description" class="text-meta text-ink-muted max-w-xs mx-auto">{{ description }}</p>
    </div>
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
