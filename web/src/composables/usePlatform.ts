import { Capacitor } from '@capacitor/core'

export function usePlatform() {
  const isNative = Capacitor.isNativePlatform()
  const platform = Capacitor.getPlatform() // 'web' | 'ios' | 'android'
  return { isNative, platform }
}
