// Invariant d'annulation testé par propriété (docs/PROMPT_DEMARRAGE.md §8.7) : « pour toute
// suite de commandes, annuler autant de fois qu'il y a eu de commandes ramène à un document
// strictement identique à l'état initial ». Écrit AVANT commands.ts/history.ts (rouge
// confirmé), comme l'exige §8.7 -- ce test protège l'undo, pas l'inverse.

import { describe, it, expect } from 'vitest'
import fc from 'fast-check'
import { createEmptyDocument } from '../../src/diagram/document'
import type { Command } from '../../src/diagram/commands'
import { DiagramHistory } from '../../src/diagram/history'

// Pool d'ids fixe et restreint (pas fc.uuid()) : garantit que remove/update ciblent
// souvent un élément réellement présent, pas systématiquement un id absent (ce qui
// rendrait le test trivial, presque toujours des no-op).
const CANDIDATE_IDS = ['id-a', 'id-b', 'id-c']

const shapeArb = fc.record({
  kind: fc.constant('shape' as const),
  id: fc.constantFrom(...CANDIDATE_IDS),
  x: fc.integer({ min: 0, max: 500 }),
  y: fc.integer({ min: 0, max: 500 }),
  width: fc.integer({ min: 1, max: 200 }),
  height: fc.integer({ min: 1, max: 200 }),
  rotation: fc.constant(0),
  locked: fc.boolean(),
  shape: fc.constantFrom('rect', 'circle', 'diamond', 'ellipse', 'text', 'sticky' as const),
  label: fc.string(),
  color: fc.constantFrom('#ffffff', '#000000', '#ff0000'),
})

const commandArb: fc.Arbitrary<Command> = fc.oneof(
  shapeArb.map((element) => ({ type: 'add-element', element }) as Command),
  fc.constantFrom(...CANDIDATE_IDS).map((id) => ({ type: 'remove-element', id }) as Command),
  fc
    .tuple(fc.constantFrom(...CANDIDATE_IDS), fc.string())
    .map(([id, label]) => ({ type: 'update-element', id, changes: { label } }) as Command),
)

describe('Invariant d\'annulation (diagrammes-commandes-annulation, Task 2)', () => {
  it('annuler une séquence entière de commandes ramène au document initial', () => {
    fc.assert(
      fc.property(fc.array(commandArb, { maxLength: 30 }), (commands) => {
        const initial = createEmptyDocument()
        const history = new DiagramHistory()
        let doc = initial

        for (const command of commands) {
          doc = history.execute(doc, command)
        }
        for (let i = 0; i < commands.length; i++) {
          doc = history.undo(doc)
        }

        expect(doc).toEqual(initial)
      }),
    )
  })
})
