<template>
  <div 
    class="w-full flex flex-col"
    :class="[isEditMode ? 'h-full overflow-hidden' : 'min-h-full']"
  >
    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex flex-col items-center justify-center py-20 gap-3 no-print bg-slate-50 dark:bg-[#070913] h-full w-full">
      <svg class="animate-spin h-8 w-8 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="text-sm font-semibold text-slate-400 uppercase tracking-widest text-slate-400">Ouverture de la note...</span>
    </div>

    <!-- Main Content -->
    <div v-else class="flex-1 flex flex-col w-full animate-fade-in print:h-auto print:overflow-visible" :class="[isEditMode ? 'overflow-hidden' : '']">
      
      <!-- Split-Screen Outer Container -->
      <div class="flex-1 flex w-full h-full overflow-hidden print:h-auto print:overflow-visible">
        
        <!-- Left Pane: PDF Visualizer removed -->
        
        <!-- Right Pane: Note Content -->
        <div class="flex-1 flex flex-col overflow-hidden h-full print:h-auto print:overflow-visible bg-white dark:bg-slate-900">
          
          <!-- 1. FULL VIEWPORT EDIT MODE -->
          <div v-if="isEditMode" class="flex-1 flex flex-col bg-white dark:bg-slate-900 overflow-hidden">
        
        <!-- Header Toolbar -->
        <div class="flex flex-col border-b border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 z-10 no-print">
          
          <!-- Row 1: Global Actions & Title -->
          <div class="flex flex-wrap items-center justify-between gap-3 px-6 py-3 border-b border-slate-50 dark:border-slate-850/60">
            <div class="flex min-w-[18rem] flex-1 items-center gap-4">
              <!-- Sidebar toggle -->
              <button 
                @click="toggleShortcutSidebar" 
                class="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 text-slate-500 transition-colors hover:border-indigo-200 hover:bg-indigo-50 hover:text-indigo-600 dark:border-slate-800 dark:text-slate-400 dark:hover:border-indigo-900 dark:hover:bg-indigo-950/30 dark:hover:text-indigo-400"
                type="button"
                title="Afficher la barre de raccourcis"
              >
                <Menu class="h-5 w-5" />
              </button>
              
              <div class="h-5 w-[1px] bg-slate-200 dark:bg-slate-800"></div>

              <!-- Title Input (Direct inline edit) -->
              <input 
                type="text" 
                v-model="title" 
                placeholder="Titre de la note..."
                class="block flex-1 max-w-xl text-lg font-bold bg-transparent border-0 focus:ring-0 focus:outline-none placeholder-slate-300 dark:placeholder-slate-700 py-1"
                @input="triggerAutoSave"
              />
            </div>

            <!-- Header Right Controls -->
            <div class="flex max-w-full flex-wrap items-center justify-end gap-2">
              <!-- Save Status -->
              <span class="text-xs font-semibold text-slate-400 flex items-center gap-1.5 mr-2">
                <span class="w-2 h-2 rounded-full bg-emerald-500" :class="[isSaving ? 'animate-pulse' : '']"></span>
                {{ saveStatus }}
              </span>

              <!-- Binder select -->
              <select 
                v-model="binderId"
                class="px-2.5 py-1.5 bg-slate-50 border border-slate-200 dark:bg-slate-800/40 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-xs font-semibold transition-all"
                @change="triggerAutoSave"
              >
                <option :value="null">Général (Aucun)</option>
                <option v-for="b in bindersStore.binders" :key="b.id" :value="b.id">{{ b.name }}</option>
              </select>

              <div class="w-48 sm:w-56">
                <TagSelector v-model="noteTags" compact @change="saveNoteTags" />
              </div>

              <!-- Collapsible Settings Toggle (Context & Links) -->
              <button 
                @click="showSettings = !showSettings"
                class="inline-flex items-center gap-1.5 px-3 py-1.5 border rounded-xl text-xs font-semibold transition-all"
                :class="[
                  showSettings 
                    ? 'border-indigo-600 bg-indigo-50 text-indigo-600 dark:border-indigo-500 dark:bg-indigo-950/20 dark:text-indigo-400' 
                    : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-850'
                ]"
              >
                <Compass class="w-3.5 h-3.5" />
                Contexte / Liens
              </button>

              <!-- Live Preview Toggle -->
              <button 
                @click="isLivePreviewActive = !isLivePreviewActive"
                class="inline-flex items-center gap-1.5 px-3 py-1.5 border rounded-xl text-xs font-semibold transition-all"
                :class="[
                  isLivePreviewActive 
                    ? 'border-indigo-600 bg-indigo-50 text-indigo-600 dark:border-indigo-500 dark:bg-indigo-950/20 dark:text-indigo-400' 
                    : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-850 text-slate-650 dark:text-slate-300'
                ]"
                type="button"
                title="Afficher l'aperçu en temps réel côte à côte"
              >
                <Columns class="w-3.5 h-3.5" />
                Aperçu
              </button>

              <!-- View Toggler -->
              <button 
                @click="toggleMode"
                class="inline-flex items-center gap-2 px-4 py-1.5 border border-slate-200 dark:border-slate-800 rounded-xl text-xs font-semibold hover:bg-slate-50 dark:hover:bg-slate-850 transition-all text-slate-600 dark:text-slate-300"
              >
                <Eye class="w-3.5 h-3.5 text-indigo-500" />
                Visualiser
              </button>

              <!-- Bouton Partage -->
              <div class="relative">
                <button
                  @click="handleShareClick"
                  type="button"
                  :title="isPublic ? 'Note publique — cliquer pour rendre privée' : 'Rendre cette note publique'"
                  class="inline-flex items-center gap-1.5 px-3 py-1.5 border rounded-xl text-xs font-semibold transition-all"
                  :class="[
                    isPublic
                      ? 'border-emerald-500 bg-emerald-50 text-emerald-600 dark:border-emerald-600 dark:bg-emerald-950/20 dark:text-emerald-400'
                      : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-850 text-slate-600 dark:text-slate-300'
                  ]"
                >
                  <Globe class="w-3.5 h-3.5" />
                  {{ isPublic ? 'Public' : 'Privé' }}
                </button>

                <!-- Popup lien de partage -->
                <Transition name="popup">
                  <div
                    v-if="sharePopupVisible && isPublic"
                    class="absolute right-0 top-full mt-2 w-80 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl shadow-xl p-4 z-50"
                  >
                    <div class="flex items-center justify-between mb-3">
                      <span class="text-xs font-bold text-slate-700 dark:text-slate-200 flex items-center gap-1.5">
                        <Globe class="w-3.5 h-3.5 text-emerald-500" />
                        Note publique
                      </span>
                      <button @click="sharePopupVisible = false" class="text-slate-400 hover:text-slate-600 transition-colors">
                        <X class="w-4 h-4" />
                      </button>
                    </div>
                    <p class="text-[11px] text-slate-500 dark:text-slate-400 mb-3">Toute personne avec ce lien peut lire cette note.</p>
                    <div class="flex items-center gap-2 bg-slate-50 dark:bg-slate-800 rounded-xl px-3 py-2">
                      <span class="text-[10px] font-mono text-slate-500 dark:text-slate-400 flex-1 truncate">{{ shareUrl }}</span>
                      <button
                        @click="copyShareLink"
                        class="shrink-0 px-2.5 py-1 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-lg transition-all active:scale-95"
                      >
                        {{ shareCopied ? 'Copié !' : 'Copier' }}
                      </button>
                    </div>
                    <button
                      @click="togglePublic"
                      class="mt-3 w-full text-xs text-rose-500 hover:text-rose-600 font-semibold transition-colors"
                    >
                      Rendre privée
                    </button>
                  </div>
                </Transition>
              </div>

              <!-- Guide Button (Edit Mode) -->
              <button 
                @click="showHelpModal = true"
                class="inline-flex items-center gap-1.5 px-3 py-1.5 border border-slate-200 dark:border-slate-800 rounded-xl text-xs font-semibold hover:bg-slate-50 dark:hover:bg-slate-850 transition-all text-slate-600 dark:text-slate-355"
                type="button"
              >
                <HelpCircle class="w-3.5 h-3.5 text-indigo-500" />
                Guide
              </button>
            </div>
          </div>

          <!-- Row 2: Formatting Toolbar -->
          <div class="flex flex-wrap items-center gap-1.5 px-6 py-2 bg-slate-50/50 dark:bg-slate-850/20">
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

            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2">Code</span>
            <button 
              v-for="btn in codeButtons" 
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
              class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-100 dark:border-emerald-900/30 rounded-xl hover:bg-emerald-100 dark:hover:bg-emerald-950/60 active:scale-95 transition-all"
              title="Associer une définition en info-bulle au texte sélectionné"
            >
              <BookOpen class="w-3.5 h-3.5" />
              Définition (Info-bulle)
            </button>

            <div class="h-4 w-[1px] bg-slate-200 dark:bg-slate-800 mx-2"></div>

            <!-- Insertion de diagramme -->
            <div class="relative inline-block">
              <select 
                @change="insertDiagramTag($event)"
                class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900/30 rounded-xl hover:bg-indigo-100 dark:hover:bg-indigo-950/60 transition-all focus:outline-none cursor-pointer"
              >
                <option value="" disabled selected>Insérer un diagramme...</option>
                <option v-for="diag in allUserDiagrams" :key="diag.id" :value="diag.id">
                  {{ diag.title }}
                </option>
                <option v-if="allUserDiagrams.length === 0" disabled>Aucun diagramme</option>
              </select>
            </div>
          </div>

          <!-- Sliding/Collapsible Drawer for Context and Links -->
          <div 
            v-if="showSettings" 
            class="grid grid-cols-1 md:grid-cols-2 gap-6 p-6 bg-slate-50/80 dark:bg-slate-900 border-b border-slate-100 dark:border-slate-800 transition-all duration-300 animate-slide-down"
          >
            <!-- 1. Context Input Section -->
            <div class="space-y-2">
              <h3 class="text-xs font-bold text-amber-700 dark:text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                <Compass class="w-4 h-4" />
                Contexte de la note
              </h3>
              <textarea 
                v-model="noteContext"
                placeholder="Historique, cadre théorique ou d'apprentissage..."
                rows="3"
                class="w-full p-3 text-xs bg-white dark:bg-slate-850 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-700 dark:text-slate-300 resize-y"
                @input="triggerAutoSave"
              ></textarea>
            </div>

            <!-- 2. Linked Notes Section -->
            <div class="space-y-3">
              <h3 class="text-xs font-bold text-indigo-700 dark:text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
                <LinkIcon class="w-4 h-4" />
                Lier à d'autres notes
              </h3>
              
              <div class="flex gap-2">
                <select 
                  v-model="selectedLinkTarget"
                  class="flex-1 px-3 py-2 bg-white dark:bg-slate-850 border border-slate-200 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-xs font-semibold"
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
                  Lier
                </button>
              </div>

              <!-- Linked notes badges -->
              <div v-if="noteLinks.length > 0" class="flex flex-wrap gap-1.5 pt-1 max-h-[80px] overflow-y-auto">
                <span 
                  v-for="linkedId in noteLinks" 
                  :key="linkedId"
                  class="inline-flex items-center gap-1.5 px-2.5 py-0.5 bg-white border border-slate-200 dark:bg-slate-800 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-[11px] font-semibold rounded-lg shadow-sm"
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

        </div>

        <!-- Split Workspace (Editor + optional Live Preview) -->
        <div class="flex-1 flex w-full overflow-hidden bg-white dark:bg-slate-900">
          <!-- Left Pane: Editor -->
          <div 
            class="flex flex-col h-full overflow-hidden cursor-text"
            :class="[isLivePreviewActive ? 'w-1/2 border-r border-slate-150 dark:border-slate-800/80' : 'w-full']"
            @click="textareaRef?.focus()"
          >
            <textarea 
              ref="textareaRef"
              v-model="noteBody"
              placeholder="Rédigez vos notes ici en Markdown..."
              class="w-full h-full p-8 md:p-12 outline-none border-0 focus:ring-0 text-base font-mono text-slate-700 dark:text-slate-300 resize-none overflow-y-auto leading-relaxed bg-transparent"
              @input="triggerAutoSave"
              @mouseup="handleTextareaSelect($event)"
              @keyup="handleTextareaSelect($event)"
              @keydown.tab.prevent="handleTabKey"
            ></textarea>
          </div>

          <!-- Right Pane: Real-time Live Preview -->
          <div 
            v-if="isLivePreviewActive"
            class="w-1/2 h-full p-8 md:p-12 overflow-y-auto bg-slate-50/30 dark:bg-slate-950/20 border-l border-slate-50 dark:border-slate-800/40 prose prose-slate max-w-none dark:prose-invert leading-relaxed text-sm dark:text-slate-300 markdown-body"
          >
            <div class="border-b border-slate-100 dark:border-slate-800/60 pb-3 mb-6 no-print">
              <span class="text-[10px] font-extrabold text-indigo-600 bg-indigo-50 dark:bg-indigo-950/40 dark:text-indigo-400 px-2.5 py-1 rounded-lg uppercase tracking-wider">Aperçu en temps réel</span>
            </div>
            <div v-html="renderMarkup(noteBody)"></div>
          </div>
        </div>

      </div>

      <!-- 2. CENTERED PREVIEW / READ MODE SHEET -->
      <div v-else class="flex-1 bg-slate-50 dark:bg-[#070913] py-10 px-4 md:px-8 print:p-0 print:bg-white w-full">
        
        <!-- Top Bar Actions inside Preview page sheet (Centered wrapper) -->
        <div class="max-w-4xl mx-auto flex items-center justify-between no-print mb-6">
          <div class="flex items-center gap-4">
            <button 
              @click="goBack" 
              class="text-sm font-semibold text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400 flex items-center gap-1"
            >
              <ChevronLeft class="w-4 h-4" />
              Retour aux notes
            </button>
            
            <div class="h-4 w-[1px] bg-slate-200 dark:bg-slate-800"></div>

            <!-- Mode Switcher: Lecture / Révision Active -->
            <div class="flex items-center bg-slate-100 dark:bg-slate-800 p-0.5 rounded-xl border border-slate-200/50 dark:border-slate-700">
              <button 
                @click="notesStore.isReviewModeActive = false"
                class="px-3 py-1.5 text-xs font-bold rounded-lg transition-all"
                :class="[!notesStore.isReviewModeActive ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-indigo-400 shadow-sm' : 'text-slate-500 hover:text-slate-700 dark:text-slate-400']"
              >
                Lecture
              </button>
              <button 
                @click="notesStore.isReviewModeActive = true"
                class="px-3 py-1.5 text-xs font-bold rounded-lg transition-all flex items-center gap-1"
                :class="[notesStore.isReviewModeActive ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-indigo-400 shadow-sm' : 'text-slate-500 hover:text-slate-700 dark:text-slate-400']"
              >
                <Brain class="w-3.5 h-3.5" />
                Révision Active
              </button>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <!-- Page blanche / Blurting (IA) -->
            <button 
              @click="router.push(`/notes/${noteId}/blurting`)"
              class="inline-flex items-center gap-2 px-4 py-2 border border-emerald-250 dark:border-emerald-900 rounded-xl text-sm font-semibold text-emerald-600 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-950/20 active:scale-95 transition-all"
            >
              <Brain class="w-4 h-4 text-emerald-500" />
              Page blanche (IA)
            </button>

            <!-- QCM (IA) -->
            <button 
              @click="router.push(`/notes/${noteId}/quiz`)"
              class="inline-flex items-center gap-2 px-4 py-2 border border-indigo-250 dark:border-indigo-900 rounded-xl text-sm font-semibold text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-950/20 active:scale-95 transition-all"
            >
              <HelpCircle class="w-4 h-4 text-indigo-500" />
              QCM (IA)
            </button>

            <!-- View Mode Toggler -->
            <button 
              @click="toggleMode"
              class="inline-flex items-center gap-2 px-4 py-2 border border-slate-200 dark:border-slate-800 rounded-xl text-sm font-semibold hover:bg-slate-50 dark:hover:bg-slate-850 transition-all text-slate-700 dark:text-slate-300"
            >
              <Edit3 class="w-4 h-4 text-indigo-500" />
              Modifier la fiche
            </button>

            <!-- Guide Button (View Mode) -->
            <button 
              @click="showHelpModal = true"
              class="inline-flex items-center gap-2 px-4 py-2 border border-slate-200 dark:border-slate-800 rounded-xl text-sm font-semibold hover:bg-slate-50 dark:hover:bg-slate-850 transition-all text-slate-650 dark:text-slate-300"
              type="button"
            >
              <HelpCircle class="w-4 h-4 text-indigo-500" />
              Guide
            </button>
            
            <!-- PDF / Print Trigger -->
            <button 
              @click="printNote"
              class="inline-flex items-center gap-2 px-4 py-2 border border-transparent rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition-all shadow-md shadow-indigo-600/10"
            >
              <FileDown class="w-4 h-4" />
              Exporter en PDF
            </button>
          </div>
        </div>

        <!-- Cohesive Paper Sheet -->
        <div class="max-w-4xl mx-auto bg-white dark:bg-slate-900 border border-slate-200/60 dark:border-slate-800 rounded-3xl p-8 lg:p-12 shadow-xl shadow-slate-200/50 dark:shadow-slate-950/40 space-y-6 print:border-none print:shadow-none print:p-0">
          
          <!-- Note Title -->
          <div class="border-b border-slate-100 dark:border-slate-800/80 pb-6 print:mb-6">
            <h1 class="text-3xl font-extrabold text-slate-900 dark:text-white print:text-black">
              {{ title || 'Note sans titre' }}
            </h1>
            <div class="flex items-center gap-3 mt-3 no-print">
              <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Classeur :</span>
              <span class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-bold text-indigo-500 bg-indigo-50 dark:bg-indigo-950/40 dark:text-indigo-400 uppercase tracking-wider">
                {{ getBinderName(binderId) }}
              </span>
              <TagBadge v-for="tag in noteTags" :key="tag.id" :tag="tag" />
            </div>
          </div>

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
          <div 
            class="prose prose-slate max-w-none dark:prose-invert leading-relaxed text-sm dark:text-slate-300 print:text-black markdown-body"
            @click="handleMarkdownClick"
          >
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
      </div>

      <!-- Help Modal (Guide for Placeholders & Split Screen) -->
      <transition 
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div 
          v-if="showHelpModal" 
          class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm no-print"
        >
          <div class="bg-white dark:bg-[#111827] border border-slate-100 dark:border-slate-800 rounded-3xl max-w-2xl w-full max-h-[85vh] overflow-y-auto p-6 shadow-2xl flex flex-col justify-between">
            <div class="space-y-6">
              <!-- Header -->
              <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                <div class="flex items-center gap-2">
                  <HelpCircle class="w-5 h-5 text-indigo-500" />
                  <h3 class="font-extrabold text-base text-slate-850 dark:text-white">Guide d'utilisation StudyHub</h3>
                </div>
                <button 
                  @click="showHelpModal = false"
                  class="p-1.5 hover:bg-slate-50 dark:hover:bg-slate-850 rounded-xl text-slate-400 dark:text-slate-500 transition-colors"
                >
                  <X class="w-5 h-5" />
                </button>
              </div>

              <!-- Content Sections -->
              <div class="space-y-5 overflow-y-auto text-xs text-slate-600 dark:text-slate-350 leading-relaxed pr-1 max-h-[60vh]">
                <!-- Section 1: Placeholders -->
                <div class="space-y-2">
                  <h4 class="font-bold text-slate-850 dark:text-white text-xs uppercase tracking-wider font-semibold">1. Syntaxes de Révision Intégrée (Active Reading)</h4>
                  <p>Incorporez des questions interactives de révision directe dans vos notes Markdown. Elles génèrent automatiquement des cartes de révision espacée (SM-2) :</p>
                  <ul class="list-disc pl-5 space-y-2.5 mt-1">
                    <li>
                      <strong class="text-indigo-600 dark:text-indigo-400">Texte à trous (Cloze) :</strong> 
                      Utilisez <code v-pre>{{trou::mot caché}}</code>.
                      <p class="text-[10px] text-slate-450 mt-0.5">Exemple : La capitale de la France est <code v-pre>{{trou::Paris}}</code>.</p>
                    </li>
                    <li>
                      <strong class="text-indigo-600 dark:text-indigo-400">Question à choix multiples (QCM) :</strong> 
                      Utilisez <code v-pre>{{qcm::Question ?::Option1|*Bonne Option*|Option3}}</code> (entourez la bonne option d'astérisques).
                      <p class="text-[10px] text-slate-450 mt-0.5">Exemple : <code v-pre>{{qcm::Combien de continents ?::4|5|*6|7*|8}}</code>.</p>
                    </li>
                    <li>
                      <strong class="text-indigo-600 dark:text-indigo-400">Ordre / Séquence :</strong> 
                      Utilisez <code v-pre>{{ordre::Titre::Étape1|Étape2|Étape3}}</code> pour ordonner des concepts.
                      <p class="text-[10px] text-slate-450 mt-0.5">Exemple : Cycle de l'eau : <code v-pre>{{ordre::Étapes::Évaporation|Condensation|Précipitations}}</code>.</p>
                    </li>
                    <li>
                      <strong class="text-indigo-600 dark:text-indigo-400">Associations :</strong> 
                      Utilisez <code v-pre>{{assoc::Titre::Clé 1: Valeur 1|Clé 2: Valeur 2}}</code>.
                      <p class="text-[10px] text-slate-450 mt-0.5">Exemple : Assigner pays/capitales : <code v-pre>{{assoc::Capitales::France: Paris|Italie: Rome}}</code>.</p>
                    </li>
                    <li>
                      <strong class="text-indigo-600 dark:text-indigo-400">Vrai / Faux :</strong> 
                      Utilisez <code v-pre>{{vf::Affirmation::vrai/faux|Justification}}</code>.
                      <p class="text-[10px] text-slate-450 mt-0.5">Exemple : <code v-pre>{{vf::La Terre est plate::faux|Elle a la forme d'un géoïde.}}</code>.</p>
                    </li>
                  </ul>
                </div>

                <!-- Section 2: Split Screen -->
                <div class="space-y-2 border-t border-slate-100 dark:border-slate-800/60 pt-4">
                  <h4 class="font-bold text-slate-850 dark:text-white text-xs uppercase tracking-wider font-semibold">2. Écran Partagé & Liaisons PDF</h4>
                  <p>Étudiez vos PDF de cours tout en rédigeant ou révisant vos notes :</p>
                  <ul class="list-disc pl-5 space-y-2.5 mt-1">
                    <li>
                      <strong class="text-indigo-600 dark:text-indigo-400">Démarrer l'écran partagé :</strong> 
                      Sélectionnez un document PDF dans la liste déroulante <strong class="text-slate-800 dark:text-white font-semibold">"Aperçu PDF"</strong> en haut à droite de l'éditeur de notes. Le PDF s'affichera à gauche.
                    </li>
                    <li>
                      <strong class="text-indigo-600 dark:text-indigo-400">Créer une citation (Deep Link) :</strong> 
                      Sélectionnez du texte dans le panneau PDF, puis cliquez sur le bouton <strong class="text-indigo-600 dark:text-indigo-400">"Citer"</strong> qui apparaît au-dessus du texte. Cela insère un lien spécial de type <code v-pre>pdf://</code> dans votre note.
                    </li>
                    <li>
                      <strong class="text-indigo-600 dark:text-indigo-400">Naviguer à partir d'un lien :</strong> 
                      Dans le mode visualisation de la note, cliquez sur un de vos liens de citation. Le PDF s'ouvrira automatiquement sur la bonne page et la zone correspondante sera surlignée.
                    </li>
                  </ul>
                </div>

                <!-- Section 3: Image Occlusion -->
                <div class="space-y-2 border-t border-slate-100 dark:border-slate-800/60 pt-4">
                  <h4 class="font-bold text-slate-850 dark:text-white text-xs uppercase tracking-wider font-semibold">3. Masques d'Image (Occlusion)</h4>
                  <p>Dans le module <strong class="text-slate-800 dark:text-white font-semibold">Diagrammes</strong>, importez un schéma (corps humain, géographie, formule), tracez des rectangles de masquage opaques sur les parties à deviner, puis nommez-les. En mode révision, cliquez sur les masques pour les révéler et évaluer votre mémorisation.</p>
                </div>
              </div>
            </div>

            <!-- Footer -->
            <div class="border-t border-slate-100 dark:border-slate-800 pt-4 mt-4 flex justify-end">
              <button 
                @click="showHelpModal = false"
                class="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-all active:scale-95 shadow-md shadow-indigo-600/10"
              >
                Compris !
              </button>
            </div>
          </div>
        </div>
      </transition>

      <!-- ============================================================ -->
      <!-- INPUT MODAL (remplace les prompt/confirm/alert natifs)       -->
      <!-- ============================================================ -->
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="inputModal.visible"
          class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm no-print"
          @click.self="inputModal.onCancel()"
        >
          <Transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="opacity-0 scale-95 translate-y-2"
            enter-to-class="opacity-100 scale-100 translate-y-0"
          >
            <div
              v-if="inputModal.visible"
              class="w-full max-w-md bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-100 dark:border-slate-800 overflow-hidden custom-input-modal"
            >
              <!-- Header -->
              <div class="px-6 pt-6 pb-4 flex items-start gap-4 input-modal-header">
                <div
                  class="flex items-center justify-center w-11 h-11 rounded-2xl flex-shrink-0 text-white shadow-lg"
                  :class="inputModal.iconBg || 'bg-indigo-500'"
                >
                  <component :is="inputModal.icon" class="w-5 h-5" />
                </div>
                <div class="flex-1 min-w-0">
                  <h3 class="font-bold text-slate-900 dark:text-white text-base input-modal-title">{{ inputModal.title }}</h3>
                  <p v-if="inputModal.description" class="text-xs text-slate-500 dark:text-slate-400 input-modal-desc">{{ inputModal.description }}</p>
                </div>
                <button @click="inputModal.onCancel()" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors mt-0.5">
                  <X class="w-5 h-5" />
                </button>
              </div>

              <!-- Fields -->
              <div class="px-6 pb-2 space-y-3">
                <div v-for="(field, i) in inputModal.fields" :key="i">
                  <label class="block text-xs font-bold text-slate-600 dark:text-slate-400 mb-1.5 uppercase tracking-wider">{{ field.label }}</label>

                  <!-- Texte -->
                  <input
                    v-if="field.type === 'text' || field.type === 'textarea'"
                    v-model="field.value"
                    :placeholder="field.placeholder || ''"
                    :ref="i === 0 ? 'modalFirstInput' : undefined"
                    class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                    @keydown.enter.prevent="inputModal.onConfirm()"
                    @keydown.escape.prevent="inputModal.onCancel()"
                  />

                  <!-- Booléen (Vrai / Faux) -->
                  <div v-else-if="field.type === 'bool'" class="flex gap-3">
                    <button
                      @click="field.value = true"
                      class="flex-1 py-2.5 rounded-xl text-sm font-bold border-2 transition-all"
                      :class="field.value === true ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-950/30 text-emerald-600 dark:text-emerald-400' : 'border-slate-200 dark:border-slate-700 text-slate-500 hover:border-emerald-300'"
                    >
                      ✓ Vrai
                    </button>
                    <button
                      @click="field.value = false"
                      class="flex-1 py-2.5 rounded-xl text-sm font-bold border-2 transition-all"
                      :class="field.value === false ? 'border-rose-500 bg-rose-50 dark:bg-rose-950/30 text-rose-600 dark:text-rose-400' : 'border-slate-200 dark:border-slate-700 text-slate-500 hover:border-rose-300'"
                    >
                      ✗ Faux
                    </button>
                  </div>

                  <!-- Select diagramme -->
                  <select
                    v-else-if="field.type === 'select'"
                    v-model="field.value"
                    class="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                  >
                    <option v-for="opt in field.options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                  </select>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex gap-3 px-6 py-5">
                <button
                  @click="inputModal.onCancel()"
                  class="flex-1 py-2.5 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all"
                >
                  Annuler
                </button>
                <button
                  @click="inputModal.onConfirm()"
                  class="flex-1 py-2.5 rounded-xl text-sm font-bold text-white transition-all active:scale-95 shadow-md"
                  :class="inputModal.confirmBg || 'bg-indigo-600 hover:bg-indigo-700 shadow-indigo-600/20'"
                >
                  {{ inputModal.confirmLabel || 'Confirmer' }}
                </button>
              </div>
            </div>
          </Transition>
        </div>
      </Transition>

      <!-- SM-2 Evaluation Modal -->
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="evaluationModal.visible"
          class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm no-print"
          @click.self="evaluationModal.visible = false"
        >
          <Transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="opacity-0 scale-95 translate-y-2"
            enter-to-class="opacity-100 scale-100 translate-y-0"
          >
            <div
              v-if="evaluationModal.visible"
              class="w-full max-w-sm bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-3xl shadow-2xl p-6 text-center sm2-modal-container"
            >
              <!-- Icon/Header -->
              <div class="flex flex-col items-center mb-3">
                <div class="w-10 h-10 bg-indigo-50 dark:bg-indigo-950/50 rounded-2xl flex items-center justify-center text-indigo-600 dark:text-indigo-400 mb-2 border border-indigo-100 dark:border-indigo-900/40">
                  <Sparkles class="w-5 h-5 animate-pulse" />
                </div>
                <h3 class="font-extrabold text-slate-900 dark:text-white text-base sm2-modal-title">C'était facile ?</h3>
                <p class="text-xs text-slate-500 dark:text-slate-400 sm2-modal-desc">Évaluez votre niveau de rappel pour l'algorithme d'apprentissage.</p>
              </div>

              <!-- Buttons Grid -->
              <div class="grid grid-cols-2 gap-2.5 mb-4">
                <button
                  v-for="btn in evaluationButtons"
                  :key="btn.val"
                  @click="submitSm2Evaluation(btn.val)"
                  :disabled="isEvaluating"
                  class="flex flex-col items-center border-2 rounded-2xl transition-all hover:scale-[1.02] active:scale-95 disabled:opacity-50 disabled:pointer-events-none sm2-modal-btn"
                  :class="btn.class"
                >
                  <span class="text-2xl sm2-btn-emoji">{{ btn.emoji }}</span>
                  <span class="text-xs font-bold sm2-btn-label">{{ btn.label }}</span>
                  <span class="text-[9px] opacity-60 sm2-btn-desc">{{ btn.desc }}</span>
                </button>
              </div>

              <!-- Actions -->
              <button
                @click="evaluationModal.visible = false"
                class="w-full py-2 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-bold text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all sm2-modal-cancel"
              >
                Passer sans évaluer
              </button>
            </div>
          </Transition>
        </div>
      </Transition>

      <!-- Floating Selection Action Bar -->
      <transition 
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div 
          v-if="showSelectionMenu && isEditMode" 
          class="fixed z-50 bottom-6 left-1/2 -translate-x-1/2 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border border-slate-200 dark:border-slate-700 rounded-2xl shadow-2xl px-4 py-2.5 flex items-center flex-wrap gap-2.5 max-w-[95vw] no-print pointer-events-auto"
        >
          <div class="flex items-center gap-1.5 border-r border-slate-200 dark:border-slate-800 pr-3 max-w-[150px]">
            <Sparkles class="w-3.5 h-3.5 text-indigo-500 flex-shrink-0 animate-pulse" />
            <span class="text-[11px] font-bold text-slate-500 dark:text-slate-400 truncate">
              "{{ selectionText }}"
            </span>
          </div>

          <div class="flex items-center gap-1 flex-wrap max-w-lg md:max-w-none">
            <!-- Trou Button -->
            <button 
              @click="applySelectionTransform('trou')"
              class="px-2 py-1 bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-950/40 dark:hover:bg-indigo-950/80 text-indigo-600 dark:text-indigo-400 rounded-lg text-[9px] font-extrabold uppercase tracking-wider transition-all active:scale-95 flex items-center gap-1"
              title="Trou (Cloze)"
            >
              <Brain class="w-2.5 h-2.5" />
              Trou
            </button>

            <!-- QCM Button -->
            <button 
              @click="applySelectionTransform('qcm')"
              class="px-2 py-1 bg-purple-50 hover:bg-purple-100 dark:bg-purple-950/40 dark:hover:bg-purple-950/80 text-purple-600 dark:text-purple-400 rounded-lg text-[9px] font-extrabold uppercase tracking-wider transition-all active:scale-95 flex items-center gap-1"
              title="QCM (Choix multiples)"
            >
              <HelpCircle class="w-2.5 h-2.5" />
              QCM
            </button>

            <!-- Sequence / Ordre Button -->
            <button 
              @click="applySelectionTransform('ordre')"
              class="px-2 py-1 bg-amber-50 hover:bg-amber-100 dark:bg-amber-950/40 dark:hover:bg-amber-950/80 text-amber-600 dark:text-amber-455 rounded-lg text-[9px] font-extrabold uppercase tracking-wider transition-all active:scale-95 flex items-center gap-1"
              title="Séquence (Ordre)"
            >
              <ListOrdered class="w-2.5 h-2.5" />
              Ordre
            </button>

            <!-- Association Button -->
            <button 
              @click="applySelectionTransform('assoc')"
              class="px-2 py-1 bg-pink-50 hover:bg-pink-100 dark:bg-pink-950/40 dark:hover:bg-pink-950/80 text-pink-600 dark:text-pink-400 rounded-lg text-[9px] font-extrabold uppercase tracking-wider transition-all active:scale-95 flex items-center gap-1"
              title="Association"
            >
              <LinkIcon class="w-2.5 h-2.5" />
              Assoc
            </button>

            <!-- Vrai/Faux Button -->
            <button 
              @click="applySelectionTransform('vf')"
              class="px-2 py-1 bg-rose-50 hover:bg-rose-100 dark:bg-rose-950/40 dark:hover:bg-rose-950/80 text-rose-600 dark:text-rose-400 rounded-lg text-[9px] font-extrabold uppercase tracking-wider transition-all active:scale-95 flex items-center gap-1"
              title="Vrai / Faux"
            >
              <CheckCircle2 class="w-2.5 h-2.5" />
              V/F
            </button>

            <!-- Definition Tooltip Button -->
            <button 
              @click="applySelectionTransform('def')"
              class="px-2 py-1 bg-emerald-50 hover:bg-emerald-100 dark:bg-emerald-950/40 dark:hover:bg-emerald-950/80 text-emerald-600 dark:text-emerald-455 rounded-lg text-[9px] font-extrabold uppercase tracking-wider transition-all active:scale-95 flex items-center gap-1"
              title="Définition info-bulle"
            >
              <BookOpen class="w-2.5 h-2.5" />
              Définition
            </button>

            <!-- Math Bloc Button -->
            <button 
              @click="applySelectionTransform('math_bloc')"
              class="px-2 py-1 bg-cyan-50 hover:bg-cyan-100 dark:bg-cyan-950/40 dark:hover:bg-cyan-950/80 text-cyan-600 dark:text-cyan-400 rounded-lg text-[9px] font-extrabold uppercase tracking-wider transition-all active:scale-95 flex items-center gap-1"
              title="Math Bloc (LaTeX)"
            >
              <Sigma class="w-2.5 h-2.5" />
              Math Bloc
            </button>

            <!-- Math Ligne Button -->
            <button 
              @click="applySelectionTransform('math_ligne')"
              class="px-2 py-1 bg-teal-50 hover:bg-teal-100 dark:bg-teal-950/40 dark:hover:bg-teal-950/80 text-teal-600 dark:text-teal-400 rounded-lg text-[9px] font-extrabold uppercase tracking-wider transition-all active:scale-95 flex items-center gap-1"
              title="Math Ligne (LaTeX)"
            >
              <Sigma class="w-2.5 h-2.5" />
              Math Ligne
            </button>

            <!-- Diagramme Button -->
            <button 
              @click="applySelectionTransform('diagramme')"
              class="px-2 py-1 bg-sky-50 hover:bg-sky-100 dark:bg-sky-950/40 dark:hover:bg-sky-950/80 text-sky-600 dark:text-sky-400 rounded-lg text-[9px] font-extrabold uppercase tracking-wider transition-all active:scale-95 flex items-center gap-1"
              title="Insérer un diagramme / schéma"
            >
              <Image class="w-2.5 h-2.5" />
              Schéma
            </button>

            <div class="h-4 w-[1px] bg-slate-200 dark:bg-slate-800 mx-1"></div>

            <!-- Bold Button -->
            <button 
              @click="applySelectionTransform('gras')"
              class="px-1.5 py-1 hover:bg-slate-100 dark:hover:bg-slate-850 text-slate-700 dark:text-slate-355 rounded-lg text-[9px] font-bold transition-all active:scale-95"
              title="Gras"
            >
              <strong>G</strong>
            </button>

            <!-- Italic Button -->
            <button 
              @click="applySelectionTransform('italique')"
              class="px-1.5 py-1 hover:bg-slate-100 dark:hover:bg-slate-850 text-slate-700 dark:text-slate-355 rounded-lg text-[9px] font-bold transition-all active:scale-95 italic"
              title="Italique"
            >
              I
            </button>

            <!-- Code Button (Inline) -->
            <button 
              @click="applySelectionTransform('code')"
              class="px-1.5 py-1 hover:bg-slate-100 dark:hover:bg-slate-850 text-slate-700 dark:text-slate-355 rounded-lg text-[9px] font-mono font-bold transition-all active:scale-95"
              title="Code en ligne"
            >
              &lt;/&gt;
            </button>

            <!-- Bloc Code Button -->
            <button 
              @click="applySelectionTransform('bloc_code')"
              class="px-1.5 py-1 hover:bg-slate-100 dark:hover:bg-slate-850 text-slate-700 dark:text-slate-355 rounded-lg text-[9px] font-mono font-bold transition-all active:scale-95"
              title="Bloc de code"
            >
              { }
            </button>
          </div>
        </div>
      </transition>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'
import { useNotesStore } from '../../stores/notes'
import { useBindersStore } from '../../stores/binders'
import { useTagsStore, type Tag } from '../../stores/tags'
import TagBadge from '../../components/ui/TagBadge.vue'
import TagSelector from '../../components/ui/TagSelector.vue'
import { 
  ChevronLeft,
  Menu,
  Eye, 
  Edit3, 
  FileDown,
  BookOpen,
  Compass,
  Link as LinkIcon,
  ChevronRight,
  Brain,
  HelpCircle,
  X,
  Globe,
  Columns,
  ListOrdered,
  CheckCircle2,
  Sparkles,
  Sigma,
  Image
} from '@lucide/vue'
import { marked } from 'marked'
import katex from 'katex'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

// Import KaTeX styles for formula rendering
import 'katex/dist/katex.min.css'

// Configure marked to use highlight.js for syntax highlighting in code blocks
marked.use({
  breaks: true,
  gfm: true,
  renderer: {
    code({ text, lang }: { text: string; lang?: string }) {
      const language = lang && hljs.getLanguage(lang) ? lang : 'plaintext'
      const highlighted = hljs.highlight(text, { language }).value
      return `<pre><code class="hljs language-${language}">${highlighted}</code></pre>`
    }
  }
})

const notesStore = useNotesStore()
const bindersStore = useBindersStore()
const tagsStore = useTagsStore()

const placeholderStates = ref<Record<string, any>>({})
const noteFlashcards = ref<any[]>([])
const route = useRoute()
const router = useRouter()

const noteId = ref(Number(route.params.id))
const allUserDiagrams = ref<any[]>([])
const loadedDiagrams = ref<Record<number, any>>({})
const loading = ref(true)
const isSaving = ref(false)
const saveStatus = ref('Enregistré')
const isEditMode = computed({
  get: () => route.query.edit === 'true',
  set: (val) => {
    router.replace({ query: { ...route.query, edit: val ? 'true' : undefined } })
  }
})
const showSettings = ref(false)
const showHelpModal = ref(false)
const isLivePreviewActive = ref(false)

function toggleShortcutSidebar() {
  window.dispatchEvent(new CustomEvent('studyhub:toggle-sidebar'))
}

// Evaluation SM-2 Popup Modal State
const evaluationModal = ref({
  visible: false,
  cardId: null as number | null,
  rawTag: ''
})

const evaluationButtons = [
  { val: 1, label: 'À revoir', emoji: '🔁', desc: 'Pas retenu', class: 'border-rose-100 dark:border-rose-950/40 bg-rose-50 hover:bg-rose-100 dark:bg-rose-950/20 text-rose-600 dark:text-rose-400 hover:border-rose-350' },
  { val: 2, label: 'Difficile', emoji: '😕', desc: 'Gros effort', class: 'border-amber-100 dark:border-amber-950/40 bg-amber-50 hover:bg-amber-100 dark:bg-amber-950/20 text-amber-600 dark:text-amber-400 hover:border-amber-350' },
  { val: 3, label: 'Correct', emoji: '🙂', desc: 'Rappel normal', class: 'border-emerald-100 dark:border-emerald-950/40 bg-emerald-50 hover:bg-emerald-100 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400 hover:border-emerald-350' },
  { val: 5, label: 'Facile', emoji: '😎', desc: 'Aucun effort', class: 'border-blue-100 dark:border-blue-950/40 bg-blue-50 hover:bg-blue-100 dark:bg-blue-950/20 text-blue-600 dark:text-blue-400 hover:border-blue-350' }
]

const isEvaluating = ref(false)

function openEvaluationModal(cardId: number, rawTag: string) {
  evaluationModal.value = {
    visible: true,
    cardId,
    rawTag
  }
}

async function submitSm2Evaluation(score: number) {
  const { cardId, rawTag } = evaluationModal.value
  if (!cardId || !rawTag) return
  
  try {
    isEvaluating.value = true
    await api.patch(`/flashcards/${cardId}/review`, { score })
    
    const state = placeholderStates.value[rawTag]
    if (state) {
      state.score = score
      placeholderStates.value = { ...placeholderStates.value }
    }
    
    evaluationModal.value.visible = false
  } catch (err) {
    console.error('Erreur lors du vote SM-2', err)
    alert("Erreur lors de l'enregistrement de l'évaluation.")
  } finally {
    isEvaluating.value = false
  }
}

const selectionText = ref('')
const selectionStart = ref(0)
const selectionEnd = ref(0)
const savedSelectionContent = ref('')  // snapshot du textarea au moment de la sélection
const showSelectionMenu = ref(false)
const selectionMenuPos = ref({ top: 0, left: 0 })

// ---------------------------------------------------------------
// Modal stylisé (remplace prompt / confirm / alert)
// ---------------------------------------------------------------
interface ModalField {
  label: string
  type: 'text' | 'bool' | 'select' | 'textarea'
  value: any
  placeholder?: string
  options?: { value: any; label: string }[]
}
interface ModalConfig {
  visible: boolean
  title: string
  description?: string
  icon: any
  iconBg?: string
  confirmBg?: string
  confirmLabel?: string
  fields: ModalField[]
  onConfirm: () => void
  onCancel: () => void
}

const inputModal = ref<ModalConfig>({
  visible: false,
  title: '',
  icon: null,
  fields: [],
  onConfirm: () => {},
  onCancel: () => {}
})

function openModal(config: Omit<ModalConfig, 'visible' | 'onConfirm' | 'onCancel'>): Promise<ModalField[] | null> {
  return new Promise((resolve) => {
    inputModal.value = {
      ...config,
      visible: true,
      onConfirm: () => {
        inputModal.value.visible = false
        resolve([...inputModal.value.fields])
      },
      onCancel: () => {
        inputModal.value.visible = false
        resolve(null)
      }
    }
    // Focus le premier champ après rendu
    setTimeout(() => {
      const el = document.querySelector<HTMLElement>('.modal-first-input')
      el?.focus()
    }, 50)
  })
}

const title = ref('')
const binderId = ref<number | null>(null)
const noteTags = ref<Tag[]>([])
const isPublic = ref(false)
const shareToken = ref<string | null>(null)
const sharePopupVisible = ref(false)
const shareCopied = ref(false)
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

const codeButtons = [
  { label: 'En Ligne', prefix: '`', suffix: '`' },
  { label: 'Bloc Code', prefix: '```\n', suffix: '\n```' }
]

// Reload components when route parameter changes (for linked notes navigation)
watch(() => route.params.id, async (newVal) => {
  if (newVal) {
    noteId.value = Number(newVal)
    await loadNoteDetails()
  }
})

onMounted(async () => {
  await Promise.all([
    notesStore.fetchNotes(),
    bindersStore.fetchBinders(),
    tagsStore.fetchTags()
  ])
  await loadUserDiagrams()
  await loadNoteDetails()
})

onBeforeUnmount(() => {
  if (autoSaveTimer) clearTimeout(autoSaveTimer)
})

async function loadUserDiagrams() {
  try {
    const res = await api.get('/diagrams?per_page=1000')
    allUserDiagrams.value = res.data.data
  } catch (err) {
    console.error('Erreur lors du chargement des diagrammes', err)
  }
}

async function fetchDiagramIfNeeded(id: number) {
  if (loadedDiagrams.value[id] !== undefined) return
  try {
    const res = await api.get(`/diagrams/${id}`)
    loadedDiagrams.value[id] = res.data
  } catch (err) {
    console.error(`Erreur de chargement du diagramme ${id}`, err)
    loadedDiagrams.value[id] = null
  }
}

watch(noteBody, (newVal) => {
  const matches = newVal.matchAll(/\[diagram:(\d+)\]/g)
  for (const match of matches) {
    const id = Number(match[1])
    fetchDiagramIfNeeded(id)
  }
}, { immediate: true })

function insertDiagramTag(event: Event) {
  const select = event.target as HTMLSelectElement
  const id = select.value
  if (!id) return
  
  insertText(`[diagram:${id}]`, '')
  select.value = '' // Reset
}

async function loadNoteDetails() {
  loading.value = true
  isSaving.value = false
  saveStatus.value = 'Enregistré'
  
  const note = await notesStore.fetchNoteById(noteId.value)
  if (note) {
    title.value = note.title
    binderId.value = note.binder_id
    isPublic.value = (note as any).is_public || false
    shareToken.value = (note as any).share_token || null
    noteFlashcards.value = (note as any).flashcards || []
    noteTags.value = (note as any).tags || []
    
    // Parse structured divisions
    const parsed = parseStructuredNote(note.content)
    noteContext.value = parsed.context
    noteDefinition.value = parsed.definition
    noteBody.value = parsed.body
    noteLinks.value = parsed.linkedIds
    
    if (route.query.edit === 'true') {
      isEditMode.value = true
    } else if (route.query.edit === 'false') {
      isEditMode.value = false
    } else if (note.title === 'Note sans titre') {
      isEditMode.value = true
    } else {
      isEditMode.value = false
    }
  }
  loading.value = false
}

async function togglePublic() {
  const newVal = !isPublic.value
  try {
    const { data } = await api.patch(`/notes/${noteId.value}/visibility`, { is_public: newVal })
    isPublic.value = data.is_public
    shareToken.value = data.share_token || null
    if (newVal) sharePopupVisible.value = true
  } catch (e) {
    console.error('Erreur toggle visibilité', e)
  }
}

function handleShareClick() {
  if (isPublic.value) {
    sharePopupVisible.value = !sharePopupVisible.value
  } else {
    togglePublic()
  }
}

const shareUrl = computed(() => {
  if (!shareToken.value) return ''
  return `${window.location.origin}/notes/public/${shareToken.value}`
})

async function copyShareLink() {
  try {
    await navigator.clipboard.writeText(shareUrl.value)
    shareCopied.value = true
    setTimeout(() => { shareCopied.value = false }, 2000)
  } catch {}
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
function renderSm2Buttons(cardId: number | null, rawTag: string): string {
  if (!cardId) return `<span class="text-[10px] text-slate-450 italic font-semibold align-middle">En attente de sauvegarde...</span>`;
  const state = placeholderStates.value[rawTag];
  if (!state || state.score === undefined) return '';
  
  const buttons = [
    { label: "À revoir", val: 1 },
    { label: "Difficile", val: 2 },
    { label: "Correct", val: 3 },
    { label: "Facile", val: 5 }
  ];
  
  const b = buttons.find(x => x.val === state.score);
  return `<button type="button" data-action="sm2-re-evaluate" data-card-id="${cardId}" data-tag="${encodeURIComponent(rawTag)}" class="ml-1.5 inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-950/40 dark:hover:bg-indigo-900/50 text-[9px] font-bold text-indigo-650 dark:text-indigo-400 border border-indigo-100 dark:border-indigo-900/50 align-middle transition-all cursor-pointer">★ ${b ? b.label : state.score}</button>`;
}

// Rendering marked + LaTeX + Definition tooltips + Active Reading Placeholders
function renderMarkup(text: string): string {
  const normalizedText = (text || '').replace(/\r\n/g, '\n')
  let temp = normalizedText.replace(/\n{3,}/g, (match) => {
    const count = match.length - 2
    return '\n\n' + Array(count).fill('&nbsp;').join('\n\n') + '\n\n'
  })
  const placeholders: string[] = []

  // 1. Double dollars $$ (Display equations block)
  temp = temp.replace(/\$\$([\s\S]+?)\$\$/g, (_match, formula) => {
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

  // 4. Diagram Integration [diagram:ID]
  temp = temp.replace(/\[diagram:(\d+)\]/g, (_match, idStr) => {
    const id = Number(idStr)
    const diag = loadedDiagrams.value[id]
    
    let html = ''
    if (diag === undefined) {
      html = `
        <div class="flex items-center gap-2 p-4 border border-slate-100 dark:border-slate-800 rounded-2xl bg-slate-50/20 text-xs font-semibold text-slate-400 my-4 select-none">
          <svg class="animate-spin h-4 w-4 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Chargement du schéma #${id}...
        </div>
      `
    } else {
      html = renderDiagramHtml(diag)
    }
    
    const key = `DIAGRAMPLACEHOLDER${placeholders.length}`
    placeholders.push(html)
    return key
  })

  const isReview = notesStore.isReviewModeActive;
  const shuffleArray = (arr: any[]) => arr.map((a: any) => [Math.random(), a]).sort((a: any, b: any) => a[0] - b[0]).map((a: any) => a[1]);

  // Trou: {{trou::mot caché}}
  temp = temp.replace(/\{\{trou::(.*?)\}\}/g, (rawTag, word) => {
    const card = noteFlashcards.value.find(c => c.original_text === rawTag);
    const cardId = card ? card.id : null;
    
    if (!isReview) {
      const displayHtml = `<span class="bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 px-1.5 py-0.5 rounded font-semibold border-b border-indigo-500">${word}</span>`;
      const key = `REVISIONPLACEHOLDER${placeholders.length}`;
      placeholders.push(displayHtml);
      return key;
    } else {
      placeholderStates.value[rawTag] = placeholderStates.value[rawTag] || { revealed: false };
      const state = placeholderStates.value[rawTag];
      
      let elementHtml = "";
      if (!state.revealed) {
        elementHtml = `<span class="px-2.5 py-0.5 bg-slate-200 dark:bg-slate-750 text-transparent rounded-lg cursor-pointer border border-slate-300 dark:border-slate-600 select-none hover:bg-slate-300 hover:text-slate-500/10 active:scale-95 transition-all inline-block align-middle font-mono font-bold" data-action="reveal" data-tag="${encodeURIComponent(rawTag)}">???</span>`;
      } else {
        elementHtml = `<span class="bg-indigo-50/80 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 px-2 py-0.5 rounded-lg font-bold border-b border-indigo-400 inline-flex items-center align-middle select-all transition-all">${word}${renderSm2Buttons(cardId, rawTag)}</span>`;
      }
      const key = `REVISIONPLACEHOLDER${placeholders.length}`;
      placeholders.push(elementHtml);
      return key;
    }
  });

  // QCM: {{qcm::Question ?::Option1|*OptionCorrecte*|Option3}}
  temp = temp.replace(/\{\{qcm::(.*?)::(.*?)\}\}/g, (rawTag, question, optionsStr) => {
    const card = noteFlashcards.value.find(c => c.original_text === rawTag);
    const cardId = card ? card.id : null;
    const options = optionsStr.split('|').map((o: string) => o.trim());
    
    if (!isReview) {
      const listItems = options.map((opt: string) => {
        const isCorrect = opt.startsWith('*') && opt.endsWith('*');
        const cleanOpt = opt.replace(/\*/g, '');
        return isCorrect 
          ? `<li class="font-extrabold text-emerald-600 dark:text-emerald-400">✓ ${cleanOpt} (Correct)</li>`
          : `<li>${cleanOpt}</li>`;
      }).join('');
      
      const displayHtml = `
        <div class="bg-slate-50/50 dark:bg-slate-900/50 p-4 border border-slate-200 dark:border-slate-800 rounded-2xl my-4 max-w-2xl shadow-sm not-prose">
          <strong class="text-[10px] uppercase tracking-wider text-slate-450 font-bold block mb-1">QCM</strong>
          <p class="font-bold text-sm text-slate-800 dark:text-slate-100 mb-2">${question}</p>
          <ul class="list-none pl-0 mt-2 space-y-1 text-xs text-slate-600 dark:text-slate-400">${listItems}</ul>
        </div>
      `;
      const key = `REVISIONPLACEHOLDER${placeholders.length}`;
      placeholders.push(displayHtml);
      return '\n\n' + key + '\n\n';
    } else {
      placeholderStates.value[rawTag] = placeholderStates.value[rawTag] || { answered: false, selectedOption: null };
      const state = placeholderStates.value[rawTag];
      
      const buttonsHtml = options.map((opt: string) => {
        const isCorrect = opt.startsWith('*') && opt.endsWith('*');
        const cleanOpt = opt.replace(/\*/g, '');
        let btnClass = "px-3 py-1.5 border border-slate-200 dark:border-slate-800 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-850 text-xs font-semibold transition-all active:scale-95";
        
        if (state.answered) {
          if (isCorrect) {
            btnClass = "px-3 py-1.5 bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-300 dark:border-emerald-900 text-emerald-600 dark:text-emerald-400 rounded-xl text-xs font-bold";
          } else if (state.selectedOption === cleanOpt) {
            btnClass = "px-3 py-1.5 bg-rose-50 dark:bg-rose-950/20 border border-rose-300 dark:border-rose-900 text-rose-600 dark:text-rose-450 rounded-xl text-xs font-bold";
          } else {
            btnClass = "px-3 py-1.5 border border-slate-100 dark:border-slate-850 opacity-40 rounded-xl text-xs font-semibold";
          }
        }
        return `<button type="button" class="${btnClass}" data-action="qcm-select" data-tag="${encodeURIComponent(rawTag)}" data-option="${encodeURIComponent(cleanOpt)}" ${state.answered ? 'disabled' : ''}>${cleanOpt}</button>`;
      }).join(' ');
      
      const elementHtml = `
        <div class="bg-slate-50/50 dark:bg-slate-900/50 p-4 border border-slate-200 dark:border-slate-800 rounded-2xl my-4 max-w-2xl shadow-sm not-prose">
          <div class="flex items-center justify-between mb-1.5">
            <strong class="text-[10px] uppercase tracking-wider text-slate-450 font-bold">QCM</strong>
            ${state.answered ? renderSm2Buttons(cardId, rawTag) : ''}
          </div>
          <p class="font-bold text-sm text-slate-800 dark:text-slate-100 mb-3">${question}</p>
          <div class="flex flex-wrap gap-2">${buttonsHtml}</div>
        </div>
      `;
      const key = `REVISIONPLACEHOLDER${placeholders.length}`;
      placeholders.push(elementHtml);
      return '\n\n' + key + '\n\n';
    }
  });

  // VF: {{vf::Affirmation::Vrai/Faux::Justification}}
  temp = temp.replace(/\{\{vf::(.*?)::(.*?)::(.*?)\}\}/g, (rawTag, assertion, answer, justification) => {
    const card = noteFlashcards.value.find(c => c.original_text === rawTag);
    const cardId = card ? card.id : null;
    const isVrai = answer.trim().toLowerCase() === "vrai";
    
    if (!isReview) {
      const displayHtml = `
        <div class="bg-slate-50/50 dark:bg-slate-900/50 p-4 border border-slate-200 dark:border-slate-800 rounded-2xl my-4 max-w-2xl shadow-sm not-prose">
          <strong class="text-[10px] uppercase tracking-wider text-slate-450 font-bold block mb-1">Vrai ou Faux</strong>
          <p class="font-semibold text-sm text-slate-800 dark:text-slate-100">${assertion}</p>
          <div class="mt-2 text-xs font-bold">Réponse : <span class="${isVrai ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}">${answer}</span></div>
          <div class="text-xs text-slate-500 dark:text-slate-400 italic mt-1">${justification}</div>
        </div>
      `;
      const key = `REVISIONPLACEHOLDER${placeholders.length}`;
      placeholders.push(displayHtml);
      return '\n\n' + key + '\n\n';
    } else {
      placeholderStates.value[rawTag] = placeholderStates.value[rawTag] || { answered: false, selectedAnswer: null };
      const state = placeholderStates.value[rawTag];
      
      const btns = ["Vrai", "Faux"].map(btnVal => {
        let btnClass = "px-4 py-2 border border-slate-200 dark:border-slate-800 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 text-xs font-bold transition-all active:scale-95";
        const isThisCorrect = btnVal.toLowerCase() === answer.trim().toLowerCase();
        
        if (state.answered) {
          if (isThisCorrect) {
            btnClass = "px-4 py-2 bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-300 dark:border-emerald-900 text-emerald-600 dark:text-emerald-400 rounded-xl text-xs font-bold";
          } else if (state.selectedAnswer === btnVal) {
            btnClass = "px-4 py-2 bg-rose-50 dark:bg-rose-950/20 border border-rose-300 dark:border-rose-900 text-rose-600 dark:text-rose-455 rounded-xl text-xs font-bold";
          } else {
            btnClass = "px-4 py-2 border border-slate-100 dark:border-slate-850 opacity-40 rounded-xl text-xs font-bold";
          }
        }
        return `<button type="button" class="${btnClass}" data-action="vf-select" data-tag="${encodeURIComponent(rawTag)}" data-value="${btnVal}" ${state.answered ? 'disabled' : ''}>${btnVal}</button>`;
      }).join(' ');
      
      const elementHtml = `
        <div class="bg-slate-50/50 dark:bg-slate-900/50 p-4 border border-slate-200 dark:border-slate-800 rounded-2xl my-4 max-w-2xl shadow-sm not-prose">
          <div class="flex items-center justify-between mb-1.5">
            <strong class="text-[10px] uppercase tracking-wider text-slate-450 font-bold">Vrai ou Faux</strong>
            ${state.answered ? renderSm2Buttons(cardId, rawTag) : ''}
          </div>
          <p class="font-semibold text-sm text-slate-800 dark:text-slate-100 mb-3">${assertion}</p>
          <div class="flex gap-3 mb-3">${btns}</div>
          ${state.answered ? `
            <div class="bg-slate-100/40 dark:bg-slate-800/40 p-3 rounded-xl text-xs mt-3">
              <div class="font-bold text-slate-700 dark:text-slate-300 mb-1">Justification :</div>
              <div class="italic text-slate-500 dark:text-slate-400">${justification}</div>
            </div>
          ` : ''}
        </div>
      `;
      const key = `REVISIONPLACEHOLDER${placeholders.length}`;
      placeholders.push(elementHtml);
      return '\n\n' + key + '\n\n';
    }
  });

  // Ordre: {{ordre::Titre::Étape 1 > Étape 2 > Étape 3}}
  temp = temp.replace(/\{\{ordre::(.*?)::(.*?)\}\}/g, (rawTag, title, stepsStr) => {
    const card = noteFlashcards.value.find(c => c.original_text === rawTag);
    const cardId = card ? card.id : null;
    const steps = stepsStr.split('>').map((s: string) => s.trim());
    
    const cleanStep = (str: string) => {
      const cleaned = str.replace(/^(?:étape\s*\d+[\s\-:]*|\d+[\.\s\-:]+)\s*/i, '').trim();
      return cleaned.length > 0 ? cleaned : str;
    };
    
    if (!isReview) {
      const stepItems = steps.map((s: string) => `<li class="mb-1">${cleanStep(s)}</li>`).join('');
      const displayHtml = `
        <div class="bg-slate-50/50 dark:bg-slate-900/50 p-2.5 border border-slate-200 dark:border-slate-800 rounded-xl my-2 max-w-2xl shadow-sm not-prose">
          <strong class="text-[9px] uppercase tracking-wider text-slate-455 font-bold block mb-0.5">Séquence : ${title}</strong>
          <ol class="list-decimal mt-1.5 space-y-0.5 text-xs" style="margin-left: 1rem !important; padding-left: 1rem !important;">${stepItems}</ol>
        </div>
      `;
      const key = `REVISIONPLACEHOLDER${placeholders.length}`;
      placeholders.push(displayHtml);
      return '\n\n' + key + '\n\n';
    } else {
      placeholderStates.value[rawTag] = placeholderStates.value[rawTag] || { 
        answered: false, 
        order: shuffleArray([...steps]) 
      };
      const state = placeholderStates.value[rawTag];
      
      const stepButtons = state.order.map((step: string, idx: number) => {
        return `
          <div class="flex items-center justify-between p-2.5 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl text-xs font-semibold mb-1.5 shadow-sm">
            <span>${cleanStep(step)}</span>
            ${!state.answered ? `
              <div class="flex gap-1 no-print">
                <button type="button" class="px-1.5 py-0.5 hover:bg-slate-100 dark:hover:bg-slate-850 rounded text-slate-400 hover:text-indigo-650" data-action="order-move" data-tag="${encodeURIComponent(rawTag)}" data-index="${idx}" data-dir="up">▲</button>
                <button type="button" class="px-1.5 py-0.5 hover:bg-slate-100 dark:hover:bg-slate-850 rounded text-slate-400 hover:text-indigo-650" data-action="order-move" data-tag="${encodeURIComponent(rawTag)}" data-index="${idx}" data-dir="down">▼</button>
              </div>
            ` : ''}
          </div>
        `;
      }).join('');
      
      const elementHtml = `
        <div class="bg-slate-50/50 dark:bg-slate-900/50 p-4 border border-slate-200 dark:border-slate-800 rounded-2xl my-4 max-w-2xl shadow-sm not-prose">
          <div class="flex items-center justify-between mb-1.5">
            <strong class="text-[10px] uppercase tracking-wider text-slate-455 font-bold">Séquence : ${title}</strong>
            ${state.answered ? renderSm2Buttons(cardId, rawTag) : ''}
          </div>
          <div class="mt-3">${stepButtons}</div>
          
          ${!state.answered ? `
            <button type="button" class="w-full mt-3 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-xs active:scale-95 transition-all border border-transparent" data-action="order-validate" data-tag="${encodeURIComponent(rawTag)}">
              Valider l'ordre
            </button>
          ` : `
            <div class="mt-3 bg-slate-100/40 dark:bg-slate-800/40 p-3 rounded-xl text-xs flex flex-col gap-1.5">
              <div class="font-bold text-slate-700 dark:text-slate-350">Ordre attendu :</div>
              <div class="flex flex-wrap items-center gap-1">
                ${steps.map((s: string) => `<span class="bg-white dark:bg-slate-800 px-2 py-1 rounded-lg border border-slate-200/50 text-[10px] font-semibold">${cleanStep(s)}</span>`).join(' ➜ ')}
              </div>
            </div>
          `}
        </div>
      `;
      const key = `REVISIONPLACEHOLDER${placeholders.length}`;
      placeholders.push(elementHtml);
      return '\n\n' + key + '\n\n';
    }
  });

  // Assoc: {{assoc::Titre::A=1 | B=2 | C=3}}
  temp = temp.replace(/\{\{assoc::(.*?)::(.*?)\}\}/g, (rawTag, title, pairsStr) => {
    const card = noteFlashcards.value.find(c => c.original_text === rawTag);
    const cardId = card ? card.id : null;
    const pairs = pairsStr.split('|').map((p: string) => {
      // Utiliser indexOf pour splitter uniquement au premier '=' (évite les bugs avec les expressions contenant des =)
      const eqIdx = p.indexOf('=')
      if (eqIdx === -1) return { key: p.trim(), value: '' }
      return { key: p.substring(0, eqIdx).trim(), value: p.substring(eqIdx + 1).trim() }
    });
    
    if (!isReview) {
      const rows = pairs.map((p: { key: string, value: string }) => `<tr><td class="border border-slate-200 dark:border-slate-800 p-2 font-semibold text-slate-700 dark:text-slate-300">${p.key}</td><td class="border border-slate-200 dark:border-slate-800 p-2 text-slate-600 dark:text-slate-400">${p.value}</td></tr>`).join('');
      const displayHtml = `
        <div class="bg-slate-50/50 dark:bg-slate-900/50 p-4 border border-slate-200 dark:border-slate-800 rounded-2xl my-4 max-w-2xl shadow-sm not-prose">
          <strong class="text-[10px] uppercase tracking-wider text-slate-400 font-bold block mb-1">Associations : ${title}</strong>
          <table class="table-auto text-xs mt-3 w-full border-collapse border border-slate-200 dark:border-slate-800">
            <thead>
              <tr class="bg-slate-150 dark:bg-slate-800 font-bold">
                <th class="border border-slate-200 dark:border-slate-800 p-2 text-left">Clé</th>
                <th class="border border-slate-200 dark:border-slate-800 p-2 text-left">Liaison</th>
              </tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      `;
      const key = `REVISIONPLACEHOLDER${placeholders.length}`;
      placeholders.push(displayHtml);
      return '\n\n' + key + '\n\n';
    } else {
      const keysList = pairs.map((p: any) => p.key);
      const valuesList = pairs.map((p: any) => p.value);
      
      placeholderStates.value[rawTag] = placeholderStates.value[rawTag] || {
        answered: false,
        shuffledKeys: shuffleArray([...keysList]),
        shuffledValues: shuffleArray([...valuesList]),
        selectedKey: null,
        matches: {}
      };
      
      const state = placeholderStates.value[rawTag];
      
      const keysHtml = state.shuffledKeys.map((k: string) => {
        const isMatched = state.matches[k] !== undefined;
        let btnClass = "p-2 border text-left rounded-xl text-xs font-semibold shadow-sm transition-all";
        if (state.selectedKey === k) {
          btnClass += " border-indigo-500 bg-indigo-50 dark:bg-indigo-950/20 text-indigo-600 dark:text-indigo-400 ring-2 ring-indigo-500/10";
        } else if (isMatched) {
          btnClass += " border-slate-200 dark:border-slate-800 bg-slate-100 dark:bg-slate-850 text-slate-400 cursor-not-allowed opacity-60";
        } else {
          btnClass += " border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-850 cursor-pointer";
        }
        
        return `<button type="button" class="${btnClass}" data-action="assoc-key-select" data-tag="${encodeURIComponent(rawTag)}" data-key="${encodeURIComponent(k)}" ${isMatched || state.answered ? 'disabled' : ''}>${k}</button>`;
      }).join('');
      
      const valuesHtml = state.shuffledValues.map((v: string) => {
        const isMatched = Object.values(state.matches).includes(v);
        let btnClass = "p-2 border text-left rounded-xl text-xs font-semibold shadow-sm transition-all";
        if (isMatched) {
          btnClass += " border-slate-200 dark:border-slate-800 bg-slate-100 dark:bg-slate-850 text-slate-400 cursor-not-allowed opacity-60";
        } else {
          btnClass += " border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-850 cursor-pointer";
        }
        
        return `<button type="button" class="${btnClass}" data-action="assoc-value-select" data-tag="${encodeURIComponent(rawTag)}" data-value="${encodeURIComponent(v)}" ${isMatched || state.answered || !state.selectedKey ? 'disabled' : ''}>${v}</button>`;
      }).join('');
      
      const matchesHtml = Object.entries(state.matches).map(([k, v]) => {
        return `<div class="flex items-center justify-between p-2 bg-indigo-50/50 dark:bg-slate-850 border border-indigo-100 dark:border-slate-800 rounded-xl text-[11px] font-semibold">${k} ➜ ${v} ${!state.answered ? `<button type="button" class="text-rose-500 hover:text-rose-700 ml-2" data-action="assoc-remove" data-tag="${encodeURIComponent(rawTag)}" data-key="${encodeURIComponent(k)}">✕</button>` : ''}</div>`;
      }).join('');
      
      const elementHtml = `
        <div class="bg-slate-50/50 dark:bg-slate-900/50 p-4 border border-slate-200 dark:border-slate-800 rounded-2xl my-4 max-w-2xl shadow-sm not-prose">
          <div class="flex items-center justify-between mb-1.5">
            <strong class="text-[10px] uppercase tracking-wider text-slate-455 font-bold">Associations : ${title}</strong>
            ${state.answered ? renderSm2Buttons(cardId, rawTag) : ''}
          </div>
          <div class="grid grid-cols-2 gap-4 mt-3">
            <div class="flex flex-col gap-1.5"><div class="text-[9px] font-bold text-slate-400 uppercase tracking-wider mb-1">Clés</div>${keysHtml}</div>
            <div class="flex flex-col gap-1.5"><div class="text-[9px] font-bold text-slate-400 uppercase tracking-wider mb-1">Valeurs</div>${valuesHtml}</div>
          </div>
          
          ${Object.keys(state.matches).length > 0 ? `<div class="mt-4 border-t border-slate-200 dark:border-slate-800 pt-3"><div class="text-[9px] font-bold text-slate-400 uppercase tracking-wider mb-2">Liaisons créées :</div><div class="flex flex-col gap-1.5">${matchesHtml}</div></div>` : ''}
          
          ${!state.answered ? `
            <button type="button" class="w-full mt-4 px-4 py-2 bg-indigo-650 hover:bg-indigo-700 text-white font-bold rounded-xl text-xs active:scale-95 transition-all border border-transparent disabled:opacity-40" data-action="assoc-validate" data-tag="${encodeURIComponent(rawTag)}" ${Object.keys(state.matches).length !== keysList.length ? 'disabled' : ''}>
              Valider les liaisons
            </button>
          ` : `
            <div class="mt-4 bg-slate-100/40 dark:bg-slate-800/40 p-3 rounded-xl text-xs flex flex-col gap-1.5">
              <div class="font-bold text-slate-700 dark:text-slate-350">Associations attendues :</div>
              <div class="grid grid-cols-1 gap-1.5">
                ${pairs.map((p: any) => `<div class="text-[11px] font-semibold text-slate-500"><span class="text-indigo-600 dark:text-indigo-400 font-bold">${p.key}</span> ➜ ${p.value}</div>`).join('')}
              </div>
            </div>
          `}
        </div>
      `;
      const key = `REVISIONPLACEHOLDER${placeholders.length}`;
      placeholders.push(elementHtml);
      return '\n\n' + key + '\n\n';
    }
  });

  // 6. Mark down parse
  let html = marked.parse(temp) as string

  placeholders.forEach((placeholderHtml, idx) => {
    html = html.replace(new RegExp(`LATEXBLOCKPLACEHOLDER${idx}(?!\\d)`, 'g'), () => placeholderHtml)
    html = html.replace(new RegExp(`LATEXINLINEPLACEHOLDER${idx}(?!\\d)`, 'g'), () => placeholderHtml)
    html = html.replace(new RegExp(`DEFPLACEHOLDER${idx}(?!\\d)`, 'g'), () => placeholderHtml)
    html = html.replace(new RegExp(`DIAGRAMPLACEHOLDER${idx}(?!\\d)`, 'g'), () => placeholderHtml)
    html = html.replace(new RegExp(`REVISIONPLACEHOLDER${idx}(?!\\d)`, 'g'), () => placeholderHtml)
  })

  // Post-processing: marked wraps placeholder text in <p> tags.
  // After replacement, this creates <p><div ...>...</div></p> which
  // the browser auto-splits into <p></p> <div>...</div> <p></p>,
  // and each empty <p> gets .markdown-body p { mb-4 } margins.
  // Fix: strip <p> wrappers around block elements and remove empty <p> tags.
  html = html.replace(/<p>\s*(<div\b)/gi, '$1')
  html = html.replace(/(<\/div>)\s*<\/p>/gi, '$1')
  html = html.replace(/<p>\s*<\/p>/gi, '')

  return html
}

function renderDiagramHtml(diagram: any): string {
  if (!diagram) return '<div class="text-xs text-slate-450 italic my-2">Diagramme introuvable.</div>'
  
  try {
    const data = JSON.parse(diagram.code)
    if (data && data.type === 'visual') {
      const nodesList = data.nodes || []
      const connectionsList = data.connections || []
      const bgImg = data.backgroundImage || ''
      const masksList = data.masks || []
      
      const maxX = Math.max(...nodesList.map((n: any) => n.x), ...masksList.map((m: any) => m.x + m.width), 350) + 80
      const maxY = Math.max(...nodesList.map((n: any) => n.y), ...masksList.map((m: any) => m.y + m.height), 200) + 80
      
      let linesSvg = ''
      connectionsList.forEach((conn: any) => {
        const fromNode = nodesList.find((n: any) => n.id === conn.from)
        const toNode = nodesList.find((n: any) => n.id === conn.to)
        if (fromNode && toNode) {
          linesSvg += `<line x1="${fromNode.x}" y1="${fromNode.y}" x2="${toNode.x}" y2="${toNode.y}" stroke="#6366f1" stroke-width="2" marker-end="url(#arrow-preview)" />`
        }
      })
      
      let nodesHtml = ''
      nodesList.forEach((node: any) => {
        let shapeStyle = ''
        if (node.type === 'rect') {
          shapeStyle = `width: 90px; height: 32px; border-radius: 8px;`
        } else if (node.type === 'circle') {
          shapeStyle = `width: 48px; height: 48px; border-radius: 50%;`
        } else if (node.type === 'diamond') {
          shapeStyle = `width: 45px; height: 45px; transform: rotate(45deg);`
        }
        
        let colorHex = '#6366f1'
        if (node.color.includes('emerald')) colorHex = '#10b981'
        else if (node.color.includes('amber')) colorHex = '#f59e0b'
        else if (node.color.includes('pink')) colorHex = '#ec4899'
        
        if (node.type === 'diamond') {
          nodesHtml += `
            <div class="absolute -translate-x-1/2 -translate-y-1/2 flex items-center justify-center text-center" style="top: ${node.y}px; left: ${node.x}px; width: 45px; height: 45px;">
              <div style="${shapeStyle} background-color: ${colorHex}; border: 1px solid rgba(0,0,0,0.05); box-shadow: 0 1px 3px rgba(0,0,0,0.05);"></div>
              <span class="absolute z-10 text-[8px] font-extrabold text-white px-1 leading-tight select-none">${node.label}</span>
            </div>
          `
        } else {
          nodesHtml += `
            <div class="absolute -translate-x-1/2 -translate-y-1/2 flex items-center justify-center text-center px-1 text-[8px] font-bold text-white shadow-sm border border-black/5" style="top: ${node.y}px; left: ${node.x}px; ${shapeStyle} background-color: ${colorHex};">
              <span class="select-none leading-tight">${node.label}</span>
            </div>
          `
        }
      })
      
      // Background image inside SVG
      let bgImgHtml = ''
      if (bgImg) {
        bgImgHtml = `<image href="${bgImg}" x="0" y="0" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" />`
      }
      
      // Occlusion masks inside SVG
      let masksSvg = ''
      let activeReviewHtml = ''
      const isReview = notesStore.isReviewModeActive
      
      masksList.forEach((mask: any) => {
        const rawTag = `[diagram:${diagram.id}] mask:${mask.id}`
        placeholderStates.value[rawTag] = placeholderStates.value[rawTag] || { revealed: false }
        const state = placeholderStates.value[rawTag]
        
        if (isReview) {
          const isRevealed = state.revealed
          const fillClass = isRevealed ? 'fill-transparent stroke-rose-500/20' : 'fill-slate-800 dark:fill-slate-700 opacity-100 cursor-pointer'
          const pointerEvents = isRevealed ? 'pointer-events-none' : 'pointer-events-auto'
          
          masksSvg += `
            <rect 
              x="${mask.x}" 
              y="${mask.y}" 
              width="${mask.width}" 
              height="${mask.height}" 
              class="${fillClass} stroke-rose-600 stroke-2"
              style="${pointerEvents}"
              data-action="reveal" 
              data-tag="${encodeURIComponent(rawTag)}"
            />
          `
          
          if (isRevealed) {
            const card = noteFlashcards.value.find(c => c.original_text === rawTag)
            const cardId = card ? card.id : null
            activeReviewHtml += `
              <div class="mt-2 p-2.5 border border-slate-100 dark:border-slate-800 rounded-xl bg-slate-50/50 dark:bg-slate-900 flex flex-col items-center gap-2">
                <span class="text-[10px] font-bold text-slate-500">Zone : <span class="text-rose-500 font-extrabold">${mask.label}</span></span>
                ${renderSm2Buttons(cardId, rawTag)}
              </div>
            `
          }
        } else {
          // Standard view mode: render masks as semi-transparent
          masksSvg += `
            <rect 
              x="${mask.x}" 
              y="${mask.y}" 
              width="${mask.width}" 
              height="${mask.height}" 
              class="fill-rose-500/20 stroke-rose-600 stroke-2"
              title="Zone cachée : ${mask.label}"
            />
            <text x="${mask.x + 4}" y="${mask.y + 12}" fill="#e11d48" font-size="8px" font-weight="bold" class="select-none pointer-events-none">${mask.label}</text>
          `
        }
      })
      
      return `
        <div class="relative w-full border border-slate-150 dark:border-slate-800 rounded-2xl bg-slate-50/20 dark:bg-slate-950/15 p-2 overflow-hidden my-4 no-print select-none" style="height: ${Math.min(500, maxY + 120)}px;">
          <div class="absolute inset-x-0 top-0 px-4 py-1 flex items-center justify-between text-[8px] text-slate-400 font-bold uppercase tracking-wider bg-slate-50/80 dark:bg-slate-900 border-b border-slate-100 dark:border-slate-800/60 z-10">
            <span>Schéma visuel : ${diagram.title}</span>
            ${isReview ? '<span class="text-rose-500 animate-pulse font-extrabold">Mode Révision - Cliquez sur les zones grises</span>' : ''}
          </div>
          <div class="w-full h-full overflow-auto pt-6 pb-24">
            <div class="relative" style="width: ${maxX}px; height: ${maxY}px;">
              <svg class="absolute inset-0 w-full h-full">
                <defs>
                  <marker id="arrow-preview" viewBox="0 0 10 10" refX="20" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
                    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#6366f1" />
                  </marker>
                </defs>
                ${bgImgHtml}
                ${linesSvg}
                ${masksSvg}
              </svg>
              ${nodesHtml}
            </div>
          </div>
          <div class="absolute inset-x-0 bottom-0 p-2 bg-white/95 dark:bg-slate-900/95 border-t border-slate-100 dark:border-slate-800/80 z-20 flex flex-col gap-1.5 max-h-36 overflow-y-auto">
            ${activeReviewHtml || `<div class="text-[9px] text-slate-400 italic text-center py-1">${isReview ? 'Aucun masque d\'occlusion révélé.' : 'Légende : masques d\'occlusion affichés.'}</div>`}
          </div>
        </div>
      `
    } else {
      return `
        <div class="border border-slate-100 dark:border-slate-800 rounded-2xl bg-slate-50/30 dark:bg-slate-950/15 p-4 my-4">
          <div class="text-[9px] text-slate-400 font-bold uppercase tracking-wider mb-2">Schéma Mermaid : ${diagram.title}</div>
          <pre class="text-[10px] text-slate-500 font-mono bg-slate-100 dark:bg-slate-800 p-3 rounded-lg overflow-x-auto select-all">${diagram.code}</pre>
        </div>
      `
    }
  } catch {
    return `
      <div class="border border-slate-100 dark:border-slate-800 rounded-2xl bg-slate-50/30 dark:bg-slate-950/15 p-4 my-4">
        <div class="text-[9px] text-slate-400 font-bold uppercase tracking-wider mb-2">Schéma Mermaid : ${diagram.title}</div>
        <pre class="text-[10px] text-slate-500 font-mono bg-slate-100 dark:bg-slate-800 p-3 rounded-lg overflow-x-auto select-all">${diagram.code}</pre>
      </div>
    `
  }
}

function handleTextareaSelect(event: Event) {
  const textarea = textareaRef.value
  if (!textarea) return
  
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  
  if (start !== end) {
    const selected = textarea.value.substring(start, end).trim()
    if (selected.length > 0) {
      selectionText.value = selected
      selectionStart.value = start
      selectionEnd.value = end
      savedSelectionContent.value = textarea.value  // snapshot du contenu au moment de la sélection
      
      if (event instanceof MouseEvent) {
        const viewportWidth = window.innerWidth
        // Clamp the left position to keep the bar within bounds (safeguard for screen width)
        const leftBound = Math.max(160, Math.min(event.clientX, viewportWidth - 160))
        selectionMenuPos.value = {
          top: event.clientY - 12,
          left: leftBound
        }
      } else {
        const rect = textarea.getBoundingClientRect()
        const viewportWidth = window.innerWidth
        const centerLeft = rect.left + rect.width / 2
        const leftBound = Math.max(160, Math.min(centerLeft, viewportWidth - 160))
        selectionMenuPos.value = {
          top: rect.top + 60,
          left: leftBound
        }
      }
      
      showSelectionMenu.value = true
      return
    }
  }
  showSelectionMenu.value = false
}

async function applySelectionTransform(type: 'trou' | 'gras' | 'italique' | 'code' | 'bloc_code' | 'def' | 'qcm' | 'ordre' | 'assoc' | 'vf' | 'math_bloc' | 'math_ligne' | 'diagramme') {
  const textarea = textareaRef.value
  if (!textarea) return
  
  // Utiliser le snapshot du contenu au moment de la sélection (évite le décalage stale après await)
  const text = savedSelectionContent.value || textarea.value
  const start = selectionStart.value
  const end = selectionEnd.value
  const selected = text.substring(start, end)
  
  let replaced = ''
  if (type === 'trou') {
    replaced = `{{trou::${selected}}}`
  } else if (type === 'gras') {
    replaced = `**${selected}**`
  } else if (type === 'italique') {
    replaced = `*${selected}*`
  } else if (type === 'code') {
    replaced = `\`${selected}\``
  } else if (type === 'bloc_code') {
    replaced = `\`\`\`\n${selected}\n\`\`\``
  } else if (type === 'def') {
    const result = await openModal({
      title: 'Définition info-bulle',
      description: `Associer une définition au terme sélectionné : « ${selected} »`,
      icon: BookOpen,
      iconBg: 'bg-emerald-500',
      confirmBg: 'bg-emerald-600 hover:bg-emerald-700 shadow-emerald-600/20',
      confirmLabel: 'Ajouter la définition',
      fields: [
        { label: 'Définition', type: 'text', value: '', placeholder: 'Entrez la définition...' }
      ]
    })
    if (!result) return
    replaced = `[${selected}]{def:${result[0].value.trim() || 'Définition...'}}`
  } else if (type === 'qcm') {
    const result = await openModal({
      title: 'Créer un QCM',
      description: `La bonne réponse sera : « ${selected} »`,
      icon: HelpCircle,
      iconBg: 'bg-purple-500',
      confirmBg: 'bg-purple-600 hover:bg-purple-700 shadow-purple-600/20',
      confirmLabel: 'Créer le QCM',
      fields: [
        { label: 'Question', type: 'text', value: 'Question ?', placeholder: 'Entrez la question...' },
        { label: 'Option fausse 1', type: 'text', value: '', placeholder: 'Mauvaise réponse 1...' },
        { label: 'Option fausse 2', type: 'text', value: '', placeholder: 'Mauvaise réponse 2...' }
      ]
    })
    if (!result) return
    replaced = `{{qcm::${result[0].value}::${result[1].value}|*${selected}*|${result[2].value}}}`
  } else if (type === 'ordre') {
    const result = await openModal({
      title: 'Séquence ordonnée',
      description: `« ${selected} » sera la première étape.`,
      icon: ListOrdered,
      iconBg: 'bg-amber-500',
      confirmBg: 'bg-amber-600 hover:bg-amber-700 shadow-amber-600/20',
      confirmLabel: 'Créer la séquence',
      fields: [
        { label: 'Titre de la séquence', type: 'text', value: 'Ordre', placeholder: 'Ex : Étapes de la photosynthèse' },
        { label: 'Étape suivante', type: 'text', value: '', placeholder: 'Entrez l’étape qui suit...' }
      ]
    })
    if (!result) return
    replaced = `{{ordre::${result[0].value}::${selected} > ${result[1].value}}}`
  } else if (type === 'assoc') {
    const result = await openModal({
      title: 'Créer une association',
      description: `« ${selected} » sera associé à une valeur.`,
      icon: LinkIcon,
      iconBg: 'bg-pink-500',
      confirmBg: 'bg-pink-600 hover:bg-pink-700 shadow-pink-600/20',
      confirmLabel: 'Créer l’association',
      fields: [
        { label: 'Titre du groupe', type: 'text', value: 'Relations', placeholder: 'Ex : Capitales' },
        { label: `Valeur associée à « ${selected} »`, type: 'text', value: '', placeholder: 'Ex : Paris' }
      ]
    })
    if (!result) return
    replaced = `{{assoc::${result[0].value}::${selected} = ${result[1].value}}}`
  } else if (type === 'vf') {
    const result = await openModal({
      title: 'Vrai / Faux',
      description: `L’assertion : « ${selected} »`,
      icon: CheckCircle2,
      iconBg: 'bg-rose-500',
      confirmBg: 'bg-rose-600 hover:bg-rose-700 shadow-rose-600/20',
      confirmLabel: 'Créer la question',
      fields: [
        { label: 'Cette assertion est...', type: 'bool', value: true },
        { label: 'Justification', type: 'text', value: '', placeholder: 'Expliquez pourquoi...' }
      ]
    })
    if (!result) return
    const ans = result[0].value ? 'Vrai' : 'Faux'
    replaced = `{{vf::${selected}::${ans}::${result[1].value || 'Justification...'}}}`
  } else if (type === 'math_bloc') {
    replaced = `$$\n${selected}\n$$`
  } else if (type === 'math_ligne') {
    replaced = `$${selected}$`
  } else if (type === 'diagramme') {
    if (allUserDiagrams.value.length === 0) {
      await openModal({
        title: 'Aucun diagramme',
        description: 'Vous n’avez créé aucun diagramme. Allez dans le module Diagrammes pour en créer un.',
        icon: Image,
        iconBg: 'bg-sky-500',
        confirmLabel: 'Compris',
        fields: []
      })
      return
    }
    const result = await openModal({
      title: 'Insérer un diagramme',
      description: 'Sélectionnez le diagramme à insérer dans la note.',
      icon: Image,
      iconBg: 'bg-sky-500',
      confirmBg: 'bg-sky-600 hover:bg-sky-700 shadow-sky-600/20',
      confirmLabel: 'Insérer',
      fields: [
        {
          label: 'Diagramme',
          type: 'select',
          value: allUserDiagrams.value[0]?.id,
          options: allUserDiagrams.value.map(d => ({ value: d.id, label: d.title }))
        }
      ]
    })
    if (!result) return
    replaced = `[diagram:${result[0].value}]`
  }
  
  noteBody.value = text.substring(0, start) + replaced + text.substring(end)
  
  triggerAutoSave()
  showSelectionMenu.value = false
  
  setTimeout(() => {
    textarea.focus()
    const newPos = start + replaced.length
    textarea.setSelectionRange(newPos, newPos)
  }, 50)
}

function handleMarkdownClick(event: MouseEvent) {
  // Intercepter les clics sur les placeholders
  handlePlaceholderInteraction(event)
}

async function handlePlaceholderInteraction(event: MouseEvent) {
  const target = event.target as HTMLElement
  const action = target.getAttribute('data-action')
  
  if (!action) return
  
  const rawTag = decodeURIComponent(target.getAttribute('data-tag') || '')
  if (!rawTag) return
  
  const state = placeholderStates.value[rawTag]
  
  if (action === 'reveal') {
    state.revealed = true
  }
  
  else if (action === 'qcm-select') {
    const optionSelected = decodeURIComponent(target.getAttribute('data-option') || '')
    state.selectedOption = optionSelected
    state.answered = true
  }
  
  else if (action === 'vf-select') {
    const val = target.getAttribute('data-value') || ''
    state.selectedAnswer = val
    state.answered = true
  }
  
  else if (action === 'order-move') {
    const idx = Number(target.getAttribute('data-index'))
    const dir = target.getAttribute('data-dir')
    const list = [...state.order]
    
    if (dir === 'up' && idx > 0) {
      const tempVal = list[idx]
      list[idx] = list[idx - 1]
      list[idx - 1] = tempVal
    } else if (dir === 'down' && idx < list.length - 1) {
      const tempVal = list[idx]
      list[idx] = list[idx + 1]
      list[idx + 1] = tempVal
    }
    state.order = list
  }
  
  else if (action === 'order-validate') {
    state.answered = true
  }
  
  else if (action === 'assoc-key-select') {
    const key = decodeURIComponent(target.getAttribute('data-key') || '')
    state.selectedKey = key
  }
  
  else if (action === 'assoc-value-select') {
    const val = decodeURIComponent(target.getAttribute('data-value') || '')
    if (state.selectedKey) {
      state.matches[state.selectedKey] = val
      state.selectedKey = null
    }
  }
  
  else if (action === 'assoc-remove') {
    const key = decodeURIComponent(target.getAttribute('data-key') || '')
    delete state.matches[key]
  }
  
  else if (action === 'assoc-validate') {
    state.answered = true
  }
  
  else if (action === 'sm2-vote') {
    const cardId = Number(target.getAttribute('data-card-id'))
    const score = Number(target.getAttribute('data-score'))
    
    try {
      target.setAttribute('disabled', 'true')
      target.innerText = '...'
      
      await api.patch(`/flashcards/${cardId}/review`, { score })
      state.score = score
    } catch (err) {
      console.error('Erreur lors du vote SM-2', err)
      alert("Erreur lors de l'enregistrement de l'évaluation.")
      target.removeAttribute('disabled')
      target.innerText = score === 1 ? 'À revoir' : score === 2 ? 'Difficile' : score === 3 ? 'Correct' : 'Facile'
    }
  }
  
  else if (action === 'sm2-re-evaluate') {
    const cardId = Number(target.getAttribute('data-card-id'))
    openEvaluationModal(cardId, rawTag)
  }
  
  // Trigger evaluation modal if applicable
  const isActionRequiringEvaluation = 
    (action === 'reveal') || // Trou or diagram mask revealed
    (action === 'qcm-select') ||
    (action === 'vf-select') ||
    (action === 'order-validate') ||
    (action === 'assoc-validate')

  const card = noteFlashcards.value.find(c => c.original_text === rawTag)
  const cardId = card ? card.id : null
    
  if (isActionRequiringEvaluation && cardId && (!state || state.score === undefined)) {
    setTimeout(() => {
      openEvaluationModal(cardId, rawTag)
    }, 700)
  }
  
  // Force reactive update
  placeholderStates.value = { ...placeholderStates.value }
}

async function goBack() {
  await saveNote()
  router.push('/notes')
}

async function toggleMode() {
  if (isEditMode.value) {
    await saveNote()
  }
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

function handleTabKey() {
  const textarea = textareaRef.value
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const text = textarea.value

  const tabValue = '  ' // 2 spaces is standard for markdown indentation
  noteBody.value = text.substring(0, start) + tabValue + text.substring(end)

  setTimeout(() => {
    textarea.focus()
    const newCursorPos = start + tabValue.length
    textarea.setSelectionRange(newCursorPos, newCursorPos)
    triggerAutoSave()
  }, 0)
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

async function insertDefinitionTooltip() {
  const textarea = textareaRef.value
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const text = textarea.value
  const selected = text.substring(start, end)
  
  if (!selected.trim()) {
    await openModal({
      title: 'Sélection requise',
      description: 'Veuillez sélectionner un mot ou un terme dans le texte pour lui associer une définition.',
      icon: BookOpen,
      iconBg: 'bg-emerald-500',
      confirmLabel: 'Compris',
      fields: []
    })
    return
  }

  const result = await openModal({
    title: 'Définition info-bulle',
    description: `Terme sélectionné : « ${selected} »`,
    icon: BookOpen,
    iconBg: 'bg-emerald-500',
    confirmBg: 'bg-emerald-600 hover:bg-emerald-700 shadow-emerald-600/20',
    confirmLabel: 'Ajouter la définition',
    fields: [
      { label: 'Définition', type: 'text', value: '', placeholder: `Définissez « ${selected} »...` }
    ]
  })
  if (!result || !result[0].value.trim()) return

  const replacement = `[${selected}]{def:${result[0].value.trim()}}`
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
    const updated = await notesStore.updateNote(noteId.value, title.value, rawContent)
    if (updated) {
      noteFlashcards.value = (updated as any).flashcards || []
    }
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

async function saveNoteTags(tags: Tag[]) {
  if (!noteId.value) return
  noteTags.value = await tagsStore.setTagsForEntity('notes', noteId.value, tags.map(tag => tag.id))
  const note = notesStore.notes.find(item => item.id === noteId.value)
  if (note) note.tags = noteTags.value
}

function printNote() {
  window.print()
}
</script>

<style>
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
  }\n  .markdown-body h1, .markdown-body h2, .markdown-body h3 {
    color: black !important;
  }
  .katex-display {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
  }
}

.popup-enter-active,
.popup-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.popup-enter-from,
.popup-leave-to {
  opacity: 0;
  transform: translateY(-6px) scale(0.97);
}

/* Spacing & Margin resets for Modals */
.sm2-modal-container {
  padding: 1.5rem !important;
}
.sm2-modal-container .sm2-modal-title {
  margin: 0 !important;
  padding: 0 !important;
  margin-bottom: 4px !important;
  line-height: 1.1 !important;
  font-size: 1.125rem !important;
}
.sm2-modal-container .sm2-modal-desc {
  margin: 0 !important;
  padding: 0 !important;
  margin-top: 4px !important;
  line-height: 1.25 !important;
  font-size: 0.75rem !important;
}
.sm2-modal-container .sm2-modal-btn {
  margin: 0 !important;
  padding: 0.625rem 0.5rem !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  line-height: 1 !important;
}
.sm2-modal-container .sm2-modal-btn .sm2-btn-emoji {
  margin: 0 0 2px 0 !important;
  padding: 0 !important;
  line-height: 1 !important;
  font-size: 1.5rem !important;
}
.sm2-modal-container .sm2-modal-btn .sm2-btn-label {
  margin: 0 !important;
  padding: 0 !important;
  line-height: 1 !important;
  font-size: 0.75rem !important;
}
.sm2-modal-container .sm2-modal-btn .sm2-btn-desc {
  margin: 2px 0 0 0 !important;
  padding: 0 !important;
  line-height: 1 !important;
  font-size: 9px !important;
}
.sm2-modal-container .sm2-modal-cancel {
  margin-top: 0.75rem !important;
}

/* Input modal spacing reset */
.custom-input-modal {
  padding: 0 !important;
}
.custom-input-modal .input-modal-header {
  padding: 1.5rem 1.5rem 1rem 1.5rem !important;
}
.custom-input-modal .input-modal-title {
  margin: 0 !important;
  padding: 0 !important;
  line-height: 1.1 !important;
  font-size: 1.125rem !important;
}
.custom-input-modal .input-modal-desc {
  margin: 4px 0 0 0 !important;
  padding: 0 !important;
  line-height: 1.25 !important;
  font-size: 0.75rem !important;
}
</style>
