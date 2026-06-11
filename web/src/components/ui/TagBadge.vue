<template>
  <span
    class="inline-flex items-center gap-1.5 rounded-lg border px-2 py-0.5 text-[11px] font-bold"
    :style="badgeStyle"
  >
    <span class="h-1.5 w-1.5 rounded-full" :style="{ backgroundColor: tag.color || fallbackColor }"></span>
    {{ tag.name }}
    <button
      v-if="removable"
      type="button"
      class="text-current opacity-60 hover:opacity-100"
      :aria-label="`Retirer ${tag.name}`"
      @click="$emit('remove', tag)"
    >
      ×
    </button>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Tag } from '../../stores/tags'

const props = withDefaults(defineProps<{
  tag: Tag
  removable?: boolean
}>(), {
  removable: false
})

defineEmits<{
  remove: [tag: Tag]
}>()

const fallbackColor = '#4F46E5'
const badgeStyle = computed(() => {
  const color = props.tag.color || fallbackColor
  return {
    borderColor: `${color}33`,
    backgroundColor: `${color}14`,
    color
  }
})
</script>
