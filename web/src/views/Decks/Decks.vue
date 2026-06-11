<template>
  <div class="space-y-6 animate-fade-in">
    <!-- View 1: Decks List (Main View) -->
    <template v-if="!selectedDeck">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-xl font-bold">Mes Decks de Flashcards</h1>
          <p class="text-xs text-slate-400 dark:text-slate-500 mt-1">Créez et révisez vos cartes mémoire avec l'algorithme de répétition espacée SM-2</p>
        </div>
        
        <div class="flex items-center gap-3">
          <button 
            @click="showAnkiModal = true"
            class="inline-flex items-center gap-2 px-4 py-2 border border-slate-200 dark:border-slate-800 rounded-xl text-sm font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 active:scale-95 transition-all cursor-pointer"
          >
            <Upload class="w-4 h-4 text-indigo-500" />
            Importer Anki
          </button>

          <button 
            @click="openCreateDeckModal"
            class="inline-flex items-center gap-2 px-4 py-2 border border-transparent rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition-all shadow-lg shadow-indigo-600/15 cursor-pointer"
          >
            <Plus class="w-4 h-4" />
            Nouveau Deck
          </button>
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

      <!-- Decks Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="deck in decksStore.decks" 
          :key="deck.id"
          class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm flex flex-col justify-between hover:shadow-md transition-all duration-200 group"
        >
          <div>
            <div class="flex items-start justify-between gap-3">
              <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold text-indigo-500 bg-indigo-50 dark:bg-indigo-950/40 dark:text-indigo-400 uppercase tracking-wider">
                {{ deck.card_count }} cartes
              </span>
              
              <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button 
                  @click.stop="openEditDeckModal(deck)" 
                  class="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800"
                  title="Modifier"
                >
                  <Edit class="w-4 h-4" />
                </button>
                <button 
                  @click.stop="deleteDeck(deck)" 
                  class="p-1 text-slate-400 hover:text-rose-500 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/30"
                  title="Supprimer"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>

            <h3 class="font-bold text-lg text-slate-800 dark:text-white mt-4">{{ deck.name }}</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-2 line-clamp-2">{{ deck.description || 'Aucune description' }}</p>
            <div v-if="deck.tags?.length" class="mt-3 flex flex-wrap gap-1.5">
              <TagBadge v-for="tag in deck.tags" :key="tag.id" :tag="tag" />
            </div>
          </div>

          <div class="flex items-center gap-3 mt-6 pt-4 border-t border-slate-50 dark:border-slate-800/50">
            <!-- Study button -->
            <button 
              @click="router.push(`/decks/${deck.id}/study`)"
              class="flex-1 px-4 py-2 border border-transparent rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition-all text-center"
            >
              Étudier
            </button>
            <!-- View cards button -->
            <button 
              @click="selectDeck(deck)"
              class="flex-1 px-4 py-2 border border-slate-200 dark:border-slate-800 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-slate-800 active:scale-95 transition-all"
            >
              Gérer cartes
            </button>
          </div>
        </div>

        <div 
          v-if="decksStore.decks.length === 0" 
          class="col-span-full border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-3xl p-12 flex flex-col items-center justify-center text-center text-slate-400"
        >
          <Layers class="w-12 h-12 text-slate-300 dark:text-slate-700 mb-3" />
          <h4 class="font-bold text-slate-800 dark:text-slate-200">Aucun deck disponible</h4>
          <p class="text-xs mt-1">Commencez par créer votre premier deck pour étudier !</p>
          <button 
            @click="openCreateDeckModal"
            class="mt-4 px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl transition-all"
          >
            Créer un Deck
          </button>
        </div>
      </div>
    </template>

    <!-- View 2: Cards Detail View (Manage Cards inside selected Deck) -->
    <template v-else>
      <div class="flex items-center gap-2 text-sm font-semibold">
        <button 
          @click="selectedDeck = null" 
          class="text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400"
        >
          Decks
        </button>
        <ChevronRight class="w-4 h-4 text-slate-400" />
        <span class="text-slate-800 dark:text-white font-bold">{{ selectedDeck.name }}</span>
      </div>

      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm">
        <div>
          <h2 class="text-lg font-bold">{{ selectedDeck.name }}</h2>
          <p class="text-xs text-slate-500 mt-1">{{ selectedDeck.description }}</p>
          <p class="text-xs font-semibold text-indigo-500 uppercase tracking-wider mt-2">{{ currentCards.length }} cartes au total</p>
        </div>
        
        <div class="flex items-center gap-3">
          <button 
            @click="router.push(`/decks/${selectedDeck.id}/study`)"
            class="px-4 py-2 text-sm font-semibold rounded-xl text-white bg-indigo-600 hover:bg-indigo-700 transition-all shadow-md shadow-indigo-600/10"
          >
            Lancer l'étude
          </button>
          <button 
            @click="openCreateCardModal"
            class="px-4 py-2 text-sm font-semibold rounded-xl border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all"
          >
            Ajouter une carte
          </button>
        </div>
      </div>

      <!-- Cards List -->
      <div class="space-y-4">
        <h3 class="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Cartes du Deck</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div 
            v-for="card in currentCards" 
            :key="card.id"
            class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-2xl p-5 shadow-sm hover:border-slate-200 dark:hover:border-slate-700/60 transition-colors group flex flex-col justify-between"
          >
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Recto (Front)</span>
                <p class="text-sm font-bold text-slate-800 dark:text-slate-200 mt-1">{{ card.front }}</p>
              </div>
              <div class="border-t sm:border-t-0 sm:border-l border-slate-50 dark:border-slate-800/50 pt-3 sm:pt-0 sm:pl-4">
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Verso (Back)</span>
                <p class="text-sm text-slate-600 dark:text-slate-400 mt-1">{{ card.back }}</p>
              </div>
            </div>

            <div class="flex items-center justify-between gap-4 mt-6 pt-3 border-t border-slate-50 dark:border-slate-800/40">
              <!-- SM-2 Stats badge -->
              <span class="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
                Intervalle : {{ card.interval }}j | EF : {{ card.ease_factor.toFixed(2) }}
              </span>
              <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button 
                  @click="openEditCardModal(card)" 
                  class="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800"
                  title="Modifier"
                >
                  <Edit class="w-3.5 h-3.5" />
                </button>
                <button 
                  @click="deleteCard(card.id)" 
                  class="p-1 text-slate-400 hover:text-rose-500 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/30"
                  title="Supprimer"
                >
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>

          <div 
            v-if="currentCards.length === 0" 
            class="col-span-full border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-2xl p-12 flex flex-col items-center justify-center text-center text-slate-400"
          >
            <Layers class="w-10 h-10 text-slate-300 dark:text-slate-700 mb-2" />
            <p class="text-xs font-semibold uppercase tracking-wider">Aucune carte dans ce deck</p>
            <button 
              @click="openCreateCardModal"
              class="mt-3 px-3.5 py-1.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl transition-all"
            >
              Ajouter une Carte
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- Create/Edit Deck Modal -->
    <div v-if="showDeckModal" class="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div class="absolute inset-0 bg-slate-950/40 backdrop-blur-sm" @click="showDeckModal = false"></div>
      <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-3xl w-full max-w-md p-6 relative z-10 shadow-2xl animate-scale-up">
        <h3 class="text-lg font-bold mb-4">{{ isEditingDeck ? 'Modifier le deck' : 'Créer un nouveau deck' }}</h3>
        <form @submit.prevent="submitDeckForm">
          <div class="space-y-4">
            <div>
              <label for="deck-name" class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Nom du deck</label>
              <input id="deck-name" type="text" required v-model="deckForm.name" class="block w-full px-4 py-3 bg-slate-50 border border-slate-200 dark:bg-slate-800/40 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-medium" placeholder="Ex: Vocabulaire Espagnol" />
            </div>
            <div>
              <label for="deck-desc" class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Description</label>
              <textarea id="deck-desc" v-model="deckForm.description" rows="3" class="block w-full px-4 py-3 bg-slate-50 border border-slate-200 dark:bg-slate-800/40 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-medium" placeholder="Ex: Verbes irréguliers et vocabulaire utile pour voyager."></textarea>
            </div>
            <div v-if="isEditingDeck">
              <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Tags</label>
              <TagSelector v-model="deckForm.tags" @change="saveDeckTags" />
            </div>
          </div>
          <div class="flex items-center justify-end gap-3 mt-6">
            <button type="button" @click="showDeckModal = false" class="px-4 py-2 text-sm font-semibold rounded-xl text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800">Annuler</button>
            <button type="submit" class="px-4 py-2 text-sm font-semibold rounded-xl text-white bg-indigo-600 hover:bg-indigo-700">Enregistrer</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Create/Edit Card Modal -->
    <div v-if="showCardModal" class="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div class="absolute inset-0 bg-slate-950/40 backdrop-blur-sm" @click="showCardModal = false"></div>
      <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-3xl w-full max-w-md p-6 relative z-10 shadow-2xl animate-scale-up">
        <h3 class="text-lg font-bold mb-4">{{ isEditingCard ? 'Modifier la carte' : 'Ajouter une carte' }}</h3>
        <form @submit.prevent="submitCardForm">
          <div class="space-y-4">
            <div>
              <label for="card-front" class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Recto (Question / Terme)</label>
              <input id="card-front" type="text" required v-model="cardForm.front" class="block w-full px-4 py-3 bg-slate-50 border border-slate-200 dark:bg-slate-800/40 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-medium" placeholder="Ex: El coche" />
            </div>
            <div>
              <label for="card-back" class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Verso (Réponse / Définition)</label>
              <textarea id="card-back" required v-model="cardForm.back" rows="3" class="block w-full px-4 py-3 bg-slate-50 border border-slate-200 dark:bg-slate-800/40 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-medium" placeholder="Ex: La voiture"></textarea>
            </div>
          </div>
          <div class="flex items-center justify-end gap-3 mt-6">
            <button type="button" @click="showCardModal = false" class="px-4 py-2 text-sm font-semibold rounded-xl text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800">Annuler</button>
            <button type="submit" class="px-4 py-2 text-sm font-semibold rounded-xl text-white bg-indigo-600 hover:bg-indigo-700">Enregistrer</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Anki Import Modal -->
    <AnkiImportModal 
      :is-open="showAnkiModal" 
      @close="showAnkiModal = false" 
      @success="decksStore.fetchDecks"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDecksStore } from '../../stores/decks'
import type { Deck, Flashcard } from '../../stores/decks'
import { useTagsStore, type Tag } from '../../stores/tags'
import TagBadge from '../../components/ui/TagBadge.vue'
import TagSelector from '../../components/ui/TagSelector.vue'
import { Plus, ChevronRight, Layers, Edit, Trash2, Upload } from '@lucide/vue'
import AnkiImportModal from '../../components/decks/AnkiImportModal.vue'

const decksStore = useDecksStore()
const tagsStore = useTagsStore()
const router = useRouter()
const route = useRoute()

const selectedDeck = ref<Deck | null>(null)
const selectedTagId = ref<number | null>(null)
const showAnkiModal = ref(false)

// Deck Form Modal
const showDeckModal = ref(false)
const isEditingDeck = ref(false)
const deckForm = ref<{ id: number; name: string; description: string; tags: Tag[] }>({ id: 0, name: '', description: '', tags: [] })

// Card Form Modal
const showCardModal = ref(false)
const isEditingCard = ref(false)
const cardForm = ref({ id: 0, front: '', back: '' })

// Filtered cards for selected deck
const currentCards = computed(() => {
  if (!selectedDeck.value) return []
  return decksStore.cards.filter(c => c.deck_id === selectedDeck.value!.id)
})

onMounted(async () => {
  await Promise.all([tagsStore.fetchTags(), decksStore.fetchDecks()])
  const deckIdQuery = route.query.id
  if (deckIdQuery) {
    const deckId = parseInt(deckIdQuery as string)
    const deck = decksStore.decks.find(d => d.id === deckId)
    if (deck) {
      selectDeck(deck)
    }
  }
})

watch(() => route.query.id, (newId) => {
  if (newId) {
    const deckId = parseInt(newId as string)
    const deck = decksStore.decks.find(d => d.id === deckId)
    if (deck) {
      selectDeck(deck)
    }
  } else {
    selectedDeck.value = null
  }
})

async function filterByTag(tagId: number | null) {
  selectedTagId.value = tagId
  await decksStore.fetchDecks(tagId)
}

function selectDeck(deck: Deck) {
  selectedDeck.value = deck
}

// Deck CRUD Methods
function openCreateDeckModal() {
  isEditingDeck.value = false
  deckForm.value = { id: 0, name: '', description: '', tags: [] }
  showDeckModal.value = true
}

function openEditDeckModal(deck: Deck) {
  isEditingDeck.value = true
  deckForm.value = { id: deck.id, name: deck.name, description: deck.description, tags: deck.tags || [] }
  showDeckModal.value = true
}

async function submitDeckForm() {
  if (isEditingDeck.value) {
    await decksStore.updateDeck(deckForm.value.id, deckForm.value.name, deckForm.value.description)
    await saveDeckTags(deckForm.value.tags)
  } else {
    await decksStore.createDeck(deckForm.value.name, deckForm.value.description)
  }
  showDeckModal.value = false
}

async function saveDeckTags(tags: Tag[]) {
  if (!isEditingDeck.value || deckForm.value.id === 0) return
  const updatedTags = await tagsStore.setTagsForEntity('decks', deckForm.value.id, tags.map(tag => tag.id))
  const deck = decksStore.decks.find(item => item.id === deckForm.value.id)
  if (deck) deck.tags = updatedTags
  deckForm.value.tags = updatedTags
}

async function deleteDeck(deck: Deck) {
  if (confirm(`Êtes-vous sûr de vouloir supprimer le deck "${deck.name}" et toutes ses cartes ?`)) {
    await decksStore.deleteDeck(deck.id)
    if (selectedDeck.value?.id === deck.id) selectedDeck.value = null
  }
}

// Card CRUD Methods
function openCreateCardModal() {
  isEditingCard.value = false
  cardForm.value = { id: 0, front: '', back: '' }
  showCardModal.value = true
}

function openEditCardModal(card: Flashcard) {
  isEditingCard.value = true
  cardForm.value = { id: card.id, front: card.front, back: card.back }
  showCardModal.value = true
}

async function submitCardForm() {
  if (!selectedDeck.value) return
  
  if (isEditingCard.value) {
    await decksStore.updateCard(cardForm.value.id, cardForm.value.front, cardForm.value.back)
  } else {
    await decksStore.createCard(selectedDeck.value.id, cardForm.value.front, cardForm.value.back)
  }
  showCardModal.value = false
}

async function deleteCard(cardId: number) {
  if (confirm('Voulez-vous supprimer cette carte ?')) {
    await decksStore.deleteCard(cardId)
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
