import api from './api'

export interface QuizOption {
  id: string
  text: string
  correct: boolean
}

export interface QuizQuestion {
  id: number
  quiz_id: number
  question_text: string
  options: QuizOption[]
  user_answer_id: string | null
}

export interface Quiz {
  id: number
  note_id: string
  user_id: number
  score_pct: number | null
  created_at: string
  completed_at: string | null
  questions: QuizQuestion[]
}

const quizService = {
  async generateQuiz(noteId: string, questionCount = 7) {
    const response = await api.post<Quiz>('/quizzes/generate', {
      note_id: noteId,
      question_count: questionCount
    })
    return response.data
  },

  async getQuizzesByNote(noteId: string) {
    const response = await api.get<Quiz[]>(`/quizzes/note/${noteId}`)
    return response.data
  },

  async getQuiz(quizId: number) {
    const response = await api.get<Quiz>(`/quizzes/${quizId}`)
    return response.data
  },

  async answerQuestion(quizId: number, questionId: number, answerId: string) {
    const response = await api.post<QuizQuestion>(`/quizzes/${quizId}/questions/${questionId}/answer`, {
      answer_id: answerId
    })
    return response.data
  },

  async completeQuiz(quizId: number) {
    const response = await api.post<Quiz>(`/quizzes/${quizId}/complete`)
    return response.data
  },

  async createFlashcards(quizId: number, deckId: number, questionIds: number[]) {
    const response = await api.post<any[]>(`/quizzes/${quizId}/create-flashcards`, {
      deck_id: deckId,
      question_ids: questionIds
    })
    return response.data
  }
}

export default quizService
