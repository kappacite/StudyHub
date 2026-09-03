// Rendu borné à la fenêtre de vue (Phase 5, cycle 3 -- §8.6 : « un canevas infini impose de
// ne rendre que ce qui est visible »). Fonctions pures sur des coordonnées (§8.7).

import { createDefaultCamera, screenToWorld, type Camera, type ViewportSize } from './camera'
import type { DiagramElement } from './document'

export interface Bounds {
  minX: number
  minY: number
  maxX: number
  maxY: number
}

export function getVisibleWorldBounds(camera: Camera, viewport: ViewportSize): Bounds {
  const topLeft = screenToWorld({ x: 0, y: 0 }, camera, viewport)
  const bottomRight = screenToWorld({ x: viewport.width, y: viewport.height }, camera, viewport)
  return { minX: topLeft.x, minY: topLeft.y, maxX: bottomRight.x, maxY: bottomRight.y }
}

export function elementBounds(element: DiagramElement): Bounds {
  return {
    minX: element.x,
    minY: element.y,
    maxX: element.x + element.width,
    maxY: element.y + element.height,
  }
}

function boundsIntersect(a: Bounds, b: Bounds): boolean {
  return a.minX <= b.maxX && a.maxX >= b.minX && a.minY <= b.maxY && a.maxY >= b.minY
}

// Intersection, pas inclusion stricte : un élément partiellement visible reste affiché,
// sans quoi une forme à cheval sur le bord de l'écran disparaîtrait brutalement.
export function cullElements(
  elements: DiagramElement[],
  camera: Camera,
  viewport: ViewportSize,
): DiagramElement[] {
  const visible = getVisibleWorldBounds(camera, viewport)
  return elements.filter((el) => boundsIntersect(elementBounds(el), visible))
}

const FIT_MARGIN = 40
const MIN_CONTENT_SIZE = 1 // évite une division par zéro sur un contenu de taille nulle

// « Recadrer sur tout » (§8.4) : la caméra qui centre l'intégralité du contenu dans la
// fenêtre de vue, avec une marge. Document vide -> caméra par défaut (pas de boîte
// englobante à calculer).
export function computeFitToContent(elements: DiagramElement[], viewport: ViewportSize): Camera {
  if (elements.length === 0) return createDefaultCamera()

  const boxes = elements.map(elementBounds)
  const minX = Math.min(...boxes.map((b) => b.minX))
  const minY = Math.min(...boxes.map((b) => b.minY))
  const maxX = Math.max(...boxes.map((b) => b.maxX))
  const maxY = Math.max(...boxes.map((b) => b.maxY))

  const contentWidth = Math.max(maxX - minX, MIN_CONTENT_SIZE) + FIT_MARGIN * 2
  const contentHeight = Math.max(maxY - minY, MIN_CONTENT_SIZE) + FIT_MARGIN * 2

  const zoom = Math.min(viewport.width / contentWidth, viewport.height / contentHeight)

  return { x: (minX + maxX) / 2, y: (minY + maxY) / 2, zoom }
}
