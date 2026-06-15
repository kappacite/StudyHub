import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

// D3c : types d'ensembles de révision *génériques* (hors flashcard recto/verso,
// qui reste un Deck). Un ensemble est homogène (un seul type).
export type RevisionType = 'qcm' | 'vf' | 'association' | 'definition' | 'ordre'

export interface QcmOption {
  id: string
  text: string
  correct: boolean
}

export interface RevisionItemPayload {
  // qcm
  question?: string
  options?: QcmOption[]
  points?: number
  // vf
  assertion?: string
  correct?: boolean
  justification?: string
  // association / ordre
  title?: string
  steps?: string[]
  pairs?: { left: string; right: string }[]
  // definition
  term?: string
  definition?: string
}

export interface RevisionSet {
  id: number
  name: string
  description: string | null
  type: RevisionType
  binder_id: string | null
  tuning_default: number
  is_public: boolean
  item_count: number
}

export interface RevisionItem {
  id: number
  set_id: number
  payload: RevisionItemPayload
  tuning: number
  position: number
  interval: number
  ease_factor: number
  repetitions: number
  next_review: string
}

export interface RunAnswer {
  item_id: number
  selected_option_ids: string[]
}

export interface RunQuestionResult {
  item_id: number
  correct: boolean
  earned: number
  points: number
  correct_option_ids: string[]
  selected_option_ids: string[]
}

export interface RunResult {
  score: number
  max_score: number
  percentage: number
  results: RunQuestionResult[]
}

export interface HistoryPoint {
  date: string
  grade: number | null
}

export interface ItemStats {
  item_id: number
  reviews: number
  success_rate: number
  lapses: number
  repetitions: number
  ease_factor: number
  interval: number
  next_review: string | null
  last_reviewed: string | null
  stability_days: number
  difficulty: number
  retrievability: number
  is_mature: boolean
  is_leech: boolean
  mastered: boolean
  mastery_date: string | null
  history: HistoryPoint[]
}

export interface ItemSummary {
  item_id: number
  label: string
  reviews: number
  success_rate: number
  difficulty: number
  retrievability: number
  is_leech: boolean
  is_mature: boolean
  due: boolean
}

export interface SetStats {
  set_id: number
  type: RevisionType
  name: string
  items_count: number
  reviewed_items: number
  mastered_count: number
  mastery_rate: number
  avg_success_rate: number
  true_retention: number
  leeches_count: number
  due_count: number
  avg_difficulty: number
  verdicts: string[]
  items: ItemSummary[]
}

export interface SetSummary {
  set_id: number
  type: RevisionType
  name: string
  items_count: number
  reviewed_items: number
  mastered_count: number
  mastery_rate: number
  avg_success_rate: number
  true_retention: number
  leeches_count: number
  due_count: number
  avg_difficulty: number
}

export interface TypeBreakdown {
  type: RevisionType
  sets_count: number
  items_count: number
  mastered_count: number
  mastery_rate: number
}

export interface BinderStats {
  binder_id: string
  name: string
  include_descendants: boolean
  sets_count: number
  items_count: number
  reviewed_items: number
  mastered_count: number
  mastery_rate: number
  avg_success_rate: number
  true_retention: number
  leeches_count: number
  due_count: number
  avg_difficulty: number
  by_type: TypeBreakdown[]
  sets: SetSummary[]
  weakest_sets: SetSummary[]
  verdicts: string[]
}

interface SetsResponse {
  data: RevisionSet[]
}

interface ItemsResponse {
  data: RevisionItem[]
}

export const useRevisionStore = defineStore('revision', () => {
  const sets = ref<RevisionSet[]>([])
  const loading = ref(false)

  async function fetchSets(type: RevisionType | null = null) {
    loading.value = true
    try {
      const params = new URLSearchParams({ per_page: '1000' })
      if (type !== null) params.set('type', type)
      const response = await api.get<SetsResponse>(`/revision/sets?${params.toString()}`)
      sets.value = response.data.data
      return sets.value
    } finally {
      loading.value = false
    }
  }

  async function createSet(
    name: string,
    type: RevisionType,
    binderId: string | null = null,
    tuningDefault = 1.0,
  ) {
    const response = await api.post<RevisionSet>('/revision/sets', {
      name,
      type,
      binder_id: binderId,
      tuning_default: tuningDefault,
    })
    sets.value.push(response.data)
    return response.data
  }

  async function updateSet(setId: number, patch: Partial<Pick<RevisionSet, 'name' | 'description' | 'tuning_default'>>) {
    const response = await api.put<RevisionSet>(`/revision/sets/${setId}`, patch)
    const index = sets.value.findIndex(s => s.id === setId)
    if (index !== -1) sets.value[index] = response.data
    return response.data
  }

  async function deleteSet(setId: number) {
    await api.delete(`/revision/sets/${setId}`)
    sets.value = sets.value.filter(s => s.id !== setId)
  }

  async function fetchSet(setId: number) {
    const response = await api.get<RevisionSet>(`/revision/sets/${setId}`)
    return response.data
  }

  async function fetchItems(setId: number) {
    const response = await api.get<ItemsResponse>(`/revision/sets/${setId}/items`)
    return response.data.data
  }

  async function createItem(setId: number, payload: RevisionItemPayload, tuning = 1.0) {
    const response = await api.post<RevisionItem>(`/revision/sets/${setId}/items`, {
      payload,
      tuning,
    })
    const set = sets.value.find(s => s.id === setId)
    if (set) set.item_count++
    return response.data
  }

  async function fetchStudyItems(setId: number) {
    const response = await api.get<RevisionItem[]>(`/revision/sets/${setId}/study`)
    return response.data
  }

  async function answerItem(setId: number, itemId: number, score: number) {
    const response = await api.post<RevisionItem>(
      `/revision/sets/${setId}/study/answer/${itemId}`,
      { score },
    )
    return response.data
  }

  async function runQcm(setId: number, answers: RunAnswer[]) {
    const response = await api.post<RunResult>(`/revision/sets/${setId}/run`, { answers })
    return response.data
  }

  async function gradeItem(setId: number, itemId: number, answer: Record<string, unknown>) {
    const response = await api.post<{ correct: boolean; item: RevisionItem }>(
      `/revision/sets/${setId}/study/grade/${itemId}`,
      { answer },
    )
    return response.data
  }

  async function fetchSetStats(setId: number) {
    const response = await api.get<SetStats>(`/stats/sets/${setId}`)
    return response.data
  }

  async function fetchItemStats(itemId: number) {
    const response = await api.get<ItemStats>(`/stats/items/${itemId}`)
    return response.data
  }

  async function fetchBinderStats(binderId: string, includeDescendants = true) {
    const suffix = includeDescendants ? '' : '?descendants=false'
    const response = await api.get<BinderStats>(`/stats/binders/${binderId}${suffix}`)
    return response.data
  }

  return {
    sets,
    loading,
    fetchSets,
    createSet,
    updateSet,
    deleteSet,
    fetchSet,
    fetchItems,
    createItem,
    fetchStudyItems,
    answerItem,
    runQcm,
    gradeItem,
    fetchSetStats,
    fetchItemStats,
    fetchBinderStats,
  }
})
