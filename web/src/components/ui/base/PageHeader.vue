<template>
  <div class="space-y-4">
    <!-- Fil d'Ariane -->
    <nav
      v-if="breadcrumbs && breadcrumbs.length"
      class="flex items-center flex-wrap gap-1.5 text-xs font-semibold text-ink-subtle"
    >
      <template v-for="(crumb, i) in breadcrumbs" :key="i">
        <router-link
          v-if="crumb.to && i < breadcrumbs.length - 1"
          :to="crumb.to"
          class="hover:text-ink transition-colors"
          >{{ crumb.label }}</router-link
        >
        <span v-else :class="i === breadcrumbs.length - 1 ? 'text-ink' : ''">{{
          crumb.label
        }}</span>
        <span v-if="i < breadcrumbs.length - 1" class="text-ink-subtle/60">›</span>
      </template>
    </nav>

    <!-- Titre + actions -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
      <div class="min-w-0">
        <h1 class="text-2xl font-bold text-ink tracking-tight truncate">{{ title }}</h1>
        <p v-if="subtitle" class="text-sm text-ink-muted mt-1">{{ subtitle }}</p>
      </div>
      <!-- flex-wrap ne joue réellement que sous le point de rupture `sm` : le
           parent est `flex-col` à cette largeur, donc ce conteneur s'étire en
           pleine largeur et peut déborder ; à `sm` et au-delà le parent passe
           en `flex-row` et ce conteneur reste `shrink-0` (taille `max-content`),
           donc flex-wrap ne se déclenche jamais même avec 6 boutons sur une
           largeur moyenne -- suffisant pour les deux largeurs de référence
           mobile/desktop de ce projet (aucun risque réaliste de débordement à
           6 boutons sur la largeur desktop). -->
      <div v-if="$slots.actions" class="flex flex-wrap items-center gap-2 shrink-0">
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
