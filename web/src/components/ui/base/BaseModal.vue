<template>
  <TransitionRoot :show="open" as="template">
    <Dialog as="div" class="relative z-50" @close="$emit('close')">
      <TransitionChild
        as="template"
        enter="duration-200 ease-out" enter-from="opacity-0" enter-to="opacity-100"
        leave="duration-150 ease-in" leave-from="opacity-100" leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-ink/40 backdrop-blur-sm" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild
            as="template"
            enter="duration-200 ease-out" enter-from="opacity-0 scale-96" enter-to="opacity-100 scale-100"
            leave="duration-150 ease-in" leave-from="opacity-100 scale-100" leave-to="opacity-0 scale-96"
          >
            <DialogPanel
              class="w-full rounded-3xl bg-surface border border-line shadow-elev-3 p-6 text-left align-middle"
              :class="sizeClass"
            >
              <div v-if="title || $slots.title" class="flex items-start justify-between gap-4 mb-4">
                <DialogTitle class="text-lg font-bold text-ink">
                  <slot name="title">{{ title }}</slot>
                </DialogTitle>
                <button
                  type="button"
                  class="p-1.5 -mr-1 -mt-1 rounded-lg text-ink-subtle hover:text-ink hover:bg-surface-soft transition-colors"
                  @click="$emit('close')"
                >
                  <X class="w-5 h-5" />
                </button>
              </div>

              <slot />

              <div v-if="$slots.footer" class="mt-6 flex items-center justify-end gap-2">
                <slot name="footer" />
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild } from '@headlessui/vue'
import { X } from '@lucide/vue'

type Size = 'sm' | 'md' | 'lg' | 'xl'

const props = withDefaults(defineProps<{
  open: boolean
  title?: string
  size?: Size
}>(), {
  size: 'md',
})

defineEmits<{ close: [] }>()

const sizeClass = computed(() => ({
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-2xl',
}[props.size]))
</script>

<style scoped>
.scale-96 { transform: scale(0.96); }
</style>
