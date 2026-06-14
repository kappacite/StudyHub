import type { AssignmentTask } from './classService'

/**
 * Route applicative pour lancer une tâche de devoir depuis la vue élève.
 * Centralisé (et testé) pour rester cohérent entre les vues.
 */
export function taskLaunchRoute(task: Pick<AssignmentTask, 'task_type' | 'ref_uuid'>): string {
  const u = task.ref_uuid ?? ''
  switch (task.task_type) {
    case 'flashcards': return `/binders/${u}`
    case 'quiz': return `/notes/${u}/quiz`
    case 'blurting': return `/notes/${u}/blurting`
    case 'exam': return `/exam/setup?binder=${u}`
    case 'read': return `/notes/${u}`
    default: return `/binders/${u}`
  }
}
