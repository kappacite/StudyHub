<template>
  <transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="opacity-0 scale-95"
    enter-to-class="opacity-100 scale-100"
    leave-active-class="transition duration-150 ease-in"
    leave-from-class="opacity-100 scale-100"
    leave-to-class="opacity-0 scale-95"
  >
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-md no-print"
      @click.self="close"
    >
      <div
        class="bg-surface dark:bg-[#111827] border border-line dark:border-line rounded-3xl max-w-2xl w-full p-6 md:p-8 shadow-2xl flex flex-col justify-between max-h-[90vh] overflow-y-auto"
      >
        <!-- Modal Header -->
        <div class="flex items-start justify-between border-b border-line dark:border-line pb-4 mb-6">
          <div class="flex items-center gap-3">
            <div class="w-11 h-11 rounded-2xl bg-primary/10 dark:bg-primary/20 text-primary flex items-center justify-center shrink-0">
              <FileDown class="w-6 h-6 text-primary" />
            </div>
            <div>
              <h3 class="font-extrabold text-lg text-ink dark:text-white leading-tight flex items-center gap-2">
                Exportation PDF & Impression
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-primary-soft dark:bg-primary-soft text-primary uppercase tracking-wider">HD</span>
              </h3>
              <p class="text-xs text-ink-subtle dark:text-ink-muted mt-0.5">
                Personnalisez la mise en page et les éléments de votre document PDF
              </p>
            </div>
          </div>
          <button
            @click="close"
            class="p-2 hover:bg-surface-soft dark:hover:bg-surface-soft rounded-xl text-ink-subtle dark:text-ink-muted transition-colors"
            type="button"
          >
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="space-y-6 overflow-y-auto pr-1">
          <!-- Note Overview Pill -->
          <div class="p-3.5 bg-surface-soft dark:bg-surface-soft/60 border border-line dark:border-line rounded-2xl flex items-center justify-between text-xs">
            <div class="flex items-center gap-2.5 truncate max-w-[75%]">
              <FileText class="w-4 h-4 text-primary shrink-0" />
              <span class="font-bold text-ink dark:text-white truncate">{{ noteTitle || 'Note sans titre' }}</span>
              <span v-if="binderName" class="px-2 py-0.5 rounded-lg text-[10px] font-semibold bg-primary-soft text-primary dark:bg-primary-soft uppercase tracking-wider shrink-0">
                {{ binderName }}
              </span>
            </div>
            <div class="flex items-center gap-2 text-[11px] text-ink-subtle shrink-0">
              <span v-if="headingsCount > 0" class="flex items-center gap-1">
                <List class="w-3.5 h-3.5 text-primary" />
                {{ headingsCount }} section{{ headingsCount > 1 ? 's' : '' }}
              </span>
              <span v-if="definitionsCount > 0" class="flex items-center gap-1">
                <BookOpen class="w-3.5 h-3.5 text-emerald-500" />
                {{ definitionsCount }} def
              </span>
            </div>
          </div>

          <!-- Section 1: Thème du PDF -->
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-ink-subtle dark:text-ink-muted mb-3 flex items-center gap-1.5">
              <Palette class="w-4 h-4 text-primary" />
              Style & Design du PDF
            </label>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <!-- Modern Theme -->
              <button
                type="button"
                @click="options.theme = 'modern'"
                :class="[
                  'p-3.5 rounded-2xl border text-left transition-all flex flex-col justify-between relative overflow-hidden',
                  options.theme === 'modern'
                    ? 'border-primary ring-2 ring-primary/20 bg-primary-soft/30 dark:bg-primary-soft/10'
                    : 'border-line dark:border-line hover:border-primary-soft bg-surface dark:bg-surface-soft'
                ]"
              >
                <div class="flex items-center justify-between mb-2">
                  <span class="font-bold text-xs text-ink dark:text-white">Modern Pro</span>
                  <div v-if="options.theme === 'modern'" class="w-4 h-4 rounded-full bg-primary text-white flex items-center justify-center">
                    <Check class="w-3 h-3" />
                  </div>
                </div>
                <p class="text-[11px] text-ink-subtle dark:text-ink-muted leading-tight">
                  En-tête stylisé, accents de couleur, badges et encadrés arrondis.
                </p>
              </button>

              <!-- Academic Theme -->
              <button
                type="button"
                @click="options.theme = 'academic'"
                :class="[
                  'p-3.5 rounded-2xl border text-left transition-all flex flex-col justify-between relative overflow-hidden',
                  options.theme === 'academic'
                    ? 'border-primary ring-2 ring-primary/20 bg-primary-soft/30 dark:bg-primary-soft/10'
                    : 'border-line dark:border-line hover:border-primary-soft bg-surface dark:bg-surface-soft'
                ]"
              >
                <div class="flex items-center justify-between mb-2">
                  <span class="font-bold text-xs text-ink dark:text-white font-serif">Académique</span>
                  <div v-if="options.theme === 'academic'" class="w-4 h-4 rounded-full bg-primary text-white flex items-center justify-center">
                    <Check class="w-3 h-3" />
                  </div>
                </div>
                <p class="text-[11px] text-ink-subtle dark:text-ink-muted leading-tight">
                  Format formel de cours & mémoire, typographie serif élégante.
                </p>
              </button>

              <!-- Minimal Theme -->
              <button
                type="button"
                @click="options.theme = 'minimal'"
                :class="[
                  'p-3.5 rounded-2xl border text-left transition-all flex flex-col justify-between relative overflow-hidden',
                  options.theme === 'minimal'
                    ? 'border-primary ring-2 ring-primary/20 bg-primary-soft/30 dark:bg-primary-soft/10'
                    : 'border-line dark:border-line hover:border-primary-soft bg-surface dark:bg-surface-soft'
                ]"
              >
                <div class="flex items-center justify-between mb-2">
                  <span class="font-bold text-xs text-ink dark:text-white">Éco Minimal</span>
                  <div v-if="options.theme === 'minimal'" class="w-4 h-4 rounded-full bg-primary text-white flex items-center justify-center">
                    <Check class="w-3 h-3" />
                  </div>
                </div>
                <p class="text-[11px] text-ink-subtle dark:text-ink-muted leading-tight">
                  Noir & blanc épuré, contraste maximal, économie d'encre d'impression.
                </p>
              </button>
            </div>
          </div>

          <!-- Section 2: Taille du texte -->
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-ink-subtle dark:text-ink-muted mb-3 flex items-center gap-1.5">
              <Type class="w-4 h-4 text-primary" />
              Taille d'écriture dans le PDF
            </label>
            <div class="flex items-center bg-surface-soft dark:bg-surface-soft p-1 rounded-xl border border-line dark:border-line">
              <button
                type="button"
                @click="options.fontSize = 'compact'"
                :class="[
                  'flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold transition-all text-center',
                  options.fontSize === 'compact'
                    ? 'bg-surface dark:bg-slate-800 text-primary shadow-sm font-bold'
                    : 'text-ink-subtle hover:text-ink dark:text-ink-muted'
                ]"
              >
                Compact (11px)
              </button>
              <button
                type="button"
                @click="options.fontSize = 'standard'"
                :class="[
                  'flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold transition-all text-center',
                  options.fontSize === 'standard'
                    ? 'bg-surface dark:bg-slate-800 text-primary shadow-sm font-bold'
                    : 'text-ink-subtle hover:text-ink dark:text-ink-muted'
                ]"
              >
                Standard (13px)
              </button>
              <button
                type="button"
                @click="options.fontSize = 'comfortable'"
                :class="[
                  'flex-1 py-1.5 px-3 rounded-lg text-xs font-semibold transition-all text-center',
                  options.fontSize === 'comfortable'
                    ? 'bg-surface dark:bg-slate-800 text-primary shadow-sm font-bold'
                    : 'text-ink-subtle hover:text-ink dark:text-ink-muted'
                ]"
              >
                Confort (15px)
              </button>
            </div>
          </div>

          <!-- Section 3: Éléments à inclure -->
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider text-ink-subtle dark:text-ink-muted mb-3 flex items-center gap-1.5">
              <Layout class="w-4 h-4 text-primary" />
              Éléments du document
            </label>
            <div class="space-y-2.5">
              <!-- Include Header -->
              <label class="flex items-center justify-between p-3 bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-xl cursor-pointer hover:border-primary-soft transition-all">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-500 flex items-center justify-center">
                    <Sparkles class="w-4 h-4" />
                  </div>
                  <div>
                    <span class="font-bold text-xs text-ink dark:text-white block">Bannière & Métadonnées d'en-tête</span>
                    <span class="text-[11px] text-ink-subtle dark:text-ink-muted">Titre, classeur, tags et date d'exportation</span>
                  </div>
                </div>
                <input
                  type="checkbox"
                  v-model="options.includeHeader"
                  class="w-4 h-4 text-primary rounded border-line focus:ring-primary accent-primary cursor-pointer"
                />
              </label>

              <!-- Include TOC -->
              <label
                :class="[
                  'flex items-center justify-between p-3 border rounded-xl transition-all',
                  headingsCount > 0
                    ? 'bg-surface dark:bg-surface-soft border-line dark:border-line cursor-pointer hover:border-primary-soft'
                    : 'bg-surface-soft/40 dark:bg-surface-soft/20 border-line/50 opacity-60 cursor-not-allowed'
                ]"
              >
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-lg bg-blue-500/10 text-blue-500 flex items-center justify-center">
                    <List class="w-4 h-4" />
                  </div>
                  <div>
                    <span class="font-bold text-xs text-ink dark:text-white block">
                      Sommaire / Table des matières
                      <span v-if="headingsCount === 0" class="text-[10px] font-normal text-ink-subtle ml-1">(Aucune section détectée)</span>
                    </span>
                    <span class="text-[11px] text-ink-subtle dark:text-ink-muted">Extrait automatiquement des titres H1, H2, H3</span>
                  </div>
                </div>
                <input
                  type="checkbox"
                  v-model="options.includeToc"
                  :disabled="headingsCount === 0"
                  class="w-4 h-4 text-primary rounded border-line focus:ring-primary accent-primary cursor-pointer"
                />
              </label>

              <!-- Include Context -->
              <label
                v-if="hasContext"
                class="flex items-center justify-between p-3 bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-xl cursor-pointer hover:border-primary-soft transition-all"
              >
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-500 flex items-center justify-center">
                    <Compass class="w-4 h-4" />
                  </div>
                  <div>
                    <span class="font-bold text-xs text-ink dark:text-white block">Contexte & Objectifs de révision</span>
                    <span class="text-[11px] text-ink-subtle dark:text-ink-muted">Inclut le bloc d'introduction de la note</span>
                  </div>
                </div>
                <input
                  type="checkbox"
                  v-model="options.includeContext"
                  class="w-4 h-4 text-primary rounded border-line focus:ring-primary accent-primary cursor-pointer"
                />
              </label>

              <!-- Include Definitions Glossary -->
              <label
                :class="[
                  'flex items-center justify-between p-3 border rounded-xl transition-all',
                  definitionsCount > 0
                    ? 'bg-surface dark:bg-surface-soft border-line dark:border-line cursor-pointer hover:border-primary-soft'
                    : 'bg-surface-soft/40 dark:bg-surface-soft/20 border-line/50 opacity-60 cursor-not-allowed'
                ]"
              >
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-500 flex items-center justify-center">
                    <BookOpen class="w-4 h-4" />
                  </div>
                  <div>
                    <span class="font-bold text-xs text-ink dark:text-white block">
                      Index des définitions en fin de document
                      <span v-if="definitionsCount === 0" class="text-[10px] font-normal text-ink-subtle ml-1">(Aucune définition clé)</span>
                    </span>
                    <span class="text-[11px] text-ink-subtle dark:text-ink-muted">Tableau récapitulatif des mots-clés définis</span>
                  </div>
                </div>
                <input
                  type="checkbox"
                  v-model="options.includeGlossary"
                  :disabled="definitionsCount === 0"
                  class="w-4 h-4 text-primary rounded border-line focus:ring-primary accent-primary cursor-pointer"
                />
              </label>

              <!-- Include Footer & Page Numbers -->
              <label class="flex items-center justify-between p-3 bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-xl cursor-pointer hover:border-primary-soft transition-all">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-lg bg-slate-500/10 text-slate-500 flex items-center justify-center">
                    <Printer class="w-4 h-4" />
                  </div>
                  <div>
                    <span class="font-bold text-xs text-ink dark:text-white block">Pied de page</span>
                    <span class="text-[11px] text-ink-subtle dark:text-ink-muted">Titre du document et ligne de séparation en bas de page</span>
                  </div>
                </div>
                <input
                  type="checkbox"
                  v-model="options.includeFooter"
                  class="w-4 h-4 text-primary rounded border-line focus:ring-primary accent-primary cursor-pointer"
                />
              </label>
            </div>
          </div>
        </div>

        <!-- Modal Footer Actions -->
        <div class="flex items-center justify-between border-t border-line dark:border-line pt-5 mt-6">
          <div class="text-[11px] text-ink-subtle dark:text-ink-muted flex items-center gap-1.5">
            <span class="inline-block w-2 h-2 rounded-full bg-emerald-500"></span>
            Conseil : Décochez <strong class="text-ink dark:text-white font-semibold">« En-têtes et pieds de page »</strong> dans l'impression pour masquer les URL.
          </div>
          <div class="flex items-center gap-3">
            <button
              type="button"
              @click="close"
              class="px-4 py-2 border border-line dark:border-line rounded-xl text-xs font-semibold text-ink-subtle hover:bg-surface-soft dark:hover:bg-surface-soft transition-all"
            >
              Annuler
            </button>
            <button
              type="button"
              @click="handleExport"
              class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-primary hover:bg-primary-strong active:scale-95 transition-all shadow-md shadow-elev-primary"
            >
              <Printer class="w-4 h-4" />
              Lancer l'exportation PDF
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import {
  FileDown,
  X,
  FileText,
  Palette,
  Check,
  Type,
  Layout,
  Sparkles,
  List,
  Compass,
  BookOpen,
  Printer
} from '@lucide/vue'

export interface PdfExportOptions {
  theme: 'modern' | 'academic' | 'minimal'
  fontSize: 'compact' | 'standard' | 'comfortable'
  includeHeader: boolean
  includeToc: boolean
  includeContext: boolean
  includeGlossary: boolean
  includeFooter: boolean
}

const props = defineProps<{
  isOpen: boolean
  noteTitle?: string
  binderName?: string
  headingsCount: number
  definitionsCount: number
  hasContext: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'export', options: PdfExportOptions): void
}>()

const options = reactive<PdfExportOptions>({
  theme: 'modern',
  fontSize: 'standard',
  includeHeader: true,
  includeToc: props.headingsCount > 0,
  includeContext: props.hasContext,
  includeGlossary: props.definitionsCount > 0,
  includeFooter: true
})

watch(() => props.headingsCount, (newVal) => {
  if (newVal > 0) options.includeToc = true
})

watch(() => props.definitionsCount, (newVal) => {
  if (newVal > 0) options.includeGlossary = true
})

function close() {
  emit('close')
}

function handleExport() {
  emit('export', { ...options })
}
</script>
