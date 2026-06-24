import { app, BrowserWindow, shell } from 'electron'
import path from 'node:path'

// En dev, on charge le serveur Vite (HMR) ; en prod (packagé), on sert le build
// statique web/dist via electron-serve sous le protocole custom app://-.
const isDev = !app.isPackaged
const DEV_SERVER_URL = process.env.VITE_DEV_SERVER_URL ?? 'http://localhost:5173'

function isInternalUrl(url: string): boolean {
  return url.startsWith('app://') || url.startsWith(DEV_SERVER_URL)
}

async function createWindow(): Promise<void> {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 960,
    minHeight: 600,
    title: 'StudyHub',
    backgroundColor: '#0f172a',
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      // Expose la version applicative au preload sans accès Node au renderer.
      additionalArguments: [`--app-version=${app.getVersion()}`],
    },
  })

  // Les liens http(s) externes s'ouvrent dans le navigateur par défaut, jamais
  // dans la fenêtre de l'app (et on ne crée pas de nouvelle fenêtre Electron).
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http://') || url.startsWith('https://')) {
      void shell.openExternal(url)
    }
    return { action: 'deny' }
  })
  win.webContents.on('will-navigate', (event, url) => {
    if (!isInternalUrl(url)) {
      event.preventDefault()
      if (url.startsWith('http')) void shell.openExternal(url)
    }
  })

  if (isDev) {
    await win.loadURL(DEV_SERVER_URL)
    win.webContents.openDevTools({ mode: 'detach' })
  } else {
    // electron-serve est ESM-only : import dynamique depuis ce module CommonJS.
    const serve = (await import('electron-serve')).default
    const loadURL = serve({ directory: path.join(process.resourcesPath, 'web-dist') })
    await loadURL(win)
  }
}

app.whenReady().then(createWindow)

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) void createWindow()
})

app.on('window-all-closed', () => {
  // Convention macOS : l'app reste active sans fenêtre ; ailleurs on quitte.
  if (process.platform !== 'darwin') app.quit()
})
