import { describe, it, expect } from 'vitest'
import { createEmptyDocument, type DiagramDocumentV1, type DiagramElement } from '../../src/diagram/document'

describe('DiagramDocumentV1 — modèle de document (diagrammes-modele-document, Task 1)', () => {
  it('createEmptyDocument produit un document v1 valide et vide', () => {
    const doc: DiagramDocumentV1 = createEmptyDocument()
    expect(doc.schema_version).toBe(1)
    expect(doc.elements).toEqual([])
    expect(doc.backgroundImage).toBeNull()
  })

  // Le discriminant `kind` doit permettre un switch exhaustif au runtime (pas seulement
  // à la compilation) sur les 4 variantes du vocabulaire v1 (cf. CONTEXT.md).
  it('le discriminant kind distingue les 4 variantes de DiagramElement', () => {
    const elements: DiagramElement[] = [
      {
        kind: 'shape',
        id: 's1',
        x: 0,
        y: 0,
        width: 10,
        height: 10,
        rotation: 0,
        locked: false,
        shape: 'rect',
        label: 'A',
        color: '#fff',
      },
      {
        kind: 'link',
        id: 'l1',
        x: 0,
        y: 0,
        width: 0,
        height: 0,
        rotation: 0,
        locked: false,
        fromId: 's1',
        toId: 's2',
        label: '',
        arrow: 'end',
        dashed: false,
        routingPoints: [],
      },
      {
        kind: 'stroke',
        id: 'd1',
        x: 0,
        y: 0,
        width: 0,
        height: 0,
        rotation: 0,
        locked: false,
        points: [{ x: 0, y: 0 }],
        color: '#000',
        strokeWidth: 2,
      },
      {
        kind: 'occlusion-mask',
        id: 'm1',
        x: 0,
        y: 0,
        width: 10,
        height: 10,
        rotation: 0,
        locked: false,
        label: 'zone',
      },
    ]

    function describeKind(el: DiagramElement): string {
      switch (el.kind) {
        case 'shape':
          return `shape:${el.shape}`
        case 'link':
          return `link:${el.fromId}->${el.toId}`
        case 'stroke':
          return `stroke:${el.points.length}`
        case 'occlusion-mask':
          return `mask:${el.label}`
      }
    }

    expect(elements.map(describeKind)).toEqual([
      'shape:rect',
      'link:s1->s2',
      'stroke:1',
      'mask:zone',
    ])
  })
})
