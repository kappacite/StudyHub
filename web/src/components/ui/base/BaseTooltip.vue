<template>
  <span
    class="relative inline-flex"
    @mouseenter="show"
    @mouseleave="hide"
    @focusin="show"
    @focusout="hide"
  >
    <span :aria-describedby="tooltipId">
      <slot />
    </span>
    <span
      v-if="visible"
      :id="tooltipId"
      role="tooltip"
      class="absolute z-50 whitespace-nowrap rounded bg-ink text-app text-xs font-medium px-2.5 py-1.5 pointer-events-none"
      :class="placementClass"
    >
      {{ content }}
    </span>
  </span>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

type Placement = 'top' | 'bottom' | 'left' | 'right'

const props = withDefaults(
  defineProps<{
    content: string
    placement?: Placement
  }>(),
  {
    placement: 'top',
  },
)

const visible = ref(false)
const tooltipId = `tooltip-${Math.random().toString(36).slice(2, 9)}`

function show() {
  visible.value = true
}
function hide() {
  visible.value = false
}

const placementClass = computed(
  () =>
    ({
      top: 'bottom-full left-1/2 -translate-x-1/2 mb-1.5',
      bottom: 'top-full left-1/2 -translate-x-1/2 mt-1.5',
      left: 'right-full top-1/2 -translate-y-1/2 mr-1.5',
      right: 'left-full top-1/2 -translate-y-1/2 ml-1.5',
    })[props.placement],
)
</script>
