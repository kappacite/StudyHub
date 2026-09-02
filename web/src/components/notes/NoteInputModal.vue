<template>
  <BaseModal :open="visible" size="md" @close="$emit('cancel')">
    <template #title>
      <span class="flex items-start gap-3">
        <span
          class="flex items-center justify-center w-11 h-11 rounded-2xl flex-shrink-0 text-white shadow-lg"
          :class="iconBg"
        >
          <component :is="icon" class="w-5 h-5" />
        </span>
        <span class="flex-1 min-w-0 pt-0.5">
          <span class="block font-bold text-ink dark:text-white text-base">{{ title }}</span>
          <span
            v-if="description"
            class="block text-xs font-normal normal-case tracking-normal text-ink-muted dark:text-ink-subtle mt-0.5"
          >
            {{ description }}
          </span>
        </span>
      </span>
    </template>

    <div class="space-y-3">
      <div v-for="(field, i) in fields" :key="i">
        <label
          class="block text-xs font-bold text-ink-muted dark:text-ink-subtle mb-1.5 uppercase tracking-wider"
          >{{ field.label }}</label
        >

        <!-- Texte -->
        <input
          v-if="field.type === 'text' || field.type === 'textarea'"
          :value="field.value"
          :placeholder="field.placeholder || ''"
          class="w-full px-4 py-2.5 bg-surface-soft dark:bg-surface-soft border border-line dark:border-line rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-primary transition-all"
          @input="updateFieldValue(i, ($event.target as HTMLInputElement).value)"
          @keydown.enter.prevent="$emit('confirm')"
          @keydown.escape.prevent="$emit('cancel')"
        />

        <!-- Booléen (Vrai / Faux) -->
        <div v-else-if="field.type === 'bool'" class="flex gap-3">
          <button
            type="button"
            class="flex-1 min-h-11 py-2.5 rounded-xl text-sm font-bold border-2 transition-all"
            :class="
              field.value === true
                ? 'border-success bg-success-soft dark:bg-success-soft text-success dark:text-success'
                : 'border-line dark:border-line text-ink-muted hover:border-success'
            "
            @click="updateFieldValue(i, true)"
          >
            ✓ Vrai
          </button>
          <button
            type="button"
            class="flex-1 min-h-11 py-2.5 rounded-xl text-sm font-bold border-2 transition-all"
            :class="
              field.value === false
                ? 'border-danger bg-danger-soft dark:bg-danger-soft text-danger dark:text-danger'
                : 'border-line dark:border-line text-ink-muted hover:border-danger'
            "
            @click="updateFieldValue(i, false)"
          >
            ✗ Faux
          </button>
        </div>

        <!-- Select -->
        <select
          v-else-if="field.type === 'select'"
          :value="field.value"
          class="w-full px-4 py-2.5 bg-surface-soft dark:bg-surface-soft border border-line dark:border-line rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-primary transition-all"
          @change="onSelectChange(i, $event)"
        >
          <option v-for="opt in field.options" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
      </div>
    </div>

    <template #footer>
      <button
        type="button"
        class="flex-1 min-h-11 py-2.5 border border-line dark:border-line rounded-xl text-sm font-semibold text-ink-muted dark:text-ink-subtle hover:bg-surface-soft dark:hover:bg-surface-soft transition-all"
        @click="$emit('cancel')"
      >
        Annuler
      </button>
      <button
        type="button"
        class="flex-1 min-h-11 py-2.5 rounded-xl text-sm font-bold text-white transition-all active:scale-95 shadow-md"
        :class="confirmBg"
        @click="$emit('confirm')"
      >
        {{ confirmLabel }}
      </button>
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
// Modale de saisie générique utilisée par NoteEdit.vue pour piloter les insertions
// (définition / QCM / ordre / association / vrai-faux / diagramme). Composant purement
// présentationnel : il ne connaît aucune règle de transformation par type d'insertion
// (celles-ci restent dans NoteEdit.vue, dans applySelectionTransform), il se contente
// d'afficher les champs fournis et d'émettre les interactions (saisie, confirmation,
// annulation) vers le parent qui reste seul propriétaire de l'état métier.
import type { Component } from 'vue'
import { BaseModal } from '../ui/base'

export interface ModalFieldOption {
  value: string | number
  label: string
}

export type ModalField =
  | { type: 'text' | 'textarea'; label: string; value: string; placeholder?: string }
  | { type: 'bool'; label: string; value: boolean }
  | { type: 'select'; label: string; value: string | number; options: ModalFieldOption[] }

const props = withDefaults(
  defineProps<{
    visible: boolean
    title: string
    description?: string
    icon: Component
    iconBg?: string
    confirmBg?: string
    confirmLabel?: string
    fields: ModalField[]
  }>(),
  {
    description: undefined,
    iconBg: 'bg-primary',
    confirmBg: 'bg-primary hover:bg-primary-strong shadow-elev-primary',
    confirmLabel: 'Confirmer',
  },
)

const emit = defineEmits<{
  'update:fields': [fields: ModalField[]]
  confirm: []
  cancel: []
}>()

function updateFieldValue(index: number, value: string | number | boolean) {
  const next = props.fields.map((field, i) =>
    i === index ? ({ ...field, value } as ModalField) : field,
  )
  emit('update:fields', next)
}

function onSelectChange(index: number, event: Event) {
  const raw = (event.target as HTMLSelectElement).value
  const field = props.fields[index]
  if (field.type !== 'select') return
  const matched = field.options.find((opt) => String(opt.value) === raw)
  updateFieldValue(index, matched ? matched.value : raw)
}
</script>
