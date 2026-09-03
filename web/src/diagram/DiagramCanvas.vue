<template>
  <svg
    class="w-full h-full touch-none select-none"
    :viewBox="viewBoxString"
    @wheel.prevent="onWheel"
    @mousedown="onBackgroundMouseDown"
  >
    <g v-for="el in visibleElements" :key="el.id" data-test="diagram-element" :data-id="el.id">
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
import type { DiagramDocumentV1 } from './document'

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

const isPanning = ref(false)
let lastPointer = { x: 0, y: 0 }

function onBackgroundMouseDown(event: MouseEvent) {
  isPanning.value = true
  lastPointer = { x: event.clientX, y: event.clientY }
  window.addEventListener('mousemove', onPanMouseMove)
  window.addEventListener('mouseup', onPanMouseUp)
}

function onPanMouseMove(event: MouseEvent) {
  if (!isPanning.value) return
  const dx = event.clientX - lastPointer.x
  const dy = event.clientY - lastPointer.y
  lastPointer = { x: event.clientX, y: event.clientY }
  camera.value = panBy(camera.value, dx, dy)
}

function onPanMouseUp() {
  isPanning.value = false
  window.removeEventListener('mousemove', onPanMouseMove)
  window.removeEventListener('mouseup', onPanMouseUp)
}

defineExpose({ camera })
</script>
