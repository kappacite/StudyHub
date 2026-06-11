import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'
import { Capacitor } from '@capacitor/core'
import { LocalNotifications } from '@capacitor/local-notifications'

export type PomodoroPhase = 'work' | 'break' | 'idle'

export const usePomodoroStore = defineStore('pomodoro', () => {
  const phase = ref<PomodoroPhase>('idle')
  const remainingSeconds = ref(25 * 60)
  const sessionCount = ref(0)
  const isRunning = ref(false)

  // Configuration parameters
  const workMinutes = ref(25)
  const breakMinutes = ref(5)
  const longBreakMinutes = ref(15)
  const longBreakInterval = ref(4)
  const enableSound = ref(true)
  const enableNotifications = ref(true)

  let timerInterval: ReturnType<typeof setInterval> | null = null

  // Web Audio synth alert
  function playAlertSound() {
    if (!enableSound.value) return
    try {
      const ctx = new (window.AudioContext || (window as any).webkitAudioContext)()
      // Play a nice double chime
      const playChime = (time: number, freq: number) => {
        const osc = ctx.createOscillator()
        const gain = ctx.createGain()
        osc.type = 'sine'
        osc.frequency.setValueAtTime(freq, time)
        gain.gain.setValueAtTime(0.4, time)
        gain.gain.exponentialRampToValueAtTime(0.001, time + 0.4)
        osc.connect(gain)
        gain.connect(ctx.destination)
        osc.start(time)
        osc.stop(time + 0.4)
      }
      playChime(ctx.currentTime, 523.25) // C5
      playChime(ctx.currentTime + 0.15, 659.25) // E5
    } catch (e) {
      console.error('Failed to play synthesized sound', e)
    }
  }

  // Push notifications
  async function triggerNotification(title: string, body: string) {
    if (!enableNotifications.value) return
    
    if (Capacitor.isNativePlatform()) {
      try {
        const perm = await LocalNotifications.checkPermissions()
        if (perm.display !== 'granted') {
          await LocalNotifications.requestPermissions()
        }
        await LocalNotifications.schedule({
          notifications: [
            {
              title,
              body,
              id: Date.now(),
              sound: 'beep.wav',
              extra: null
            }
          ]
        })
      } catch (e) {
        console.error('Failed to trigger native notification', e)
      }
    } else if ('Notification' in window) {
      try {
        if (Notification.permission === 'granted') {
          new Notification(title, { body })
        } else if (Notification.permission !== 'denied') {
          const permission = await Notification.requestPermission()
          if (permission === 'granted') {
            new Notification(title, { body })
          }
        }
      } catch (e) {
        console.error('Failed to trigger browser notification', e)
      }
    }
  }

  // Log completed session to API
  async function logStudySession(durationSecs: number) {
    try {
      await api.post('/stats/sessions', {
        module: 'pomodoro',
        duration_seconds: durationSecs,
        cards_reviewed: 0,
        cards_correct: 0
      })
    } catch (err) {
      console.error('Erreur lors de l\'enregistrement de la session Pomodoro', err)
    }
  }

  function tick() {
    if (remainingSeconds.value > 0) {
      remainingSeconds.value--
    } else {
      // Timer finished! Transition to next phase
      playAlertSound()
      
      if (phase.value === 'work') {
        sessionCount.value++
        const loggedDuration = workMinutes.value * 60
        logStudySession(loggedDuration)
        
        triggerNotification(
          'Session terminée ! 🎯',
          `Félicitations, vous avez complété la session #${sessionCount.value}. C'est l'heure d'une pause !`
        )
        
        // Check if long break is due
        if (sessionCount.value % longBreakInterval.value === 0) {
          phase.value = 'break'
          remainingSeconds.value = longBreakMinutes.value * 60
        } else {
          phase.value = 'break'
          remainingSeconds.value = breakMinutes.value * 60
        }
      } else if (phase.value === 'break') {
        triggerNotification(
          'Pause terminée ! ⚡',
          'Prêt à vous remettre au travail ? C\'est reparti pour une nouvelle session !'
        )
        phase.value = 'work'
        remainingSeconds.value = workMinutes.value * 60
      }
    }
  }

  function start() {
    if (isRunning.value) return
    isRunning.value = true
    
    if (phase.value === 'idle') {
      phase.value = 'work'
      remainingSeconds.value = workMinutes.value * 60
    }
    
    if (timerInterval) clearInterval(timerInterval)
    timerInterval = setInterval(tick, 1000)
  }

  function pause() {
    isRunning.value = false
    if (timerInterval) {
      clearInterval(timerInterval)
      timerInterval = null
    }
  }

  function reset() {
    pause()
    phase.value = 'idle'
    remainingSeconds.value = workMinutes.value * 60
  }

  function skip() {
    // Force complete the current phase
    if (phase.value === 'work') {
      sessionCount.value++
      logStudySession(workMinutes.value * 60 - remainingSeconds.value)
      
      if (sessionCount.value % longBreakInterval.value === 0) {
        phase.value = 'break'
        remainingSeconds.value = longBreakMinutes.value * 60
      } else {
        phase.value = 'break'
        remainingSeconds.value = breakMinutes.value * 60
      }
    } else if (phase.value === 'break') {
      phase.value = 'work'
      remainingSeconds.value = workMinutes.value * 60
    } else {
      phase.value = 'work'
      remainingSeconds.value = workMinutes.value * 60
    }
  }

  function saveSettings(
    workMins: number, 
    breakMins: number, 
    longBreakMins: number, 
    sound: boolean, 
    notifs: boolean
  ) {
    workMinutes.value = workMins
    breakMinutes.value = breakMins
    longBreakMinutes.value = longBreakMins
    enableSound.value = sound
    enableNotifications.value = notifs

    // If currently idle, apply the new work minutes to remainingSeconds
    if (phase.value === 'idle') {
      remainingSeconds.value = workMins * 60
    }
  }

  return {
    phase,
    remainingSeconds,
    sessionCount,
    isRunning,
    workMinutes,
    breakMinutes,
    longBreakMinutes,
    longBreakInterval,
    enableSound,
    enableNotifications,
    start,
    pause,
    reset,
    skip,
    saveSettings
  }
})
