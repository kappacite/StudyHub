import { describe, it, expect } from 'vitest'
import { taskLaunchRoute } from '../../src/services/assignmentTasks'

describe('taskLaunchRoute', () => {
  it('route les flashcards vers le classeur', () => {
    expect(taskLaunchRoute({ task_type: 'flashcards', ref_uuid: 'b1' })).toBe('/binders/b1')
  })

  it('route le QCM vers la page quiz de la note', () => {
    expect(taskLaunchRoute({ task_type: 'quiz', ref_uuid: 'n1' })).toBe('/notes/n1/quiz')
  })

  it('route le blurting vers la page blurting de la note', () => {
    expect(taskLaunchRoute({ task_type: 'blurting', ref_uuid: 'n2' })).toBe('/notes/n2/blurting')
  })

  it("route l'examen vers la configuration avec le classeur présélectionné", () => {
    expect(taskLaunchRoute({ task_type: 'exam', ref_uuid: 'b3' })).toBe('/exam/setup?binder=b3')
  })

  it('route la lecture vers la note', () => {
    expect(taskLaunchRoute({ task_type: 'read', ref_uuid: 'n4' })).toBe('/notes/n4')
  })

  it('gère un ref_uuid absent sans planter', () => {
    expect(taskLaunchRoute({ task_type: 'read', ref_uuid: null })).toBe('/notes/')
  })
})
