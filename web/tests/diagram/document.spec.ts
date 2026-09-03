import { describe, it, expect } from 'vitest'
import {
  createEmptyDocument,
  parseDiagramDocument,
  serializeDiagramDocument,
  type DiagramDocumentV1,
  type DiagramElement,
} from '../../src/diagram/document'

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

describe('parseDiagramDocument / serializeDiagramDocument (Task 3)', () => {
  it('une chaîne vide, null ou undefined produit un document vide', () => {
    expect(parseDiagramDocument('')).toEqual(createEmptyDocument())
    expect(parseDiagramDocument(null)).toEqual(createEmptyDocument())
    expect(parseDiagramDocument(undefined)).toEqual(createEmptyDocument())
  })

  it('un JSON v1 valide est retourné tel quel', () => {
    const doc: DiagramDocumentV1 = {
      schema_version: 1,
      elements: [
        {
          kind: 'shape', id: 's1', x: 1, y: 2, width: 3, height: 4, rotation: 0,
          locked: false, shape: 'circle', label: 'A', color: '#fff',
        },
      ],
      backgroundImage: null,
    }
    expect(parseDiagramDocument(JSON.stringify(doc))).toEqual(doc)
  })

  it('un JSON v0 (sans schema_version, forme legacy reconnaissable) est migré', () => {
    const legacy = JSON.stringify({
      nodes: [{ id: 1, label: 'A', type: 'rect', x: 0, y: 0, color: '#fff' }],
      connections: [],
      masks: [],
      backgroundImage: null,
      drawings: [],
    })
    const parsed = parseDiagramDocument(legacy)
    expect(parsed.schema_version).toBe(1)
    expect(parsed.elements).toHaveLength(1)
    expect(parsed.elements[0].kind).toBe('shape')
  })

  it('un JSON invalide ou imprévu dégrade silencieusement vers un document vide', () => {
    expect(parseDiagramDocument('{ not json')).toEqual(createEmptyDocument())
    expect(parseDiagramDocument('42')).toEqual(createEmptyDocument())
    expect(parseDiagramDocument('null')).toEqual(createEmptyDocument())
  })

  it('rondtrip : parse(serialize(doc)) égale doc pour un document v1 non trivial', () => {
    const doc: DiagramDocumentV1 = {
      schema_version: 1,
      elements: [
        {
          kind: 'link', id: 'l1', x: 0, y: 0, width: 0, height: 0, rotation: 0,
          locked: false, fromId: 's1', toId: 's2', label: 'relie', arrow: 'both',
          dashed: true, routingPoints: [{ x: 5, y: 5 }],
        },
      ],
      backgroundImage: 'data:image/png;base64,AAAA',
    }
    expect(parseDiagramDocument(serializeDiagramDocument(doc))).toEqual(doc)
  })
})
