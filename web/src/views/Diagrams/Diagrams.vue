<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header principal -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl font-bold">Créateur de Diagrammes & Cartes Mentales</h1>
        <p class="text-xs text-slate-400 dark:text-slate-500 mt-1">
          Concevez des schémas visuels en plaçant des formes, en créant des liaisons et en les organisant à la main.
        </p>
      </div>

      <!-- Tab Switcher (Créateur Visuel vs Code Mermaid) -->
      <div v-if="selectedDiagram" class="flex items-center gap-1.5 bg-slate-100 p-1 rounded-xl dark:bg-slate-900 border border-slate-100 dark:border-slate-800">
        <button 
          @click="activeTab = 'visual'"
          class="px-4 py-2 text-xs font-bold rounded-lg transition-all"
          :class="[activeTab === 'visual' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900']"
        >
          Créateur Visuel
        </button>
        <button 
          @click="activeTab = 'mermaid'"
          class="px-4 py-2 text-xs font-bold rounded-lg transition-all"
          :class="[activeTab === 'mermaid' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900']"
        >
          Mode Code Mermaid
        </button>
      </div>
    </div>

    <div class="flex flex-wrap items-center gap-2 rounded-2xl border border-slate-100 bg-white p-3 dark:border-slate-800 dark:bg-slate-900">
      <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Filtrer</span>
      <button type="button" class="rounded-xl px-3 py-1.5 text-xs font-bold" :class="selectedTagId === null ? 'bg-indigo-600 text-white' : 'bg-slate-50 text-slate-500 dark:bg-slate-800 dark:text-slate-300'" @click="filterByTag(null)">Tous</button>
      <button
        v-for="tag in tagsStore.tags"
        :key="tag.id"
        type="button"
        class="rounded-xl px-3 py-1.5 text-xs font-bold"
        :style="selectedTagId === tag.id ? { backgroundColor: tag.color || '#4F46E5', color: '#fff' } : undefined"
        :class="selectedTagId === tag.id ? '' : 'bg-slate-50 text-slate-500 dark:bg-slate-800 dark:text-slate-300'"
        @click="filterByTag(tag.id)"
      >
        {{ tag.name }}
      </button>
    </div>

    <!-- Layout principal en grille -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <!-- 1. PANNEAU GAUCHE : LISTE DES DIAGRAMMES (3 colonnes) -->
      <div class="lg:col-span-3 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-5 shadow-sm space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="font-extrabold text-sm text-slate-800 dark:text-white uppercase tracking-wider">Mes Diagrammes</h3>
          <button 
            @click="createNewDiagram"
            class="p-1.5 bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-950/40 dark:hover:bg-indigo-900/60 text-indigo-600 dark:text-indigo-400 rounded-xl transition-all active:scale-90"
            title="Créer un nouveau diagramme"
          >
            <Plus class="w-4 h-4" />
          </button>
        </div>

        <!-- Chargement -->
        <div v-if="loadingList" class="flex justify-center py-8">
          <svg class="animate-spin h-5 w-5 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
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
                ? 'border-indigo-500 bg-indigo-50/30 dark:bg-indigo-950/20 text-indigo-600 dark:text-indigo-400 font-bold' 
                : 'border-slate-100 hover:border-slate-200 dark:border-slate-800 dark:hover:border-slate-700 text-slate-700 dark:text-slate-350'
            ]"
          >
            <div class="flex items-center gap-2.5 min-w-0">
              <Activity class="w-4 h-4 flex-shrink-0 text-slate-400" :class="{ 'text-indigo-500': selectedDiagram?.id === diag.id }" />
              <span class="text-xs truncate font-semibold">{{ diag.title || 'Diagramme sans titre' }}</span>
            </div>

            <!-- Bouton de suppression -->
            <button 
              @click.stop="deleteDiagram(diag)"
              class="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-500 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/20 transition-all"
              title="Supprimer le diagramme"
            >
              <Trash2 class="w-3.5 h-3.5" />
            </button>
          </div>

          <div v-if="diagrams.length === 0" class="text-center py-8 text-xs text-slate-400 italic">
            Aucun diagramme enregistré. Cliquez sur le bouton + pour commencer !
          </div>
        </div>
      </div>

      <!-- 2. PANNEAU CENTRAL/DROIT : L'ÉDITEUR ACTIF (9 colonnes) -->
      <div class="lg:col-span-9 space-y-6">
        <!-- Message si aucun diagramme sélectionné -->
        <div 
          v-if="!selectedDiagram" 
          class="border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-3xl p-16 flex flex-col items-center justify-center text-center text-slate-400 bg-white dark:bg-slate-900"
        >
          <Activity class="w-12 h-12 text-slate-300 dark:text-slate-700 mb-3" />
          <h4 class="font-bold text-slate-850 dark:text-slate-200">Aucun diagramme en cours d'édition</h4>
          <p class="text-xs mt-1">Sélectionnez un diagramme dans la liste latérale ou créez-en un nouveau.</p>
          <button 
            @click="createNewDiagram"
            class="mt-4 px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl transition-all"
          >
            Nouveau diagramme
          </button>
        </div>

        <!-- Éditeur actif -->
        <div v-else class="space-y-4">
          <!-- Barre d'outils du diagramme en cours d'édition -->
          <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-4 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
            <div class="flex items-center gap-3 w-full sm:w-auto">
              <span class="text-xs font-bold text-slate-450 uppercase tracking-wider">Titre :</span>
              <input 
                type="text" 
                v-model="selectedDiagram.title"
                class="flex-1 sm:w-64 px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 dark:bg-slate-850 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 font-bold"
                placeholder="Nom du diagramme..."
              />
            </div>
            <div class="w-full sm:w-80">
              <TagSelector v-model="selectedDiagram.tags" @change="saveDiagramTags" />
            </div>

            <!-- Intégration de l'ID du diagramme pour insertion dans les notes -->
            <div class="flex items-center gap-3 w-full sm:w-auto justify-end">
              <span 
                class="text-[10px] bg-slate-100 dark:bg-slate-800 px-2.5 py-1 rounded-lg text-slate-500 font-mono font-bold select-all cursor-help"
                title="Copiez cette balise et collez-la dans n'importe quelle note de cours pour y afficher ce diagramme."
              >
                Code note : [diagram:{{ selectedDiagram.id }}]
              </span>

              <button 
                @click="saveDiagram"
                :disabled="saving"
                class="inline-flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-md shadow-emerald-600/10 disabled:opacity-50 active:scale-95 transition-all"
              >
                <Save class="w-3.5 h-3.5" />
                {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
              </button>
            </div>
          </div>

          <!-- TAB 1: CRÉATEUR VISUEL INTERACTIF -->
          <div v-if="activeTab === 'visual'" class="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
            <!-- Palette de formes (3 cols) -->
            <div class="md:col-span-3 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-5 shadow-sm space-y-4">
              <div>
                <h4 class="font-bold text-xs text-slate-850 dark:text-white uppercase tracking-wider">Ajouter des formes</h4>
                <p class="text-[9px] text-slate-400 mt-0.5">Glissez ou cliquez pour insérer sur le plan</p>
              </div>

              <div class="grid grid-cols-1 gap-2">
                <button 
                  @click="addNode('rect')"
                  class="flex items-center gap-3 p-2.5 bg-slate-50 hover:bg-indigo-50/50 dark:bg-slate-800/40 dark:hover:bg-indigo-950/20 border border-slate-100 dark:border-slate-850 rounded-xl text-left transition-colors"
                >
                  <div class="w-8 h-5 bg-indigo-500 rounded border border-indigo-600"></div>
                  <span class="text-[11px] font-bold">Concept (Rectangle)</span>
                </button>

                <button 
                  @click="addNode('circle')"
                  class="flex items-center gap-3 p-2.5 bg-slate-50 hover:bg-indigo-50/50 dark:bg-slate-800/40 dark:hover:bg-indigo-950/20 border border-slate-100 dark:border-slate-850 rounded-xl text-left transition-colors"
                >
                  <div class="w-7 h-7 rounded-full bg-emerald-500 border border-emerald-600"></div>
                  <span class="text-[11px] font-bold">Événement (Cercle)</span>
                </button>

                <button 
                  @click="addNode('diamond')"
                  class="flex items-center gap-3 p-2.5 bg-slate-50 hover:bg-indigo-50/50 dark:bg-slate-800/40 dark:hover:bg-indigo-950/20 border border-slate-100 dark:border-slate-850 rounded-xl text-left transition-colors"
                >
                  <div class="w-5 h-5 rotate-45 bg-amber-500 border border-amber-600 mx-1"></div>
                  <span class="text-[11px] font-bold">Décision (Losange)</span>
                </button>
              </div>

              <!-- Contrôles d'occlusion et d'image d'arrière-plan -->
              <div class="h-[1px] bg-slate-100 dark:bg-slate-800"></div>

              <div class="space-y-4">
                <div>
                  <h4 class="font-bold text-xs text-slate-850 dark:text-white uppercase tracking-wider">Image d'arrière-plan</h4>
                  <p class="text-[9px] text-slate-400 mt-0.5">Importez une image pour l'occulter</p>
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
                    class="flex-1 px-3 py-2 text-xs font-bold border border-slate-200 dark:border-slate-850 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-850 transition-colors"
                  >
                    {{ backgroundImage ? 'Changer l\'image' : 'Importer image' }}
                  </button>
                  <button 
                    v-if="backgroundImage"
                    @click="backgroundImage = null" 
                    class="p-2 text-rose-500 border border-rose-100 dark:border-rose-950/20 rounded-xl hover:bg-rose-50 dark:hover:bg-rose-950/25 transition-colors"
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
                        ? 'bg-rose-600 border-rose-700 text-white shadow-sm hover:bg-rose-700' 
                        : 'border-slate-250 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-850 text-slate-700 dark:text-slate-350'
                    ]"
                  >
                    <Sparkles class="w-3.5 h-3.5" />
                    {{ drawingMode === 'mask' ? 'Mode Masque : Actif' : 'Dessiner un masque rect' }}
                  </button>
                </div>
              </div>

              <div class="h-[1px] bg-slate-100 dark:bg-slate-800"></div>

              <!-- Options du nœud sélectionné -->
              <div v-if="selectedNode" class="space-y-4">
                <h4 class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Élément sélectionné</h4>
                
                <div>
                  <label class="block text-[9px] font-bold text-slate-400 mb-1 uppercase">Texte</label>
                  <input 
                    type="text" 
                    v-model="selectedNode.label"
                    class="w-full px-2.5 py-1.5 text-xs bg-slate-50 border border-slate-200 dark:bg-slate-850 dark:border-slate-800 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500 font-semibold"
                  />
                </div>

                <div>
                  <label class="block text-[9px] font-bold text-slate-400 mb-1 uppercase">Couleur</label>
                  <div class="flex flex-wrap gap-1.5">
                    <button 
                      v-for="color in colors" 
                      :key="color.bg"
                      @click="selectedNode.color = color.bg"
                      class="w-5.5 h-5.5 rounded-full border transition-transform"
                      :class="[color.bg, selectedNode.color === color.bg ? 'border-slate-900 scale-110 dark:border-white' : 'border-transparent']"
                      :title="color.name"
                    ></button>
                  </div>
                </div>

                <div class="space-y-2 pt-2">
                  <button 
                    @click="startLinking"
                    class="w-full flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-bold border border-slate-250 dark:border-slate-700 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-850 transition-colors"
                    :class="[linkingSourceId === selectedNode.id ? 'bg-indigo-50 text-indigo-600 border-indigo-200' : '']"
                  >
                    <LinkIcon class="w-3.5 h-3.5" />
                    {{ linkingSourceId === selectedNode.id ? 'Cible : cliquez sur une forme' : 'Relier à...' }}
                  </button>
                  
                  <button 
                    @click="deleteSelectedNode"
                    class="w-full flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-bold text-rose-600 border border-rose-100 hover:bg-rose-50 dark:border-rose-950/20 dark:hover:bg-rose-950/30 rounded-xl transition-colors"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                    Supprimer la forme
                  </button>
                </div>
              </div>

              <!-- Options du masque sélectionné -->
              <div v-else-if="selectedMask" class="space-y-4">
                <h4 class="text-[10px] font-bold text-slate-400 uppercase tracking-wider text-rose-500">Masque sélectionné</h4>
                
                <div>
                  <label class="block text-[9px] font-bold text-slate-400 mb-1 uppercase">Texte masqué</label>
                  <input 
                    type="text" 
                    v-model="selectedMask.label"
                    class="w-full px-2.5 py-1.5 text-xs bg-slate-50 border border-slate-200 dark:bg-slate-850 dark:border-slate-800 rounded-lg focus:outline-none focus:ring-1 focus:ring-rose-500 font-semibold"
                    placeholder="ex: Le Noyau"
                  />
                </div>

                <div class="pt-2">
                  <button 
                    @click="deleteSelectedMask"
                    class="w-full flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-bold text-rose-600 border border-rose-100 hover:bg-rose-50 dark:border-rose-950/20 dark:hover:bg-rose-950/30 rounded-xl transition-colors"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                    Supprimer le masque
                  </button>
                </div>
              </div>

              <div v-else class="text-center py-4 text-slate-400 text-xs italic">
                Sélectionnez une forme ou un masque sur le canevas pour l'éditer.
              </div>
            </div>

            <!-- Canevas d'édition (9 cols) -->
            <div class="md:col-span-9 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-2 shadow-sm flex flex-col overflow-hidden">
              <div class="px-4 py-1.5 border-b border-slate-50 dark:border-slate-800/50 flex items-center justify-between text-[9px] text-slate-450 font-bold uppercase tracking-wider select-none">
                <span>Plan interactif</span>
                <span v-if="drawingMode === 'mask'" class="text-rose-500 font-extrabold animate-pulse">Mode Masque actif : Cliquez-glissez pour dessiner un masque</span>
                <span v-else>Clic : Sélectionner / Déplacer | Option Relier pour lier</span>
              </div>

              <!-- Zone SVG interactive -->
              <div 
                class="relative w-full h-[450px] bg-slate-50/50 dark:bg-slate-950/15 overflow-hidden select-none"
                :class="[drawingMode === 'mask' ? 'cursor-cell' : 'cursor-crosshair']"
                @mousedown="onCanvasMouseDown"
                @mousemove="onCanvasMouseMove"
                @mouseup="onCanvasMouseUp"
                @mouseleave="onCanvasMouseUp"
              >
                <!-- SVG global pour grille, image de fond, connexions et masques -->
                <svg class="absolute inset-0 w-full h-full" style="cursor: inherit;">
                  <defs>
                    <pattern id="canvas-grid" width="20" height="20" patternUnits="userSpaceOnUse">
                      <rect width="20" height="20" fill="none" />
                      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="currentColor" stroke-width="0.5" class="text-slate-200/50 dark:text-slate-800/40" />
                    </pattern>
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
                  
                  <!-- Grille -->
                  <rect width="100%" height="100%" fill="url(#canvas-grid)" class="pointer-events-none" />
                  
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
                  <g class="pointer-events-none">
                    <g v-for="(conn, idx) in connections" :key="idx">
                      <line 
                        v-if="getNode(conn.from) && getNode(conn.to)"
                        :x1="getNode(conn.from)!.x" 
                        :y1="getNode(conn.from)!.y" 
                        :x2="getNode(conn.to)!.x" 
                        :y2="getNode(conn.to)!.y" 
                        stroke="#6366f1" 
                        stroke-width="2" 
                        marker-end="url(#arrow)" 
                      />
                    </g>
                  </g>
                  
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
                </svg>

                <!-- Formes/Nœuds interactifs -->
                <div 
                  v-for="node in nodes" 
                  :key="node.id"
                  class="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-grab active:cursor-grabbing select-none"
                  :style="{ top: `${node.y}px`, left: `${node.x}px` }"
                  @mousedown.stop="onNodeMouseDown(node, $event)"
                  @click.stop="onNodeClick(node)"
                >
                  <!-- Rectangle -->
                  <div 
                    v-if="node.type === 'rect'"
                    class="w-28 h-10 rounded-xl border flex items-center justify-center text-center px-2 text-[10px] font-bold text-white shadow transition-all"
                    :class="[
                      node.color,
                      selectedNodeId === node.id ? 'ring-2 ring-indigo-500 scale-105 ring-offset-2 dark:ring-offset-slate-900' : ''
                    ]"
                  >
                    {{ node.label }}
                  </div>

                  <!-- Cercle -->
                  <div 
                    v-else-if="node.type === 'circle'"
                    class="w-14 h-14 rounded-full border flex items-center justify-center text-center p-2 text-[9px] font-extrabold text-white shadow transition-all"
                    :class="[
                      node.color,
                      selectedNodeId === node.id ? 'ring-2 ring-indigo-500 scale-105 ring-offset-2 dark:ring-offset-slate-900' : ''
                    ]"
                  >
                    {{ node.label }}
                  </div>

                  <!-- Losange -->
                  <div 
                    v-else-if="node.type === 'diamond'"
                    class="relative w-14 h-14 flex items-center justify-center text-center transition-all select-none"
                    :class="[selectedNodeId === node.id ? 'scale-105' : '']"
                  >
                    <div 
                      class="absolute inset-0 rotate-45 border rounded-lg shadow transition-all"
                      :class="[node.color, selectedNodeId === node.id ? 'ring-2 ring-indigo-500 ring-offset-2 dark:ring-offset-slate-900' : '']"
                    ></div>
                    <span class="relative z-10 text-[8px] font-extrabold text-white px-2 leading-tight">{{ node.label }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- TAB 2: CODE MERMAID EDITOR -->
          <div v-else class="grid grid-cols-1 md:grid-cols-12 gap-6">
            <!-- Code Editor (4 cols) -->
            <div class="md:col-span-4 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-5 shadow-sm flex flex-col space-y-3">
              <div>
                <h4 class="font-bold text-xs text-slate-850 dark:text-white uppercase tracking-wider">Code Mermaid</h4>
                <p class="text-[9px] text-slate-400 mt-0.5">Décrivez votre schéma textuellement</p>
              </div>
              <textarea 
                v-model="mermaidCode" 
                rows="15" 
                class="w-full p-4 font-mono text-xs bg-slate-50 border border-slate-205 dark:bg-slate-950/40 dark:border-slate-800 rounded-2xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-700 dark:text-slate-350 resize-y"
              ></textarea>
            </div>

            <!-- Visual Preview Simulation (8 cols) -->
            <div class="md:col-span-8 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-5 shadow-sm flex flex-col min-h-[400px]">
              <h3 class="font-bold text-xs text-slate-800 dark:text-white uppercase tracking-wider border-b border-slate-50 dark:border-slate-800/50 pb-3 mb-4">
                Aperçu du Rendu
              </h3>
              <div class="flex-1 flex items-center justify-center p-4 border border-dashed border-slate-100 dark:border-slate-850 rounded-2xl bg-slate-50/30 dark:bg-slate-950/20 overflow-auto">
                <div class="text-center space-y-2">
                  <Activity class="w-8 h-8 text-indigo-500 mx-auto animate-pulse" />
                  <p class="text-xs font-semibold text-slate-500 dark:text-slate-400">Rendu du schéma Mermaid</p>
                  <pre class="text-[10px] text-slate-400 font-mono bg-slate-100 dark:bg-slate-800 px-3 py-1.5 rounded-lg select-all max-w-sm truncate">{{ mermaidCode }}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { useTagsStore, type Tag } from '../../stores/tags'
import TagSelector from '../../components/ui/TagSelector.vue'
import { 
  Plus, 
  Trash2, 
  Save, 
  Link as LinkIcon, 
  Activity, 
  Sparkles
} from '@lucide/vue'

interface VisualNode {
  id: number
  label: string
  type: 'rect' | 'circle' | 'diamond'
  x: number
  y: number
  color: string
}

interface Connection {
  from: number
  to: number
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
const linkingSourceId = ref<number | null>(null)

// Chargement & Sauvegarde
const loadingList = ref(false)
const saving = ref(false)

// Drag and drop canevas
const isDragging = ref(false)
const draggedNodeId = ref<number | null>(null)
const dragOffset = ref({ x: 0, y: 0 })

// Modèles locaux d'édition
const nodes = ref<VisualNode[]>([])
const connections = ref<Connection[]>([])
const mermaidCode = ref('')

// Modèles locaux d'occlusion et image de fond
const drawingMode = ref<'select' | 'mask'>('select')
const isDrawingMask = ref(false)
const tempMask = ref<{ startX: number; startY: number; x: number; y: number; width: number; height: number } | null>(null)
const masks = ref<{ id: string; x: number; y: number; width: number; height: number; label: string }[]>([])
const selectedMaskId = ref<string | null>(null)
const backgroundImage = ref<string | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

const selectedMask = computed(() => masks.value.find(m => m.id === selectedMaskId.value) || null)

const colors = [
  { name: 'Indigo', bg: 'bg-indigo-600' },
  { name: 'Émeraude', bg: 'bg-emerald-500' },
  { name: 'Ambre', bg: 'bg-amber-500' },
  { name: 'Rose', bg: 'bg-pink-500' }
]

const selectedNode = computed(() => {
  if (selectedNodeId.value === null) return null
  return nodes.value.find(n => n.id === selectedNodeId.value) || null
})

function getNode(id: number) {
  return nodes.value.find(n => n.id === id)
}

onMounted(async () => {
  await Promise.all([tagsStore.fetchTags(), fetchDiagramsList()])
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
  selectedNodeId.value = null
  linkingSourceId.value = null
  selectedMaskId.value = null
  drawingMode.value = 'select'
  
  // Parser le contenu du diagramme
  try {
    const data = JSON.parse(diag.code)
    if (data && data.type === 'visual') {
      nodes.value = data.nodes || []
      connections.value = data.connections || []
      backgroundImage.value = data.backgroundImage || null
      masks.value = data.masks || []
      activeTab.value = 'visual'
    } else {
      // Si ce n'est pas du JSON, on charge comme du code Mermaid
      mermaidCode.value = diag.code || ''
      backgroundImage.value = null
      masks.value = []
      activeTab.value = 'mermaid'
    }
  } catch {
    // Si JSON parse échoue, c'est du Mermaid brut
    mermaidCode.value = diag.code || ''
    nodes.value = []
    connections.value = []
    backgroundImage.value = null
    masks.value = []
    activeTab.value = 'mermaid'
  }
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
      masks: masks.value
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
function addNode(type: 'rect' | 'circle' | 'diamond') {
  const newId = nodes.value.length ? Math.max(...nodes.value.map(n => n.id)) + 1 : 1
  let label = 'Concept'
  if (type === 'circle') label = 'Événement'
  if (type === 'diamond') label = 'Décision'

  const newNode: VisualNode = {
    id: newId,
    label,
    type,
    x: 150 + Math.random() * 60,
    y: 150 + Math.random() * 60,
    color: 'bg-indigo-600'
  }
  
  nodes.value.push(newNode)
  selectedNodeId.value = newId
}

function onNodeClick(node: VisualNode) {
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
  } else {
    selectedNodeId.value = node.id
  }
}

function startLinking() {
  if (selectedNodeId.value !== null) {
    linkingSourceId.value = selectedNodeId.value
  }
}

function deleteSelectedNode() {
  if (selectedNodeId.value === null) return
  nodes.value = nodes.value.filter(n => n.id !== selectedNodeId.value)
  connections.value = connections.value.filter(
    c => c.from !== selectedNodeId.value && c.to !== selectedNodeId.value
  )
  selectedNodeId.value = null
  linkingSourceId.value = null
}

// Drag & drop canevas
function onNodeMouseDown(node: VisualNode, event: MouseEvent) {
  if (drawingMode.value === 'mask') return
  
  isDragging.value = true
  draggedNodeId.value = node.id
  selectedNodeId.value = node.id
  selectedMaskId.value = null
  
  dragOffset.value = {
    x: event.clientX - node.x,
    y: event.clientY - node.y
  }
}

function onCanvasMouseDown(event: MouseEvent) {
  if (drawingMode.value === 'mask') {
    isDrawingMask.value = true
    const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    tempMask.value = {
      startX: x,
      startY: y,
      x,
      y,
      width: 0,
      height: 0
    }
  } else {
    selectedNodeId.value = null
    selectedMaskId.value = null
  }
}

function onCanvasMouseMove(event: MouseEvent) {
  if (drawingMode.value === 'mask' && isDrawingMask.value && tempMask.value) {
    const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
    const currentX = event.clientX - rect.left
    const currentY = event.clientY - rect.top
    
    const startX = tempMask.value.startX
    const startY = tempMask.value.startY
    
    tempMask.value.x = Math.min(startX, currentX)
    tempMask.value.y = Math.min(startY, currentY)
    tempMask.value.width = Math.abs(currentX - startX)
    tempMask.value.height = Math.abs(currentY - startY)
  } else if (isDragging.value && draggedNodeId.value !== null) {
    const node = nodes.value.find(n => n.id === draggedNodeId.value)
    if (node) {
      let newX = event.clientX - dragOffset.value.x
      let newY = event.clientY - dragOffset.value.y

      node.x = Math.max(30, Math.min(650, newX))
      node.y = Math.max(30, Math.min(420, newY))
    }
  }
}

function onCanvasMouseUp() {
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
  } else {
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
  selectedNodeId.value = null
  selectedMaskId.value = mask.id
}

function deleteSelectedMask() {
  if (selectedMaskId.value === null) return
  masks.value = masks.value.filter(m => m.id !== selectedMaskId.value)
  selectedMaskId.value = null
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
