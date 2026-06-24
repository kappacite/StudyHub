# Application mobile (Capacitor)

> Coque mobile Android/iOS qui **réutilise le build web** (`web/`) sans réécriture.
> Skill associé : `mobile-build`.

## Pourquoi Capacitor

Un seul codebase front (Vue 3) sert le web, le bureau (Electron) et le mobile
(Capacitor). Le code Vue n'est jamais dupliqué : le conditionnel natif passe par
`usePlatform()` (`isNative`).

```
[Bureau: Electron] ─┐
[Mobile: Capacitor] ─┴ wraps → [Web: Vue + Vite] ←→ [API REST: Flask] ←→ [PostgreSQL]
```

## Emplacement

Capacitor est enraciné dans **`web/`** (config + CLI + plugins dans le même package —
résolution des plugins sans friction). Le projet natif Android est généré dans
**`web/android`** (le projet iOS sera `web/ios`, à créer sur un Mac).

| Fichier / dossier | Rôle |
|---|---|
| `web/capacitor.config.ts` | Config Capacitor (appId, appName, webDir, scheme, plugins). |
| `web/android/` | Projet natif Android (Gradle) — commité. |
| `web/dist/` | Build web copié dans `web/android/app/src/main/assets/public` par `cap sync`. |

## Deux contraintes spécifiques mobile

### 1. Routing — history HTML5 conservée
Avec `androidScheme: 'https'`, l'app est servie depuis `https://localhost` (vraie
origine HTTP) : l'history HTML5 (`createWebHistory`) fonctionne. **Pas de hash history**
(contrairement au desktop Electron servi en `app://`).

### 2. API — pas de Nginx + CORS
En natif il n'y a pas de proxy : le script `build:mobile` injecte
`VITE_API_BASE_URL=https://study.leshen.cloud` (lu par `web/src/services/api.ts`).
Les origines natives sont autorisées dans `CORS_ALLOWED_ORIGINS`
(`backend/app/__init__.py`) :
- **Android** : `https://localhost`
- **iOS** : `capacitor://localhost`

## Build & exécution

```bash
cd web
npm run build:mobile      # build front (API prod injectée)
npm run cap:sync          # build:mobile + cap sync android
npm run cap:android       # ouvre Android Studio
npx cap run android       # émulateur / appareil
```

⚠️ Toujours `cap sync android` après un build avant de tester natif.

## Dev avec live-reload (optionnel)

Pour itérer sans rebuild à chaque fois, pointer Capacitor vers le serveur Vite via
`server.url` dans `capacitor.config.ts` (IP du poste de dev, ex.
`http://192.168.x.x:5173`) puis `npx cap run android`. Penser à ajouter cette origine
au CORS dev. Ne pas committer `server.url`.

## Reste à faire

- **Compilation APK** : nécessite le SDK Android (Android Studio) ou un job CI ; non
  réalisable sans SDK. → `npx cap open android` puis build, ou pipeline CI.
- Icône & splash screen (`@capacitor/assets`).
- Plateforme **iOS** (`npx cap add ios`) — Mac + Xcode requis.
- Tests sur émulateur / appareil réel.
