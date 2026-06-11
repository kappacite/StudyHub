import { computed } from 'vue'
import { usePomodoroStore } from '../stores/pomodoro'

export function usePomodoro() {
  const store = usePomodoroStore()

  const formattedTime = computed(() => {
    const minutes = Math.floor(store.remainingSeconds / 60)
    const seconds = store.remainingSeconds % 60
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
  })

  const progress = computed(() => {
    let totalSeconds = store.workMinutes * 60
    if (store.phase === 'work') {
      totalSeconds = store.workMinutes * 60
    } else if (store.phase === 'break') {
      const isLongBreak = store.sessionCount > 0 && store.sessionCount % store.longBreakInterval === 0
      totalSeconds = (isLongBreak ? store.longBreakMinutes : store.breakMinutes) * 60
    } else if (store.phase === 'idle') {
      totalSeconds = store.workMinutes * 60
    }
    
    if (totalSeconds <= 0) return 0
    return (1 - (store.remainingSeconds / totalSeconds)) * 100
  })

  return {
    phase: computed(() => store.phase),
    remainingSeconds: computed(() => store.remainingSeconds),
    sessionCount: computed(() => store.sessionCount),
    isRunning: computed(() => store.isRunning),
    workMinutes: computed(() => store.workMinutes),
    breakMinutes: computed(() => store.breakMinutes),
    longBreakMinutes: computed(() => store.longBreakMinutes),
    enableSound: computed(() => store.enableSound),
    enableNotifications: computed(() => store.enableNotifications),
    formattedTime,
    progress,
    start: store.start,
    pause: store.pause,
    reset: store.reset,
    skip: store.skip,
    saveSettings: store.saveSettings
  }
}
