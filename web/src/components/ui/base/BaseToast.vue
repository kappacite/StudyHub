<template>
  <div
    role="status"
    aria-live="polite"
    class="flex items-start gap-3 rounded-lg border p-4 shadow-elev-2"
    :class="variantClass"
  >
    <component :is="icon" class="w-5 h-5 flex-shrink-0 mt-0.5" />
    <div class="flex-1 min-w-0">
      <p v-if="title" class="text-sm font-bold">{{ title }}</p>
      <p class="text-sm" :class="title ? 'mt-0.5' : ''">
        <slot>{{ message }}</slot>
      </p>
    </div>
    <button
      v-if="closable"
      type="button"
      class="flex-shrink-0 -mr-1 -mt-1 p-1 rounded hover:bg-black/5 dark:hover:bg-white/5"
      aria-label="Fermer"
      @click="$emit('close')"
    >
      <X class="w-4 h-4" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { CheckCircle2, AlertTriangle, XCircle, Info, X } from '@lucide/vue'

type Variant = 'info' | 'success' | 'warning' | 'danger'

const props = withDefaults(
  defineProps<{
    variant?: Variant
    title?: string
    message?: string
    closable?: boolean
  }>(),
  {
    variant: 'info',
    closable: true,
  },
)

defineEmits<{ close: [] }>()

const variantClass = computed(
  () =>
    ({
      info: 'bg-primary-soft border-primary/30 text-primary',
      success: 'bg-success-soft border-success/30 text-success',
      warning: 'bg-accent-soft border-accent/30 text-accent',
      danger: 'bg-danger-soft border-danger/30 text-danger',
    })[props.variant],
)

const icon = computed(
  () =>
    ({
      info: Info,
      success: CheckCircle2,
      warning: AlertTriangle,
      danger: XCircle,
    })[props.variant],
)
</script>
