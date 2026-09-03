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

  describe('sélection (diagrammes-placement-selection, Task 3)', () => {
    it('clic sur un élément expose son id comme sélectionné', async () => {
      const doc: DiagramDocumentV1 = { ...createEmptyDocument(), elements: [shape('a', 0, 0)] }
      const wrapper = mountCanvas(doc)
      const el = wrapper.find('[data-test="diagram-element"]')
      await el.trigger('mousedown', { clientX: 400, clientY: 300 })
      await el.trigger('mouseup', { clientX: 400, clientY: 300 })
      expect((wrapper.vm as unknown as { selectedElementId: string | null }).selectedElementId).toBe('a')
    })

    it('clic sur le fond après une sélection la retire', async () => {
      const doc: DiagramDocumentV1 = { ...createEmptyDocument(), elements: [shape('a', 0, 0)] }
      const wrapper = mountCanvas(doc)
      const el = wrapper.find('[data-test="diagram-element"]')
      await el.trigger('mousedown', { clientX: 400, clientY: 300 })
      await el.trigger('mouseup', { clientX: 400, clientY: 300 })
      const svg = wrapper.find('svg')
      await svg.trigger('mousedown', { clientX: 10, clientY: 10 })
      await svg.trigger('mouseup', { clientX: 10, clientY: 10 })
      expect((wrapper.vm as unknown as { selectedElementId: string | null }).selectedElementId).toBeNull()
    })

    it("un glisser (dépassant le seuil) sur le fond ne modifie pas la sélection courante", async () => {
      const doc: DiagramDocumentV1 = { ...createEmptyDocument(), elements: [shape('a', 0, 0)] }
      const wrapper = mountCanvas(doc)
      const el = wrapper.find('[data-test="diagram-element"]')
      await el.trigger('mousedown', { clientX: 400, clientY: 300 })
      await el.trigger('mouseup', { clientX: 400, clientY: 300 })
      const svg = wrapper.find('svg')
      await svg.trigger('mousedown', { clientX: 10, clientY: 10 })
      await svg.trigger('mousemove', { clientX: 80, clientY: 80 })
      await svg.trigger('mouseup', { clientX: 80, clientY: 80 })
      expect((wrapper.vm as unknown as { selectedElementId: string | null }).selectedElementId).toBe('a')
    })
  })

  describe('déplacement d\'un élément (diagrammes-placement-selection, Task 4)', () => {
    it('un glisser complet produit exactement une entrée dans l\'historique (pas une par mousemove)', async () => {
      const doc: DiagramDocumentV1 = { ...createEmptyDocument(), elements: [shape('a', 0, 0)] }
      const wrapper = mountCanvas(doc)
      const el = wrapper.find('[data-test="diagram-element"]')
      await el.trigger('mousedown', { clientX: 400, clientY: 300 })
      await el.trigger('mousemove', { clientX: 410, clientY: 300 })
      await el.trigger('mousemove', { clientX: 420, clientY: 305 })
      await el.trigger('mousemove', { clientX: 430, clientY: 310 })
      await el.trigger('mouseup', { clientX: 430, clientY: 310 })
      expect(wrapper.emitted('update:document')).toHaveLength(1)
    })

    it('annuler après un glisser restitue la position d\'avant le geste', async () => {
      const doc: DiagramDocumentV1 = { ...createEmptyDocument(), elements: [shape('a', 0, 0)] }
      const wrapper = mountCanvas(doc)
      const el = wrapper.find('[data-test="diagram-element"]')
      await el.trigger('mousedown', { clientX: 400, clientY: 300 })
      await el.trigger('mousemove', { clientX: 430, clientY: 310 })
      await el.trigger('mouseup', { clientX: 430, clientY: 310 })
      const emitted = wrapper.emitted('update:document')!
      const afterDrag = emitted[0][0] as DiagramDocumentV1
      expect(afterDrag.elements[0]).not.toMatchObject({ x: 0, y: 0 })

      const vm = wrapper.vm as unknown as { history: { undo: (d: DiagramDocumentV1) => DiagramDocumentV1 } }
      const restored = vm.history.undo(afterDrag)
      expect(restored.elements[0]).toMatchObject({ x: 0, y: 0 })
    })

    it('maintenir Alt pendant le glisser place l\'élément à la position brute (non magnétisée)', async () => {
      const doc: DiagramDocumentV1 = { ...createEmptyDocument(), elements: [shape('a', 0, 0)] }
      const wrapper = mountCanvas(doc)
      const el = wrapper.find('[data-test="diagram-element"]')
      await el.trigger('mousedown', { clientX: 400, clientY: 300 })
      await el.trigger('mousemove', { clientX: 423, clientY: 317, altKey: true })
      await el.trigger('mouseup', { clientX: 423, clientY: 317, altKey: true })
      const emitted = wrapper.emitted('update:document')!
      const doc2 = emitted[0][0] as DiagramDocumentV1
      expect(doc2.elements[0]).toMatchObject({ x: 23, y: 17 })
    })

    it('sans Alt, la position est magnétisée sur la grille', async () => {
      const doc: DiagramDocumentV1 = { ...createEmptyDocument(), elements: [shape('a', 0, 0)] }
      const wrapper = mountCanvas(doc)
      const el = wrapper.find('[data-test="diagram-element"]')
      await el.trigger('mousedown', { clientX: 400, clientY: 300 })
      await el.trigger('mousemove', { clientX: 423, clientY: 317 })
      await el.trigger('mouseup', { clientX: 423, clientY: 317 })
      const emitted = wrapper.emitted('update:document')!
      const doc2 = emitted[0][0] as DiagramDocumentV1
      expect(doc2.elements[0]).toMatchObject({ x: 20, y: 20 })
    })
  })

  describe('rendu visuel : contour de sélection et guides (diagrammes-placement-selection, Task 5)', () => {
    it('le contour de sélection ne rend que si un élément est sélectionné', async () => {
      const doc: DiagramDocumentV1 = { ...createEmptyDocument(), elements: [shape('a', 0, 0)] }
      const wrapper = mountCanvas(doc)
      expect(wrapper.findAll('[data-test="selection-outline"]')).toHaveLength(0)

      const el = wrapper.find('[data-test="diagram-element"]')
      await el.trigger('mousedown', { clientX: 400, clientY: 300 })
      await el.trigger('mouseup', { clientX: 400, clientY: 300 })
      expect(wrapper.findAll('[data-test="selection-outline"]')).toHaveLength(1)
    })

    it("les guides d'alignement ne rendent que pendant un glisser actif avec un alignement détecté", async () => {
      // b est déjà aligné en x=100 avec la position où a va être amené par le glisser
      // (écart en Y assez grand pour ne pas aussi matcher sur cet axe).
      const doc: DiagramDocumentV1 = {
        ...createEmptyDocument(),
        elements: [shape('a', 0, 0), shape('b', 100, 200)],
      }
      const wrapper = mountCanvas(doc)
      const els = wrapper.findAll('[data-test="diagram-element"]')
      const a = els.find((w) => w.attributes('data-id') === 'a')!

      expect(wrapper.findAll('[data-test="alignment-guide"]').length).toBe(0)

      // Glisse 'a' de x=0 vers x proche de 100 (dans le seuil d'alignement).
      await a.trigger('mousedown', { clientX: 400, clientY: 300 })
      await a.trigger('mousemove', { clientX: 502, clientY: 300 })
      expect(wrapper.findAll('[data-test="alignment-guide"]').length).toBeGreaterThan(0)

      await a.trigger('mouseup', { clientX: 502, clientY: 300 })
      expect(wrapper.findAll('[data-test="alignment-guide"]').length).toBe(0)
    })
  })
})
