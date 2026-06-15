import type { AssignmentTask } from './classService'

/**
 * Route applicative pour lancer une tâche de devoir depuis la vue élève.
 * Centralisé (et testé) pour rester cohérent entre les vues.
 */
export function taskLaunchRoute(task: Pick<AssignmentTask, 'task_type' | 'ref_uuid' | 'ref_id'>): string {
  const u = task.ref_uuid ?? ''
  switch (task.task_type) {
    case 'flashcards': return `/binders/${u}`
    case 'quiz': return `/notes/${u}/quiz`
    case 'blurting': return `/notes/${u}/blurting`
    case 'exam': return `/exam/setup?binder=${u}`
    case 'read': return `/notes/${u}`
    // Ensemble de révision : identifié par ref_id (pas d'UUID public). La page
    // d'étude redirige les QCM vers leur passage scoré.
    case 'revision': return `/revision/sets/${task.ref_id}/study`
    default: return `/binders/${u}`
  }
}
