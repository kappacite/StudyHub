import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Flashcard {
  id: number
  deck_id: number
  front: string
  back: string
  // SM-2 fields
  interval: number // en jours
  ease_factor: number
  repetitions: number
  next_review: string // date ISO
}

export interface Deck {
  id: number
  binder_id: number | null
  name: string
  description: string
  card_count: number
  created_at: string
}

export const useDecksStore = defineStore('decks', () => {
  const decks = ref<Deck[]>([
    { id: 1, binder_id: 1, name: 'Vocabulaire Anglais C1', description: 'Vocabulaire avancé pour le TOEIC/IELTS', card_count: 3, created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 5).toISOString() },
    { id: 2, binder_id: 2, name: 'Anatomie - Système Cardiaque', description: 'Apprendre le fonctionnement du coeur et des vaisseaux', card_count: 2, created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString() },
    { id: 3, binder_id: null, name: 'Histoire contemporaine', description: 'Dates clés du XXème siècle', card_count: 2, created_at: new Date().toISOString() }
  ])

  const cards = ref<Flashcard[]>([
    // Deck 1
    { id: 1, deck_id: 1, front: 'To advocate', back: 'Défendre publiquement une opinion, soutenir une cause.', interval: 1, ease_factor: 2.5, repetitions: 0, next_review: new Date().toISOString() },
    { id: 2, deck_id: 1, front: 'Obsolete', back: 'Périmé, dépassé par le progrès.', interval: 6, ease_factor: 2.6, repetitions: 1, next_review: new Date().toISOString() },
    { id: 3, deck_id: 1, front: 'To jeopardize', back: 'Mettre en péril, compromettre.', interval: 12, ease_factor: 2.7, repetitions: 2, next_review: new Date(Date.now() + 1000 * 60 * 60 * 24 * 2).toISOString() },
    // Deck 2
    { id: 4, deck_id: 2, front: 'Myocarde', back: 'Le muscle cardiaque proprement dit, responsable de la contraction.', interval: 1, ease_factor: 2.5, repetitions: 0, next_review: new Date().toISOString() },
    { id: 5, deck_id: 2, front: 'Ventricule gauche', back: 'Cavité du coeur pompant le sang oxygéné vers tout le corps via l\'aorte.', interval: 1, ease_factor: 2.5, repetitions: 0, next_review: new Date().toISOString() },
    // Deck 3
    { id: 6, deck_id: 3, front: 'Chute du mur de Berlin', back: '9 novembre 1989', interval: 1, ease_factor: 2.5, repetitions: 0, next_review: new Date().toISOString() },
    { id: 7, deck_id: 3, front: 'Accords de Yalta', back: '4 au 11 février 1945', interval: 12, ease_factor: 2.5, repetitions: 2, next_review: new Date(Date.now() + 1000 * 60 * 60 * 24 * 5).toISOString() }
  ])

  const loading = ref(false)

  async function fetchDecks() {
    loading.value = true
    return new Promise<Deck[]>((resolve) => {
      setTimeout(() => {
        loading.value = false
        resolve(decks.value)
      }, 500)
    })
  }

  async function fetchDeckById(id: number) {
    return new Promise<Deck | undefined>((resolve) => {
      setTimeout(() => {
        resolve(decks.value.find(d => d.id === id))
      }, 300)
    })
  }

  async function createDeck(name: string, description: string, binderId: number | null = null) {
    loading.value = true
    return new Promise<Deck>((resolve) => {
      setTimeout(() => {
        const newDeck: Deck = {
          id: decks.value.length ? Math.max(...decks.value.map(d => d.id)) + 1 : 1,
          binder_id: binderId,
          name,
          description,
          card_count: 0,
          created_at: new Date().toISOString()
        }
        decks.value.push(newDeck)
        loading.value = false
        resolve(newDeck)
      }, 600)
    })
  }

  async function updateDeck(id: number, name: string, description: string) {
    return new Promise<Deck>((resolve, reject) => {
      setTimeout(() => {
        const index = decks.value.findIndex(d => d.id === id)
        if (index !== -1) {
          decks.value[index] = { ...decks.value[index], name, description }
          resolve(decks.value[index])
        } else {
          reject(new Error('Deck introuvable'))
        }
      }, 400)
    })
  }

  async function deleteDeck(id: number) {
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        decks.value = decks.value.filter(d => d.id !== id)
        cards.value = cards.value.filter(c => c.deck_id !== id)
        resolve()
      }, 400)
    })
  }

  async function fetchCardsForDeck(deckId: number) {
    loading.value = true
    return new Promise<Flashcard[]>((resolve) => {
      setTimeout(() => {
        loading.value = false
        resolve(cards.value.filter(c => c.deck_id === deckId))
      }, 400)
    })
  }

  async function createCard(deckId: number, front: string, back: string) {
    return new Promise<Flashcard>((resolve) => {
      setTimeout(() => {
        const newCard: Flashcard = {
          id: cards.value.length ? Math.max(...cards.value.map(c => c.id)) + 1 : 1,
          deck_id: deckId,
          front,
          back,
          interval: 1,
          ease_factor: 2.5,
          repetitions: 0,
          next_review: new Date().toISOString()
        }
        cards.value.push(newCard)
        // Update count in deck
        const deck = decks.value.find(d => d.id === deckId)
        if (deck) deck.card_count++
        resolve(newCard)
      }, 400)
    })
  }

  async function updateCard(cardId: number, front: string, back: string) {
    return new Promise<Flashcard>((resolve, reject) => {
      setTimeout(() => {
        const index = cards.value.findIndex(c => c.id === cardId)
        if (index !== -1) {
          cards.value[index] = { ...cards.value[index], front, back }
          resolve(cards.value[index])
        } else {
          reject(new Error('Carte introuvable'))
        }
      }, 300)
    })
  }

  async function deleteCard(cardId: number) {
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        const cardToDelete = cards.value.find(c => c.id === cardId)
        if (cardToDelete) {
          const deck = decks.value.find(d => d.id === cardToDelete.deck_id)
          if (deck) deck.card_count = Math.max(0, deck.card_count - 1)
        }
        cards.value = cards.value.filter(c => c.id !== cardId)
        resolve()
      }, 300)
    })
  }

  // SM-2 logic & Study queue
  async function fetchStudyCards(deckId: number) {
    return new Promise<Flashcard[]>((resolve) => {
      setTimeout(() => {
        const today = new Date()
        const studyList = cards.value.filter(c => {
          return c.deck_id === deckId && new Date(c.next_review) <= today
        })
        resolve(studyList)
      }, 400)
    })
  }

  async function answerCard(cardId: number, quality: number) {
    return new Promise<Flashcard>((resolve, reject) => {
      setTimeout(() => {
        const index = cards.value.findIndex(c => c.id === cardId)
        if (index === -1) return reject(new Error('Carte introuvable'))

        const card = cards.value[index]
        
        let interval = card.interval
        let easeFactor = card.ease_factor
        let repetitions = card.repetitions

        if (quality < 3) {
          // Reprendre à zéro
          repetitions = 0
          interval = 1
        } else {
          if (repetitions === 0) {
            interval = 1
          } else if (repetitions === 1) {
            interval = 6
          } else {
            interval = Math.round(interval * easeFactor)
          }
          repetitions++
        }

        // Mettre à jour ease factor
        easeFactor = easeFactor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if (easeFactor < 1.3) easeFactor = 1.3

        // Calculer la prochaine date de révision
        const nextReviewDate = new Date()
        nextReviewDate.setDate(nextReviewDate.getDate() + interval)

        const updatedCard: Flashcard = {
          ...card,
          interval,
          ease_factor: easeFactor,
          repetitions,
          next_review: nextReviewDate.toISOString()
        }

        cards.value[index] = updatedCard
        resolve(updatedCard)
      }, 300)
    })
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
