<template>
  <PageContainer size="wide">
    <PageHeader title="Bibliothèque" :breadcrumbs="breadcrumbItems">
      <template #actions>
        <template v-if="isOwner">
          <BaseButton v-if="currentBinderId !== null" variant="secondary" size="sm" @click="router.push(`/revision/binders/${currentBinderId}/stats`)">
            <template #icon><BarChart3 class="w-4 h-4" /></template>
            Stats
          </BaseButton>
          <BaseButton
            v-if="currentBinderId !== null"
            :variant="currentBinder?.is_public ? 'soft' : 'secondary'"
            size="sm"
            @click="openShareModal"
          >
            <template #icon><Globe class="w-4 h-4" /></template>
            {{ currentBinder?.is_public ? 'Public' : 'Partager' }}
          </BaseButton>
          <BaseButton
            v-if="currentBinderId !== null"
            :variant="isSharedToClass ? 'soft' : 'secondary'"
            size="sm"
            @click="openClassShareModal"
          >
            <template #icon><GraduationCap class="w-4 h-4" /></template>
            {{ isSharedToClass ? `Partagé (${sharedClasses.length})` : 'Classe' }}
          </BaseButton>

          <div class="relative">
            <BaseButton size="sm" @click="showAddMenu = !showAddMenu">
              <template #icon><Plus class="w-4 h-4" /></template>
              Ajouter
              <ChevronDown class="w-4 h-4" />
            </BaseButton>
            <template v-if="showAddMenu">
              <div class="fixed inset-0 z-10" @click="showAddMenu = false"></div>
              <div class="absolute right-0 mt-2 w-60 bg-surface border border-line rounded-2xl shadow-elev-3 z-20 p-1.5 animate-pop-in">
                <button v-for="item in addMenu" :key="item.label" @click="item.action" class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold text-ink hover:bg-surface-soft transition-colors text-left">
                  <component :is="item.icon" class="w-4 h-4 text-primary shrink-0" />
                  {{ item.label }}
                </button>
              </div>
            </template>
          </div>
        </template>
        <BaseButton v-else :loading="cloning" @click="cloneBinder">
          <template #icon><Copy class="w-4 h-4" /></template>
          {{ cloning ? 'Copie en cours...' : 'Créer une copie personnelle' }}
        </BaseButton>
      </template>

      <template #tabs>
        <Tabs v-model="activeType" :tabs="contentTabs" />
      </template>
    </PageHeader>

    <!-- Filtre par tags -->
    <div class="flex flex-wrap items-center gap-2 rounded-2xl border border-line bg-surface p-3">
      <span class="text-xs font-bold uppercase tracking-wider text-ink-subtle">Filtrer</span>
      <button
        type="button"
        class="rounded-full px-3 py-1.5 text-xs font-bold transition-colors"
        :class="selectedTagId === null ? 'bg-primary text-white' : 'bg-surface-soft text-ink-muted'"
        @click="filterByTag(null)"
      >Tous</button>
      <button
        v-for="tag in tagsStore.tags"
        :key="tag.id"
        type="button"
        class="rounded-full px-3 py-1.5 text-xs font-bold transition-colors"
        :style="selectedTagId === tag.id ? { backgroundColor: tag.color || '#F06292', color: '#fff' } : undefined"
        :class="selectedTagId === tag.id ? '' : 'bg-surface-soft text-ink-muted'"
        @click="filterByTag(tag.id)"
      >{{ tag.name }}</button>
    </div>

    <!-- Bandeau lecture seule -->
    <div v-if="!isOwner" class="p-4 bg-warning-soft border border-warning/30 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-warning">
      <div class="flex items-center gap-2">
        <Eye class="w-5 h-5 shrink-0" />
        <span class="text-xs font-semibold text-ink-muted">Vous visualisez ce dossier en lecture seule (cours suivi). Pour le modifier, créez une copie personnelle.</span>
      </div>
      <BaseButton variant="soft" size="sm" :loading="cloning" @click="cloneBinder">
        <template #icon><Copy class="w-3.5 h-3.5" /></template>
        Créer une copie
      </BaseButton>
    </div>

    <!-- Loading -->
    <div v-if="bindersStore.loading" class="flex flex-col items-center justify-center py-20 gap-3">
      <svg class="animate-spin h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="text-sm font-semibold text-ink-subtle uppercase tracking-widest">Chargement...</span>
    </div>

    <SplitView v-else>
      <!-- Colonne gauche : arbre des dossiers -->
      <template #left>
        <BaseCard padding="sm">
          <div class="flex items-center justify-between mb-2 px-1">
            <h3 class="text-xs font-bold uppercase tracking-wider text-ink-subtle">Dossiers</h3>
            <button v-if="isOwner" @click="openCreateModal" class="p-1 rounded-lg text-primary hover:bg-primary-soft transition-colors" title="Nouveau dossier">
              <FolderPlus class="w-4 h-4" />
            </button>
          </div>
          <div class="space-y-1">
            <ListRow
              v-for="folder in currentSubBinders"
              :key="folder.id"
              interactive
              class="group"
              @click="goTo(folder.id)"
            >
              <template #leading>
                <div class="w-9 h-9 rounded-xl bg-primary-soft text-primary flex items-center justify-center">
                  <FolderClosed class="w-4.5 h-4.5" />
                </div>
              </template>
              <div class="min-w-0">
                <span class="font-semibold text-sm text-ink truncate block">{{ folder.name }}</span>
                <span v-if="folder.read_only" class="text-[9px] font-bold uppercase tracking-wide text-warning">Cours</span>
                <div v-if="folder.tags?.length" class="mt-1 flex flex-wrap gap-1">
                  <TagBadge v-for="tag in folder.tags" :key="tag.id" :tag="tag" />
                </div>
              </div>
              <template #trailing>
                <button
                  v-if="isOwner"
                  @click.stop="confirmDelete(folder)"
                  class="opacity-0 group-hover:opacity-100 p-1.5 text-ink-subtle hover:text-danger rounded-lg hover:bg-danger-soft transition-all"
                  title="Supprimer"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </template>
            </ListRow>
            <p v-if="currentSubBinders.length === 0" class="text-center py-6 text-ink-subtle text-xs font-semibold uppercase tracking-wider">
              Aucun sous-dossier
            </p>
          </div>
        </BaseCard>
      </template>

      <!-- Colonne droite : contenu typé -->
      <template #right>
        <div class="space-y-6">
          <!-- Notes -->
          <BaseCard v-if="showSection('notes')">
            <h3 class="font-bold text-sm text-ink flex items-center gap-2 mb-3">
              <FileText class="w-4 h-4 text-cat-note" />
              Notes ({{ currentNotes.length }})
            </h3>
            <div class="space-y-1">
              <ListRow
                v-for="note in currentNotes"
                :key="note.id"
                interactive
                class="group"
                :title="note.title"
                @click="router.push(`/notes/${note.id}`)"
              >
                <template #leading><div class="w-9 h-9 rounded-xl bg-cat-note-soft text-cat-note flex items-center justify-center"><FileText class="w-4.5 h-4.5" /></div></template>
                <template #trailing>
                  <span v-if="note.read_only" class="px-1.5 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wide bg-warning-soft text-warning">Cours</span>
                  <button v-if="isOwner" @click.stop="detachItem('note', note.id)" class="opacity-0 group-hover:opacity-100 p-1.5 text-ink-subtle hover:text-warning rounded-lg hover:bg-warning-soft transition-all" title="Retirer du classeur"><FolderMinus class="w-4 h-4" /></button>
                  <ChevronRight class="w-4 h-4 text-ink-subtle" />
                </template>
              </ListRow>
              <p v-if="currentNotes.length === 0" class="text-center py-6 text-ink-subtle text-xs font-semibold uppercase tracking-wider">Aucune note</p>
            </div>
          </BaseCard>

          <!-- Decks -->
          <BaseCard v-if="showSection('decks')">
            <h3 class="font-bold text-sm text-ink flex items-center gap-2 mb-3">
              <Layers class="w-4 h-4 text-cat-deck" />
              Jeux de révision ({{ currentDecks.length }})
            </h3>
            <div class="space-y-1">
              <ListRow
                v-for="deck in currentDecks"
                :key="deck.id"
                interactive
                class="group"
                :title="deck.name"
                :subtitle="`${deck.card_count} item(s)`"
                @click="router.push(`/decks/${deck.id}/study`)"
              >
                <template #leading><div class="w-9 h-9 rounded-xl bg-cat-deck-soft text-cat-deck flex items-center justify-center"><Layers class="w-4.5 h-4.5" /></div></template>
                <template #trailing>
                  <button v-if="isOwner" @click.stop="detachItem('deck', deck.id)" class="opacity-0 group-hover:opacity-100 p-1.5 text-ink-subtle hover:text-warning rounded-lg hover:bg-warning-soft transition-all" title="Retirer du classeur"><FolderMinus class="w-4 h-4" /></button>
                  <ChevronRight class="w-4 h-4 text-ink-subtle" />
                </template>
              </ListRow>
              <p v-if="currentDecks.length === 0" class="text-center py-6 text-ink-subtle text-xs font-semibold uppercase tracking-wider">Aucun jeu de révision</p>
            </div>
          </BaseCard>

          <!-- Ensembles de révision -->
          <BaseCard v-if="showSection('sets')">
            <h3 class="font-bold text-sm text-ink flex items-center gap-2 mb-3">
              <FileQuestion class="w-4 h-4 text-cat-set" />
              Ensembles de révision ({{ currentSets.length }})
            </h3>
            <div class="space-y-1">
              <ListRow
                v-for="set in currentSets"
                :key="set.id"
                interactive
                class="group"
                :title="set.name"
                :subtitle="`${REVISION_TYPE_LABELS[set.type]} · ${set.item_count} item(s)`"
                @click="openSet(set)"
              >
                <template #leading><div class="w-9 h-9 rounded-xl bg-cat-set-soft text-cat-set flex items-center justify-center"><FileQuestion class="w-4.5 h-4.5" /></div></template>
                <template #trailing>
                  <button @click.stop="router.push(`/revision/sets/${set.id}/stats`)" class="p-1.5 text-ink-subtle hover:text-primary rounded-lg hover:bg-primary-soft" title="Statistiques"><BarChart3 class="w-4 h-4" /></button>
                  <button v-if="isOwner" @click.stop="detachItem('set', set.id)" class="p-1.5 text-ink-subtle hover:text-warning rounded-lg hover:bg-warning-soft" title="Retirer du classeur"><FolderMinus class="w-4 h-4" /></button>
                  <ChevronRight class="w-4 h-4 text-ink-subtle" />
                </template>
              </ListRow>
              <p v-if="currentSets.length === 0" class="text-center py-6 text-ink-subtle text-xs font-semibold uppercase tracking-wider">Aucun ensemble de révision</p>
            </div>
          </BaseCard>

          <!-- Diagrammes -->
          <BaseCard v-if="showSection('diagrams')">
            <h3 class="font-bold text-sm text-ink flex items-center gap-2 mb-3">
              <Activity class="w-4 h-4 text-cat-diagram" />
              Diagrammes ({{ currentDiagrams.length }})
            </h3>
            <div class="space-y-1">
              <ListRow
                v-for="diagram in currentDiagrams"
                :key="diagram.id"
                interactive
                class="group"
                :title="diagram.title || 'Diagramme sans titre'"
                @click="router.push(`/diagrams?id=${diagram.id}`)"
              >
                <template #leading><div class="w-9 h-9 rounded-xl bg-cat-diagram-soft text-cat-diagram flex items-center justify-center"><Activity class="w-4.5 h-4.5" /></div></template>
                <template #trailing>
                  <button v-if="isOwner" @click.stop="detachItem('diagram', diagram.id)" class="opacity-0 group-hover:opacity-100 p-1.5 text-ink-subtle hover:text-warning rounded-lg hover:bg-warning-soft transition-all" title="Retirer du classeur"><FolderMinus class="w-4 h-4" /></button>
                  <ChevronRight class="w-4 h-4 text-ink-subtle" />
                </template>
              </ListRow>
              <p v-if="currentDiagrams.length === 0" class="text-center py-6 text-ink-subtle text-xs font-semibold uppercase tracking-wider">Aucun diagramme</p>
            </div>
          </BaseCard>

          <!-- PDF -->
          <BaseCard v-if="showSection('pdfs')">
            <h3 class="font-bold text-sm text-ink flex items-center gap-2 mb-3">
              <FileDown class="w-4 h-4 text-cat-pdf" />
              Documents PDF ({{ currentPdfs.length }})
            </h3>
            <div class="space-y-1">
              <ListRow
                v-for="pdf in currentPdfs"
                :key="pdf.id"
                interactive
                class="group"
                :title="pdf.name"
                @click="router.push('/pdfs')"
              >
                <template #leading><div class="w-9 h-9 rounded-xl bg-cat-pdf-soft text-cat-pdf flex items-center justify-center"><FileDown class="w-4.5 h-4.5" /></div></template>
                <template #trailing>
                  <button v-if="isOwner && !pdf.read_only" @click.stop="detachItem('pdf', pdf.id)" class="opacity-0 group-hover:opacity-100 p-1.5 text-ink-subtle hover:text-warning rounded-lg hover:bg-warning-soft transition-all" title="Retirer du classeur"><FolderMinus class="w-4 h-4" /></button>
                  <ChevronRight class="w-4 h-4 text-ink-subtle" />
                </template>
              </ListRow>
              <p v-if="currentPdfs.length === 0" class="text-center py-6 text-ink-subtle text-xs font-semibold uppercase tracking-wider">Aucun document PDF</p>
            </div>
          </BaseCard>
        </div>
      </template>
    </SplitView>

    <!-- Modale : rattacher un élément existant -->
    <BaseModal :open="showAttachModal" title="Ajouter un élément existant" size="lg" @close="showAttachModal = false">
      <p class="text-xs text-ink-muted -mt-2 mb-4">Déplace des éléments non rangés ou d'un autre classeur vers celui-ci.</p>
      <div class="max-h-[55vh] overflow-y-auto -mx-2 px-2 space-y-4">
        <div v-for="group in attachableGroups" :key="group.type">
          <p v-if="group.items.length" class="text-[10px] font-bold text-ink-subtle uppercase tracking-widest mb-1.5">{{ group.label }}</p>
          <label v-for="it in group.items" :key="`${group.type}:${it.id}`" class="flex items-center gap-3 p-2.5 rounded-xl hover:bg-surface-soft cursor-pointer">
            <input type="checkbox" :checked="isSelected(group.type, it.id)" @change="toggleSelect(group.type, it.id)" class="rounded border-line text-primary focus:ring-primary" />
            <span class="text-sm font-semibold text-ink truncate">{{ it.label }}</span>
          </label>
        </div>
        <p v-if="attachableGroups.every(g => g.items.length === 0)" class="text-center py-8 text-xs text-ink-subtle uppercase tracking-wider">Aucun élément disponible à rattacher.</p>
      </div>
      <template #footer>
        <BaseButton variant="ghost" @click="showAttachModal = false">Annuler</BaseButton>
        <BaseButton :disabled="selectedCount === 0" :loading="attaching" @click="confirmAttach">Ajouter{{ selectedCount ? ` (${selectedCount})` : '' }}</BaseButton>
      </template>
    </BaseModal>

    <!-- Modale : créer un dossier -->
    <BaseModal :open="showModal" title="Créer un nouveau dossier" @close="showModal = false">
      <form @submit.prevent="createFolder" class="space-y-4">
        <BaseField label="Nom du dossier" for-id="folder-name">
          <BaseInput id="folder-name" v-model="newFolderName" placeholder="Ex: Anatomie, Semestre 2..." />
        </BaseField>
        <BaseField label="Tags">
          <TagSelector v-model="folderTags" />
        </BaseField>
        <div class="flex items-center justify-end gap-2 pt-2">
          <BaseButton type="button" variant="ghost" @click="showModal = false">Annuler</BaseButton>
          <BaseButton type="submit">Créer</BaseButton>
        </div>
      </form>
    </BaseModal>

    <!-- Modale : partage communautaire -->
    <BaseModal :open="showShareModal" title="Partager sur l'Espace Communautaire" @close="showShareModal = false">
      <p class="text-xs text-ink-muted -mt-2 mb-4">Publiez ce classeur et ses ressources pour les rendre accessibles à la communauté.</p>
      <form @submit.prevent="saveShareSettings" class="space-y-4">
        <div class="flex items-center justify-between p-3.5 bg-surface-soft border border-line rounded-2xl">
          <div>
            <span class="block text-xs font-bold text-ink">Statut de visibilité</span>
            <span class="text-[10px] text-ink-subtle">{{ shareIsPublic ? 'Visible sur la Marketplace' : 'Visible uniquement par vous' }}</span>
          </div>
          <BaseButton type="button" size="sm" :variant="shareIsPublic ? 'soft' : 'secondary'" @click="shareIsPublic = !shareIsPublic">
            {{ shareIsPublic ? 'Public' : 'Privé' }}
          </BaseButton>
        </div>
        <BaseField label="Description" for-id="share-description">
          <textarea id="share-description" v-model="shareDescription" rows="3" placeholder="Décrivez le contenu de ce dossier..." class="block w-full px-4 py-3 bg-surface border border-line rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/40 text-sm font-medium text-ink"></textarea>
        </BaseField>
        <BaseField label="Mots-clés (séparés par des virgules)" for-id="share-tags">
          <BaseInput id="share-tags" v-model="shareTags" placeholder="Ex: Chimie, Médecine, Semestre 1" />
        </BaseField>
        <div class="flex items-center justify-end gap-2 pt-2">
          <BaseButton type="button" variant="ghost" @click="showShareModal = false">Annuler</BaseButton>
          <BaseButton type="submit">Enregistrer</BaseButton>
        </div>
      </form>
    </BaseModal>

    <!-- Modale : partage à une classe -->
    <BaseModal :open="showClassShareModal" title="Partager ce classeur à une classe" @close="showClassShareModal = false">
      <p class="text-xs text-ink-muted -mt-2 mb-4">Le classeur est partagé <strong>par référence</strong> : tout élément ajouté ensuite devient automatiquement visible des élèves, en lecture seule.</p>
      <div v-if="classShareBusy && myClasses.length === 0" class="py-8 text-center text-sm text-ink-subtle"><Loader2 class="w-5 h-5 animate-spin inline" /></div>
      <div v-else-if="ownedClasses.length === 0" class="py-8 text-center text-sm text-ink-subtle">Vous n'animez aucune classe pour l'instant.</div>
      <ul v-else class="space-y-2 max-h-72 overflow-y-auto">
        <li v-for="c in ownedClasses" :key="c.id" class="flex items-center justify-between p-3 bg-surface-soft border border-line rounded-2xl">
          <div class="min-w-0">
            <p class="text-sm font-bold text-ink truncate">{{ c.name }}</p>
            <span class="text-[10px] text-ink-subtle">{{ c.members_count }} membre(s)</span>
          </div>
          <BaseButton size="sm" :variant="isClassShared(c.id) ? 'soft' : 'secondary'" :disabled="classShareBusy" @click="toggleClassShare(c)">
            {{ isClassShared(c.id) ? 'Partagé ✓' : 'Partager' }}
          </BaseButton>
        </li>
      </ul>
      <template #footer>
        <BaseButton variant="ghost" @click="showClassShareModal = false">Fermer</BaseButton>
      </template>
    </BaseModal>
  </PageContainer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../services/api'
import { useBindersStore } from '../../stores/binders'
import type { Binder } from '../../stores/binders'
import { useNotesStore } from '../../stores/notes'
import { useDecksStore } from '../../stores/decks'
import { useTagsStore, type Tag } from '../../stores/tags'
import TagBadge from '../../components/ui/TagBadge.vue'
import TagSelector from '../../components/ui/TagSelector.vue'
import { PageContainer, PageHeader, Tabs, SplitView, ListRow, BaseCard, BaseButton, BaseModal, BaseField, BaseInput } from '../../components/ui/base'
import type { TabItem } from '../../components/ui/base'
import { useRevisionStore } from '../../stores/revision'
import type { RevisionType } from '../../stores/revision'

const REVISION_TYPE_LABELS: Record<RevisionType, string> = {
  qcm: 'QCM',
  vf: 'Vrai / Faux',
  association: 'Association',
  definition: 'Définition',
  ordre: 'Ordre',
}
import { FolderClosed, Plus, ChevronRight, ChevronDown, FileText, Layers, Trash2, Globe, Copy, Eye, Loader2, FolderPlus, FileQuestion, BarChart3, FolderMinus, FolderInput, GraduationCap, Activity, FileDown } from 'lucide-vue-next'
import groupService, { type BinderClassRef } from '../../services/groupService'
import classService, { type ClassInfo } from '../../services/classService'
import type { BinderItemType } from '../../stores/binders'

const bindersStore = useBindersStore()
const notesStore = useNotesStore()
const decksStore = useDecksStore()
const revisionStore = useRevisionStore()
const tagsStore = useTagsStore()
const router = useRouter()
const route = useRoute()

const currentBinderId = ref<string | null>(null)

// ─── Onglets de type de contenu (filtre du dossier courant) ─────────────────
type ContentType = 'all' | 'notes' | 'decks' | 'sets' | 'diagrams' | 'pdfs'
function isValidType(v: unknown): v is ContentType {
  return v === 'all' || v === 'notes' || v === 'decks' || v === 'sets' || v === 'diagrams' || v === 'pdfs'
}
const activeType = ref<ContentType>(isValidType(route.query.type) ? route.query.type : 'all')
function showSection(t: ContentType) {
  return activeType.value === 'all' || activeType.value === t
}
watch(activeType, (t) => {
  const q = t === 'all' ? undefined : t
  if (route.query.type !== q) router.replace({ query: { ...route.query, type: q } })
})

const contentTabs = computed<TabItem[]>(() => [
  { key: 'all', label: 'Tout' },
  { key: 'notes', label: 'Notes', badge: currentNotes.value.length || undefined },
  { key: 'decks', label: 'Decks', badge: currentDecks.value.length || undefined },
  { key: 'sets', label: 'Ensembles', badge: currentSets.value.length || undefined },
  { key: 'diagrams', label: 'Diagrammes', badge: currentDiagrams.value.length || undefined },
  { key: 'pdfs', label: 'PDF', badge: currentPdfs.value.length || undefined },
])

async function fetchMissingBinder(binderId: string) {
  try {
    const response = await api.get(`/binders/${binderId}`)
    const fetchedBinder = response.data
    if (!bindersStore.binders.some(b => b.id === fetchedBinder.id)) {
      bindersStore.binders.push(fetchedBinder)
    }
  } catch (error) {
    console.error('Erreur lors du chargement du classeur', error)
  }
}

// Navigation par URL : /bibliotheque/:id — le watch ci-dessous synchronise l'état.
function goTo(id: string | null) {
  router.push(id ? `/bibliotheque/${id}` : '/bibliotheque')
}

watch(() => route.params.id, (newId) => {
  currentBinderId.value = (newId as string) || null
}, { immediate: true })

watch(currentBinderId, async (newVal) => {
  if (newVal !== null) {
    const exists = bindersStore.binders.some(b => b.id === newVal)
    if (!exists) {
      await fetchMissingBinder(newVal)
    }
  }
}, { immediate: true })
const showModal = ref(false)
const newFolderName = ref('')
const folderTags = ref<Tag[]>([])
const selectedTagId = ref<number | null>(null)

const showAddMenu = ref(false)

const addMenu = [
  { label: 'Sous-dossier', icon: FolderPlus, action: () => closeMenuThen(openCreateModal) },
  { label: 'Élément existant', icon: FolderInput, action: () => closeMenuThen(openAttachModal) },
  { label: 'Note', icon: FileText, action: () => closeMenuThen(addNote) },
  { label: 'Diagramme', icon: Activity, action: () => closeMenuThen(addDiagram) },
]

function closeMenuThen(fn: () => void) {
  showAddMenu.value = false
  fn()
}

async function addNote() {
  const note = await notesStore.createNote('Nouvelle note', '', currentBinderId.value)
  router.push(`/notes/${note.id}?edit=true`)
}

async function addDiagram() {
  // Crée un diagramme rattaché au dossier courant puis ouvre l'éditeur (?id=…).
  // L'éditeur (/diagrams) sélectionne le diagramme via route.query.id.
  const defaultCode = JSON.stringify({
    type: 'visual',
    nodes: [{ id: 1, label: 'Concept central', type: 'rect', x: 250, y: 150, color: 'bg-indigo-600' }],
    connections: [],
    backgroundImage: null,
    masks: [],
  })
  try {
    const res = await api.post('/diagrams', {
      title: 'Nouveau diagramme',
      code: defaultCode,
      binder_id: currentBinderId.value,
    })
    router.push(`/diagrams?id=${res.data.id}`)
  } catch (e) {
    console.error('Erreur lors de la création du diagramme', e)
  }
}

const showShareModal = ref(false)
const shareIsPublic = ref(false)
const shareDescription = ref('')
const shareTags = ref('')

interface BinderDiagram { id: number; title: string; binder_id: string | null }
interface BinderPdf { id: string; name: string; binder_id: string | null; read_only?: boolean }
const allDiagrams = ref<BinderDiagram[]>([])
const allPdfs = ref<BinderPdf[]>([])

async function fetchBinderMedia() {
  try {
    const [diag, pdf] = await Promise.all([
      api.get('/diagrams?per_page=100'),
      api.get('/pdfs?per_page=100'),
    ])
    allDiagrams.value = diag.data.data
    allPdfs.value = pdf.data.data
  } catch (error) {
    console.error('Erreur lors du chargement des diagrammes/PDF', error)
  }
}

onMounted(async () => {
  await Promise.all([
    bindersStore.fetchBinders(),
    notesStore.fetchNotes(),
    decksStore.fetchDecks(),
    revisionStore.fetchSets(),
    tagsStore.fetchTags(),
    fetchBinderMedia()
  ])
})

async function filterByTag(tagId: number | null) {
  selectedTagId.value = tagId
  await bindersStore.fetchBinders(tagId)
}

const currentSubBinders = computed(() => bindersStore.binders.filter(b => b.parent_id === currentBinderId.value))
const currentNotes = computed(() => notesStore.notes.filter(n => n.binder_id === currentBinderId.value))
const currentDecks = computed(() => decksStore.decks.filter(d => d.binder_id === currentBinderId.value))
const currentSets = computed(() => revisionStore.sets.filter(s => s.binder_id === currentBinderId.value))
const currentDiagrams = computed(() => allDiagrams.value.filter(d => d.binder_id === currentBinderId.value))
const currentPdfs = computed(() => allPdfs.value.filter(p => p.binder_id === currentBinderId.value))

function openSet(set: { id: number; type: RevisionType }) {
  const path = set.type === 'qcm' ? 'run' : 'study'
  router.push(`/revision/sets/${set.id}/${path}`)
}

const showAttachModal = ref(false)
const attaching = ref(false)
const selected = ref<Record<string, { type: BinderItemType; id: number | string }>>({})

const attachableGroups = computed(() => {
  const cur = currentBinderId.value
  return [
    { type: 'note' as BinderItemType, label: 'Notes', items: notesStore.notes.filter(n => n.binder_id !== cur && !n.read_only).map(n => ({ id: n.id, label: n.title })) },
    { type: 'deck' as BinderItemType, label: 'Jeux de révision', items: decksStore.decks.filter(d => d.binder_id !== cur).map(d => ({ id: d.id, label: d.name })) },
    { type: 'set' as BinderItemType, label: 'Ensembles de révision', items: revisionStore.sets.filter(s => s.binder_id !== cur).map(s => ({ id: s.id, label: s.name })) },
    { type: 'diagram' as BinderItemType, label: 'Diagrammes', items: allDiagrams.value.filter(d => d.binder_id !== cur).map(d => ({ id: d.id, label: d.title || 'Diagramme sans titre' })) },
    { type: 'pdf' as BinderItemType, label: 'Documents PDF', items: allPdfs.value.filter(p => p.binder_id !== cur && !p.read_only).map(p => ({ id: p.id, label: p.name })) },
  ]
})

const selectedCount = computed(() => Object.keys(selected.value).length)
function keyOf(type: BinderItemType, id: number | string) { return `${type}:${id}` }
function isSelected(type: BinderItemType, id: number | string) { return keyOf(type, id) in selected.value }
function toggleSelect(type: BinderItemType, id: number | string) {
  const k = keyOf(type, id)
  if (k in selected.value) { delete selected.value[k] }
  else { selected.value[k] = { type, id } }
}

function openAttachModal() {
  selected.value = {}
  showAttachModal.value = true
}

async function refreshContentStores() {
  await Promise.all([notesStore.fetchNotes(), decksStore.fetchDecks(), revisionStore.fetchSets(), fetchBinderMedia()])
}

async function confirmAttach() {
  if (!currentBinderId.value || selectedCount.value === 0) return
  attaching.value = true
  try {
    await bindersStore.attachItems(currentBinderId.value, Object.values(selected.value))
    await refreshContentStores()
    showAttachModal.value = false
  } catch (e) {
    console.error("Erreur lors du rattachement d'éléments", e)
  } finally {
    attaching.value = false
  }
}

async function detachItem(type: BinderItemType, id: number | string) {
  if (!currentBinderId.value) return
  try {
    await bindersStore.detachItems(currentBinderId.value, [{ type, id }])
    await refreshContentStores()
  } catch (e) {
    console.error("Erreur lors du retrait de l'élément", e)
  }
}

// Fil d'Ariane (PageHeader) — navigation par URL.
const breadcrumbItems = computed(() => {
  const items: { label: string; to?: string }[] = [{ label: 'Racine', to: '/bibliotheque' }]
  if (currentBinderId.value === null) return items
  const trail: Binder[] = []
  let current = bindersStore.binders.find(b => b.id === currentBinderId.value)
  while (current) {
    trail.unshift(current)
    const parentId = current.parent_id
    current = parentId !== null ? bindersStore.binders.find(b => b.id === parentId) : undefined
  }
  trail.forEach(b => items.push({ label: b.name, to: `/bibliotheque/${b.id}` }))
  return items
})

function openCreateModal() {
  newFolderName.value = ''
  folderTags.value = []
  showModal.value = true
}

async function createFolder() {
  if (newFolderName.value.trim()) {
    const binder = await bindersStore.createBinder(newFolderName.value.trim(), currentBinderId.value)
    if (folderTags.value.length > 0) {
      const updatedTags = await tagsStore.setTagsForEntity('binders', binder.id, folderTags.value.map(tag => tag.id))
      binder.tags = updatedTags
    }
    showModal.value = false
  }
}

async function confirmDelete(folder: Binder) {
  if (confirm(`Êtes-vous sûr de vouloir supprimer le dossier "${folder.name}" et tous ses sous-dossiers ?`)) {
    await bindersStore.deleteBinder(folder.id)
  }
}

const currentBinder = computed(() => {
  if (currentBinderId.value === null) return null
  return bindersStore.binders.find(b => b.id === currentBinderId.value) || null
})

import { useAuthStore } from '../../stores/auth'
const authStore = useAuthStore()
const currentUserId = computed(() => authStore.user?.id)

const isOwner = computed(() => {
  if (currentBinderId.value === null) return true
  return !currentBinder.value || currentBinder.value.user_id === currentUserId.value
})

const cloning = ref(false)
async function cloneBinder() {
  if (currentBinderId.value === null) return
  cloning.value = true
  try {
    const response = await api.post(`/packages/${currentBinderId.value}/clone`)
    const cloned = response.data
    await bindersStore.fetchBinders()
    router.push(`/bibliotheque/${cloned.id}`)
  } catch (err) {
    console.error('Erreur lors du clonage du classeur', err)
    alert('Impossible de copier ce classeur.')
  } finally {
    cloning.value = false
  }
}

function openShareModal() {
  if (!currentBinder.value) return
  shareIsPublic.value = currentBinder.value.is_public || false
  shareDescription.value = currentBinder.value.description || ''
  shareTags.value = currentBinder.value.tags ? currentBinder.value.tags.map(tag => tag.name).join(', ') : ''
  showShareModal.value = true
}

async function saveShareSettings() {
  if (!currentBinder.value) return
  const tagsArray = shareTags.value.split(',').map(t => t.trim()).filter(t => t.length > 0)
  await bindersStore.updateBinder(currentBinder.value.id, {
    is_public: shareIsPublic.value,
    description: shareDescription.value.trim() || null,
    tags: tagsArray.length > 0 ? tagsArray : null
  })
  showShareModal.value = false
}

const showClassShareModal = ref(false)
const myClasses = ref<ClassInfo[]>([])
const sharedClasses = ref<BinderClassRef[]>([])
const classShareBusy = ref(false)

const ownedClasses = computed(() => myClasses.value.filter(c => c.created_by === currentUserId.value))
const isSharedToClass = computed(() => sharedClasses.value.length > 0)

async function loadSharedClasses() {
  if (currentBinderId.value === null || !isOwner.value) {
    sharedClasses.value = []
    return
  }
  try {
    sharedClasses.value = await groupService.getBinderClasses(currentBinderId.value)
  } catch {
    sharedClasses.value = []
  }
}

async function openClassShareModal() {
  if (currentBinderId.value === null) return
  showClassShareModal.value = true
  classShareBusy.value = true
  try {
    myClasses.value = await classService.getMyClasses()
    await loadSharedClasses()
  } finally {
    classShareBusy.value = false
  }
}

function isClassShared(classId: number) {
  return sharedClasses.value.some(c => c.id === classId)
}

async function toggleClassShare(c: ClassInfo) {
  if (currentBinderId.value === null) return
  classShareBusy.value = true
  try {
    if (isClassShared(c.id)) {
      await groupService.unshareBinder(c.id, currentBinderId.value)
    } else {
      await groupService.shareBinder(c.id, currentBinderId.value, 'read')
    }
    await loadSharedClasses()
  } catch {
    alert('Action impossible sur cette classe.')
  } finally {
    classShareBusy.value = false
  }
}

watch(currentBinderId, loadSharedClasses, { immediate: true })
</script>
