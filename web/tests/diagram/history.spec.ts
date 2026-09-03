import { describe, it, expect } from 'vitest'
import { createEmptyDocument } from '../../src/diagram/document'
import { DiagramHistory } from '../../src/diagram/history'
import type { ShapeElement } from '../../src/diagram/document'

function shape(id: string): ShapeElement {
  return {
    kind: 'shape', id, x: 0, y: 0, width: 10, height: 10, rotation: 0, locked: false,
    shape: 'rect', label: 'A', color: '#fff',
  }
}

describe('DiagramHistory (diagrammes-commandes-annulation, Task 4)', () => {
  it('undo sans historique est un no-op', () => {
    const history = new DiagramHistory()
    const doc = createEmptyDocument()
    expect(history.undo(doc)).toBe(doc)
  })

  it('redo sans rétablissement disponible est un no-op', () => {
    const history = new DiagramHistory()
    const doc = createEmptyDocument()
    expect(history.redo(doc)).toBe(doc)
  })

  it('redo restitue exactement le document capturé après la commande', () => {
    const history = new DiagramHistory()
    const initial = createEmptyDocument()
    const afterAdd = history.execute(initial, { type: 'add-element', element: shape('a') })
    const afterUndo = history.undo(afterAdd)
    const afterRedo = history.redo(afterUndo)
    expect(afterRedo).toEqual(afterAdd)
  })

  it("un execute après un undo vide la pile de rétablissement (pas de redo fantôme)", () => {
    const history = new DiagramHistory()
    const initial = createEmptyDocument()
    const afterAddA = history.execute(initial, { type: 'add-element', element: shape('a') })
    const afterUndo = history.undo(afterAddA)
    // Nouvelle commande après l'undo : la branche "a" est abandonnée.
    const afterAddB = history.execute(afterUndo, { type: 'add-element', element: shape('b') })
    const afterRedo = history.redo(afterAddB)
    // Rien à rétablir : la pile de redo a été vidée par le execute() précédent.
    expect(afterRedo).toBe(afterAddB)
  })
})
