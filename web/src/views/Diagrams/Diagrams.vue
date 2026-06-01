<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl font-bold">Créateur de Diagrammes & Cartes Mentales</h1>
        <p class="text-xs text-slate-400 dark:text-slate-500 mt-1">Concevez des schémas visuels en plaçant des formes, en créant des liaisons et en les organisant à la main.</p>
      </div>

      <!-- Tab Switcher (Visual Editor vs Mermaid Code Editor) -->
      <div class="flex items-center gap-1.5 bg-slate-105 p-1 rounded-xl dark:bg-slate-900 border border-slate-100 dark:border-slate-800">
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

    <!-- TAB 1: VISUAL INTERACTIVE CREATOR -->
    <div v-if="activeTab === 'visual'" class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      <!-- Toolbox Panel (Left - 3 columns) -->
      <div class="lg:col-span-3 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-3xl p-5 shadow-sm space-y-6">
        <div>
          <h3 class="font-bold text-sm text-slate-800 dark:text-white">Boîte à outils</h3>
          <p class="text-[10px] text-slate-400 mt-0.5">Cliquez sur une forme pour l'ajouter</p>
        </div>

        <!-- Add Shapes Buttons -->
        <div class="grid grid-cols-1 gap-2.5">
          <button 
            @click="addNode('rect')"
            class="flex items-center gap-3 p-3 bg-slate-50 hover:bg-indigo-50/50 dark:bg-slate-800/40 dark:hover:bg-indigo-950/20 border border-slate-100 dark:border-slate-850 rounded-xl text-left transition-colors"
          >
            <div class="w-8 h-6 bg-indigo-500 rounded border border-indigo-600"></div>
            <span class="text-xs font-semibold">Concept (Rectangle)</span>
          </button>

          <button 
            @click="addNode('circle')"
            class="flex items-center gap-3 p-3 bg-slate-50 hover:bg-indigo-50/50 dark:bg-slate-800/40 dark:hover:bg-indigo-950/20 border border-slate-100 dark:border-slate-850 rounded-xl text-left transition-colors"
          >
            <div class="w-8 h-8 rounded-full bg-emerald-500 border border-emerald-600"></div>
            <span class="text-xs font-semibold">Événement (Cercle)</span>
          </button>

          <button 
            @click="addNode('diamond')"
            class="flex items-center gap-3 p-3 bg-slate-50 hover:bg-indigo-50/50 dark:bg-slate-800/40 dark:hover:bg-indigo-950/20 border border-slate-100 dark:border-slate-850 rounded-xl text-left transition-colors"
          >
            <div class="w-6 h-6 rotate-45 bg-amber-500 border border-amber-600 mx-1"></div>
            <span class="text-xs font-semibold">Décision (Losange)</span>
          </button>
        </div>

        <div class="h-[1px] bg-slate-100 dark:bg-slate-800"></div>

        <!-- Selection Customization Controls -->
        <div v-if="selectedNode" class="space-y-4">
          <h4 class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Élément sélectionné</h4>
          
          <!-- Label input -->
          <div>
            <label class="block text-[10px] font-bold text-slate-400 mb-1.5 uppercase">Texte de l'étiquette</label>
            <input 
              type="text" 
              v-model="selectedNode.label"
              class="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 dark:bg-slate-850 dark:border-slate-800 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500 font-semibold"
            />
          </div>

          <!-- Color selection -->
          <div>
            <label class="block text-[10px] font-bold text-slate-400 mb-1.5 uppercase">Couleur</label>
            <div class="flex gap-2">
              <button 
                v-for="color in colors" 
                :key="color.bg"
                @click="selectedNode.color = color.bg"
                class="w-6 h-6 rounded-full border-2 transition-transform"
                :class="[color.bg, selectedNode.color === color.bg ? 'border-slate-900 scale-110 dark:border-white' : 'border-transparent']"
                :title="color.name"
              ></button>
            </div>
          </div>

          <!-- Action operations -->
          <div class="space-y-2 pt-2">
            <!-- Link trigger -->
            <button 
              @click="startLinking"
              class="w-full flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-bold border border-slate-200 dark:border-slate-800 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-850 transition-colors"
              :class="[linkingSourceId === selectedNode.id ? 'bg-indigo-50 text-indigo-600 border-indigo-200' : '']"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
              </svg>
              {{ linkingSourceId === selectedNode.id ? 'Cliquez sur la cible...' : 'Créer un lien' }}
            </button>
            
            <!-- Delete node -->
            <button 
              @click="deleteSelectedNode"
              class="w-full flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-bold text-rose-600 border border-rose-100 hover:bg-rose-50 dark:border-rose-950/20 dark:hover:bg-rose-950/30 rounded-xl transition-colors"
            >
              <Trash2 class="w-4 h-4" />
              Supprimer la forme
            </button>
          </div>
        </div>

        <div v-else class="text-center py-6 text-slate-400 text-xs font-medium italic">
          Sélectionnez une forme sur le plan pour modifier ses options.
        </div>
      </div>

      <!-- Canvas Editor Area (Right - 9 columns) -->
      <div class="lg:col-span-9 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-3xl p-2 shadow-sm overflow-hidden flex flex-col">
        
        <!-- Canvas Status info -->
        <div class="px-4 py-2 border-b border-slate-50 dark:border-slate-800/50 flex items-center justify-between text-[10px] text-slate-400 font-semibold uppercase tracking-wider select-none">
          <span>Plan de travail interactif</span>
          <span>Déplacer : Glisser-Déposer | Éditer : Clic simple</span>
        </div>

        <!-- Interactive SVG Canvas Container -->
        <div 
          class="relative w-full h-[550px] bg-slate-50/50 dark:bg-slate-950/15 overflow-hidden select-none cursor-crosshair"
          @mousemove="onCanvasMouseMove"
          @mouseup="onCanvasMouseUp"
          @mouseleave="onCanvasMouseUp"
        >
          <!-- Grid Background (subtle lines) -->
          <svg class="absolute inset-0 w-full h-full text-slate-200/50 dark:text-slate-800/40 pointer-events-none" width="100%" height="100%">
            <defs>
              <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <rect width="20" height="20" fill="none" />
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="currentColor" stroke-width="0.5" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>

          <!-- SVG Elements (Lines and Markers) -->
          <svg class="absolute inset-0 w-full h-full pointer-events-none">
            <defs>
              <!-- Arrow head definition -->
              <marker 
                id="arrowhead" 
                viewBox="0 0 10 10" 
                refX="22" 
                refY="5" 
                markerWidth="6" 
                markerHeight="6" 
                orient="auto-start-reverse"
              >
                <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#818cf8" />
              </marker>
            </defs>

            <!-- Render connections (arrows) -->
            <g v-for="(conn, idx) in connections" :key="idx">
              <line 
                v-if="getNode(conn.from) && getNode(conn.to)"
                :x1="getNode(conn.from)!.x" 
                :y1="getNode(conn.from)!.y" 
                :x2="getNode(conn.to)!.x" 
                :y2="getNode(conn.to)!.y" 
                stroke="#818cf8" 
                stroke-width="2.5" 
                marker-end="url(#arrowhead)" 
              />
            </g>
          </svg>

          <!-- Render Nodes (Interactive Shapes) -->
          <div 
            v-for="node in nodes" 
            :key="node.id"
            class="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-grab active:cursor-grabbing select-none"
            :style="{ top: `${node.y}px`, left: `${node.x}px` }"
            @mousedown.stop="onNodeMouseDown(node, $event)"
            @click.stop="onNodeClick(node)"
          >
            <!-- Rectangle node -->
            <div 
              v-if="node.type === 'rect'"
              class="w-32 h-11 rounded-xl border flex items-center justify-center text-center px-2 text-xs font-bold text-white shadow-md transition-all"
              :class="[
                node.color,
                selectedNodeId === node.id ? 'ring-2 ring-indigo-500 scale-105 ring-offset-2 dark:ring-offset-slate-900' : ''
              ]"
            >
              {{ node.label }}
            </div>

            <!-- Circle node -->
            <div 
              v-else-if="node.type === 'circle'"
              class="w-16 h-16 rounded-full border flex items-center justify-center text-center p-2 text-[10px] font-extrabold text-white shadow-md transition-all"
              :class="[
                node.color,
                selectedNodeId === node.id ? 'ring-2 ring-indigo-500 scale-105 ring-offset-2 dark:ring-offset-slate-900' : ''
              ]"
            >
              {{ node.label }}
            </div>

            <!-- Diamond node -->
            <div 
              v-else-if="node.type === 'diamond'"
              class="relative w-16 h-16 flex items-center justify-center text-center transition-all select-none"
              :class="[selectedNodeId === node.id ? 'scale-105' : '']"
            >
              <div 
                class="absolute inset-0 rotate-45 border rounded-lg shadow-md transition-all"
                :class="[node.color, selectedNodeId === node.id ? 'ring-2 ring-indigo-500 ring-offset-2 dark:ring-offset-slate-900' : '']"
              ></div>
              <span class="relative z-10 text-[9px] font-extrabold text-white px-2 leading-tight">{{ node.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: CODE MERMAID EDITOR (Previous version logic) -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <div class="lg:col-span-4 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-3xl p-6 shadow-sm flex flex-col space-y-4">
        <div>
          <h3 class="font-bold text-sm text-slate-800 dark:text-white">Code Source Mermaid</h3>
          <p class="text-[11px] text-slate-400 mt-0.5">Modifiez le code ci-dessous pour mettre à jour le schéma en temps réel</p>
        </div>
        <textarea v-model="mermaidCode" rows="15" class="w-full p-4 font-mono text-xs bg-slate-50 border border-slate-200 dark:bg-slate-950/40 dark:border-slate-800 rounded-2xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-slate-700 dark:text-slate-300 resize-y"></textarea>
      </div>

      <div class="lg:col-span-8 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-3xl p-6 shadow-sm flex flex-col min-h-[500px]">
        <div class="flex items-center justify-between border-b border-slate-50 dark:border-slate-800/50 pb-4 mb-6">
          <h3 class="font-bold text-sm text-slate-800 dark:text-white">Rendu Référant (Simulation)</h3>
        </div>
        <div class="flex-1 flex items-center justify-center p-4 border border-dashed border-slate-100 dark:border-slate-850 rounded-2xl bg-slate-50/30 dark:bg-slate-950/20 overflow-auto">
          <!-- Static representation as fallback -->
          <svg viewBox="0 0 500 400" class="w-full max-w-[460px] h-auto">
            <circle cx="250" cy="200" r="100" fill="none" stroke="#6366f1" stroke-dasharray="6,6" stroke-width="2" />
            <rect x="180" y="80" width="120" height="35" rx="10" fill="#6366f1" />
            <text x="250" y="102" fill="white" text-anchor="middle" font-size="11" font-weight="bold">Acetyl-CoA</text>
            <circle cx="350" cy="130" r="30" fill="#10b981" />
            <text x="350" y="133" fill="white" text-anchor="middle" font-size="10" font-weight="bold">Citrate</text>
            <circle cx="350" cy="270" r="30" fill="#10b981" />
            <text x="350" y="273" fill="white" text-anchor="middle" font-size="10" font-weight="bold">Succinate</text>
            <circle cx="150" cy="200" r="35" fill="#f59e0b" />
            <text x="150" y="203" fill="white" text-anchor="middle" font-size="10" font-weight="bold">Oxaloacétate</text>
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Trash2 } from '@lucide/vue'

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

const activeTab = ref('visual')
const selectedNodeId = ref<number | null>(null)
const linkingSourceId = ref<number | null>(null)

// Drag and drop state
const isDragging = ref(false)
const draggedNodeId = ref<number | null>(null)
const dragOffset = ref({ x: 0, y: 0 })

const colors = [
  { name: 'Indigo', bg: 'bg-indigo-600 border-indigo-700 dark:bg-indigo-600' },
  { name: 'Émeraude', bg: 'bg-emerald-500 border-emerald-600 dark:bg-emerald-600' },
  { name: 'Ambre', bg: 'bg-amber-500 border-amber-600 dark:bg-amber-600' },
  { name: 'Rose', bg: 'bg-pink-500 border-pink-600 dark:bg-pink-600' }
]

// Visual Nodes Mock dataset (Cycle de Krebs visual reconstruction)
const nodes = ref<VisualNode[]>([
  { id: 1, label: 'Acetyl-CoA', type: 'rect', x: 250, y: 110, color: 'bg-indigo-600 border-indigo-700 dark:bg-indigo-600' },
  { id: 2, label: 'Citrate', type: 'circle', x: 370, y: 180, color: 'bg-emerald-500 border-emerald-600 dark:bg-emerald-600' },
  { id: 3, label: 'Succinate', type: 'circle', x: 340, y: 340, color: 'bg-emerald-500 border-emerald-600 dark:bg-emerald-600' },
  { id: 4, label: 'Oxaloacétate', type: 'diamond', x: 130, y: 240, color: 'bg-amber-500 border-amber-600 dark:bg-amber-600' }
])

const connections = ref<Connection[]>([
  { from: 1, to: 2 },
  { from: 2, to: 3 },
  { from: 3, to: 4 },
  { from: 4, to: 1 }
])

const mermaidCode = ref(`graph TD
  AcetylCoA[Acetyl-CoA] --> Citrate((Citrate))
  Citrate --> Succinate((Succinate))
  Succinate --> Oxaloacetate((Oxaloacétate))
  Oxaloacetate --> AcetylCoA`)

const selectedNode = computed(() => {
  if (selectedNodeId.value === null) return null
  return nodes.value.find(n => n.id === selectedNodeId.value) || null
})

function getNode(id: number) {
  return nodes.value.find(n => n.id === id)
}

// Add Node tool action
function addNode(type: 'rect' | 'circle' | 'diamond') {
  const newId = nodes.value.length ? Math.max(...nodes.value.map(n => n.id)) + 1 : 1
  let label = 'Nouveau'
  if (type === 'rect') label = 'Concept'
  if (type === 'circle') label = 'Événement'
  if (type === 'diamond') label = 'Décision'

  const newNode: VisualNode = {
    id: newId,
    label,
    type,
    x: 100 + Math.random() * 80,
    y: 100 + Math.random() * 80,
    color: 'bg-indigo-600 border-indigo-700 dark:bg-indigo-600'
  }
  
  nodes.value.push(newNode)
  selectedNodeId.value = newId
}

// Node actions
function onNodeClick(node: VisualNode) {
  if (linkingSourceId.value !== null) {
    // If we are in linking mode, make connection to clicked target node
    if (linkingSourceId.value !== node.id) {
      // Avoid duplicate links
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
  
  // Remove node
  nodes.value = nodes.value.filter(n => n.id !== selectedNodeId.value)
  // Remove linked connections
  connections.value = connections.value.filter(
    c => c.from !== selectedNodeId.value && c.to !== selectedNodeId.value
  )
  
  selectedNodeId.value = null
  linkingSourceId.value = null
}

// Drag & drop logic
function onNodeMouseDown(node: VisualNode, event: MouseEvent) {
  isDragging.value = true
  draggedNodeId.value = node.id
  selectedNodeId.value = node.id
  
  // Save cursor position offset relative to node origin
  dragOffset.value = {
    x: event.clientX - node.x,
    y: event.clientY - node.y
  }
}

function onCanvasMouseMove(event: MouseEvent) {
  if (!isDragging.value || draggedNodeId.value === null) return

  const node = nodes.value.find(n => n.id === draggedNodeId.value)
  if (node) {
    // Recalculate coordinates within canvas boundaries
    let newX = event.clientX - dragOffset.value.x
    let newY = event.clientY - dragOffset.value.y

    // Boundaries clamping (e.g. 50 to max)
    node.x = Math.max(40, Math.min(680, newX))
    node.y = Math.max(40, Math.min(500, newY))
  }
}

function onCanvasMouseUp() {
  isDragging.value = false
  draggedNodeId.value = null
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

.perspective-1000 {
  perspective: 1000px;
}
</style>
