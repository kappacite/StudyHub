<template>
  <aside class="flex flex-col gap-6">
    <BaseCard padding="md">
      <h2 class="font-display text-display-md text-ink dark:text-white mb-1">Assistant IA</h2>
      <p class="text-xs text-ink-muted dark:text-ink-subtle leading-relaxed mb-4">
        S'entraîner sur cette note, à partir de son contenu.
      </p>
      <div class="flex flex-col gap-2">
        <button
          v-for="activity in activities"
          :key="activity.type"
          type="button"
          class="w-full flex items-center gap-2.5 px-3.5 py-2.5 border border-line dark:border-line rounded-lg text-sm font-semibold text-ink dark:text-ink-subtle hover:bg-primary-soft dark:hover:bg-primary-soft hover:text-primary dark:hover:text-primary hover:border-primary dark:hover:border-primary transition-all text-left"
          @click="$emit('start-activity', activity.type)"
        >
          <component :is="activity.icon" class="w-4 h-4 text-primary flex-shrink-0" />
          {{ activity.label }}
        </button>
      </div>
    </BaseCard>

    <BaseCard padding="md">
      <h2 class="font-display text-display-md text-ink dark:text-white mb-4">Métadonnées</h2>
      <dl class="space-y-3 text-sm">
        <div class="flex items-center justify-between gap-2">
          <dt
            class="text-xs font-semibold text-ink-muted dark:text-ink-subtle uppercase tracking-wider"
          >
            Classeur
          </dt>
          <dd class="text-ink dark:text-white font-semibold text-right">{{ binderName }}</dd>
        </div>

        <div v-if="tags.length > 0" class="flex flex-col gap-2">
          <dt
            class="text-xs font-semibold text-ink-muted dark:text-ink-subtle uppercase tracking-wider"
          >
            Tags
          </dt>
          <dd class="flex flex-wrap gap-1.5">
            <TagBadge v-for="tag in tags" :key="tag.id" :tag="tag" />
          </dd>
        </div>

        <div class="flex items-center justify-between gap-2">
          <dt
            class="text-xs font-semibold text-ink-muted dark:text-ink-subtle uppercase tracking-wider"
          >
            Modifiée
          </dt>
          <dd class="text-ink dark:text-white font-mono text-xs">{{ formattedUpdatedAt }}</dd>
        </div>
      </dl>
    </BaseCard>
  </aside>
</template>

<script setup lang="ts">
// Sidebar présentationnelle affichée à côté de la fiche en mode lecture (remplace
// l'ancienne modale "Réviser avec l'IA"). Aucun appel API/store direct : tout arrive par
// props, et le choix d'une méthode d'entraînement remonte au parent via l'emit
// `start-activity` — c'est NoteEdit.vue qui reste seul propriétaire de la navigation
// (startAiActivity) et des données (classeur/tags/date de modification).
import { computed, type Component } from 'vue'
import { Sparkles, Brain, Lightbulb } from '@lucide/vue'
import { BaseCard } from '../ui/base'
import TagBadge from '../ui/TagBadge.vue'
import type { Tag } from '../../stores/tags'

type ActivityType = 'evaluation' | 'blurting' | 'feynman'

interface Activity {
  type: ActivityType
  label: string
  icon: Component
}

const props = defineProps<{
  binderName: string
  tags: Tag[]
  updatedAt: string
}>()

defineEmits<{
  'start-activity': [type: ActivityType]
}>()

// Ordre d'affichage conforme au canevas Direction A (NoteEdit.dc.html) : Évaluation
// mixte / Méthode de la feuille blanche / Méthode Feynman — exactement ces 3 méthodes,
// pas de 4e bouton "Générer un quiz" (NoteQuiz.vue reste accessible par URL directe,
// simplement retiré de ce panneau).
const activities: Activity[] = [
  { type: 'evaluation', label: 'Évaluation mixte', icon: Sparkles },
  { type: 'blurting', label: 'Méthode de la feuille blanche', icon: Brain },
  { type: 'feynman', label: 'Méthode Feynman', icon: Lightbulb },
]

const formattedUpdatedAt = computed(() => {
  if (!props.updatedAt) return '—'
  const date = new Date(props.updatedAt)
  if (Number.isNaN(date.getTime())) return '—'
  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })
})
</script>
