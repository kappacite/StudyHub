import api from './api'

export interface ExamOption {
  id: string
  text: string
  correct?: boolean
}

export interface ExamItem {
  id: number
  item_type: 'flashcard' | 'qcm'
  item_id: number
  front: string
  back: string | null
  options: ExamOption[] | null
  user_answer: any | null
  is_correct: boolean | null
}

export interface ExamSession {
  id: number
  binder_id: number | null
  user_id: number
  duration_seconds: number
  started_at: string
  completed_at: string | null
  score_pct: number | null
  flashcard_score: number | null
  qcm_score: number | null
  time_taken_seconds: number | null
  items: ExamItem[]
}

const examService = {
  async startExam(
    binderId: number,
    durationMinutes = 30,
    includeFlashcards = true,
    includeQcm = true,
    questionLimit = 20
  ) {
    const response = await api.post<ExamSession>('/exam/start', {
      binder_id: binderId,
      duration_minutes: durationMinutes,
      include_flashcards: includeFlashcards,
      include_qcm: includeQcm,
      question_limit: questionLimit
    })
    return response.data
  },

  async getExamSession(sessionId: number) {
    const response = await api.get<ExamSession>(`/exam/${sessionId}`)
    return response.data
  },

  async submitAnswer(sessionId: number, itemId: number, answer: any) {
    const response = await api.post<{ is_correct: boolean }>(`/exam/${sessionId}/questions/${itemId}/answer`, {
      answer
    })
    return response.data
  },

  async completeExam(sessionId: number) {
    const response = await api.post<ExamSession>(`/exam/${sessionId}/complete`)
    return response.data
  }
}

export default examService
