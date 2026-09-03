import { describe, it, expect } from 'vitest'
import {
  createDefaultCamera,
  screenToWorld,
  worldToScreen,
  panBy,
  zoomAt,
} from '../../src/diagram/camera'

const VIEWPORT = { width: 800, height: 600 }

describe('camera (diagrammes-canevas-pan-zoom, Task 1)', () => {
  it('caméra par défaut : le centre écran correspond à l\'origine monde', () => {
    const camera = createDefaultCamera()
    expect(worldToScreen({ x: 0, y: 0 }, camera, VIEWPORT)).toEqual({ x: 400, y: 300 })
    expect(screenToWorld({ x: 400, y: 300 }, camera, VIEWPORT)).toEqual({ x: 0, y: 0 })
  })

  it('rondtrip screenToWorld(worldToScreen(p)) === p', () => {
    const camera = { x: 120, y: -40, zoom: 1.5 }
    const world = { x: 250, y: -80 }
    const screen = worldToScreen(world, camera, VIEWPORT)
    const back = screenToWorld(screen, camera, VIEWPORT)
    expect(back.x).toBeCloseTo(world.x, 6)
    expect(back.y).toBeCloseTo(world.y, 6)
  })

  it('un zoom de 2 rend un déplacement écran deux fois plus petit en coordonnées monde', () => {
    const camera1 = { x: 0, y: 0, zoom: 1 }
    const camera2 = { x: 0, y: 0, zoom: 2 }
    const p1a = screenToWorld({ x: 400, y: 300 }, camera1, VIEWPORT)
    const p1b = screenToWorld({ x: 500, y: 300 }, camera1, VIEWPORT)
    const p2a = screenToWorld({ x: 400, y: 300 }, camera2, VIEWPORT)
    const p2b = screenToWorld({ x: 500, y: 300 }, camera2, VIEWPORT)
    const dxZoom1 = p1b.x - p1a.x
    const dxZoom2 = p2b.x - p2a.x
    expect(dxZoom2).toBeCloseTo(dxZoom1 / 2, 6)
  })

  it('panBy déplace la caméra sans changer le zoom', () => {
    const camera = { x: 0, y: 0, zoom: 1 }
    const panned = panBy(camera, 50, -20)
    expect(panned.zoom).toBe(1)
    expect(panned).not.toEqual(camera)
  })

  it('zoomAt garde le point écran ciblé fixe en coordonnées monde', () => {
    const camera = { x: 10, y: 5, zoom: 1 }
    const screenPoint = { x: 250, y: 180 }
    const worldBefore = screenToWorld(screenPoint, camera, VIEWPORT)
    const zoomed = zoomAt(camera, screenPoint, 2, VIEWPORT)
    const worldAfter = screenToWorld(screenPoint, zoomed, VIEWPORT)
    expect(zoomed.zoom).toBeCloseTo(2, 6)
    expect(worldAfter.x).toBeCloseTo(worldBefore.x, 6)
    expect(worldAfter.y).toBeCloseTo(worldBefore.y, 6)
  })
})
