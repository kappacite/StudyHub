import { describe, it, expect } from 'vitest'
import { getVisibleWorldBounds, elementBounds, cullElements } from '../../src/diagram/viewport'
import type { ShapeElement } from '../../src/diagram/document'

const VIEWPORT = { width: 800, height: 600 }

function shape(id: string, x: number, y: number, width = 50, height = 50): ShapeElement {
  return { kind: 'shape', id, x, y, width, height, rotation: 0, locked: false, shape: 'rect', label: '', color: '#fff' }
}

describe('viewport (diagrammes-canevas-pan-zoom, Task 3)', () => {
  it('getVisibleWorldBounds à la caméra par défaut couvre le viewport centré sur l\'origine', () => {
    const bounds = getVisibleWorldBounds({ x: 0, y: 0, zoom: 1 }, VIEWPORT)
    expect(bounds).toEqual({ minX: -400, minY: -300, maxX: 400, maxY: 300 })
  })

  it('un zoom plus fort réduit la zone visible en coordonnées monde', () => {
    const zoomedOut = getVisibleWorldBounds({ x: 0, y: 0, zoom: 1 }, VIEWPORT)
    const zoomedIn = getVisibleWorldBounds({ x: 0, y: 0, zoom: 2 }, VIEWPORT)
    const widthOut = zoomedOut.maxX - zoomedOut.minX
    const widthIn = zoomedIn.maxX - zoomedIn.minX
    expect(widthIn).toBeCloseTo(widthOut / 2, 6)
  })

  it('elementBounds calcule la boîte englobante depuis x/y/width/height', () => {
    expect(elementBounds(shape('a', 10, 20, 30, 40))).toEqual({ minX: 10, minY: 20, maxX: 40, maxY: 60 })
  })

  describe('cullElements', () => {
    const camera = { x: 0, y: 0, zoom: 1 } // visible: [-400,400] x [-300,300]

    it('exclut un élément entièrement hors-champ', () => {
      const far = shape('far', 10000, 10000)
      expect(cullElements([far], camera, VIEWPORT)).toEqual([])
    })

    it('conserve un élément partiellement chevauchant la fenêtre de vue', () => {
      const edge = shape('edge', 380, 0, 100, 100) // déborde de minX=380 à maxX=480, hors de 400
      expect(cullElements([edge], camera, VIEWPORT).map((e) => e.id)).toEqual(['edge'])
    })

    it('conserve un élément entièrement dans la fenêtre de vue', () => {
      const inside = shape('inside', 0, 0)
      expect(cullElements([inside], camera, VIEWPORT).map((e) => e.id)).toEqual(['inside'])
    })

    it('un document vide ne casse rien', () => {
      expect(cullElements([], camera, VIEWPORT)).toEqual([])
    })

    it('un zoom réduit élargit la zone visible, incluant des éléments auparavant hors-champ', () => {
      const far = shape('far', 1000, 0, 10, 10)
      const zoomedOutCamera = { x: 0, y: 0, zoom: 0.1 }
      expect(cullElements([far], camera, VIEWPORT)).toEqual([])
      expect(cullElements([far], zoomedOutCamera, VIEWPORT).map((e) => e.id)).toEqual(['far'])
    })
  })
})
