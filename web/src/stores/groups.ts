import { defineStore } from 'pinia'
import { ref } from 'vue'
import groupService from '../services/groupService'
import type { Group, GroupDetail, GroupActivity, MemberProgress } from '../services/groupService'

export const useGroupsStore = defineStore('groups', () => {
  const groups = ref<Group[]>([])
  const currentGroup = ref<GroupDetail | null>(null)
  const activities = ref<GroupActivity[]>([])
  const membersProgress = ref<MemberProgress[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchMyGroups() {
    loading.value = true
    error.value = null
    try {
      groups.value = await groupService.getMyGroups()
    } catch (e: unknown) {
      error.value = 'Impossible de charger vos groupes.'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchGroupDetail(groupId: number) {
    loading.value = true
    error.value = null
    try {
      currentGroup.value = await groupService.getGroupDetail(groupId)
    } catch (e: unknown) {
      error.value = 'Groupe introuvable.'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createGroup(name: string, description?: string) {
    const newGroup = await groupService.createGroup(name, description)
    groups.value.unshift(newGroup)
    return newGroup
  }

  async function joinGroup(inviteCode: string) {
    const group = await groupService.joinGroup(inviteCode)
    const exists = groups.value.some(g => g.id === group.id)
    if (!exists) groups.value.unshift(group)
    return group
  }

  async function fetchGroupActivity(groupId: number) {
    const data = await groupService.getGroupActivity(groupId)
    activities.value = data
  }

  async function fetchMembersProgress(groupId: number) {
    const data = await groupService.getGroupMembersProgress(groupId)
    membersProgress.value = data
  }

  async function shareBinder(groupId: number, binderId: string, permission: 'read' | 'write') {
    await groupService.shareBinder(groupId, binderId, permission)
    if (currentGroup.value?.id === groupId) {
      await fetchGroupDetail(groupId)
    }
  }

  async function unshareBinder(groupId: number, binderId: string) {
    await groupService.unshareBinder(groupId, binderId)
    if (currentGroup.value) {
      currentGroup.value.binders = currentGroup.value.binders.filter(b => b.binder_id !== binderId)
    }
  }

  async function updateMemberRole(groupId: number, targetUserId: number, role: 'admin' | 'member') {
    await groupService.updateMemberRole(groupId, targetUserId, role)
    if (currentGroup.value) {
      const m = currentGroup.value.members.find(m => m.user_id === targetUserId)
      if (m) m.role = role
    }
  }

  async function leaveGroup(groupId: number, userId: number) {
    await groupService.leaveOrExcludeMember(groupId, userId)
    groups.value = groups.value.filter(g => g.id !== groupId)
  }

  async function excludeMember(groupId: number, targetUserId: number) {
    await groupService.leaveOrExcludeMember(groupId, targetUserId)
    if (currentGroup.value) {
      currentGroup.value.members = currentGroup.value.members.filter(m => m.user_id !== targetUserId)
    }
  }

  return {
    groups,
    currentGroup,
    activities,
    membersProgress,
    loading,
    error,
    fetchMyGroups,
    fetchGroupDetail,
    createGroup,
    joinGroup,
    fetchGroupActivity,
    fetchMembersProgress,
    shareBinder,
    unshareBinder,
    updateMemberRole,
    leaveGroup,
    excludeMember
  }
})
