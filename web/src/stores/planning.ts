import { defineStore } from 'pinia'
import { ref } from 'vue'
import planningService from '../services/planningService'
import type { PlanningDay, PlanningItemKind } from '../services/planningService'
import type { Flashcard } from './decks'

export const usePlanningStore = defineStore('planning', () => {
  const calendarDays = ref<PlanningDay[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Seul le parcours "deck" (StudyDeck.vue) consomme advanceReviewCards -- un ensemble de
  // révision route directement vers /revision/sets/:id/study sans passer par ce store
  // (cf. studyItemAdvance, PlanningPage.vue), donc pas de RevisionItem à stocker ici.
  const advanceReviewCards = ref<Flashcard[]>([])
  const advanceDeckId = ref<number | null>(null)

  async function fetchCalendar(from: string, to: string) {
    loading.value = true
    error.value = null
    try {
      const data = await planningService.getCalendar(from, to)
      calendarDays.value = data.days
    } catch (err) {
      console.error('Erreur de chargement du planning', err)
      error.value = err instanceof Error ? err.message : 'Impossible de charger le planning.'
    } finally {
      loading.value = false
    }
  }

  async function prepareAdvanceReview(
    kind: PlanningItemKind,
    id: number,
    dateStr?: string,
    itemIds: number[] = [],
  ) {
    loading.value = true
    error.value = null
    try {
      const items = await planningService.advanceReview(kind, id, itemIds, dateStr)
      if (kind === 'deck') {
        advanceReviewCards.value = items as Flashcard[]
        advanceDeckId.value = id
      }
      return items
    } catch (err) {
      console.error('Erreur lors de la preparation de la revision anticipee', err)
      error.value = err instanceof Error ? err.message : 'Impossible de preparer la session.'
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
    clearAdvanceReview,
  }
})
