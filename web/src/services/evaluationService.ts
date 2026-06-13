import api from './api'

export type EvalItemType = 'qcm' | 'vf' | 'trou' | 'open'
export type SelfGrade = 'acquired' | 'partial' | 'missed'

export interface EvalOption {
  id: string
  text: string
  correct?: boolean
}

export interface EvalItemPayload {
  question?: string
  options?: EvalOption[]
  assertion?: string
  justification?: string
  correct?: boolean
  text_with_blank?: string
  answer?: string
  model_answer?: string
  key_points?: string[]
}

export interface EvalUserAnswer {
  value: unknown
  self_grade?: SelfGrade
}

export interface EvalItem {
  id: number
  type: EvalItemType
  source: 'ai' | 'manual'
  payload: EvalItemPayload
  user_answer: EvalUserAnswer | null
  is_correct: boolean | null
}

export interface Evaluation {
  id: number
  note_id: string
  user_id: number
  score_pct: number | null
  created_at: string
  completed_at: string | null
  items: EvalItem[]
}

export interface EvalCorrection {
  correct_option_id?: string
  options?: EvalOption[]
  correct?: boolean
  justification?: string
  answer?: string
  model_answer?: string
  key_points?: string[]
}

export interface EvalAnswerResult {
  item_id: number
  is_correct: boolean | null
  correction: EvalCorrection
}

interface GenerateTaskResponse {
  task_id: string
  status: string
}

interface TaskPollResponse {
  status: string
  result?: Evaluation
  error?: { message: string }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

const evaluationService = {
  /**
   * Lance la génération asynchrone (IA) puis sonde la tâche jusqu'à complétion.
   * Renvoie la feuille d'évaluation (vue question, corrections masquées).
   */
  async generate(noteId: string, itemCount = 8, force = false): Promise<Evaluation> {
    const { data } = await api.post<GenerateTaskResponse>('/evaluations/generate', {
      note_id: noteId,
      item_count: itemCount,
      force,
    })

    const taskId = data.task_id
    if (!taskId) {
      throw new Error("L'API n'a pas retourné d'identifiant de tâche.")
    }

    for (let attempt = 0; attempt < 60; attempt++) {
      await sleep(2000)
      const poll = await api.get<TaskPollResponse>(`/evaluations/tasks/${taskId}`)
      const status = poll.data.status
      if (status === 'SUCCESS' && poll.data.result) {
        return poll.data.result
      }
      if (status === 'FAILURE' || poll.data.error) {
        throw new Error(poll.data.error?.message || "La génération de l'évaluation a échoué.")
      }
    }
    throw new Error("La génération de l'évaluation a expiré. Réessayez plus tard.")
  },

  async get(evaluationId: number): Promise<Evaluation> {
    const { data } = await api.get<Evaluation>(`/evaluations/${evaluationId}`)
    return data
  },

  async answer(
    evaluationId: number,
    itemId: number,
    value: unknown,
    selfGrade?: SelfGrade,
  ): Promise<EvalAnswerResult> {
    const { data } = await api.post<EvalAnswerResult>(
      `/evaluations/${evaluationId}/items/${itemId}/answer`,
      { value, self_grade: selfGrade ?? null },
    )
    return data
  },

  async complete(evaluationId: number): Promise<Evaluation> {
    const { data } = await api.post<Evaluation>(`/evaluations/${evaluationId}/complete`)
    return data
  },
}

export default evaluationService
