import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PomodoroTimer from '../../../src/components/ui/PomodoroTimer.vue'

describe('PomodoroTimer', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  // Fix round 1 (item 3) : la nouvelle barre de navigation mobile de AppLayout.vue
  // occupe aussi le coin bas-droit sur mobile — le FAB doit s'en décaler pour ne
  // pas la chevaucher, tout en gardant sa position d'origine en desktop (lg+, où
  // la barre de navigation mobile n'existe pas).
  it('se décale au-dessus de la barre de navigation mobile (bottom-6 réservé au desktop)', () => {
    const wrapper = mount(PomodoroTimer)
    const classes = wrapper.classes()
    expect(classes).toContain('lg:bottom-6')
    expect(classes).not.toContain('bottom-6')
  })
})
