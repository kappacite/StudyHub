import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export interface Flashcard {
  id: number
  deck_id: number
  front: string
  back: string
  interval: number
  ease_factor: number
  repetitions: number
  next_review: string
}

export interface Deck {
  id: number
  binder_id: number | null
  name: string
  description: string
  card_count: number
  created_at: string
}

interface DecksResponse {
  data: Deck[]
}

interface CardsResponse {
  data: Flashcard[]
}

export const useDecksStore = defineStore('decks', () => {
  const decks = ref<Deck[]>([])
  const cards = ref<Flashcard[]>([])
  const loading = ref(false)

  async function fetchDecks() {
    loading.value = true
    try {
      const response = await api.get<DecksResponse>('/decks?per_page=1000')
      decks.value = response.data.data
      return decks.value
    } catch (error) {
      console.error('Erreur lors du chargement des decks', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function fetchDeckById(id: number) {
    try {
      const response = await api.get<Deck>(`/decks/${id}`)
      const index = decks.value.findIndex(d => d.id === id)
      if (index !== -1) {
        decks.value[index] = response.data
      } else {
        decks.value.push(response.data)
      }
      return response.data
    } catch (error) {
      console.error(`Erreur lors du chargement du deck ${id}`, error)
      // Fallback local search
      return decks.value.find(d => d.id === id)
    }
  }

  async function createDeck(name: string, description: string, binderId: number | null = null) {
    loading.value = true
    try {
      const response = await api.post<Deck>('/decks', {
        name,
        description,
        binder_id: binderId
      })
      const newDeck = response.data
      decks.value.push(newDeck)
      return newDeck
    } catch (error) {
      console.error('Erreur lors de la création du deck', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function updateDeck(id: number, name: string, description: string) {
    try {
      const response = await api.put<Deck>(`/decks/${id}`, { name, description })
      const updatedDeck = response.data
      const index = decks.value.findIndex(d => d.id === id)
      if (index !== -1) {
        decks.value[index] = updatedDeck
      }
      return updatedDeck
    } catch (error) {
      console.error('Erreur lors de la mise à jour du deck', error)
      throw error
    }
  }

  async function deleteDeck(id: number) {
    try {
      await api.delete(`/decks/${id}`)
      decks.value = decks.value.filter(d => d.id !== id)
      cards.value = cards.value.filter(c => c.deck_id !== id)
    } catch (error) {
      console.error('Erreur lors de la suppression du deck', error)
      throw error
    }
  }

  async function fetchCardsForDeck(deckId: number) {
    loading.value = true
    try {
      const response = await api.get<CardsResponse>(`/decks/${deckId}/cards?per_page=1000`)
      // Remplacer les cartes de ce deck dans notre cache local
      cards.value = cards.value.filter(c => c.deck_id !== deckId).concat(response.data.data)
      return response.data.data
    } catch (error) {
      console.error('Erreur de chargement des cartes', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function createCard(deckId: number, front: string, back: string) {
    try {
      const response = await api.post<Flashcard>(`/decks/${deckId}/cards`, { front, back })
      const newCard = response.data
      cards.value.push(newCard)
      
      // Mettre à jour le nombre local de cartes dans le deck
      const deck = decks.value.find(d => d.id === deckId)
      if (deck) deck.card_count++
      
      return newCard
    } catch (error) {
      console.error('Erreur de création de carte', error)
      throw error
    }
  }

  async function updateCard(cardId: number, front: string, back: string) {
    const card = cards.value.find(c => c.id === cardId)
    if (!card) throw new Error('Carte introuvable localement pour mise à jour')
    
    try {
      const response = await api.put<Flashcard>(`/decks/${card.deck_id}/cards/${cardId}`, { front, back })
      const updatedCard = response.data
      const index = cards.value.findIndex(c => c.id === cardId)
      if (index !== -1) {
        cards.value[index] = updatedCard
      }
      return updatedCard
    } catch (error) {
      console.error('Erreur de modification de carte', error)
      throw error
    }
  }

  async function deleteCard(cardId: number) {
    const card = cards.value.find(c => c.id === cardId)
    if (!card) throw new Error('Carte introuvable localement pour suppression')
    
    try {
      await api.delete(`/decks/${card.deck_id}/cards/${cardId}`)
      const deck = decks.value.find(d => d.id === card.deck_id)
      if (deck) deck.card_count = Math.max(0, deck.card_count - 1)
      
      cards.value = cards.value.filter(c => c.id !== cardId)
    } catch (error) {
      console.error('Erreur de suppression de carte', error)
      throw error
    }
  }

  async function fetchStudyCards(deckId: number) {
    try {
      const response = await api.get<Flashcard[]>(`/decks/${deckId}/study`)
      return response.data
    } catch (error) {
      console.error('Erreur de chargement des cartes d\'étude', error)
      throw error
    }
  }

  async function answerCard(cardId: number, quality: number) {
    const card = cards.value.find(c => c.id === cardId)
    if (!card) throw new Error('Carte introuvable localement pour évaluation')
    
    try {
      const response = await api.post<Flashcard>(`/decks/${card.deck_id}/study/answer/${cardId}`, {
        score: quality
      })
      const updatedCard = response.data
      const index = cards.value.findIndex(c => c.id === cardId)
      if (index !== -1) {
        cards.value[index] = updatedCard
      }
      return updatedCard
    } catch (error) {
      console.error('Erreur de soumission du score de la carte', error)
      throw error
    }
  }

  return {
    decks,
    cards,
    loading,
    fetchDecks,
    fetchDeckById,
    createDeck,
    updateDeck,
    deleteDeck,
    fetchCardsForDeck,
    createCard,
    updateCard,
    deleteCard,
    fetchStudyCards,
    answerCard
  }
})
