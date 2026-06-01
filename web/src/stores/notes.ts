import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Note {
  id: number
  binder_id: number | null
  title: string
  content: string
  created_at: string
  updated_at: string
}

export const useNotesStore = defineStore('notes', () => {
  const notes = ref<Note[]>([
    {
      id: 1,
      binder_id: 1,
      title: 'Résumé de thermodynamique',
      content: '# Thermodynamique : Les Principes\n\nLa thermodynamique est la branche de la physique qui étudie les relations entre la chaleur, le travail et les autres formes d\'énergie.\n\n## Premier Principe\nLe premier principe est le principe de conservation de l\'énergie :\n$$\\Delta U = Q + W$$\n\nOù :\n* $\\Delta U$ : Énergie interne du système\n* $Q$ : Chaleur échangée\n* $W$ : Travail mécanique échangé\n\n## Deuxième Principe\nIl introduit la notion d\'entropie $S$ pour caractériser l\'irréversibilité des transformations :\n$$\\Delta S \\ge \\int \\frac{\\delta Q}{T}$$',
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 10).toISOString(),
      updated_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString()
    },
    {
      id: 2,
      binder_id: 2,
      title: 'Notes physiologie cardiaque',
      content: '# Physiologie Cardiaque\n\nLe coeur est une double pompe musculaire auto-excitée.\n\nLe cycle cardiaque comprend deux phases majeures :\n1. **La systole** : phase de contraction et d\'éjection du sang.\n2. **La diastole** : phase de relâchement et de remplissage des cavités.\n\nLa pression artérielle moyenne ($PAM$) peut être estimée par :\n$$PAM \\approx PAD + \\frac{1}{3}(PAS - PAD)$$',
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(),
      updated_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString()
    },
    {
      id: 3,
      binder_id: null,
      title: 'Idées de projet de groupe',
      content: '# Projet de Web Mobile\n\nIdées pour le projet de fin d\'année :\n* Une application de covoiturage pour étudiants.\n* **StudyHub** : Une plateforme tout-en-un avec flashcards, notes, diagrammes et PDFs (sélectionné !).',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
  ])

  const loading = ref(false)

  async function fetchNotes() {
    loading.value = true
    return new Promise<Note[]>((resolve) => {
      setTimeout(() => {
        loading.value = false
        resolve(notes.value)
      }, 500)
    })
  }

  async function fetchNoteById(id: number) {
    loading.value = true
    return new Promise<Note | undefined>((resolve) => {
      setTimeout(() => {
        loading.value = false
        resolve(notes.value.find(n => n.id === id))
      }, 300)
    })
  }

  async function createNote(title: string, content: string = '', binderId: number | null = null) {
    loading.value = true
    return new Promise<Note>((resolve) => {
      setTimeout(() => {
        const newNote: Note = {
          id: notes.value.length ? Math.max(...notes.value.map(n => n.id)) + 1 : 1,
          binder_id: binderId,
          title,
          content,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        notes.value.push(newNote)
        loading.value = false
        resolve(newNote)
      }, 600)
    })
  }

  async function updateNote(id: number, title: string, content: string) {
    return new Promise<Note>((resolve, reject) => {
      setTimeout(() => {
        const index = notes.value.findIndex(n => n.id === id)
        if (index !== -1) {
          notes.value[index] = {
            ...notes.value[index],
            title,
            content,
            updated_at: new Date().toISOString()
          }
          resolve(notes.value[index])
        } else {
          reject(new Error('Note introuvable'))
        }
      }, 400)
    })
  }

  async function deleteNote(id: number) {
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        notes.value = notes.value.filter(n => n.id !== id)
        resolve()
      }, 400)
    })
  }

  return {
    notes,
    loading,
    fetchNotes,
    fetchNoteById,
    createNote,
    updateNote,
    deleteNote
  }
})
