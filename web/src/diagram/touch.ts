// Géométrie tactile (Phase 5, cycle 7 -- §8.7, fonctions pures).

import type { Point } from './camera'

export function computeDistance(p1: Point, p2: Point): number {
  return Math.hypot(p2.x - p1.x, p2.y - p1.y)
}

export function computeMidpoint(p1: Point, p2: Point): Point {
  return { x: (p1.x + p2.x) / 2, y: (p1.y + p2.y) / 2 }
}
