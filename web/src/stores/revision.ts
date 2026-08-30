import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

// D8 (bibliotheque-ensembles) : un ensemble peut desormais etre heterogene
// (type: null) -- le type vit au niveau de l'item. RevisionType reste le type
// *homogene* d'un ensemble (5 valeurs, historique) ; RevisionItemType est le
// type d'un item individuel (6 valeurs, ajoute "flashcard").
export type RevisionType = 'qcm' | 'vf' | 'association' | 'definition' | 'ordre'
export type RevisionItemType = RevisionType | 'flashcard'

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
  // flashcard
  front?: string
  back?: string
}

export interface RevisionSet {
  id: number
  name: string
  description: string | null
  type: RevisionType | null
  binder_id: string | null
  tuning_default: number
  is_public: boolean
  item_count: number
  read_only?: boolean
  // Toujours renvoyé par le backend (RevisionSetResponse) ; optionnel ici pour ne
  // pas casser les littéraux de test existants qui ne le renseignent pas encore
  // (même convention que read_only ci-dessus). Utilisé par binderAggregate()
  // (Binders.vue, Task 1 bibliotheque-redesign) pour le libellé de dernière activité.
  updated_at?: string
}

export interface RevisionItem {
  id: number
  set_id: number
  type: RevisionItemType
  payload: RevisionItemPayload
  tuning: number
  position: number
  interval: number
  ease_factor: number
  repetitions: number
  next_review: string
  created_at: string
  updated_at: string
}

// QCM question par question (check/commit — Task 2/Task 6 revision-flexibilite) :
// remplace l'ancien passage scoré en lot (RunAnswer/RunResult, route /run
// supprimee cote backend) par le meme principe check (sans effet de bord) puis
// commit que vf/association/ordre (cf. checkItemAnswer/gradeItem plus bas).
export interface QcmCheckResult {
  correct: boolean
  earned: number
  points: number
  correct_option_ids: string[]
}

export interface QcmAnswerResult extends QcmCheckResult {
  item: RevisionItem
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
  type: RevisionItemType
  label: string
  reviews: number
  success_rate: number
  difficulty: number
  retrievability: number
  is_leech: boolean
  is_mature: boolean
  due: boolean
}

export interface GradeDistribution {
  again: number
  hard: number
  good: number
  easy: number
}

export interface WeeklyProgressionPoint {
  reviews: number
  success_rate: number
}

export interface SessionHistoryDay {
  date: string
  reviews: number
  success_rate: number
  duration_seconds: number
}

export interface SetStats {
  set_id: number
  type: RevisionType | null
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
  grade_distribution: GradeDistribution
  weekly_progression: WeeklyProgressionPoint[]
  session_history: SessionHistoryDay[]
  total_duration_seconds: number
  next_review_at: string | null
}

export interface SetSummary {
  set_id: number
  type: RevisionType | null
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
  type: RevisionItemType
  sets_count: number
  items_count: number
  mastered_count: number
  mastery_rate: number
}

export interface BinderStats {
  binder_id: string
  // UUID publics du classeur + de son sous-arbre effectivement inclus (selon
  // include_descendants) -- permet de scoper d'autres ressources (ex. decks)
  // sur le meme perimetre sans re-marcher l'arbre cote frontend.
  binder_ids: string[]
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
  total_duration_seconds: number
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
    type: RevisionType | null,
    description: string | null = null,
    binderId: string | null = null,
    tuningDefault = 1.0,
  ) {
    const response = await api.post<RevisionSet>('/revision/sets', {
      name,
      type,
      description,
      binder_id: binderId,
      tuning_default: tuningDefault,
    })
    sets.value.push(response.data)
    return response.data
  }

  async function updateSet(
    setId: number,
    patch: Partial<Pick<RevisionSet, 'name' | 'description' | 'tuning_default' | 'binder_id'>>,
  ) {
    const response = await api.put<RevisionSet>(`/revision/sets/${setId}`, patch)
    const index = sets.value.findIndex((s) => s.id === setId)
    if (index !== -1) sets.value[index] = response.data
    return response.data
  }

  async function deleteSet(setId: number) {
    await api.delete(`/revision/sets/${setId}`)
    sets.value = sets.value.filter((s) => s.id !== setId)
  }

  async function fetchSet(setId: number) {
    const response = await api.get<RevisionSet>(`/revision/sets/${setId}`)
    return response.data
  }

  async function fetchItems(setId: number) {
    const response = await api.get<ItemsResponse>(`/revision/sets/${setId}/items`)
    return response.data.data
  }

  async function createItem(
    setId: number,
    payload: RevisionItemPayload,
    type?: RevisionItemType,
    tuning = 1.0,
  ) {
    const body: { payload: RevisionItemPayload; type?: RevisionItemType; tuning: number } = {
      payload,
      tuning,
    }
    if (type !== undefined) body.type = type
    const response = await api.post<RevisionItem>(`/revision/sets/${setId}/items`, body)
    const set = sets.value.find((s) => s.id === setId)
    if (set) set.item_count++
    return response.data
  }

  async function updateItem(
    setId: number,
    itemId: number,
    payload: RevisionItemPayload,
    tuning?: number,
  ) {
    const body: { payload: RevisionItemPayload; tuning?: number } = { payload }
    if (tuning !== undefined) body.tuning = tuning
    const response = await api.put<RevisionItem>(`/revision/sets/${setId}/items/${itemId}`, body)
    return response.data
  }

  async function deleteItem(setId: number, itemId: number) {
    await api.delete(`/revision/sets/${setId}/items/${itemId}`)
    const set = sets.value.find((s) => s.id === setId)
    if (set && set.item_count > 0) set.item_count--
  }

  async function fetchStudyItems(setId: number, includeNotDue = false) {
    const suffix = includeNotDue ? '?include_not_due=true' : ''
    const response = await api.get<RevisionItem[]>(`/revision/sets/${setId}/study${suffix}`)
    return response.data
  }

  async function answerItem(setId: number, itemId: number, score: number, durationSeconds = 0) {
    const response = await api.post<RevisionItem>(
      `/revision/sets/${setId}/study/answer/${itemId}`,
      { score, duration_seconds: durationSeconds },
    )
    return response.data
  }

  // Verification sans effet de bord (Task 6) : correction d'une question qcm
  // (earned/points/correct_option_ids) sans appliquer de note SM-2, sur le
  // meme principe que checkItemAnswer ci-dessous.
  async function checkQcmAnswer(setId: number, itemId: number, selectedOptionIds: string[]) {
    const response = await api.post<QcmCheckResult>(
      `/revision/sets/${setId}/study/qcm-check/${itemId}`,
      { selected_option_ids: selectedOptionIds },
    )
    return response.data
  }

  // Applique la note SM-2 choisie par l'utilisateur apres avoir vu la
  // correction (cf. checkQcmAnswer) -- meme principe que gradeItem, mais pour
  // une question qcm (reponse deja typee en selected_option_ids).
  async function answerQcmItem(
    setId: number,
    itemId: number,
    selectedOptionIds: string[],
    score: number,
    durationSeconds = 0,
  ) {
    const response = await api.post<QcmAnswerResult>(
      `/revision/sets/${setId}/study/qcm-answer/${itemId}`,
      { selected_option_ids: selectedOptionIds, score, duration_seconds: durationSeconds },
    )
    return response.data
  }

  // Verification sans effet de bord (Task 5) : permet d'afficher la correction
  // d'un item vf/association/ordre avant de demander une auto-evaluation
  // manuelle, sans encore appliquer de note SM-2 (contrairement a gradeItem).
  async function checkItemAnswer(setId: number, itemId: number, answer: Record<string, unknown>) {
    const response = await api.post<{ correct: boolean }>(
      `/revision/sets/${setId}/study/check/${itemId}`,
      { answer },
    )
    return response.data
  }

  async function gradeItem(
    setId: number,
    itemId: number,
    answer: Record<string, unknown>,
    score: number,
    durationSeconds = 0,
  ) {
    const response = await api.post<{ correct: boolean; item: RevisionItem }>(
      `/revision/sets/${setId}/study/grade/${itemId}`,
      { answer, score, duration_seconds: durationSeconds },
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
    updateItem,
    deleteItem,
    fetchStudyItems,
    answerItem,
    checkQcmAnswer,
    answerQcmItem,
    checkItemAnswer,
    gradeItem,
    fetchSetStats,
    fetchItemStats,
    fetchBinderStats,
  }
})
