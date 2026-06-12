<template>
  <Transition name="fade-backdrop">
    <div 
      v-if="isOpen" 
      class="fixed inset-0 z-[100] flex items-start justify-center bg-slate-900/60 backdrop-blur-sm p-4 md:p-10 no-print"
      @click.self="close"
    >
      <Transition name="scale-up">
        <div 
          v-if="isOpen"
          class="w-full max-w-3xl bg-white dark:bg-[#111827] rounded-2xl shadow-2xl border border-slate-100 dark:border-slate-800 flex flex-col overflow-hidden max-h-[85vh] mt-10 md:mt-16"
          @click.stop
        >
          <!-- Search Header Input -->
          <div class="flex items-center gap-3 px-4 py-3 border-b border-slate-100 dark:border-slate-800">
            <Search class="w-5 h-5 text-indigo-500 flex-shrink-0 animate-pulse" />
            <input
              ref="searchInput"
              v-model="query"
              type="text"
              placeholder="Rechercher des notes, decks, cartes, diagrammes..."
              class="flex-1 min-w-0 bg-transparent outline-none border-none py-1 text-base font-semibold text-slate-800 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500"
              @keydown.down.prevent="moveDown"
              @keydown.up.prevent="moveUp"
              @keydown.enter.prevent="selectCurrent"
              @keydown.esc="close"
            />
            <button 
              @click="close" 
              class="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
            >
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- Search Results Area -->
          <div class="flex-1 overflow-y-auto p-4 space-y-6">
            <!-- Loading State -->
            <div v-if="isLoading" class="flex flex-col items-center justify-center py-12 text-slate-400">
              <Loader2 class="w-8 h-8 text-indigo-500 animate-spin mb-3" />
              <span class="text-sm font-semibold">Recherche en cours...</span>
            </div>

            <!-- Error State -->
            <div v-else-if="error" class="p-4 bg-rose-50 dark:bg-rose-950/20 text-rose-600 dark:text-rose-400 rounded-xl text-sm font-semibold border border-rose-100 dark:border-rose-950/50">
              {{ error }}
            </div>

            <!-- Empty / Query Too Short Info State -->
            <div v-else-if="query.trim().length < 2" class="flex flex-col items-center justify-center py-12 text-slate-400 dark:text-slate-500">
              <Search class="w-12 h-12 text-slate-300 dark:text-slate-700 mb-3" />
              <p class="text-sm font-semibold text-center">Entrez au moins 2 caractères pour rechercher</p>
              <p class="text-xs mt-1 text-center">Recherche rapide dans le contenu de tous vos modules.</p>
            </div>

            <!-- No Results Found State -->
            <div v-else-if="total === 0" class="flex flex-col items-center justify-center py-12 text-slate-400 dark:text-slate-500">
              <Search class="w-12 h-12 text-slate-300 dark:text-slate-700 mb-3" />
              <p class="text-sm font-semibold text-center">Aucun résultat trouvé pour "{{ query }}"</p>
              <p class="text-xs mt-1 text-center">Essayez d'autres mots clés ou vérifiez l'orthographe.</p>
            </div>

            <!-- Results List Grouped -->
            <div v-else class="space-y-6">
              <!-- Notes Section -->
              <div v-if="results.notes.length > 0">
                <h3 class="flex items-center gap-1.5 text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-3">
                  <FileText class="w-3.5 h-3.5" />
                  Notes ({{ results.notes.length }})
                </h3>
                <div class="space-y-1">
                  <div 
                    v-for="(note, i) in results.notes" 
                    :key="note.id"
                    :class="[
                      'p-3 rounded-xl cursor-pointer transition-all border border-transparent flex flex-col',
                      getAbsoluteIndex('notes', i) === selectedIndex 
                        ? 'bg-indigo-50/70 border-indigo-100 text-indigo-900 dark:bg-indigo-950/40 dark:border-indigo-900/60 dark:text-indigo-200' 
                        : 'hover:bg-slate-50 dark:hover:bg-slate-800/30'
                    ]"
                    @click="navigateTo(note, 'note')"
                    @mouseenter="selectedIndex = getAbsoluteIndex('notes', i)"
                  >
                    <div class="flex items-center justify-between gap-4">
                      <span class="font-bold text-sm text-slate-800 dark:text-slate-200">{{ note.title }}</span>
                      <div class="flex flex-wrap gap-1">
                        <TagBadge 
                          v-for="tag in note.tags" 
                          :key="tag.id" 
                          :tag="(tag as any)" 
                          class="scale-90 transform origin-right"
                        />
                      </div>
                    </div>
                    <p 
                      class="text-xs mt-1.5 text-slate-500 dark:text-slate-400 line-clamp-2 search-excerpt"
                      v-dompurify-html="note.excerpt"
                    ></p>
                  </div>
                </div>
              </div>

              <!-- Decks Section -->
              <div v-if="results.decks.length > 0">
                <h3 class="flex items-center gap-1.5 text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-3">
                  <Layers class="w-3.5 h-3.5" />
                  Decks ({{ results.decks.length }})
                </h3>
                <div class="space-y-1">
                  <div 
                    v-for="(deck, i) in results.decks" 
                    :key="deck.id"
                    :class="[
                      'p-3 rounded-xl cursor-pointer transition-all border border-transparent flex flex-col',
                      getAbsoluteIndex('decks', i) === selectedIndex 
                        ? 'bg-indigo-50/70 border-indigo-100 text-indigo-900 dark:bg-indigo-950/40 dark:border-indigo-900/60 dark:text-indigo-200' 
                        : 'hover:bg-slate-50 dark:hover:bg-slate-800/30'
                    ]"
                    @click="navigateTo(deck, 'deck')"
                    @mouseenter="selectedIndex = getAbsoluteIndex('decks', i)"
                  >
                    <div class="flex items-center justify-between gap-4">
                      <span class="font-bold text-sm text-slate-800 dark:text-slate-200">{{ deck.name }}</span>
                      <div class="flex flex-wrap gap-1">
                        <TagBadge 
                          v-for="tag in deck.tags" 
                          :key="tag.id" 
                          :tag="(tag as any)" 
                          class="scale-90 transform origin-right"
                        />
                      </div>
                    </div>
                    <p 
                      v-if="deck.excerpt" 
                      class="text-xs mt-1.5 text-slate-500 dark:text-slate-400 line-clamp-2 search-excerpt"
                      v-dompurify-html="deck.excerpt"
                    ></p>
                  </div>
                </div>
              </div>

              <!-- Flashcards Section -->
              <div v-if="results.flashcards.length > 0">
                <h3 class="flex items-center gap-1.5 text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-3">
                  <Brain class="w-3.5 h-3.5" />
                  Flashcards ({{ results.flashcards.length }})
                </h3>
                <div class="space-y-1">
                  <div 
                    v-for="(card, i) in results.flashcards" 
                    :key="card.id"
                    :class="[
                      'p-3 rounded-xl cursor-pointer transition-all border border-transparent flex justify-between items-center gap-4',
                      getAbsoluteIndex('flashcards', i) === selectedIndex 
                        ? 'bg-indigo-50/70 border-indigo-100 text-indigo-900 dark:bg-indigo-950/40 dark:border-indigo-900/60 dark:text-indigo-200' 
                        : 'hover:bg-slate-50 dark:hover:bg-slate-800/30'
                    ]"
                    @click="navigateTo(card, 'flashcard')"
                    @mouseenter="selectedIndex = getAbsoluteIndex('flashcards', i)"
                  >
                    <div class="flex flex-col min-w-0">
                      <span class="font-semibold text-sm text-slate-800 dark:text-slate-200 truncate">{{ card.front }}</span>
                      <span class="text-[10px] font-bold text-indigo-500 dark:text-indigo-400 mt-0.5 uppercase tracking-wide">
                        {{ card.deck_name }}
                      </span>
                    </div>
                    <ChevronRight class="w-4 h-4 text-slate-400 flex-shrink-0" />
                  </div>
                </div>
              </div>

              <!-- Diagrams Section -->
              <div v-if="results.diagrams.length > 0">
                <h3 class="flex items-center gap-1.5 text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-3">
                  <Activity class="w-3.5 h-3.5" />
                  Diagrammes ({{ results.diagrams.length }})
                </h3>
                <div class="space-y-1">
                  <div 
                    v-for="(diag, i) in results.diagrams" 
                    :key="diag.id"
                    :class="[
                      'p-3 rounded-xl cursor-pointer transition-all border border-transparent flex justify-between items-center gap-4',
                      getAbsoluteIndex('diagrams', i) === selectedIndex 
                        ? 'bg-indigo-50/70 border-indigo-100 text-indigo-900 dark:bg-indigo-950/40 dark:border-indigo-900/60 dark:text-indigo-200' 
                        : 'hover:bg-slate-50 dark:hover:bg-slate-800/30'
                    ]"
                    @click="navigateTo(diag, 'diagram')"
                    @mouseenter="selectedIndex = getAbsoluteIndex('diagrams', i)"
                  >
                    <span class="font-semibold text-sm text-slate-800 dark:text-slate-200">{{ diag.title }}</span>
                    <ChevronRight class="w-4 h-4 text-slate-400 flex-shrink-0" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer Shortcut info -->
          <div class="px-4 py-3 bg-slate-50 dark:bg-slate-900/50 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-400 dark:text-slate-500 font-medium no-print">
            <div class="flex items-center gap-3">
              <span class="flex items-center gap-1">
                <kbd class="px-1.5 py-0.5 bg-slate-200/60 dark:bg-slate-800 rounded font-bold">↵</kbd> Ouvrir
              </span>
              <span class="flex items-center gap-1">
                <kbd class="px-1.5 py-0.5 bg-slate-200/60 dark:bg-slate-800 rounded font-bold">↑↓</kbd> Naviguer
              </span>
              <span class="flex items-center gap-1">
                <kbd class="px-1.5 py-0.5 bg-slate-200/60 dark:bg-slate-800 rounded font-bold">Echap</kbd> Fermer
              </span>
            </div>
            <div v-if="total > 0">
              {{ total }} {{ total > 1 ? 'résultats' : 'résultat' }}
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Search, 
  X, 
  Loader2, 
  FileText, 
  Layers, 
  Brain, 
  Activity, 
  ChevronRight 
} from '@lucide/vue'
import { useSearch } from '../../composables/useSearch'
import TagBadge from './TagBadge.vue'

const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const router = useRouter()
const searchInput = ref<HTMLInputElement | null>(null)
const selectedIndex = ref(0)

const { query, isLoading, results, total, error } = useSearch()

// Calculate continuous index across groups
const getAbsoluteIndex = (type: 'notes' | 'decks' | 'flashcards' | 'diagrams', relativeIndex: number): number => {
  let offset = 0
  if (type === 'notes') return relativeIndex
  offset += results.value.notes.length
  
  if (type === 'decks') return offset + relativeIndex
  offset += results.value.decks.length
  
  if (type === 'flashcards') return offset + relativeIndex
  offset += results.value.flashcards.length
  
  if (type === 'diagrams') return offset + relativeIndex
  return -1
}

// Flat list computed helper for selection logic
const flatList = computed(() => {
  const items: Array<{ id: number | string; type: string; route: string; item: any }> = []
  
  results.value.notes.forEach(note => {
    items.push({ id: note.id, type: 'note', route: `/notes/${note.id}`, item: note })
  })
  
  results.value.decks.forEach(deck => {
    items.push({ id: deck.id, type: 'deck', route: `/decks?id=${deck.id}`, item: deck })
  })
  
  results.value.flashcards.forEach(card => {
    items.push({ id: card.id, type: 'flashcard', route: `/decks/${card.deck_id}/study`, item: card })
  })
  
  results.value.diagrams.forEach(diag => {
    items.push({ id: diag.id, type: 'diagram', route: `/diagrams?id=${diag.id}`, item: diag })
  })
  
  return items
})

// Auto-focus input when modal opens
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    query.value = ''
    selectedIndex.value = 0
    nextTick(() => {
      searchInput.value?.focus()
    })
  }
})

// Reset index on new search results
watch(total, () => {
  selectedIndex.value = 0
})

function close() {
  emit('close')
}

function moveDown() {
  if (flatList.value.length === 0) return
  selectedIndex.value = (selectedIndex.value + 1) % flatList.value.length
}

function moveUp() {
  if (flatList.value.length === 0) return
  selectedIndex.value = (selectedIndex.value - 1 + flatList.value.length) % flatList.value.length
}

function selectCurrent() {
  if (flatList.value.length === 0 || selectedIndex.value < 0 || selectedIndex.value >= flatList.value.length) return
  const current = flatList.value[selectedIndex.value]
  router.push(current.route)
  close()
}

function navigateTo(item: any, type: string) {
  let route = ''
  if (type === 'note') route = `/notes/${item.id}`
  else if (type === 'deck') route = `/decks?id=${item.id}`
  else if (type === 'flashcard') route = `/decks/${item.deck_id}/study`
  else if (type === 'diagram') route = `/diagrams?id=${item.id}`
  
  if (route) {
    router.push(route)
    close()
  }
}
</script>

<style scoped>
/* Fade Backdrop Animation */
.fade-backdrop-enter-active,
.fade-backdrop-leave-active {
  transition: opacity 0.25s ease;
}
.fade-backdrop-enter-from,
.fade-backdrop-leave-to {
  opacity: 0;
}

/* Scale Up Modal Animation */
.scale-up-enter-active,
.scale-up-leave-active {
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.2s ease;
}
.scale-up-enter-from,
.scale-up-leave-to {
  transform: scale(0.95);
  opacity: 0;
}

/* Customize excerpt <mark> tags inside search results */
:deep(.search-excerpt mark) {
  background-color: rgba(99, 102, 241, 0.25);
  color: rgb(79, 70, 229);
  font-weight: 700;
  border-radius: 4px;
  padding: 0 2px;
}
.dark :deep(.search-excerpt mark) {
  background-color: rgba(129, 140, 248, 0.3);
  color: rgb(165, 180, 252);
}
</style>
