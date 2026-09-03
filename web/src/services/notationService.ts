import axios from 'axios'
import api from './api'

// Notation IA de la note (qualité de la fiche, distincte de l'Évaluation mixte qui note
// la performance de l'étudiant) -- notes-ia-planning-corrections, Task 4/5. Flux
// asynchrone (Celery + polling), avec repli synchrone côté serveur, même patron que
// feynmanService.ts.

export interface NotationResult {
  score?: number
  verdict?: string
  points_forts?: string[]
  ameliorations?: string[]
  suggestions?: string
  // Renseigne uniquement par getExisting() (notes-ia-planning-corrections, Task 12) --
  // absent d'une reponse fraiche de grade()/pollTask().
  updated_at?: string
}

export interface NotationGradeResponse {
  status: string
  result?: NotationResult
  task_id?: string
}

export interface NotationTaskResponse {
  status: string
  result?: NotationResult
  error?: { message: string }
}

const notationService = {
  async grade(noteId: string) {
    const response = await api.post<NotationGradeResponse>('/notation/grade', {
      note_id: noteId,
    })
    return response.data
  },

  async pollTask(taskId: string) {
    const response = await api.get<NotationTaskResponse>(`/notation/tasks/${taskId}`)
    return response.data
  },

  // notes-ia-planning-corrections, Task 12 : notation deja enregistree pour cette note,
  // ou null si aucune (404 -- cas normal, pas une erreur). Permet au frontend de proposer
  // voir/reevaluer plutot que de relancer l'IA a chaque clic sur "Notation".
  async getExisting(noteId: string): Promise<NotationResult | null> {
    try {
      const response = await api.get<NotationResult>(`/notation/${noteId}`)
      return response.data
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.status === 404) return null
      throw err
    }
  },
}

export default notationService
