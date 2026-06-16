<template>
  <button
    type="button"
    role="switch"
    :aria-checked="modelValue"
    class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2 focus-visible:ring-offset-app"
    :class="modelValue ? 'bg-primary' : 'bg-line'"
    @click="$emit('update:modelValue', !modelValue)"
  >
    <span
      class="pointer-events-none inline-flex h-5 w-5 transform items-center justify-center rounded-full bg-white shadow transition duration-200 ease-in-out"
      :class="modelValue ? 'translate-x-5' : 'translate-x-0'"
    >
      <slot :checked="modelValue" />
    </span>
  </button>
</template>

<script setup lang="ts">
defineProps<{ modelValue: boolean }>()
defineEmits<{ 'update:modelValue': [value: boolean] }>()
</script>
