<template>
  <svg
    class="w-full h-full touch-none select-none"
    :viewBox="viewBoxString"
    @wheel.prevent="onWheel"
    @mousedown="onBackgroundMouseDown"
  >
    <g
      v-for="el in visibleElements"
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
import { cullElements, getVisibleWorldBounds } from './viewport'
import type { DiagramDocumentV1, DiagramElement } from './document'

const props = defineProps<{
  document: DiagramDocumentV1
  viewportWidth: number
  viewportHeight: number
}>()

const camera = ref<Camera>(createDefaultCamera())
const viewportSize = computed(() => ({ width: props.viewportWidth, height: props.viewportHeight }))

const visibleElements = computed(() =>
  cullElements(props.document.elements, camera.value, viewportSize.value),
)

const viewBoxString = computed(() => {
  const b = getVisibleWorldBounds(camera.value, viewportSize.value)
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

const selectedElementId = ref<string | null>(null)

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
  let moved = false

  function onMove(e: MouseEvent) {
    if (!moved && Math.hypot(e.clientX - start.x, e.clientY - start.y) > CLICK_THRESHOLD_PX) {
      moved = true
    }
  }

  function onUp() {
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
    selectedElementId.value = element.id
  }

  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

defineExpose({ camera, selectedElementId })
</script>
