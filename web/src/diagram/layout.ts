// Placement automatique et navigation (Phase 5, cycle 6 -- §8.4/§8.7). Fonctions pures.

import type { Point } from './camera'
import type { Bounds } from './viewport'
import type { DiagramElement } from './document'

interface Size {
  width: number
  height: number
}

function overlaps(a: Bounds, b: Bounds): boolean {
  return a.minX < b.maxX && a.maxX > b.minX && a.minY < b.maxY && a.maxY > b.minY
}

// Position d'un nouvel élément (« créer un frère/enfant », §8.4) : immédiatement à droite de
// l'origine, décalée par incréments tant qu'elle chevauche une forme existante. Algorithme
// volontairement simple (une seule direction) -- cf. CONTEXT.md, suffisant pour l'exigence
// « sans chevauchement », le rangement fin relève du cycle 9.
export function computeSiblingPosition(
  originBounds: Bounds,
  existingBounds: Bounds[],
  gap: number,
  newSize: Size,
): Point {
  let x = originBounds.maxX + gap
  const y = originBounds.minY

  while (true) {
    const candidate: Bounds = {
      minX: x,
      minY: y,
      maxX: x + newSize.width,
      maxY: y + newSize.height,
    }
    const blocking = existingBounds.find((b) => overlaps(candidate, b))
    if (!blocking) return { x, y }
    x = blocking.maxX + gap
  }
}

export type NavigationDirection = 'next' | 'previous'

// Navigation cyclique entre formes (§8.4) dans l'ordre du tableau -- pas de navigation
// spatiale, suffisant pour ce cycle.
export function getAdjacentElementId(
  elements: DiagramElement[],
  currentId: string | null,
  direction: NavigationDirection,
): string | null {
  const shapes = elements.filter((el) => el.kind === 'shape')
  if (shapes.length === 0) return null

  const currentIndex = shapes.findIndex((el) => el.id === currentId)
  if (currentIndex === -1) return shapes[0].id

  const delta = direction === 'next' ? 1 : -1
  const nextIndex = (currentIndex + delta + shapes.length) % shapes.length
  return shapes[nextIndex].id
}
