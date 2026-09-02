<template>
  <div :class="containerClass">
    <button
      v-for="tab in tabs"
      :key="tab.key"
      type="button"
      class="inline-flex items-center gap-1.5 text-sm font-semibold whitespace-nowrap transition-all duration-200"
      :class="[tabShapeClass, tab.key === modelValue ? activeClass : inactiveClass]"
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
import { computed } from 'vue'
import type { Component } from 'vue'

export interface TabItem {
  key: string
  label: string
  icon?: Component
  badge?: string | number | null
}

// `pills` (défaut) : rangée de pilules posée à même la page — forme historique, utilisée par
// ClassesLanding, TeacherDashboard, GroupDetail et DesignSystemDemo. Ne pas la modifier.
// `segmented` : bascule 2 positions de `Notes.dc.html` — le conteneur porte le fond et
// l'ombre, l'onglet actif est un thumb plein qui glisse dedans (Bibliothèque).
type Variant = 'pills' | 'segmented'

const props = withDefaults(
  defineProps<{
    modelValue: string
    tabs: TabItem[]
    variant?: Variant
  }>(),
  { variant: 'pills' },
)

defineEmits<{ 'update:modelValue': [key: string] }>()

const segmented = computed(() => props.variant === 'segmented')

const containerClass = computed(() =>
  segmented.value
    ? 'inline-flex items-center gap-1 p-1 rounded-btn-primary bg-surface shadow-elev-1'
    : 'inline-flex items-center gap-1 flex-wrap max-w-full',
)

const tabShapeClass = computed(() =>
  // `min-h-11` (44px) : cible tactile minimale exigée par `components/CLAUDE.md`. La
  // maquette dessine une bascule plus courte (~35px) ; on garde son padding horizontal et
  // son rayon, mais pas une hauteur sous le seuil d'accessibilité.
  segmented.value ? 'rounded-lg px-5 min-h-11' : 'rounded-full px-4 py-1.5',
)

const activeClass = 'bg-primary text-primary-ink'

const inactiveClass = computed(() =>
  segmented.value
    ? 'text-ink-muted hover:text-ink'
    : 'text-ink-muted hover:text-ink hover:bg-surface-soft',
)
</script>
