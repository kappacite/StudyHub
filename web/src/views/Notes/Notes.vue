<template>
  <PageContainer>
    <PageHeader title="Mes Notes de Cours" subtitle="Rédigez, organisez et structurez vos cours au format Markdown ou texte enrichi">
      <template #actions>
        <BaseButton @click="createNewNote">
          <template #icon><Plus class="w-4 h-4" /></template>
          Nouvelle note
        </BaseButton>
      </template>
    </PageHeader>

    <!-- Recherche & filtre classeur -->
    <div class="flex flex-col sm:flex-row gap-3 items-center rounded-2xl border border-line bg-surface p-4">
      <div class="relative flex-1 w-full">
        <Search class="absolute left-3.5 top-3 h-4.5 w-4.5 text-ink-subtle" />
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Rechercher une note par son titre..."
          class="block w-full pl-11 pr-4 py-2.5 bg-surface-soft border border-line rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/40 text-sm font-medium text-ink transition-all"
        />
      </div>
      <div class="w-full sm:w-48">
        <select
          v-model="selectedBinderFilter"
          class="block w-full px-4 py-2.5 bg-surface-soft border border-line rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/40 text-sm font-medium text-ink transition-all"
        >
          <option :value="null">Tous les classeurs</option>
          <option value="none">Sans classeur</option>
          <option v-for="b in bindersStore.binders" :key="b.id" :value="b.id">{{ b.name }}</option>
        </select>
      </div>
    </div>

    <!-- Filtre par tags -->
    <div class="flex flex-wrap items-center gap-2 rounded-2xl border border-line bg-surface p-3">
      <span class="text-xs font-bold uppercase tracking-wider text-ink-subtle mr-1">Filtrer par tag</span>
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

    <!-- Loading -->
    <div v-if="notesStore.loading" class="flex flex-col items-center justify-center py-20 gap-3">
      <svg class="animate-spin h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="text-sm font-semibold text-ink-subtle uppercase tracking-widest">Chargement de vos notes...</span>
    </div>

    <!-- Liste des notes -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <BaseCard
        v-for="note in filteredNotes"
        :key="note.id"
        interactive
        class="flex flex-col justify-between group cursor-pointer"
        @click="router.push(`/notes/${note.id}?edit=false`)"
      >
        <div>
          <div class="flex items-start justify-between gap-3">
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-lg text-[10px] font-bold uppercase tracking-wider" :class="getBinderBadgeClass(note.binder_id)">
              {{ getBinderName(note.binder_id) }}
            </span>
            <button
              @click.stop="confirmDelete(note)"
              class="opacity-0 group-hover:opacity-100 p-1.5 text-ink-subtle hover:text-danger rounded-lg hover:bg-danger-soft transition-all"
              title="Supprimer la note"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>

          <h3 class="font-bold text-lg text-ink mt-4 line-clamp-1">{{ note.title || 'Note sans titre' }}</h3>
          <div v-if="note.tags?.length" class="mt-2 flex flex-wrap gap-1">
            <TagBadge v-for="tag in note.tags" :key="tag.id" :tag="tag" />
          </div>
          <p class="text-xs text-ink-muted mt-2 line-clamp-3 leading-relaxed">
            {{ stripHtml(note.content) || 'Aucun contenu...' }}
          </p>
        </div>

        <div class="flex items-center justify-between mt-6 pt-4 border-t border-line-soft">
          <span class="text-[10px] text-ink-subtle font-semibold uppercase tracking-wider">Créé le {{ new Date(note.created_at).toLocaleDateString('fr-FR') }}</span>
          <div class="flex items-center gap-2">
            <BaseButton variant="secondary" size="sm" @click.stop="router.push(`/notes/${note.id}?edit=false`)" title="Visualiser la note">
              <template #icon><Eye class="w-3.5 h-3.5 text-cat-note" /></template>
              Visualiser
            </BaseButton>
            <BaseButton size="sm" @click.stop="router.push(`/notes/${note.id}?edit=true`)" title="Éditer la note">
              <template #icon><Edit3 class="w-3.5 h-3.5" /></template>
              Éditer
            </BaseButton>
          </div>
        </div>
      </BaseCard>

      <div
        v-if="filteredNotes.length === 0"
        class="col-span-full border-2 border-dashed border-line rounded-3xl p-12 flex flex-col items-center justify-center text-center text-ink-subtle"
      >
        <FileText class="w-12 h-12 text-cat-note/40 mb-3" />
        <h4 class="font-bold text-ink">Aucune note trouvée</h4>
        <p class="text-xs mt-1">Modifiez vos filtres ou créez une nouvelle note !</p>
        <BaseButton size="sm" class="mt-4" @click="createNewNote">Créer une note</BaseButton>
      </div>
    </div>
  </PageContainer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotesStore } from '../../stores/notes'
import type { Note } from '../../stores/notes'
import { useBindersStore } from '../../stores/binders'
import { useTagsStore } from '../../stores/tags'
import TagBadge from '../../components/ui/TagBadge.vue'
import { PageContainer, PageHeader, BaseButton, BaseCard } from '../../components/ui/base'
import { Plus, Search, FileText, Trash2, Eye, Edit3 } from '@lucide/vue'

const notesStore = useNotesStore()
const bindersStore = useBindersStore()
const tagsStore = useTagsStore()
const router = useRouter()

const searchQuery = ref('')
const selectedBinderFilter = ref<string | null>(null)
const selectedTagId = ref<number | null>(null)

onMounted(async () => {
  await notesStore.fetchNotes()
  await bindersStore.fetchBinders()
  await tagsStore.fetchTags()
})

async function filterByTag(tagId: number | null) {
  selectedTagId.value = tagId
  await notesStore.fetchNotes(tagId)
}

const filteredNotes = computed(() => {
  return notesStore.notes.filter(note => {
    const matchesSearch = note.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                          note.content.toLowerCase().includes(searchQuery.value.toLowerCase())

    let matchesBinder = true
    if (selectedBinderFilter.value === 'none') {
      matchesBinder = note.binder_id === null
    } else if (selectedBinderFilter.value !== null) {
      matchesBinder = note.binder_id === selectedBinderFilter.value
    }

    return matchesSearch && matchesBinder
  })
})

function getBinderName(binderId: string | null): string {
  if (binderId === null) return 'Général'
  const binder = bindersStore.binders.find(b => b.id === binderId)
  return binder ? binder.name : 'Général'
}

function getBinderBadgeClass(binderId: string | null): string {
  if (binderId === null) {
    return 'bg-surface-soft text-ink-muted'
  }
  // Alterne les teintes catégorielles selon un hash de l'id.
  const styles = [
    'bg-primary-soft text-primary',
    'bg-cat-set-soft text-cat-set',
    'bg-cat-note-soft text-cat-note',
    'bg-accent-soft text-accent',
  ]
  const code = binderId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  return styles[code % styles.length]
}

function stripHtml(html: string): string {
  const tmp = document.createElement('DIV')
  tmp.innerHTML = html
  return tmp.textContent || tmp.innerText || ''
}

async function createNewNote() {
  const newNote = await notesStore.createNote('Note sans titre')
  router.push(`/notes/${newNote.id}?edit=true`)
}

async function confirmDelete(note: Note) {
  if (confirm(`Êtes-vous sûr de vouloir supprimer la note "${note.title}" ?`)) {
    await notesStore.deleteNote(note.id)
  }
}
</script>
