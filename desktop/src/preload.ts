import { contextBridge } from 'electron'

// Version applicative passée par le main via additionalArguments.
const versionArg = process.argv.find((arg) => arg.startsWith('--app-version='))
const version = versionArg ? versionArg.split('=')[1] : '0.0.0'

// Pont minimal exposé au renderer (web/src/composables/usePlatform.ts le lit).
// Aucun accès Node/Electron direct n'est exposé.
contextBridge.exposeInMainWorld('studyhub', {
  isDesktop: true,
  version,
})
