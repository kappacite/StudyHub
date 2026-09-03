import { describe, it, expect } from 'vitest'
import { snapToGrid, computeAlignmentSnap } from '../../src/diagram/snapping'
import type { Bounds } from '../../src/diagram/viewport'

function bounds(minX: number, minY: number, size = 50): Bounds {
  return { minX, minY, maxX: minX + size, maxY: minY + size }
}

describe('snapToGrid (diagrammes-placement-selection, Task 1)', () => {
  it('un point déjà sur la grille reste inchangé', () => {
    expect(snapToGrid({ x: 20, y: 30 }, 10)).toEqual({ x: 20, y: 30 })
  })

  it('un point à mi-chemin arrondit au plus proche', () => {
    expect(snapToGrid({ x: 24, y: 26 }, 10)).toEqual({ x: 20, y: 30 })
  })

  it('une grille de taille 1 est un no-op', () => {
    expect(snapToGrid({ x: 12.3, y: -7.8 }, 1)).toEqual({ x: 12, y: -8 })
  })

  it('un point négatif arrondit correctement', () => {
    expect(snapToGrid({ x: -24, y: -26 }, 10)).toEqual({ x: -20, y: -30 })
  })
})

describe('computeAlignmentSnap (diagrammes-placement-selection, Task 2)', () => {
  it('aligne le bord gauche sur un voisin proche', () => {
    const dragged = bounds(102, 500) // loin en Y pour ne pas aussi matcher sur l'axe Y
    const other = bounds(100, 0)
    const { snapped, guides } = computeAlignmentSnap(dragged, [other], 5)
    expect(snapped.x).toBe(100)
    expect(guides.some((g) => g.axis === 'x' && g.position === 100)).toBe(true)
  })

  it("aucun voisin dans le seuil ne produit aucun snap", () => {
    const dragged = bounds(200, 500)
    const other = bounds(100, 0)
    const { snapped, guides } = computeAlignmentSnap(dragged, [other], 5)
    expect(snapped).toEqual({ x: 200, y: 500 })
    expect(guides).toEqual([])
  })

  it('avec plusieurs voisins candidats, le plus proche gagne', () => {
    const dragged = bounds(103, 500)
    const near = bounds(100, 0) // distance 3
    const far = bounds(110, 0) // distance 7, aussi dans un seuil large mais plus loin
    const { snapped } = computeAlignmentSnap(dragged, [far, near], 10)
    expect(snapped.x).toBe(100)
  })
})
