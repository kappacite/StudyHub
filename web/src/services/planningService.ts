import api from './api'
import type { Flashcard } from '../stores/decks'

export interface DeckBreakdown {
  deck_id: number
  deck_name: string
  count: number
}

export interface PlanningDay {
  date: string // YYYY-MM-DD
  total_due: number
  breakdown: DeckBreakdown[]
}

export interface PlanningCalendar {
  days: PlanningDay[]
}

const planningService = {
  async getCalendar(from: string, to: string) {
    const response = await api.get<PlanningCalendar>(`/planning/calendar?from=${from}&to=${to}`)
    return response.data
  },

  async advanceReview(deckId: number, cardIds?: number[], date?: string) {
    const response = await api.post<Flashcard[]>('/planning/advance', {
      deck_id: deckId,
      card_ids: cardIds || null,
      date: date || null
    })
    return response.data
  }
}

export default planningService
