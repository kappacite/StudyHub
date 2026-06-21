<template>
  <div class="mx-auto w-full space-y-6" :class="sizeClass">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type Size = 'default' | 'narrow' | 'wide'

const props = withDefaults(defineProps<{
  size?: Size
}>(), {
  size: 'default',
})

const sizeClass = computed(() => ({
  default: 'max-w-6xl',
  narrow: 'max-w-3xl',
  wide: 'max-w-7xl',
}[props.size]))
</script>
