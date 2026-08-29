import { describe, it, expect } from 'vitest'
import { formatDuration } from '../../src/utils/duration'

// Task 9 (reviser-hub-redesign) : formatage partage "Xh MM" / "N min" --
// utilise par RevisionSetStats.vue et RevisionBinderStats.vue, ne doit pas
// etre duplique.
describe('formatDuration', () => {
  it('formate en minutes arrondies sous 1h', () => {
    expect(formatDuration(480)).toBe('8 min')
    expect(formatDuration(0)).toBe('0 min')
  })

  it('formate en heures/minutes a partir de 1h (exemples exacts du mockup)', () => {
    expect(formatDuration(8100)).toBe('2h 15')
  })

  it('rend exactement 60 minutes comme 1h 00', () => {
    expect(formatDuration(3600)).toBe('1h 00')
  })

  it('arrondit une frontiere proche de 1h sans produire de minutes >= 60', () => {
    // 3599s arrondit a 60 min au total -- doit basculer en "1h 00", pas "0h 60".
    expect(formatDuration(3599)).toBe('1h 00')
  })
})
