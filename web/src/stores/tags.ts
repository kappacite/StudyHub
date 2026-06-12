import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export interface Tag {
  id: number
  name: string
  color: string | null
  created_at: string
}

interface TagsResponse {
  data: Tag[]
}

export type TaggableEntity = 'notes' | 'decks' | 'diagrams' | 'pdfs' | 'binders'

export const useTagsStore = defineStore('tags', () => {
  const tags = ref<Tag[]>([])
  const loading = ref(false)

  async function fetchTags() {
    loading.value = true
    try {
      const response = await api.get<TagsResponse>('/tags')
      tags.value = response.data.data
      return tags.value
    } finally {
      loading.value = false
    }
  }

  async function createTag(name: string, color: string | null = null) {
    const response = await api.post<Tag>('/tags', { name, color })
    tags.value = [...tags.value, response.data].sort((a, b) => a.name.localeCompare(b.name))
    return response.data
  }

  async function updateTag(id: number, payload: { name?: string; color?: string | null }) {
    const response = await api.put<Tag>(`/tags/${id}`, payload)
    const index = tags.value.findIndex(tag => tag.id === id)
    if (index !== -1) tags.value[index] = response.data
    return response.data
  }

  async function deleteTag(id: number) {
    await api.delete(`/tags/${id}`)
    tags.value = tags.value.filter(tag => tag.id !== id)
  }

  async function setTagsForEntity(entity: TaggableEntity, id: number | string, tagIds: number[]) {
    const response = await api.post<TagsResponse>(`/${entity}/${id}/tags`, { tag_ids: tagIds })
    return response.data.data
  }

  return {
    tags,
    loading,
    fetchTags,
    createTag,
    updateTag,
    deleteTag,
    setTagsForEntity
  }
})
