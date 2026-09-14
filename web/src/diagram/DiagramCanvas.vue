<template>
  <svg
    class="w-full h-full touch-none select-none"
    :viewBox="viewBoxString"
    @wheel.prevent="onWheel"
    @mousedown="onBackgroundMouseDown"
    @touchstart.prevent="onBackgroundTouchStart"
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
      @touchstart.stop.prevent="onElementTouchStart($event, el)"
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

    <line
      v-if="isCreatingLink && phantomLinkStart && linkTargetPoint"
      data-test="phantom-link"
      :x1="phantomLinkStart.x"
      :y1="phantomLinkStart.y"
      :x2="linkTargetPoint.x"
      :y2="linkTargetPoint.y"
      class="stroke-ink"
      stroke-width="2"
      stroke-dasharray="4"
    />

    <foreignObject
      v-if="renamingBounds"
      :x="renamingBounds.minX"
      :y="renamingBounds.minY"
      :width="renamingBounds.maxX - renamingBounds.minX"
      :height="renamingBounds.maxY - renamingBounds.minY"
    >
      <input
        v-model="renameBuffer"
        data-test="rename-input"
        class="w-full h-full"
        @keydown.enter.stop="commitRename"
        @keydown.esc.stop="cancelRename"
        @keydown.stop
      />
    </foreignObject>
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
import { computeDistance, computeMidpoint } from './touch'
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

const isCreatingLink = ref(false)
const linkStartElement = ref<DiagramElement | null>(null)
const linkTargetPoint = ref<{ x: number, y: number } | null>(null)

const phantomLinkStart = computed(() => {
  if (!linkStartElement.value) return null
  const b = elementBounds(linkStartElement.value)
  return {
    x: (b.minX + b.maxX) / 2,
    y: (b.minY + b.maxY) / 2,
  }
})

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

// Renommage (F2, cycle 6) : aucune édition de texte en place n'existe encore pour le
// libellé d'une forme -- entrée de texte HTML superposée via <foreignObject>, cf. CONTEXT.md.
const renamingElementId = ref<string | null>(null)
const renameBuffer = ref('')

const renamingBounds = computed(() => {
  if (!renamingElementId.value) return null
  const el = props.document.elements.find((e) => e.id === renamingElementId.value)
  return el ? elementBounds(el) : null
})

function commitRename() {
  if (!renamingElementId.value) return
  const id = renamingElementId.value
  const newDoc = history.execute(props.document, {
    type: 'update-element',
    id,
    changes: { label: renameBuffer.value },
  })
  renamingElementId.value = null
  emit('update:document', newDoc)
}

function cancelRename() {
  renamingElementId.value = null
}

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

// Glisser à un doigt = panoramique du fond (Task 2, cycle 7) -- même seuil clic/glisser que
// la souris. Répartiteur `onBackgroundTouchStart` : une nouvelle touche (donc un nouveau
// `touchstart`) annule le geste précédent avant d'en démarrer un autre, pour permettre la
// transition 1 doigt (panoramique) -> 2 doigts (pincement, Task 3) sans état incohérent.
let activeTouchCleanup: (() => void) | null = null

function startBackgroundPanTouch(touch: Touch): () => void {
  const start = { x: touch.clientX, y: touch.clientY }
  let last = { ...start }
  let moved = false

  function onMove(e: TouchEvent) {
    if (e.touches.length !== 1) return
    const t = e.touches[0]
    if (!moved && Math.hypot(t.clientX - start.x, t.clientY - start.y) > CLICK_THRESHOLD_PX) {
      moved = true
    }
    if (moved) {
      camera.value = panBy(camera.value, t.clientX - last.x, t.clientY - last.y)
    }
    last = { x: t.clientX, y: t.clientY }
  }

  function onEnd() {
    if (!moved) selectedElementId.value = null
    cleanup()
  }

  function cleanup() {
    window.removeEventListener('touchmove', onMove)
    window.removeEventListener('touchend', onEnd)
  }

  window.addEventListener('touchmove', onMove)
  window.addEventListener('touchend', onEnd)
  return cleanup
}

// Pincer pour zoomer (Task 3, cycle 7) : recalcule le zoom de façon incrémentale (ratio de
// distance depuis le dernier `touchmove`, pas depuis le début du geste) et recentre sur le
// point médian courant à chaque mouvement -- supporte naturellement un panoramique simultané
// au pincement (le médian peut se déplacer pendant que la distance change).
function touchPoint(touch: Touch): { x: number; y: number } {
  return { x: touch.clientX, y: touch.clientY }
}

function startPinchZoomTouch(touchA: Touch, touchB: Touch): () => void {
  let lastDistance = computeDistance(touchPoint(touchA), touchPoint(touchB))

  function onMove(e: TouchEvent) {
    if (e.touches.length !== 2) return
    const a = touchPoint(e.touches[0])
    const b = touchPoint(e.touches[1])
    const distance = computeDistance(a, b)
    const midpoint = computeMidpoint(a, b)
    const factor = distance / lastDistance
    camera.value = zoomAt(camera.value, midpoint, factor, viewportSize.value)
    lastDistance = distance
  }

  function onEnd() {
    cleanup()
  }

  function cleanup() {
    window.removeEventListener('touchmove', onMove)
    window.removeEventListener('touchend', onEnd)
  }

  window.addEventListener('touchmove', onMove)
  window.addEventListener('touchend', onEnd)
  return cleanup
}

function onBackgroundTouchStart(event: TouchEvent) {
  activeTouchCleanup?.()
  activeTouchCleanup = null

  if (event.touches.length === 1) {
    activeTouchCleanup = startBackgroundPanTouch(event.touches[0])
  } else if (event.touches.length === 2) {
    activeTouchCleanup = startPinchZoomTouch(event.touches[0], event.touches[1])
  }
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
// Complète une création de lien vers l'élément sous `screenPoint`, s'il y en a un -- partagé
// entre `startLinking` (souris, Maj+glisser) et `startLinkingTouch` (tactile, appui long,
// Task 4 du cycle 7), pas de duplication de cette logique entre les deux entrées.
function completeLinkAt(source: DiagramElement, screenPoint: { x: number; y: number }) {
  const worldPoint = screenToWorld(screenPoint, camera.value, viewportSize.value)
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

function startLinking(source: DiagramElement) {
  function onUp(e: MouseEvent) {
    window.removeEventListener('mouseup', onUp)
    completeLinkAt(source, { x: e.clientX, y: e.clientY })
  }

  window.addEventListener('mouseup', onUp)
}

// Appui long sur un élément = équivalent tactile de Maj + glisser (Task 4, cycle 7) -- aucune
// touche modificatrice possible au doigt.
const LONG_PRESS_MS = 500

// Position d'un élément déplacé, magnétisée sauf demande explicite de l'appelant (souris :
// Alt maintenu ; réutilisé tel quel par le glisser tactile, Task 2 du cycle 7 -- pas de
// duplication de la décision alignement/grille entre souris et tactile).
function computeSnappedElementPosition(
  element: DiagramElement,
  originalX: number,
  originalY: number,
  dxScreen: number,
  dyScreen: number,
  disableSnap: boolean,
): { x: number; y: number; guides: AlignmentGuide[] } {
  const zoom = camera.value.zoom
  const rawX = originalX + dxScreen / zoom
  const rawY = originalY + dyScreen / zoom

  if (disableSnap) return { x: rawX, y: rawY, guides: [] }

  const draggedBounds = {
    minX: rawX,
    minY: rawY,
    maxX: rawX + element.width,
    maxY: rawY + element.height,
  }
  const others = props.document.elements.filter((el) => el.id !== element.id).map(elementBounds)
  const { snapped, guides } = computeAlignmentSnap(draggedBounds, others, ALIGN_THRESHOLD_PX / zoom)
  if (guides.length > 0) return { x: snapped.x, y: snapped.y, guides }

  const gridSnapped = snapToGrid({ x: rawX, y: rawY }, GRID_SIZE)
  return { x: gridSnapped.x, y: gridSnapped.y, guides: [] }
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

    const result = computeSnappedElementPosition(
      element,
      originalX,
      originalY,
      e.clientX - start.x,
      e.clientY - start.y,
      e.altKey,
    )
    finalX = result.x
    finalY = result.y
    activeGuides.value = result.guides
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

// Glisser à un doigt sur un élément = déplacement (Task 2, cycle 7) -- réutilise
// `computeSnappedElementPosition` (aucune duplication de la décision de magnétisme avec la
// souris). Une seule commande à la levée du doigt, comme la souris (cycle 4).
function onElementTouchStart(event: TouchEvent, element: DiagramElement) {
  if (event.touches.length !== 1) return

  const touch = event.touches[0]
  const start = { x: touch.clientX, y: touch.clientY }
  const originalX = element.x
  const originalY = element.y
  let moved = false
  let finalX = originalX
  let finalY = originalY

  let longPressTimer: ReturnType<typeof setTimeout> | null = setTimeout(() => {
    isCreatingLink.value = true
    linkStartElement.value = element
    linkTargetPoint.value = screenToWorld({ x: start.x, y: start.y }, camera.value, viewportSize.value)
    longPressTimer = null
  }, LONG_PRESS_MS)

  function clearTimer() {
    if (longPressTimer) {
      clearTimeout(longPressTimer)
      longPressTimer = null
    }
  }

  function onMove(e: TouchEvent) {
    if (e.touches.length !== 1) return
    const t = e.touches[0]
    
    if (isCreatingLink.value) {
      linkTargetPoint.value = screenToWorld({ x: t.clientX, y: t.clientY }, camera.value, viewportSize.value)
      return
    }

    if (!moved && Math.hypot(t.clientX - start.x, t.clientY - start.y) > CLICK_THRESHOLD_PX) {
      moved = true
      clearTimer()
    }
    if (!moved) return

    const result = computeSnappedElementPosition(
      element,
      originalX,
      originalY,
      t.clientX - start.x,
      t.clientY - start.y,
      false,
    )
    finalX = result.x
    finalY = result.y
    activeGuides.value = result.guides
    dragPreview.value = { id: element.id, x: finalX, y: finalY }
  }

  function onEnd(e: TouchEvent) {
    window.removeEventListener('touchmove', onMove)
    window.removeEventListener('touchend', onEnd)
    clearTimer()

    if (isCreatingLink.value) {
      const t = e.changedTouches[0]
      completeLinkAt(element, { x: t.clientX, y: t.clientY })
      isCreatingLink.value = false
      linkStartElement.value = null
      linkTargetPoint.value = null
      return
    }

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

  window.addEventListener('touchmove', onMove)
  window.addEventListener('touchend', onEnd)
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
  if (renamingElementId.value) return // l'entrée de renommage gère ses propres touches (@keydown.stop)

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

  if (event.key === 'F2') {
    event.preventDefault()
    renamingElementId.value = selected.id
    renameBuffer.value = selected.label
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
