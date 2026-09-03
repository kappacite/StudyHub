<template>
  <div class="w-full flex flex-col" :class="[isEditMode ? 'h-full overflow-hidden' : 'min-h-full']">
    <!-- Loading State -->
    <div
      v-if="loading"
      class="flex-1 flex flex-col items-center justify-center py-20 gap-3 no-print bg-surface-soft dark:bg-[#070913] h-full w-full"
    >
      <svg
        class="animate-spin h-8 w-8 text-primary"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        ></circle>
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
      <span class="text-sm font-semibold text-ink-subtle uppercase tracking-widest text-ink-subtle"
        >Ouverture de la note...</span
      >
    </div>

    <!-- Error State — échec du chargement initial -->
    <div
      v-else-if="loadError"
      class="flex-1 flex items-center justify-center py-20 px-4 no-print h-full w-full"
    >
      <div class="w-full max-w-md">
        <BaseCard padding="none">
          <BaseEmptyState
            title="Le chargement a échoué"
            description="Cette note n'a pas pu être récupérée. Vérifiez votre connexion et réessayez."
          >
            <template #icon><AlertCircle class="w-8 h-8 text-danger" /></template>
            <template #actions>
              <BaseButton @click="loadNoteDetails">Réessayer</BaseButton>
            </template>
          </BaseEmptyState>
        </BaseCard>
      </div>
    </div>

    <!-- Main Content -->
    <div
      v-else
      class="flex-1 flex flex-col w-full animate-fade-in print:h-auto print:overflow-visible"
      :class="[isEditMode ? 'overflow-hidden' : '']"
    >
      <!-- Bannière lecture seule : note partagée par un cours -->
      <div
        v-if="isReadOnly"
        class="flex items-center justify-between gap-2 px-6 py-2 bg-warning-soft dark:bg-warning-soft border-b border-warning dark:border-warning text-warning dark:text-warning text-xs font-semibold no-print"
      >
        <span class="flex items-center gap-2">
          <Eye class="w-4 h-4" />
          Note partagée par un cours — lecture seule.
        </span>
        <span class="flex items-center gap-2">
          <button
            class="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg border border-warning dark:border-warning font-semibold hover:bg-warning-soft dark:hover:bg-warning-soft active:scale-95 transition-all"
            @click="hideFromView"
          >
            <EyeOff class="w-3.5 h-3.5" />
            Cacher
          </button>
          <button
            :disabled="isCopying"
            class="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-warning text-white font-semibold hover:bg-warning active:scale-95 transition-all disabled:opacity-50"
            @click="copyForEditing"
          >
            <Copy class="w-3.5 h-3.5" />
            {{ isCopying ? 'Copie…' : 'Copier pour modifier' }}
          </button>
        </span>
      </div>

      <!-- Split-Screen Outer Container -->
      <div class="flex-1 flex w-full h-full overflow-hidden print:h-auto print:overflow-visible">
        <!-- Left Pane: PDF Visualizer removed -->

        <!-- Right Pane: Note Content -->
        <div
          class="flex-1 flex flex-col overflow-hidden h-full print:h-auto print:overflow-visible bg-surface dark:bg-surface-soft"
        >
          <!-- 1. FULL VIEWPORT EDIT MODE -->
          <div
            v-if="isEditMode"
            class="flex-1 flex flex-col bg-surface dark:bg-surface-soft overflow-hidden"
          >
            <!-- Header Toolbar -->
            <div
              class="flex flex-col border-b border-line dark:border-line bg-surface dark:bg-surface-soft z-10 no-print"
            >
              <!-- Row 1: Global Actions & Title -->
              <div
                class="flex flex-wrap items-center justify-between gap-3 px-6 py-3 border-b border-line-soft dark:border-line"
              >
                <div class="flex min-w-[18rem] flex-1 items-center gap-4">
                  <!-- Sidebar toggle -->
                  <button
                    class="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-line text-ink-muted transition-colors hover:border-primary hover:bg-primary-soft hover:text-primary dark:border-line dark:text-ink-subtle dark:hover:border-primary dark:hover:bg-primary-soft dark:hover:text-primary"
                    type="button"
                    title="Afficher la barre de raccourcis"
                    @click="toggleShortcutSidebar"
                  >
                    <Menu class="h-5 w-5" />
                  </button>

                  <div class="h-5 w-[1px] bg-line dark:bg-surface-soft"></div>

                  <!-- Title Input (Direct inline edit) -->
                  <input
                    v-model="title"
                    type="text"
                    placeholder="Titre de la note..."
                    class="block flex-1 max-w-xl text-lg font-bold bg-transparent border-0 focus:ring-0 focus:outline-none placeholder:text-ink-subtle py-1"
                    @input="triggerAutoSave"
                  />
                </div>

                <!-- Header Right Controls -->
                <div class="flex max-w-full flex-wrap items-center justify-end gap-2">
                  <!-- Save Status -->
                  <span
                    class="text-xs font-semibold text-ink-subtle flex items-center gap-1.5 mr-2"
                  >
                    <span
                      class="w-2 h-2 rounded-full bg-success"
                      :class="[isSaving ? 'animate-pulse' : '']"
                    ></span>
                    {{ saveStatus }}
                  </span>

                  <!-- Binder select -->
                  <select
                    v-model="binderId"
                    class="px-2.5 py-1.5 bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-xs font-semibold transition-all"
                    @change="triggerAutoSave"
                  >
                    <option :value="null">Général (Aucun)</option>
                    <option v-for="b in bindersStore.binders" :key="b.id" :value="b.id">
                      {{ b.name }}
                    </option>
                  </select>

                  <div class="w-48 sm:w-56">
                    <TagSelector v-model="noteTags" compact @change="saveNoteTags" />
                  </div>

                  <!-- Collapsible Settings Toggle (Context & Links) -->
                  <button
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 border rounded-xl text-xs font-semibold transition-all"
                    :class="[
                      showSettings
                        ? 'border-primary bg-primary-soft text-primary dark:border-primary dark:bg-primary-soft dark:text-primary'
                        : 'border-line dark:border-line hover:bg-surface-soft dark:hover:bg-surface-soft',
                    ]"
                    @click="showSettings = !showSettings"
                  >
                    <Compass class="w-3.5 h-3.5" />
                    Contexte / Liens
                  </button>

                  <!-- Live Preview Toggle -->
                  <button
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 border rounded-xl text-xs font-semibold transition-all"
                    :class="[
                      isLivePreviewActive
                        ? 'border-primary bg-primary-soft text-primary dark:border-primary dark:bg-primary-soft dark:text-primary'
                        : 'border-line dark:border-line hover:bg-surface-soft dark:hover:bg-surface-soft text-ink-muted dark:text-ink-subtle',
                    ]"
                    type="button"
                    title="Afficher l'aperçu en temps réel côte à côte"
                    @click="isLivePreviewActive = !isLivePreviewActive"
                  >
                    <Columns class="w-3.5 h-3.5" />
                    Aperçu
                  </button>

                  <!-- View Toggler -->
                  <button
                    class="inline-flex items-center gap-2 px-4 py-1.5 border border-line dark:border-line rounded-xl text-xs font-semibold hover:bg-surface-soft dark:hover:bg-surface-soft transition-all text-ink-muted dark:text-ink-subtle"
                    @click="toggleMode"
                  >
                    <Eye class="w-3.5 h-3.5 text-primary" />
                    Visualiser
                  </button>

                  <!-- Bouton Partage -->
                  <div class="relative">
                    <button
                      type="button"
                      :title="
                        isPublic
                          ? 'Note publique — cliquer pour rendre privée'
                          : 'Rendre cette note publique'
                      "
                      class="inline-flex items-center gap-1.5 px-3 py-1.5 border rounded-xl text-xs font-semibold transition-all"
                      :class="[
                        isPublic
                          ? 'border-success bg-success-soft text-success dark:border-success dark:bg-success-soft dark:text-success'
                          : 'border-line dark:border-line hover:bg-surface-soft dark:hover:bg-surface-soft text-ink-muted dark:text-ink-subtle',
                      ]"
                      @click="handleShareClick"
                    >
                      <Globe class="w-3.5 h-3.5" />
                      {{ isPublic ? 'Public' : 'Privé' }}
                    </button>

                    <!-- Popup lien de partage -->
                    <Transition name="popup">
                      <div
                        v-if="sharePopupVisible && isPublic"
                        class="absolute right-0 top-full mt-2 w-80 bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-2xl shadow-xl p-4 z-50"
                      >
                        <div class="flex items-center justify-between mb-3">
                          <span
                            class="text-xs font-bold text-ink dark:text-ink-subtle flex items-center gap-1.5"
                          >
                            <Globe class="w-3.5 h-3.5 text-success" />
                            Note publique
                          </span>
                          <button
                            class="text-ink-subtle hover:text-ink-muted transition-colors"
                            @click="sharePopupVisible = false"
                          >
                            <X class="w-4 h-4" />
                          </button>
                        </div>
                        <p class="text-xs text-ink-muted dark:text-ink-subtle mb-3">
                          Toute personne avec ce lien peut lire cette note.
                        </p>
                        <div
                          class="flex items-center gap-2 bg-surface-soft dark:bg-surface-soft rounded-xl px-3 py-2"
                        >
                          <span
                            class="text-tiny font-mono text-ink-muted dark:text-ink-subtle flex-1 truncate"
                            >{{ shareUrl }}</span
                          >
                          <button
                            class="shrink-0 px-2.5 py-1 bg-primary hover:bg-primary-strong text-white text-xs font-bold rounded-lg transition-all active:scale-95"
                            @click="copyShareLink"
                          >
                            {{ shareCopied ? 'Copié !' : 'Copier' }}
                          </button>
                        </div>
                        <button
                          class="mt-3 w-full text-xs text-danger hover:text-danger font-semibold transition-colors"
                          @click="togglePublic"
                        >
                          Rendre privée
                        </button>
                      </div>
                    </Transition>
                  </div>

                  <!-- Guide Button (Edit Mode) -->
                  <button
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 border border-line dark:border-line rounded-xl text-xs font-semibold hover:bg-surface-soft dark:hover:bg-surface-soft transition-all text-ink-muted dark:text-ink-subtle"
                    type="button"
                    @click="showHelpModal = true"
                  >
                    <HelpCircle class="w-3.5 h-3.5 text-primary" />
                    Guide
                  </button>
                </div>
              </div>

              <!-- Row 2: Formatting Toolbar -->
              <div
                class="flex flex-wrap items-center gap-1.5 px-6 py-2 bg-surface-soft dark:bg-surface-soft"
              >
                <span class="text-tiny font-bold text-ink-subtle uppercase tracking-wider px-2"
                  >Format</span
                >
                <button
                  v-for="btn in formatButtons"
                  :key="btn.label"
                  type="button"
                  class="p-2 text-xs font-semibold text-ink-muted dark:text-ink-subtle hover:text-primary hover:bg-surface dark:hover:bg-surface-soft rounded-lg transition-all"
                  :title="btn.label"
                  @click="insertText(btn.prefix, btn.suffix)"
                >
                  {{ btn.label }}
                </button>

                <div class="h-4 w-[1px] bg-line dark:bg-surface-soft mx-2"></div>

                <span class="text-tiny font-bold text-ink-subtle uppercase tracking-wider px-2"
                  >LaTeX</span
                >
                <button
                  v-for="btn in latexButtons"
                  :key="btn.label"
                  type="button"
                  class="p-2 text-xs font-mono font-bold text-ink-muted dark:text-ink-subtle hover:text-primary hover:bg-surface dark:hover:bg-surface-soft rounded-lg transition-all"
                  :title="btn.label"
                  @click="insertText(btn.prefix, btn.suffix)"
                >
                  {{ btn.label }}
                </button>

                <div class="h-4 w-[1px] bg-line dark:bg-surface-soft mx-2"></div>

                <span class="text-tiny font-bold text-ink-subtle uppercase tracking-wider px-2"
                  >Code</span
                >
                <button
                  v-for="btn in codeButtons"
                  :key="btn.label"
                  type="button"
                  class="p-2 text-xs font-mono font-bold text-ink-muted dark:text-ink-subtle hover:text-primary hover:bg-surface dark:hover:bg-surface-soft rounded-lg transition-all"
                  :title="btn.label"
                  @click="insertText(btn.prefix, btn.suffix)"
                >
                  {{ btn.label }}
                </button>

                <div class="h-4 w-[1px] bg-line dark:bg-surface-soft mx-2"></div>

                <!-- Smart Space: Definition Tooltip insertion -->
                <button
                  type="button"
                  class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-success dark:text-success bg-success-soft dark:bg-success-soft border border-success dark:border-success rounded-xl hover:bg-success-soft dark:hover:bg-success-soft active:scale-95 transition-all"
                  title="Associer une définition en info-bulle au texte sélectionné"
                  @click="insertDefinitionTooltip"
                >
                  <BookOpen class="w-3.5 h-3.5" />
                  Définition (Info-bulle)
                </button>

                <div class="h-4 w-[1px] bg-line dark:bg-surface-soft mx-2"></div>

                <!-- Insertion de diagramme -->
                <div class="relative inline-block">
                  <select
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-primary dark:text-primary bg-primary-soft dark:bg-primary-soft border border-primary dark:border-primary rounded-xl hover:bg-primary-soft dark:hover:bg-primary-soft transition-all focus:outline-none cursor-pointer"
                    @change="insertDiagramTag($event)"
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
                class="grid grid-cols-1 md:grid-cols-2 gap-6 p-6 bg-surface-soft dark:bg-surface-soft border-b border-line dark:border-line transition-all duration-300 animate-slide-down"
              >
                <!-- 1. Context Input Section -->
                <div class="space-y-2">
                  <h3
                    class="text-xs font-bold text-warning dark:text-warning uppercase tracking-wider flex items-center gap-1.5"
                  >
                    <Compass class="w-4 h-4" />
                    Contexte de la note
                  </h3>
                  <textarea
                    v-model="noteContext"
                    placeholder="Historique, cadre théorique ou d'apprentissage..."
                    rows="3"
                    class="w-full p-3 text-xs bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-ink dark:text-ink-subtle resize-y"
                    @input="triggerAutoSave"
                  ></textarea>
                </div>

                <!-- 2. Linked Notes Section -->
                <div class="space-y-3">
                  <h3
                    class="text-xs font-bold text-primary dark:text-primary uppercase tracking-wider flex items-center gap-1.5"
                  >
                    <LinkIcon class="w-4 h-4" />
                    Lier à d'autres notes
                  </h3>

                  <div class="flex gap-2">
                    <select
                      v-model="selectedLinkTarget"
                      class="flex-1 px-3 py-2 bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-xs font-semibold"
                    >
                      <option :value="null" disabled>Sélectionner une note...</option>
                      <option v-for="item in linkableNotes" :key="item.id" :value="item.id">
                        {{ item.title }}
                      </option>
                    </select>

                    <button
                      type="button"
                      class="px-4 py-2 text-xs font-bold text-white bg-primary hover:bg-primary-strong rounded-xl active:scale-95 transition-all shadow-sm"
                      @click="addNoteLink"
                    >
                      Lier
                    </button>
                  </div>

                  <!-- Linked notes badges -->
                  <div
                    v-if="noteLinks.length > 0"
                    class="flex flex-wrap gap-1.5 pt-1 max-h-[80px] overflow-y-auto"
                  >
                    <span
                      v-for="linkedId in noteLinks"
                      :key="linkedId"
                      class="inline-flex items-center gap-1.5 px-2.5 py-0.5 bg-surface border border-line dark:bg-surface-soft dark:border-line text-ink dark:text-ink-subtle text-tiny font-semibold rounded-lg shadow-sm"
                    >
                      {{ getNoteTitle(linkedId) }}
                      <button
                        type="button"
                        class="text-ink-subtle hover:text-danger transition-colors"
                        @click="removeNoteLink(linkedId)"
                      >
                        ✕
                      </button>
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Split Workspace (Editor + optional Live Preview) -->
            <div class="flex-1 flex w-full overflow-hidden bg-surface dark:bg-surface-soft">
              <!-- Left Pane: Editor -->
              <div
                class="flex flex-col h-full overflow-hidden cursor-text"
                :class="[
                  isLivePreviewActive ? 'w-1/2 border-r border-line dark:border-line' : 'w-full',
                ]"
                @click="textareaRef?.focus()"
              >
                <textarea
                  ref="textareaRef"
                  v-model="noteBody"
                  placeholder="Rédigez vos notes ici en Markdown..."
                  class="w-full h-full p-8 md:p-12 outline-none border-0 focus:ring-0 text-base font-mono text-ink dark:text-ink-subtle resize-none overflow-y-auto leading-relaxed bg-transparent"
                  @input="triggerAutoSave"
                  @mouseup="handleTextareaSelect($event)"
                  @keyup="handleTextareaSelect($event)"
                  @keydown.tab.prevent="handleTabKey"
                  @keydown.enter.shift.prevent="insertSoftBreak"
                ></textarea>
              </div>

              <!-- Right Pane: Real-time Live Preview -->
              <div
                v-if="isLivePreviewActive"
                class="w-1/2 h-full p-8 md:p-12 overflow-y-auto bg-surface-soft dark:bg-surface-soft border-l border-line-soft dark:border-line prose prose-slate max-w-none dark:prose-invert leading-relaxed text-sm dark:text-ink-subtle markdown-body"
              >
                <div class="border-b border-line dark:border-line pb-3 mb-6 no-print">
                  <span
                    class="text-tiny font-extrabold text-primary bg-primary-soft dark:bg-primary-soft dark:text-primary px-2.5 py-1 rounded-lg uppercase tracking-wider"
                    >Aperçu en temps réel</span
                  >
                </div>
                <div v-dompurify-html="renderMarkup(noteBody)"></div>
              </div>
            </div>
          </div>

          <!-- 2. CENTERED PREVIEW / READ MODE SHEET -->
          <div
            v-else
            class="flex-1 bg-surface-soft dark:bg-[#070913] py-10 px-4 md:px-8 print:p-0 print:bg-surface w-full"
          >
            <!-- Top Bar Actions inside Preview page sheet (Centered wrapper) -->
            <div
              class="max-w-4xl mx-auto flex flex-wrap items-center justify-between gap-y-3 no-print mb-6"
            >
              <div class="flex flex-wrap items-center gap-4">
                <button
                  class="text-sm font-semibold text-ink-muted hover:text-primary dark:text-ink-subtle dark:hover:text-primary flex items-center gap-1"
                  @click="goBack"
                >
                  <ChevronLeft class="w-4 h-4" />
                  Retour aux notes
                </button>

                <div class="h-4 w-[1px] bg-line dark:bg-surface-soft"></div>

                <!-- Mode Switcher: Lecture / Révision Active -->
                <div
                  class="flex items-center bg-surface-soft dark:bg-surface-soft p-0.5 rounded-xl border border-line dark:border-line"
                >
                  <button
                    class="px-3 py-1.5 text-xs font-bold rounded-lg transition-all"
                    :class="[
                      !notesStore.isReviewModeActive
                        ? 'bg-surface dark:bg-surface-soft text-primary shadow-sm'
                        : 'text-ink-muted hover:text-ink dark:text-ink-subtle',
                    ]"
                    @click="notesStore.isReviewModeActive = false"
                  >
                    Lecture
                  </button>
                  <button
                    class="px-3 py-1.5 text-xs font-bold rounded-lg transition-all flex items-center gap-1"
                    :class="[
                      notesStore.isReviewModeActive
                        ? 'bg-surface dark:bg-surface-soft text-primary shadow-sm'
                        : 'text-ink-muted hover:text-ink dark:text-ink-subtle',
                    ]"
                    @click="notesStore.isReviewModeActive = true"
                  >
                    <Brain class="w-3.5 h-3.5" />
                    Révision Active
                  </button>
                </div>
              </div>

              <div class="flex flex-wrap items-center gap-3">
                <!-- View Mode Toggler -->
                <button
                  class="inline-flex items-center gap-2 px-4 py-2 border border-line dark:border-line rounded-xl text-sm font-semibold hover:bg-surface-soft dark:hover:bg-surface-soft transition-all text-ink dark:text-ink-subtle"
                  @click="toggleMode"
                >
                  <Edit3 class="w-4 h-4 text-primary" />
                  Modifier la fiche
                </button>

                <!-- Guide Button (View Mode) -->
                <button
                  class="inline-flex items-center gap-2 px-4 py-2 border border-line dark:border-line rounded-xl text-sm font-semibold hover:bg-surface-soft dark:hover:bg-surface-soft transition-all text-ink-muted dark:text-ink-subtle"
                  type="button"
                  @click="showHelpModal = true"
                >
                  <HelpCircle class="w-4 h-4 text-primary" />
                  Guide
                </button>

                <!-- PDF / Print Trigger -->
                <button
                  class="inline-flex items-center gap-2 px-4 py-2 border border-transparent rounded-xl text-sm font-semibold text-white bg-primary hover:bg-primary-strong active:scale-95 transition-all shadow-md shadow-elev-primary"
                  @click="printNote"
                >
                  <FileDown class="w-4 h-4" />
                  Exporter en PDF
                </button>
              </div>
            </div>

            <!-- Fiche + sidebar Assistant IA / Métadonnées (mode lecture uniquement) -->
            <div class="max-w-6xl mx-auto flex flex-col lg:flex-row gap-6 lg:items-start">
              <!-- Cohesive Paper Sheet -->
              <div
                class="flex-1 min-w-0 bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-8 lg:p-12 shadow-xl shadow-soft-lg dark:shadow-soft-lg space-y-6 print:border-none print:shadow-none print:p-0 print:bg-white print:text-black"
              >
                <!-- Fil d'ariane (canevas Direction A) -->
                <nav
                  class="flex items-center gap-1.5 font-mono text-tiny tracking-wide text-ink-muted uppercase no-print"
                  aria-label="Fil d'ariane"
                >
                  <span>Bibliothèque</span>
                  <span aria-hidden="true">/</span>
                  <span>{{ getBinderName(binderId) }}</span>
                  <span aria-hidden="true">/</span>
                  <span>Notes</span>
                </nav>

                <!-- PRINT-ONLY DEDICATED HEADER -->
                <div
                  v-if="pdfExportOptions.includeHeader"
                  class="hidden print:block print-header-banner mb-6 pb-4 border-b-2 border-slate-900"
                >
                  <div class="flex items-center justify-between mb-3 text-xs text-slate-500">
                    <div
                      v-if="getBinderName(binderId)"
                      class="font-bold text-slate-900 uppercase tracking-wider"
                    >
                      {{ getBinderName(binderId) }}
                    </div>
                    <div class="text-[11px] font-medium text-slate-500">
                      {{ currentExportDateFormatted }}
                    </div>
                  </div>

                  <h1
                    class="text-3xl font-extrabold text-slate-950 tracking-tight leading-tight mb-2"
                  >
                    {{ title || 'Note sans titre' }}
                  </h1>

                  <div v-if="noteTags.length > 0" class="flex flex-wrap gap-1.5 mt-2">
                    <span
                      v-for="tag in noteTags"
                      :key="tag.id"
                      class="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold bg-slate-100 text-slate-800 border border-slate-300"
                    >
                      #{{ tag.name }}
                    </span>
                  </div>
                </div>

                <!-- Screen Note Title (Hidden in print if print header banner is enabled) -->
                <div
                  :class="[
                    'border-b border-line dark:border-line pb-6 print:mb-4',
                    pdfExportOptions.includeHeader ? 'print:hidden' : '',
                  ]"
                >
                  <div class="flex items-start justify-between gap-4">
                    <h1 class="text-3xl font-extrabold text-ink print:text-black">
                      {{ title || 'Note sans titre' }}
                    </h1>

                    <!-- Notation IA (notes-ia-planning-corrections, Task 5) : note la qualité
                    de la fiche elle-même, à ne pas confondre avec l'Évaluation mixte. -->
                    <button
                      type="button"
                      class="no-print shrink-0 inline-flex items-center gap-2 px-4 py-2 border border-accent dark:border-accent rounded-xl text-sm font-semibold text-accent dark:text-accent hover:bg-accent-soft dark:hover:bg-accent-soft transition-all"
                      @click="openGradeModal"
                    >
                      <Star class="w-4 h-4" />
                      Notation
                    </button>
                  </div>
                  <div class="flex items-center gap-3 mt-3 no-print">
                    <span class="text-xs font-semibold text-ink-subtle uppercase tracking-wider"
                      >Classeur :</span
                    >
                    <span
                      class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-bold text-primary bg-primary-soft dark:bg-primary-soft dark:text-primary uppercase tracking-wider"
                    >
                      {{ getBinderName(binderId) }}
                    </span>
                    <TagBadge v-for="tag in noteTags" :key="tag.id" :tag="tag" />
                  </div>
                </div>

                <!-- PRINT-ONLY TABLE OF CONTENTS -->
                <div
                  v-if="pdfExportOptions.includeToc && extractedHeadings.length > 0"
                  class="hidden print:block print-toc-block bg-slate-50 border border-slate-300 rounded-xl p-5 mb-6 break-inside-avoid"
                >
                  <div
                    class="text-xs font-black uppercase tracking-wider text-slate-700 mb-3 flex items-center gap-2 border-b border-slate-200 pb-2"
                  >
                    <span class="w-2 h-2 rounded-full bg-indigo-600 inline-block"></span>
                    Sommaire de la note
                  </div>
                  <div class="space-y-1 text-xs">
                    <div
                      v-for="(h, idx) in extractedHeadings"
                      :key="idx"
                      :class="[
                        'flex items-center justify-between',
                        h.level === 1 ? 'font-bold text-slate-900 pt-1' : '',
                        h.level === 2 ? 'font-semibold text-slate-800 pl-4' : '',
                        h.level === 3 ? 'text-slate-600 pl-8 text-[11px]' : '',
                      ]"
                    >
                      <span>• {{ h.text }}</span>
                    </div>
                  </div>
                </div>

                <!-- 1. Context Block -->
                <div
                  v-if="noteContext && pdfExportOptions.includeContext"
                  class="bg-warning-soft border-l-4 border-warning rounded-r-2xl p-5 dark:bg-warning-soft dark:border-warning print:bg-[#fffbeb] print:border-warning print:my-4 print:p-4 print:rounded-r-xl break-inside-avoid"
                >
                  <h3
                    class="text-xs font-bold text-warning dark:text-warning flex items-center gap-1.5 uppercase tracking-wider mb-2 print:text-amber-900"
                  >
                    <Compass class="w-4 h-4" />
                    Contexte de la note
                  </h3>
                  <div
                    v-dompurify-html="renderMarkup(noteContext)"
                    class="prose prose-amber max-w-none text-xs leading-relaxed dark:prose-invert print:text-black"
                  ></div>
                </div>

                <!-- Legacy Definitions Block -->
                <div
                  v-if="noteDefinition"
                  class="bg-success-soft border-l-4 border-success rounded-r-2xl p-5 dark:bg-success-soft dark:border-success print:bg-[#ecfdf5] print:border-success print:my-4 print:p-4 print:rounded-r-xl break-inside-avoid"
                >
                  <h3
                    class="text-xs font-bold text-success dark:text-success flex items-center gap-1.5 uppercase tracking-wider mb-2 print:text-emerald-900"
                  >
                    <BookOpen class="w-4 h-4" />
                    Définitions clés (Legacy)
                  </h3>
                  <div
                    v-dompurify-html="renderMarkup(noteDefinition)"
                    class="prose prose-emerald max-w-none text-xs leading-relaxed dark:prose-invert print:text-black"
                  ></div>
                </div>

                <!-- 2. Main Note Content Block -->
                <div
                  class="prose prose-slate max-w-none dark:prose-invert leading-relaxed text-sm dark:text-ink-subtle print:text-black markdown-body"
                  @click="handleMarkdownClick"
                >
                  <div v-dompurify-html="renderMarkup(noteBody)"></div>
                </div>

                <!-- PRINT-ONLY DEFINITIONS GLOSSARY -->
                <div
                  v-if="pdfExportOptions.includeGlossary && extractedDefinitions.length > 0"
                  class="hidden print:block print-glossary-block border-t-2 border-slate-900 pt-6 mt-8 break-inside-avoid"
                >
                  <h3
                    class="text-sm font-extrabold uppercase tracking-wider text-slate-950 mb-3 flex items-center gap-2"
                  >
                    <BookOpen class="w-4.5 h-4.5 text-emerald-600 inline-block" />
                    Index des Définitions Clés
                  </h3>
                  <div class="grid grid-cols-2 gap-3 text-xs">
                    <div
                      v-for="item in extractedDefinitions"
                      :key="item.term"
                      class="p-3 bg-slate-50 border border-slate-300 rounded-lg"
                    >
                      <div class="font-bold text-slate-950 border-b border-slate-200 pb-1 mb-1">
                        {{ item.term }}
                      </div>
                      <div class="text-slate-800 text-[11px] leading-relaxed">{{ item.def }}</div>
                    </div>
                  </div>
                </div>

                <!-- 3. Linked Notes Block -->
                <div
                  v-if="noteLinks.length > 0"
                  class="border-t border-line dark:border-line pt-6 no-print"
                >
                  <h3
                    class="text-xs font-bold text-ink-subtle uppercase tracking-wider flex items-center gap-1.5 mb-3"
                  >
                    <LinkIcon class="w-4.5 h-4.5 text-primary" />
                    Notes liées
                  </h3>
                  <div class="flex flex-wrap gap-2">
                    <button
                      v-for="linkedId in noteLinks"
                      :key="linkedId"
                      class="inline-flex items-center gap-1.5 px-3.5 py-2 bg-surface-soft hover:bg-primary-soft dark:bg-surface-soft dark:hover:bg-primary-soft border border-line dark:border-line rounded-xl transition-all text-xs font-semibold"
                      @click="navigateToNote(linkedId)"
                    >
                      <span>{{ getNoteTitle(linkedId) }}</span>
                      <ChevronRight class="w-3.5 h-3.5 text-ink-subtle" />
                    </button>
                  </div>
                </div>

                <!-- PRINT-ONLY FOOTER -->
                <div
                  v-if="pdfExportOptions.includeFooter"
                  class="hidden print:flex print-footer-banner pt-6 mt-8 border-t border-slate-300 text-[10px] text-slate-500 justify-between items-center"
                >
                  <span>StudyHub • Document d'étude exporté en haute définition</span>
                  <span>Fiche d'apprentissage</span>
                </div>
              </div>

              <!-- Sidebar Assistant IA / Métadonnées (canevas Direction A) -->
              <NoteSidebar
                class="w-full lg:w-72 shrink-0 no-print"
                :binder-name="getBinderName(binderId)"
                :tags="noteTags"
                :updated-at="noteUpdatedAt"
                @start-activity="startAiActivity"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Help Modal (Guide for Placeholders & Split Screen) -->
      <NoteEditHelpModal v-if="showHelpModal" @close="showHelpModal = false" />

      <!-- ============================================================ -->
      <!-- INPUT MODAL (remplace les prompt/confirm/alert natifs)       -->
      <!-- ============================================================ -->
      <NoteInputModal
        :visible="inputModal.visible"
        :title="inputModal.title"
        :description="inputModal.description"
        :icon="inputModal.icon"
        :icon-bg="inputModal.iconBg"
        :confirm-bg="inputModal.confirmBg"
        :confirm-label="inputModal.confirmLabel"
        :fields="inputModal.fields"
        @update:fields="inputModal.fields = $event"
        @confirm="inputModal.onConfirm()"
        @cancel="inputModal.onCancel()"
      />

      <!-- SM-2 Evaluation Modal -->
      <NoteEvaluationModal
        :visible="evaluationModal.visible"
        :is-evaluating="isEvaluating"
        @evaluate="submitSm2Evaluation($event)"
        @cancel="evaluationModal.visible = false"
      />

      <!-- Notation IA (notes-ia-planning-corrections, Task 5) -->
      <NoteGradeModal
        :open="gradeModal.open"
        :loading="gradeModal.loading"
        :error="gradeModal.error"
        :result="gradeModal.result"
        @close="gradeModal.open = false"
      />

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
          class="fixed z-50 bottom-6 left-1/2 -translate-x-1/2 bg-surface/95 dark:bg-surface-soft backdrop-blur-md border border-line dark:border-line rounded-2xl shadow-2xl px-4 py-2.5 flex items-center flex-wrap gap-2.5 max-w-[95vw] no-print pointer-events-auto"
        >
          <div
            class="flex items-center gap-1.5 border-r border-line dark:border-line pr-3 max-w-[150px]"
          >
            <Sparkles class="w-3.5 h-3.5 text-primary flex-shrink-0 animate-pulse" />
            <span class="text-[11px] font-bold text-ink-muted dark:text-ink-subtle truncate">
              "{{ selectionText }}"
            </span>
          </div>

          <div class="flex items-center gap-1 flex-wrap max-w-lg md:max-w-none">
            <!-- Trou Button -->
            <button
              class="px-2 py-1 bg-primary-soft hover:bg-primary-soft dark:bg-primary-soft dark:hover:bg-primary-soft text-primary dark:text-primary rounded-lg text-[9px] font-extrabold uppercase tracking-wider transition-all active:scale-95 flex items-center gap-1"
              title="Trou (Cloze)"
              @click="applySelectionTransform('trou')"
            >
              <Brain class="w-2.5 h-2.5" />
              Trou
            </button>

            <!-- QCM Button -->
            <button
              class="px-2 py-1 bg-accent-soft hover:bg-accent-soft dark:bg-accent-soft dark:hover:bg-accent-soft text-accent dark:text-accent rounded-lg text-[9px] font-extrabold uppercase tracking-wider transition-all active:scale-95 flex items-center gap-1"
              title="QCM (Choix multiples)"
              @click="applySelectionTransform('qcm')"
            >
              <HelpCircle class="w-2.5 h-2.5" />
              QCM
            </button>

            <!-- Sequence / Ordre Button -->
            <button
              class="px-2 py-1 bg-warning-soft hover:bg-warning-soft dark:bg-warning-soft dark:hover:bg-warning-soft text-warning dark:text-warning rounded-lg text-[9px] font-extrabold uppercase tracking-wider transition-all active:scale-95 flex items-center gap-1"
              title="Séquence (Ordre)"
              @click="applySelectionTransform('ordre')"
            >
              <ListOrdered class="w-2.5 h-2.5" />
              Ordre
            </button>

            <!-- Association Button -->
            <button
              class="px-2 py-1 bg-pink-50 hover:bg-pink-100 dark:bg-pink-950/40 dark:hover:bg-pink-950/80 text-pink-600 dark:text-pink-400 rounded-lg text-[9px] font-extrabold uppercase tracking-wider transition-all active:scale-95 flex items-center gap-1"
              title="Association"
              @click="applySelectionTransform('assoc')"
            >
              <LinkIcon class="w-2.5 h-2.5" />
              Assoc
            </button>

            <!-- Vrai/Faux Button -->
            <button
              class="px-2 py-1 bg-danger-soft hover:bg-danger-soft dark:bg-danger-soft dark:hover:bg-danger-soft text-danger dark:text-danger rounded-lg text-[9px] font-extrabold uppercase tracking-wider transition-all active:scale-95 flex items-center gap-1"
              title="Vrai / Faux"
              @click="applySelectionTransform('vf')"
            >
              <CheckCircle2 class="w-2.5 h-2.5" />
              V/F
            </button>

            <!-- Definition Tooltip Button -->
            <button
              class="px-2 py-1 bg-success-soft hover:bg-success-soft dark:bg-success-soft dark:hover:bg-success-soft text-success dark:text-success rounded-lg text-[9px] font-extrabold uppercase tracking-wider transition-all active:scale-95 flex items-center gap-1"
              title="Définition info-bulle"
              @click="applySelectionTransform('def')"
            >
              <BookOpen class="w-2.5 h-2.5" />
              Définition
            </button>

            <!-- Math Bloc Button -->
            <button
              class="px-2 py-1 bg-cyan-50 hover:bg-cyan-100 dark:bg-cyan-950/40 dark:hover:bg-cyan-950/80 text-cyan-600 dark:text-cyan-400 rounded-lg text-[9px] font-extrabold uppercase tracking-wider transition-all active:scale-95 flex items-center gap-1"
              title="Math Bloc (LaTeX)"
              @click="applySelectionTransform('math_bloc')"
            >
              <Sigma class="w-2.5 h-2.5" />
              Math Bloc
            </button>

            <!-- Math Ligne Button -->
            <button
              class="px-2 py-1 bg-teal-50 hover:bg-teal-100 dark:bg-teal-950/40 dark:hover:bg-teal-950/80 text-teal-600 dark:text-teal-400 rounded-lg text-[9px] font-extrabold uppercase tracking-wider transition-all active:scale-95 flex items-center gap-1"
              title="Math Ligne (LaTeX)"
              @click="applySelectionTransform('math_ligne')"
            >
              <Sigma class="w-2.5 h-2.5" />
              Math Ligne
            </button>

            <!-- Diagramme Button -->
            <button
              class="px-2 py-1 bg-sky-50 hover:bg-sky-100 dark:bg-sky-950/40 dark:hover:bg-sky-950/80 text-sky-600 dark:text-sky-400 rounded-lg text-[9px] font-extrabold uppercase tracking-wider transition-all active:scale-95 flex items-center gap-1"
              title="Insérer un diagramme / schéma"
              @click="applySelectionTransform('diagramme')"
            >
              <Image class="w-2.5 h-2.5" />
              Schéma
            </button>

            <div class="h-4 w-[1px] bg-line dark:bg-surface-soft mx-1"></div>

            <!-- Bold Button -->
            <button
              class="px-1.5 py-1 hover:bg-surface-soft dark:hover:bg-surface-soft text-ink dark:text-ink-subtle rounded-lg text-[9px] font-bold transition-all active:scale-95"
              title="Gras"
              @click="applySelectionTransform('gras')"
            >
              <strong>G</strong>
            </button>

            <!-- Italic Button -->
            <button
              class="px-1.5 py-1 hover:bg-surface-soft dark:hover:bg-surface-soft text-ink dark:text-ink-subtle rounded-lg text-[9px] font-bold transition-all active:scale-95 italic"
              title="Italique"
              @click="applySelectionTransform('italique')"
            >
              I
            </button>

            <!-- Code Button (Inline) -->
            <button
              class="px-1.5 py-1 hover:bg-surface-soft dark:hover:bg-surface-soft text-ink dark:text-ink-subtle rounded-lg text-[9px] font-mono font-bold transition-all active:scale-95"
              title="Code en ligne"
              @click="applySelectionTransform('code')"
            >
              &lt;/&gt;
            </button>

            <!-- Bloc Code Button -->
            <button
              class="px-1.5 py-1 hover:bg-surface-soft dark:hover:bg-surface-soft text-ink dark:text-ink-subtle rounded-lg text-[9px] font-mono font-bold transition-all active:scale-95"
              title="Bloc de code"
              @click="applySelectionTransform('bloc_code')"
            >
              { }
            </button>
          </div>
        </div>
      </transition>

      <!-- PDF Export Modal -->
      <NotePdfExportModal
        :is-open="showPdfModal"
        :note-title="title"
        :binder-name="getBinderName(binderId)"
        :headings-count="extractedHeadings.length"
        :definitions-count="extractedDefinitions.length"
        :has-context="!!noteContext"
        @close="showPdfModal = false"
        @export="handlePdfExport"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'
import { useNotesStore } from '../../stores/notes'
import { useBindersStore } from '../../stores/binders'
import { useTagsStore, type Tag } from '../../stores/tags'
import { BaseCard, BaseEmptyState, BaseButton } from '../../components/ui/base'
import TagBadge from '../../components/ui/TagBadge.vue'
import TagSelector from '../../components/ui/TagSelector.vue'
import NotePdfExportModal, {
  type PdfExportOptions,
} from '../../components/notes/NotePdfExportModal.vue'
import NoteEditHelpModal from '../../components/notes/NoteEditHelpModal.vue'
import NoteInputModal, { type ModalField } from '../../components/notes/NoteInputModal.vue'
import NoteEvaluationModal from '../../components/notes/NoteEvaluationModal.vue'
import NoteGradeModal from '../../components/notes/NoteGradeModal.vue'
import notationService from '../../services/notationService'
import type { NotationResult } from '../../services/notationService'
import NoteSidebar from '../../components/notes/NoteSidebar.vue'
import {
  ChevronLeft,
  Menu,
  Eye,
  EyeOff,
  Copy,
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
  Image,
  Star,
  AlertCircle,
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
    },
  },
})

const notesStore = useNotesStore()
const bindersStore = useBindersStore()
const tagsStore = useTagsStore()

const placeholderStates = ref<Record<string, any>>({})
const noteFlashcards = ref<any[]>([])
const route = useRoute()
const router = useRouter()

const noteId = ref(route.params.id as string)
const allUserDiagrams = ref<any[]>([])
const loadedDiagrams = ref<Record<number, any>>({})
const loading = ref(true)
const loadError = ref(false)
const isSaving = ref(false)
const saveStatus = ref('Enregistré')
// Note partagée par un cours (lecture seule) : aucune édition possible.
const isReadOnly = ref(false)
const isCopying = ref(false)
const isEditMode = computed({
  get: () => !isReadOnly.value && route.query.edit === 'true',
  set: (val) => {
    if (isReadOnly.value) return
    router.replace({ query: { ...route.query, edit: val ? 'true' : undefined } })
  },
})
const showSettings = ref(false)
const showHelpModal = ref(false)
const showPdfModal = ref(false)

const pdfExportOptions = ref<PdfExportOptions>({
  theme: 'modern',
  fontSize: 'standard',
  includeHeader: true,
  includeToc: true,
  includeContext: true,
  includeGlossary: true,
  includeFooter: true,
})

const extractedHeadings = computed(() => {
  if (!noteBody.value) return []
  const matches = Array.from(noteBody.value.matchAll(/^(#{1,3})\s+(.+)$/gm))
  return matches.map((match) => ({
    level: match[1].length,
    text: match[2].trim().replace(/[*_~`]/g, ''),
  }))
})

const extractedDefinitions = computed(() => {
  const fullText =
    (noteContext.value || '') + '\n' + (noteDefinition.value || '') + '\n' + (noteBody.value || '')
  const matches = Array.from(fullText.matchAll(/\[([^\]]+)\]\{def:([^\}]+)\}/g))
  const map = new Map<string, string>()
  for (const match of matches) {
    const term = match[1].trim()
    const def = match[2].trim()
    if (term && def && !map.has(term)) {
      map.set(term, def)
    }
  }
  return Array.from(map.entries()).map(([term, def]) => ({ term, def }))
})

const currentExportDateFormatted = computed(() => {
  return new Date().toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
})

// Handler unique appelé depuis l'emit `start-activity` de NoteSidebar (Assistant IA :
// Évaluation mixte / Méthode de la feuille blanche / Méthode Feynman).
function startAiActivity(type: string) {
  router.push(`/notes/${noteId.value}/${type}`)
}
const isLivePreviewActive = ref(false)

function toggleShortcutSidebar() {
  window.dispatchEvent(new CustomEvent('studyhub:toggle-sidebar'))
}

// Evaluation SM-2 Popup Modal State
const evaluationModal = ref({
  visible: false,
  cardId: null as number | null,
  rawTag: '',
})

const isEvaluating = ref(false)

function openEvaluationModal(cardId: number, rawTag: string) {
  evaluationModal.value = {
    visible: true,
    cardId,
    rawTag,
  }
}

// Notation IA (notes-ia-planning-corrections, Task 5) : meme flux async (Celery +
// polling, repli synchrone) que evaluateFeynman() dans NoteFeynman.vue.
const gradeModal = ref<{
  open: boolean
  loading: boolean
  error: string | null
  result: NotationResult | null
}>({
  open: false,
  loading: false,
  error: null,
  result: null,
})

async function openGradeModal() {
  gradeModal.value = { open: true, loading: true, error: null, result: null }
  try {
    const res = await notationService.grade(noteId.value)
    if (res.status === 'SUCCESS' && res.result) {
      gradeModal.value.result = res.result
      gradeModal.value.loading = false
      return
    }
    const taskId = res.task_id
    if (!taskId) throw new Error("L'API n'a pas retourné d'identifiant de tâche (task_id).")

    let finished = false
    let attempts = 0
    const maxAttempts = 60
    while (!finished && attempts < maxAttempts) {
      attempts++
      await new Promise((resolve) => setTimeout(resolve, 2000))
      const poll = await notationService.pollTask(taskId)
      if (poll.status === 'SUCCESS') {
        finished = true
        gradeModal.value.result = poll.result ?? null
      } else if (poll.status === 'FAILURE' || poll.error) {
        finished = true
        throw new Error(poll.error?.message || 'La notation a échoué.')
      }
    }
    if (!finished) throw new Error('La notation a mis trop de temps. Veuillez réessayer.')
  } catch (err) {
    gradeModal.value.error = err instanceof Error ? err.message : 'La notation IA a échoué.'
    console.error('Erreur de notation IA', err)
  } finally {
    gradeModal.value.loading = false
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
const savedSelectionContent = ref('') // snapshot du textarea au moment de la sélection
const showSelectionMenu = ref(false)
const selectionMenuPos = ref({ top: 0, left: 0 })

// ---------------------------------------------------------------
// Modal stylisé (remplace prompt / confirm / alert) — rendu délégué à
// NoteInputModal.vue (composant purement présentationnel) ; la logique de
// transformation par type d'insertion reste ici, dans applySelectionTransform.
// ---------------------------------------------------------------
interface ModalConfig {
  visible: boolean
  title: string
  description?: string
  icon: Component
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
  icon: BookOpen,
  fields: [],
  onConfirm: () => {},
  onCancel: () => {},
})

function openModal(
  config: Omit<ModalConfig, 'visible' | 'onConfirm' | 'onCancel'>,
): Promise<ModalField[] | null> {
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
      },
    }
  })
}

const title = ref('')
const binderId = ref<string | null>(null)
const noteTags = ref<Tag[]>([])
const noteUpdatedAt = ref('')
const isPublic = ref(false)
const shareToken = ref<string | null>(null)
const sharePopupVisible = ref(false)
const shareCopied = ref(false)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

// Structured Notes Divisions
const noteContext = ref('')
const noteDefinition = ref('')
const noteBody = ref('')
const noteLinks = ref<string[]>([])

const selectedLinkTarget = ref<string | null>(null)

let autoSaveTimer: any = null

const formatButtons = [
  { label: 'Titre H1', prefix: '# ', suffix: '' },
  { label: 'Titre H2', prefix: '## ', suffix: '' },
  { label: 'Gras', prefix: '**', suffix: '**' },
  { label: 'Italique', prefix: '*', suffix: '*' },
]

const latexButtons = [
  { label: 'Bloc Équation', prefix: '$$\n', suffix: '\n$$' },
  { label: 'En Ligne', prefix: '$', suffix: '$' },
  { label: 'Fraction', prefix: '\\frac{', suffix: '}{}' },
  { label: 'Somme', prefix: '\\sum_{', suffix: '}^{}' },
  { label: 'Intégrale', prefix: '\\int_{', suffix: '}^{}' },
]

const codeButtons = [
  { label: 'En Ligne', prefix: '`', suffix: '`' },
  { label: 'Bloc Code', prefix: '```\n', suffix: '\n```' },
]

// Reload components when route parameter changes (for linked notes navigation)
watch(
  () => route.params.id,
  async (newVal) => {
    if (newVal) {
      noteId.value = newVal as string
      await loadNoteDetails()
    }
  },
)

onMounted(async () => {
  // Afficher la note d'abord : on n'attend plus le chargement des listes
  // auxiliaires (jusqu'à 1000 notes/classeurs/tags/diagrammes) avant le rendu.
  await loadNoteDetails()

  // Listes auxiliaires en arrière-plan (sélecteurs de liens, classeurs, tags,
  // diagrammes). Les libellés se remplissent réactivement à leur arrivée.
  Promise.all([
    notesStore.fetchNotes(),
    bindersStore.fetchBinders(),
    tagsStore.fetchTags(),
    loadUserDiagrams(),
  ]).catch(() => {
    /* non bloquant : l'éditeur reste utilisable */
  })
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

watch(
  noteBody,
  (newVal) => {
    const matches = newVal.matchAll(/\[diagram:(\d+)\]/g)
    for (const match of matches) {
      const id = Number(match[1])
      fetchDiagramIfNeeded(id)
    }
  },
  { immediate: true },
)

function insertDiagramTag(event: Event) {
  const select = event.target as HTMLSelectElement
  const id = select.value
  if (!id) return

  insertText(`[diagram:${id}]`, '')
  select.value = '' // Reset
}

async function loadNoteDetails() {
  loading.value = true
  loadError.value = false
  isSaving.value = false
  saveStatus.value = 'Enregistré'

  try {
    // notesStore.fetchNoteById capture déjà ses propres erreurs réseau et
    // retombe sur un `find` local (donc ne rejette jamais) : un échec se
    // traduit par une note absente (`undefined`), pas par une exception.
    const note = await notesStore.fetchNoteById(noteId.value)
    if (!note) {
      loadError.value = true
      return
    }

    title.value = note.title
    binderId.value = note.binder_id
    isReadOnly.value = !!(note as any).read_only
    isPublic.value = (note as any).is_public || false
    shareToken.value = (note as any).share_token || null
    noteFlashcards.value = (note as any).flashcards || []
    noteTags.value = (note as any).tags || []
    noteUpdatedAt.value = note.updated_at || ''

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
  } catch (error) {
    console.error(`Erreur lors du chargement de la note ${noteId.value}`, error)
    loadError.value = true
  } finally {
    loading.value = false
  }
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
    setTimeout(() => {
      shareCopied.value = false
    }, 2000)
  } catch {}
}

// Structured Divisions Parsers
function parseStructuredNote(rawContent: string) {
  let contextVal = ''
  let definitionVal = ''
  let bodyVal = rawContent
  let linkedIdsVal: string[] = []

  // Extraire les liens
  const linksMatch = rawContent.match(/<!-- LINKED_NOTES: ([a-fA-F0-9-,\s]*) -->/)
  if (linksMatch) {
    linkedIdsVal = linksMatch[1]
      .split(',')
      .map((id) => id.trim())
      .filter((id) => id.length > 0)
  }

  // Extraire le contexte
  const contextMatch = rawContent.match(
    /<!-- SECTION_CONTEXT -->([\s\S]*?)<!-- END_SECTION_CONTEXT -->/,
  )
  if (contextMatch) {
    contextVal = contextMatch[1].trim()
  }

  // Extraire la définition
  const defMatch = rawContent.match(
    /<!-- SECTION_DEFINITION -->([\s\S]*?)<!-- END_SECTION_DEFINITION -->/,
  )
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
    linkedIds: linkedIdsVal,
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
  if (!cardId) {
    // En révision active, on n'affiche pas le rappel « En attente de sauvegarde… »
    // (bruit visuel pendant la révision) : seul le mode Lecture/édition l'indique.
    if (notesStore.isReviewModeActive) return ''
    return `<span class="text-tiny text-ink-subtle italic font-semibold align-middle">En attente de sauvegarde...</span>`
  }
  const state = placeholderStates.value[rawTag]
  if (!state || state.score === undefined) return ''

  const buttons = [
    { label: 'À revoir', val: 1 },
    { label: 'Difficile', val: 2 },
    { label: 'Correct', val: 3 },
    { label: 'Facile', val: 5 },
  ]

  const b = buttons.find((x) => x.val === state.score)
  return `<button type="button" data-action="sm2-re-evaluate" data-card-id="${cardId}" data-tag="${encodeURIComponent(rawTag)}" class="ml-1.5 inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-primary-soft hover:bg-primary-soft dark:bg-primary-soft dark:hover:bg-primary-soft text-tiny font-bold text-primary dark:text-primary border border-primary dark:border-primary align-middle transition-all cursor-pointer">★ ${b ? b.label : state.score}</button>`
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
      return `<span class="text-danger font-bold border border-danger p-1 rounded">LaTeX Block Error: ${formula}</span>`
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
      return `<span class="text-danger font-bold">LaTeX Inline Error: ${formula}</span>`
    }
  })

  // 3. Definition Tooltips [term]{def:definition}
  temp = temp.replace(/\[([^\]]+)\]\{def:([^\}]+)\}/g, (_match, term, definition) => {
    const html = `<span class="group relative inline-block underline decoration-success decoration-dashed cursor-help bg-success-soft/30 dark:bg-success-soft/20 px-1.5 py-0.5 rounded transition-all duration-200" def-term="${term}">${term}<span class="pointer-events-none absolute bottom-full left-1/2 z-50 mb-2 w-64 -translate-x-1/2 rounded-xl bg-ink dark:bg-ink p-3 text-xs font-medium text-app dark:text-app shadow-xl opacity-0 transition-opacity duration-200 group-hover:opacity-100 leading-normal normal-case text-center">${definition}</span><span class="hidden print:inline text-xs text-success dark:text-success font-normal italic"> (${definition})</span></span>`
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
        <div class="flex items-center gap-2 p-4 border border-line dark:border-line rounded-2xl bg-surface-soft/20 text-xs font-semibold text-ink-subtle my-4 select-none">
          <svg class="animate-spin h-4 w-4 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
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

  const isReview = notesStore.isReviewModeActive
  const shuffleArray = (arr: any[]) =>
    arr
      .map((a: any) => [Math.random(), a])
      .sort((a: any, b: any) => a[0] - b[0])
      .map((a: any) => a[1])

  // Trou: {{trou::mot caché}}
  temp = temp.replace(/\{\{trou::(.*?)\}\}/g, (rawTag, word) => {
    const card = noteFlashcards.value.find((c) => c.original_text === rawTag)
    const cardId = card ? card.id : null

    if (!isReview) {
      const displayHtml = `<span class="bg-primary-soft dark:bg-primary-soft text-primary dark:text-primary px-1.5 py-0.5 rounded font-semibold border-b border-primary">${word}</span>`
      const key = `REVISIONPLACEHOLDER${placeholders.length}`
      placeholders.push(displayHtml)
      return key
    } else {
      placeholderStates.value[rawTag] = placeholderStates.value[rawTag] || { revealed: false }
      const state = placeholderStates.value[rawTag]

      let elementHtml = ''
      if (!state.revealed) {
        elementHtml = `<span class="px-2.5 py-0.5 bg-surface-soft dark:bg-surface-soft text-transparent rounded-lg cursor-pointer border border-line dark:border-line select-none hover:bg-line dark:hover:bg-line hover:text-ink-subtle/10 active:scale-95 transition-all inline-block align-middle font-mono font-bold" data-action="reveal" data-tag="${encodeURIComponent(rawTag)}">???</span>`
      } else {
        elementHtml = `<span class="bg-primary-soft/80 dark:bg-primary-soft text-primary dark:text-primary px-2 py-0.5 rounded-lg font-bold border-b border-primary inline-flex items-center align-middle select-all transition-all">${word}${renderSm2Buttons(cardId, rawTag)}</span>`
      }
      const key = `REVISIONPLACEHOLDER${placeholders.length}`
      placeholders.push(elementHtml)
      return key
    }
  })

  // QCM: {{qcm::Question ?::Option1|*OptionCorrecte*|Option3}}
  temp = temp.replace(/\{\{qcm::(.*?)::(.*?)\}\}/g, (rawTag, question, optionsStr) => {
    const card = noteFlashcards.value.find((c) => c.original_text === rawTag)
    const cardId = card ? card.id : null
    const options = optionsStr.split('|').map((o: string) => o.trim())

    if (!isReview) {
      const listItems = options
        .map((opt: string) => {
          const isCorrect = opt.startsWith('*') && opt.endsWith('*')
          const cleanOpt = opt.replace(/\*/g, '')
          return isCorrect
            ? `<li class="font-extrabold text-success dark:text-success">✓ ${cleanOpt} (Correct)</li>`
            : `<li>${cleanOpt}</li>`
        })
        .join('')

      const displayHtml = `
        <div class="bg-surface-soft/50 dark:bg-surface-soft/50 p-4 border border-line dark:border-line rounded-2xl my-4 max-w-2xl shadow-sm not-prose">
          <strong class="text-tiny uppercase tracking-wider text-ink-subtle font-bold block mb-1">QCM</strong>
          <p class="font-bold text-sm text-ink dark:text-ink-subtle mb-2">${question}</p>
          <ul class="list-none pl-0 mt-2 space-y-1 text-xs text-ink-muted dark:text-ink-subtle">${listItems}</ul>
        </div>
      `
      const key = `REVISIONPLACEHOLDER${placeholders.length}`
      placeholders.push(displayHtml)
      return '\n\n' + key + '\n\n'
    } else {
      placeholderStates.value[rawTag] = placeholderStates.value[rawTag] || {
        answered: false,
        selectedOption: null,
      }
      const state = placeholderStates.value[rawTag]

      const buttonsHtml = options
        .map((opt: string) => {
          const isCorrect = opt.startsWith('*') && opt.endsWith('*')
          const cleanOpt = opt.replace(/\*/g, '')
          let btnClass =
            'px-3 py-1.5 border border-line dark:border-line rounded-xl hover:bg-surface-soft dark:hover:bg-surface-soft text-xs font-semibold transition-all active:scale-95'

          if (state.answered) {
            if (isCorrect) {
              btnClass =
                'px-3 py-1.5 bg-success-soft dark:bg-success-soft border border-success dark:border-success text-success dark:text-success rounded-xl text-xs font-bold'
            } else if (state.selectedOption === cleanOpt) {
              btnClass =
                'px-3 py-1.5 bg-danger-soft dark:bg-danger-soft border border-danger dark:border-danger text-danger dark:text-danger rounded-xl text-xs font-bold'
            } else {
              btnClass =
                'px-3 py-1.5 border border-line dark:border-line opacity-40 rounded-xl text-xs font-semibold'
            }
          }
          return `<button type="button" class="${btnClass}" data-action="qcm-select" data-tag="${encodeURIComponent(rawTag)}" data-option="${encodeURIComponent(cleanOpt)}" ${state.answered ? 'disabled' : ''}>${cleanOpt}</button>`
        })
        .join(' ')

      const elementHtml = `
        <div class="bg-surface-soft/50 dark:bg-surface-soft/50 p-4 border border-line dark:border-line rounded-2xl my-4 max-w-2xl shadow-sm not-prose">
          <div class="flex items-center justify-between mb-1.5">
            <strong class="text-tiny uppercase tracking-wider text-ink-subtle font-bold">QCM</strong>
            ${state.answered ? renderSm2Buttons(cardId, rawTag) : ''}
          </div>
          <p class="font-bold text-sm text-ink dark:text-ink-subtle mb-3">${question}</p>
          <div class="flex flex-wrap gap-2">${buttonsHtml}</div>
        </div>
      `
      const key = `REVISIONPLACEHOLDER${placeholders.length}`
      placeholders.push(elementHtml)
      return '\n\n' + key + '\n\n'
    }
  })

  // VF: {{vf::Affirmation::Vrai/Faux::Justification}}
  temp = temp.replace(
    /\{\{vf::(.*?)::(.*?)::(.*?)\}\}/g,
    (rawTag, assertion, answer, justification) => {
      const card = noteFlashcards.value.find((c) => c.original_text === rawTag)
      const cardId = card ? card.id : null
      const isVrai = answer.trim().toLowerCase() === 'vrai'

      if (!isReview) {
        const displayHtml = `
        <div class="bg-surface-soft/50 dark:bg-surface-soft/50 p-4 border border-line dark:border-line rounded-2xl my-4 max-w-2xl shadow-sm not-prose">
          <strong class="text-tiny uppercase tracking-wider text-ink-subtle font-bold block mb-1">Vrai ou Faux</strong>
          <p class="font-semibold text-sm text-ink dark:text-ink-subtle">${assertion}</p>
          <div class="mt-2 text-xs font-bold">Réponse : <span class="${isVrai ? 'text-success dark:text-success' : 'text-danger dark:text-danger'}">${answer}</span></div>
          <div class="text-xs text-ink-muted dark:text-ink-subtle italic mt-1">${justification}</div>
        </div>
      `
        const key = `REVISIONPLACEHOLDER${placeholders.length}`
        placeholders.push(displayHtml)
        return '\n\n' + key + '\n\n'
      } else {
        placeholderStates.value[rawTag] = placeholderStates.value[rawTag] || {
          answered: false,
          selectedAnswer: null,
        }
        const state = placeholderStates.value[rawTag]

        const btns = ['Vrai', 'Faux']
          .map((btnVal) => {
            let btnClass =
              'px-4 py-2 border border-line dark:border-line rounded-xl hover:bg-surface-soft dark:hover:bg-surface-soft text-xs font-bold transition-all active:scale-95'
            const isThisCorrect = btnVal.toLowerCase() === answer.trim().toLowerCase()

            if (state.answered) {
              if (isThisCorrect) {
                btnClass =
                  'px-4 py-2 bg-success-soft dark:bg-success-soft border border-success dark:border-success text-success dark:text-success rounded-xl text-xs font-bold'
              } else if (state.selectedAnswer === btnVal) {
                btnClass =
                  'px-4 py-2 bg-danger-soft dark:bg-danger-soft border border-danger dark:border-danger text-danger dark:text-danger rounded-xl text-xs font-bold'
              } else {
                btnClass =
                  'px-4 py-2 border border-line dark:border-line opacity-40 rounded-xl text-xs font-bold'
              }
            }
            return `<button type="button" class="${btnClass}" data-action="vf-select" data-tag="${encodeURIComponent(rawTag)}" data-value="${btnVal}" ${state.answered ? 'disabled' : ''}>${btnVal}</button>`
          })
          .join(' ')

        const elementHtml = `
        <div class="bg-surface-soft/50 dark:bg-surface-soft/50 p-4 border border-line dark:border-line rounded-2xl my-4 max-w-2xl shadow-sm not-prose">
          <div class="flex items-center justify-between mb-1.5">
            <strong class="text-tiny uppercase tracking-wider text-ink-subtle font-bold">Vrai ou Faux</strong>
            ${state.answered ? renderSm2Buttons(cardId, rawTag) : ''}
          </div>
          <p class="font-semibold text-sm text-ink dark:text-ink-subtle mb-3">${assertion}</p>
          <div class="flex gap-3 mb-3">${btns}</div>
          ${
            state.answered
              ? `
            <div class="bg-surface-soft/40 dark:bg-surface-soft/40 p-3 rounded-xl text-xs mt-3">
              <div class="font-bold text-ink dark:text-ink-subtle mb-1">Justification :</div>
              <div class="italic text-ink-muted dark:text-ink-subtle">${justification}</div>
            </div>
          `
              : ''
          }
        </div>
      `
        const key = `REVISIONPLACEHOLDER${placeholders.length}`
        placeholders.push(elementHtml)
        return '\n\n' + key + '\n\n'
      }
    },
  )

  // Ordre: {{ordre::Titre::Étape 1 > Étape 2 > Étape 3}}
  temp = temp.replace(/\{\{ordre::(.*?)::(.*?)\}\}/g, (rawTag, title, stepsStr) => {
    const card = noteFlashcards.value.find((c) => c.original_text === rawTag)
    const cardId = card ? card.id : null
    const steps = stepsStr.split('>').map((s: string) => s.trim())

    const cleanStep = (str: string) => {
      const cleaned = str.replace(/^(?:étape\s*\d+[\s\-:]*|\d+[\.\s\-:]+)\s*/i, '').trim()
      return cleaned.length > 0 ? cleaned : str
    }

    if (!isReview) {
      const stepItems = steps.map((s: string) => `<li class="mb-1">${cleanStep(s)}</li>`).join('')
      const displayHtml = `
        <div class="bg-surface-soft/50 dark:bg-surface-soft/50 p-2.5 border border-line dark:border-line rounded-xl my-2 max-w-2xl shadow-sm not-prose">
          <strong class="text-tiny uppercase tracking-wider text-ink-subtle font-bold block mb-0.5">Séquence : ${title}</strong>
          <ol class="list-decimal mt-1.5 space-y-0.5 text-xs" style="margin-left: 1rem !important; padding-left: 1rem !important;">${stepItems}</ol>
        </div>
      `
      const key = `REVISIONPLACEHOLDER${placeholders.length}`
      placeholders.push(displayHtml)
      return '\n\n' + key + '\n\n'
    } else {
      placeholderStates.value[rawTag] = placeholderStates.value[rawTag] || {
        answered: false,
        order: shuffleArray([...steps]),
      }
      const state = placeholderStates.value[rawTag]

      const stepButtons = state.order
        .map((step: string, idx: number) => {
          return `
          <div class="flex items-center justify-between p-2.5 bg-surface dark:bg-surface border border-line dark:border-line rounded-xl text-xs font-semibold mb-1.5 shadow-sm">
            <span>${cleanStep(step)}</span>
            ${
              !state.answered
                ? `
              <div class="flex gap-1 no-print">
                <button type="button" class="px-1.5 py-0.5 hover:bg-surface-soft dark:hover:bg-surface-soft rounded text-ink-subtle hover:text-primary" data-action="order-move" data-tag="${encodeURIComponent(rawTag)}" data-index="${idx}" data-dir="up">▲</button>
                <button type="button" class="px-1.5 py-0.5 hover:bg-surface-soft dark:hover:bg-surface-soft rounded text-ink-subtle hover:text-primary" data-action="order-move" data-tag="${encodeURIComponent(rawTag)}" data-index="${idx}" data-dir="down">▼</button>
              </div>
            `
                : ''
            }
          </div>
        `
        })
        .join('')

      const elementHtml = `
        <div class="bg-surface-soft/50 dark:bg-surface-soft/50 p-4 border border-line dark:border-line rounded-2xl my-4 max-w-2xl shadow-sm not-prose">
          <div class="flex items-center justify-between mb-1.5">
            <strong class="text-tiny uppercase tracking-wider text-ink-subtle font-bold">Séquence : ${title}</strong>
            ${state.answered ? renderSm2Buttons(cardId, rawTag) : ''}
          </div>
          <div class="mt-3">${stepButtons}</div>
          
          ${
            !state.answered
              ? `
            <button type="button" class="w-full mt-3 px-4 py-2 bg-primary hover:bg-primary-strong text-white font-bold rounded-xl text-xs active:scale-95 transition-all border border-transparent" data-action="order-validate" data-tag="${encodeURIComponent(rawTag)}">
              Valider l'ordre
            </button>
          `
              : `
            <div class="mt-3 bg-surface-soft/40 dark:bg-surface-soft/40 p-3 rounded-xl text-xs flex flex-col gap-1.5">
              <div class="font-bold text-ink dark:text-ink-subtle">Ordre attendu :</div>
              <div class="flex flex-wrap items-center gap-1">
                ${steps.map((s: string) => `<span class="bg-surface dark:bg-surface-soft px-2 py-1 rounded-lg border border-line/50 dark:border-line/50 text-tiny font-semibold">${cleanStep(s)}</span>`).join(' ➜ ')}
              </div>
            </div>
          `
          }
        </div>
      `
      const key = `REVISIONPLACEHOLDER${placeholders.length}`
      placeholders.push(elementHtml)
      return '\n\n' + key + '\n\n'
    }
  })

  // Assoc: {{assoc::Titre::A=1 | B=2 | C=3}}
  temp = temp.replace(/\{\{assoc::(.*?)::(.*?)\}\}/g, (rawTag, title, pairsStr) => {
    const card = noteFlashcards.value.find((c) => c.original_text === rawTag)
    const cardId = card ? card.id : null
    const pairs = pairsStr.split('|').map((p: string) => {
      // Utiliser indexOf pour splitter uniquement au premier '=' (évite les bugs avec les expressions contenant des =)
      const eqIdx = p.indexOf('=')
      if (eqIdx === -1) return { key: p.trim(), value: '' }
      return { key: p.substring(0, eqIdx).trim(), value: p.substring(eqIdx + 1).trim() }
    })

    if (!isReview) {
      const rows = pairs
        .map(
          (p: { key: string; value: string }) =>
            `<tr><td class="border border-line dark:border-line p-2 font-semibold text-ink dark:text-ink-subtle">${p.key}</td><td class="border border-line dark:border-line p-2 text-ink-muted dark:text-ink-subtle">${p.value}</td></tr>`,
        )
        .join('')
      const displayHtml = `
        <div class="bg-surface-soft/50 dark:bg-surface-soft/50 p-4 border border-line dark:border-line rounded-2xl my-4 max-w-2xl shadow-sm not-prose">
          <strong class="text-tiny uppercase tracking-wider text-ink-subtle font-bold block mb-1">Associations : ${title}</strong>
          <table class="table-auto text-xs mt-3 w-full border-collapse border border-line dark:border-line">
            <thead>
              <tr class="bg-surface-soft dark:bg-surface-soft font-bold">
                <th class="border border-line dark:border-line p-2 text-left">Clé</th>
                <th class="border border-line dark:border-line p-2 text-left">Liaison</th>
              </tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      `
      const key = `REVISIONPLACEHOLDER${placeholders.length}`
      placeholders.push(displayHtml)
      return '\n\n' + key + '\n\n'
    } else {
      const keysList = pairs.map((p: any) => p.key)
      const valuesList = pairs.map((p: any) => p.value)

      placeholderStates.value[rawTag] = placeholderStates.value[rawTag] || {
        answered: false,
        shuffledKeys: shuffleArray([...keysList]),
        shuffledValues: shuffleArray([...valuesList]),
        selectedKey: null,
        matches: {},
      }

      const state = placeholderStates.value[rawTag]

      const keysHtml = state.shuffledKeys
        .map((k: string) => {
          const isMatched = state.matches[k] !== undefined
          let btnClass =
            'p-2 border text-left rounded-xl text-xs font-semibold shadow-sm transition-all'
          if (state.selectedKey === k) {
            btnClass +=
              ' border-primary bg-primary-soft dark:bg-primary-soft text-primary dark:text-primary ring-2 ring-primary/10'
          } else if (isMatched) {
            btnClass +=
              ' border-line dark:border-line bg-surface-soft dark:bg-surface-soft text-ink-subtle cursor-not-allowed opacity-60'
          } else {
            btnClass +=
              ' border-line dark:border-line hover:bg-surface-soft dark:hover:bg-surface-soft cursor-pointer'
          }

          return `<button type="button" class="${btnClass}" data-action="assoc-key-select" data-tag="${encodeURIComponent(rawTag)}" data-key="${encodeURIComponent(k)}" ${isMatched || state.answered ? 'disabled' : ''}>${k}</button>`
        })
        .join('')

      const valuesHtml = state.shuffledValues
        .map((v: string) => {
          const isMatched = Object.values(state.matches).includes(v)
          let btnClass =
            'p-2 border text-left rounded-xl text-xs font-semibold shadow-sm transition-all'
          if (isMatched) {
            btnClass +=
              ' border-line dark:border-line bg-surface-soft dark:bg-surface-soft text-ink-subtle cursor-not-allowed opacity-60'
          } else {
            btnClass +=
              ' border-line dark:border-line hover:bg-surface-soft dark:hover:bg-surface-soft cursor-pointer'
          }

          return `<button type="button" class="${btnClass}" data-action="assoc-value-select" data-tag="${encodeURIComponent(rawTag)}" data-value="${encodeURIComponent(v)}" ${isMatched || state.answered || !state.selectedKey ? 'disabled' : ''}>${v}</button>`
        })
        .join('')

      const matchesHtml = Object.entries(state.matches)
        .map(([k, v]) => {
          return `<div class="flex items-center justify-between p-2 bg-primary-soft/50 dark:bg-primary-soft border border-primary dark:border-primary rounded-xl text-xs font-semibold">${k} ➜ ${v} ${!state.answered ? `<button type="button" class="text-danger hover:text-danger ml-2" data-action="assoc-remove" data-tag="${encodeURIComponent(rawTag)}" data-key="${encodeURIComponent(k)}">✕</button>` : ''}</div>`
        })
        .join('')

      const elementHtml = `
        <div class="bg-surface-soft/50 dark:bg-surface-soft/50 p-4 border border-line dark:border-line rounded-2xl my-4 max-w-2xl shadow-sm not-prose">
          <div class="flex items-center justify-between mb-1.5">
            <strong class="text-tiny uppercase tracking-wider text-ink-subtle font-bold">Associations : ${title}</strong>
            ${state.answered ? renderSm2Buttons(cardId, rawTag) : ''}
          </div>
          <div class="grid grid-cols-2 gap-4 mt-3">
            <div class="flex flex-col gap-1.5"><div class="text-tiny font-bold text-ink-subtle uppercase tracking-wider mb-1">Clés</div>${keysHtml}</div>
            <div class="flex flex-col gap-1.5"><div class="text-tiny font-bold text-ink-subtle uppercase tracking-wider mb-1">Valeurs</div>${valuesHtml}</div>
          </div>

          ${Object.keys(state.matches).length > 0 ? `<div class="mt-4 border-t border-line dark:border-line pt-3"><div class="text-tiny font-bold text-ink-subtle uppercase tracking-wider mb-2">Liaisons créées :</div><div class="flex flex-col gap-1.5">${matchesHtml}</div></div>` : ''}
          
          ${
            !state.answered
              ? `
            <button type="button" class="w-full mt-4 px-4 py-2 bg-primary hover:bg-primary-strong text-white font-bold rounded-xl text-xs active:scale-95 transition-all border border-transparent disabled:opacity-40" data-action="assoc-validate" data-tag="${encodeURIComponent(rawTag)}" ${Object.keys(state.matches).length !== keysList.length ? 'disabled' : ''}>
              Valider les liaisons
            </button>
          `
              : `
            <div class="mt-4 bg-surface-soft/40 dark:bg-surface-soft/40 p-3 rounded-xl text-xs flex flex-col gap-1.5">
              <div class="font-bold text-ink dark:text-ink-subtle">Associations attendues :</div>
              <div class="grid grid-cols-1 gap-1.5">
                ${pairs.map((p: any) => `<div class="text-xs font-semibold text-ink-muted"><span class="text-primary dark:text-primary font-bold">${p.key}</span> ➜ ${p.value}</div>`).join('')}
              </div>
            </div>
          `
          }
        </div>
      `
      const key = `REVISIONPLACEHOLDER${placeholders.length}`
      placeholders.push(elementHtml)
      return '\n\n' + key + '\n\n'
    }
  })

  // 6. Mark down parse
  let html = marked.parse(temp) as string

  placeholders.forEach((placeholderHtml, idx) => {
    html = html.replace(
      new RegExp(`LATEXBLOCKPLACEHOLDER${idx}(?!\\d)`, 'g'),
      () => placeholderHtml,
    )
    html = html.replace(
      new RegExp(`LATEXINLINEPLACEHOLDER${idx}(?!\\d)`, 'g'),
      () => placeholderHtml,
    )
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
  if (!diagram)
    return '<div class="text-xs text-ink-subtle italic my-2">Diagramme introuvable.</div>'

  try {
    const data = JSON.parse(diagram.code)
    if (data && data.type === 'visual') {
      const nodesList = data.nodes || []
      const connectionsList = data.connections || []
      const bgImg = data.backgroundImage || ''
      const masksList = data.masks || []

      const maxX =
        Math.max(
          ...nodesList.map((n: any) => n.x),
          ...masksList.map((m: any) => m.x + m.width),
          350,
        ) + 80
      const maxY =
        Math.max(
          ...nodesList.map((n: any) => n.y),
          ...masksList.map((m: any) => m.y + m.height),
          200,
        ) + 80

      let linesSvg = ''
      connectionsList.forEach((conn: any) => {
        const fromNode = nodesList.find((n: any) => n.id === conn.from)
        const toNode = nodesList.find((n: any) => n.id === conn.to)
        if (fromNode && toNode) {
          linesSvg += `<line x1="${fromNode.x}" y1="${fromNode.y}" x2="${toNode.x}" y2="${toNode.y}" stroke="rgb(var(--sh-primary))" stroke-width="2" marker-end="url(#arrow-preview)" />`
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
              <span class="absolute z-10 text-tiny font-extrabold text-white px-1 leading-tight select-none">${node.label}</span>
            </div>
          `
        } else {
          nodesHtml += `
            <div class="absolute -translate-x-1/2 -translate-y-1/2 flex items-center justify-center text-center px-1 text-tiny font-bold text-white shadow-sm border border-black/5" style="top: ${node.y}px; left: ${node.x}px; ${shapeStyle} background-color: ${colorHex};">
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
          const fillClass = isRevealed
            ? 'fill-transparent stroke-danger/20'
            : 'fill-ink opacity-100 cursor-pointer'
          const pointerEvents = isRevealed ? 'pointer-events-none' : 'pointer-events-auto'

          masksSvg += `
            <rect 
              x="${mask.x}" 
              y="${mask.y}" 
              width="${mask.width}" 
              height="${mask.height}" 
              class="${fillClass} stroke-danger stroke-2"
              style="${pointerEvents}"
              data-action="reveal" 
              data-tag="${encodeURIComponent(rawTag)}"
            />
          `

          if (isRevealed) {
            const card = noteFlashcards.value.find((c) => c.original_text === rawTag)
            const cardId = card ? card.id : null
            activeReviewHtml += `
              <div class="mt-2 p-2.5 border border-line dark:border-line rounded-xl bg-surface-soft/50 dark:bg-surface-soft flex flex-col items-center gap-2">
                <span class="text-tiny font-bold text-ink-muted">Zone : <span class="text-danger font-extrabold">${mask.label}</span></span>
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
              class="fill-danger/20 stroke-danger stroke-2"
              title="Zone cachée : ${mask.label}"
            />
            <text x="${mask.x + 4}" y="${mask.y + 12}" fill="rgb(var(--sh-danger))" font-size="8px" font-weight="bold" class="select-none pointer-events-none">${mask.label}</text>
          `
        }
      })

      return `
        <div class="relative w-full border border-line dark:border-line rounded-2xl bg-surface-soft/20 dark:bg-surface-soft/15 p-2 overflow-hidden my-4 no-print select-none" style="height: ${Math.min(500, maxY + 120)}px;">
          <div class="absolute inset-x-0 top-0 px-4 py-1 flex items-center justify-between text-tiny text-ink-subtle font-bold uppercase tracking-wider bg-surface-soft/80 dark:bg-surface-soft border-b border-line dark:border-line/60 z-10">
            <span>Schéma visuel : ${diagram.title}</span>
            ${isReview ? '<span class="text-danger animate-pulse font-extrabold">Mode Révision - Cliquez sur les zones grises</span>' : ''}
          </div>
          <div class="w-full h-full overflow-auto pt-6 pb-24">
            <div class="relative" style="width: ${maxX}px; height: ${maxY}px;">
              <svg class="absolute inset-0 w-full h-full">
                <defs>
                  <marker id="arrow-preview" viewBox="0 0 10 10" refX="20" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
                    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="rgb(var(--sh-primary))" />
                  </marker>
                </defs>
                ${bgImgHtml}
                ${linesSvg}
                ${masksSvg}
              </svg>
              ${nodesHtml}
            </div>
          </div>
          <div class="absolute inset-x-0 bottom-0 p-2 bg-surface/95 dark:bg-surface-soft/95 border-t border-line dark:border-line/80 z-20 flex flex-col gap-1.5 max-h-36 overflow-y-auto">
            ${activeReviewHtml || `<div class="text-tiny text-ink-subtle italic text-center py-1">${isReview ? "Aucun masque d'occlusion révélé." : "Légende : masques d'occlusion affichés."}</div>`}
          </div>
        </div>
      `
    } else {
      return `
        <div class="border border-line dark:border-line rounded-2xl bg-surface-soft/30 dark:bg-surface-soft/15 p-4 my-4">
          <div class="text-tiny text-ink-subtle font-bold uppercase tracking-wider mb-2">Schéma Mermaid : ${diagram.title}</div>
          <pre class="text-tiny text-ink-muted font-mono bg-surface-soft dark:bg-surface-soft p-3 rounded-lg overflow-x-auto select-all">${diagram.code}</pre>
        </div>
      `
    }
  } catch {
    return `
      <div class="border border-line dark:border-line rounded-2xl bg-surface-soft/30 dark:bg-surface-soft/15 p-4 my-4">
        <div class="text-tiny text-ink-subtle font-bold uppercase tracking-wider mb-2">Schéma Mermaid : ${diagram.title}</div>
        <pre class="text-tiny text-ink-muted font-mono bg-surface-soft dark:bg-surface-soft p-3 rounded-lg overflow-x-auto select-all">${diagram.code}</pre>
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
      savedSelectionContent.value = textarea.value // snapshot du contenu au moment de la sélection

      if (event instanceof MouseEvent) {
        const viewportWidth = window.innerWidth
        // Clamp the left position to keep the bar within bounds (safeguard for screen width)
        const leftBound = Math.max(160, Math.min(event.clientX, viewportWidth - 160))
        selectionMenuPos.value = {
          top: event.clientY - 12,
          left: leftBound,
        }
      } else {
        const rect = textarea.getBoundingClientRect()
        const viewportWidth = window.innerWidth
        const centerLeft = rect.left + rect.width / 2
        const leftBound = Math.max(160, Math.min(centerLeft, viewportWidth - 160))
        selectionMenuPos.value = {
          top: rect.top + 60,
          left: leftBound,
        }
      }

      showSelectionMenu.value = true
      return
    }
  }
  showSelectionMenu.value = false
}

async function applySelectionTransform(
  type:
    | 'trou'
    | 'gras'
    | 'italique'
    | 'code'
    | 'bloc_code'
    | 'def'
    | 'qcm'
    | 'ordre'
    | 'assoc'
    | 'vf'
    | 'math_bloc'
    | 'math_ligne'
    | 'diagramme',
) {
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
        { label: 'Définition', type: 'text', value: '', placeholder: 'Entrez la définition...' },
      ],
    })
    if (!result) return
    replaced = `[${selected}]{def:${String(result[0].value).trim() || 'Définition...'}}`
  } else if (type === 'qcm') {
    const result = await openModal({
      title: 'Créer un QCM',
      description: `La bonne réponse sera : « ${selected} »`,
      icon: HelpCircle,
      iconBg: 'bg-purple-500',
      confirmBg: 'bg-purple-600 hover:bg-purple-700 shadow-purple-600/20',
      confirmLabel: 'Créer le QCM',
      fields: [
        {
          label: 'Question',
          type: 'text',
          value: 'Question ?',
          placeholder: 'Entrez la question...',
        },
        { label: 'Option fausse 1', type: 'text', value: '', placeholder: 'Mauvaise réponse 1...' },
        { label: 'Option fausse 2', type: 'text', value: '', placeholder: 'Mauvaise réponse 2...' },
      ],
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
        {
          label: 'Titre de la séquence',
          type: 'text',
          value: 'Ordre',
          placeholder: 'Ex : Étapes de la photosynthèse',
        },
        {
          label: 'Étape suivante',
          type: 'text',
          value: '',
          placeholder: 'Entrez l’étape qui suit...',
        },
      ],
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
        {
          label: 'Titre du groupe',
          type: 'text',
          value: 'Relations',
          placeholder: 'Ex : Capitales',
        },
        {
          label: `Valeur associée à « ${selected} »`,
          type: 'text',
          value: '',
          placeholder: 'Ex : Paris',
        },
      ],
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
        { label: 'Justification', type: 'text', value: '', placeholder: 'Expliquez pourquoi...' },
      ],
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
        description:
          'Vous n’avez créé aucun diagramme. Allez dans le module Diagrammes pour en créer un.',
        icon: Image,
        iconBg: 'bg-sky-500',
        confirmLabel: 'Compris',
        fields: [],
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
          options: allUserDiagrams.value.map((d) => ({ value: d.id, label: d.title })),
        },
      ],
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
  } else if (action === 'qcm-select') {
    const optionSelected = decodeURIComponent(target.getAttribute('data-option') || '')
    state.selectedOption = optionSelected
    state.answered = true
  } else if (action === 'vf-select') {
    const val = target.getAttribute('data-value') || ''
    state.selectedAnswer = val
    state.answered = true
  } else if (action === 'order-move') {
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
  } else if (action === 'order-validate') {
    state.answered = true
  } else if (action === 'assoc-key-select') {
    const key = decodeURIComponent(target.getAttribute('data-key') || '')
    state.selectedKey = key
  } else if (action === 'assoc-value-select') {
    const val = decodeURIComponent(target.getAttribute('data-value') || '')
    if (state.selectedKey) {
      state.matches[state.selectedKey] = val
      state.selectedKey = null
    }
  } else if (action === 'assoc-remove') {
    const key = decodeURIComponent(target.getAttribute('data-key') || '')
    delete state.matches[key]
  } else if (action === 'assoc-validate') {
    state.answered = true
  } else if (action === 'sm2-vote') {
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
      target.innerText =
        score === 1 ? 'À revoir' : score === 2 ? 'Difficile' : score === 3 ? 'Correct' : 'Facile'
    }
  } else if (action === 'sm2-re-evaluate') {
    const cardId = Number(target.getAttribute('data-card-id'))
    openEvaluationModal(cardId, rawTag)
  }

  // Trigger evaluation modal if applicable
  const isActionRequiringEvaluation =
    action === 'reveal' || // Trou or diagram mask revealed
    action === 'qcm-select' ||
    action === 'vf-select' ||
    action === 'order-validate' ||
    action === 'assoc-validate'

  const card = noteFlashcards.value.find((c) => c.original_text === rawTag)
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

function getBinderName(bId: string | null): string {
  if (bId === null) return 'Général (Aucun)'
  const b = bindersStore.binders.find((x) => x.id === bId)
  return b ? b.name : 'Général (Aucun)'
}

// Linked Notes logic
const linkableNotes = computed(() => {
  return notesStore.notes.filter((n) => n.id !== noteId.value && !noteLinks.value.includes(n.id))
})

function addNoteLink() {
  if (selectedLinkTarget.value !== null) {
    noteLinks.value.push(selectedLinkTarget.value)
    selectedLinkTarget.value = null
    triggerAutoSave()
  }
}

function removeNoteLink(id: string) {
  noteLinks.value = noteLinks.value.filter((linkedId) => linkedId !== id)
  triggerAutoSave()
}

function getNoteTitle(id: string): string {
  const n = notesStore.notes.find((x) => x.id === id)
  return n ? n.title : 'Note inconnue'
}

function navigateToNote(id: string) {
  router.push(`/notes/${id}`)
}

// Saut de ligne souple (Maj+Entrée). Dans une cellule de tableau Markdown, une
// ligne = une ligne de tableau : un vrai « \n » casserait la ligne. On insère
// donc un <br> explicite (rendu en saut de ligne dans la cellule) ; ailleurs un
// saut de ligne souple suffit (marked est configuré avec breaks: true).
function insertSoftBreak() {
  const textarea = textareaRef.value
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const text = textarea.value

  const lineStart = text.lastIndexOf('\n', start - 1) + 1
  const nextNewline = text.indexOf('\n', start)
  const currentLine = text.substring(lineStart, nextNewline === -1 ? text.length : nextNewline)
  const inTableRow = /^\s*\|/.test(currentLine)

  const insertion = inTableRow ? '<br>' : '\n'
  noteBody.value = text.substring(0, start) + insertion + text.substring(end)

  setTimeout(() => {
    textarea.focus()
    const pos = start + insertion.length
    textarea.setSelectionRange(pos, pos)
    triggerAutoSave()
  }, 0)
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
      description:
        'Veuillez sélectionner un mot ou un terme dans le texte pour lui associer une définition.',
      icon: BookOpen,
      iconBg: 'bg-emerald-500',
      confirmLabel: 'Compris',
      fields: [],
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
      {
        label: 'Définition',
        type: 'text',
        value: '',
        placeholder: `Définissez « ${selected} »...`,
      },
    ],
  })
  if (!result || !String(result[0].value).trim()) return

  const replacement = `[${selected}]{def:${String(result[0].value).trim()}}`
  noteBody.value = text.substring(0, start) + replacement + text.substring(end)

  setTimeout(() => {
    textarea.focus()
    const newCursorPos = start + replacement.length
    textarea.setSelectionRange(newCursorPos, newCursorPos)
    triggerAutoSave()
  }, 50)
}

async function copyForEditing() {
  if (isCopying.value) return
  isCopying.value = true
  try {
    const newNote = await notesStore.copyNote(noteId.value)
    // Ouvre la copie perso en mode édition.
    router.push(`/notes/${newNote.id}?edit=true`)
  } catch (e) {
    console.error('Erreur lors de la copie de la note', e)
  } finally {
    isCopying.value = false
  }
}

async function hideFromView() {
  try {
    await notesStore.hideNote(noteId.value)
    router.push('/notes')
  } catch (e) {
    console.error('Erreur lors du masquage de la note', e)
  }
}

function triggerAutoSave() {
  if (isReadOnly.value) return // note partagée en lecture seule : pas de sauvegarde
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
    const updated = await notesStore.updateNote(
      noteId.value,
      title.value,
      rawContent,
      binderId.value,
    )
    if (updated) {
      noteFlashcards.value = (updated as any).flashcards || []
    }
    const index = notesStore.notes.findIndex((n) => n.id === noteId.value)
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
  showPdfModal.value = true
}

function handlePdfExport(options: PdfExportOptions) {
  pdfExportOptions.value = options
  showPdfModal.value = false

  const themeClass = `pdf-theme-${options.theme}`
  const sizeClass = `pdf-size-${options.fontSize}`
  document.body.classList.add(themeClass, sizeClass)

  setTimeout(() => {
    window.print()
    document.body.classList.remove(
      'pdf-theme-modern',
      'pdf-theme-academic',
      'pdf-theme-minimal',
      'pdf-size-compact',
      'pdf-size-standard',
      'pdf-size-comfortable',
    )
  }, 150)
}

async function saveNoteTags(tags: Tag[]) {
  if (!noteId.value) return
  noteTags.value = await tagsStore.setTagsForEntity(
    'notes',
    noteId.value,
    tags.map((tag) => tag.id),
  )
  const note = notesStore.notes.find((item) => item.id === noteId.value)
  if (note) note.tags = noteTags.value
}
</script>

<style>
/* High-Definition Print & PDF Export Styling */
@media print {
  @page {
    size: A4 portrait;
    margin: 0;
  }

  /* Universal exact print color rendering */
  *,
  *:before,
  *:after {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    color-adjust: exact !important;
  }

  /* Force visibility of print-specific containers */
  .print-header-banner,
  .print-toc-block,
  .print-glossary-block,
  .print-footer-banner {
    display: block !important;
  }

  .print-footer-banner {
    display: flex !important;
  }

  /* Hide interactive, navigation, and modal components */
  aside,
  header,
  nav,
  button,
  select,
  input,
  .no-print,
  [no-print],
  .teleport-modal {
    display: none !important;
  }

  /* Page layout resets */
  body {
    padding: 12mm 15mm 15mm 15mm !important;
    margin: 0 !important;
    background: white !important;
    color: #0f172a !important;
  }

  .min-h-screen,
  main,
  .max-w-6xl,
  .max-w-4xl {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
    background: white !important;
    box-shadow: none !important;
  }

  /* Theme styling variations */
  body.pdf-theme-modern {
    font-family:
      system-ui,
      -apple-system,
      BlinkMacSystemFont,
      'Segoe UI',
      Roboto,
      sans-serif !important;
    color: #0f172a !important;
  }

  body.pdf-theme-academic {
    font-family: Georgia, Cambria, 'Times New Roman', Times, serif !important;
    color: #111827 !important;
  }

  body.pdf-theme-minimal {
    font-family: system-ui, sans-serif !important;
    color: #000000 !important;
  }

  /* Font sizes */
  body.pdf-size-compact .markdown-body {
    font-size: 11px !important;
    line-height: 1.5 !important;
  }
  body.pdf-size-standard .markdown-body {
    font-size: 13px !important;
    line-height: 1.6 !important;
  }
  body.pdf-size-comfortable .markdown-body {
    font-size: 15px !important;
    line-height: 1.75 !important;
  }

  /* Prevent orphaned headings */
  .markdown-body h1,
  .markdown-body h2,
  .markdown-body h3,
  .markdown-body h4,
  .markdown-body h5,
  .markdown-body h6 {
    break-after: avoid !important;
    page-break-after: avoid !important;
    color: #0f172a !important;
    font-weight: 800 !important;
  }

  .markdown-body h1 {
    font-size: 1.65em !important;
    margin-top: 1.2em !important;
    margin-bottom: 0.5em !important;
    border-bottom: 2px solid #cbd5e1 !important;
    padding-bottom: 0.3em !important;
  }

  .markdown-body h2 {
    font-size: 1.3em !important;
    margin-top: 1em !important;
    margin-bottom: 0.4em !important;
    border-bottom: 1px solid #e2e8f0 !important;
    padding-bottom: 0.2em !important;
  }

  .markdown-body h3 {
    font-size: 1.1em !important;
    margin-top: 0.8em !important;
    margin-bottom: 0.3em !important;
  }

  /* Page break avoidance for compound blocks */
  pre,
  code,
  table,
  blockquote,
  .katex-display,
  .not-prose,
  .print-toc-block,
  .print-glossary-block,
  .print-header-banner,
  img {
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }

  /* Markdown body code blocks */
  .markdown-body pre {
    background-color: #f8fafc !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
    font-family: 'JetBrains Mono', Consolas, monospace !important;
    white-space: pre-wrap !important;
    word-break: break-word !important;
  }

  .markdown-body code {
    background-color: #f1f5f9 !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-size: 0.9em !important;
  }

  /* Table styling */
  .markdown-body table {
    width: 100% !important;
    border-collapse: collapse !important;
    margin: 1.2em 0 !important;
  }

  .markdown-body th {
    background-color: #f1f5f9 !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
    padding: 8px 12px !important;
    font-weight: 700 !important;
    text-align: left !important;
  }

  .markdown-body td {
    border: 1px solid #e2e8f0 !important;
    padding: 6px 12px !important;
  }

  .markdown-body tr:nth-child(even) td {
    background-color: #f8fafc !important;
  }

  /* Blockquote styling */
  .markdown-body blockquote {
    border-left: 4px solid #6366f1 !important;
    background-color: #f8fafc !important;
    padding: 10px 16px !important;
    margin: 1em 0 !important;
    border-radius: 0 8px 8px 0 !important;
  }

  /* KaTeX formula display */
  .katex-display {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
  }
}

.popup-enter-active,
.popup-leave-active {
  transition:
    opacity 0.15s ease,
    transform 0.15s ease;
}
.popup-enter-from,
.popup-leave-to {
  opacity: 0;
  transform: translateY(-6px) scale(0.97);
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
