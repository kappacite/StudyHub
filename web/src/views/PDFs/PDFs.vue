<template>
  <div class="space-y-6 animate-fade-in">
    <!-- View 1: Documents List -->
    <template v-if="!activePdf">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-xl font-bold">Mes Documents PDF</h1>
          <p class="text-xs text-slate-400 dark:text-slate-500 mt-1">Importez, lisez et organisez vos supports de cours au format PDF</p>
        </div>

        <div class="flex items-center gap-3">
          <input
            type="file"
            ref="fileInputRef"
            class="hidden"
            accept="application/pdf,.pdf"
            @change="handleFileUpload"
          />
          <button
            @click="triggerFileInput"
            :disabled="uploading"
            class="inline-flex items-center gap-2 px-4 py-2 border border-transparent rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition-all shadow-lg shadow-indigo-600/15 disabled:opacity-50"
          >
            <Loader2 v-if="uploading" class="w-4 h-4 animate-spin" />
            <Plus v-else class="w-4 h-4" />
            {{ uploading ? 'Import en cours…' : 'Importer un PDF' }}
          </button>
        </div>
      </div>

      <!-- Tag Filter Bar -->
      <div class="flex flex-wrap items-center gap-2 rounded-2xl border border-slate-100 bg-white p-3 dark:border-slate-800 dark:bg-slate-900 shadow-sm">
        <span class="text-xs font-bold uppercase tracking-wider text-slate-400 mr-1">Filtrer par tag</span>
        <button
          type="button"
          class="rounded-xl px-3 py-1.5 text-xs font-bold transition-all active:scale-95"
          :class="selectedTagId === null ? 'bg-indigo-600 text-white' : 'bg-slate-50 text-slate-500 dark:bg-slate-800 dark:text-slate-350 hover:bg-slate-100 dark:hover:bg-slate-700'"
          @click="filterByTag(null)"
        >
          Tous
        </button>
        <button
          v-for="tag in tagsStore.tags"
          :key="tag.id"
          type="button"
          class="rounded-xl px-3 py-1.5 text-xs font-bold transition-all active:scale-95"
          :style="selectedTagId === tag.id ? { backgroundColor: tag.color || '#4F46E5', color: '#fff' } : undefined"
          :class="selectedTagId === tag.id ? '' : 'bg-slate-50 text-slate-500 dark:bg-slate-800 dark:text-slate-350 hover:bg-slate-100 dark:hover:bg-slate-700'"
          @click="filterByTag(tag.id)"
        >
          {{ tag.name }}
        </button>
      </div>

      <!-- Loading -->
      <div v-if="pdfStore.loading" class="flex items-center justify-center py-16">
        <Loader2 class="w-8 h-8 text-indigo-500 animate-spin" />
      </div>

      <!-- PDF Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="pdf in filteredPdfs"
          :key="pdf.id"
          class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-5 shadow-sm hover:shadow-md transition-all duration-200 group flex flex-col justify-between"
        >
          <div>
            <div class="flex items-start justify-between gap-3">
              <span
                v-if="pdf.read_only"
                class="inline-flex items-center px-2 py-1 rounded-lg text-[9px] font-bold text-amber-600 bg-amber-50 dark:bg-amber-950/30 dark:text-amber-400 uppercase tracking-wider"
              >
                Cours partagé
              </span>
              <span v-else class="inline-flex items-center px-2 py-1 rounded-lg text-[9px] font-bold text-slate-500 bg-slate-50 dark:bg-slate-800 dark:text-slate-400 uppercase tracking-wider">
                PDF
              </span>
              <div v-if="!pdf.read_only" class="flex items-center gap-1 opacity-0 group-hover:opacity-100">
                <button
                  @click.stop="openEditPdfModal(pdf)"
                  class="p-1.5 text-slate-400 hover:text-indigo-600 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-all"
                  title="Modifier le document"
                >
                  <PenLine class="w-4 h-4" />
                </button>
                <button
                  @click.stop="deletePdf(pdf.id)"
                  class="p-1.5 text-slate-400 hover:text-rose-500 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-all"
                  title="Supprimer le document"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>

            <!-- PDF icon & details -->
            <div class="flex items-center gap-4 mt-4">
              <div class="w-12 h-14 rounded-xl bg-rose-50 dark:bg-rose-950/30 text-rose-500 flex items-center justify-center border border-rose-100/50 dark:border-rose-900/30 flex-shrink-0">
                <FileText class="w-6 h-6" />
              </div>
              <div class="min-w-0 flex-1">
                <h3 class="font-bold text-sm text-slate-800 dark:text-slate-100 truncate">{{ pdf.name }}</h3>
                <div v-if="pdf.tags?.length" class="mt-1 flex flex-wrap gap-1">
                  <TagBadge v-for="tag in pdf.tags" :key="tag.id" :tag="tag" />
                </div>
                <p class="text-[10px] text-slate-400 mt-0.5">Ajouté le {{ new Date(pdf.created_at).toLocaleDateString('fr-FR') }}</p>
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
          v-if="filteredPdfs.length === 0"
          class="col-span-full border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-3xl p-12 flex flex-col items-center justify-center text-center text-slate-400"
        >
          <FileText class="w-12 h-12 text-slate-300 dark:text-slate-700 mb-3" />
          <h4 class="font-bold text-slate-800 dark:text-slate-200">Aucun PDF disponible</h4>
          <p class="text-xs mt-1">Importez vos premiers PDF de cours.</p>
        </div>
      </div>
    </template>

    <!-- View 2: PDF Reader -->
    <template v-else>
      <div class="flex items-center gap-2 text-sm font-semibold border-b border-slate-100 dark:border-slate-800 pb-4">
        <button
          @click="pdfStore.closePdf"
          class="text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400"
        >
          Documents
        </button>
        <ChevronRight class="w-4 h-4 text-slate-400" />
        <span class="text-slate-800 dark:text-white font-bold truncate max-w-[200px]">{{ activePdf?.name }}</span>
      </div>

      <div class="mt-6">
        <PdfReader />
      </div>
    </template>

    <!-- Edit PDF Modal -->
    <div v-if="showEditPdfModal" class="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div class="absolute inset-0 bg-slate-950/40 backdrop-blur-sm" @click="showEditPdfModal = false"></div>
      <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-3xl w-full max-w-md p-6 relative z-10 shadow-2xl animate-scale-up">
        <h3 class="text-lg font-bold mb-4">Modifier le document PDF</h3>
        <form @submit.prevent="submitPdfForm">
          <div class="space-y-4">
            <div>
              <label for="pdf-name" class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Nom du document</label>
              <input id="pdf-name" type="text" required v-model="pdfForm.name" class="block w-full px-4 py-3 bg-slate-50 border border-slate-200 dark:bg-slate-800/40 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-medium" />
            </div>
            <div>
              <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Tags</label>
              <TagSelector v-model="pdfForm.tags" />
            </div>
          </div>
          <div class="flex items-center justify-end gap-3 mt-6">
            <button type="button" @click="showEditPdfModal = false" class="px-4 py-2 text-sm font-semibold rounded-xl text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800">Annuler</button>
            <button type="submit" :disabled="savingEdit" class="px-4 py-2 text-sm font-semibold rounded-xl text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50">Enregistrer</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, Eye, Trash2, FileText, ChevronRight, PenLine, Loader2 } from '@lucide/vue'
import { storeToRefs } from 'pinia'
import { usePdfStore, type PdfDocument } from '../../stores/pdf'
import { useTagsStore, type Tag } from '../../stores/tags'
import PdfReader from '../../components/pdf/PdfReader.vue'
import TagSelector from '../../components/ui/TagSelector.vue'
import TagBadge from '../../components/ui/TagBadge.vue'

const pdfStore = usePdfStore()
const tagsStore = useTagsStore()
const { pdfs, activePdf } = storeToRefs(pdfStore)
const fileInputRef = ref<HTMLInputElement | null>(null)

const selectedTagId = ref<number | null>(null)
const showEditPdfModal = ref(false)
const uploading = ref(false)
const savingEdit = ref(false)
const pdfForm = ref<{ id: string; name: string; tags: Tag[] }>({ id: '', name: '', tags: [] })

onMounted(async () => {
  await Promise.all([tagsStore.fetchTags(), pdfStore.fetchPdfs()])
})

const filteredPdfs = computed(() => {
  if (selectedTagId.value === null) return pdfs.value
  return pdfs.value.filter(pdf => pdf.tags && pdf.tags.some(t => t.id === selectedTagId.value))
})

function filterByTag(tagId: number | null) {
  selectedTagId.value = tagId
}

function openEditPdfModal(pdf: PdfDocument) {
  pdfForm.value = { id: pdf.id, name: pdf.name, tags: pdf.tags || [] }
  showEditPdfModal.value = true
}

async function submitPdfForm() {
  savingEdit.value = true
  try {
    await pdfStore.renamePdf(pdfForm.value.id, pdfForm.value.name.trim())
    const tags = await tagsStore.setTagsForEntity('pdfs', pdfForm.value.id, pdfForm.value.tags.map(t => t.id))
    pdfStore.setPdfTags(pdfForm.value.id, tags)
    showEditPdfModal.value = false
  } catch {
    alert("Impossible d'enregistrer les modifications.")
  } finally {
    savingEdit.value = false
  }
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

async function openPdf(pdf: PdfDocument) {
  await pdfStore.openPdf(pdf.id)
}

async function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  if (!target.files || target.files.length === 0) return
  const file = target.files[0]
  uploading.value = true
  try {
    await pdfStore.uploadPdf(file, file.name)
  } catch {
    alert("L'import du PDF a échoué. Vérifiez que le fichier est un PDF valide.")
  } finally {
    uploading.value = false
    target.value = ''
  }
}

async function deletePdf(id: string) {
  if (!confirm('Voulez-vous supprimer ce document ?')) return
  try {
    await pdfStore.removePdf(id)
  } catch {
    alert('Suppression impossible.')
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
</style>
