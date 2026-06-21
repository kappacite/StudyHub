<template>
  <PageContainer>
    <!-- Vue 1 : liste des documents -->
    <template v-if="!activePdf">
      <PageHeader title="Mes Documents PDF" subtitle="Importez, lisez et organisez vos supports de cours au format PDF">
        <template #actions>
          <input
            type="file"
            ref="fileInputRef"
            class="hidden"
            accept="application/pdf,.pdf"
            @change="handleFileUpload"
          />
          <BaseButton :loading="uploading" :disabled="uploading" @click="triggerFileInput">
            <template #icon><Plus v-if="!uploading" class="w-4 h-4" /></template>
            {{ uploading ? 'Import en cours…' : 'Importer un PDF' }}
          </BaseButton>
        </template>
      </PageHeader>

      <!-- Filtre par tags -->
      <div class="flex flex-wrap items-center gap-2 rounded-2xl border border-line bg-surface p-3">
        <span class="text-xs font-bold uppercase tracking-wider text-ink-subtle mr-1">Filtrer par tag</span>
        <button
          type="button"
          class="rounded-full px-3 py-1.5 text-xs font-bold transition-colors"
          :class="selectedTagId === null ? 'bg-primary text-white' : 'bg-surface-soft text-ink-muted'"
          @click="filterByTag(null)"
        >Tous</button>
        <button
          v-for="tag in tagsStore.tags"
          :key="tag.id"
          type="button"
          class="rounded-full px-3 py-1.5 text-xs font-bold transition-colors"
          :style="selectedTagId === tag.id ? { backgroundColor: tag.color || '#F06292', color: '#fff' } : undefined"
          :class="selectedTagId === tag.id ? '' : 'bg-surface-soft text-ink-muted'"
          @click="filterByTag(tag.id)"
        >{{ tag.name }}</button>
      </div>

      <!-- Loading -->
      <div v-if="pdfStore.loading" class="flex items-center justify-center py-16">
        <Loader2 class="w-8 h-8 text-primary animate-spin" />
      </div>

      <!-- Grille PDF -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <BaseCard
          v-for="pdf in filteredPdfs"
          :key="pdf.id"
          padding="sm"
          interactive
          class="flex flex-col justify-between group"
        >
          <div>
            <div class="flex items-start justify-between gap-3">
              <span
                v-if="pdf.read_only"
                class="inline-flex items-center px-2 py-1 rounded-lg text-[9px] font-bold text-warning bg-warning-soft uppercase tracking-wider"
              >Cours partagé</span>
              <span v-else class="inline-flex items-center px-2 py-1 rounded-lg text-[9px] font-bold text-ink-muted bg-surface-soft uppercase tracking-wider">PDF</span>
              <div v-if="!pdf.read_only" class="flex items-center gap-1 opacity-0 group-hover:opacity-100">
                <button
                  @click.stop="openEditPdfModal(pdf)"
                  class="p-1.5 text-ink-subtle hover:text-primary rounded-lg hover:bg-primary-soft transition-all"
                  title="Modifier le document"
                >
                  <PenLine class="w-4 h-4" />
                </button>
                <button
                  @click.stop="deletePdf(pdf.id)"
                  class="p-1.5 text-ink-subtle hover:text-danger rounded-lg hover:bg-danger-soft transition-all"
                  title="Supprimer le document"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>

            <div class="flex items-center gap-4 mt-4">
              <div class="w-12 h-14 rounded-xl bg-cat-pdf-soft text-cat-pdf flex items-center justify-center flex-shrink-0">
                <FileText class="w-6 h-6" />
              </div>
              <div class="min-w-0 flex-1">
                <h3 class="font-bold text-sm text-ink truncate">{{ pdf.name }}</h3>
                <div v-if="pdf.tags?.length" class="mt-1 flex flex-wrap gap-1">
                  <TagBadge v-for="tag in pdf.tags" :key="tag.id" :tag="tag" />
                </div>
                <p class="text-[10px] text-ink-subtle mt-0.5">Ajouté le {{ new Date(pdf.created_at).toLocaleDateString('fr-FR') }}</p>
              </div>
            </div>
          </div>

          <div class="mt-6 pt-4 border-t border-line-soft">
            <BaseButton variant="secondary" size="sm" block @click="openPdf(pdf)">
              <template #icon><Eye class="w-4 h-4" /></template>
              Ouvrir le document
            </BaseButton>
          </div>
        </BaseCard>

        <div
          v-if="filteredPdfs.length === 0"
          class="col-span-full border-2 border-dashed border-line rounded-3xl p-12 flex flex-col items-center justify-center text-center text-ink-subtle"
        >
          <FileText class="w-12 h-12 text-cat-pdf/40 mb-3" />
          <h4 class="font-bold text-ink">Aucun PDF disponible</h4>
          <p class="text-xs mt-1">Importez vos premiers PDF de cours.</p>
        </div>
      </div>
    </template>

    <!-- Vue 2 : lecteur PDF -->
    <template v-else>
      <div class="flex items-center gap-2 text-sm font-semibold border-b border-line pb-4">
        <button
          @click="pdfStore.closePdf"
          class="text-ink-muted hover:text-primary transition-colors"
        >Documents</button>
        <ChevronRight class="w-4 h-4 text-ink-subtle" />
        <span class="text-ink font-bold truncate max-w-[200px]">{{ activePdf?.name }}</span>
      </div>

      <div class="mt-6">
        <PdfReader />
      </div>
    </template>

    <!-- Modale d'édition PDF -->
    <BaseModal :open="showEditPdfModal" title="Modifier le document PDF" @close="showEditPdfModal = false">
      <form @submit.prevent="submitPdfForm" class="space-y-4">
        <BaseField label="Nom du document" for-id="pdf-name">
          <BaseInput id="pdf-name" v-model="pdfForm.name" placeholder="Nom du document" />
        </BaseField>
        <BaseField label="Tags">
          <TagSelector v-model="pdfForm.tags" />
        </BaseField>
        <div class="flex items-center justify-end gap-2 pt-2">
          <BaseButton type="button" variant="ghost" @click="showEditPdfModal = false">Annuler</BaseButton>
          <BaseButton type="submit" :loading="savingEdit">Enregistrer</BaseButton>
        </div>
      </form>
    </BaseModal>
  </PageContainer>
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
import { PageContainer, PageHeader, BaseButton, BaseCard, BaseModal, BaseField, BaseInput } from '../../components/ui/base'

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
