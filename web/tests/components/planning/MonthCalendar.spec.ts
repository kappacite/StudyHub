import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MonthCalendar from '../../../src/components/planning/MonthCalendar.vue'
import type { PlanningDay } from '../../../src/services/planningService'

describe('MonthCalendar — notes-ia-planning-corrections Task 2 (breakdown kind/id/name)', () => {
  it('affiche le nom des items deck ET revision_set (plus deck_id/deck_name)', () => {
    const days: PlanningDay[] = [
      {
        date: '2026-09-10',
        total_due: 3,
        breakdown: [
          { kind: 'deck', id: 1, name: 'Anatomie', count: 2 },
          { kind: 'revision_set', id: 2, name: 'Chimie', count: 1 },
        ],
      },
    ]
    const wrapper = mount(MonthCalendar, { props: { days } })
    expect(wrapper.text()).toContain('Anatomie')
    expect(wrapper.text()).toContain('Chimie')
  })
})
