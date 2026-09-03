// Corpus de non-régression de format (docs/PROMPT_DEMARRAGE.md §8.7/§8.8 : « un corpus de
// documents sérialisés de chaque version doit continuer à s'ouvrir, un test par version de
// schéma »).
//
// RÈGLE : ne jamais retirer une fixture existante de ce fichier ou du dossier
// fixtures/, même si elle semble redondante -- seulement en ajouter à mesure que de
// nouvelles versions de schéma apparaissent dans les cycles suivants. C'est la garantie
// mécanique que les diagrammes déjà enregistrés par de vrais utilisateurs continuent de
// s'ouvrir, cycle après cycle.

import { describe, it, expect } from 'vitest'
import { parseDiagramDocument } from '../../src/diagram/document'
import organigrammeSimple from './fixtures/v0-organigramme-simple.json'
import occlusionAnatomie from './fixtures/v0-occlusion-anatomie.json'
import croquisMainLevee from './fixtures/v0-croquis-main-levee.json'

const legacyV0Corpus = [
  { name: 'organigramme simple (nœuds + liens)', doc: organigrammeSimple },
  { name: 'occlusion anatomie (masques + image de fond)', doc: occlusionAnatomie },
  { name: 'croquis main levée (nœud + trait libre)', doc: croquisMainLevee },
]

describe('Corpus de non-régression de format v0 (diagrammes-modele-document, Task 4)', () => {
  it.each(legacyV0Corpus)('$name se parse en DiagramDocumentV1 valide sans exception', ({ doc }) => {
    const parsed = parseDiagramDocument(JSON.stringify(doc))
    expect(parsed.schema_version).toBe(1)
    expect(Array.isArray(parsed.elements)).toBe(true)
    expect(parsed.elements.length).toBeGreaterThan(0)
  })
})
