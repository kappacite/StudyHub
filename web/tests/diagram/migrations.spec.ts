import { describe, it, expect } from 'vitest'
import { migrateLegacyV0ToV1 } from '../../src/diagram/migrations'

// Forme v0 réelle produite par Diagrams.vue (ad hoc, non versionnée) --
// cf. workflow/diagrammes-modele-document/CONTEXT.md pour le détail.
function legacyDoc(overrides: Record<string, unknown> = {}) {
  return {
    nodes: [{ id: 1, label: 'Concept A', type: 'rect', x: 10, y: 20, color: '#6366f1' }],
    connections: [{ from: 1, to: 2, label: 'mène à', arrow: 'end', dashed: false }],
    masks: [{ id: 'mask-1700000000000', x: 5, y: 5, width: 40, height: 30, label: 'Zone cachée' }],
    backgroundImage: 'data:image/png;base64,AAAA',
    drawings: [{ id: 'stroke-abc', points: [{ x: 0, y: 0 }, { x: 5, y: 5 }], color: '#ef4444', width: 3 }],
    ...overrides,
  }
}

describe('migrateLegacyV0ToV1 (diagrammes-modele-document, Task 2)', () => {
  it('migre un document v0 complet sans perte de donnée', () => {
    const v1 = migrateLegacyV0ToV1(legacyDoc())

    expect(v1.schema_version).toBe(1)
    expect(v1.backgroundImage).toBe('data:image/png;base64,AAAA')

    const shape = v1.elements.find((e) => e.kind === 'shape')
    expect(shape).toMatchObject({
      kind: 'shape', shape: 'rect', label: 'Concept A', x: 10, y: 20, color: '#6366f1',
    })

    const link = v1.elements.find((e) => e.kind === 'link')
    expect(link).toMatchObject({
      kind: 'link', label: 'mène à', arrow: 'end', dashed: false, routingPoints: [],
    })
    // Le lien référence l'id migré (string) du nœud source, pas l'id numérique v0 brut.
    expect(link!.fromId).toBe(shape!.id)

    const mask = v1.elements.find((e) => e.kind === 'occlusion-mask')
    expect(mask).toMatchObject({ kind: 'occlusion-mask', x: 5, y: 5, width: 40, height: 30, label: 'Zone cachée' })

    const stroke = v1.elements.find((e) => e.kind === 'stroke')
    expect(stroke).toMatchObject({
      kind: 'stroke', color: '#ef4444', strokeWidth: 3,
      points: [{ x: 0, y: 0 }, { x: 5, y: 5 }],
    })
  })

  it('migre un document v0 partiel (champs manquants) sans erreur', () => {
    const v1 = migrateLegacyV0ToV1({})
    expect(v1.schema_version).toBe(1)
    expect(v1.elements).toEqual([])
    expect(v1.backgroundImage).toBeNull()
  })

  it("un id de nœud numérique et une connexion ne produisent jamais le même id final", () => {
    const v1 = migrateLegacyV0ToV1(legacyDoc({
      nodes: [{ id: 1, label: 'A', type: 'rect', x: 0, y: 0, color: '#fff' }],
    }))
    const ids = v1.elements.map((e) => e.id)
    expect(new Set(ids).size).toBe(ids.length)
  })

  it('une connexion sans arrow/dashed/label explicites obtient des valeurs par défaut sûres', () => {
    const v1 = migrateLegacyV0ToV1(legacyDoc({
      connections: [{ from: 1, to: 2 }],
    }))
    const link = v1.elements.find((e) => e.kind === 'link')
    expect(link).toMatchObject({ label: '', arrow: 'end', dashed: false })
  })
})
