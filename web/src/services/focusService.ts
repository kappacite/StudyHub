import api from './api'

export interface FocusItem {
  type: 'deck' | 'note' | 'assignment'
  id: number
  title: string
  count: number
  is_late: boolean
  last_session_ago_days: number | null
  due_date?: string | null
  assignment_id?: number | null
}

export interface FocusToday {
  total_due: number
  late_count: number
  flashcard_count: number
  blurting_count: number
  assignment_count: number
  items: FocusItem[]
}

export interface ForecastItem {
  date: string
  count: number
  load_level: 'low' | 'medium' | 'high'
}

export interface FocusForecast {
  forecast: ForecastItem[]
}

export interface RetentionSubject {
  binder_id: number
  binder_name: string
  retention_pct: number
  overdue_count: number
  trend_7d: number
}

export interface FocusRetention {
  by_subject: RetentionSubject[]
}

const focusService = {
  async getFocusToday() {
    const response = await api.get<FocusToday>('/focus/today')
    return response.data
  },

  async getFocusForecast(days = 14) {
    const response = await api.get<FocusForecast>(`/focus/forecast?days=${days}`)
    return response.data
  },

  async getFocusRetention() {
    const response = await api.get<FocusRetention>('/focus/retention')
    return response.data
  }
}

export default focusService
