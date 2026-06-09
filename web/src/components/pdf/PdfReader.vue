<template>
  <div class="flex flex-col h-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-3xl p-4 md:p-6 overflow-hidden">
    <!-- Header Reader Toolbar -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-4 no-print select-none">
      <div class="flex items-center gap-2 text-xs font-semibold truncate max-w-xs">
        <span class="text-slate-800 dark:text-white font-bold truncate">{{ pdfStore.activePdf?.name }}</span>
      </div>

      <div class="flex items-center gap-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-3 py-1 rounded-xl shadow-sm">
        <button 
          @click="prevPage" 
          :disabled="pdfStore.currentPage === 1" 
          class="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg disabled:opacity-40"
        >
          <ChevronLeft class="w-4 h-4 text-slate-600 dark:text-slate-350" />
        </button>
        <span class="text-xs font-bold px-1 text-slate-700 dark:text-slate-300">
          Page {{ pdfStore.currentPage }} / {{ pdfStore.activePdf?.pages.length }}
        </span>
        <button 
          @click="nextPage" 
          :disabled="pdfStore.currentPage === pdfStore.activePdf?.pages.length" 
          class="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg disabled:opacity-40"
        >
          <ChevronRight class="w-4 h-4 text-slate-600 dark:text-slate-350" />
        </button>
        
        <div class="h-4 w-[1px] bg-slate-200 dark:bg-slate-800"></div>

        <button @click="zoomIn" class="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg">
          <ZoomIn class="w-4 h-4 text-slate-600 dark:text-slate-350" />
        </button>
        <span class="text-xs font-bold text-slate-700 dark:text-slate-300">{{ pdfStore.zoom }}%</span>
        <button @click="zoomOut" class="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg">
          <ZoomOut class="w-4 h-4 text-slate-600 dark:text-slate-350" />
        </button>
      </div>
    </div>

    <!-- Reader Scrollable Page Container -->
    <div 
      class="flex-1 flex justify-center bg-slate-100 dark:bg-slate-900/60 p-4 md:p-6 overflow-auto mt-4 rounded-2xl relative min-h-[400px]"
      ref="containerRef"
      @mouseup="handleTextSelection"
    >
      <!-- Simulated A4 Paper page rendering -->
      <div 
        class="bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-200 shadow-md border border-slate-200 dark:border-slate-800 p-8 md:p-12 transition-transform duration-200 transform origin-top w-full min-h-[550px] max-w-[650px] flex flex-col justify-between relative select-text"
        :style="{ transform: `scale(${pdfStore.zoom / 100})` }"
        id="pdf-page-container"
      >
        <!-- Page Header -->
        <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2 mb-4 text-[9px] text-slate-400 font-semibold uppercase tracking-wider select-none">
          <span>{{ pdfStore.activePdf?.name }}</span>
          <span>Page {{ pdfStore.currentPage }}</span>
        </div>

        <!-- Page Content -->
        <div class="flex-1 space-y-4 prose prose-slate max-w-none dark:prose-invert">
          <h2 class="text-base font-bold text-slate-950 dark:text-white leading-tight">
            {{ activePageContent.title }}
          </h2>
          <div 
            v-html="activePageContent.body" 
            class="text-xs leading-relaxed space-y-3 pdf-text-select"
          ></div>
        </div>

        <!-- Page Footer -->
        <div class="border-t border-slate-100 dark:border-slate-800 pt-2 mt-6 flex items-center justify-between text-[9px] text-slate-400 font-semibold uppercase tracking-wider select-none">
          <span>StudyHub PDF Reader</span>
          <span>Page {{ pdfStore.currentPage }}</span>
        </div>

        <!-- Visual annotation pins -->
        <div 
          v-for="pin in currentPageAnnotations" 
          :key="pin.id"
          class="absolute w-5 h-5 rounded-full bg-indigo-600/90 text-white flex items-center justify-center font-bold text-[9px] shadow shadow-indigo-600/30 border-2 border-white select-none cursor-pointer hover:scale-110 transition-transform"
          :style="{ top: `${pin.y}%`, left: `${pin.x}%` }"
          :title="pin.text"
        >
          {{ pin.id }}
        </div>
      </div>

      <!-- Floating Cite Button -->
      <div 
        v-if="showCiteButton" 
        class="absolute z-50 flex items-center bg-slate-900 text-white text-xs font-bold rounded-xl shadow-lg border border-slate-800 px-3 py-1.5 gap-1.5 hover:bg-indigo-600 cursor-pointer select-none active:scale-95 transition-all"
        :style="{ top: `${citeButtonY}px`, left: `${citeButtonX}px` }"
        @mousedown.prevent="citeSelectedText"
      >
        <Quote class="w-3.5 h-3.5 text-indigo-400" />
        <span>Citer dans la note</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { usePdfStore } from '../../stores/pdf'
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, Quote } from '@lucide/vue'

const emit = defineEmits(['cite'])

const pdfStore = usePdfStore()
const containerRef = ref<HTMLElement | null>(null)

const showCiteButton = ref(false)
const citeButtonX = ref(0)
const citeButtonY = ref(0)
const selectedText = ref('')

const activePageContent = computed(() => {
  if (!pdfStore.activePdf) return { title: '', body: '' }
  return pdfStore.activePdf.pages[pdfStore.currentPage - 1] || { title: '', body: '' }
})

const currentPageAnnotations = computed(() => {
  if (!pdfStore.activePdf) return []
  return pdfStore.activePdf.annotations.filter(a => a.page === pdfStore.currentPage)
})

function prevPage() {
  if (pdfStore.currentPage > 1) {
    pdfStore.currentPage--
    showCiteButton.value = false
  }
}

function nextPage() {
  if (pdfStore.activePdf && pdfStore.currentPage < pdfStore.activePdf.pages.length) {
    pdfStore.currentPage++
    showCiteButton.value = false
  }
}

function zoomIn() {
  if (pdfStore.zoom < 150) pdfStore.zoom += 10
}

function zoomOut() {
  if (pdfStore.zoom > 70) pdfStore.zoom -= 10
}

function handleTextSelection(event: MouseEvent) {
  const selection = window.getSelection()
  if (selection && selection.toString().trim()) {
    selectedText.value = selection.toString().trim()
    
    // Position du bouton Citer
    if (containerRef.value) {
      const rect = containerRef.value.getBoundingClientRect()
      // Positionner près du clic
      citeButtonX.value = event.clientX - rect.left
      citeButtonY.value = event.clientY - rect.top - 40
      showCiteButton.value = true
    }
  } else {
    showCiteButton.value = false
  }
}

function citeSelectedText() {
  if (!selectedText.value) return
  
  // Générer des coordonnées X/Y simulées pour le deep link
  const mockX = Math.floor(Math.random() * 40) + 30
  const mockY = Math.floor(Math.random() * 50) + 20
  
  emit('cite', {
    text: selectedText.value,
    page: pdfStore.currentPage,
    x: mockX,
    y: mockY
  })
  
  // Masquer la sélection
  window.getSelection()?.removeAllRanges()
  showCiteButton.value = false
}
</script>
