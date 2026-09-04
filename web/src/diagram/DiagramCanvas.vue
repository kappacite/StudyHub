<template>
  <svg
    class="w-full h-full touch-none select-none"
    :viewBox="viewBoxString"
    @wheel.prevent="onWheel"
    @mousedown="onBackgroundMouseDown"
  >
    <polyline
      v-for="rl in renderedLinks"
      :key="rl.id"
      data-test="diagram-link"
      :points="rl.points"
      fill="none"
      class="stroke-ink"
      stroke-width="2"
      :stroke-dasharray="rl.dashed ? '6 4' : undefined"
    />

    <g
      v-for="el in displayElements"
      :key="el.id"
      data-test="diagram-element"
      :data-id="el.id"
      @mousedown.stop="onElementMouseDown($event, el)"
    >
      <ellipse
        v-if="el.kind === 'shape' && (el.shape === 'circle' || el.shape === 'ellipse')"
        :cx="el.x + el.width / 2"
        :cy="el.y + el.height / 2"
        :rx="el.width / 2"
        :ry="el.height / 2"
        :fill="el.color"
      />
      <rect
        v-else-if="el.kind === 'shape'"
        :x="el.x"
        :y="el.y"
        :width="el.width"
        :height="el.height"
        :fill="el.color"
      />
      <text
        v-if="el.kind === 'shape'"
        :x="el.x + el.width / 2"
        :y="el.y + el.height / 2"
        text-anchor="middle"
        dominant-baseline="middle"
      >
        {{ el.label }}
      </text>
    </g>

    <rect
      v-if="selectedElementBounds"
      data-test="selection-outline"
      :x="selectedElementBounds.minX"
      :y="selectedElementBounds.minY"
      :width="selectedElementBounds.maxX - selectedElementBounds.minX"
      :height="selectedElementBounds.maxY - selectedElementBounds.minY"
      fill="none"
      class="stroke-accent"
      stroke-width="2"
      pointer-events="none"
    />

    <template v-for="(guide, i) in activeGuides" :key="i">
      <line
        v-if="guide.axis === 'x'"
        data-test="alignment-guide"
        :x1="guide.position"
        :y1="visibleWorldBounds.minY"
        :x2="guide.position"
        :y2="visibleWorldBounds.maxY"
        class="stroke-danger"
        stroke-width="1"
        pointer-events="none"
      />
      <line
        v-else
        data-test="alignment-guide"
        :x1="visibleWorldBounds.minX"
        :y1="guide.position"
        :x2="visibleWorldBounds.maxX"
        :y2="guide.position"
        class="stroke-danger"
        stroke-width="1"
        pointer-events="none"
      />
    </template>
  </svg>
</template>

<script setup lang="ts">
// Canevas de rendu (Phase 5, cycle 3) : lecture seule pour l'instant -- pas de sélection ni
// de déplacement d'élément (cycle 4). Panoramique (glisser sur le fond) et zoom (molette)
// seulement. Ne mute jamais `props.document` ; la caméra est un état purement local à ce
// composant, aucune commande n'est déclenchée ici (DiagramHistory n'entre en jeu qu'à partir
// du cycle où un geste modifie réellement le document).
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { createDefaultCamera, panBy, screenToWorld, zoomAt, type Camera } from './camera'
import { cullElements, elementBounds, getVisibleWorldBounds, type Bounds } from './viewport'
import { snapToGrid, computeAlignmentSnap, type AlignmentGuide } from './snapping'
import { DiagramHistory } from './history'
import { computeAnchorPoint } from './anchoring'
import { computeSiblingPosition, getAdjacentElementId } from './layout'
import type { DiagramDocumentV1, DiagramElement, LinkElement, ShapeElement } from './document'

const props = defineProps<{
  document: DiagramDocumentV1
  viewportWidth: number
  viewportHeight: number
}>()

const emit = defineEmits<{ 'update:document': [doc: DiagramDocumentV1] }>()

// Une seule commande par geste de glisser (cf. CONTEXT.md) : pas de flood de la pile
// d'annulation à chaque mousemove.
const history = new DiagramHistory()

const GRID_SIZE = 10
const ALIGN_THRESHOLD_PX = 6

const camera = ref<Camera>(createDefaultCamera())
const viewportSize = computed(() => ({ width: props.viewportWidth, height: props.viewportHeight }))
const selectedElementId = ref<string | null>(null)

const visibleElements = computed(() =>
  cullElements(props.document.elements, camera.value, viewportSize.value),
)

// Position "live" pendant un glisser actif : override d'affichage seulement, jamais écrit
// dans `props.document` avant la commande unique de fin de geste (cf. onElementMouseDown).
const dragPreview = ref<{ id: string; x: number; y: number } | null>(null)
const activeGuides = ref<AlignmentGuide[]>([])

const displayElements = computed(() =>
  visibleElements.value.map((el) =>
    dragPreview.value && dragPreview.value.id === el.id
      ? { ...el, x: dragPreview.value.x, y: dragPreview.value.y }
      : el,
  ),
)

const selectedElementBounds = computed(() => {
  if (!selectedElementId.value) return null
  const el = displayElements.value.find((e) => e.id === selectedElementId.value)
  return el ? elementBounds(el) : null
})

// Résout un id d'ancrage dans le document COMPLET (pas `visibleElements`) : un lien reste
// affiché même si l'une de ses formes est hors-champ (culling, cycle 3). Applique l'override
// de glisser en cours (Task 4, cycle 4) pour qu'un lien suive sa forme pendant le geste.
function resolveElement(id: string): DiagramElement | undefined {
  const el = props.document.elements.find((e) => e.id === id)
  if (!el) return undefined
  if (dragPreview.value && dragPreview.value.id === id) {
    return { ...el, x: dragPreview.value.x, y: dragPreview.value.y }
  }
  return el
}

interface RenderedLink {
  id: string
  points: string
  dashed: boolean
}

// Un lien dont fromId/toId ne résout à aucune forme (orpheline, cf. CONTEXT.md) est
// silencieusement ignoré -- pas d'exception, pas de tracé cassé.
const renderedLinks = computed<RenderedLink[]>(() => {
  const links: RenderedLink[] = []
  for (const el of props.document.elements) {
    if (el.kind !== 'link') continue
    const fromEl = resolveElement(el.fromId)
    const toEl = resolveElement(el.toId)
    if (!fromEl || !toEl) continue

    const fromBounds = elementBounds(fromEl)
    const toBounds = elementBounds(toEl)
    const fromCenter = {
      x: (fromBounds.minX + fromBounds.maxX) / 2,
      y: (fromBounds.minY + fromBounds.maxY) / 2,
    }
    const toCenter = {
      x: (toBounds.minX + toBounds.maxX) / 2,
      y: (toBounds.minY + toBounds.maxY) / 2,
    }
    const fromAnchor = computeAnchorPoint(fromBounds, toCenter)
    const toAnchor = computeAnchorPoint(toBounds, fromCenter)
    const points = [fromAnchor, ...el.routingPoints, toAnchor]

    links.push({
      id: el.id,
      points: points.map((p) => `${p.x},${p.y}`).join(' '),
      dashed: el.dashed,
    })
  }
  return links
})

const visibleWorldBounds = computed(() => getVisibleWorldBounds(camera.value, viewportSize.value))

const viewBoxString = computed(() => {
  const b = visibleWorldBounds.value
  return `${b.minX} ${b.minY} ${b.maxX - b.minX} ${b.maxY - b.minY}`
})

function onWheel(event: WheelEvent) {
  const factor = event.deltaY < 0 ? 1.1 : 1 / 1.1
  camera.value = zoomAt(
    camera.value,
    { x: event.offsetX, y: event.offsetY },
    factor,
    viewportSize.value,
  )
}

// Seuil (px écran) sous lequel un mousedown+mouseup est un clic (sélection/désélection),
// au-delà duquel c'est un geste (panoramique du fond, déplacement d'un élément -- cycle 4).
const CLICK_THRESHOLD_PX = 4

function onBackgroundMouseDown(event: MouseEvent) {
  const start = { x: event.clientX, y: event.clientY }
  let last = { ...start }
  let moved = false

  function onMove(e: MouseEvent) {
    if (!moved && Math.hypot(e.clientX - start.x, e.clientY - start.y) > CLICK_THRESHOLD_PX) {
      moved = true
    }
    if (moved) {
      camera.value = panBy(camera.value, e.clientX - last.x, e.clientY - last.y)
    }
    last = { x: e.clientX, y: e.clientY }
  }

  function onUp() {
    if (!moved) selectedElementId.value = null
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
  }

  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

function pointInBounds(point: { x: number; y: number }, bounds: Bounds): boolean {
  return (
    point.x >= bounds.minX &&
    point.x <= bounds.maxX &&
    point.y >= bounds.minY &&
    point.y <= bounds.maxY
  )
}

// Maj + glisser d'une forme vers une autre crée un lien (Task 3) -- réutilise la commande
// générique `add-element` du cycle 2, aucun nouveau type de commande nécessaire.
function startLinking(source: DiagramElement) {
  function onUp(e: MouseEvent) {
    window.removeEventListener('mouseup', onUp)
    const worldPoint = screenToWorld(
      { x: e.clientX, y: e.clientY },
      camera.value,
      viewportSize.value,
    )
    const target = props.document.elements.find(
      (el) => el.id !== source.id && pointInBounds(worldPoint, elementBounds(el)),
    )
    if (!target) return

    const newLink: LinkElement = {
      kind: 'link',
      id: `link-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      x: 0,
      y: 0,
      width: 0,
      height: 0,
      rotation: 0,
      locked: false,
      fromId: source.id,
      toId: target.id,
      label: '',
      arrow: 'end',
      dashed: false,
      routingPoints: [],
    }
    const newDoc = history.execute(props.document, { type: 'add-element', element: newLink })
    emit('update:document', newDoc)
  }

  window.addEventListener('mouseup', onUp)
}

function onElementMouseDown(event: MouseEvent, element: DiagramElement) {
  if (event.shiftKey) {
    startLinking(element)
    return
  }

  const start = { x: event.clientX, y: event.clientY }
  const originalX = element.x
  const originalY = element.y
  let moved = false
  let finalX = originalX
  let finalY = originalY

  function onMove(e: MouseEvent) {
    if (!moved && Math.hypot(e.clientX - start.x, e.clientY - start.y) > CLICK_THRESHOLD_PX) {
      moved = true
    }
    if (!moved) return

    const zoom = camera.value.zoom
    const rawX = originalX + (e.clientX - start.x) / zoom
    const rawY = originalY + (e.clientY - start.y) / zoom

    if (e.altKey) {
      finalX = rawX
      finalY = rawY
      activeGuides.value = []
    } else {
      const draggedBounds = {
        minX: rawX,
        minY: rawY,
        maxX: rawX + element.width,
        maxY: rawY + element.height,
      }
      const others = props.document.elements.filter((el) => el.id !== element.id).map(elementBounds)
      const { snapped, guides } = computeAlignmentSnap(
        draggedBounds,
        others,
        ALIGN_THRESHOLD_PX / zoom,
      )
      if (guides.length > 0) {
        finalX = snapped.x
        finalY = snapped.y
        activeGuides.value = guides
      } else {
        const gridSnapped = snapToGrid({ x: rawX, y: rawY }, GRID_SIZE)
        finalX = gridSnapped.x
        finalY = gridSnapped.y
        activeGuides.value = []
      }
    }
    dragPreview.value = { id: element.id, x: finalX, y: finalY }
  }

  function onUp() {
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
    selectedElementId.value = element.id
    dragPreview.value = null
    activeGuides.value = []
    if (!moved) return

    const newDoc = history.execute(props.document, {
      type: 'update-element',
      id: element.id,
      changes: { x: finalX, y: finalY },
    })
    emit('update:document', newDoc)
  }

  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

// Interactions clavier (Phase 5, cycle 6 -- §8.4). Raccourcis retenus dans CONTEXT.md :
// Entrée = créer un frère, Tab = créer un enfant, flèches = naviguer, Suppr = supprimer.
// Aucun n'agit sans sélection, sauf les flèches (sélectionnent le premier élément).
const SIBLING_GAP = 20

function createShapeNear(origin: ShapeElement): ShapeElement {
  const originBounds = elementBounds(origin)
  const otherBounds = props.document.elements.filter((el) => el.id !== origin.id).map(elementBounds)
  const size = { width: origin.width, height: origin.height }
  const pos = computeSiblingPosition(originBounds, otherBounds, SIBLING_GAP, size)
  return {
    kind: 'shape',
    id: `shape-${Date.now()}-${Math.random().toString(36).slice(2)}`,
    x: pos.x,
    y: pos.y,
    width: origin.width,
    height: origin.height,
    rotation: 0,
    locked: false,
    shape: origin.shape,
    label: '',
    color: origin.color,
  }
}

function onKeyDown(event: KeyboardEvent) {
  const selectedId = selectedElementId.value

  if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
    event.preventDefault()
    const direction = event.key === 'ArrowRight' ? 'next' : 'previous'
    const nextId = getAdjacentElementId(props.document.elements, selectedId, direction)
    if (nextId) selectedElementId.value = nextId
    return
  }

  if (!selectedId) return
  const selected = props.document.elements.find((el) => el.id === selectedId)
  if (!selected || selected.kind !== 'shape') return

  if (event.key === 'Enter') {
    event.preventDefault()
    const sibling = createShapeNear(selected)
    const newDoc = history.execute(props.document, { type: 'add-element', element: sibling })
    selectedElementId.value = sibling.id
    emit('update:document', newDoc)
    return
  }

  if (event.key === 'Tab') {
    event.preventDefault()
    const child = createShapeNear(selected)
    const docWithChild = history.execute(props.document, { type: 'add-element', element: child })
    const newLink: LinkElement = {
      kind: 'link',
      id: `link-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      x: 0,
      y: 0,
      width: 0,
      height: 0,
      rotation: 0,
      locked: false,
      fromId: selected.id,
      toId: child.id,
      label: '',
      arrow: 'end',
      dashed: false,
      routingPoints: [],
    }
    const docWithLink = history.execute(docWithChild, { type: 'add-element', element: newLink })
    selectedElementId.value = child.id
    emit('update:document', docWithLink)
    return
  }

  if (event.key === 'Delete' || event.key === 'Backspace') {
    event.preventDefault()
    const newDoc = history.execute(props.document, { type: 'remove-element', id: selected.id })
    selectedElementId.value = null
    emit('update:document', newDoc)
  }
}

onMounted(() => window.addEventListener('keydown', onKeyDown))
onUnmounted(() => window.removeEventListener('keydown', onKeyDown))

defineExpose({ camera, selectedElementId, history })
</script>
