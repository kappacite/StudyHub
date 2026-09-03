// Modèle de caméra pour le canevas infini (Phase 5, cycle 3). Fonctions pures sur des
// coordonnées (§8.7) -- pas de DOM, testables sans canevas.
//
// Convention : `camera.x`/`camera.y` sont les coordonnées MONDE qui apparaissent au CENTRE
// de la fenêtre de vue. `camera.zoom` est un facteur pixels-écran par unité-monde (zoom > 1
// = rapproché). Caméra par défaut : origine monde au centre écran, zoom 1.

export interface Point {
  x: number
  y: number
}

export interface Camera {
  x: number
  y: number
  zoom: number
}

export interface ViewportSize {
  width: number
  height: number
}

export function createDefaultCamera(): Camera {
  return { x: 0, y: 0, zoom: 1 }
}

export function worldToScreen(point: Point, camera: Camera, viewport: ViewportSize): Point {
  return {
    x: (point.x - camera.x) * camera.zoom + viewport.width / 2,
    y: (point.y - camera.y) * camera.zoom + viewport.height / 2,
  }
}

export function screenToWorld(point: Point, camera: Camera, viewport: ViewportSize): Point {
  return {
    x: (point.x - viewport.width / 2) / camera.zoom + camera.x,
    y: (point.y - viewport.height / 2) / camera.zoom + camera.y,
  }
}

// Panoramique en delta écran (ex. delta de glisser en pixels) -- converti en delta monde
// selon le zoom courant, pour que le geste suive le curseur au pixel près quel que soit le
// niveau de zoom.
export function panBy(camera: Camera, dxScreen: number, dyScreen: number): Camera {
  return {
    ...camera,
    x: camera.x - dxScreen / camera.zoom,
    y: camera.y - dyScreen / camera.zoom,
  }
}

// Zoom centré sur un point écran donné (ex. position du curseur) : ce point reste
// visuellement fixe après le zoom, propriété attendue d'un zoom "sous la souris".
export function zoomAt(
  camera: Camera,
  screenPoint: Point,
  factor: number,
  viewport: ViewportSize,
): Camera {
  const worldPoint = screenToWorld(screenPoint, camera, viewport)
  const newZoom = camera.zoom * factor
  return {
    zoom: newZoom,
    x: worldPoint.x - (screenPoint.x - viewport.width / 2) / newZoom,
    y: worldPoint.y - (screenPoint.y - viewport.height / 2) / newZoom,
  }
}
