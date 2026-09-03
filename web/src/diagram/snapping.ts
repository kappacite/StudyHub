// Magnétisme et guides d'alignement (Phase 5, cycle 4 -- §8.4/§8.7). Fonctions pures sur des
// coordonnées, sans DOM ni canevas.

import type { Point } from './camera'
import type { Bounds } from './viewport'

export function snapToGrid(point: Point, gridSize: number): Point {
  return {
    x: Math.round(point.x / gridSize) * gridSize,
    y: Math.round(point.y / gridSize) * gridSize,
  }
}

export interface AlignmentGuide {
  axis: 'x' | 'y'
  position: number
}

interface AxisCandidate {
  delta: number
  distance: number
  position: number
}

function edgesX(b: Bounds): number[] {
  return [b.minX, (b.minX + b.maxX) / 2, b.maxX]
}

function edgesY(b: Bounds): number[] {
  return [b.minY, (b.minY + b.maxY) / 2, b.maxY]
}

function bestAxisMatch(
  draggedEdges: number[],
  otherEdges: number[],
  threshold: number,
  current: AxisCandidate | null,
): AxisCandidate | null {
  let best = current
  for (const de of draggedEdges) {
    for (const oe of otherEdges) {
      const distance = Math.abs(de - oe)
      if (distance <= threshold && (!best || distance < best.distance)) {
        best = { delta: oe - de, distance, position: oe }
      }
    }
  }
  return best
}

// Aligne le bord/centre gauche-droite-haut-bas de l'élément déplacé sur celui du voisin le
// plus proche, sur chaque axe indépendamment, dans un seuil donné (en unités monde -- au
//'appelant de convertir un seuil en pixels-écran selon le zoom courant). Le voisin le plus
// proche gagne quand plusieurs sont dans le seuil ; aucun snap si aucun voisin n'est assez
// proche sur cet axe.
export function computeAlignmentSnap(
  draggedBounds: Bounds,
  otherBounds: Bounds[],
  thresholdWorld: number,
): { snapped: Point; guides: AlignmentGuide[] } {
  let bestX: AxisCandidate | null = null
  let bestY: AxisCandidate | null = null

  for (const other of otherBounds) {
    bestX = bestAxisMatch(edgesX(draggedBounds), edgesX(other), thresholdWorld, bestX)
    bestY = bestAxisMatch(edgesY(draggedBounds), edgesY(other), thresholdWorld, bestY)
  }

  const snapped: Point = {
    x: draggedBounds.minX + (bestX?.delta ?? 0),
    y: draggedBounds.minY + (bestY?.delta ?? 0),
  }
  const guides: AlignmentGuide[] = []
  if (bestX) guides.push({ axis: 'x', position: bestX.position })
  if (bestY) guides.push({ axis: 'y', position: bestY.position })

  return { snapped, guides }
}
