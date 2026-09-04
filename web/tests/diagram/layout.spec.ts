import { describe, it, expect } from 'vitest'
import { computeSiblingPosition, getAdjacentElementId } from '../../src/diagram/layout'
import type { Bounds } from '../../src/diagram/viewport'
import type { ShapeElement } from '../../src/diagram/document'

function shapeEl(id: string): ShapeElement {
  return { kind: 'shape', id, x: 0, y: 0, width: 50, height: 50, rotation: 0, locked: false, shape: 'rect', label: id, color: '#fff' }
}

function bounds(minX: number, minY: number, width = 50, height = 50): Bounds {
  return { minX, minY, maxX: minX + width, maxY: minY + height }
}

const SIZE = { width: 50, height: 50 }

function overlaps(a: Bounds, b: Bounds): boolean {
  return a.minX < b.maxX && a.maxX > b.minX && a.minY < b.maxY && a.maxY > b.minY
}

describe('computeSiblingPosition (diagrammes-interactions-clavier, Task 1)', () => {
  it("aucune forme existante -> position immédiatement à droite de l'origine", () => {
    const origin = bounds(0, 0)
    expect(computeSiblingPosition(origin, [], 20, SIZE)).toEqual({ x: 70, y: 0 })
  })

  it('une forme déjà présente à la position candidate -> décalée sans chevauchement', () => {
    const origin = bounds(0, 0)
    const occupying = bounds(70, 0) // exactement la position candidate par défaut
    const pos = computeSiblingPosition(origin, [occupying], 20, SIZE)
    const newBounds = { minX: pos.x, minY: pos.y, maxX: pos.x + SIZE.width, maxY: pos.y + SIZE.height }
    expect(overlaps(newBounds, occupying)).toBe(false)
  })

  it("plusieurs formes en chaîne -> la nouvelle position ne chevauche aucune d'entre elles", () => {
    const origin = bounds(0, 0)
    const chain = [bounds(70, 0), bounds(140, 0), bounds(210, 0)]
    const pos = computeSiblingPosition(origin, chain, 20, SIZE)
    const newBounds = { minX: pos.x, minY: pos.y, maxX: pos.x + SIZE.width, maxY: pos.y + SIZE.height }
    for (const b of chain) {
      expect(overlaps(newBounds, b)).toBe(false)
    }
  })
})

describe('getAdjacentElementId (diagrammes-interactions-clavier, Task 2)', () => {
  const three = [shapeEl('a'), shapeEl('b'), shapeEl('c')]

  it('suivant/précédent sur une liste de 3 -> ordre attendu', () => {
    expect(getAdjacentElementId(three, 'a', 'next')).toBe('b')
    expect(getAdjacentElementId(three, 'b', 'next')).toBe('c')
    expect(getAdjacentElementId(three, 'b', 'previous')).toBe('a')
  })

  it('suivant depuis le dernier élément revient au premier (cyclique)', () => {
    expect(getAdjacentElementId(three, 'c', 'next')).toBe('a')
    expect(getAdjacentElementId(three, 'a', 'previous')).toBe('c')
  })

  it('currentId absent -> sélectionne le premier élément', () => {
    expect(getAdjacentElementId(three, null, 'next')).toBe('a')
    expect(getAdjacentElementId(three, 'inexistant', 'next')).toBe('a')
  })

  it('liste vide -> null, pas d\'exception', () => {
    expect(getAdjacentElementId([], null, 'next')).toBeNull()
  })
})
