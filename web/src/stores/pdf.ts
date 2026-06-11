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
  const pdfs = ref<PdfDocument[]>([
    {
      id: 1,
      name: 'Cours d\'Optique Géométrique L1.pdf',
      size: '2.4 Mo',
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 14).toISOString(),
      pages: [
        { 
          title: 'Chapitre 1 : Les lois de Snell-Descartes', 
          body: '<p class="pdf-text-select">L\'optique géométrique repose sur l\'approximation que la longueur d\'onde de la lumière est négligeable devant les dimensions des obstacles.</p><h3>Loi de la Réflexion</h3><p class="pdf-text-select">Le rayon réfléchi appartient au plan d\'incidence et l\'angle de réflexion est égal à l\'angle d\'incidence : <strong>i1 = i\'1</strong>.</p><h3>Loi de la Réfraction</h3><p class="pdf-text-select">Les indices de réfraction n1 et n2 et les angles d\'incidence i1 et de réfraction i2 sont liés par la relation : <strong>n1 * sin(i1) = n2 * sin(i2)</strong>.</p>' 
        },
        { 
          title: 'Chapitre 2 : Systèmes centrés et approximation de Gauss', 
          body: '<p class="pdf-text-select">Un système optique est dit centré s\'il possède un axe de symétrie de révolution appelé axe optique.</p><h3>Conditions de Gauss</h3><p class="pdf-text-select">Pour obtenir des images nettes (stigmatisme approché), les conditions de Gauss doivent être respectées :</p><ul><li class="pdf-text-select">Les rayons incidents doivent être peu inclinés sur l\'axe optique.</li><li class="pdf-text-select">Les rayons doivent couper l\'axe optique à proximité immédiate du centre optique.</li></ul>' 
        }
      ],
      annotations: [
        { id: 1, page: 1, text: 'Important : Formule n1 sin(i1) = n2 sin(i2) à retenir par cœur !', x: 25, y: 70 },
        { id: 2, page: 2, text: 'Définition à réviser pour le DS.', x: 40, y: 35 }
      ],
      tags: []
    },
    {
      id: 2,
      name: 'TD Biochimie - Cycle de Krebs.pdf',
      size: '1.8 Mo',
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(),
      pages: [
        {
          title: 'Exercice 1 : Réactions enzymatiques du cycle',
          body: '<p class="pdf-text-select">Le cycle de Krebs est une série de réactions chimiques utilisées par tous les organismes aérobies pour générer de l\'énergie par l\'oxydation de l\'acétate.</p><p class="pdf-text-select">1. Expliquez le rôle de la citrate synthase dans l\'étape d\'assemblage initial.</p><p class="pdf-text-select">2. Donnez le bilan énergétique global du cycle en termes d\'équivalents ATP.</p>'
        }
      ],
      annotations: [],
      tags: []
    }
  ])

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
