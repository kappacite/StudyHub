// Ancrage de lien (Phase 5, cycle 5 -- §8.7, fonction pure). Simplification assumée
// (cf. CONTEXT.md du chantier) : ancrage sur le rectangle englobant pour toutes les formes,
// y compris cercle/ellipse -- pas d'intersection elliptique précise.

import type { Point } from './camera'
import type { Bounds } from './viewport'

// Point où le rayon partant du centre de `bounds` vers `towardPoint` croise son rectangle
// englobant. `towardPoint` = centre exact -> dégénère proprement vers le centre (pas de NaN).
export function computeAnchorPoint(bounds: Bounds, towardPoint: Point): Point {
  const cx = (bounds.minX + bounds.maxX) / 2
  const cy = (bounds.minY + bounds.maxY) / 2
  const dx = towardPoint.x - cx
  const dy = towardPoint.y - cy

  if (dx === 0 && dy === 0) return { x: cx, y: cy }

  const halfW = (bounds.maxX - bounds.minX) / 2
  const halfH = (bounds.maxY - bounds.minY) / 2
  const scale = Math.min(halfW / Math.abs(dx), halfH / Math.abs(dy))

  return { x: cx + dx * scale, y: cy + dy * scale }
}
