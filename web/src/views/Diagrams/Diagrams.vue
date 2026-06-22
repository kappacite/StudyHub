<template>
  <PageContainer size="wide">
    <PageHeader
      title="Créateur de Diagrammes & Cartes Mentales"
      subtitle="Concevez des schémas visuels en plaçant des formes, en créant des liaisons et en les organisant à la main."
    >
      <!-- Bascule Créateur Visuel vs Code Mermaid -->
      <template v-if="selectedDiagram" #actions>
        <div class="flex items-center gap-1 bg-surface-soft p-1 rounded-full border border-line">
          <button
            @click="activeTab = 'visual'"
            class="px-4 py-1.5 text-xs font-bold rounded-full transition-colors"
            :class="activeTab === 'visual' ? 'bg-primary text-white shadow-elev-primary' : 'text-ink-muted hover:text-ink'"
          >Créateur Visuel</button>
          <button
            @click="activeTab = 'mermaid'"
            class="px-4 py-1.5 text-xs font-bold rounded-full transition-colors"
            :class="activeTab === 'mermaid' ? 'bg-primary text-white shadow-elev-primary' : 'text-ink-muted hover:text-ink'"
          >Mode Code Mermaid</button>
        </div>
      </template>
    </PageHeader>

    <div class="flex flex-wrap items-center gap-2 rounded-2xl border border-line bg-surface p-3">
      <span class="text-xs font-bold uppercase tracking-wider text-ink-subtle">Filtrer</span>
      <button type="button" class="rounded-full px-3 py-1.5 text-xs font-bold transition-colors" :class="selectedTagId === null ? 'bg-primary text-white' : 'bg-surface-soft text-ink-muted'" @click="filterByTag(null)">Tous</button>
      <button
        v-for="tag in tagsStore.tags"
        :key="tag.id"
        type="button"
        class="rounded-full px-3 py-1.5 text-xs font-bold transition-colors"
        :style="selectedTagId === tag.id ? { backgroundColor: tag.color || '#F06292', color: '#fff' } : undefined"
        :class="selectedTagId === tag.id ? '' : 'bg-surface-soft text-ink-muted'"
        @click="filterByTag(tag.id)"
      >
        {{ tag.name }}
      </button>
    </div>

    <!-- Layout principal en grille -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <!-- 1. PANNEAU GAUCHE : LISTE DES DIAGRAMMES (3 colonnes) -->
      <div class="lg:col-span-3 bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-5 shadow-sm space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="font-extrabold text-sm text-ink dark:text-white uppercase tracking-wider">Mes Diagrammes</h3>
          <button 
            @click="createNewDiagram"
            class="p-1.5 bg-primary-soft hover:bg-primary-soft dark:bg-primary-soft dark:hover:bg-primary-soft text-primary dark:text-primary rounded-xl transition-all active:scale-90"
            title="Créer un nouveau diagramme"
          >
            <Plus class="w-4 h-4" />
          </button>
        </div>

        <!-- Chargement -->
        <div v-if="loadingList" class="flex justify-center py-8">
          <svg class="animate-spin h-5 w-5 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>

        <!-- Liste des schémas -->
        <div v-else class="space-y-2 max-h-[450px] overflow-y-auto pr-1">
          <div 
            v-for="diag in diagrams" 
            :key="diag.id"
            @click="selectDiagram(diag)"
            class="p-3.5 border rounded-2xl cursor-pointer transition-all flex items-center justify-between group"
            :class="[
              selectedDiagram?.id === diag.id 
                ? 'border-primary bg-primary-soft dark:bg-primary-soft text-primary dark:text-primary font-bold' 
                : 'border-line hover:border-line dark:border-line dark:hover:border-line text-ink dark:text-ink-subtle'
            ]"
          >
            <div class="flex items-center gap-2.5 min-w-0">
              <Activity class="w-4 h-4 flex-shrink-0 text-ink-subtle" :class="{ 'text-primary': selectedDiagram?.id === diag.id }" />
              <span class="text-xs truncate font-semibold">{{ diag.title || 'Diagramme sans titre' }}</span>
            </div>

            <!-- Bouton de suppression -->
            <button 
              @click.stop="deleteDiagram(diag)"
              class="opacity-0 group-hover:opacity-100 p-1 text-ink-subtle hover:text-danger rounded-lg hover:bg-danger-soft dark:hover:bg-danger-soft transition-all"
              title="Supprimer le diagramme"
            >
              <Trash2 class="w-3.5 h-3.5" />
            </button>
          </div>

          <div v-if="diagrams.length === 0" class="text-center py-8 text-xs text-ink-subtle italic">
            Aucun diagramme enregistré. Cliquez sur le bouton + pour commencer !
          </div>
        </div>
      </div>

      <!-- 2. PANNEAU CENTRAL/DROIT : L'ÉDITEUR ACTIF (9 colonnes) -->
      <div class="lg:col-span-9 space-y-6">
        <!-- Message si aucun diagramme sélectionné -->
        <div 
          v-if="!selectedDiagram" 
          class="border-2 border-dashed border-line dark:border-line rounded-3xl p-16 flex flex-col items-center justify-center text-center text-ink-subtle bg-surface dark:bg-surface-soft"
        >
          <Activity class="w-12 h-12 text-ink-subtle dark:text-ink mb-3" />
          <h4 class="font-bold text-ink dark:text-ink-subtle">Aucun diagramme en cours d'édition</h4>
          <p class="text-xs mt-1">Sélectionnez un diagramme dans la liste latérale ou créez-en un nouveau.</p>
          <button 
            @click="createNewDiagram"
            class="mt-4 px-4 py-2 text-xs font-bold text-white bg-primary hover:bg-primary-strong rounded-xl transition-all"
          >
            Nouveau diagramme
          </button>
        </div>

        <!-- Éditeur actif -->
        <div v-else class="space-y-4">
          <!-- Barre d'outils du diagramme en cours d'édition -->
          <div class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-4 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
            <div class="flex items-center gap-3 w-full sm:w-auto">
              <span class="text-xs font-bold text-ink-muted uppercase tracking-wider">Titre :</span>
              <input 
                type="text" 
                v-model="selectedDiagram.title"
                class="flex-1 sm:w-64 px-3 py-1.5 text-xs bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-xl focus:outline-none focus:ring-2 focus:ring-primary font-bold"
                placeholder="Nom du diagramme..."
              />
            </div>
            <div class="w-full sm:w-80">
              <TagSelector v-model="selectedDiagram.tags" @change="saveDiagramTags" />
            </div>

            <!-- Intégration de l'ID du diagramme pour insertion dans les notes -->
            <div class="flex items-center gap-3 w-full sm:w-auto justify-end">
              <span 
                class="text-[10px] bg-surface-soft dark:bg-surface-soft px-2.5 py-1 rounded-lg text-ink-muted font-mono font-bold select-all cursor-help"
                title="Copiez cette balise et collez-la dans n'importe quelle note de cours pour y afficher ce diagramme."
              >
                Code note : [diagram:{{ selectedDiagram.id }}]
              </span>

              <button 
                @click="saveDiagram"
                :disabled="saving"
                class="inline-flex items-center gap-1.5 px-4 py-2 bg-success hover:bg-success text-white rounded-xl text-xs font-bold shadow-md shadow-soft-lg disabled:opacity-50 active:scale-95 transition-all"
              >
                <Save class="w-3.5 h-3.5" />
                {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
              </button>
            </div>
          </div>

          <!-- TAB 1: CRÉATEUR VISUEL INTERACTIF -->
          <div v-if="activeTab === 'visual'" class="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
            <!-- Palette de formes (3 cols) -->
            <div class="md:col-span-3 bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-5 shadow-sm space-y-4">
              <div>
                <h4 class="font-bold text-xs text-ink dark:text-white uppercase tracking-wider">Ajouter des formes</h4>
                <p class="text-[9px] text-ink-subtle mt-0.5">Glissez ou cliquez pour insérer sur le plan</p>
              </div>

              <div class="grid grid-cols-1 gap-2">
                <button 
                  @click="addNode('rect')"
                  class="flex items-center gap-3 p-2.5 bg-surface-soft hover:bg-primary-soft dark:bg-surface-soft dark:hover:bg-primary-soft border border-line dark:border-line rounded-xl text-left transition-colors"
                >
                  <div class="h-8 w-12 rounded-lg border-2 border-primary bg-primary shadow-sm"></div>
                  <span class="text-[11px] font-bold">Concept (Rectangle)</span>
                </button>

                <button 
                  @click="addNode('circle')"
                  class="flex items-center gap-3 p-2.5 bg-surface-soft hover:bg-primary-soft dark:bg-surface-soft dark:hover:bg-primary-soft border border-line dark:border-line rounded-xl text-left transition-colors"
                >
                  <div class="h-10 w-10 rounded-full border-2 border-success bg-success shadow-sm"></div>
                  <span class="text-[11px] font-bold">Événement (Cercle)</span>
                </button>

                <button 
                  @click="addNode('diamond')"
                  class="flex items-center gap-3 p-2.5 bg-surface-soft hover:bg-primary-soft dark:bg-surface-soft dark:hover:bg-primary-soft border border-line dark:border-line rounded-xl text-left transition-colors"
                >
                  <div class="mx-2 h-8 w-8 rotate-45 border-2 border-warning bg-warning shadow-sm"></div>
                  <span class="text-[11px] font-bold">Décision (Losange)</span>
                </button>

                <button
                  @click="addNode('ellipse')"
                  class="flex items-center gap-3 p-2.5 bg-surface-soft hover:bg-primary-soft dark:bg-surface-soft dark:hover:bg-primary-soft border border-line dark:border-line rounded-xl text-left transition-colors"
                >
                  <div class="h-7 w-12 rounded-[50%] border-2 border-info bg-info shadow-sm"></div>
                  <span class="text-[11px] font-bold">Domaine (Ellipse)</span>
                </button>

                <button
                  @click="addNode('text')"
                  class="flex items-center gap-3 p-2.5 bg-surface-soft hover:bg-primary-soft dark:bg-surface-soft dark:hover:bg-primary-soft border border-line dark:border-line rounded-xl text-left transition-colors"
                >
                  <div class="flex h-8 w-12 items-center justify-center text-base font-black text-ink">T</div>
                  <span class="text-[11px] font-bold">Texte libre</span>
                </button>

                <button
                  @click="addNode('sticky')"
                  class="flex items-center gap-3 p-2.5 bg-surface-soft hover:bg-primary-soft dark:bg-surface-soft dark:hover:bg-primary-soft border border-line dark:border-line rounded-xl text-left transition-colors"
                >
                  <div class="h-9 w-9 -rotate-3 rounded-sm bg-amber-200 shadow-sm"></div>
                  <span class="text-[11px] font-bold">Post-it (Note)</span>
                </button>
              </div>

              <button
                @click="snapToGrid = !snapToGrid"
                class="w-full flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-bold border rounded-xl transition-all"
                :class="snapToGrid ? 'bg-primary-soft text-primary border-primary' : 'border-line dark:border-line hover:bg-surface-soft dark:hover:bg-surface-soft text-ink dark:text-ink-subtle'"
              >
                <Grid3x3 class="w-3.5 h-3.5" />
                {{ snapToGrid ? 'Aligner sur la grille : actif' : 'Aligner sur la grille' }}
              </button>

              <!-- Contrôles d'occlusion et d'image d'arrière-plan -->
              <div class="h-[1px] bg-surface-soft dark:bg-surface-soft"></div>

              <div class="space-y-4">
                <div>
                  <h4 class="font-bold text-xs text-ink dark:text-white uppercase tracking-wider">Image d'arrière-plan</h4>
                  <p class="text-[9px] text-ink-subtle mt-0.5">Importez une image pour l'occulter</p>
                </div>
                
                <input 
                  type="file" 
                  ref="fileInput" 
                  class="hidden" 
                  accept="image/*" 
                  @change="onBackgroundImageUploaded" 
                />
                
                <div class="flex gap-2">
                  <button 
                    @click="fileInput?.click()" 
                    class="flex-1 px-3 py-2 text-xs font-bold border border-line dark:border-line rounded-xl hover:bg-surface-soft dark:hover:bg-surface-soft transition-colors text-ink dark:text-ink-subtle"
                  >
                    {{ backgroundImage ? 'Changer l\'image' : 'Importer image' }}
                  </button>
                  <button 
                    v-if="backgroundImage"
                    @click="backgroundImage = null" 
                    class="p-2 text-danger border border-danger dark:border-danger rounded-xl hover:bg-danger-soft dark:hover:bg-danger-soft transition-colors"
                    title="Supprimer l'image"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                </div>

                <div class="space-y-2 pt-1">
                  <button 
                    @click="drawingMode = drawingMode === 'mask' ? 'select' : 'mask'"
                    class="w-full flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-bold border rounded-xl transition-all"
                    :class="[
                      drawingMode === 'mask' 
                        ? 'bg-danger border-danger text-white shadow-sm hover:bg-danger-strong' 
                        : 'border-line dark:border-line hover:bg-surface-soft dark:hover:bg-surface-soft text-ink dark:text-ink-subtle'
                    ]"
                  >
                    <Sparkles class="w-3.5 h-3.5" />
                    {{ drawingMode === 'mask' ? 'Mode Masque : Actif' : 'Dessiner un masque rect' }}
                  </button>

                  <button
                    @click="togglePenMode"
                    class="w-full flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-bold border rounded-xl transition-all"
                    :class="[
                      drawingMode === 'pen'
                        ? 'bg-primary border-primary text-white shadow-sm hover:bg-primary-strong'
                        : 'border-line dark:border-line hover:bg-surface-soft dark:hover:bg-surface-soft text-ink dark:text-ink-subtle'
                    ]"
                  >
                    <Pencil class="w-3.5 h-3.5" />
                    {{ drawingMode === 'pen' ? 'Crayon : actif' : 'Crayon (main levée)' }}
                  </button>

                  <div v-if="drawingMode === 'pen'" class="flex items-center justify-center gap-2 pt-1">
                    <button
                      v-for="pc in penColors"
                      :key="pc.hex"
                      @click="penColor = pc.hex"
                      class="h-7 w-7 rounded-full border-2 shadow-sm transition-transform hover:scale-105"
                      :class="penColor === pc.hex ? 'ring-2 ring-primary scale-110 border-white' : 'border-white dark:border-line'"
                      :style="{ backgroundColor: pc.hex }"
                      :title="pc.name"
                    ></button>
                  </div>
                </div>
              </div>

              <div class="h-[1px] bg-surface-soft dark:bg-surface-soft"></div>

              <!-- Sélection multiple : alignement de groupe -->
              <div v-if="selectedNodeIds.length > 1" class="space-y-4">
                <h4 class="text-[10px] font-bold uppercase tracking-wider text-primary">{{ selectedNodeIds.length }} éléments sélectionnés</h4>

                <div>
                  <label class="block text-[9px] font-bold text-ink-subtle mb-1 uppercase">Aligner horizontalement</label>
                  <div class="grid grid-cols-3 gap-1">
                    <button @click="alignSelectedNodes('left')" title="Aligner à gauche" class="px-2 py-1.5 text-[10px] font-bold border border-line rounded-lg hover:bg-surface-soft dark:hover:bg-surface-soft text-ink dark:text-ink-subtle transition-colors">Gauche</button>
                    <button @click="alignSelectedNodes('centerH')" title="Centrer horizontalement" class="px-2 py-1.5 text-[10px] font-bold border border-line rounded-lg hover:bg-surface-soft dark:hover:bg-surface-soft text-ink dark:text-ink-subtle transition-colors">Centre</button>
                    <button @click="alignSelectedNodes('right')" title="Aligner à droite" class="px-2 py-1.5 text-[10px] font-bold border border-line rounded-lg hover:bg-surface-soft dark:hover:bg-surface-soft text-ink dark:text-ink-subtle transition-colors">Droite</button>
                  </div>
                </div>

                <div>
                  <label class="block text-[9px] font-bold text-ink-subtle mb-1 uppercase">Aligner verticalement</label>
                  <div class="grid grid-cols-3 gap-1">
                    <button @click="alignSelectedNodes('top')" title="Aligner en haut" class="px-2 py-1.5 text-[10px] font-bold border border-line rounded-lg hover:bg-surface-soft dark:hover:bg-surface-soft text-ink dark:text-ink-subtle transition-colors">Haut</button>
                    <button @click="alignSelectedNodes('middleV')" title="Centrer verticalement" class="px-2 py-1.5 text-[10px] font-bold border border-line rounded-lg hover:bg-surface-soft dark:hover:bg-surface-soft text-ink dark:text-ink-subtle transition-colors">Milieu</button>
                    <button @click="alignSelectedNodes('bottom')" title="Aligner en bas" class="px-2 py-1.5 text-[10px] font-bold border border-line rounded-lg hover:bg-surface-soft dark:hover:bg-surface-soft text-ink dark:text-ink-subtle transition-colors">Bas</button>
                  </div>
                </div>

                <div class="pt-2">
                  <button
                    @click="deleteSelectedNode"
                    class="w-full flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-bold text-danger border border-danger hover:bg-danger-soft dark:border-danger dark:hover:bg-danger-soft rounded-xl transition-colors"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                    Supprimer la sélection
                  </button>
                </div>
              </div>

              <!-- Options du nœud sélectionné -->
              <div v-else-if="selectedNode" class="space-y-4">
                <h4 class="text-[10px] font-bold text-ink-subtle uppercase tracking-wider">Élément sélectionné</h4>
                
                <div>
                  <label class="block text-[9px] font-bold text-ink-subtle mb-1 uppercase">Texte</label>
                  <input 
                    type="text" 
                    v-model="selectedNode.label"
                    class="w-full px-2.5 py-1.5 text-xs bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-lg focus:outline-none focus:ring-1 focus:ring-primary font-semibold"
                  />
                </div>

                <div v-if="selectedNode.type !== 'text' && selectedNode.type !== 'sticky'">
                  <label class="block text-[9px] font-bold text-ink-subtle mb-1 uppercase">Couleur</label>
                  <div class="flex flex-wrap gap-2">
                    <button
                      v-for="color in colors"
                      :key="color.bg"
                      @click="selectedNode.color = color.bg"
                      class="h-8 w-8 rounded-full border-2 shadow-sm transition-transform hover:scale-105"
                      :class="[color.bg, selectedNode.color === color.bg ? 'border-line scale-110 ring-2 ring-primary dark:border-white dark:ring-primary' : 'border-white dark:border-line']"
                      :title="color.name"
                    ></button>
                  </div>
                </div>

                <div class="space-y-2 pt-2">
                  <button 
                    @click="startLinking"
                    class="w-full flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-bold border border-line dark:border-line rounded-xl hover:bg-surface-soft dark:hover:bg-surface-soft transition-colors"
                    :class="[linkingSourceId === selectedNode.id ? 'bg-primary-soft text-primary border-primary' : '']"
                  >
                    <LinkIcon class="w-3.5 h-3.5" />
                    {{ linkingSourceId === selectedNode.id ? 'Cible : cliquez sur une forme' : 'Relier à...' }}
                  </button>
                  
                  <button 
                    @click="deleteSelectedNode"
                    class="w-full flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-bold text-danger border border-danger hover:bg-danger-soft dark:border-danger dark:hover:bg-danger-soft rounded-xl transition-colors"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                    Supprimer la forme
                  </button>
                </div>
              </div>

              <!-- Options du masque sélectionné -->
              <div v-else-if="selectedMask" class="space-y-4">
                <h4 class="text-[10px] font-bold text-ink-subtle uppercase tracking-wider text-danger">Masque sélectionné</h4>
                
                <div>
                  <label class="block text-[9px] font-bold text-ink-subtle mb-1 uppercase">Texte masqué</label>
                  <input 
                    type="text" 
                    v-model="selectedMask.label"
                    class="w-full px-2.5 py-1.5 text-xs bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-lg focus:outline-none focus:ring-1 focus:ring-danger font-semibold"
                    placeholder="ex: Le Noyau"
                  />
                </div>

                <div class="pt-2">
                  <button 
                    @click="deleteSelectedMask"
                    class="w-full flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-bold text-danger border border-danger hover:bg-danger-soft dark:border-danger dark:hover:bg-danger-soft rounded-xl transition-colors"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                    Supprimer le masque
                  </button>
                </div>
              </div>

              <!-- Options du lien sélectionné -->
              <div v-else-if="selectedConnection" class="space-y-4">
                <h4 class="text-[10px] font-bold uppercase tracking-wider text-primary">Lien sélectionné</h4>

                <p class="text-[11px] text-ink-muted leading-snug">
                  <span class="font-bold text-ink">{{ getNode(selectedConnection.from)?.label || '?' }}</span>
                  →
                  <span class="font-bold text-ink">{{ getNode(selectedConnection.to)?.label || '?' }}</span>
                </p>

                <div>
                  <label class="block text-[9px] font-bold text-ink-subtle mb-1 uppercase">Libellé</label>
                  <input
                    type="text"
                    :value="selectedConnection.label || ''"
                    @input="selectedConnection.label = ($event.target as HTMLInputElement).value"
                    class="w-full px-2.5 py-1.5 text-xs bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-lg focus:outline-none focus:ring-1 focus:ring-primary font-semibold"
                    placeholder="ex: entraîne"
                  />
                </div>

                <div>
                  <label class="block text-[9px] font-bold text-ink-subtle mb-1 uppercase">Flèche</label>
                  <div class="flex items-center gap-1 bg-surface-soft p-1 rounded-xl border border-line">
                    <button
                      v-for="opt in arrowOptions"
                      :key="opt.value"
                      @click="selectedConnection.arrow = opt.value"
                      class="flex-1 px-2 py-1 text-[10px] font-bold rounded-lg transition-colors"
                      :class="connArrow(selectedConnection) === opt.value ? 'bg-primary text-white' : 'text-ink-muted hover:text-ink'"
                    >{{ opt.label }}</button>
                  </div>
                </div>

                <button
                  @click="selectedConnection.dashed = !selectedConnection.dashed"
                  class="w-full flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-bold border rounded-xl transition-colors"
                  :class="selectedConnection.dashed ? 'bg-primary-soft text-primary border-primary' : 'border-line dark:border-line hover:bg-surface-soft dark:hover:bg-surface-soft text-ink dark:text-ink-subtle'"
                >
                  {{ selectedConnection.dashed ? 'Trait : pointillé' : 'Trait : plein' }}
                </button>

                <div class="pt-2">
                  <button
                    @click="deleteSelectedConnection"
                    class="w-full flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-bold text-danger border border-danger hover:bg-danger-soft dark:border-danger dark:hover:bg-danger-soft rounded-xl transition-colors"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                    Supprimer le lien
                  </button>
                </div>
              </div>

              <!-- Options du tracé sélectionné -->
              <div v-else-if="selectedDrawing" class="space-y-4">
                <h4 class="text-[10px] font-bold uppercase tracking-wider text-primary">Tracé sélectionné</h4>
                <p class="text-[11px] text-ink-muted leading-snug">Tracé au crayon ({{ selectedDrawing.points.length }} points).</p>
                <div class="pt-2">
                  <button
                    @click="deleteSelectedDrawing"
                    class="w-full flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-bold text-danger border border-danger hover:bg-danger-soft dark:border-danger dark:hover:bg-danger-soft rounded-xl transition-colors"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                    Supprimer le tracé
                  </button>
                </div>
              </div>

              <div v-else class="text-center py-4 text-ink-subtle text-xs italic">
                Double-cliquez une forme pour la renommer. Cliquez un lien pour le supprimer.
              </div>
            </div>

            <!-- Canevas d'édition (9 cols) -->
            <div class="md:col-span-9 bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-2 shadow-sm flex flex-col overflow-hidden">
              <div class="px-4 py-1.5 border-b border-line-soft dark:border-line flex items-center justify-between text-[9px] text-ink-muted font-bold uppercase tracking-wider select-none">
                <span>Plan interactif</span>
                <span v-if="drawingMode === 'mask'" class="text-danger font-extrabold animate-pulse">Mode Masque actif : Cliquez-glissez pour dessiner un masque</span>
                <span v-else-if="drawingMode === 'pen'" class="text-primary font-extrabold animate-pulse">Crayon actif : cliquez-glissez pour dessiner</span>
                <span v-else>Glisser : déplacer · Molette : naviguer · Ctrl+molette : zoom · Maj+clic / Maj+glisser : multi-sélection · Suppr : effacer</span>
              </div>

              <!-- Zone SVG interactive (pan + zoom) -->
              <div
                ref="canvasRef"
                data-testid="diagram-canvas"
                class="relative w-full h-[450px] bg-surface-soft dark:bg-surface-soft overflow-hidden select-none"
                :class="[drawingMode === 'mask' ? 'cursor-cell' : (drawingMode === 'pen' ? 'cursor-crosshair' : (isPanning && panMoved ? 'cursor-grabbing' : 'cursor-grab'))]"
                :style="gridStyle"
                @mousedown="onCanvasMouseDown"
                @mousemove="onCanvasMouseMove"
                @mouseup="onCanvasMouseUp"
                @mouseleave="onCanvasMouseUp"
                @wheel.prevent="onWheel"
              >
                <!-- Conteneur « monde » : translate(pan) + scale(zoom) -->
                <div class="absolute inset-0 origin-top-left" :style="worldStyle">
                <!-- SVG : image de fond, connexions et masques (coordonnées monde) -->
                <svg class="absolute inset-0 w-full h-full overflow-visible" style="cursor: inherit;">
                  <defs>
                    <marker
                      id="arrow" 
                      viewBox="0 0 10 10" 
                      refX="22" 
                      refY="5" 
                      markerWidth="6" 
                      markerHeight="6" 
                      orient="auto-start-reverse"
                    >
                      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#6366f1" />
                    </marker>
                  </defs>

                  <!-- Image de fond -->
                  <image 
                    v-if="backgroundImage" 
                    :href="backgroundImage" 
                    x="0" 
                    y="0" 
                    width="100%" 
                    height="100%" 
                    preserveAspectRatio="xMidYMid meet" 
                    class="pointer-events-none"
                  />
                  
                  <!-- Connexions -->
                  <g>
                    <g v-for="(conn, idx) in connections" :key="idx">
                      <template v-if="getNode(conn.from) && getNode(conn.to)">
                        <!-- Zone de clic élargie (invisible) -->
                        <line
                          :x1="getNode(conn.from)!.x"
                          :y1="getNode(conn.from)!.y"
                          :x2="getNode(conn.to)!.x"
                          :y2="getNode(conn.to)!.y"
                          stroke="transparent"
                          stroke-width="14"
                          class="cursor-pointer"
                          @click.stop="onConnectionClick(idx)"
                        />
                        <!-- Trait visible -->
                        <line
                          :x1="getNode(conn.from)!.x"
                          :y1="getNode(conn.from)!.y"
                          :x2="getNode(conn.to)!.x"
                          :y2="getNode(conn.to)!.y"
                          :stroke="selectedConnectionIndex === idx ? '#ec4899' : '#6366f1'"
                          :stroke-width="selectedConnectionIndex === idx ? 3.5 : 2"
                          :stroke-dasharray="conn.dashed ? '7 5' : undefined"
                          :marker-start="connArrow(conn) === 'both' ? 'url(#arrow)' : undefined"
                          :marker-end="connArrow(conn) !== 'none' ? 'url(#arrow)' : undefined"
                          class="pointer-events-none transition-all"
                        />
                        <!-- Libellé du lien -->
                        <text
                          v-if="conn.label"
                          :x="(getNode(conn.from)!.x + getNode(conn.to)!.x) / 2"
                          :y="(getNode(conn.from)!.y + getNode(conn.to)!.y) / 2 - 4"
                          text-anchor="middle"
                          class="pointer-events-none fill-ink stroke-surface text-[10px] font-bold"
                          style="paint-order: stroke; stroke-width: 3px;"
                        >{{ conn.label }}</text>
                      </template>
                    </g>
                  </g>
                  
                  <!-- Tracés au crayon (main levée) -->
                  <g v-for="stroke in drawings" :key="stroke.id">
                    <!-- Zone de clic élargie -->
                    <polyline
                      :points="strokePoints(stroke)"
                      fill="none"
                      stroke="transparent"
                      :stroke-width="(stroke.width || 3) + 12"
                      :class="drawingMode === 'select' ? 'cursor-pointer' : 'pointer-events-none'"
                      @click.stop="onDrawingClick(stroke.id)"
                    />
                    <!-- Tracé visible -->
                    <polyline
                      :points="strokePoints(stroke)"
                      fill="none"
                      :stroke="stroke.color"
                      :stroke-width="stroke.width || 3"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      :class="['pointer-events-none transition-all', selectedDrawingId === stroke.id ? 'opacity-100' : 'opacity-90']"
                      :style="selectedDrawingId === stroke.id ? 'filter: drop-shadow(0 0 2px rgb(var(--sh-primary)));' : ''"
                    />
                  </g>

                  <!-- Tracé en cours -->
                  <polyline
                    v-if="currentStroke"
                    :points="strokePoints(currentStroke)"
                    fill="none"
                    :stroke="currentStroke.color"
                    :stroke-width="currentStroke.width"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    class="pointer-events-none"
                  />

                  <!-- Masques d'occlusion -->
                  <rect
                    v-for="mask in masks"
                    :key="mask.id" 
                    :x="mask.x" 
                    :y="mask.y" 
                    :width="mask.width" 
                    :height="mask.height" 
                    class="stroke-rose-600 stroke-2 cursor-pointer transition-colors"
                    :class="[
                      selectedMaskId === mask.id 
                        ? 'fill-rose-500/50' 
                        : 'fill-rose-500/30 hover:fill-rose-500/45'
                    ]"
                    :style="selectedMaskId === mask.id ? 'stroke-dasharray: 4;' : ''"
                    @click.stop="onMaskClick(mask)"
                  />
                  
                  <!-- Rectangle de dessin temporaire -->
                  <rect
                    v-if="drawingMode === 'mask' && tempMask"
                    :x="tempMask.x"
                    :y="tempMask.y"
                    :width="tempMask.width"
                    :height="tempMask.height"
                    class="fill-rose-500/25 stroke-rose-600 stroke-2 pointer-events-none"
                  />

                  <!-- Rectangle de sélection (marquee) -->
                  <rect
                    v-if="marqueeRect"
                    :x="marqueeRect.x"
                    :y="marqueeRect.y"
                    :width="marqueeRect.width"
                    :height="marqueeRect.height"
                    class="fill-primary/10 stroke-primary stroke-1 pointer-events-none"
                    style="stroke-dasharray: 4;"
                  />
                </svg>

                <!-- Formes/Nœuds interactifs -->
                <div 
                  v-for="node in nodes" 
                  :key="node.id"
                  class="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-grab active:cursor-grabbing select-none"
                  :style="{ top: `${node.y}px`, left: `${node.x}px` }"
                  @mousedown.stop="onNodeMouseDown(node, $event)"
                  @click.stop="onNodeClick(node)"
                  @dblclick.stop="startEditingNode(node)"
                >
                  <!-- Rectangle -->
                  <div 
                    v-if="node.type === 'rect'"
                    class="w-28 h-10 rounded-xl border flex items-center justify-center text-center px-2 text-[10px] font-bold text-white shadow transition-all"
                    :class="[
                      node.color,
                      isNodeSelected(node.id) ? 'ring-2 ring-primary scale-105 ring-offset-2 dark:ring-offset-surface' : ''
                    ]"
                    :style="sizeStyle(node)"
                  >
                    <input
                      v-if="editingNodeId === node.id"
                      v-model="node.label"
                      class="w-full bg-transparent text-center text-[10px] font-bold text-white outline-none placeholder-white/60"
                      @mousedown.stop
                      @click.stop
                      @blur="stopEditingNode"
                      @keydown.enter.prevent="stopEditingNode"
                      @keydown.esc.prevent="stopEditingNode"
                      v-focus
                    />
                    <template v-else>{{ node.label }}</template>
                  </div>

                  <!-- Cercle -->
                  <div 
                    v-else-if="node.type === 'circle'"
                    class="w-14 h-14 rounded-full border flex items-center justify-center text-center p-2 text-[9px] font-extrabold text-white shadow transition-all"
                    :class="[
                      node.color,
                      isNodeSelected(node.id) ? 'ring-2 ring-primary scale-105 ring-offset-2 dark:ring-offset-surface' : ''
                    ]"
                  >
                    <input
                      v-if="editingNodeId === node.id"
                      v-model="node.label"
                      class="w-full bg-transparent text-center text-[9px] font-extrabold text-white outline-none placeholder-white/60"
                      @mousedown.stop
                      @click.stop
                      @blur="stopEditingNode"
                      @keydown.enter.prevent="stopEditingNode"
                      @keydown.esc.prevent="stopEditingNode"
                      v-focus
                    />
                    <template v-else>{{ node.label }}</template>
                  </div>

                  <!-- Losange -->
                  <div 
                    v-else-if="node.type === 'diamond'"
                    class="relative w-14 h-14 flex items-center justify-center text-center transition-all select-none"
                    :class="[isNodeSelected(node.id) ? 'scale-105' : '']"
                  >
                    <div 
                      class="absolute inset-0 rotate-45 border rounded-lg shadow transition-all"
                      :class="[node.color, isNodeSelected(node.id) ? 'ring-2 ring-primary ring-offset-2 dark:ring-offset-surface' : '']"
                    ></div>
                    <input
                      v-if="editingNodeId === node.id"
                      v-model="node.label"
                      class="relative z-10 w-12 bg-transparent text-center text-[8px] font-extrabold text-white outline-none placeholder-white/60"
                      @mousedown.stop
                      @click.stop
                      @blur="stopEditingNode"
                      @keydown.enter.prevent="stopEditingNode"
                      @keydown.esc.prevent="stopEditingNode"
                      v-focus
                    />
                    <span v-else class="relative z-10 text-[8px] font-extrabold text-white px-2 leading-tight">{{ node.label }}</span>
                  </div>

                  <!-- Ellipse -->
                  <div
                    v-else-if="node.type === 'ellipse'"
                    class="w-24 h-12 rounded-[50%] border flex items-center justify-center text-center px-3 text-[10px] font-bold text-white shadow transition-all"
                    :class="[
                      node.color,
                      isNodeSelected(node.id) ? 'ring-2 ring-primary scale-105 ring-offset-2 dark:ring-offset-surface' : ''
                    ]"
                    :style="sizeStyle(node)"
                  >
                    <input
                      v-if="editingNodeId === node.id"
                      v-model="node.label"
                      class="w-full bg-transparent text-center text-[10px] font-bold text-white outline-none placeholder-white/60"
                      @mousedown.stop
                      @click.stop
                      @blur="stopEditingNode"
                      @keydown.enter.prevent="stopEditingNode"
                      @keydown.esc.prevent="stopEditingNode"
                      v-focus
                    />
                    <template v-else>{{ node.label }}</template>
                  </div>

                  <!-- Texte libre -->
                  <div
                    v-else-if="node.type === 'text'"
                    class="px-2 py-1 rounded-lg text-center text-xs font-bold text-ink dark:text-white transition-all"
                    :class="[isNodeSelected(node.id) ? 'ring-2 ring-primary ring-offset-2 dark:ring-offset-surface' : '']"
                  >
                    <input
                      v-if="editingNodeId === node.id"
                      v-model="node.label"
                      class="w-32 bg-transparent text-center text-xs font-bold text-ink dark:text-white outline-none"
                      @mousedown.stop
                      @click.stop
                      @blur="stopEditingNode"
                      @keydown.enter.prevent="stopEditingNode"
                      @keydown.esc.prevent="stopEditingNode"
                      v-focus
                    />
                    <template v-else>{{ node.label }}</template>
                  </div>

                  <!-- Post-it -->
                  <div
                    v-else-if="node.type === 'sticky'"
                    class="w-24 h-24 -rotate-2 p-2 flex items-center justify-center text-center text-[10px] font-bold text-amber-950 bg-amber-200 shadow-md transition-all"
                    :class="[isNodeSelected(node.id) ? 'ring-2 ring-primary ring-offset-2 dark:ring-offset-surface' : '']"
                    :style="sizeStyle(node)"
                  >
                    <textarea
                      v-if="editingNodeId === node.id"
                      v-model="node.label"
                      class="w-full h-full bg-transparent text-center text-[10px] font-bold text-amber-950 outline-none resize-none"
                      @mousedown.stop
                      @click.stop
                      @blur="stopEditingNode"
                      @keydown.esc.prevent="stopEditingNode"
                      v-focus
                    />
                    <span v-else class="whitespace-pre-wrap leading-tight">{{ node.label }}</span>
                  </div>

                  <!-- Poignée de redimensionnement (coin bas-droit) -->
                  <div
                    v-if="selectedNodeIds.length === 1 && isNodeSelected(node.id) && isResizable(node)"
                    class="absolute -bottom-1.5 -right-1.5 h-3 w-3 rounded-sm bg-primary border border-white shadow cursor-nwse-resize"
                    @mousedown.stop="onResizeStart(node, $event)"
                    @click.stop
                  ></div>
                </div>
                </div>

                <!-- Barre annuler / rétablir flottante -->
                <div class="absolute top-2 left-2 flex items-center gap-1 rounded-xl border border-line bg-surface/90 dark:bg-surface-soft/90 backdrop-blur px-1 py-1 shadow-sm">
                  <button @click="undo" :disabled="!canUndo" title="Annuler (Ctrl+Z)" class="p-1.5 rounded-lg text-ink-muted hover:bg-surface-soft dark:hover:bg-surface transition-colors disabled:opacity-40 disabled:cursor-not-allowed"><Undo2 class="w-4 h-4" /></button>
                  <button @click="redo" :disabled="!canRedo" title="Rétablir (Ctrl+Maj+Z)" class="p-1.5 rounded-lg text-ink-muted hover:bg-surface-soft dark:hover:bg-surface transition-colors disabled:opacity-40 disabled:cursor-not-allowed"><Redo2 class="w-4 h-4" /></button>
                </div>

                <!-- Barre de zoom flottante -->
                <div class="absolute top-2 right-2 flex items-center gap-1 rounded-xl border border-line bg-surface/90 dark:bg-surface-soft/90 backdrop-blur px-1 py-1 shadow-sm">
                  <button @click="zoomBy(1 / 1.2)" title="Dézoomer" class="p-1.5 rounded-lg text-ink-muted hover:bg-surface-soft dark:hover:bg-surface transition-colors"><ZoomOut class="w-4 h-4" /></button>
                  <button @click="resetView" aria-label="Réinitialiser la vue" title="Réinitialiser la vue" class="px-2 py-1 text-[10px] font-bold text-ink-muted hover:bg-surface-soft dark:hover:bg-surface rounded-lg transition-colors tabular-nums">{{ Math.round(zoom * 100) }}%</button>
                  <button @click="zoomBy(1.2)" title="Zoomer" class="p-1.5 rounded-lg text-ink-muted hover:bg-surface-soft dark:hover:bg-surface transition-colors"><ZoomIn class="w-4 h-4" /></button>
                </div>
              </div>
            </div>
          </div>

          <!-- TAB 2: CODE MERMAID EDITOR -->
          <div v-else class="grid grid-cols-1 md:grid-cols-12 gap-6">
            <!-- Code Editor (4 cols) -->
            <div class="md:col-span-4 bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-5 shadow-sm flex flex-col space-y-3">
              <div>
                <h4 class="font-bold text-xs text-ink dark:text-white uppercase tracking-wider">Code Mermaid</h4>
                <p class="text-[9px] text-ink-subtle mt-0.5">Décrivez votre schéma textuellement</p>
              </div>
              <textarea 
                v-model="mermaidCode" 
                rows="15" 
                class="w-full p-4 font-mono text-xs bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-2xl focus:outline-none focus:ring-2 focus:ring-primary text-ink dark:text-ink-subtle resize-y"
              ></textarea>
            </div>

            <!-- Visual Preview Simulation (8 cols) -->
            <div class="md:col-span-8 bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-5 shadow-sm flex flex-col min-h-[400px]">
              <h3 class="font-bold text-xs text-ink dark:text-white uppercase tracking-wider border-b border-line-soft dark:border-line pb-3 mb-4">
                Aperçu du Rendu
              </h3>
              <div class="flex-1 flex items-center justify-center p-4 border border-dashed border-line dark:border-line rounded-2xl bg-surface-soft dark:bg-surface-soft overflow-auto">
                <div class="text-center space-y-2">
                  <Activity class="w-8 h-8 text-primary mx-auto animate-pulse" />
                  <p class="text-xs font-semibold text-ink-muted dark:text-ink-subtle">Rendu du schéma Mermaid</p>
                  <pre class="text-[10px] text-ink-subtle font-mono bg-surface-soft dark:bg-surface-soft px-3 py-1.5 rounded-lg select-all max-w-sm truncate">{{ mermaidCode }}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </PageContainer>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../services/api'
import { useTagsStore, type Tag } from '../../stores/tags'
import TagSelector from '../../components/ui/TagSelector.vue'
import { PageContainer, PageHeader } from '../../components/ui/base'
import {
  Plus,
  Trash2,
  Save,
  Link as LinkIcon,
  Activity,
  Sparkles,
  ZoomIn,
  ZoomOut,
  Grid3x3,
  Undo2,
  Redo2,
  Pencil
} from '@lucide/vue'

type NodeShape = 'rect' | 'circle' | 'diamond' | 'ellipse' | 'text' | 'sticky'
type ArrowStyle = 'end' | 'both' | 'none'

interface VisualNode {
  id: number
  label: string
  type: NodeShape
  x: number
  y: number
  color: string
  width?: number
  height?: number
}

interface Connection {
  from: number
  to: number
  label?: string
  arrow?: ArrowStyle
  dashed?: boolean
}

interface BackendDiagram {
  id: number
  title: string
  code: string
  binder_id: number | null
  created_at: string
  tags: Tag[]
}

const diagrams = ref<BackendDiagram[]>([])
const selectedDiagram = ref<BackendDiagram | null>(null)
const tagsStore = useTagsStore()
const selectedTagId = ref<number | null>(null)

const activeTab = ref('visual')
const selectedNodeId = ref<number | null>(null)
const selectedNodeIds = ref<number[]>([])
const linkingSourceId = ref<number | null>(null)
const editingNodeId = ref<number | null>(null)
const selectedConnectionIndex = ref<number | null>(null)

// Directive locale : focus automatique de l'input d'édition inline
const vFocus = {
  mounted: (el: HTMLInputElement) => el.focus()
}

// Chargement & Sauvegarde
const loadingList = ref(false)
const saving = ref(false)

// Drag and drop canevas
const isDragging = ref(false)
const draggedNodeId = ref<number | null>(null)
const dragOffset = ref({ x: 0, y: 0 })
const dragOffsets = ref<{ id: number; dx: number; dy: number }[]>([])

// Sélection par rectangle (marquee) — Maj + glisser sur le fond
const isMarqueeing = ref(false)
const marqueeRect = ref<{ startX: number; startY: number; x: number; y: number; width: number; height: number } | null>(null)

// Pan + zoom du canevas (état de vue, non persisté dans `code`)
const canvasRef = ref<HTMLElement | null>(null)
const zoom = ref(1)
const panX = ref(0)
const panY = ref(0)
const isPanning = ref(false)
const panMoved = ref(false)
const panPointerStart = ref({ x: 0, y: 0 })
const panOriginStart = ref({ x: 0, y: 0 })

// Redimensionnement des nœuds + alignement sur la grille
const GRID_SIZE = 20
const MIN_NODE_SIZE = 40
const RESIZABLE_TYPES: NodeShape[] = ['rect', 'ellipse', 'sticky']
const snapToGrid = ref(false)
const resizingNodeId = ref<number | null>(null)

function isResizable(node: VisualNode) {
  return RESIZABLE_TYPES.includes(node.type)
}

function sizeStyle(node: VisualNode) {
  if (node.width == null || node.height == null) return {}
  return { width: `${node.width}px`, height: `${node.height}px` }
}

function snapVal(v: number) {
  return snapToGrid.value ? Math.round(v / GRID_SIZE) * GRID_SIZE : v
}

function onResizeStart(node: VisualNode, _event: MouseEvent) {
  resizingNodeId.value = node.id
  selectSingleNode(node.id)
}

// ---- Sélection des nœuds (simple + multiple) ----
function isNodeSelected(id: number) {
  return selectedNodeIds.value.includes(id)
}

function selectSingleNode(id: number) {
  selectedNodeId.value = id
  selectedNodeIds.value = [id]
}

function clearNodeSelection() {
  selectedNodeId.value = null
  selectedNodeIds.value = []
}

function toggleNodeSelection(id: number) {
  const i = selectedNodeIds.value.indexOf(id)
  if (i >= 0) {
    selectedNodeIds.value.splice(i, 1)
    selectedNodeId.value = selectedNodeIds.value[selectedNodeIds.value.length - 1] ?? null
  } else {
    selectedNodeIds.value.push(id)
    selectedNodeId.value = id
  }
}

// Taille effective d'un nœud (px) : valeur explicite ou défaut par forme
const NODE_DEFAULT_SIZE: Record<NodeShape, { w: number; h: number }> = {
  rect: { w: 112, h: 40 },
  circle: { w: 56, h: 56 },
  diamond: { w: 56, h: 56 },
  ellipse: { w: 96, h: 48 },
  text: { w: 80, h: 28 },
  sticky: { w: 96, h: 96 }
}

function effectiveSize(node: VisualNode) {
  return {
    w: node.width ?? NODE_DEFAULT_SIZE[node.type].w,
    h: node.height ?? NODE_DEFAULT_SIZE[node.type].h
  }
}

// Alignement des bords/centres des nœuds sélectionnés (positionnés par leur centre)
function alignSelectedNodes(edge: 'left' | 'centerH' | 'right' | 'top' | 'middleV' | 'bottom') {
  const sel = nodes.value.filter(n => selectedNodeIds.value.includes(n.id))
  if (sel.length < 2) return
  const boxes = sel.map(n => {
    const { w, h } = effectiveSize(n)
    return { n, w, h, left: n.x - w / 2, right: n.x + w / 2, top: n.y - h / 2, bottom: n.y + h / 2 }
  })
  const minLeft = Math.min(...boxes.map(b => b.left))
  const maxRight = Math.max(...boxes.map(b => b.right))
  const minTop = Math.min(...boxes.map(b => b.top))
  const maxBottom = Math.max(...boxes.map(b => b.bottom))
  for (const b of boxes) {
    if (edge === 'left') b.n.x = minLeft + b.w / 2
    else if (edge === 'right') b.n.x = maxRight - b.w / 2
    else if (edge === 'centerH') b.n.x = (minLeft + maxRight) / 2
    else if (edge === 'top') b.n.y = minTop + b.h / 2
    else if (edge === 'bottom') b.n.y = maxBottom - b.h / 2
    else if (edge === 'middleV') b.n.y = (minTop + maxBottom) / 2
  }
}

const gridStyle = computed(() => {
  const size = 20 * zoom.value
  return {
    backgroundImage:
      'linear-gradient(to right, rgba(148,163,184,0.18) 1px, transparent 1px),' +
      'linear-gradient(to bottom, rgba(148,163,184,0.18) 1px, transparent 1px)',
    backgroundSize: `${size}px ${size}px`,
    backgroundPosition: `${panX.value}px ${panY.value}px`,
  }
})

const worldStyle = computed(() => ({
  transform: `translate(${panX.value}px, ${panY.value}px) scale(${zoom.value})`,
  transformOrigin: '0 0',
}))

// Convertit des coordonnées écran (clientX/Y) en coordonnées « monde » du canevas
function screenToWorld(clientX: number, clientY: number) {
  const rect = canvasRef.value?.getBoundingClientRect()
  const left = rect?.left ?? 0
  const top = rect?.top ?? 0
  return {
    x: (clientX - left - panX.value) / zoom.value,
    y: (clientY - top - panY.value) / zoom.value,
  }
}

function clampCoord(v: number) {
  return Math.max(-3000, Math.min(6000, v))
}

function zoomAtPoint(factor: number, clientX: number, clientY: number) {
  const rect = canvasRef.value?.getBoundingClientRect()
  const left = rect?.left ?? 0
  const top = rect?.top ?? 0
  const newZoom = Math.max(0.3, Math.min(3, zoom.value * factor))
  // Garder le point monde sous le curseur à la même position écran
  const wx = (clientX - left - panX.value) / zoom.value
  const wy = (clientY - top - panY.value) / zoom.value
  panX.value = (clientX - left) - wx * newZoom
  panY.value = (clientY - top) - wy * newZoom
  zoom.value = newZoom
}

function zoomBy(factor: number) {
  const rect = canvasRef.value?.getBoundingClientRect()
  if (!rect) {
    zoom.value = Math.max(0.3, Math.min(3, zoom.value * factor))
    return
  }
  zoomAtPoint(factor, rect.left + rect.width / 2, rect.top + rect.height / 2)
}

function resetView() {
  zoom.value = 1
  panX.value = 0
  panY.value = 0
}

function onWheel(event: WheelEvent) {
  if (event.ctrlKey || event.metaKey) {
    zoomAtPoint(event.deltaY < 0 ? 1.1 : 1 / 1.1, event.clientX, event.clientY)
  } else {
    panX.value -= event.deltaX
    panY.value -= event.deltaY
  }
}

// Modèles locaux d'édition
const nodes = ref<VisualNode[]>([])
const connections = ref<Connection[]>([])
const mermaidCode = ref('')

// Modèles locaux d'occlusion et image de fond
const drawingMode = ref<'select' | 'mask' | 'pen'>('select')
const isDrawingMask = ref(false)
const tempMask = ref<{ startX: number; startY: number; x: number; y: number; width: number; height: number } | null>(null)
const masks = ref<{ id: string; x: number; y: number; width: number; height: number; label: string }[]>([])
const selectedMaskId = ref<string | null>(null)
const backgroundImage = ref<string | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

// Crayon main levée (tracés)
interface PenStroke {
  id: string
  points: { x: number; y: number }[]
  color: string
  width: number
}
const drawings = ref<PenStroke[]>([])
const currentStroke = ref<PenStroke | null>(null)
const isDrawingPen = ref(false)
const selectedDrawingId = ref<string | null>(null)
const penColor = ref('#ef4444')
const penColors = [
  { name: 'Rouge', hex: '#ef4444' },
  { name: 'Bleu', hex: '#3b82f6' },
  { name: 'Vert', hex: '#22c55e' },
  { name: 'Encre', hex: '#1e293b' }
]

function strokePoints(stroke: PenStroke) {
  return stroke.points.map(p => `${p.x},${p.y}`).join(' ')
}

const selectedMask = computed(() => masks.value.find(m => m.id === selectedMaskId.value) || null)
const selectedConnection = computed(() =>
  selectedConnectionIndex.value === null ? null : connections.value[selectedConnectionIndex.value] || null
)
const selectedDrawing = computed(() => drawings.value.find(d => d.id === selectedDrawingId.value) || null)

const colors = [
  { name: 'Indigo', bg: 'bg-indigo-600' },
  { name: 'Émeraude', bg: 'bg-emerald-500' },
  { name: 'Ambre', bg: 'bg-amber-500' },
  { name: 'Rose', bg: 'bg-pink-500' }
]

const arrowOptions: { value: ArrowStyle; label: string }[] = [
  { value: 'end', label: 'Fin' },
  { value: 'both', label: 'Double' },
  { value: 'none', label: 'Aucune' }
]

// Style de flèche d'un lien (défaut rétro-compatible : flèche en fin)
function connArrow(conn: Connection): ArrowStyle {
  return conn.arrow ?? 'end'
}

const selectedNode = computed(() => {
  if (selectedNodeId.value === null) return null
  return nodes.value.find(n => n.id === selectedNodeId.value) || null
})

function getNode(id: number) {
  return nodes.value.find(n => n.id === id)
}

const route = useRoute()

onMounted(async () => {
  await Promise.all([tagsStore.fetchTags(), fetchDiagramsList()])
  const diagIdQuery = route.query.id
  if (diagIdQuery) {
    const diagId = parseInt(diagIdQuery as string)
    const diag = diagrams.value.find(d => d.id === diagId)
    if (diag) {
      selectDiagram(diag)
    }
  }
})

watch(() => route.query.id, (newId) => {
  if (newId) {
    const diagId = parseInt(newId as string)
    const diag = diagrams.value.find(d => d.id === diagId)
    if (diag) {
      selectDiagram(diag)
    }
  } else {
    selectedDiagram.value = null
  }
})

async function fetchDiagramsList(tagId: number | null = selectedTagId.value) {
  loadingList.value = true
  try {
    const params = new URLSearchParams({ per_page: '1000' })
    if (tagId !== null) params.set('tag_id', String(tagId))
    const res = await api.get(`/diagrams?${params.toString()}`)
    diagrams.value = res.data.data
  } catch (err) {
    console.error('Erreur lors du chargement des diagrammes', err)
  } finally {
    loadingList.value = false
  }
}

async function filterByTag(tagId: number | null) {
  selectedTagId.value = tagId
  await fetchDiagramsList(tagId)
}

function selectDiagram(diag: BackendDiagram) {
  selectedDiagram.value = { ...diag }
  clearNodeSelection()
  linkingSourceId.value = null
  selectedMaskId.value = null
  selectedConnectionIndex.value = null
  editingNodeId.value = null
  selectedDrawingId.value = null
  drawingMode.value = 'select'
  resetView()
  isPanning.value = false
  resizingNodeId.value = null

  // Parser le contenu du diagramme
  try {
    const data = JSON.parse(diag.code)
    if (data && data.type === 'visual') {
      nodes.value = data.nodes || []
      connections.value = data.connections || []
      backgroundImage.value = data.backgroundImage || null
      masks.value = data.masks || []
      drawings.value = data.drawings || []
      activeTab.value = 'visual'
    } else {
      // Si ce n'est pas du JSON, on charge comme du code Mermaid
      mermaidCode.value = diag.code || ''
      backgroundImage.value = null
      masks.value = []
      drawings.value = []
      activeTab.value = 'mermaid'
    }
  } catch {
    // Si JSON parse échoue, c'est du Mermaid brut
    mermaidCode.value = diag.code || ''
    nodes.value = []
    connections.value = []
    backgroundImage.value = null
    masks.value = []
    drawings.value = []
    activeTab.value = 'mermaid'
  }

  initHistory()
}

async function saveDiagramTags(tags: Tag[]) {
  if (!selectedDiagram.value) return
  selectedDiagram.value.tags = await tagsStore.setTagsForEntity('diagrams', selectedDiagram.value.id, tags.map(tag => tag.id))
  const diagram = diagrams.value.find(item => item.id === selectedDiagram.value?.id)
  if (diagram) diagram.tags = selectedDiagram.value.tags
}

async function createNewDiagram() {
  const title = prompt('Entrez le titre du nouveau diagramme :')
  if (!title) return
  
  const defaultCode = JSON.stringify({
    type: 'visual',
    nodes: [
      { id: 1, label: 'Concept central', type: 'rect', x: 250, y: 150, color: 'bg-indigo-600' }
    ],
    connections: [],
    backgroundImage: null,
    masks: []
  })

  try {
    const res = await api.post('/diagrams', {
      title,
      code: defaultCode
    })
    
    // Réinitialiser les états locaux
    backgroundImage.value = null
    masks.value = []
    selectedMaskId.value = null
    drawingMode.value = 'select'
    
    // Rafraîchir la liste et sélectionner le nouveau diagramme
    await fetchDiagramsList()
    const newlyCreated = diagrams.value.find(d => d.id === res.data.id)
    if (newlyCreated) {
      selectDiagram(newlyCreated)
    }
  } catch (err) {
    console.error('Erreur de création de diagramme', err)
    alert('Impossible de créer le diagramme.')
  }
}

async function saveDiagram() {
  if (!selectedDiagram.value) return
  
  saving.value = true
  
  let codePayload = ''
  if (activeTab.value === 'visual') {
    codePayload = JSON.stringify({
      type: 'visual',
      nodes: nodes.value,
      connections: connections.value,
      backgroundImage: backgroundImage.value,
      masks: masks.value,
      drawings: drawings.value
    })
  } else {
    codePayload = mermaidCode.value
  }

  try {
    await api.put(`/diagrams/${selectedDiagram.value.id}`, {
      title: selectedDiagram.value.title,
      code: codePayload
    })
    
    alert('Diagramme enregistré avec succès !')
    await fetchDiagramsList()
  } catch (err) {
    console.error('Erreur lors de la sauvegarde du diagramme', err)
    alert('Erreur lors de la sauvegarde.')
  } finally {
    saving.value = false
  }
}

async function deleteDiagram(diag: BackendDiagram) {
  if (!confirm(`Supprimer le diagramme "${diag.title}" définitivement ?`)) return
  
  try {
    await api.delete(`/diagrams/${diag.id}`)
    
    if (selectedDiagram.value?.id === diag.id) {
      selectedDiagram.value = null
    }
    
    await fetchDiagramsList()
  } catch (err) {
    console.error(err)
    alert('Impossible de supprimer le diagramme.')
  }
}

// Outils d'édition visuelle
const NODE_DEFAULT_LABEL: Record<NodeShape, string> = {
  rect: 'Concept',
  circle: 'Événement',
  diamond: 'Décision',
  ellipse: 'Domaine',
  text: 'Texte',
  sticky: 'Note...'
}

function addNode(type: NodeShape) {
  const newId = nodes.value.length ? Math.max(...nodes.value.map(n => n.id)) + 1 : 1

  const newNode: VisualNode = {
    id: newId,
    label: NODE_DEFAULT_LABEL[type],
    type,
    x: 150 + Math.random() * 60,
    y: 150 + Math.random() * 60,
    color: 'bg-indigo-600'
  }

  nodes.value.push(newNode)
  selectSingleNode(newId)
}

function onNodeClick(node: VisualNode) {
  // La sélection est gérée dans onNodeMouseDown ; ici on ne traite que le liage.
  if (linkingSourceId.value !== null) {
    if (linkingSourceId.value !== node.id) {
      const alreadyLinked = connections.value.some(
        c => c.from === linkingSourceId.value && c.to === node.id
      )
      if (!alreadyLinked) {
        connections.value.push({
          from: linkingSourceId.value,
          to: node.id
        })
      }
    }
    linkingSourceId.value = null
  }
}

function startEditingNode(node: VisualNode) {
  selectSingleNode(node.id)
  selectedMaskId.value = null
  selectedConnectionIndex.value = null
  selectedDrawingId.value = null
  editingNodeId.value = node.id
}

function stopEditingNode() {
  editingNodeId.value = null
}

function onConnectionClick(idx: number) {
  selectedConnectionIndex.value = idx
  clearNodeSelection()
  selectedMaskId.value = null
  selectedDrawingId.value = null
  editingNodeId.value = null
}

function deleteSelectedConnection() {
  if (selectedConnectionIndex.value === null) return
  connections.value.splice(selectedConnectionIndex.value, 1)
  selectedConnectionIndex.value = null
}

function startLinking() {
  if (selectedNodeId.value !== null) {
    linkingSourceId.value = selectedNodeId.value
  }
}

function deleteSelectedNode() {
  if (selectedNodeIds.value.length === 0) return
  const ids = new Set(selectedNodeIds.value)
  nodes.value = nodes.value.filter(n => !ids.has(n.id))
  connections.value = connections.value.filter(
    c => !ids.has(c.from) && !ids.has(c.to)
  )
  clearNodeSelection()
  linkingSourceId.value = null
}

// Drag & drop canevas
function onNodeMouseDown(node: VisualNode, event: MouseEvent) {
  if (drawingMode.value === 'mask' || drawingMode.value === 'pen') return
  // En cours de liage : laisser le clic choisir la cible (pas de drag/sélection)
  if (linkingSourceId.value !== null) return

  selectedMaskId.value = null
  selectedConnectionIndex.value = null
  selectedDrawingId.value = null

  // Maj+clic : (dé)sélectionne le nœud sans démarrer de déplacement
  if (event.shiftKey) {
    toggleNodeSelection(node.id)
    return
  }

  // Clic simple sur un nœud hors sélection : sélection unique ; sinon on garde le groupe
  if (!isNodeSelected(node.id)) selectSingleNode(node.id)
  if (editingNodeId.value !== node.id) editingNodeId.value = null

  isDragging.value = true
  draggedNodeId.value = node.id

  const w = screenToWorld(event.clientX, event.clientY)
  dragOffset.value = { x: node.x - w.x, y: node.y - w.y }
  // Décalages de chaque nœud sélectionné pour un déplacement de groupe
  dragOffsets.value = selectedNodeIds.value
    .map(id => getNode(id))
    .filter((n): n is VisualNode => !!n)
    .map(n => ({ id: n.id, dx: n.x - w.x, dy: n.y - w.y }))
}

function onCanvasMouseDown(event: MouseEvent) {
  if (drawingMode.value === 'pen') {
    isDrawingPen.value = true
    const w = screenToWorld(event.clientX, event.clientY)
    currentStroke.value = {
      id: 'pen-' + Date.now(),
      points: [{ x: w.x, y: w.y }],
      color: penColor.value,
      width: 3
    }
  } else if (drawingMode.value === 'mask') {
    isDrawingMask.value = true
    const w = screenToWorld(event.clientX, event.clientY)
    tempMask.value = {
      startX: w.x,
      startY: w.y,
      x: w.x,
      y: w.y,
      width: 0,
      height: 0
    }
  } else if (event.shiftKey) {
    // Maj + glisser sur le fond : sélection par rectangle (marquee)
    isMarqueeing.value = true
    const w = screenToWorld(event.clientX, event.clientY)
    marqueeRect.value = { startX: w.x, startY: w.y, x: w.x, y: w.y, width: 0, height: 0 }
  } else {
    // Démarre un éventuel pan ; la désélection a lieu au relâchement sans déplacement
    isPanning.value = true
    panMoved.value = false
    panPointerStart.value = { x: event.clientX, y: event.clientY }
    panOriginStart.value = { x: panX.value, y: panY.value }
  }
}

function onCanvasMouseMove(event: MouseEvent) {
  if (drawingMode.value === 'pen' && isDrawingPen.value && currentStroke.value) {
    const w = screenToWorld(event.clientX, event.clientY)
    const pts = currentStroke.value.points
    const last = pts[pts.length - 1]
    // N'ajoute un point que si le curseur a bougé suffisamment (lissage)
    if (Math.hypot(w.x - last.x, w.y - last.y) > 2) pts.push({ x: w.x, y: w.y })
  } else if (resizingNodeId.value !== null) {
    const node = nodes.value.find(n => n.id === resizingNodeId.value)
    if (node) {
      // Redimensionnement ancré au centre : la poignée est au coin bas-droit
      const w = screenToWorld(event.clientX, event.clientY)
      node.width = snapVal(Math.max(MIN_NODE_SIZE, 2 * (w.x - node.x)))
      node.height = snapVal(Math.max(MIN_NODE_SIZE, 2 * (w.y - node.y)))
    }
  } else if (drawingMode.value === 'mask' && isDrawingMask.value && tempMask.value) {
    const w = screenToWorld(event.clientX, event.clientY)
    const startX = tempMask.value.startX
    const startY = tempMask.value.startY

    tempMask.value.x = Math.min(startX, w.x)
    tempMask.value.y = Math.min(startY, w.y)
    tempMask.value.width = Math.abs(w.x - startX)
    tempMask.value.height = Math.abs(w.y - startY)
  } else if (isMarqueeing.value && marqueeRect.value) {
    const w = screenToWorld(event.clientX, event.clientY)
    const startX = marqueeRect.value.startX
    const startY = marqueeRect.value.startY
    marqueeRect.value.x = Math.min(startX, w.x)
    marqueeRect.value.y = Math.min(startY, w.y)
    marqueeRect.value.width = Math.abs(w.x - startX)
    marqueeRect.value.height = Math.abs(w.y - startY)
  } else if (isDragging.value && draggedNodeId.value !== null) {
    const w = screenToWorld(event.clientX, event.clientY)
    // Déplacement de groupe via les décalages capturés au départ
    for (const off of dragOffsets.value) {
      const node = getNode(off.id)
      if (node) {
        node.x = clampCoord(snapVal(w.x + off.dx))
        node.y = clampCoord(snapVal(w.y + off.dy))
      }
    }
  } else if (isPanning.value) {
    const dx = event.clientX - panPointerStart.value.x
    const dy = event.clientY - panPointerStart.value.y
    if (Math.hypot(dx, dy) > 3) panMoved.value = true
    panX.value = panOriginStart.value.x + dx
    panY.value = panOriginStart.value.y + dy
  }
}

function onCanvasMouseUp() {
  if (resizingNodeId.value !== null) {
    resizingNodeId.value = null
    return
  }
  if (drawingMode.value === 'pen' && isDrawingPen.value) {
    isDrawingPen.value = false
    if (currentStroke.value && currentStroke.value.points.length > 1) {
      drawings.value.push(currentStroke.value)
    }
    currentStroke.value = null
    return
  }
  if (drawingMode.value === 'mask' && isDrawingMask.value && tempMask.value) {
    isDrawingMask.value = false
    const width = tempMask.value.width
    const height = tempMask.value.height
    if (width > 5 && height > 5) {
      const label = prompt('Entrez le mot caché / label de la zone occultée :')
      if (label) {
        const id = 'mask-' + Date.now()
        masks.value.push({
          id,
          x: tempMask.value.x,
          y: tempMask.value.y,
          width,
          height,
          label
        })
        selectedMaskId.value = id
      }
    }
    tempMask.value = null
  } else if (isMarqueeing.value && marqueeRect.value) {
    // Sélectionne les nœuds dont le centre est dans le rectangle
    const r = marqueeRect.value
    if (r.width > 4 && r.height > 4) {
      const ids = nodes.value
        .filter(n => n.x >= r.x && n.x <= r.x + r.width && n.y >= r.y && n.y <= r.y + r.height)
        .map(n => n.id)
      selectedNodeIds.value = ids
      selectedNodeId.value = ids[ids.length - 1] ?? null
      selectedMaskId.value = null
      selectedConnectionIndex.value = null
      selectedDrawingId.value = null
    }
    isMarqueeing.value = false
    marqueeRect.value = null
  } else {
    // Clic simple sur le fond (pan sans déplacement) → désélection
    if (isPanning.value && !panMoved.value) {
      clearNodeSelection()
      selectedMaskId.value = null
      selectedConnectionIndex.value = null
      selectedDrawingId.value = null
      editingNodeId.value = null
    }
    isPanning.value = false
    panMoved.value = false
    isDragging.value = false
    draggedNodeId.value = null
  }
}

function onBackgroundImageUploaded(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      backgroundImage.value = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

function onMaskClick(mask: any) {
  clearNodeSelection()
  selectedConnectionIndex.value = null
  selectedDrawingId.value = null
  selectedMaskId.value = mask.id
}

function deleteSelectedMask() {
  if (selectedMaskId.value === null) return
  masks.value = masks.value.filter(m => m.id !== selectedMaskId.value)
  selectedMaskId.value = null
}

function onDrawingClick(id: string) {
  if (drawingMode.value !== 'select') return
  clearNodeSelection()
  selectedMaskId.value = null
  selectedConnectionIndex.value = null
  editingNodeId.value = null
  selectedDrawingId.value = id
}

function deleteSelectedDrawing() {
  if (selectedDrawingId.value === null) return
  drawings.value = drawings.value.filter(d => d.id !== selectedDrawingId.value)
  selectedDrawingId.value = null
}

function togglePenMode() {
  drawingMode.value = drawingMode.value === 'pen' ? 'select' : 'pen'
  clearNodeSelection()
  selectedMaskId.value = null
  selectedConnectionIndex.value = null
  selectedDrawingId.value = null
  editingNodeId.value = null
}

// Raccourci clavier : Suppr / Backspace efface l'élément sélectionné
// ---- Historique (annuler / rétablir) ----
const history = ref<string[]>([])
const historyIndex = ref(0)
const isApplyingHistory = ref(false)
let histTimer: ReturnType<typeof setTimeout> | null = null

const canUndo = computed(() => historyIndex.value > 0)
const canRedo = computed(() => historyIndex.value < history.value.length - 1)

function snapshotDoc() {
  return JSON.stringify({
    nodes: nodes.value,
    connections: connections.value,
    masks: masks.value,
    backgroundImage: backgroundImage.value,
    drawings: drawings.value,
  })
}

function initHistory() {
  history.value = [snapshotDoc()]
  historyIndex.value = 0
}

function recordHistory() {
  if (isApplyingHistory.value) return
  const snap = snapshotDoc()
  if (snap === history.value[historyIndex.value]) return
  // Tronque la branche « rétablir » avant d'empiler le nouvel état
  history.value = history.value.slice(0, historyIndex.value + 1)
  history.value.push(snap)
  if (history.value.length > 50) history.value.shift()
  historyIndex.value = history.value.length - 1
}

function applySnapshot(snap: string) {
  const data = JSON.parse(snap)
  isApplyingHistory.value = true
  nodes.value = data.nodes || []
  connections.value = data.connections || []
  masks.value = data.masks || []
  backgroundImage.value = data.backgroundImage ?? null
  drawings.value = data.drawings || []
  clearNodeSelection()
  selectedMaskId.value = null
  selectedConnectionIndex.value = null
  selectedDrawingId.value = null
  editingNodeId.value = null
  resizingNodeId.value = null
  nextTick(() => { isApplyingHistory.value = false })
}

function undo() {
  if (!canUndo.value) return
  historyIndex.value--
  applySnapshot(history.value[historyIndex.value])
}

function redo() {
  if (!canRedo.value) return
  historyIndex.value++
  applySnapshot(history.value[historyIndex.value])
}

watch([nodes, connections, masks, backgroundImage, drawings], () => {
  if (isApplyingHistory.value) return
  if (histTimer) clearTimeout(histTimer)
  histTimer = setTimeout(recordHistory, 350)
}, { deep: true })

function onKeydown(event: KeyboardEvent) {
  if (!selectedDiagram.value || activeTab.value !== 'visual') return

  // Ne pas intercepter pendant la saisie de texte (titre, label inline, tags…)
  const target = event.target as HTMLElement | null
  const typing = !!target && (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName))

  const mod = event.ctrlKey || event.metaKey
  if (mod && (event.key === 'z' || event.key === 'Z')) {
    if (typing) return
    event.shiftKey ? redo() : undo()
    event.preventDefault()
    return
  }
  if (mod && (event.key === 'y' || event.key === 'Y')) {
    if (typing) return
    redo()
    event.preventDefault()
    return
  }

  if (event.key !== 'Delete' && event.key !== 'Backspace') return
  if (typing) return

  if (selectedNodeIds.value.length > 0) {
    deleteSelectedNode()
    event.preventDefault()
  } else if (selectedMaskId.value !== null) {
    deleteSelectedMask()
    event.preventDefault()
  } else if (selectedConnectionIndex.value !== null) {
    deleteSelectedConnection()
    event.preventDefault()
  } else if (selectedDrawingId.value !== null) {
    deleteSelectedDrawing()
    event.preventDefault()
  }
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
</script>
