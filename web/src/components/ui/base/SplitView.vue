<template>
  <div class="flex flex-col lg:flex-row gap-6">
    <aside class="w-full shrink-0" :class="leftWidthClass">
      <slot name="left" />
    </aside>
    <div class="flex-1 min-w-0">
      <slot name="right" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  /** Largeur Tailwind de la colonne gauche en >= lg (ex. 'lg:w-72'). */
  leftWidth?: string
}>(), {
  leftWidth: 'lg:w-72',
})

const leftWidthClass = computed(() => props.leftWidth)
</script>
