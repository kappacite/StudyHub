<template>
  <div class="space-y-6 max-w-3xl mx-auto animate-fade-in">
    <div class="flex items-center justify-between text-sm font-semibold">
      <button @click="goBack" class="text-ink-muted hover:text-primary dark:text-ink-subtle flex items-center gap-1">
        <ChevronLeft class="w-4 h-4" /> Retour
      </button>
      <span v-if="setMeta" class="text-xs font-bold text-primary bg-primary-soft dark:bg-primary-soft dark:text-primary px-2.5 py-1 rounded-lg uppercase tracking-wider">
        Gérer · {{ setMeta.name }}
      </span>
    </div>

    <div v-if="loading" class="py-20 text-center text-sm font-semibold text-ink-subtle uppercase tracking-widest">Chargement…</div>

    <div v-else-if="readOnly" class="bg-warning-soft dark:bg-warning-soft border border-warning text-warning rounded-2xl p-5 text-sm">
      Cet ensemble provient d'un cours partagé : son contenu n'est pas modifiable.
    </div>

    <template v-else-if="setMeta">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-lg font-bold text-ink dark:text-white">{{ setMeta.name }}</h2>
          <p class="text-[11px] font-semibold text-ink-subtle uppercase tracking-wider mt-0.5">
            {{ typeLabel }} · {{ items.length }} élément(s)
          </p>
        </div>
        <button
          @click="openAdd"
          class="inline-flex items-center gap-1.5 px-4 py-2.5 text-xs font-bold text-white bg-primary hover:bg-primary-strong rounded-xl transition-all shadow-md active:scale-95"
        >
          <Plus class="w-4 h-4" /> Ajouter un élément
        </button>
      </div>

      <div class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-2xl p-3 sm:p-5">
        <div v-if="items.length" class="space-y-2">
          <div
            v-for="(it, idx) in items"
            :key="it.id"
            class="flex items-center gap-2 border border-line dark:border-line rounded-xl p-3"
          >
            <span class="shrink-0 w-6 h-6 flex items-center justify-center rounded-lg bg-primary-soft dark:bg-primary-soft text-primary text-[11px] font-bold">{{ idx + 1 }}</span>
            <span class="min-w-0 flex-1 text-sm font-semibold text-ink dark:text-ink-subtle truncate">{{ itemLabel(it) }}</span>
            <button @click="openEdit(it)" class="shrink-0 p-1.5 text-ink-subtle hover:text-primary rounded-lg hover:bg-primary-soft transition-all" title="Modifier l'élément">
              <Pencil class="w-4 h-4" />
            </button>
            <button @click="confirmDelete(it.id)" class="shrink-0 p-1.5 text-ink-subtle hover:text-danger rounded-lg hover:bg-danger-soft transition-all" title="Supprimer l'élément">
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>
        <p v-else class="text-center py-10 text-xs text-ink-subtle uppercase tracking-wider">
          Aucun élément. Cliquez sur « Ajouter un élément » pour commencer.
        </p>
      </div>
    </template>

    <RevisionItemModal
      v-if="showModal"
      :binder-id="null"
      :decks="[]"
      :edit-item="editingItem || undefined"
      :locked-set-id="setId"
      :locked-type="setMeta?.type"
      @close="closeModal"
      @created="onSaved"
      @updated="onSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useRevisionStore } from '../../stores/revision'
import type { RevisionItem, RevisionSet } from '../../stores/revision'
import RevisionItemModal from '../../components/decks/RevisionItemModal.vue'
import { ChevronLeft, Pencil, Trash2, Plus } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const revisionStore = useRevisionStore()

const setId = Number(route.params.id)
const loading = ref(true)
const setMeta = ref<RevisionSet | null>(null)
const items = ref<RevisionItem[]>([])
const editingItem = ref<RevisionItem | null>(null)
const showModal = ref(false)

const readOnly = computed(() => !!setMeta.value?.read_only)

const TYPE_LABELS: Record<string, string> = {
  qcm: 'QCM', vf: 'Vrai / Faux', association: 'Association',
  definition: 'Définition', ordre: 'Ordre',
}
const typeLabel = computed(() => setMeta.value ? (TYPE_LABELS[setMeta.value.type] || setMeta.value.type) : '')

// Libellé lisible dérivé du payload (aligné sur le label backend des stats).
function itemLabel(it: RevisionItem): string {
  const p = it.payload || {}
  return (
    p.question || p.assertion || p.term || p.title ||
    (p.pairs?.length ? `${p.pairs.length} paire(s)` : '') ||
    'Élément sans intitulé'
  )
}

async function load() {
  loading.value = true
  try {
    setMeta.value = await revisionStore.fetchSet(setId)
    if (!setMeta.value.read_only) {
      items.value = await revisionStore.fetchItems(setId)
    }
  } catch (e) {
    console.error('Erreur de chargement de l\'ensemble', e)
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
  items.value = await revisionStore.fetchItems(setId)
}

async function confirmDelete(itemId: number) {
  if (!confirm('Supprimer cet élément ? Cette action est définitive.')) return
  try {
    await revisionStore.deleteItem(setId, itemId)
    items.value = await revisionStore.fetchItems(setId)
  } catch (e) {
    console.error('Erreur lors de la suppression', e)
    alert('Impossible de supprimer cet élément.')
  }
}

function goBack() {
  router.back()
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.4s ease-out forwards; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
