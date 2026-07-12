---
name: mobile-build
description: Coque mobile Capacitor StudyHub (projet natif web/android, routing history, CORS natif, build:mobile + cap sync). À charger avant de toucher web/android, capacitor.config.ts ou un comportement natif.
---

# mobile-build

Référence canonique : `docs/mobile.md`. Capacitor 8 encapsule le **build web** (`web/`) sans
réécriture : un seul codebase Vue 3 sert web + desktop + mobile. Conditionnel natif via
`usePlatform()` (`isNative`) — jamais de duplication de code Vue.

## Emplacement (Capacitor enraciné dans `web/`)

| Fichier / dossier | Rôle |
|---|---|
| `web/capacitor.config.ts` | appId, appName, webDir, scheme, plugins. |
| `web/android/` | Projet natif Android (Gradle), **commité**. |
| `web/dist/` | Build web copié dans `web/android/app/src/main/assets/public` par `cap sync`. |

## Deux contraintes mobile

1. **Routing** : `androidScheme: 'https'` ⇒ servi depuis `https://localhost` (vraie origine HTTP),
   donc **history HTML5** (`createWebHistory`) fonctionne. Pas de hash history (≠ desktop Electron).
2. **API/CORS** : pas de Nginx en natif. `build:mobile` injecte
   `VITE_API_BASE_URL=https://study.leshen.cloud` (lu par `web/src/services/api.ts`). Origines natives
   autorisées dans `CORS_ALLOWED_ORIGINS` (`backend/app/__init__.py`) : Android `https://localhost`,
   iOS `capacitor://localhost`.

## Build & exécution

```bash
cd web
npm run build:mobile      # build front (API prod injectée)
npm run cap:sync          # build:mobile + cap sync android
npm run cap:android       # ouvre Android Studio
npx cap run android       # émulateur / appareil
```

⚠️ **Toujours `npx cap sync` après un build** avant de tester en natif (sinon l'APK sert un
ancien `dist/`).

## Live-reload (optionnel)

Pointer `server.url` (IP du poste, ex. `http://192.168.x.x:5173`) dans `capacitor.config.ts`,
ajouter cette origine au CORS dev, `npx cap run android`. **Ne pas committer `server.url`.**

## Reste à faire / limites

- Build APK : nécessite le SDK Android (Android Studio) ou un job CI — pas réalisable sans SDK.
- Icône/splash (`@capacitor/assets`). iOS (`npx cap add ios`) requiert un Mac + Xcode.
