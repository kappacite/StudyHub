import api from './api'

// ─── Types ─────────────────────────────────────────────────────────────────

export interface ClassInfo {
  id: number
  name: string
  description: string | null
  invite_code: string
  type: string
  is_class: boolean
  created_by: number | null
  created_at: string
  members_count: number
}

export interface AssignmentProgress {
  user_id: number
  username: string
  cards_reviewed: number
  score_pct: number | null
  completed_at: string | null
}

export interface Assignment {
  id: number
  group_id: number
  binder_id: number
  binder_name: string
  title: string
  description: string | null
  due_date: string | null
  created_by: number
  created_at: string
  progress?: AssignmentProgress[]
}

export interface AssignmentSummary {
  id: number
  group_id: number
  group_name: string
  binder_id: number
  binder_name: string
  title: string
  description: string | null
  due_date: string | null
  created_at: string
  my_cards_reviewed: number
  my_score_pct: number | null
  my_completed_at: string | null
  status: 'todo' | 'in_progress' | 'done' | 'late'
}

// ─── Service ────────────────────────────────────────────────────────────────

const classService = {
  async createClass(name: string, description?: string): Promise<ClassInfo> {
    const resp = await api.post<ClassInfo>('/classes', { name, description })
    return resp.data
  },

  async listAssignments(classId: number): Promise<Assignment[]> {
    const resp = await api.get<Assignment[]>(`/classes/${classId}/assignments`)
    return resp.data
  },

  async createAssignment(
    classId: number,
    payload: { binder_id: number; title: string; description?: string; due_date?: string }
  ): Promise<Assignment> {
    const resp = await api.post<Assignment>(`/classes/${classId}/assignments`, payload)
    return resp.data
  },

  async getAssignment(classId: number, assignmentId: number): Promise<Assignment> {
    const resp = await api.get<Assignment>(`/classes/${classId}/assignments/${assignmentId}`)
    return resp.data
  },

  async deleteAssignment(classId: number, assignmentId: number): Promise<void> {
    await api.delete(`/classes/${classId}/assignments/${assignmentId}`)
  },

  async getStudentProgress(classId: number, studentId: number): Promise<AssignmentProgress[]> {
    const resp = await api.get<AssignmentProgress[]>(
      `/classes/${classId}/students/${studentId}/progress`
    )
    return resp.data
  },

  async getMyAssignments(): Promise<AssignmentSummary[]> {
    const resp = await api.get<AssignmentSummary[]>('/assignments/mine')
    return resp.data
  }
}

export default classService
