import api from './api'
import type { Flashcard } from '../stores/decks'
import type { RevisionItem } from '../stores/revision'

// notes-ia-planning-corrections, Task 1/2 : generalise l'ancien DeckBreakdown (deck_id/
// deck_name) pour couvrir aussi les RevisionSet -- kind discrimine la source cote UI
// (rendu ET routage du bouton "Reviser").
export type PlanningItemKind = 'deck' | 'revision_set'

export interface BreakdownItem {
  kind: PlanningItemKind
  id: number
  name: string
  count: number
}

export interface PlanningDay {
  date: string // YYYY-MM-DD
  total_due: number
  breakdown: BreakdownItem[]
}

export interface PlanningCalendar {
  days: PlanningDay[]
}

const planningService = {
  async getCalendar(from: string, to: string) {
    const response = await api.get<PlanningCalendar>(`/planning/calendar?from=${from}&to=${to}`)
    return response.data
  },

  async advanceReview(
    kind: PlanningItemKind,
    id: number,
    itemIds?: number[],
    date?: string | null,
  ) {
    const response = await api.post<Flashcard[] | RevisionItem[]>('/planning/advance', {
      deck_id: kind === 'deck' ? id : null,
      set_id: kind === 'revision_set' ? id : null,
      card_ids: itemIds || null,
      date: date || null,
    })
    return response.data
  },
}

export default planningService
