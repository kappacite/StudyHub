import { describe, it, expect, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import DiagramCanvas from '../../src/diagram/DiagramCanvas.vue'
import { createEmptyDocument } from '../../src/diagram/document'
import type { ShapeElement, DiagramDocumentV1 } from '../../src/diagram/document'

function shape(id: string, x: number, y: number): ShapeElement {
  return { kind: 'shape', id, x, y, width: 50, height: 50, rotation: 0, locked: false, shape: 'rect', label: id, color: '#fff' }
}

function mountCanvas(doc: DiagramDocumentV1) {
  return mount(DiagramCanvas, {
    props: { document: doc, viewportWidth: 800, viewportHeight: 600 },
    // Le panoramique écoute mousemove/mouseup sur `window` (glisser qui peut sortir du
    // canevas) : nécessite un montage attaché au vrai document pour que les événements
    // déclenchés sur le <svg> remontent jusqu'à `window`.
    attachTo: document.body,
  })
}

describe('DiagramCanvas (diagrammes-canevas-pan-zoom, Task 5)', () => {
  // `attachTo: document.body` (nécessaire pour les listeners de panoramique sur `window`)
  // laisserait sinon des nœuds détachés s'accumuler dans le document entre les tests.
  afterEach(() => {
    document.body.innerHTML = ''
  })


  it('ne rend que les éléments visibles (culling), pas la totalité du document', () => {
    const doc: DiagramDocumentV1 = {
      ...createEmptyDocument(),
      elements: [shape('inside', 0, 0), shape('far', 100000, 100000)],
    }
    const wrapper = mountCanvas(doc)
    const rendered = wrapper.findAll('[data-test="diagram-element"]')
    expect(rendered).toHaveLength(1)
    expect(rendered[0].attributes('data-id')).toBe('inside')
  })

  it('la molette modifie le viewBox (zoom)', async () => {
    const doc: DiagramDocumentV1 = { ...createEmptyDocument(), elements: [shape('a', 0, 0)] }
    const wrapper = mountCanvas(doc)
    const svg = wrapper.find('svg')
    const before = svg.attributes('viewBox')
    await svg.trigger('wheel', { deltaY: -100, clientX: 400, clientY: 300 })
    const after = svg.attributes('viewBox')
    expect(after).not.toBe(before)
  })

  it('un glisser sur le fond modifie le viewBox (panoramique)', async () => {
    const doc: DiagramDocumentV1 = { ...createEmptyDocument(), elements: [shape('a', 0, 0)] }
    const wrapper = mountCanvas(doc)
    const svg = wrapper.find('svg')
    const before = svg.attributes('viewBox')
    await svg.trigger('mousedown', { clientX: 100, clientY: 100 })
    await svg.trigger('mousemove', { clientX: 150, clientY: 130 })
    await svg.trigger('mouseup', { clientX: 150, clientY: 130 })
    const after = svg.attributes('viewBox')
    expect(after).not.toBe(before)
  })
})
