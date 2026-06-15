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
  teacher_score?: number | null
  teacher_feedback?: string | null
  graded_at?: string | null
}

export type TaskType = 'flashcards' | 'quiz' | 'exam' | 'blurting' | 'read' | 'revision'

export interface AssignmentTask {
  id: number
  task_type: TaskType
  ref_id: number | null
  ref_uuid: string | null
  ref_label: string | null
  goal: Record<string, unknown> | null
  order: number
  my_status: 'todo' | 'in_progress' | 'done' | null
  my_score_pct: number | null
  my_completed_at: string | null
}

export interface AssignmentTaskInput {
  task_type: TaskType
  ref: string
  goal?: Record<string, unknown>
}

export interface Assignment {
  id: number
  group_id: number
  binder_id: string
  binder_name: string
  title: string
  description: string | null
  instructions?: string | null
  due_date: string | null
  publish_at?: string | null
  allow_late?: boolean
  created_by: number
  created_at: string
  tasks: AssignmentTask[]
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
  tasks: AssignmentTask[]
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
    payload: {
      title: string
      description?: string
      instructions?: string
      due_date?: string
      publish_at?: string
      allow_late?: boolean
      // Voie multi-tâches (préférée) ou voie legacy mono-classeur.
      tasks?: AssignmentTaskInput[]
      binder_id?: string
    }
  ): Promise<Assignment> {
    const resp = await api.post<Assignment>(`/classes/${classId}/assignments`, payload)
    return resp.data
  },

  async submitTask(
    classId: number,
    assignmentId: number,
    taskId: number
  ): Promise<AssignmentTask> {
    const resp = await api.post<AssignmentTask>(
      `/classes/${classId}/assignments/${assignmentId}/tasks/${taskId}/submit`,
      {}
    )
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
  },

  async getClassAnalytics(classId: number): Promise<ClassOverview> {
    const resp = await api.get<ClassOverview>(`/classes/${classId}/analytics`)
    return resp.data
  },

  async getClassInsights(classId: number): Promise<ClassInsight> {
    const resp = await api.get<ClassInsight>(`/classes/${classId}/insights`)
    return resp.data
  },

  async refreshClassInsights(classId: number): Promise<{ status: string; task_id?: string }> {
    const resp = await api.post(`/classes/${classId}/insights`)
    return resp.data
  },

  async gradeSubmission(
    classId: number,
    assignmentId: number,
    studentId: number,
    payload: { teacher_score?: number; teacher_feedback?: string }
  ): Promise<AssignmentProgress> {
    const resp = await api.patch<AssignmentProgress>(
      `/classes/${classId}/assignments/${assignmentId}/submissions/${studentId}`,
      payload
    )
    return resp.data
  },

  async postAnnouncement(classId: number, payload: { title: string; body?: string }): Promise<FeedItem> {
    const resp = await api.post<FeedItem>(`/classes/${classId}/announcements`, payload)
    return resp.data
  },

  async getFeed(classId: number): Promise<FeedItem[]> {
    const resp = await api.get<FeedItem[]>(`/classes/${classId}/feed`)
    return resp.data
  },

  async getLeaderboard(classId: number): Promise<Leaderboard> {
    const resp = await api.get<Leaderboard>(`/classes/${classId}/leaderboard`)
    return resp.data
  },

  async getRoster(classId: number): Promise<RosterEntry[]> {
    const resp = await api.get<RosterEntry[]>(`/classes/${classId}/members`)
    return resp.data
  },

  async removeMember(classId: number, userId: number): Promise<void> {
    // Réutilise l'endpoint groupes (les classes sont des groupes).
    await api.delete(`/groups/${classId}/members/${userId}`)
  },

  async regenerateInvite(classId: number): Promise<{ invite_code: string }> {
    const resp = await api.post<{ invite_code: string }>(`/classes/${classId}/invite/regenerate`)
    return resp.data
  },

  async distributeBinder(classId: number, binderId: string): Promise<{ distributed: number; failed: number }> {
    const resp = await api.post(`/classes/${classId}/distribute`, { binder_id: binderId })
    return resp.data
  },

  // Questions des élèves (Q&A) — B4
  async listQuestions(classId: number): Promise<ClassQuestion[]> {
    const resp = await api.get<ClassQuestion[]>(`/classes/${classId}/questions`)
    return resp.data
  },

  async postQuestion(classId: number, body: string): Promise<ClassQuestion> {
    const resp = await api.post<ClassQuestion>(`/classes/${classId}/questions`, { body })
    return resp.data
  },

  async answerQuestion(classId: number, questionId: number, body: string): Promise<ClassQuestion> {
    const resp = await api.post<ClassQuestion>(`/classes/${classId}/questions/${questionId}/answer`, { body })
    return resp.data
  }
}

export interface AssignmentStat {
  id: number
  title: string
  due_date: string | null
  submissions_count: number
  completed_count: number
  completion_rate: number
  avg_score: number | null
}

export interface StudentStat {
  user_id: number
  username: string
  completed_assignments: number
  avg_score: number | null
  study_minutes: number
  success_rate: number | null
}

export interface ClassOverview {
  class_id: number
  students_count: number
  assignments_count: number
  completion_rate: number
  avg_score: number | null
  active_students_7d: number
  avg_study_minutes: number
  study_success_rate: number | null
  assignments: AssignmentStat[]
  students: StudentStat[]
}

export interface WeakTopic {
  note_id: number
  note_title: string
  error_rate: number
  sample: number
}

export interface ClassInsight {
  class_id: number
  weak_topics: WeakTopic[]
  summary: string
  ai: boolean
  created_at: string | null
}

export interface RosterEntry {
  user_id: number
  username: string
  role: string
  joined_at: string | null
  completed_assignments: number
  last_active: string | null
}

export interface FeedItem {
  id: number
  type: string
  username: string
  payload: Record<string, unknown> | null
  created_at: string
}

export interface LeaderboardEntry {
  user_id: number
  username: string
  completed_assignments: number
  avg_score: number | null
  streak: number
  points: number
  badges: string[]
}

export interface Leaderboard {
  enabled: boolean
  entries: LeaderboardEntry[]
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

export interface ClassQuestion {
  id: number
  body: string
  answer: string | null
  status: 'open' | 'answered'
  author_id: number
  author_username: string | null
  answered_by_username: string | null
  created_at: string
  answered_at: string | null
}

export default classService

