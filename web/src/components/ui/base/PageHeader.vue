<template>
  <div class="space-y-4">
    <!-- Fil d'Ariane -->
    <nav v-if="breadcrumbs && breadcrumbs.length" class="flex items-center flex-wrap gap-1.5 text-xs font-semibold text-ink-subtle">
      <template v-for="(crumb, i) in breadcrumbs" :key="i">
        <router-link
          v-if="crumb.to && i < breadcrumbs.length - 1"
          :to="crumb.to"
          class="hover:text-ink transition-colors"
        >{{ crumb.label }}</router-link>
        <span v-else :class="i === breadcrumbs.length - 1 ? 'text-ink' : ''">{{ crumb.label }}</span>
        <span v-if="i < breadcrumbs.length - 1" class="text-ink-subtle/60">›</span>
      </template>
    </nav>

    <!-- Titre + actions -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
      <div class="min-w-0">
        <h1 class="text-2xl font-bold text-ink tracking-tight truncate">{{ title }}</h1>
        <p v-if="subtitle" class="text-sm text-ink-muted mt-1">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.actions" class="flex items-center gap-2 shrink-0">
        <slot name="actions" />
      </div>
    </div>

    <!-- Onglets -->
    <div v-if="$slots.tabs">
      <slot name="tabs" />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Breadcrumb {
  label: string
  to?: string
}

defineProps<{
  title: string
  subtitle?: string
  breadcrumbs?: Breadcrumb[]
}>()
</script>
