<template>
  <div class="inline-flex items-center gap-1 flex-wrap max-w-full">
    <button
      v-for="tab in tabs"
      :key="tab.key"
      type="button"
      class="inline-flex items-center gap-1.5 rounded-full px-4 py-1.5 text-sm font-semibold whitespace-nowrap transition-all duration-200"
      :class="
        tab.key === modelValue
          ? 'bg-primary text-primary-ink'
          : 'text-ink-muted hover:text-ink hover:bg-surface-soft'
      "
      @click="$emit('update:modelValue', tab.key)"
    >
      <component :is="tab.icon" v-if="tab.icon" class="w-4 h-4" />
      {{ tab.label }}
      <span
        v-if="tab.badge !== undefined && tab.badge !== null && tab.badge !== ''"
        class="ml-0.5 rounded-full px-1.5 py-0.5 text-tiny font-bold"
        :class="
          tab.key === modelValue
            ? 'bg-primary-ink/20 text-primary-ink'
            : 'bg-surface-soft text-ink-muted'
        "
        >{{ tab.badge }}</span
      >
    </button>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

export interface TabItem {
  key: string
  label: string
  icon?: Component
  badge?: string | number | null
}

defineProps<{
  modelValue: string
  tabs: TabItem[]
}>()

defineEmits<{ 'update:modelValue': [key: string] }>()
</script>
