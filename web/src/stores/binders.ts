import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Binder {
  id: number
  parent_id: number | null
  name: string
  created_at: string
}

export const useBindersStore = defineStore('binders', () => {
  const binders = ref<Binder[]>([
    { id: 1, parent_id: null, name: 'Semestre 1', created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30).toISOString() },
    { id: 2, parent_id: null, name: 'Sciences Médicales', created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 20).toISOString() },
    { id: 3, parent_id: 1, name: 'Physique L1', created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 25).toISOString() },
    { id: 4, parent_id: 1, name: 'Mathématiques Algèbre', created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 24).toISOString() },
    { id: 5, parent_id: 2, name: 'Anatomie Cardiaque', created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 15).toISOString() }
  ])

  const loading = ref(false)

  async function fetchBinders() {
    loading.value = true
    return new Promise<Binder[]>((resolve) => {
      setTimeout(() => {
        loading.value = false
        resolve(binders.value)
      }, 400)
    })
  }

  async function createBinder(name: string, parentId: number | null = null) {
    loading.value = true
    return new Promise<Binder>((resolve) => {
      setTimeout(() => {
        const newBinder: Binder = {
          id: binders.value.length ? Math.max(...binders.value.map(b => b.id)) + 1 : 1,
          parent_id: parentId,
          name,
          created_at: new Date().toISOString()
        }
        binders.value.push(newBinder)
        loading.value = false
        resolve(newBinder)
      }, 500)
    })
  }

  async function updateBinder(id: number, name: string) {
    return new Promise<Binder>((resolve, reject) => {
      setTimeout(() => {
        const index = binders.value.findIndex(b => b.id === id)
        if (index !== -1) {
          binders.value[index] = { ...binders.value[index], name }
          resolve(binders.value[index])
        } else {
          reject(new Error('Classeur introuvable'))
        }
      }, 300)
    })
  }

  async function deleteBinder(id: number) {
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        // Supprimer récursivement ou juste orpheliniser les enfants ?
        // Dans une logique propre, on supprime le classeur. Les classeurs enfants de premier niveau sont orphelinisés ou supprimés.
        // Ici, supprimons aussi les sous-dossiers pour rester propre.
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
        resolve()
      }, 400)
    })
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
