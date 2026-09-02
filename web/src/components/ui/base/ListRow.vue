<template>
  <component
    :is="as"
    :to="as === 'router-link' ? to : undefined"
    class="flex items-center gap-3 rounded-xl text-left w-full"
    :class="[
      paddingClass,
      interactive ? 'transition-colors hover:bg-surface-soft cursor-pointer' : '',
    ]"
  >
    <div v-if="$slots.leading" class="shrink-0">
      <slot name="leading" />
    </div>

    <div class="flex-1 min-w-0">
      <slot>
        <p v-if="title" class="text-sm font-semibold text-ink truncate">{{ title }}</p>
        <p v-if="subtitle" class="text-xs text-ink-muted truncate">{{ subtitle }}</p>
      </slot>
    </div>

    <div v-if="$slots.trailing" class="shrink-0 flex items-center gap-2">
      <slot name="trailing" />
    </div>
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type As = 'div' | 'button' | 'router-link'
// 'default' (px-3 py-2.5, inchangé) : lignes compactes. 'cozy' (px-0 py-4) : lignes plus
// aérées sans indent horizontal -- Notes.dc.html, le retrait vient du padding de la carte
// englobante (Task 5, bibliotheque-notes-listes).
type Padding = 'default' | 'cozy'

const props = withDefaults(
  defineProps<{
    as?: As
    to?: string
    title?: string
    subtitle?: string
    interactive?: boolean
    padding?: Padding
  }>(),
  {
    as: 'div',
    interactive: false,
    padding: 'default',
  },
)

const paddingClass = computed(() => (props.padding === 'cozy' ? 'px-0 py-4' : 'px-3 py-2.5'))
</script>
