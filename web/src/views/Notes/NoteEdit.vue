<template>
  <div class="space-y-6 max-w-6xl mx-auto animate-fade-in print:max-w-full print:p-0 print:space-y-0">
    
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
          {{ isEditMode ? 'Visualiser la fiche' : 'Modifier la fiche' }}
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
      
      <!-- Title & Binder Selection Card (Meta) -->
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

      <!-- WORKSPACE 1: EDIT MODE (INTEGRATED SINGLE-COLUMN SHEET) -->
      <div v-if="isEditMode" class="max-w-4xl mx-auto bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 rounded-3xl p-6 lg:p-10 shadow-xl shadow-slate-200/50 dark:shadow-slate-950/40 space-y-6">
        
        <!-- 1. Context Input Section -->
        <div class="bg-amber-50/30 border border-amber-100/50 rounded-2xl p-5 dark:bg-amber-950/5 dark:border-amber-900/30 space-y-3">
          <h3 class="text-xs font-bold text-amber-700 dark:text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
            <Compass class="w-4 h-4" />
            Contexte de la note
          </h3>
          <textarea 
            v-model="noteContext"
            placeholder="Historique, cadre théorique ou d'apprentissage..."
            rows="2"
            class="w-full p-3 text-xs bg-white dark:bg-slate-850 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-700 dark:text-slate-300 resize-y"
            @input="triggerAutoSave"
          ></textarea>
        </div>

        <!-- 2. Main Note Body Section -->
        <div class="border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden flex flex-col min-h-[500px]">
          <!-- Header with Title and Insertion/Toolbar -->
          <div class="px-5 py-3.5 border-b border-slate-100 dark:border-slate-800 bg-slate-50/40 dark:bg-slate-900/40 flex items-center justify-between">
            <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <FileText class="w-4 h-4 text-indigo-500" />
              Notes de cours
            </h3>
          </div>

          <!-- Markdown, LaTeX & Tooltip Insertion Bar -->
          <div class="flex flex-wrap items-center gap-1.5 p-3 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/20">
            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2">Format</span>
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

            <div class="h-4 w-[1px] bg-slate-200 dark:bg-slate-800 mx-2"></div>
            
            <!-- Smart Space: Definition Tooltip insertion -->
            <button 
              type="button" 
              @click="insertDefinitionTooltip"
              class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-100 dark:border-emerald-900/30 rounded-xl hover:bg-emerald-100 dark:hover:bg-emerald-950/60 active:scale-95 transition-all"
              title="Associer une définition en info-bulle au texte sélectionné"
            >
              <BookOpen class="w-3.5 h-3.5" />
              Définition (Info-bulle)
            </button>
          </div>

          <!-- Raw Markdown Text Area -->
          <textarea 
            ref="textareaRef"
            v-model="noteBody"
            placeholder="Rédigez vos notes ici en Markdown..."
            class="flex-1 p-6 outline-none bg-transparent border-0 focus:ring-0 text-sm font-mono text-slate-700 dark:text-slate-300 min-h-[400px] resize-y leading-relaxed"
            @input="triggerAutoSave"
          ></textarea>
        </div>

        <!-- 3. Linked Notes Section -->
        <div class="bg-indigo-50/20 border border-indigo-100/50 rounded-2xl p-5 dark:bg-indigo-950/5 dark:border-indigo-900/30 space-y-4">
          <h3 class="text-xs font-bold text-indigo-700 dark:text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
            <LinkIcon class="w-4 h-4" />
            Lier à d'autres notes
          </h3>
          
          <div class="flex gap-2">
            <select 
              v-model="selectedLinkTarget"
              class="flex-1 max-w-md px-3 py-2 bg-white dark:bg-slate-850 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-xs font-semibold"
            >
              <option :value="null" disabled>Sélectionner une note...</option>
              <option 
                v-for="item in linkableNotes" 
                :key="item.id" 
                :value="item.id"
              >
                {{ item.title }}
              </option>
            </select>
            
            <button 
              @click="addNoteLink"
              type="button"
              class="px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl active:scale-95 transition-all shadow-sm"
            >
              Lier la note
            </button>
          </div>

          <!-- Linked notes badges -->
          <div v-if="noteLinks.length > 0" class="flex flex-wrap gap-1.5 pt-1">
            <span 
              v-for="linkedId in noteLinks" 
              :key="linkedId"
              class="inline-flex items-center gap-1.5 px-3 py-1 bg-white border border-slate-200 dark:bg-slate-800 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs font-semibold rounded-lg shadow-sm"
            >
              {{ getNoteTitle(linkedId) }}
              <button 
                @click="removeNoteLink(linkedId)" 
                type="button" 
                class="text-slate-400 hover:text-rose-500 transition-colors"
              >
                ✕
              </button>
            </span>
          </div>
        </div>

      </div>

      <!-- WORKSPACE 2: PREVIEW / READ MODE (INTEGRATED COHESIVE SHEET) -->
      <div v-else class="max-w-4xl mx-auto bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 rounded-3xl p-8 lg:p-12 shadow-xl shadow-slate-200/50 dark:shadow-slate-950/40 space-y-6 print:border-none print:shadow-none print:p-0">
        
        <!-- 1. Context Block (Full width, integrated at the top of the paper) -->
        <div 
          v-if="noteContext"
          class="bg-amber-50/50 border-l-4 border-amber-500 rounded-r-2xl p-5 dark:bg-amber-950/10 dark:border-amber-700/50 print:bg-[#fffbeb] print:border-amber-300"
        >
          <h3 class="text-xs font-bold text-amber-800 dark:text-amber-400 flex items-center gap-1.5 uppercase tracking-wider mb-2 no-print">
            <Compass class="w-4 h-4" />
            Contexte de la note
          </h3>
          <div 
            v-html="renderMarkup(noteContext)"
            class="prose prose-amber max-w-none text-xs leading-relaxed dark:prose-invert print:text-black"
          ></div>
        </div>

        <!-- Legacy Definitions Block (for backward compatibility only if loaded) -->
        <div 
          v-if="noteDefinition"
          class="bg-emerald-50/30 border-l-4 border-emerald-500 rounded-r-2xl p-5 dark:bg-emerald-950/10 dark:border-emerald-700/50 print:bg-[#ecfdf5] print:border-emerald-300"
        >
          <h3 class="text-xs font-bold text-emerald-800 dark:text-emerald-400 flex items-center gap-1.5 uppercase tracking-wider mb-2">
            <BookOpen class="w-4 h-4" />
            Définitions clés (Legacy)
          </h3>
          <div 
            v-html="renderMarkup(noteDefinition)"
            class="prose prose-emerald max-w-none text-xs leading-relaxed dark:prose-invert print:text-black"
          ></div>
        </div>

        <!-- 2. Main Note Content Block -->
        <div class="prose prose-slate max-w-none dark:prose-invert leading-relaxed text-sm dark:text-slate-300 print:text-black markdown-body">
          <div v-html="renderMarkup(noteBody)"></div>
        </div>

        <!-- 3. Linked Notes Block (Integrated at the bottom of the sheet) -->
        <div v-if="noteLinks.length > 0" class="border-t border-slate-100 dark:border-slate-800 pt-6 no-print">
          <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5 mb-3">
            <LinkIcon class="w-4.5 h-4.5 text-indigo-500" />
            Notes liées
          </h3>
          <div class="flex flex-wrap gap-2">
            <button 
              v-for="linkedId in noteLinks" 
              :key="linkedId"
              @click="navigateToNote(linkedId)"
              class="inline-flex items-center gap-1.5 px-3.5 py-2 bg-slate-50 hover:bg-indigo-50 dark:bg-slate-850/40 dark:hover:bg-indigo-950/20 border border-slate-100 dark:border-slate-800 rounded-xl transition-all text-xs font-semibold"
            >
              <span>{{ getNoteTitle(linkedId) }}</span>
              <ChevronRight class="w-3.5 h-3.5 text-slate-400" />
            </button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNotesStore } from '../../stores/notes'
import { useBindersStore } from '../../stores/binders'
import { 
  ChevronLeft, 
  Eye, 
  Edit3, 
  FileDown,
  BookOpen,
  Compass,
  Link as LinkIcon,
  ChevronRight,
  FileText
} from '@lucide/vue'
import { marked } from 'marked'
import katex from 'katex'

// Import KaTeX styles for formula rendering
import 'katex/dist/katex.min.css'

const notesStore = useNotesStore()
const bindersStore = useBindersStore()
const route = useRoute()
const router = useRouter()

const noteId = ref(Number(route.params.id))
const loading = ref(true)
const isSaving = ref(false)
const saveStatus = ref('Enregistré')
const isEditMode = ref(false)

const title = ref('')
const binderId = ref<number | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

// Structured Notes Divisions
const noteContext = ref('')
const noteDefinition = ref('')
const noteBody = ref('')
const noteLinks = ref<number[]>([])

const selectedLinkTarget = ref<number | null>(null)

let autoSaveTimer: any = null

const formatButtons = [
  { label: 'Titre H1', prefix: '# ', suffix: '' },
  { label: 'Titre H2', prefix: '## ', suffix: '' },
  { label: 'Gras', prefix: '**', suffix: '**' },
  { label: 'Italique', prefix: '*', suffix: '*' }
]

const latexButtons = [
  { label: 'Bloc Équation', prefix: '$$\n', suffix: '\n$$' },
  { label: 'En Ligne', prefix: '$', suffix: '$' },
  { label: 'Fraction', prefix: '\\frac{', suffix: '}{}' },
  { label: 'Somme', prefix: '\\sum_{', suffix: '}^{}' },
  { label: 'Intégrale', prefix: '\\int_{', suffix: '}^{}' }
]

// Reload components when route parameter changes (for linked notes navigation)
watch(() => route.params.id, async (newVal) => {
  if (newVal) {
    noteId.value = Number(newVal)
    await loadNoteDetails()
  }
})

onMounted(async () => {
  await notesStore.fetchNotes()
  await bindersStore.fetchBinders()
  await loadNoteDetails()
})

onBeforeUnmount(() => {
  if (autoSaveTimer) clearTimeout(autoSaveTimer)
})

async function loadNoteDetails() {
  loading.value = true
  isSaving.value = false
  saveStatus.value = 'Enregistré'
  
  const note = await notesStore.fetchNoteById(noteId.value)
  if (note) {
    title.value = note.title
    binderId.value = note.binder_id
    
    // Parse structured divisions
    const parsed = parseStructuredNote(note.content)
    noteContext.value = parsed.context
    noteDefinition.value = parsed.definition
    noteBody.value = parsed.body
    noteLinks.value = parsed.linkedIds
    
    if (note.title === 'Note sans titre') {
      isEditMode.value = true
    } else {
      isEditMode.value = false
    }
  }
  loading.value = false
}

// Structured Divisions Parsers
function parseStructuredNote(rawContent: string) {
  let contextVal = ''
  let definitionVal = ''
  let bodyVal = rawContent
  let linkedIdsVal: number[] = []

  // Extraire les liens
  const linksMatch = rawContent.match(/<!-- LINKED_NOTES: ([\d,\s]*) -->/)
  if (linksMatch) {
    linkedIdsVal = linksMatch[1].split(',')
      .map(id => Number(id.trim()))
      .filter(id => !isNaN(id) && id > 0)
  }

  // Extraire le contexte
  const contextMatch = rawContent.match(/<!-- SECTION_CONTEXT -->([\s\S]*?)<!-- END_SECTION_CONTEXT -->/)
  if (contextMatch) {
    contextVal = contextMatch[1].trim()
  }

  // Extraire la définition
  const defMatch = rawContent.match(/<!-- SECTION_DEFINITION -->([\s\S]*?)<!-- END_SECTION_DEFINITION -->/)
  if (defMatch) {
    definitionVal = defMatch[1].trim()
  }

  // Extraire le corps
  const bodyMatch = rawContent.match(/<!-- SECTION_BODY -->([\s\S]*?)<!-- END_SECTION_BODY -->/)
  if (bodyMatch) {
    bodyVal = bodyMatch[1].trim()
  } else {
    // Nettoyer si ancienne note simple
    bodyVal = rawContent
      .replace(/<!-- SECTION_CONTEXT -->[\s\S]*?<!-- END_SECTION_CONTEXT -->/g, '')
      .replace(/<!-- SECTION_DEFINITION -->[\s\S]*?<!-- END_SECTION_DEFINITION -->/g, '')
      .replace(/<!-- LINKED_NOTES: [\d,\s]* -->/g, '')
      .trim()
  }

  return {
    context: contextVal,
    definition: definitionVal,
    body: bodyVal,
    linkedIds: linkedIdsVal
  }
}

function compileStructuredNote() {
  let raw = ''
  
  if (noteContext.value.trim()) {
    raw += `<!-- SECTION_CONTEXT -->\n${noteContext.value.trim()}\n<!-- END_SECTION_CONTEXT -->\n\n`
  }
  
  if (noteDefinition.value.trim()) {
    raw += `<!-- SECTION_DEFINITION -->\n${noteDefinition.value.trim()}\n<!-- END_SECTION_DEFINITION -->\n\n`
  }
  
  raw += `<!-- SECTION_BODY -->\n${noteBody.value.trim()}\n<!-- END_SECTION_BODY -->\n\n`
  
  if (noteLinks.value.length > 0) {
    raw += `<!-- LINKED_NOTES: ${noteLinks.value.join(', ')} -->`
  }
  
  return raw
}

// Rendering marked + LaTeX + Definition tooltips
function renderMarkup(text: string): string {
  const markdownText = text || ''
  const placeholders: string[] = []

  // 1. Double dollars $$ (Display equations block)
  let temp = markdownText.replace(/\$\$([\s\S]+?)\$\$/g, (_match, formula) => {
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

  // 3. Definition Tooltips [term]{def:definition}
  temp = temp.replace(/\[([^\]]+)\]\{def:([^\}]+)\}/g, (_match, term, definition) => {
    const html = `<span class="group relative inline-block underline decoration-emerald-500 decoration-dashed cursor-help bg-emerald-50/30 dark:bg-emerald-950/20 px-1.5 py-0.5 rounded transition-all duration-200">${term}<span class="pointer-events-none absolute bottom-full left-1/2 z-50 mb-2 w-64 -translate-x-1/2 rounded-xl bg-slate-900 dark:bg-slate-950 p-3 text-xs font-medium text-slate-100 dark:text-slate-200 shadow-xl opacity-0 transition-opacity duration-200 group-hover:opacity-100 leading-normal normal-case text-center">${definition}</span></span>`
    const key = `DEFPLACEHOLDER${placeholders.length}`
    placeholders.push(html)
    return key
  })

  // 4. Mark down parse
  let html = marked.parse(temp) as string

  // 5. Put LaTeX and Definition HTML back
  placeholders.forEach((placeholderHtml, idx) => {
    html = html.replace(`LATEXBLOCKPLACEHOLDER${idx}`, placeholderHtml)
    html = html.replace(`LATEXINLINEPLACEHOLDER${idx}`, placeholderHtml)
    html = html.replace(`DEFPLACEHOLDER${idx}`, placeholderHtml)
  })

  return html
}

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

// Linked Notes logic
const linkableNotes = computed(() => {
  return notesStore.notes.filter(n => n.id !== noteId.value && !noteLinks.value.includes(n.id))
})

function addNoteLink() {
  if (selectedLinkTarget.value !== null) {
    noteLinks.value.push(selectedLinkTarget.value)
    selectedLinkTarget.value = null
    triggerAutoSave()
  }
}

function removeNoteLink(id: number) {
  noteLinks.value = noteLinks.value.filter(linkedId => linkedId !== id)
  triggerAutoSave()
}

function getNoteTitle(id: number): string {
  const n = notesStore.notes.find(x => x.id === id)
  return n ? n.title : 'Note inconnue'
}

function navigateToNote(id: number) {
  router.push(`/notes/${id}`)
}

// Textarea insertion helpers (inserts inside noteBody)
function insertText(prefix: string, suffix: string) {
  const textarea = textareaRef.value
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const text = textarea.value
  const selected = text.substring(start, end)
  
  const replacement = prefix + selected + suffix
  noteBody.value = text.substring(0, start) + replacement + text.substring(end)
  
  setTimeout(() => {
    textarea.focus()
    const newCursorPos = start + prefix.length + selected.length + suffix.length
    textarea.setSelectionRange(newCursorPos, newCursorPos)
    triggerAutoSave()
  }, 50)
}

function insertDefinitionTooltip() {
  const textarea = textareaRef.value
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const text = textarea.value
  const selected = text.substring(start, end)
  
  if (!selected.trim()) {
    alert("Veuillez sélectionner un mot ou un terme dans le texte pour lui associer une définition.")
    return
  }
  
  const definition = prompt(`Entrez la définition pour le terme "${selected}" :`)
  if (definition === null) return // User cancelled
  
  if (!definition.trim()) {
    alert("La définition ne peut pas être vide.")
    return
  }
  
  const replacement = `[${selected}]{def:${definition.trim()}}`
  noteBody.value = text.substring(0, start) + replacement + text.substring(end)
  
  setTimeout(() => {
    textarea.focus()
    const newCursorPos = start + replacement.length
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
  
  // Re-build markdown raw note structure
  const rawContent = compileStructuredNote()
  
  try {
    await notesStore.updateNote(noteId.value, title.value, rawContent)
    const index = notesStore.notes.findIndex(n => n.id === noteId.value)
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

function printNote() {
  window.print()
}
</script>

<style>
/* Markdown formatting body styling */
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

.katex-display {
  @apply my-4 p-3 bg-slate-50 dark:bg-slate-950/40 rounded-2xl border border-slate-100 dark:border-slate-800/50 overflow-x-auto;
}

/* Print CSS Settings */
@media print {
  aside, header, nav, button, select, no-print, .no-print {
    display: none !important;
  }
  .min-h-screen, main, .max-w-6xl {
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
  .markdown-body p, .markdown-body ul, .markdown-body ol {
    color: #111827 !important;
  }
  .markdown-body h1, .markdown-body h2, .markdown-body h3 {
    color: black !important;
  }
  .katex-display {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
  }
}
</style>
