---
name: desktop-build
description: Coque bureau Electron StudyHub (desktop/, hash history, electron-serve app://, CORS app://-, electron-builder). À charger avant de toucher desktop/, le packaging bureau ou un comportement Electron.
---

# desktop-build

Référence canonique : `docs/desktop.md`. Electron encapsule le **build web** (`web/`) sans
réécriture. Même codebase Vue 3 que web/mobile.

## Structure (`desktop/`)

| Fichier | Rôle |
|---|---|
| `src/main.ts` | Process principal : `BrowserWindow`, chargement, sécurité. |
| `src/preload.ts` | `contextBridge` → expose `window.studyhub` (`isDesktop`, `version`). |
| `electron-builder.yml` | Cibles de packaging Linux/Windows/macOS. |
| `build/icon.png` | Icône source ≥512px. |

`dist/` (compilé) et `release/` (installeurs) sont gitignored.

## Dev vs prod (renderer)

- **Dev** (`!app.isPackaged`) → `loadURL('http://localhost:5173')` (Vite HMR), DevTools ouverts,
  backend `http://localhost:5000`.
- **Prod** (packagé) → `web/dist` copié hors asar (`extraResources` → `web-dist`), servi par
  `electron-serve` sous `app://-`. `electron-serve` est **ESM-only** → import dynamique depuis le
  main CommonJS : `(await import('electron-serve')).default`.

## Trois contraintes desktop

1. **Routing — hash history** : `createWebHistory` casse en `app://`. Le router bascule en
   `createWebHashHistory` quand `VITE_DESKTOP=true` (`web/src/router/index.ts`). Le web reste HTML5.
2. **API** : pas de Nginx ⇒ le build desktop renseigne `VITE_API_BASE_URL=https://study.leshen.cloud`.
3. **CORS** : le renderer packagé émet `Origin: app://-` → ajouter à `CORS_ALLOWED_ORIGINS`
   (`backend/app/__init__.py` + env prod). Vérifier l'Origin réelle au 1er lancement packagé.

## Sécurité (ne pas relâcher)

`contextIsolation: true`, `nodeIntegration: false`, `sandbox: true`. Le preload n'expose qu'un
objet minimal. Liens externes via `shell.openExternal`, jamais dans la fenêtre app.

## Build & packaging

```bash
cd desktop && npm install
npm run dev          # Vite + Electron (HMR)
npm run dist         # build web (desktop) + tsc + installeur OS courant
npm run dist:linux   # AppImage + deb
npm run dist:win     # NSIS .exe (buildable sous Linux/CI)
npm run dist:mac     # dmg (Mac requis pour signature)
```

⚠️ Cible `deb` sous Fedora/Nobara : `fpm` réclame `libcrypt.so.1` →
`sudo dnf install libxcrypt-compat`. L'AppImage se construit sans. Sortie : `desktop/release/`.
