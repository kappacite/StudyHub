# Application bureau (Electron)

> Coque bureau Windows / macOS / Linux qui **réutilise le build web** (`web/`) sans
> réécriture. Skill associé : `desktop-build`.

## Pourquoi Electron

Un seul codebase front (Vue 3) sert le web, le mobile (Capacitor) et le bureau
(Electron). Déploiement bureau rapide : on package le build statique existant, sans
réimplémenter l'UI.

```
[Bureau: Electron] ─┐
[Mobile: Capacitor] ─┼─ wraps ─→ [Web: Vue + Vite] ←→ [API REST: Flask] ←→ [PostgreSQL]
```

## Structure (`desktop/`)

| Fichier | Rôle |
|---|---|
| `src/main.ts` | Process principal : crée la `BrowserWindow`, gère le chargement et la sécurité. |
| `src/preload.ts` | Pont `contextBridge` exposant `window.studyhub` (`isDesktop`, `version`). |
| `electron-builder.yml` | Config de packaging (cibles Linux/Windows/macOS). |
| `build/icon.png` | Icône source ≥512px (mac `.icns` / win `.ico` dérivés auto). |
| `tsconfig.json` | Compile `src/` → `dist/` (CommonJS, `tsc`). |

`dist/` (compilé) et `release/` (installeurs) sont gitignored.

## Chargement renderer : dev vs prod

- **Dev** (`!app.isPackaged`) → `loadURL('http://localhost:5173')` (serveur Vite, HMR),
  DevTools ouverts. Backend par défaut `http://localhost:5000`.
- **Prod** (packagé) → `web/dist` est copié hors asar (`extraResources` → `web-dist`)
  et servi par `electron-serve` sous `app://-`. Lu depuis `process.resourcesPath`.

`electron-serve` est ESM-only : il est chargé par **import dynamique** depuis le main
CommonJS (`(await import('electron-serve')).default`).

## Trois contraintes spécifiques desktop

### 1. Routing — hash history
L'history HTML5 (`createWebHistory`) casse hors d'un serveur HTTP (rechargement /
deep-link en `app://`). Le router bascule en `createWebHashHistory` quand le flag de
build `VITE_DESKTOP=true` est présent (`web/src/router/index.ts`). Le web reste en
history HTML5.

### 2. API — pas de Nginx
En web prod, `api.ts` utilise l'URL relative `/api/v1` proxifiée par Nginx. En desktop
il n'y a pas de proxy : le build desktop renseigne `VITE_API_BASE_URL` vers le backend
hébergé (`https://study.leshen.cloud`).

### 3. CORS — origine `app://-`
Le renderer packagé émet ses requêtes avec `Origin: app://-`. Cette origine est ajoutée
à la whitelist `CORS_ALLOWED_ORIGINS` (`backend/app/__init__.py`, et la variable d'env
correspondante en prod).
> ⚠️ Au premier lancement packagé, vérifier l'`Origin` réellement émise (DevTools /
> logs backend) et l'ajuster si `electron-serve` change de schéma.

## Sécurité

`contextIsolation: true`, `nodeIntegration: false`, `sandbox: true`. Le preload
n'expose qu'un objet minimal. Les liens http(s) externes s'ouvrent dans le navigateur
par défaut (`shell.openExternal`), jamais dans la fenêtre de l'app.

## Build & packaging

```bash
cd desktop && npm install
npm run dev          # Vite + Electron (HMR)
npm run dist         # build web (desktop) + tsc + installeur de l'OS courant
npm run dist:linux   # AppImage + deb
npm run dist:win     # NSIS .exe   (buildable sous Linux/CI)
npm run dist:mac     # dmg         (Mac requis pour signature/notarisation)
```

`build:web` injecte `VITE_DESKTOP=true` et `VITE_API_BASE_URL=https://study.leshen.cloud`
puis lance le build de `web/`. Sortie des installeurs : `desktop/release/`.

> ⚠️ **Cible `deb` sous Fedora/Nobara** : le `fpm` embarqué par electron-builder utilise
> un Ruby qui réclame `libcrypt.so.1`, absente par défaut. Installer le paquet de
> compat (`sudo dnf install libxcrypt-compat`) pour produire le `.deb` localement.
> L'**AppImage** (cible portable principale) se construit sans cette dépendance, et le
> `.deb` se construit normalement en CI (Debian/Ubuntu).

## Reste à faire

- Icône définitive (placeholder dérivé de `web/public/favicon.svg`).
- Signature/notarisation macOS et signature Windows.
- Build Windows/macOS en CI (auto-update éventuel).
