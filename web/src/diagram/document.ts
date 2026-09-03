// Modèle de document versionné pour l'outil de diagrammes (Phase 5, cycle 1 --
// docs/PROMPT_DEMARRAGE.md §8, arbitrages détaillés dans
// workflow/diagrammes-modele-document/CONTEXT.md).
//
// Un seul tableau d'éléments, ordre = ordre d'empilement (§8.3 : « pas un moteur par
// type de diagramme, mais un seul canevas, un vocabulaire d'éléments »). N'ajoute PAS
// les types container/texte-libre/image/LaTeX du cycle 8 -- ce serait de la
// spéculation (YAGNI). Le mécanisme de version + migration (voir migrations.ts) est
// ce qui permettra de les ajouter proprement en schema_version 2 le moment venu.

export type ShapeKind = 'rect' | 'circle' | 'diamond' | 'ellipse' | 'text' | 'sticky'
export type ArrowStyle = 'end' | 'both' | 'none'

export interface Point {
  x: number
  y: number
}

interface BaseElement {
  id: string
  x: number
  y: number
  width: number
  height: number
  rotation: number
  locked: boolean
}

export interface ShapeElement extends BaseElement {
  kind: 'shape'
  shape: ShapeKind
  label: string
  color: string
}

export interface LinkElement extends BaseElement {
  kind: 'link'
  fromId: string
  toId: string
  label: string
  arrow: ArrowStyle
  dashed: boolean
  routingPoints: Point[]
}

export interface StrokeElement extends BaseElement {
  kind: 'stroke'
  points: Point[]
  color: string
  strokeWidth: number
}

export interface OcclusionMaskElement extends BaseElement {
  kind: 'occlusion-mask'
  label: string
}

export type DiagramElement = ShapeElement | LinkElement | StrokeElement | OcclusionMaskElement

export interface DiagramDocumentV1 {
  schema_version: 1
  elements: DiagramElement[]
  backgroundImage: string | null
}

export function createEmptyDocument(): DiagramDocumentV1 {
  return {
    schema_version: 1,
    elements: [],
    backgroundImage: null,
  }
}
