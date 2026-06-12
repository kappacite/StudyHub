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

      <!-- Action Buttons -->
      <div class="flex items-center gap-3">
        <template v-if="isOwner">
          <button 
            v-if="currentBinderId !== null"
            @click="openShareModal"
            class="inline-flex items-center gap-2 px-4 py-2 border rounded-xl text-sm font-semibold transition-all active:scale-95"
            :class="[
              currentBinder?.is_public 
                ? 'border-emerald-500 bg-emerald-50 text-emerald-600 dark:border-emerald-600 dark:bg-emerald-950/20 dark:text-emerald-400' 
                : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-850 text-slate-600 dark:text-slate-350'
            ]"
          >
            <Globe class="w-4 h-4" />
            {{ currentBinder?.is_public ? 'Public' : 'Partager' }}
          </button>

          <button 
            @click="openCreateModal"
            class="inline-flex items-center gap-2 px-4 py-2 border border-transparent rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition-all shadow-lg shadow-indigo-600/15"
          >
            <Plus class="w-4 h-4" />
            Nouveau dossier
          </button>
        </template>
        <template v-else>
          <button 
            @click="cloneBinder"
            :disabled="cloning"
            class="inline-flex items-center gap-2 px-4 py-2 border border-transparent rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition-all shadow-lg shadow-indigo-600/15 disabled:opacity-50"
          >
            <Loader2 v-if="cloning" class="w-4 h-4 animate-spin" />
            <Copy v-else class="w-4 h-4" />
            {{ cloning ? 'Copie en cours...' : 'Créer une copie personnelle' }}
          </button>
        </template>
      </div>
    </div>

    <div class="flex flex-wrap items-center gap-2 rounded-2xl border border-slate-100 bg-white p-3 dark:border-slate-800 dark:bg-slate-900">
      <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Filtrer</span>
      <button
        type="button"
        class="rounded-xl px-3 py-1.5 text-xs font-bold"
        :class="selectedTagId === null ? 'bg-indigo-600 text-white' : 'bg-slate-50 text-slate-500 dark:bg-slate-800 dark:text-slate-300'"
        @click="filterByTag(null)"
      >
        Tous
      </button>
      <button
        v-for="tag in tagsStore.tags"
        :key="tag.id"
        type="button"
        class="rounded-xl px-3 py-1.5 text-xs font-bold"
        :style="selectedTagId === tag.id ? { backgroundColor: tag.color || '#4F46E5', color: '#fff' } : undefined"
        :class="selectedTagId === tag.id ? '' : 'bg-slate-50 text-slate-500 dark:bg-slate-800 dark:text-slate-300'"
        @click="filterByTag(tag.id)"
      >
        {{ tag.name }}
      </button>
    </div>

    <!-- Read only / Follow class warning banner -->
    <div v-if="!isOwner" class="p-4 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900/30 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-amber-850 dark:text-amber-300">
      <div class="flex items-center gap-2">
        <Eye class="w-5 h-5 text-amber-500 flex-shrink-0" />
        <span class="text-xs font-semibold">Vous visualisez ce dossier en lecture seule (cours suivi). Pour le modifier, veuillez créer une copie personnelle.</span>
      </div>
      <button 
        @click="cloneBinder"
        :disabled="cloning"
        class="px-3.5 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-xl text-xs font-bold transition-all active:scale-95 disabled:opacity-50 flex items-center gap-1.5"
      >
        <Loader2 v-if="cloning" class="w-3.5 h-3.5 animate-spin" />
        <Copy v-else class="w-3.5 h-3.5" />
        Créer une copie
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
              <div class="min-w-0">
                <span class="font-bold truncate text-sm text-slate-800 dark:text-slate-200">{{ folder.name }}</span>
                <div v-if="folder.tags?.length" class="mt-1 flex flex-wrap gap-1">
                  <TagBadge v-for="tag in folder.tags" :key="tag.id" :tag="tag" />
                </div>
              </div>
            </div>
            
            <button 
              v-if="isOwner"
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
            <div>
              <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Tags</label>
              <TagSelector v-model="folderTags" />
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

    <!-- Share Folder Modal -->
    <div 
      v-if="showShareModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4"
    >
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-slate-950/40 backdrop-blur-sm" @click="showShareModal = false"></div>
      
      <!-- Modal box -->
      <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl w-full max-w-md p-6 relative z-10 shadow-2xl animate-scale-up">
        <h3 class="text-lg font-bold mb-2">Partager sur l'Espace Communautaire</h3>
        <p class="text-xs text-slate-450 dark:text-slate-500 mb-4">
          Publiez ce classeur et toutes les ressources qu'il contient (notes, flashcards...) pour les rendre accessibles à la communauté.
        </p>
        
        <form @submit.prevent="saveShareSettings">
          <div class="space-y-4">
            <!-- Toggle Visibilité -->
            <div class="flex items-center justify-between p-3.5 bg-slate-50 dark:bg-slate-800/30 border border-slate-100 dark:border-slate-800 rounded-2xl">
              <div>
                <label class="block text-xs font-bold text-slate-800 dark:text-slate-200">Statut de visibilité</label>
                <span class="text-[10px] text-slate-450">{{ shareIsPublic ? 'Visible sur la Marketplace' : 'Visible uniquement par vous' }}</span>
              </div>
              <button 
                type="button" 
                @click="shareIsPublic = !shareIsPublic"
                class="px-3 py-1.5 border rounded-xl text-xs font-bold transition-all active:scale-95"
                :class="[
                  shareIsPublic 
                    ? 'border-emerald-500 bg-emerald-50 text-emerald-600 dark:border-emerald-600 dark:bg-emerald-950/20 dark:text-emerald-400' 
                    : 'border-slate-200 dark:border-slate-800 text-slate-500'
                ]"
              >
                {{ shareIsPublic ? 'Public' : 'Privé' }}
              </button>
            </div>

            <!-- Description -->
            <div>
              <label for="share-description" class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Description</label>
              <textarea 
                id="share-description" 
                v-model="shareDescription"
                placeholder="Décrivez le contenu de ce dossier..."
                rows="3"
                class="block w-full px-4 py-3 bg-slate-50 border border-slate-200 dark:bg-slate-800/40 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-medium"
              ></textarea>
            </div>

            <!-- Tags -->
            <div>
              <label for="share-tags" class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Mots-clés (tags, séparés par virgules)</label>
              <input 
                id="share-tags" 
                type="text" 
                v-model="shareTags"
                placeholder="Ex: Chimie, Médecine, Semestre 1"
                class="block w-full px-4 py-3 bg-slate-50 border border-slate-200 dark:bg-slate-800/40 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-medium"
              />
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 mt-6">
            <button 
              type="button" 
              @click="showShareModal = false"
              class="px-4 py-2 text-sm font-semibold rounded-xl text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800"
            >
              Annuler
            </button>
            <button 
              type="submit"
              class="px-4 py-2 text-sm font-semibold rounded-xl text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition-all"
            >
              Enregistrer
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
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
import { FolderClosed, Plus, ChevronRight, FileText, Layers, Trash2, Globe, Copy, Eye, Loader2 } from 'lucide-vue-next'

const bindersStore = useBindersStore()
const notesStore = useNotesStore()
const decksStore = useDecksStore()
const tagsStore = useTagsStore()
const router = useRouter()
const route = useRoute()

const currentBinderId = ref<string | null>(null)

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

// Refs pour le partage du classeur
const showShareModal = ref(false)
const shareIsPublic = ref(false)
const shareDescription = ref('')
const shareTags = ref('')

onMounted(async () => {
  await Promise.all([
    bindersStore.fetchBinders(),
    notesStore.fetchNotes(),
    decksStore.fetchDecks(),
    tagsStore.fetchTags()
  ])
})

async function filterByTag(tagId: number | null) {
  selectedTagId.value = tagId
  await bindersStore.fetchBinders(tagId)
}

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
    router.push(`/binders/${cloned.id}`)
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
  const tagsArray = shareTags.value.split(',')
    .map(t => t.trim())
    .filter(t => t.length > 0)
  
  await bindersStore.updateBinder(currentBinder.value.id, {
    is_public: shareIsPublic.value,
    description: shareDescription.value.trim() || null,
    tags: tagsArray.length > 0 ? tagsArray : null
  })
  
  showShareModal.value = false
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
