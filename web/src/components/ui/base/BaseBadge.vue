<template>
  <span
    class="inline-flex items-center gap-1 rounded-full font-semibold"
    :class="[sizeClass, variantClass]"
  >
    <slot />
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type Variant = 'neutral' | 'primary' | 'accent' | 'success' | 'warning' | 'danger' | 'info'
type Size = 'sm' | 'md'

const props = withDefaults(defineProps<{
  variant?: Variant
  size?: Size
}>(), {
  variant: 'neutral',
  size: 'md',
})

const sizeClass = computed(() => ({
  sm: 'text-[10px] px-2 py-0.5',
  md: 'text-xs px-2.5 py-1',
}[props.size]))

const variantClass = computed(() => ({
  neutral: 'bg-surface-soft text-ink-muted',
  primary: 'bg-primary-soft text-primary',
  accent: 'bg-accent-soft text-accent',
  success: 'bg-success-soft text-success',
  warning: 'bg-warning-soft text-warning',
  danger: 'bg-danger-soft text-danger',
  info: 'bg-info-soft text-info',
}[props.variant]))
</script>
