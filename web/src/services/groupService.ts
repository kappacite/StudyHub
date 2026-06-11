import api from './api'

// ─── Types ────────────────────────────────────────────────────────────────────

export interface GroupMember {
  user_id: number
  username: string
  email: string
  role: 'owner' | 'admin' | 'member'
  joined_at: string
}

export interface GroupBinder {
  group_id: number
  binder_id: number
  binder_name: string
  permission: 'read' | 'write'
  pinned: boolean
  added_by: number | null
  added_at: string
}

export interface GroupActivity {
  id: number
  user_id: number
  username: string
  type: 'joined' | 'shared_binder' | 'completed_session' | 'posted_note'
  payload: Record<string, unknown> | null
  created_at: string
}

export interface Group {
  id: number
  name: string
  description: string | null
  invite_code: string
  created_by: number | null
  created_at: string
  members_count: number
  binders_count: number
}

export interface GroupDetail {
  id: number
  name: string
  description: string | null
  invite_code: string
  created_by: number | null
  created_at: string
  members: GroupMember[]
  binders: GroupBinder[]
}

export interface MemberProgress {
  user_id: number
  username: string
  total_time_seconds: number
  cards_reviewed: number
  cards_correct: number
}

// ─── Service ──────────────────────────────────────────────────────────────────

const groupService = {
  async createGroup(name: string, description?: string) {
    const response = await api.post<Group>('/groups', { name, description })
    return response.data
  },

  async getMyGroups() {
    const response = await api.get<Group[]>('/groups')
    return response.data
  },

  async getGroupDetail(groupId: number) {
    const response = await api.get<GroupDetail>(`/groups/${groupId}`)
    return response.data
  },

  async joinGroup(inviteCode: string) {
    const response = await api.post<Group>('/groups/join', { invite_code: inviteCode })
    return response.data
  },

  async leaveOrExcludeMember(groupId: number, targetUserId: number) {
    await api.delete(`/groups/${groupId}/members/${targetUserId}`)
  },

  async updateMemberRole(groupId: number, targetUserId: number, role: 'admin' | 'member') {
    const response = await api.patch<GroupMember>(`/groups/${groupId}/members/${targetUserId}`, { role })
    return response.data
  },

  async shareBinder(groupId: number, binderId: number, permission: 'read' | 'write') {
    const response = await api.post<GroupBinder>(`/groups/${groupId}/binders`, {
      binder_id: binderId,
      permission
    })
    return response.data
  },

  async unshareBinder(groupId: number, binderId: number) {
    await api.delete(`/groups/${groupId}/binders/${binderId}`)
  },

  async getGroupActivity(groupId: number, page = 1, perPage = 20) {
    const response = await api.get<GroupActivity[]>(`/groups/${groupId}/activity`, {
      params: { page, per_page: perPage }
    })
    return response.data
  },

  async getGroupMembersProgress(groupId: number) {
    const response = await api.get<MemberProgress[]>(`/groups/${groupId}/members/progress`)
    return response.data
  }
}

export default groupService
