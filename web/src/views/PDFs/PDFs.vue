<template>
  <div class="space-y-6 animate-fade-in">
    <!-- View 1: Documents List -->
    <template v-if="!activePdf">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-xl font-bold">Mes Documents PDF</h1>
          <p class="text-xs text-slate-400 dark:text-slate-500 mt-1">Importez, lisez et annotez vos supports de cours au format PDF</p>
        </div>
        
        <div class="flex items-center gap-3">
          <input 
            type="file" 
            ref="fileInputRef" 
            class="hidden" 
            accept=".pdf"
            @change="handleFileUpload"
          />
          <button 
            @click="triggerFileInput"
            class="inline-flex items-center gap-2 px-4 py-2 border border-transparent rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition-all shadow-lg shadow-indigo-600/15"
          >
            <Plus class="w-4 h-4" />
            Importer un PDF
          </button>
        </div>
      </div>

      <!-- PDF Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="pdf in pdfs" 
          :key="pdf.id"
          class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-5 shadow-sm hover:shadow-md transition-all duration-200 group flex flex-col justify-between"
        >
          <div>
            <div class="flex items-start justify-between gap-3">
              <span class="inline-flex items-center px-2 py-1 rounded-lg text-[9px] font-bold text-slate-500 bg-slate-50 dark:bg-slate-800 dark:text-slate-400 uppercase tracking-wider">
                {{ pdf.size }}
              </span>
              <button 
                @click.stop="deletePdf(pdf.id)" 
                class="opacity-0 group-hover:opacity-100 p-1.5 text-slate-400 hover:text-rose-500 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-all"
                title="Supprimer le document"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>

            <!-- PDF icon & details -->
            <div class="flex items-center gap-4 mt-4">
              <div class="w-12 h-14 rounded-xl bg-rose-50 dark:bg-rose-950/30 text-rose-500 flex items-center justify-center border border-rose-100/50 dark:border-rose-900/30 flex-shrink-0">
                <FileText class="w-6 h-6" />
              </div>
              <div class="min-w-0">
                <h3 class="font-bold text-sm text-slate-800 dark:text-slate-100 truncate">{{ pdf.name }}</h3>
                <p class="text-[10px] text-slate-400 mt-0.5">Ajouté le {{ new Date(pdf.created_at).toLocaleDateString('fr-FR') }}</p>
                <p class="text-[10px] text-indigo-500 dark:text-indigo-400 font-semibold uppercase tracking-wider mt-1">{{ pdf.annotations.length }} annotations</p>
              </div>
            </div>
          </div>

          <div class="mt-6 pt-4 border-t border-slate-50 dark:border-slate-800/50">
            <button 
              @click="openPdf(pdf)"
              class="w-full px-4 py-2 border border-slate-200 dark:border-slate-850 rounded-xl text-xs font-bold text-slate-700 hover:bg-slate-50 dark:text-slate-200 dark:hover:bg-slate-800 transition-colors active:scale-95 flex items-center justify-center gap-1.5"
            >
              <Eye class="w-4 h-4" />
              Ouvrir le document
            </button>
          </div>
        </div>

        <div 
          v-if="pdfs.length === 0" 
          class="col-span-full border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-3xl p-12 flex flex-col items-center justify-center text-center text-slate-400"
        >
          <FileText class="w-12 h-12 text-slate-300 dark:text-slate-700 mb-3" />
          <h4 class="font-bold text-slate-800 dark:text-slate-200">Aucun PDF disponible</h4>
          <p class="text-xs mt-1">Glissez-déposez ou importez vos premiers PDF de cours.</p>
        </div>
      </div>
    </template>

    <!-- View 2: PDF Interactive Reader & Annotator -->
    <template v-else>
      <!-- Navigation / Controls -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 dark:border-slate-800 pb-4">
        <div class="flex items-center gap-2 text-sm font-semibold">
          <button 
            @click="activePdf = null" 
            class="text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400"
          >
            Documents
          </button>
          <ChevronRight class="w-4 h-4 text-slate-400" />
          <span class="text-slate-800 dark:text-white font-bold truncate max-w-[200px]">{{ activePdf.name }}</span>
        </div>

        <!-- Toolbar Reader Controls -->
        <div class="flex items-center gap-3 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 px-3 py-1.5 rounded-xl shadow-sm">
          <button @click="prevPage" :disabled="currentPage === 1" class="p-1 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg disabled:opacity-40">
            <ChevronLeft class="w-4 h-4" />
          </button>
          <span class="text-xs font-bold px-1 select-none">Page {{ currentPage }} / {{ activePdf.pages.length }}</span>
          <button @click="nextPage" :disabled="currentPage === activePdf.pages.length" class="p-1 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg disabled:opacity-40">
            <ChevronRight class="w-4 h-4" />
          </button>
          
          <div class="h-4 w-[1px] bg-slate-200 dark:bg-slate-800"></div>

          <button @click="zoomIn" class="p-1 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg">
            <ZoomIn class="w-4 h-4" />
          </button>
          <span class="text-xs font-bold select-none">{{ zoom }}%</span>
          <button @click="zoomOut" class="p-1 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg">
            <ZoomOut class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- Document Split Pane (Visualizer + Annotator) -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        <!-- Visualizer Area (8 cols) -->
        <div class="lg:col-span-8 flex justify-center bg-slate-100 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-850 p-6 rounded-3xl overflow-auto min-h-[500px]">
          <!-- Simulated A4 Paper page rendering -->
          <div 
            class="bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 shadow-lg border border-slate-100 dark:border-slate-800/80 p-12 transition-transform duration-200 transform origin-top max-w-[800px] w-full min-h-[600px] flex flex-col justify-between relative"
            :style="{ transform: `scale(${zoom / 100})` }"
          >
            <!-- Watermark/Header of simulated page -->
            <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3 mb-6 text-[10px] text-slate-400 font-semibold uppercase tracking-wider select-none">
              <span>{{ activePdf.name }}</span>
              <span>Page {{ currentPage }}</span>
            </div>

            <!-- Page Rich Text Content -->
            <div class="flex-1 space-y-4 prose prose-slate max-w-none dark:prose-invert">
              <h2 class="text-lg font-bold text-slate-950 dark:text-white leading-tight">
                {{ activePageContent.title }}
              </h2>
              <div 
                v-html="activePageContent.body" 
                class="text-xs leading-relaxed space-y-3"
              ></div>
            </div>

            <!-- Footer of simulated page -->
            <div class="border-t border-slate-100 dark:border-slate-800 pt-3 mt-8 flex items-center justify-between text-[10px] text-slate-400 font-semibold uppercase tracking-wider select-none">
              <span>StudyHub PDF Reader</span>
              <span>Série 2026</span>
            </div>

            <!-- Visual annotation pin (simulation) -->
            <div 
              v-for="pin in currentPageAnnotations" 
              :key="pin.id"
              class="absolute w-6 h-6 rounded-full bg-indigo-600/90 text-white flex items-center justify-center font-bold text-[10px] shadow shadow-indigo-600/30 animate-pulse border-2 border-white select-none cursor-pointer"
              :style="{ top: `${pin.y}%`, left: `${pin.x}%` }"
              :title="pin.text"
            >
              {{ pin.id }}
            </div>
          </div>
        </div>

        <!-- Annotator Panel (4 cols) -->
        <div class="lg:col-span-4 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm space-y-6">
          <div>
            <h3 class="font-bold text-sm text-slate-800 dark:text-white">Annotations & Notes</h3>
            <p class="text-[11px] text-slate-400 mt-0.5">Prenez des notes rattachées directement à ce document</p>
          </div>

          <!-- Add annotation form -->
          <form @submit.prevent="addAnnotation" class="space-y-3">
            <textarea 
              v-model="newAnnotationText"
              rows="3"
              required
              placeholder="Rédiger une annotation..."
              class="w-full p-3 text-xs bg-slate-50 border border-slate-200 dark:bg-slate-800/40 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-medium transition-all"
            ></textarea>
            <button 
              type="submit"
              class="w-full px-4 py-2 border border-transparent rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition-all text-center active:scale-95 shadow-md shadow-indigo-600/10"
            >
              Épingler à la page
            </button>
          </form>

          <!-- Annotations List -->
          <div class="space-y-3">
            <h4 class="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Liste des notes</h4>
            <div class="space-y-2 max-h-[220px] overflow-y-auto pr-1">
              <div 
                v-for="anno in activePdf.annotations" 
                :key="anno.id"
                class="p-3 bg-slate-50 dark:bg-slate-850/40 border border-slate-100 dark:border-slate-800 rounded-2xl flex items-start justify-between gap-3 group"
              >
                <div>
                  <div class="flex items-center gap-1.5">
                    <span class="inline-flex items-center justify-center w-4 h-4 rounded-full bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400 text-[9px] font-bold">
                      {{ anno.id }}
                    </span>
                    <span class="text-[9px] font-semibold text-slate-400 uppercase tracking-wider">Page {{ anno.page }}</span>
                  </div>
                  <p class="text-[11px] text-slate-700 dark:text-slate-300 mt-1 leading-relaxed">{{ anno.text }}</p>
                </div>
                <button 
                  @click="deleteAnnotation(anno.id)" 
                  class="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-500 rounded hover:bg-rose-50 dark:hover:bg-rose-950/20"
                  title="Supprimer"
                >
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
              </div>

              <div 
                v-if="activePdf.annotations.length === 0" 
                class="text-center py-6 text-slate-400 text-xs font-semibold uppercase tracking-wider"
              >
                Aucune annotation
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Plus, Eye, Trash2, FileText, ChevronLeft, ChevronRight, ZoomIn, ZoomOut } from '@lucide/vue'

interface Annotation {
  id: number
  page: number
  text: string
  x: number // position X en pourcentage sur le document
  y: number // position Y
}

interface PageContent {
  title: string
  body: string
}

interface PdfDocument {
  id: number
  name: string
  size: string
  created_at: string
  pages: PageContent[]
  annotations: Annotation[]
}

const fileInputRef = ref<HTMLInputElement | null>(null)

function triggerFileInput() {
  fileInputRef.value?.click()
}
const activePdf = ref<PdfDocument | null>(null)
const currentPage = ref(1)
const zoom = ref(100)
const newAnnotationText = ref('')

const pdfs = ref<PdfDocument[]>([
  {
    id: 1,
    name: 'Cours d\'Optique Géométrique L1.pdf',
    size: '2.4 Mo',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 14).toISOString(),
    pages: [
      { 
        title: 'Chapitre 1 : Les lois de Snell-Descartes', 
        body: '<p>L\'optique géométrique repose sur l\'approximation que la longueur d\'onde de la lumière est négligeable devant les dimensions des obstacles.</p><h3>Loi de la Réflexion</h3><p>Le rayon réfléchi appartient au plan d\'incidence et l\'angle de réflexion est égal à l\'angle d\'incidence : <strong>i1 = i\'1</strong>.</p><h3>Loi de la Réfraction</h3><p>Les indices de réfraction n1 et n2 et les angles d\'incidence i1 et de réfraction i2 sont liés par la relation : <strong>n1 * sin(i1) = n2 * sin(i2)</strong>.</p>' 
      },
      { 
        title: 'Chapitre 2 : Systèmes centrés et approximation de Gauss', 
        body: '<p>Un système optique est dit centré s\'il possède un axe de symétrie de révolution appelé axe optique.</p><h3>Conditions de Gauss</h3><p>Pour obtenir des images nettes (stigmatisme approché), les conditions de Gauss doivent être respectées :</p><ul><li>Les rayons incidents doivent être peu inclinés sur l\'axe optique.</li><li>Les rayons doivent couper l\'axe optique à proximité immédiate du centre optique.</li></ul>' 
      }
    ],
    annotations: [
      { id: 1, page: 1, text: 'Important : Formule n1 sin(i1) = n2 sin(i2) à retenir par cœur !', x: 25, y: 70 },
      { id: 2, page: 2, text: 'Définition à réviser pour le DS.', x: 40, y: 35 }
    ]
  },
  {
    id: 2,
    name: 'TD Biochimie - Cycle de Krebs.pdf',
    size: '1.8 Mo',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(),
    pages: [
      {
        title: 'Exercice 1 : Réactions enzymatiques du cycle',
        body: '<p>Le cycle de Krebs est une série de réactions chimiques utilisées par tous les organismes aérobies pour générer de l\'énergie par l\'oxydation de l\'acétate.</p><p>1. Expliquez le rôle de la citrate synthase dans l\'étape d\'assemblage initial.</p><p>2. Donnez le bilan énergétique global du cycle en termes d\'équivalents ATP.</p>'
      }
    ],
    annotations: []
  }
])

const activePageContent = computed(() => {
  if (!activePdf.value) return { title: '', body: '' }
  return activePdf.value.pages[currentPage.value - 1] || { title: '', body: '' }
})

const currentPageAnnotations = computed(() => {
  if (!activePdf.value) return []
  return activePdf.value.annotations.filter(a => a.page === currentPage.value)
})

function openPdf(pdf: PdfDocument) {
  activePdf.value = pdf
  currentPage.value = 1
  zoom.value = 100
}

function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    const file = target.files[0]
    
    // Simulate creating a new PDF entry
    const newPdf: PdfDocument = {
      id: pdfs.value.length ? Math.max(...pdfs.value.map(p => p.id)) + 1 : 1,
      name: file.name,
      size: `${(file.size / (1024 * 1024)).toFixed(1)} Mo`,
      created_at: new Date().toISOString(),
      pages: [
        { 
          title: 'Document importé : Page 1', 
          body: `<p>Contenu simulé pour le document <strong>${file.name}</strong>.</p><p>Pour brancher les fichiers réels, Capacitor/Filesystem ou l'API REST permettront de charger les données réelles du fichier PDF.</p>`
        }
      ],
      annotations: []
    }
    
    pdfs.value.push(newPdf)
  }
}

function deletePdf(id: number) {
  if (confirm('Voulez-vous supprimer ce document ?')) {
    pdfs.value = pdfs.value.filter(p => p.id !== id)
    if (activePdf.value?.id === id) activePdf.value = null
  }
}

// Reader actions
function nextPage() {
  if (activePdf.value && currentPage.value < activePdf.value.pages.length) {
    currentPage.value++
  }
}

function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

function zoomIn() {
  if (zoom.value < 150) zoom.value += 10
}

function zoomOut() {
  if (zoom.value > 70) zoom.value -= 10
}

// Annotations
function addAnnotation() {
  if (!activePdf.value || !newAnnotationText.value.trim()) return

  const list = activePdf.value.annotations
  const newId = list.length ? Math.max(...list.map(a => a.id)) + 1 : 1
  
  // Random placement on screen for simulation
  const mockX = Math.floor(Math.random() * 40) + 20
  const mockY = Math.floor(Math.random() * 50) + 30

  const newAnno: Annotation = {
    id: newId,
    page: currentPage.value,
    text: newAnnotationText.value.trim(),
    x: mockX,
    y: mockY
  }

  activePdf.value.annotations.push(newAnno)
  newAnnotationText.value = ''
}

function deleteAnnotation(id: number) {
  if (activePdf.value) {
    activePdf.value.annotations = activePdf.value.annotations.filter(a => a.id !== id)
  }
}
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.rotate-y-180 {
  transform: rotateY(180deg);
}

.backface-hidden {
  backface-visibility: hidden;
}

.slide-up-enter-active {
  transition: opacity 0.3s ease, transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-up-enter-from {
  opacity: 0;
  transform: translateY(15px);
}
</style>
