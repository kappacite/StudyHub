import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'
import type { Tag } from './tags'

export interface PdfDocument {
  id: string
  name: string
  filename: string
  binder_id: string | null
  tags: Tag[]
  read_only: boolean
  created_at: string
  updated_at: string
}

export const usePdfStore = defineStore('pdf', () => {
  const pdfs = ref<PdfDocument[]>([])
  const activePdf = ref<PdfDocument | null>(null)
  // URL blob du fichier réel en cours de lecture (le stream /file est protégé par JWT,
  // on le charge donc en blob via l'instance Axios authentifiée).
  const activePdfUrl = ref<string | null>(null)
  const loading = ref(false)
  const opening = ref(false)

  async function fetchPdfs(tagId: number | null = null) {
    loading.value = true
    try {
      const params: Record<string, string | number> = { per_page: 100 }
      if (tagId !== null) params.tag_id = tagId
      const res = await api.get('/pdfs', { params })
      pdfs.value = res.data.data
    } finally {
      loading.value = false
    }
  }

  async function uploadPdf(file: File, name?: string) {
    const form = new FormData()
    form.append('file', file)
    if (name) form.append('name', name)
    const res = await api.post<PdfDocument>('/pdfs', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    pdfs.value.unshift(res.data)
    return res.data
  }

  async function renamePdf(id: string, name: string) {
    const res = await api.put<PdfDocument>(`/pdfs/${id}`, { name })
    const idx = pdfs.value.findIndex(p => p.id === id)
    if (idx !== -1) pdfs.value[idx] = res.data
    if (activePdf.value?.id === id) activePdf.value = res.data
    return res.data
  }

  async function removePdf(id: string) {
    await api.delete(`/pdfs/${id}`)
    pdfs.value = pdfs.value.filter(p => p.id !== id)
    if (activePdf.value?.id === id) closePdf()
  }

  async function openPdf(id: string) {
    const pdf = pdfs.value.find(p => p.id === id)
    if (!pdf) return
    opening.value = true
    try {
      const res = await api.get(`/pdfs/${id}/file`, { responseType: 'blob' })
      if (activePdfUrl.value) URL.revokeObjectURL(activePdfUrl.value)
      activePdfUrl.value = URL.createObjectURL(res.data as Blob)
      activePdf.value = pdf
    } finally {
      opening.value = false
    }
  }

  function closePdf() {
    if (activePdfUrl.value) {
      URL.revokeObjectURL(activePdfUrl.value)
      activePdfUrl.value = null
    }
    activePdf.value = null
  }

  function setPdfTags(id: string, tags: Tag[]) {
    const idx = pdfs.value.findIndex(p => p.id === id)
    if (idx !== -1) pdfs.value[idx] = { ...pdfs.value[idx], tags }
    if (activePdf.value?.id === id) activePdf.value = { ...activePdf.value, tags }
  }

  return {
    pdfs,
    activePdf,
    activePdfUrl,
    loading,
    opening,
    fetchPdfs,
    uploadPdf,
    renamePdf,
    removePdf,
    openPdf,
    closePdf,
    setPdfTags,
  }
})
