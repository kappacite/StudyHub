<template>
  <svg
    class="w-full h-full touch-none select-none"
    :viewBox="viewBoxString"
    @wheel.prevent="onWheel"
    @mousedown="onBackgroundMouseDown"
  >
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
import { ref, computed } from 'vue'
import { createDefaultCamera, panBy, zoomAt, type Camera } from './camera'
import { cullElements, elementBounds, getVisibleWorldBounds } from './viewport'
import { snapToGrid, computeAlignmentSnap, type AlignmentGuide } from './snapping'
import { DiagramHistory } from './history'
import type { DiagramDocumentV1, DiagramElement } from './document'

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

function onElementMouseDown(event: MouseEvent, element: DiagramElement) {
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

defineExpose({ camera, selectedElementId, history })
</script>
