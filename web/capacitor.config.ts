import type { CapacitorConfig } from '@capacitor/cli'

// La coque mobile réutilise le build web (webDir 'dist') sans réécriture.
// androidScheme 'https' → l'app est servie depuis https://localhost (vraie origine
// HTTP) : l'history HTML5 du router fonctionne, et l'origine CORS est https://localhost.
const config: CapacitorConfig = {
  appId: 'com.studyhub.app',
  appName: 'StudyHub',
  webDir: 'dist',
  server: { androidScheme: 'https' },
  plugins: {
    LocalNotifications: { smallIcon: 'ic_stat_icon', iconColor: '#4F46E5' },
  },
}

export default config
