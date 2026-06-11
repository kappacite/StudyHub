import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'
import type { Tag } from './tags'

export interface Binder {
  id: number
  parent_id: number | null
  name: string
  created_at: string
  is_public?: boolean
  description?: string | null
  tags?: Tag[]
}

interface BindersResponse {
  data: Binder[]
}

export const useBindersStore = defineStore('binders', () => {
  const binders = ref<Binder[]>([])
  const loading = ref(false)

  async function fetchBinders(tagId: number | null = null) {
    loading.value = true
    try {
      const params = new URLSearchParams({ all: 'true' })
      if (tagId !== null) params.set('tag_id', String(tagId))
      const response = await api.get<BindersResponse>(`/binders?${params.toString()}`)
      binders.value = response.data.data
      return binders.value
    } catch (error) {
      console.error('Erreur de chargement des classeurs', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function createBinder(name: string, parentId: number | null = null) {
    loading.value = true
    try {
      const response = await api.post<Binder>('/binders', {
        name,
        parent_id: parentId
      })
      const newBinder = response.data
      binders.value.push(newBinder)
      return newBinder
    } catch (error) {
      console.error('Erreur de création du classeur', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function updateBinder(id: number, data: Record<string, unknown>) {
    try {
      const response = await api.put<Binder>(`/binders/${id}`, data)
      const updatedBinder = response.data
      const index = binders.value.findIndex(b => b.id === id)
      if (index !== -1) {
        binders.value[index] = updatedBinder
      }
      return updatedBinder
    } catch (error) {
      console.error('Erreur de mise à jour du classeur', error)
      throw error
    }
  }

  async function deleteBinder(id: number) {
    try {
      await api.delete(`/binders/${id}`)
      // Supprimer localement le classeur et tous ses enfants récursivement
      const idsToDelete = [id]
      const findChildren = (parentId: number) => {
        binders.value.forEach(b => {
          if (b.parent_id === parentId) {
            idsToDelete.push(b.id)
            findChildren(b.id)
          }
        })
      }
      findChildren(id)
      binders.value = binders.value.filter(b => !idsToDelete.includes(b.id))
    } catch (error) {
      console.error('Erreur de suppression du classeur', error)
      throw error
    }
  }

  return {
    binders,
    loading,
    fetchBinders,
    createBinder,
    updateBinder,
    deleteBinder
  }
})
