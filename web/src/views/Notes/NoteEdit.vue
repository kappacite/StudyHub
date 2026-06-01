<template>
  <div class="space-y-6 max-w-4xl mx-auto animate-fade-in print:max-w-full print:p-0 print:space-y-0">
    
    <!-- Top Bar Actions (Hidden when printing) -->
    <div class="flex items-center justify-between no-print">
      <button 
        @click="goBack" 
        class="text-sm font-semibold text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400 flex items-center gap-1"
      >
        <ChevronLeft class="w-4 h-4" />
        Retour aux notes
      </button>

      <div class="flex items-center gap-3">
        <!-- Save Status -->
        <span class="text-xs font-semibold text-slate-400 flex items-center gap-1.5 mr-2">
          <span class="w-2 h-2 rounded-full bg-emerald-500" :class="[isSaving ? 'animate-pulse' : '']"></span>
          {{ saveStatus }}
        </span>

        <!-- View Mode Toggler -->
        <button 
          @click="toggleMode"
          class="inline-flex items-center gap-2 px-4 py-2 border border-slate-200 dark:border-slate-800 rounded-xl text-sm font-semibold hover:bg-slate-50 dark:hover:bg-slate-850 transition-all"
        >
          <component :is="isEditMode ? Eye : Edit3" class="w-4 h-4 text-indigo-500" />
          {{ isEditMode ? 'Aperçu / Lire' : 'Modifier la note' }}
        </button>
        
        <!-- PDF / Print Trigger -->
        <button 
          v-if="!isEditMode"
          @click="printNote"
          class="inline-flex items-center gap-2 px-4 py-2 border border-transparent rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition-all shadow-md shadow-indigo-600/10"
        >
          <FileDown class="w-4 h-4" />
          Exporter en PDF
        </button>

        <button 
          v-if="isEditMode"
          @click="saveNote"
          class="px-4 py-2 text-sm font-semibold rounded-xl text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition-all shadow-md shadow-indigo-600/10"
        >
          Enregistrer
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 gap-3 no-print">
      <svg class="animate-spin h-8 w-8 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="text-sm font-semibold text-slate-400 uppercase tracking-widest">Ouverture de la note...</span>
    </div>

    <div v-else class="space-y-6 print:space-y-0">
      
      <!-- Title & Binder Selection Card (Meta) (Hidden when printing if configured, but keeping clean view) -->
      <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm space-y-4 print:border-none print:shadow-none print:p-0 print:mb-6">
        <input 
          v-if="isEditMode"
          type="text" 
          v-model="title" 
          placeholder="Titre de la note..."
          class="block w-full text-2xl font-bold bg-transparent border-0 border-b border-transparent hover:border-slate-100 focus:border-indigo-500 focus:ring-0 px-0 pb-1.5 focus:outline-none transition-all placeholder-slate-300 dark:placeholder-slate-700"
          @input="triggerAutoSave"
        />
        <h1 v-else class="text-3xl font-extrabold text-slate-900 dark:text-white print:text-black">
          {{ title || 'Note sans titre' }}
        </h1>

        <div class="flex items-center gap-3 no-print">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Associer au classeur :</span>
          <select 
            v-if="isEditMode"
            v-model="binderId"
            class="px-3 py-1.5 bg-slate-50 border border-slate-200 dark:bg-slate-800/40 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-xs font-semibold transition-all"
            @change="triggerAutoSave"
          >
            <option :value="null">Général (Aucun)</option>
            <option v-for="b in bindersStore.binders" :key="b.id" :value="b.id">{{ b.name }}</option>
          </select>
          <span v-else class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-bold text-indigo-500 bg-indigo-50 dark:bg-indigo-950/40 dark:text-indigo-400 uppercase tracking-wider">
            {{ getBinderName(binderId) }}
          </span>
        </div>
      </div>

      <!-- WORKSPACE 1: EDIT MODE -->
      <div v-if="isEditMode" class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl overflow-hidden shadow-sm flex flex-col min-h-[500px]">
        <!-- Markdown & LaTeX Fast insertion bar -->
        <div class="flex flex-wrap items-center gap-1.5 p-3 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/20">
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2">Formatage</span>
          <button 
            v-for="btn in formatButtons" 
            :key="btn.label" 
            type="button" 
            @click="insertText(btn.prefix, btn.suffix)"
            class="p-2 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:text-indigo-600 hover:bg-white dark:hover:bg-slate-800 rounded-lg transition-all"
            :title="btn.label"
          >
            {{ btn.label }}
          </button>
          
          <div class="h-4 w-[1px] bg-slate-200 dark:bg-slate-800 mx-2"></div>
          
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2">LaTeX</span>
          <button 
            v-for="btn in latexButtons" 
            :key="btn.label" 
            type="button" 
            @click="insertText(btn.prefix, btn.suffix)"
            class="p-2 text-xs font-mono font-bold text-slate-600 dark:text-slate-300 hover:text-indigo-600 hover:bg-white dark:hover:bg-slate-800 rounded-lg transition-all"
            :title="btn.label"
          >
            {{ btn.label }}
          </button>
        </div>

        <!-- Raw Markdown Text Area -->
        <textarea 
          ref="textareaRef"
          v-model="content"
          placeholder="Rédigez en Markdown et LaTeX. Par exemple : \n\n# Titre\nLe premier principe s'écrit :\n$$\\Delta U = Q + W$$\n\nEt en ligne : $\\Delta U$ est la variation."
          class="flex-1 p-6 outline-none bg-transparent border-0 focus:ring-0 text-sm font-mono text-slate-700 dark:text-slate-300 min-h-[400px] resize-y leading-relaxed"
          @input="triggerAutoSave"
        ></textarea>
      </div>

      <!-- WORKSPACE 2: PREVIEW / READ MODE -->
      <div 
        v-else 
        class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-12 shadow-sm min-h-[500px] print-container print:border-none print:shadow-none print:p-0"
      >
        <!-- Compiled Markdown & LaTeX Output -->
        <div 
          v-html="renderedContent" 
          class="prose prose-slate max-w-none dark:prose-invert leading-relaxed text-sm dark:text-slate-300 print:text-black markdown-body"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNotesStore } from '../../stores/notes'
import { useBindersStore } from '../../stores/binders'
import { ChevronLeft, Eye, Edit3, FileDown } from '@lucide/vue'
import { marked } from 'marked'
import katex from 'katex'

// Import KaTeX styles for formula rendering
import 'katex/dist/katex.min.css'

const notesStore = useNotesStore()
const bindersStore = useBindersStore()
const route = useRoute()
const router = useRouter()

const noteId = Number(route.params.id)
const loading = ref(true)
const isSaving = ref(false)
const saveStatus = ref('Enregistré')
const isEditMode = ref(false) // Default to read-mode for visualization first, or edit

const title = ref('')
const binderId = ref<number | null>(null)
const content = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)

let autoSaveTimer: any = null

const formatButtons = [
  { label: 'Titre H1', prefix: '# ', suffix: '' },
  { label: 'Titre H2', prefix: '## ', suffix: '' },
  { label: 'Gras', prefix: '**', suffix: '**' },
  { label: 'Italique', prefix: '*', suffix: '*' },
  { label: 'Liste', prefix: '* ', suffix: '' }
]

const latexButtons = [
  { label: 'Bloc Équation', prefix: '$$\n', suffix: '\n$$' },
  { label: 'En Ligne', prefix: '$', suffix: '$' },
  { label: 'Fraction', prefix: '\\frac{', suffix: '}{}' },
  { label: 'Somme', prefix: '\\sum_{', suffix: '}^{}' },
  { label: 'Intégrale', prefix: '\\int_{', suffix: '}^{}' },
  { label: 'Grec (Δ)', prefix: '\\Delta', suffix: '' }
]

// Render markdown and LaTeX combined string
const renderedContent = computed(() => {
  const text = content.value || ''
  const placeholders: string[] = []

  // 1. Double dollars $$ (Display equations block)
  let temp = text.replace(/\$\$([\s\S]+?)\$\$/g, (_match, formula) => {
    try {
      const html = katex.renderToString(formula.trim(), { displayMode: true, throwOnError: false })
      const key = `LATEXBLOCKPLACEHOLDER${placeholders.length}`
      placeholders.push(html)
      return key
    } catch (e) {
      return `<span class="text-rose-500 font-bold border border-rose-200 p-1 rounded">LaTeX Block Error: ${formula}</span>`
    }
  })

  // 2. Single dollars $ (Inline equations)
  temp = temp.replace(/\$([\s\S]+?)\$/g, (_match, formula) => {
    try {
      const html = katex.renderToString(formula.trim(), { displayMode: false, throwOnError: false })
      const key = `LATEXINLINEPLACEHOLDER${placeholders.length}`
      placeholders.push(html)
      return key
    } catch (e) {
      return `<span class="text-rose-500 font-bold">LaTeX Inline Error: ${formula}</span>`
    }
  })

  // 3. Mark down parse
  let html = marked.parse(temp) as string

  // 4. Put LaTeX formulas back
  placeholders.forEach((latexHtml, idx) => {
    html = html.replace(`LATEXBLOCKPLACEHOLDER${idx}`, latexHtml)
    html = html.replace(`LATEXINLINEPLACEHOLDER${idx}`, latexHtml)
  })

  return html
})

onMounted(async () => {
  await bindersStore.fetchBinders()
  const note = await notesStore.fetchNoteById(noteId)
  
  if (note) {
    title.value = note.title
    binderId.value = note.binder_id
    content.value = note.content
    
    // If the note content starts with HTML tag, keep editMode false, but if it is raw, adapt.
    // In our new mock, notes are in markdown, so we can display them.
    // If the note title is empty or "Note sans titre", open directly in edit mode for ease of use.
    if (note.title === 'Note sans titre') {
      isEditMode.value = true
    }
  }
  loading.value = false
})

onBeforeUnmount(() => {
  if (autoSaveTimer) clearTimeout(autoSaveTimer)
})

function goBack() {
  saveNote()
  router.push('/notes')
}

function toggleMode() {
  saveNote()
  isEditMode.value = !isEditMode.value
}

function getBinderName(bId: number | null): string {
  if (bId === null) return 'Général (Aucun)'
  const b = bindersStore.binders.find(x => x.id === bId)
  return b ? b.name : 'Général (Aucun)'
}

// Textarea insertion helpers
function insertText(prefix: string, suffix: string) {
  const textarea = textareaRef.value
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const text = textarea.value
  const selected = text.substring(start, end)
  
  const replacement = prefix + selected + suffix
  content.value = text.substring(0, start) + replacement + text.substring(end)
  
  // Refocus and place cursor
  setTimeout(() => {
    textarea.focus()
    const newCursorPos = start + prefix.length + selected.length + suffix.length
    textarea.setSelectionRange(newCursorPos, newCursorPos)
    triggerAutoSave()
  }, 50)
}

function triggerAutoSave() {
  saveStatus.value = 'Modifications...'
  isSaving.value = true
  
  if (autoSaveTimer) clearTimeout(autoSaveTimer)
  autoSaveTimer = setTimeout(() => {
    saveNote()
  }, 1500)
}

async function saveNote() {
  isSaving.value = true
  saveStatus.value = 'Sauvegarde...'
  try {
    await notesStore.updateNote(noteId, title.value, content.value)
    const index = notesStore.notes.findIndex(n => n.id === noteId)
    if (index !== -1) {
      notesStore.notes[index].binder_id = binderId.value
    }
    saveStatus.value = 'Sauvegardé'
  } catch (err) {
    saveStatus.value = 'Erreur'
  } finally {
    isSaving.value = false
  }
}

// Print / PDF generation trigger
function printNote() {
  window.print()
}
</script>

<style>
/* CSS styles for LaTeX and Markdown output integration */
.markdown-body h1 {
  @apply text-2xl font-extrabold text-slate-900 dark:text-white mt-6 mb-4 border-b border-slate-100 dark:border-slate-800 pb-2;
}

.markdown-body h2 {
  @apply text-xl font-bold text-slate-800 dark:text-slate-100 mt-5 mb-3;
}

.markdown-body h3 {
  @apply text-lg font-bold text-slate-800 dark:text-slate-200 mt-4 mb-2;
}

.markdown-body p {
  @apply text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-4;
}

.markdown-body ul {
  @apply list-disc pl-6 mb-4 space-y-1.5 text-sm;
}

.markdown-body ol {
  @apply list-decimal pl-6 mb-4 space-y-1.5 text-sm;
}

.markdown-body blockquote {
  @apply border-l-4 border-indigo-500 pl-4 italic text-slate-500 dark:text-slate-400 my-4;
}

.markdown-body strong {
  @apply font-bold text-slate-900 dark:text-white;
}

/* Custom styling for KaTeX print compatibility */
.katex-display {
  @apply my-6 p-4 bg-slate-50 dark:bg-slate-950/40 rounded-2xl border border-slate-100 dark:border-slate-800/50 overflow-x-auto;
}

/* Print CSS Configurations */
@media print {
  /* Hide UI components completely */
  aside, 
  header, 
  nav, 
  button, 
  select, 
  .no-print {
    display: none !important;
  }

  /* Reset main layouts wrapper */
  .min-h-screen, 
  main, 
  .max-w-4xl {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
    background: white !important;
    color: black !important;
    box-shadow: none !important;
  }
  
  .print-container {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
    padding: 0 !important;
  }
  
  .markdown-body p, 
  .markdown-body ul, 
  .markdown-body ol {
    color: #111827 !important;
  }
  
  .markdown-body h1, 
  .markdown-body h2, 
  .markdown-body h3 {
    color: black !important;
  }

  .katex-display {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
  }
}
</style>
