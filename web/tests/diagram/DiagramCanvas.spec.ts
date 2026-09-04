import { describe, it, expect, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import DiagramCanvas from '../../src/diagram/DiagramCanvas.vue'
import { createEmptyDocument } from '../../src/diagram/document'
import type { ShapeElement, LinkElement, DiagramDocumentV1 } from '../../src/diagram/document'

function shape(id: string, x: number, y: number): ShapeElement {
  return { kind: 'shape', id, x, y, width: 50, height: 50, rotation: 0, locked: false, shape: 'rect', label: id, color: '#fff' }
}

function link(id: string, fromId: string, toId: string, overrides: Partial<LinkElement> = {}): LinkElement {
  return {
    kind: 'link', id, x: 0, y: 0, width: 0, height: 0, rotation: 0, locked: false,
    fromId, toId, label: '', arrow: 'end', dashed: false, routingPoints: [],
    ...overrides,
  }
}

let mountedWrappers: ReturnType<typeof mount>[] = []

function mountCanvas(doc: DiagramDocumentV1) {
  const wrapper = mount(DiagramCanvas, {
    props: { document: doc, viewportWidth: 800, viewportHeight: 600 },
    // Le panoramique écoute mousemove/mouseup sur `window` (glisser qui peut sortir du
    // canevas) : nécessite un montage attaché au vrai document pour que les événements
    // déclenchés sur le <svg> remontent jusqu'à `window`.
    attachTo: document.body,
  })
  mountedWrappers.push(wrapper)
  return wrapper
}

describe('DiagramCanvas (diagrammes-canevas-pan-zoom, Task 5)', () => {
  // `attachTo: document.body` (nécessaire pour les listeners de panoramique/clavier sur
  // `window`) laisserait sinon des nœuds détachés s'accumuler entre les tests -- et, depuis
  // le cycle 6 (keydown monté une fois, écouté tant que le composant existe, pas seulement le
  // temps d'un geste comme le panoramique/glisser), des listeners `window` orphelins de
  // composants jamais démontés continueraient à réagir aux événements des tests suivants.
  // `unmount()` déclenche `onUnmounted` (retrait du listener) avant de vider le DOM.
  afterEach(() => {
    for (const wrapper of mountedWrappers) wrapper.unmount()
    mountedWrappers = []
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

  describe('rendu des liens (diagrammes-liens-ancrage, Task 2)', () => {
    it('un lien valide produit un tracé visible', () => {
      const doc: DiagramDocumentV1 = {
        ...createEmptyDocument(),
        elements: [shape('a', 0, 0), shape('b', 200, 0), link('l1', 'a', 'b')],
      }
      const wrapper = mountCanvas(doc)
      expect(wrapper.findAll('[data-test="diagram-link"]')).toHaveLength(1)
    })

    it("un lien orphelin (id absent) ne casse pas le rendu et ne produit aucun tracé", () => {
      const doc: DiagramDocumentV1 = {
        ...createEmptyDocument(),
        elements: [shape('a', 0, 0), link('l1', 'a', 'inexistant')],
      }
      expect(() => mountCanvas(doc)).not.toThrow()
      const wrapper = mountCanvas(doc)
      expect(wrapper.findAll('[data-test="diagram-link"]')).toHaveLength(0)
    })

    it('un lien avec des routingPoints passe par ces points (pas une ligne droite directe)', () => {
      const doc: DiagramDocumentV1 = {
        ...createEmptyDocument(),
        elements: [
          shape('a', 0, 0),
          shape('b', 200, 0),
          link('l1', 'a', 'b', { routingPoints: [{ x: 100, y: 150 }] }),
        ],
      }
      const wrapper = mountCanvas(doc)
      const points = wrapper.find('[data-test="diagram-link"]').attributes('points')!
      expect(points).toContain('100,150')
    })
  })

  describe('création de lien par geste (diagrammes-liens-ancrage, Task 3)', () => {
    // Caméra par défaut (zoom 1, origine monde au centre écran 400,300) : 'a' [0,50]x[0,50]
    // occupe l'écran [400,450]x[300,350], 'b' [200,250]x[0,50] occupe [600,650]x[300,350].
    function docWithTwoShapes(): DiagramDocumentV1 {
      return { ...createEmptyDocument(), elements: [shape('a', 0, 0), shape('b', 200, 0)] }
    }

    it("glisser avec Maj d'une forme vers une autre ajoute un lien avec le bon fromId/toId", async () => {
      const wrapper = mountCanvas(docWithTwoShapes())
      const a = wrapper.findAll('[data-test="diagram-element"]').find((w) => w.attributes('data-id') === 'a')!
      await a.trigger('mousedown', { clientX: 410, clientY: 310, shiftKey: true })
      await a.trigger('mouseup', { clientX: 620, clientY: 320, shiftKey: true })

      const emitted = wrapper.emitted('update:document')!
      expect(emitted).toHaveLength(1)
      const doc2 = emitted[0][0] as DiagramDocumentV1
      const newLink = doc2.elements.find((e) => e.kind === 'link') as LinkElement | undefined
      expect(newLink).toMatchObject({ fromId: 'a', toId: 'b' })
    })

    it("relâcher hors de toute forme ne crée rien", async () => {
      const wrapper = mountCanvas(docWithTwoShapes())
      const a = wrapper.findAll('[data-test="diagram-element"]').find((w) => w.attributes('data-id') === 'a')!
      await a.trigger('mousedown', { clientX: 410, clientY: 310, shiftKey: true })
      await a.trigger('mouseup', { clientX: 10, clientY: 10, shiftKey: true })
      expect(wrapper.emitted('update:document')).toBeUndefined()
    })

    it('relâcher sur la forme de départ ne crée rien', async () => {
      const wrapper = mountCanvas(docWithTwoShapes())
      const a = wrapper.findAll('[data-test="diagram-element"]').find((w) => w.attributes('data-id') === 'a')!
      await a.trigger('mousedown', { clientX: 410, clientY: 310, shiftKey: true })
      await a.trigger('mouseup', { clientX: 420, clientY: 320, shiftKey: true })
      expect(wrapper.emitted('update:document')).toBeUndefined()
    })

    it('sans Maj, un glisser reste un déplacement (non-régression du cycle 4)', async () => {
      const wrapper = mountCanvas(docWithTwoShapes())
      const a = wrapper.findAll('[data-test="diagram-element"]').find((w) => w.attributes('data-id') === 'a')!
      await a.trigger('mousedown', { clientX: 410, clientY: 310 })
      await a.trigger('mousemove', { clientX: 440, clientY: 310 })
      await a.trigger('mouseup', { clientX: 440, clientY: 310 })

      const emitted = wrapper.emitted('update:document')!
      const doc2 = emitted[0][0] as DiagramDocumentV1
      expect(doc2.elements.some((e) => e.kind === 'link')).toBe(false)
      expect(doc2.elements.find((e) => e.id === 'a')).toMatchObject({ x: 30 })
    })
  })

  describe('interactions clavier (diagrammes-interactions-clavier, Task 3)', () => {
    async function selectElement(wrapper: ReturnType<typeof mount>, id: string) {
      const el = wrapper.findAll('[data-test="diagram-element"]').find((w) => w.attributes('data-id') === id)!
      await el.trigger('mousedown', { clientX: 410, clientY: 310 })
      await el.trigger('mouseup', { clientX: 410, clientY: 310 })
    }

    it('Entrée ajoute une forme non chevauchante et la sélectionne', async () => {
      const doc: DiagramDocumentV1 = { ...createEmptyDocument(), elements: [shape('a', 0, 0)] }
      const wrapper = mountCanvas(doc)
      await selectElement(wrapper, 'a')

      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }))
      await wrapper.vm.$nextTick()

      const emitted = wrapper.emitted('update:document')!
      const doc2 = emitted[0][0] as DiagramDocumentV1
      expect(doc2.elements).toHaveLength(2)
      const created = doc2.elements.find((e) => e.id !== 'a') as ShapeElement
      expect(created.x).toBeGreaterThan(50) // à droite de 'a' (largeur 50)
      const vm = wrapper.vm as unknown as { selectedElementId: string | null }
      expect(vm.selectedElementId).toBe(created.id)
    })

    it('Tab ajoute une forme ET un lien depuis la sélection', async () => {
      const doc: DiagramDocumentV1 = { ...createEmptyDocument(), elements: [shape('a', 0, 0)] }
      const wrapper = mountCanvas(doc)
      await selectElement(wrapper, 'a')

      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab' }))
      await wrapper.vm.$nextTick()

      const emitted = wrapper.emitted('update:document')!
      const lastDoc = emitted[emitted.length - 1][0] as DiagramDocumentV1
      const newShape = lastDoc.elements.find((e) => e.kind === 'shape' && e.id !== 'a') as ShapeElement
      const newLink = lastDoc.elements.find((e) => e.kind === 'link') as LinkElement
      expect(newShape).toBeDefined()
      expect(newLink).toMatchObject({ fromId: 'a', toId: newShape.id })
    })

    it('Suppr retire la forme sélectionnée du document émis', async () => {
      const doc: DiagramDocumentV1 = { ...createEmptyDocument(), elements: [shape('a', 0, 0), shape('b', 200, 0)] }
      const wrapper = mountCanvas(doc)
      await selectElement(wrapper, 'a')

      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Delete' }))
      await wrapper.vm.$nextTick()

      const emitted = wrapper.emitted('update:document')!
      const doc2 = emitted[0][0] as DiagramDocumentV1
      expect(doc2.elements.map((e) => e.id)).toEqual(['b'])
    })

    it('flèche droite cycle vers l\'élément suivant', async () => {
      const doc: DiagramDocumentV1 = { ...createEmptyDocument(), elements: [shape('a', 0, 0), shape('b', 200, 0)] }
      const wrapper = mountCanvas(doc)
      await selectElement(wrapper, 'a')

      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight' }))
      await wrapper.vm.$nextTick()

      const vm = wrapper.vm as unknown as { selectedElementId: string | null }
      expect(vm.selectedElementId).toBe('b')
    })

    it("aucun raccourci n'agit si rien n'est sélectionné (sauf flèche)", async () => {
      const doc: DiagramDocumentV1 = { ...createEmptyDocument(), elements: [shape('a', 0, 0)] }
      const wrapper = mountCanvas(doc)

      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }))
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab' }))
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Delete' }))
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('update:document')).toBeUndefined()
    })
  })
})
