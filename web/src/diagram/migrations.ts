// Migration du format ad hoc v0 (Diagrams.vue, non versionné) vers DiagramDocumentV1
// (Phase 5, cycle 1 -- docs/PROMPT_DEMARRAGE.md §8.8 : « les documents de toutes les
// versions antérieures s'ouvrent encore »). Aucune perte de donnée admise.

import type { ArrowStyle, DiagramDocumentV1, DiagramElement, Point, ShapeKind } from './document'
import { createEmptyDocument } from './document'

interface LegacyNode {
  id: number | string
  label?: string
  type?: ShapeKind
  x?: number
  y?: number
  color?: string
  width?: number
  height?: number
}

interface LegacyConnection {
  from: number | string
  to: number | string
  label?: string
  arrow?: ArrowStyle
  dashed?: boolean
}

interface LegacyMask {
  id: string
  x?: number
  y?: number
  width?: number
  height?: number
  label?: string
}

interface LegacyStroke {
  id: string
  points?: Point[]
  color?: string
  width?: number
}

interface LegacyDocument {
  nodes?: LegacyNode[]
  connections?: LegacyConnection[]
  masks?: LegacyMask[]
  backgroundImage?: string | null
  drawings?: LegacyStroke[]
}

// Préfixé par type pour garantir l'unicité entre catégories -- un node id=1 (v0, non
// préfixé, numérique) et une connexion à l'index 1 ne doivent jamais produire le même
// id final une fois migrés.
function shapeElementId(nodeId: number | string): string {
  return `shape-${nodeId}`
}

export function migrateLegacyV0ToV1(raw: unknown): DiagramDocumentV1 {
  const legacy = (raw ?? {}) as LegacyDocument
  const elements: DiagramElement[] = []

  for (const node of legacy.nodes ?? []) {
    elements.push({
      kind: 'shape',
      id: shapeElementId(node.id),
      x: node.x ?? 0,
      y: node.y ?? 0,
      width: node.width ?? 0,
      height: node.height ?? 0,
      rotation: 0,
      locked: false,
      shape: node.type ?? 'rect',
      label: node.label ?? '',
      color: node.color ?? '#000000',
    })
  }

  legacy.connections?.forEach((conn, index) => {
    elements.push({
      kind: 'link',
      id: `link-${index}`,
      x: 0,
      y: 0,
      width: 0,
      height: 0,
      rotation: 0,
      locked: false,
      fromId: shapeElementId(conn.from),
      toId: shapeElementId(conn.to),
      label: conn.label ?? '',
      arrow: conn.arrow ?? 'end',
      dashed: conn.dashed ?? false,
      routingPoints: [],
    })
  })

  for (const mask of legacy.masks ?? []) {
    elements.push({
      kind: 'occlusion-mask',
      id: `mask-${mask.id}`,
      x: mask.x ?? 0,
      y: mask.y ?? 0,
      width: mask.width ?? 0,
      height: mask.height ?? 0,
      rotation: 0,
      locked: false,
      label: mask.label ?? '',
    })
  }

  for (const stroke of legacy.drawings ?? []) {
    elements.push({
      kind: 'stroke',
      id: `stroke-${stroke.id}`,
      x: 0,
      y: 0,
      width: 0,
      height: 0,
      rotation: 0,
      locked: false,
      points: stroke.points ?? [],
      color: stroke.color ?? '#000000',
      strokeWidth: stroke.width ?? 1,
    })
  }

  return {
    ...createEmptyDocument(),
    elements,
    backgroundImage: legacy.backgroundImage ?? null,
  }
}
