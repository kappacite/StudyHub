// Commandes d'édition (Phase 5, cycle 2 -- docs/PROMPT_DEMARRAGE.md §8.7). Jeu minimal
// générique (ajout/suppression/modification) ; les commandes plus spécifiques des cycles
// suivants (déplacement explicite, ancrage de lien...) réutiliseront cette infrastructure.
//
// applyCommand ne mute jamais le document ni un élément existant -- condition posée par
// l'invariant d'annulation (cycle 1, passation) : chaque commande retourne un NOUVEAU
// DiagramDocumentV1.

import type { DiagramDocumentV1, DiagramElement } from './document'

export type Command =
  | { type: 'add-element'; element: DiagramElement }
  | { type: 'remove-element'; id: string }
  | { type: 'update-element'; id: string; changes: Partial<DiagramElement> }

export function applyCommand(doc: DiagramDocumentV1, command: Command): DiagramDocumentV1 {
  switch (command.type) {
    case 'add-element':
      return { ...doc, elements: [...doc.elements, command.element] }

    case 'remove-element':
      return { ...doc, elements: doc.elements.filter((el) => el.id !== command.id) }

    case 'update-element': {
      const index = doc.elements.findIndex((el) => el.id === command.id)
      if (index === -1) return doc
      const elements = [...doc.elements]
      elements[index] = { ...elements[index], ...command.changes } as DiagramElement
      return { ...doc, elements }
    }
  }
}
