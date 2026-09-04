import { describe, it, expect } from 'vitest'
import { computeAnchorPoint } from '../../src/diagram/anchoring'

const SQUARE = { minX: 0, minY: 0, maxX: 100, maxY: 100 } // centre (50,50), demi-côté 50

describe('computeAnchorPoint (diagrammes-liens-ancrage, Task 1)', () => {
  it('cible directement à droite -> ancrage au milieu du bord droit', () => {
    expect(computeAnchorPoint(SQUARE, { x: 500, y: 50 })).toEqual({ x: 100, y: 50 })
  })

  it('cible directement au-dessus -> ancrage au milieu du bord haut', () => {
    expect(computeAnchorPoint(SQUARE, { x: 50, y: -500 })).toEqual({ x: 50, y: 0 })
  })

  it('cible = centre exact -> retourne le centre sans NaN', () => {
    expect(computeAnchorPoint(SQUARE, { x: 50, y: 50 })).toEqual({ x: 50, y: 50 })
  })

  it('cible en diagonale à 45° sur un carré -> ancrage exactement au coin', () => {
    const anchor = computeAnchorPoint(SQUARE, { x: 500, y: 500 })
    expect(anchor.x).toBeCloseTo(100, 6)
    expect(anchor.y).toBeCloseTo(100, 6)
  })
})
