<template>
  <div class="space-y-1.5">
    <label v-if="label" :for="forId" class="block text-sm font-semibold text-ink">
      {{ label }}
      <span v-if="required" class="text-danger">*</span>
    </label>
    <slot />
    <p v-if="error" class="text-xs font-medium text-danger">{{ error }}</p>
    <p v-else-if="hint" class="text-xs text-ink-muted">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label?: string
  error?: string
  hint?: string
  required?: boolean
  forId?: string
}>()
</script>
