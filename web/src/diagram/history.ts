// Pile d'annulation/rétablissement (Phase 5, cycle 2). Undo par snapshot du document
// (voir CONTEXT.md du chantier) : chaque commande appliquée capture le document `before`
// en plus du document `after` -- restituer `before` garantit par construction l'invariant
// d'annulation, sans avoir à écrire une commande inverse par type.

import type { Command } from './commands'
import { applyCommand } from './commands'
import type { DiagramDocumentV1 } from './document'

interface AppliedCommand {
  command: Command
  before: DiagramDocumentV1
  after: DiagramDocumentV1
}

export class DiagramHistory {
  private undoStack: AppliedCommand[] = []
  private redoStack: AppliedCommand[] = []

  execute(doc: DiagramDocumentV1, command: Command): DiagramDocumentV1 {
    const after = applyCommand(doc, command)
    this.undoStack.push({ command, before: doc, after })
    this.redoStack = []
    return after
  }

  undo(current: DiagramDocumentV1): DiagramDocumentV1 {
    const applied = this.undoStack.pop()
    if (!applied) return current
    this.redoStack.push(applied)
    return applied.before
  }

  redo(current: DiagramDocumentV1): DiagramDocumentV1 {
    const applied = this.redoStack.pop()
    if (!applied) return current
    this.undoStack.push(applied)
    return applied.after
  }
}
