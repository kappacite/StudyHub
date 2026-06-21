<template>
  <div class="inline-flex items-center gap-1 p-1 rounded-xl bg-surface-soft overflow-x-auto max-w-full">
    <button
      v-for="tab in tabs"
      :key="tab.key"
      type="button"
      class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-semibold whitespace-nowrap transition-all duration-200"
      :class="tab.key === modelValue
        ? 'bg-surface shadow-soft text-primary'
        : 'text-ink-muted hover:text-ink'"
      @click="$emit('update:modelValue', tab.key)"
    >
      <component :is="tab.icon" v-if="tab.icon" class="w-4 h-4" />
      {{ tab.label }}
      <span
        v-if="tab.badge !== undefined && tab.badge !== null && tab.badge !== ''"
        class="ml-0.5 px-1.5 py-0.5 rounded-full text-[10px] font-bold"
        :class="tab.key === modelValue ? 'bg-primary-soft text-primary' : 'bg-surface text-ink-muted'"
      >{{ tab.badge }}</span>
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
