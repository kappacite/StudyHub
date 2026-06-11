import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Tag } from './tags'

export interface Annotation {
  id: number
  page: number
  text: string
  x: number
  y: number
}

export interface PageContent {
  title: string
  body: string
}

export interface PdfDocument {
  id: number
  name: string
  size: string
  created_at: string
  pages: PageContent[]
  annotations: Annotation[]
  tags: Tag[]
}

export const usePdfStore = defineStore('pdf', () => {
  const pdfs = ref<PdfDocument[]>([])

  const activePdf = ref<PdfDocument | null>(null)
  const currentPage = ref(1)
  const zoom = ref(100)
  const isSplitScreenActive = ref(false)

  function openPdf(pdfId: number, page: number = 1) {
    const found = pdfs.value.find(p => p.id === pdfId)
    if (found) {
      activePdf.value = found
      currentPage.value = page
      zoom.value = 100
    }
  }

  function closePdf() {
    activePdf.value = null
    isSplitScreenActive.value = false
  }

  return {
    pdfs,
    activePdf,
    currentPage,
    zoom,
    isSplitScreenActive,
    openPdf,
    closePdf
  }
})
