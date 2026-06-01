<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header with Breadcrumbs and actions -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <!-- Breadcrumb navigation -->
      <div class="flex items-center gap-1.5 text-sm font-semibold">
        <button 
          @click="currentBinderId = null" 
          class="text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400 flex items-center gap-1"
        >
          <FolderClosed class="w-4 h-4" />
          Racine
        </button>
        
        <template v-for="(crumb, idx) in breadcrumbs" :key="crumb.id">
          <ChevronRight class="w-4 h-4 text-slate-400" />
          <button 
            @click="currentBinderId = crumb.id" 
            class="text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400"
            :class="[idx === breadcrumbs.length - 1 ? 'text-slate-800 dark:text-white font-bold pointer-events-none' : '']"
          >
            {{ crumb.name }}
          </button>
        </template>
      </div>

      <!-- Action Button -->
      <button 
        @click="openCreateModal"
        class="inline-flex items-center gap-2 px-4 py-2 border border-transparent rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition-all shadow-lg shadow-indigo-600/15"
      >
        <Plus class="w-4 h-4" />
        Nouveau dossier
      </button>
    </div>

    <!-- Loading state -->
    <div v-if="bindersStore.loading" class="flex flex-col items-center justify-center py-20 gap-3">
      <svg class="animate-spin h-8 w-8 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="text-sm font-semibold text-slate-400 uppercase tracking-widest">Chargement...</span>
    </div>

    <div v-else class="space-y-8">
      <!-- Direct Subfolders Section -->
      <div>
        <h3 class="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-4">Dossiers ({{ currentSubBinders.length }})</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <div 
            v-for="folder in currentSubBinders" 
            :key="folder.id"
            class="flex items-center justify-between p-4 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl hover:border-indigo-500/30 dark:hover:border-indigo-500/30 shadow-sm transition-all duration-200 group cursor-pointer"
            @click="currentBinderId = folder.id"
          >
            <div class="flex items-center gap-3 min-w-0">
              <div class="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-950/30 text-indigo-600 dark:text-indigo-400 flex items-center justify-center group-hover:scale-105 transition-transform">
                <FolderClosed class="w-5 h-5 fill-indigo-100 dark:fill-indigo-950/20" />
              </div>
              <span class="font-bold truncate text-sm text-slate-800 dark:text-slate-200">{{ folder.name }}</span>
            </div>
            
            <button 
              @click.stop="confirmDelete(folder)" 
              class="opacity-0 group-hover:opacity-100 p-1.5 text-slate-400 hover:text-rose-500 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-all"
              title="Supprimer"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>

          <div 
            v-if="currentSubBinders.length === 0" 
            class="col-span-full border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-2xl p-8 flex flex-col items-center justify-center text-center text-slate-400"
          >
            <FolderClosed class="w-8 h-8 text-slate-300 dark:text-slate-700 mb-2" />
            <p class="text-xs font-semibold uppercase tracking-wider">Aucun sous-dossier</p>
          </div>
        </div>
      </div>

      <!-- Associated Contents Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Associated Notes -->
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm">
          <h3 class="font-bold text-sm text-slate-800 dark:text-white flex items-center gap-2 mb-4">
            <FileText class="w-4 h-4 text-indigo-500" />
            Notes associées ({{ currentNotes.length }})
          </h3>
          
          <div class="space-y-3">
            <div 
              v-for="note in currentNotes" 
              :key="note.id"
              class="flex items-center justify-between p-3.5 bg-slate-50 dark:bg-slate-800/30 border border-slate-100 dark:border-slate-800 rounded-2xl hover:border-slate-200 transition-colors cursor-pointer group"
              @click="router.push(`/notes/${note.id}`)"
            >
              <div class="min-w-0">
                <p class="text-sm font-bold truncate text-slate-800 dark:text-slate-200">{{ note.title }}</p>
                <p class="text-[10px] text-slate-400 mt-0.5">Mis à jour il y a 2h</p>
              </div>
              <ChevronRight class="w-4 h-4 text-slate-400 group-hover:translate-x-1 transition-transform" />
            </div>

            <div 
              v-if="currentNotes.length === 0" 
              class="text-center py-8 text-slate-400 text-xs font-semibold uppercase tracking-wider"
            >
              Aucune note dans ce dossier
            </div>
          </div>
        </div>

        <!-- Associated Decks -->
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm">
          <h3 class="font-bold text-sm text-slate-800 dark:text-white flex items-center gap-2 mb-4">
            <Layers class="w-4 h-4 text-indigo-500" />
            Flashcards associées ({{ currentDecks.length }})
          </h3>
          
          <div class="space-y-3">
            <div 
              v-for="deck in currentDecks" 
              :key="deck.id"
              class="flex items-center justify-between p-3.5 bg-slate-50 dark:bg-slate-800/30 border border-slate-100 dark:border-slate-800 rounded-2xl hover:border-slate-200 transition-colors cursor-pointer group"
              @click="router.push(`/decks`)"
            >
              <div class="min-w-0">
                <p class="text-sm font-bold truncate text-slate-800 dark:text-slate-200">{{ deck.name }}</p>
                <p class="text-[10px] text-indigo-500 dark:text-indigo-400 font-semibold uppercase tracking-wider mt-0.5">
                  {{ deck.card_count }} cartes
                </p>
              </div>
              <ChevronRight class="w-4 h-4 text-slate-400 group-hover:translate-x-1 transition-transform" />
            </div>

            <div 
              v-if="currentDecks.length === 0" 
              class="text-center py-8 text-slate-400 text-xs font-semibold uppercase tracking-wider"
            >
              Aucun deck dans ce dossier
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Folder Modal -->
    <div 
      v-if="showModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4"
    >
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-slate-950/40 backdrop-blur-sm" @click="showModal = false"></div>
      
      <!-- Modal box -->
      <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl w-full max-w-md p-6 relative z-10 shadow-2xl animate-scale-up">
        <h3 class="text-lg font-bold mb-4">Créer un nouveau dossier</h3>
        
        <form @submit.prevent="createFolder">
          <div class="space-y-4">
            <div>
              <label for="folder-name" class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Nom du dossier</label>
              <input 
                id="folder-name" 
                type="text" 
                required 
                v-model="newFolderName"
                placeholder="Ex: Anatomie, Semestre 2..."
                class="block w-full px-4 py-3 bg-slate-50 border border-slate-200 dark:bg-slate-800/40 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-medium"
              />
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 mt-6">
            <button 
              type="button" 
              @click="showModal = false"
              class="px-4 py-2 text-sm font-semibold rounded-xl text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800"
            >
              Annuler
            </button>
            <button 
              type="submit"
              class="px-4 py-2 text-sm font-semibold rounded-xl text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Créer
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBindersStore } from '../../stores/binders'
import type { Binder } from '../../stores/binders'
import { useNotesStore } from '../../stores/notes'
import { useDecksStore } from '../../stores/decks'
import { FolderClosed, Plus, ChevronRight, FileText, Layers, Trash2 } from '@lucide/vue'

const bindersStore = useBindersStore()
const notesStore = useNotesStore()
const decksStore = useDecksStore()
const router = useRouter()

const currentBinderId = ref<number | null>(null)
const showModal = ref(false)
const newFolderName = ref('')

onMounted(async () => {
  await bindersStore.fetchBinders()
  await notesStore.fetchNotes()
  await decksStore.fetchDecks()
})

// Subfolders of the current binder
const currentSubBinders = computed(() => {
  return bindersStore.binders.filter(b => b.parent_id === currentBinderId.value)
})

// Notes belonging to the current binder
const currentNotes = computed(() => {
  return notesStore.notes.filter(n => n.binder_id === currentBinderId.value)
})

// Decks belonging to the current binder
const currentDecks = computed(() => {
  return decksStore.decks.filter(d => d.binder_id === currentBinderId.value)
})

// Breadcrumbs trace path from root
const breadcrumbs = computed(() => {
  if (currentBinderId.value === null) return []
  
  const trail: Binder[] = []
  let current = bindersStore.binders.find(b => b.id === currentBinderId.value)
  
  while (current) {
    trail.unshift(current)
    const parentId = current.parent_id
    current = parentId !== null ? bindersStore.binders.find(b => b.id === parentId) : undefined
  }
  
  return trail
})

function openCreateModal() {
  newFolderName.value = ''
  showModal.value = true
}

async function createFolder() {
  if (newFolderName.value.trim()) {
    await bindersStore.createBinder(newFolderName.value.trim(), currentBinderId.value)
    showModal.value = false
  }
}

async function confirmDelete(folder: Binder) {
  if (confirm(`Êtes-vous sûr de vouloir supprimer le dossier "${folder.name}" et tous ses sous-dossiers ?`)) {
    await bindersStore.deleteBinder(folder.id)
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

@keyframes scaleUp {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.animate-scale-up {
  animation: scaleUp 0.15s ease-out forwards;
}
</style>
