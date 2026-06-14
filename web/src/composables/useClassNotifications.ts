import { Capacitor } from '@capacitor/core'
import type { AssignmentSummary } from '../services/classService'

/**
 * Programmation de rappels locaux (mobile) pour les deadlines de devoirs.
 * Sans infra serveur : on s'appuie sur @capacitor/local-notifications, planifiées
 * côté client à partir des dates limites. No-op sur le web.
 */
export function useClassNotifications() {
  async function scheduleDueReminders(assignments: AssignmentSummary[]) {
    if (!Capacitor.isNativePlatform()) return
    try {
      const { LocalNotifications } = await import('@capacitor/local-notifications')
      const perm = await LocalNotifications.requestPermissions()
      if (perm.display !== 'granted') return

      const now = Date.now()
      const notifications = assignments
        .filter(a => a.due_date && a.status !== 'done')
        .map(a => ({ a, remindAt: new Date(a.due_date as string).getTime() - 24 * 3600 * 1000 }))
        .filter(x => x.remindAt > now)
        .map(x => ({
          id: x.a.id,
          title: 'Devoir à rendre demain',
          body: x.a.title,
          schedule: { at: new Date(x.remindAt) },
        }))

      if (notifications.length) {
        await LocalNotifications.schedule({ notifications })
      }
    } catch {
      // Plugin indisponible / permission refusée : on ignore silencieusement.
    }
  }

  return { scheduleDueReminders }
}
