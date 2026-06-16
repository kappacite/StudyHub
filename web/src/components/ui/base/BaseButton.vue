<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="inline-flex items-center justify-center gap-2 font-semibold rounded-xl transition-all duration-200 active:scale-[.97] focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2 focus-visible:ring-offset-app disabled:opacity-50 disabled:pointer-events-none"
    :class="[sizeClass, variantClass, block ? 'w-full' : '']"
  >
    <svg v-if="loading" class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
    <slot name="icon" />
    <slot />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type Variant = 'primary' | 'secondary' | 'ghost' | 'soft' | 'danger'
type Size = 'sm' | 'md' | 'lg'

const props = withDefaults(defineProps<{
  variant?: Variant
  size?: Size
  type?: 'button' | 'submit' | 'reset'
  block?: boolean
  loading?: boolean
  disabled?: boolean
}>(), {
  variant: 'primary',
  size: 'md',
  type: 'button',
  block: false,
  loading: false,
  disabled: false,
})

const sizeClass = computed(() => ({
  sm: 'text-xs px-3 py-1.5',
  md: 'text-sm px-4 py-2.5',
  lg: 'text-base px-5 py-3',
}[props.size]))

const variantClass = computed(() => ({
  primary: 'bg-primary text-white hover:bg-primary-strong shadow-soft-primary',
  secondary: 'bg-surface text-ink border border-line hover:bg-surface-soft',
  ghost: 'text-ink-muted hover:bg-surface-soft hover:text-ink',
  soft: 'bg-primary-soft text-primary hover:brightness-95 dark:hover:brightness-125',
  danger: 'bg-danger text-white hover:bg-danger-strong',
}[props.variant]))
</script>
