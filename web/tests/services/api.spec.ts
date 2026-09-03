import { describe, it, expect } from 'vitest'
import api from '../../src/services/api'

describe('api client — timeout', () => {
  it('le timeout est de 60s (1 minute), suffisant pour un appel IA synchrone sans worker Celery local', () => {
    expect(api.defaults.timeout).toBe(60000)
  })
})
