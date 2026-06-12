import api from './api'

// ─── Types ─────────────────────────────────────────────────────────────────

export interface ClassInfo {
  id: number
  name: string
  description: string | null
  invite_code: string
  type: string
  is_class: boolean
  is_public: boolean
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
  binder_id: string
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
  binder_id: string
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
  async createClass(name: string, description?: string, isPublic?: boolean): Promise<ClassInfo> {
    const resp = await api.post<ClassInfo>('/classes', { name, description, is_public: isPublic })
    return resp.data
  },

  async getMyClasses(): Promise<ClassInfo[]> {
    const resp = await api.get<ClassInfo[]>('/classes')
    return resp.data
  },

  async listAssignments(classId: number): Promise<Assignment[]> {
    const resp = await api.get<Assignment[]>(`/classes/${classId}/assignments`)
    return resp.data
  },

  async createAssignment(
    classId: number,
    payload: { binder_id: string; title: string; description?: string; due_date?: string }
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
  },

  async getPublicClasses(search?: string): Promise<ClassInfo[]> {
    const resp = await api.get<ClassInfo[]>('/classes/public', { params: { search } })
    return resp.data
  },

  async followClass(classId: number): Promise<ClassInfo> {
    const resp = await api.post<ClassInfo>(`/classes/${classId}/follow`)
    return resp.data
  },

  async getClassMaterialsProgress(classId: number): Promise<StudentMaterialsProgress[]> {
    const resp = await api.get<StudentMaterialsProgress[]>(`/classes/${classId}/materials/progress`)
    return resp.data
  }
}

export interface BinderProgress {
  binder_id: string
  binder_name: string
  cards_reviewed: number
  total_cards: number
  score_pct: number
  last_reviewed_at: string | null
}

export interface StudentMaterialsProgress {
  user_id: number
  username: string
  binders_progress: BinderProgress[]
}

export default classService

