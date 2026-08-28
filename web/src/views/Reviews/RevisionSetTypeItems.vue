<template>
  <PageContainer size="narrow">
    <div class="flex items-center justify-between text-sm font-semibold mb-4">
      <router-link
        data-test="back-to-set-link"
        :to="`/revision/sets/${setId}`"
        class="text-ink-muted hover:text-primary flex items-center gap-1"
      >
        <ChevronLeft class="w-4 h-4" /> Retour à l'ensemble
      </router-link>
      <span
        v-if="setMeta"
        class="text-xs font-bold text-primary bg-primary-soft px-2.5 py-1 rounded-lg uppercase tracking-wider"
      >
        {{ typeLabel }} · {{ setMeta.name }}
      </span>
    </div>

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

    <template v-else>
      <div class="flex items-center justify-between mb-3">
        <h2 class="font-display text-lg font-bold text-ink">{{ typeLabel }}</h2>
        <BaseButton size="sm" @click="openAdd">
          <template #icon><Plus class="w-4 h-4" /></template>
          Ajouter un élément
        </BaseButton>
      </div>

      <BaseCard padding="sm">
        <div v-if="filteredItems.length" class="space-y-2">
          <div
            v-for="it in filteredItems"
            :key="it.id"
            class="flex items-center gap-2 border border-line rounded-xl p-3"
          >
            <span class="min-w-0 flex-1 text-sm font-semibold text-ink truncate">{{
              itemLabel(it)
            }}</span>
            <button
              data-test="edit-item-button"
              class="p-1.5 text-ink-subtle hover:text-primary rounded-lg hover:bg-primary-soft"
              title="Modifier"
              @click="openEdit(it)"
            >
              <Pencil class="w-4 h-4" />
            </button>
            <button
              data-test="delete-item-button"
              class="p-1.5 text-ink-subtle hover:text-danger rounded-lg hover:bg-danger-soft"
              title="Supprimer"
              @click="confirmDelete(it.id)"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>
        <p v-else class="text-center py-10 text-xs text-ink-subtle uppercase tracking-wider">
          Aucun élément de ce type.
        </p>
      </BaseCard>
    </template>

    <RevisionItemModal
      v-if="showModal"
      :binder-id="null"
      :decks="[]"
      :edit-item="editingItem || undefined"
      :locked-set-id="setId"
      :locked-type="itemType"
      @close="closeModal"
      @created="onSaved"
      @updated="onSaved"
    />
  </PageContainer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useRevisionStore } from '../../stores/revision'
import type { RevisionItem, RevisionItemType, RevisionSet } from '../../stores/revision'
import RevisionItemModal from '../../components/decks/RevisionItemModal.vue'
import { PageContainer, BaseCard, BaseButton, BaseEmptyState } from '../../components/ui/base'
import { ChevronLeft, Pencil, Trash2, Plus, AlertCircle } from 'lucide-vue-next'

const route = useRoute()
const revisionStore = useRevisionStore()

const setId = Number(route.params.id)
const itemType = route.params.type as RevisionItemType

const TYPE_LABELS: Record<RevisionItemType, string> = {
  flashcard: 'Flashcards',
  qcm: 'QCM',
  vf: 'Vrai / Faux',
  definition: 'Définition',
  ordre: 'Ordre',
  association: 'Association',
}
const typeLabel = computed(() => TYPE_LABELS[itemType])

const loading = ref(true)
const loadError = ref(false)
const setMeta = ref<RevisionSet | null>(null)
const allItems = ref<RevisionItem[]>([])
const filteredItems = computed(() => allItems.value.filter((i) => i.type === itemType))
const editingItem = ref<RevisionItem | null>(null)
const showModal = ref(false)

function itemLabel(it: RevisionItem): string {
  const p = it.payload || {}
  return (
    p.question ||
    p.assertion ||
    p.term ||
    p.front ||
    p.title ||
    (p.pairs?.length ? `${p.pairs.length} paire(s)` : '') ||
    'Élément sans intitulé'
  )
}

async function load() {
  loading.value = true
  loadError.value = false
  try {
    ;[setMeta.value, allItems.value] = await Promise.all([
      revisionStore.fetchSet(setId),
      revisionStore.fetchItems(setId),
    ])
  } catch (e) {
    console.error('Erreur de chargement', e)
    loadError.value = true
  } finally {
    loading.value = false
  }
}

onMounted(load)

function openAdd() {
  editingItem.value = null
  showModal.value = true
}
function openEdit(it: RevisionItem) {
  editingItem.value = it
  showModal.value = true
}
function closeModal() {
  showModal.value = false
  editingItem.value = null
}
async function onSaved() {
  closeModal()
  allItems.value = await revisionStore.fetchItems(setId)
}

async function confirmDelete(itemId: number) {
  if (!confirm('Supprimer cet élément ? Cette action est définitive.')) return
  try {
    await revisionStore.deleteItem(setId, itemId)
    allItems.value = await revisionStore.fetchItems(setId)
  } catch (e) {
    console.error('Erreur lors de la suppression', e)
    alert('Impossible de supprimer cet élément.')
  }
}
</script>
