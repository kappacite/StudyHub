// Rendu borné à la fenêtre de vue (Phase 5, cycle 3 -- §8.6 : « un canevas infini impose de
// ne rendre que ce qui est visible »). Fonctions pures sur des coordonnées (§8.7).

import { screenToWorld, type Camera, type ViewportSize } from './camera'
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
