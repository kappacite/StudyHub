import { describe, it, expect } from 'vitest'
import { computeDistance, computeMidpoint } from '../../src/diagram/touch'

describe('touch geometry (diagrammes-interactions-tactiles, Task 1)', () => {
  it('computeDistance sur un triangle 3-4-5', () => {
    expect(computeDistance({ x: 0, y: 0 }, { x: 3, y: 4 })).toBe(5)
  })

  it('computeDistance est nulle pour deux points identiques', () => {
    expect(computeDistance({ x: 10, y: 10 }, { x: 10, y: 10 })).toBe(0)
  })

  it('computeMidpoint de deux points connus', () => {
    expect(computeMidpoint({ x: 0, y: 0 }, { x: 10, y: 20 })).toEqual({ x: 5, y: 10 })
  })
})
