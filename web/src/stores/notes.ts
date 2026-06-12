import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'
import type { Tag } from './tags'

export interface Note {
  id: string
  binder_id: string | null
  title: string
  content: string
  created_at: string
  updated_at: string
  tags: Tag[]
}

interface NotesResponse {
  data: Note[]
}

export const useNotesStore = defineStore('notes', () => {
  const notes = ref<Note[]>([])
  const loading = ref(false)
  const isReviewModeActive = ref(false)

  async function fetchNotes(tagId: number | null = null) {
    loading.value = true
    try {
      const params = new URLSearchParams({ per_page: '1000' })
      if (tagId !== null) params.set('tag_id', String(tagId))
      const response = await api.get<NotesResponse>(`/notes?${params.toString()}`)
      notes.value = response.data.data
      return notes.value
    } catch (error) {
      console.error('Erreur lors du chargement des notes', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function fetchNoteById(id: string) {
    loading.value = true
    try {
      const response = await api.get<Note>(`/notes/${id}`)
      const index = notes.value.findIndex(n => n.id === id)
      if (index !== -1) {
        notes.value[index] = response.data
      } else {
        notes.value.push(response.data)
      }
      return response.data
    } catch (error) {
      console.error(`Erreur de chargement de la note ${id}`, error)
      // Fallback local search
      return notes.value.find(n => n.id === id)
    } finally {
      loading.value = false
    }
  }

  async function createNote(title: string, content: string = '', binderId: string | null = null) {
    loading.value = true
    try {
      const response = await api.post<Note>('/notes', {
        title,
        content,
        binder_id: binderId
      })
      const newNote = response.data
      notes.value.push(newNote)
      return newNote
    } catch (error) {
      console.error('Erreur de création de la note', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function updateNote(id: string, title: string, content: string) {
    try {
      const note = notes.value.find(n => n.id === id)
      const binder_id = note ? note.binder_id : null
      
      const response = await api.put<Note>(`/notes/${id}`, {
        title,
        content,
        binder_id
      })
      const updatedNote = response.data
      const index = notes.value.findIndex(n => n.id === id)
      if (index !== -1) {
        notes.value[index] = updatedNote
      }
      return updatedNote
    } catch (error) {
      console.error('Erreur de mise à jour de la note', error)
      throw error
    }
  }

  async function deleteNote(id: string) {
    try {
      await api.delete(`/notes/${id}`)
      notes.value = notes.value.filter(n => n.id !== id)
    } catch (error) {
      console.error('Erreur de suppression de la note', error)
      throw error
    }
  }

  return {
    notes,
    loading,
    isReviewModeActive,
    fetchNotes,
    fetchNoteById,
    createNote,
    updateNote,
    deleteNote
  }
})
