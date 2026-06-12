import { describe, it, expect, vi, beforeEach } from 'vitest'

// Capacitor n'existe pas dans l'environnement de test : on le mocke.
const capacitor = vi.hoisted(() => ({
  isNativePlatform: vi.fn(),
  getPlatform: vi.fn(),
}))
vi.mock('@capacitor/core', () => ({ Capacitor: capacitor }))

import { usePlatform } from '../../src/composables/usePlatform'

describe('usePlatform', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('reflète une plateforme native (iOS)', () => {
    capacitor.isNativePlatform.mockReturnValue(true)
    capacitor.getPlatform.mockReturnValue('ios')

    const { isNative, platform } = usePlatform()

    expect(isNative).toBe(true)
    expect(platform).toBe('ios')
  })

  it('reflète le web (non natif)', () => {
    capacitor.isNativePlatform.mockReturnValue(false)
    capacitor.getPlatform.mockReturnValue('web')

    const { isNative, platform } = usePlatform()

    expect(isNative).toBe(false)
    expect(platform).toBe('web')
  })
})
