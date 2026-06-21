<template>
  <div class="relative">
    <span v-if="$slots.icon" class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-ink-subtle pointer-events-none">
      <slot name="icon" />
    </span>
    <input
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      class="w-full rounded-xl bg-surface-soft border border-line text-sm text-ink placeholder:text-ink-subtle transition focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary/40 disabled:opacity-50"
      :class="$slots.icon ? 'pl-11 pr-4 py-2.5' : 'px-4 py-2.5'"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  modelValue?: string | number
  type?: string
  placeholder?: string
  disabled?: boolean
}>(), {
  modelValue: '',
  type: 'text',
  placeholder: '',
  disabled: false,
})

defineEmits<{ 'update:modelValue': [value: string] }>()
</script>
