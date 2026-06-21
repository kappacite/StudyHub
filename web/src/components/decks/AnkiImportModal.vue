<template>
  <Transition name="fade-backdrop">
    <div 
      v-if="isOpen" 
      class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 no-print"
      @click.self="close"
    >
      <Transition name="scale-up">
        <div 
          v-if="isOpen"
          class="w-full max-w-md bg-surface dark:bg-[#111827] rounded-2xl shadow-2xl border border-line dark:border-line flex flex-col overflow-hidden max-h-[90vh]"
          @click.stop
        >
          <!-- Header -->
          <div class="flex items-center justify-between px-5 py-4 border-b border-line dark:border-line">
            <span class="font-bold text-base text-ink dark:text-ink-subtle">Importer depuis Anki</span>
            <button 
              @click="close" 
              class="p-1 rounded-lg text-ink-subtle hover:text-ink-muted dark:hover:text-ink-subtle hover:bg-surface-soft dark:hover:bg-surface-soft transition-colors"
            >
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- Body -->
          <div class="flex-1 overflow-y-auto p-5 space-y-4">
            <!-- Summary Result State -->
            <div v-if="result" class="space-y-4">
              <div class="p-4 bg-success-soft dark:bg-success-soft text-success dark:text-success rounded-xl border border-success dark:border-success text-center space-y-1">
                <p class="font-bold text-sm">Importation réussie ! 🎉</p>
                <p class="text-xs">Le deck <span class="font-bold">{{ result.deck_name }}</span> a été créé avec succès.</p>
              </div>

              <!-- Stats -->
              <div class="grid grid-cols-2 gap-4">
                <div class="bg-surface-soft dark:bg-surface-soft p-3 rounded-xl border border-line dark:border-line text-center">
                  <p class="text-[10px] uppercase font-bold text-ink-subtle">Cartes importées</p>
                  <p class="text-2xl font-extrabold text-primary dark:text-primary mt-1">{{ result.cards_imported }}</p>
                </div>
                <div class="bg-surface-soft dark:bg-surface-soft p-3 rounded-xl border border-line dark:border-line text-center">
                  <p class="text-[10px] uppercase font-bold text-ink-subtle">Cartes ignorées</p>
                  <p class="text-2xl font-extrabold text-ink-muted mt-1">{{ result.cards_skipped }}</p>
                </div>
              </div>

              <!-- Warnings -->
              <div v-if="result.warnings && result.warnings.length > 0" class="space-y-2">
                <p class="text-xs font-bold text-warning dark:text-warning uppercase tracking-wider">Avertissements ({{ result.warnings.length }})</p>
                <div class="bg-warning-soft dark:bg-warning-soft border border-warning dark:border-warning rounded-xl p-3 max-h-36 overflow-y-auto space-y-1">
                  <p v-for="(warn, i) in result.warnings" :key="i" class="text-xs text-warning dark:text-warning flex items-start gap-1.5">
                    <span class="text-[8px] mt-1.5">•</span>
                    <span>{{ warn }}</span>
                  </p>
                </div>
              </div>

              <button 
                @click="onSuccessClose" 
                class="w-full py-2.5 bg-primary hover:bg-primary-strong text-white rounded-xl font-bold text-sm shadow-md transition-all active:scale-95 cursor-pointer"
              >
                Fermer
              </button>
            </div>

            <!-- Upload Form State -->
            <div v-else class="space-y-4">
              <!-- Drag & Drop Zone -->
              <div 
                @dragover.prevent="isDragOver = true"
                @dragleave.prevent="isDragOver = false"
                @drop.prevent="handleDrop"
                :class="[
                  'border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all duration-200 flex flex-col items-center justify-center min-h-[160px]',
                  isDragOver 
                    ? 'border-primary bg-primary-soft dark:bg-primary-soft' 
                    : 'border-line hover:border-line dark:border-line dark:hover:border-line'
                ]"
                @click="triggerFileSelect"
              >
                <input 
                  ref="fileInput" 
                  type="file" 
                  accept=".apkg" 
                  class="hidden" 
                  @change="handleFileSelect"
                />
                
                <Upload class="w-10 h-10 text-ink-subtle mb-3" />
                <template v-if="!file">
                  <p class="text-xs font-bold text-ink dark:text-ink-subtle">Glissez-déposez votre fichier .apkg ici</p>
                  <p class="text-[10px] text-ink-subtle dark:text-ink-muted mt-1">ou cliquez pour parcourir (max 50 Mo)</p>
                </template>
                <template v-else>
                  <p class="text-xs font-bold text-primary dark:text-primary truncate max-w-full px-4">{{ file.name }}</p>
                  <p class="text-[10px] text-ink-subtle dark:text-ink-muted mt-1">{{ formatFileSize(file.size) }}</p>
                </template>
              </div>

              <!-- Destination Binder Selector -->
              <div class="space-y-1.5">
                <label class="text-xs font-bold text-ink-muted dark:text-ink-subtle uppercase tracking-wider">Classeur de destination (Optionnel)</label>
                <select 
                  v-model="selectedBinderId"
                  class="w-full rounded-xl border border-line dark:border-line bg-surface dark:bg-surface-soft px-3 py-2 text-xs font-semibold text-ink dark:text-ink-subtle outline-none focus:border-primary"
                >
                  <option :value="null">Aucun classeur</option>
                  <option v-for="binder in bindersStore.binders" :key="binder.id" :value="binder.id">
                    {{ binder.name }}
                  </option>
                </select>
              </div>

              <!-- Error Display -->
              <div v-if="error" class="p-3 bg-danger-soft dark:bg-danger-soft text-danger dark:text-danger rounded-xl text-xs font-semibold border border-danger dark:border-danger">
                {{ error }}
              </div>

              <!-- Submit Button -->
              <button 
                @click="uploadFile" 
                :disabled="!file || isUploading"
                class="w-full py-2.5 bg-primary hover:bg-primary-strong text-white rounded-xl font-bold text-sm shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 cursor-pointer transition-all active:scale-95"
              >
                <Loader2 v-if="isUploading" class="w-4 h-4 animate-spin" />
                <span>{{ isUploading ? 'Importation en cours...' : 'Démarrer l\'importation' }}</span>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { X, Upload, Loader2 } from '@lucide/vue'
import { useBindersStore } from '../../stores/binders'
import { useDecksStore } from '../../stores/decks'

const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'success', deckId: number): void
}>()

const bindersStore = useBindersStore()
const decksStore = useDecksStore()

const fileInput = ref<HTMLInputElement | null>(null)
const file = ref<File | null>(null)
const isDragOver = ref(false)
const selectedBinderId = ref<string | null>(null)
const isUploading = ref(false)
const error = ref<string | null>(null)

interface ImportResult {
  deck_id: number
  deck_name: string
  cards_imported: number
  cards_skipped: number
  warnings: string[]
}

const result = ref<ImportResult | null>(null)

onMounted(() => {
  bindersStore.fetchBinders()
})

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    file.value = null
    selectedBinderId.value = null
    error.value = null
    result.value = null
    bindersStore.fetchBinders()
  }
})

function close() {
  emit('close')
}

function onSuccessClose() {
  const deckId = result.value?.deck_id
  close()
  if (deckId) {
    emit('success', deckId)
  }
}

function triggerFileSelect() {
  fileInput.value?.click()
}

function validateFile(selectedFile: File): boolean {
  error.value = null
  
  if (!selectedFile.name.toLowerCase().endsWith('.apkg')) {
    error.value = 'Veuillez sélectionner un fichier au format Anki (.apkg).'
    return false
  }
  
  // Max size 50 MB
  const maxSize = 50 * 1024 * 1024
  if (selectedFile.size > maxSize) {
    error.value = 'Le fichier est trop volumineux (maximum 50 Mo).'
    return false
  }
  
  return true
}

function handleFileSelect(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    const selectedFile = target.files[0]
    if (validateFile(selectedFile)) {
      file.value = selectedFile
    }
  }
}

function handleDrop(e: DragEvent) {
  isDragOver.value = false
  if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
    const selectedFile = e.dataTransfer.files[0]
    if (validateFile(selectedFile)) {
      file.value = selectedFile
    }
  }
}

async function uploadFile() {
  if (!file.value) return
  
  isUploading.value = true
  error.value = null
  
  try {
    const res = await decksStore.importAnki(file.value, selectedBinderId.value)
    result.value = res
  } catch (err: any) {
    console.error(err)
    error.value = err.response?.data?.error?.message || err.message || 'Une erreur est survenue lors de l\'importation.'
  } finally {
    isUploading.value = false
  }
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'Ko', 'Mo', 'Go']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>

<style scoped>
/* Fade Backdrop Animation */
.fade-backdrop-enter-active,
.fade-backdrop-leave-active {
  transition: opacity 0.25s ease;
}
.fade-backdrop-enter-from,
.fade-backdrop-leave-to {
  opacity: 0;
}

/* Scale Up Modal Animation */
.scale-up-enter-active,
.scale-up-leave-active {
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.2s ease;
}
.scale-up-enter-from,
.scale-up-leave-to {
  transform: scale(0.95);
  opacity: 0;
}
</style>
