<template>
  <component
    :is="as"
    class="rounded-2xl bg-surface border border-line shadow-elev-1"
    :class="[paddingClass, interactive ? 'transition-all duration-200 hover:-translate-y-0.5 hover:shadow-elev-2' : '']"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type Padding = 'none' | 'sm' | 'md' | 'lg'

const props = withDefaults(defineProps<{
  as?: string
  padding?: Padding
  interactive?: boolean
}>(), {
  as: 'div',
  padding: 'md',
  interactive: false,
})

const paddingClass = computed(() => ({
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
}[props.padding]))
</script>
