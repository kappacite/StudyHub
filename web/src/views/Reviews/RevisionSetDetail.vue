<template>
  <PageContainer>
    <div
      v-if="loading"
      class="py-20 text-center text-sm font-semibold text-ink-subtle uppercase tracking-widest"
    >
      Chargement…
    </div>

    <BaseEmptyState
      v-else-if="loadError"
      title="Le chargement a échoué"
      description="Vos données n'ont pas pu être récupérées. Vérifiez votre connexion et réessayez."
    >
      <template #icon><AlertCircle class="w-6 h-6" /></template>
      <template #actions>
        <BaseButton data-test="retry-button" @click="load">Réessayer</BaseButton>
      </template>
    </BaseEmptyState>

    <template v-else-if="set">
      <div class="flex items-start justify-between gap-4 flex-wrap mb-6">
        <div>
          <div class="flex items-center gap-2">
            <h1 class="font-display text-xl font-bold text-ink">{{ set.name }}</h1>
            <button
              data-test="edit-set-button"
              class="p-1.5 text-ink-subtle hover:text-primary rounded-lg hover:bg-primary-soft transition-all"
              title="Éditer l'ensemble"
              @click="showSetModal = true"
            >
              <Pencil class="w-4 h-4" />
            </button>
          </div>
          <p v-if="set.description" class="text-sm text-ink-muted mt-1 max-w-md">
            {{ set.description }}
          </p>
        </div>
        <BaseButton data-test="study-set-button" @click="studySet()">
          <template #icon><Play class="w-4 h-4" /></template>
          Réviser l'ensemble
        </BaseButton>
      </div>

      <div class="flex items-center justify-between mb-3">
        <span class="text-xs font-bold text-ink-subtle uppercase tracking-wider"
          >{{ items.length }} élément(s)</span
        >
        <BaseButton variant="secondary" size="sm" @click="showItemModal = true">
          <template #icon><Plus class="w-4 h-4" /></template>
          Ajouter un élément
        </BaseButton>
      </div>

      <BaseEmptyState
        v-if="items.length === 0"
        title="Aucun élément"
        description="Ajoutez un premier élément à cet ensemble."
      >
        <template #actions>
          <BaseButton @click="showItemModal = true">Ajouter un élément</BaseButton>
        </template>
      </BaseEmptyState>

      <BaseCard v-else padding="sm">
        <div class="space-y-1">
          <ListRow v-for="group in typeGroups" :key="group.type" class="group">
            <template #leading>
              <div
                class="w-9 h-9 rounded-xl bg-cat-set-soft text-cat-set flex items-center justify-center"
              >
                <component :is="group.icon" class="w-4.5 h-4.5" />
              </div>
            </template>
            <div class="min-w-0">
              <span class="font-semibold text-sm text-ink truncate block">{{ group.label }}</span>
              <span class="text-xs text-ink-subtle"
                >{{ group.items.length }} · {{ group.lastReviewedLabel }}</span
              >
            </div>
            <template #trailing>
              <button
                :data-test="`study-type-${group.type}`"
                class="p-1.5 text-ink-subtle hover:text-primary rounded-lg hover:bg-primary-soft"
                title="Réviser"
                @click="studySet(group.type)"
              >
                <Play class="w-4 h-4" />
              </button>
              <button
                :data-test="`edit-type-${group.type}`"
                class="p-1.5 text-ink-subtle hover:text-primary rounded-lg hover:bg-primary-soft"
                title="Éditer"
                @click="router.push(`/revision/sets/${setId}/items/${group.type}`)"
              >
                <Pencil class="w-4 h-4" />
              </button>
              <button
                :data-test="`delete-type-${group.type}`"
                class="p-1.5 text-ink-subtle hover:text-danger rounded-lg hover:bg-danger-soft"
                title="Supprimer"
                @click="deleteGroup(group)"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </template>
          </ListRow>
        </div>
      </BaseCard>
    </template>

    <RevisionSetModal
      v-if="showSetModal && set"
      mode="edit"
      :binder-id="set.binder_id"
      :set="set"
      @close="showSetModal = false"
      @updated="onSetUpdated"
    />
    <RevisionItemModal
      v-if="showItemModal"
      :binder-id="null"
      :decks="[]"
      :locked-set-id="setId"
      @close="showItemModal = false"
      @created="onItemCreated"
    />
  </PageContainer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useRevisionStore } from '../../stores/revision'
import type { RevisionItem, RevisionItemType, RevisionSet } from '../../stores/revision'
import RevisionSetModal from '../../components/decks/RevisionSetModal.vue'
import RevisionItemModal from '../../components/decks/RevisionItemModal.vue'
import {
  PageContainer,
  BaseCard,
  BaseButton,
  BaseEmptyState,
  ListRow,
} from '../../components/ui/base'
import {
  Play,
  Pencil,
  Trash2,
  Plus,
  AlertCircle,
  Layers,
  HelpCircle,
  Rows3,
  BookOpen,
  ListOrdered,
  Shuffle,
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const revisionStore = useRevisionStore()

const setId = Number(route.params.id)
const loading = ref(true)
const loadError = ref(false)
const set = ref<RevisionSet | null>(null)
const items = ref<RevisionItem[]>([])
const showSetModal = ref(false)
const showItemModal = ref(false)

const TYPE_META: Record<RevisionItemType, { label: string; icon: unknown }> = {
  flashcard: { label: 'Flashcards', icon: Layers },
  qcm: { label: 'QCM', icon: HelpCircle },
  vf: { label: 'Vrai / Faux', icon: Rows3 },
  definition: { label: 'Définition', icon: BookOpen },
  ordre: { label: 'Ordre', icon: ListOrdered },
  association: { label: 'Association', icon: Shuffle },
}

function formatLastReviewed(items: RevisionItem[]): string {
  const dates = items
    .map((i) => i.updated_at)
    .filter(Boolean)
    .sort()
    .reverse()
  if (dates.length === 0) return 'jamais passé'
  const days = Math.floor((Date.now() - new Date(dates[0]).getTime()) / 86400000)
  if (days <= 0) return "dernier passage aujourd'hui"
  if (days === 1) return 'dernier passage hier'
  return `dernier passage il y a ${days} jours`
}

const typeGroups = computed(() => {
  const byType = new Map<RevisionItemType, RevisionItem[]>()
  for (const item of items.value) {
    const list = byType.get(item.type) ?? []
    list.push(item)
    byType.set(item.type, list)
  }
  return Array.from(byType.entries()).map(([type, groupItems]) => ({
    type,
    items: groupItems,
    label: TYPE_META[type].label,
    icon: TYPE_META[type].icon,
    lastReviewedLabel: formatLastReviewed(groupItems),
  }))
})

async function load() {
  loading.value = true
  loadError.value = false
  try {
    const [fetchedSet, fetchedItems] = await Promise.all([
      revisionStore.fetchSet(setId),
      revisionStore.fetchItems(setId),
    ])
    set.value = fetchedSet
    items.value = fetchedItems
  } catch (e) {
    console.error("Erreur de chargement de l'ensemble", e)
    loadError.value = true
  } finally {
    loading.value = false
  }
}

onMounted(load)

function studySet(type?: RevisionItemType) {
  router.push(type ? `/revision/sets/${setId}/study?type=${type}` : `/revision/sets/${setId}/study`)
}

async function deleteGroup(group: {
  type: RevisionItemType
  items: RevisionItem[]
  label: string
}) {
  const count = group.items.length
  const noun = group.label.toLowerCase()
  if (!confirm(`Supprimer les ${count} ${noun} de cet ensemble ?`)) return
  for (const item of group.items) {
    await revisionStore.deleteItem(setId, item.id)
  }
  await load()
}

function onSetUpdated() {
  showSetModal.value = false
  load()
}

function onItemCreated() {
  showItemModal.value = false
  load()
}
</script>
