import { defineStore } from 'pinia'
import { ref } from 'vue'
import planningService from '../services/planningService'
import type { PlanningDay } from '../services/planningService'
import type { Flashcard } from './decks'

export const usePlanningStore = defineStore('planning', () => {
  const calendarDays = ref<PlanningDay[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  const advanceReviewCards = ref<Flashcard[]>([])
  const advanceDeckId = ref<number | null>(null)

  async function fetchCalendar(from: string, to: string) {
    loading.value = true
    error.value = null
    try {
      const data = await planningService.getCalendar(from, to)
      calendarDays.value = data.days
    } catch (err: any) {
      console.error('Erreur de chargement du planning', err)
      error.value = err.message || 'Impossible de charger le planning.'
    } finally {
      loading.value = false
    }
  }

  async function prepareAdvanceReview(deckId: number, dateStr?: string, cardIds: number[] = []) {
    loading.value = true
    error.value = null
    try {
      const cards = await planningService.advanceReview(deckId, cardIds, dateStr)
      advanceReviewCards.value = cards
      advanceDeckId.value = deckId
      return cards
    } catch (err: any) {
      console.error('Erreur lors de la preparation de la revision anticipee', err)
      error.value = err.message || 'Impossible de preparer la session.'
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearAdvanceReview() {
    advanceReviewCards.value = []
    advanceDeckId.value = null
  }

  return {
    calendarDays,
    loading,
    error,
    advanceReviewCards,
    advanceDeckId,
    fetchCalendar,
    prepareAdvanceReview,
    clearAdvanceReview
  }
})
