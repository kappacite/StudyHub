import api from './api'

// Méthode Feynman (IA) : compare l'explication rédigée par l'utilisateur à la
// note de référence. Flux asynchrone (Celery + polling), avec repli synchrone
// côté serveur (POST /feynman/analyze peut renvoyer le résultat directement,
// status === 'SUCCESS', sans passer par le polling de tâche).

export interface FeynmanGap {
  concept: string
  issue: string
}

export interface FeynmanResult {
  clarity_score?: number
  jargon?: string[]
  gaps?: FeynmanGap[]
  feedback?: string
  suggestion?: string
}

export interface FeynmanAnalyzeResponse {
  status: string
  result?: FeynmanResult
  task_id?: string
}

export interface FeynmanTaskResponse {
  status: string
  result?: FeynmanResult
  error?: { message: string }
}

const feynmanService = {
  async analyze(noteId: string, userExplanation: string, durationSeconds: number) {
    const response = await api.post<FeynmanAnalyzeResponse>('/feynman/analyze', {
      note_id: noteId,
      user_explanation: userExplanation,
      duration_seconds: durationSeconds,
    })
    return response.data
  },

  async pollTask(taskId: string) {
    const response = await api.get<FeynmanTaskResponse>(`/feynman/tasks/${taskId}`)
    return response.data
  },
}

export default feynmanService
