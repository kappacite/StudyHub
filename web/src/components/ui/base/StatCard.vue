<template>
  <BaseCard padding="md" :class="'flex items-center gap-4'">
    <div
      v-if="$slots.icon"
      class="flex items-center justify-center w-11 h-11 rounded-2xl shrink-0"
      :class="accentClass"
    >
      <slot name="icon" />
    </div>
    <div class="min-w-0">
      <p class="text-2xl font-extrabold text-ink leading-tight truncate">{{ value }}</p>
      <p class="text-xs font-semibold text-ink-muted uppercase tracking-wide truncate">{{ label }}</p>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BaseCard from './BaseCard.vue'

type Accent = 'primary' | 'accent' | 'success' | 'warning' | 'danger' | 'info'

const props = withDefaults(defineProps<{
  label: string
  value: string | number
  accent?: Accent
}>(), {
  accent: 'primary',
})

const accentClass = computed(() => ({
  primary: 'bg-primary-soft text-primary',
  accent: 'bg-accent-soft text-accent',
  success: 'bg-success-soft text-success',
  warning: 'bg-warning-soft text-warning',
  danger: 'bg-danger-soft text-danger',
  info: 'bg-info-soft text-info',
}[props.accent]))
</script>
