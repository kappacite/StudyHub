<template>
  <div class="animate-pulse bg-surface-soft" :class="[rounded, customClass]" />
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  rounded?: string
  customClass?: string
}>(), {
  rounded: 'rounded-xl',
  customClass: 'h-4 w-full',
})
</script>
