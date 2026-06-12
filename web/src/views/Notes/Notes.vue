<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl font-bold">Mes Notes de Cours</h1>
        <p class="text-xs text-slate-400 dark:text-slate-500 mt-1">Rédigez, organisez et structurez vos cours au format Markdown ou texte enrichi</p>
      </div>
      
      <button 
        @click="createNewNote"
        class="inline-flex items-center gap-2 px-4 py-2 border border-transparent rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition-all shadow-lg shadow-indigo-600/15"
      >
        <Plus class="w-4 h-4" />
        Nouvelle note
      </button>
    </div>

    <!-- Search and Filters -->
    <div class="flex flex-col sm:flex-row gap-4 items-center bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-2xl p-4 shadow-sm">
      <!-- Search Input -->
      <div class="relative flex-1 w-full">
        <Search class="absolute left-3.5 top-3.5 h-4.5 w-4.5 text-slate-400" />
        <input 
          type="text" 
          v-model="searchQuery"
          placeholder="Rechercher une note par son titre..."
          class="block w-full pl-11 pr-4 py-2.5 bg-slate-50 border border-slate-200 dark:bg-slate-800/40 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-medium transition-all"
        />
      </div>
      
      <!-- Binder Filter -->
      <div class="w-full sm:w-48">
        <select 
          v-model="selectedBinderFilter"
          class="block w-full px-4 py-2.5 bg-slate-50 border border-slate-200 dark:bg-slate-800/40 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-medium transition-all"
        >
          <option :value="null">Tous les classeurs</option>
          <option value="none">Sans classeur</option>
          <option v-for="b in bindersStore.binders" :key="b.id" :value="b.id">{{ b.name }}</option>
        </select>
      </div>
    </div>

    <!-- Tag Filter Bar -->
    <div class="flex flex-wrap items-center gap-2 rounded-2xl border border-slate-100 bg-white p-3 dark:border-slate-800 dark:bg-slate-900 shadow-sm">
      <span class="text-xs font-bold uppercase tracking-wider text-slate-400 mr-1">Filtrer par tag</span>
      <button
        type="button"
        class="rounded-xl px-3 py-1.5 text-xs font-bold transition-all active:scale-95"
        :class="selectedTagId === null ? 'bg-indigo-600 text-white' : 'bg-slate-50 text-slate-500 dark:bg-slate-800 dark:text-slate-350 hover:bg-slate-100 dark:hover:bg-slate-700'"
        @click="filterByTag(null)"
      >
        Tous
      </button>
      <button
        v-for="tag in tagsStore.tags"
        :key="tag.id"
        type="button"
        class="rounded-xl px-3 py-1.5 text-xs font-bold transition-all active:scale-95"
        :style="selectedTagId === tag.id ? { backgroundColor: tag.color || '#4F46E5', color: '#fff' } : undefined"
        :class="selectedTagId === tag.id ? '' : 'bg-slate-50 text-slate-500 dark:bg-slate-800 dark:text-slate-350 hover:bg-slate-100 dark:hover:bg-slate-700'"
        @click="filterByTag(tag.id)"
      >
        {{ tag.name }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="notesStore.loading" class="flex flex-col items-center justify-center py-20 gap-3">
      <svg class="animate-spin h-8 w-8 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="text-sm font-semibold text-slate-400 uppercase tracking-widest">Chargement de vos notes...</span>
    </div>

    <!-- Notes List -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="note in filteredNotes" 
        :key="note.id"
        class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm flex flex-col justify-between hover:shadow-md transition-all duration-200 group cursor-pointer"
        @click="router.push(`/notes/${note.id}?edit=false`)"
      >
        <div>
          <div class="flex items-start justify-between gap-3">
            <!-- Binder Badge if available -->
            <span 
              class="inline-flex items-center px-2.5 py-0.5 rounded-lg text-[10px] font-bold uppercase tracking-wider"
              :class="getBinderBadgeClass(note.binder_id)"
            >
              {{ getBinderName(note.binder_id) }}
            </span>

            <button 
              @click.stop="confirmDelete(note)" 
              class="opacity-0 group-hover:opacity-100 p-1.5 text-slate-400 hover:text-rose-500 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-all"
              title="Supprimer la note"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>

          <h3 class="font-bold text-lg text-slate-800 dark:text-white mt-4 line-clamp-1">{{ note.title || 'Note sans titre' }}</h3>
          <!-- Tags list -->
          <div v-if="note.tags?.length" class="mt-2 flex flex-wrap gap-1">
            <TagBadge v-for="tag in note.tags" :key="tag.id" :tag="tag" />
          </div>
          <!-- Strip HTML tags to show clean preview -->
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-2 line-clamp-3 leading-relaxed">
            {{ stripHtml(note.content) || 'Aucun contenu...' }}
          </p>
        </div>

        <div class="flex items-center justify-between mt-6 pt-4 border-t border-slate-50 dark:border-slate-800/50">
          <span class="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Créé le {{ new Date(note.created_at).toLocaleDateString('fr-FR') }}</span>
          
          <div class="flex items-center gap-2">
            <button 
              @click.stop="router.push(`/notes/${note.id}?edit=false`)"
              class="px-2.5 py-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-150/40 dark:bg-slate-800/40 dark:hover:bg-slate-800 dark:border-slate-700/50 text-slate-650 dark:text-slate-300 rounded-xl text-xs font-bold transition-all flex items-center gap-1 active:scale-95"
              title="Visualiser la note"
            >
              <Eye class="w-3.5 h-3.5 text-indigo-500" />
              Visualiser
            </button>
            <button 
              @click.stop="router.push(`/notes/${note.id}?edit=true`)"
              class="px-2.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-1 active:scale-95 shadow-md shadow-indigo-600/10"
              title="Éditer la note"
            >
              <Edit3 class="w-3.5 h-3.5" />
              Éditer
            </button>
          </div>
        </div>
      </div>

      <div 
        v-if="filteredNotes.length === 0" 
        class="col-span-full border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-3xl p-12 flex flex-col items-center justify-center text-center text-slate-400"
      >
        <FileText class="w-12 h-12 text-slate-300 dark:text-slate-700 mb-3" />
        <h4 class="font-bold text-slate-800 dark:text-slate-200">Aucune note trouvée</h4>
        <p class="text-xs mt-1">Modifiez vos filtres ou créez une nouvelle note !</p>
        <button 
          @click="createNewNote"
          class="mt-4 px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl transition-all"
        >
          Créer une note
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotesStore } from '../../stores/notes'
import type { Note } from '../../stores/notes'
import { useBindersStore } from '../../stores/binders'
import { useTagsStore } from '../../stores/tags'
import TagBadge from '../../components/ui/TagBadge.vue'
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
    // Filter by search
    const matchesSearch = note.title.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          note.content.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    // Filter by binder
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
    return 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400'
  }
  // Alternate styles based on ID hash/length
  const styles = [
    'bg-indigo-50 text-indigo-600 dark:bg-indigo-950/40 dark:text-indigo-400',
    'bg-emerald-50 text-emerald-600 dark:bg-emerald-950/40 dark:text-emerald-400',
    'bg-purple-50 text-purple-600 dark:bg-purple-950/40 dark:text-purple-400',
    'bg-amber-50 text-amber-600 dark:bg-amber-950/40 dark:text-amber-400'
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

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
