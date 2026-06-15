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

  return {
    sets,
    loading,
    fetchSets,
    createSet,
    updateSet,
    deleteSet,
    fetchItems,
    createItem,
    fetchStudyItems,
    answerItem,
  }
})
