import { Capacitor } from '@capacitor/core'

/**
 * Pont exposé par le preload Electron (desktop/src/preload.ts) via contextBridge.
 * Absent sur web et mobile.
 */
interface StudyHubDesktopBridge {
  isDesktop: true
  version: string
}

declare global {
  interface Window {
    studyhub?: StudyHubDesktopBridge
  }
}

export function usePlatform() {
  const isNative = Capacitor.isNativePlatform()
  const platform = Capacitor.getPlatform() // 'web' | 'ios' | 'android'
  // Desktop = coque Electron. Le pont preload est la source fiable ; on retombe sur
  // l'user-agent ('Electron') au cas où le preload ne serait pas encore prêt.
  const isDesktop =
    window.studyhub?.isDesktop === true ||
    (typeof navigator !== 'undefined' && navigator.userAgent.includes('Electron'))
  return { isNative, platform, isDesktop }
}
