<template>
  <component
    :is="as"
    class="bg-surface border border-line shadow-elev-1"
    :class="[
      radiusClass,
      paddingClass,
      interactive ? 'transition-all duration-200 hover:-translate-y-0.5 hover:shadow-elev-2' : '',
    ]"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type Padding = 'none' | 'sm' | 'md' | 'lg'
// 'card' (défaut, rounded-lg) : chrome générique. 'bristol' (rounded, "bandeaux fiche
// bristol" -- skill design-system § Rayons) : BinderCard.vue en est le premier consommateur.
type Radius = 'card' | 'bristol'

const props = withDefaults(
  defineProps<{
    as?: string
    padding?: Padding
    radius?: Radius
    interactive?: boolean
  }>(),
  {
    as: 'div',
    padding: 'md',
    radius: 'card',
    interactive: false,
  },
)

const radiusClass = computed(() => (props.radius === 'bristol' ? 'rounded' : 'rounded-lg'))

const paddingClass = computed(
  () =>
    ({
      none: '',
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8',
    })[props.padding],
)
</script>
