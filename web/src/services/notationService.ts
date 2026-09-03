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
}

export default notationService
