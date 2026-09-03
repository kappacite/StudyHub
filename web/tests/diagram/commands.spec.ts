import { describe, it, expect } from 'vitest'
import { createEmptyDocument } from '../../src/diagram/document'
import { applyCommand, type Command } from '../../src/diagram/commands'
import type { ShapeElement } from '../../src/diagram/document'

function shape(id: string, overrides: Partial<ShapeElement> = {}): ShapeElement {
  return {
    kind: 'shape', id, x: 0, y: 0, width: 10, height: 10, rotation: 0, locked: false,
    shape: 'rect', label: 'A', color: '#fff',
    ...overrides,
  }
}

describe('applyCommand (diagrammes-commandes-annulation, Task 3)', () => {
  it('add-element ajoute en fin de tableau (ordre = z-order)', () => {
    const doc = createEmptyDocument()
    const withOne = applyCommand(doc, { type: 'add-element', element: shape('a') })
    const withTwo = applyCommand(withOne, { type: 'add-element', element: shape('b') })
    expect(withTwo.elements.map((e) => e.id)).toEqual(['a', 'b'])
  })

  it("remove-element sur un id absent est un no-op (pas d'exception)", () => {
    const doc = applyCommand(createEmptyDocument(), { type: 'add-element', element: shape('a') })
    const result = applyCommand(doc, { type: 'remove-element', id: 'absent' })
    expect(result).toEqual(doc)
  })

  it('remove-element retire exactement l\'élément visé', () => {
    let doc = createEmptyDocument()
    doc = applyCommand(doc, { type: 'add-element', element: shape('a') })
    doc = applyCommand(doc, { type: 'add-element', element: shape('b') })
    const result = applyCommand(doc, { type: 'remove-element', id: 'a' })
    expect(result.elements.map((e) => e.id)).toEqual(['b'])
  })

  it('update-element fusionne les champs donnés sans toucher aux autres', () => {
    const doc = applyCommand(createEmptyDocument(), {
      type: 'add-element',
      element: shape('a', { label: 'Ancien', color: '#000' }),
    })
    const result = applyCommand(doc, {
      type: 'update-element',
      id: 'a',
      changes: { label: 'Nouveau' },
    })
    const updated = result.elements[0] as ShapeElement
    expect(updated.label).toBe('Nouveau')
    expect(updated.color).toBe('#000')
  })

  it('update-element sur un id absent est un no-op', () => {
    const doc = applyCommand(createEmptyDocument(), { type: 'add-element', element: shape('a') })
    const result = applyCommand(doc, {
      type: 'update-element',
      id: 'absent',
      changes: { label: 'X' },
    })
    expect(result).toEqual(doc)
  })

  it("n'exécute jamais de mutation en place (le document d'entrée reste inchangé)", () => {
    const doc = applyCommand(createEmptyDocument(), { type: 'add-element', element: shape('a') })
    const before = JSON.parse(JSON.stringify(doc))
    applyCommand(doc, { type: 'update-element', id: 'a', changes: { label: 'Y' } } satisfies Command)
    expect(doc).toEqual(before)
  })
})
