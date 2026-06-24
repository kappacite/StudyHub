# StudyHub — Application d'étude tout-en-un

> Règles **toujours actives**. Le détail (patterns, spec API, déploiement) vit dans
> des **skills** chargés à la demande et dans `docs/`. Charge le skill correspondant
> avant de travailler sur une couche. Ne duplique pas ce contenu ici.

## Carte du projet — où trouver quoi

| Tu travailles sur… | Charge le skill | Référence canonique |
|---|---|---|
| `backend/` (dao, services, api, models, schemas) | `backend-patterns` | `docs/backend.md` |
| `web/src` (views, components, stores, services) | `frontend-patterns` | `docs/frontend.md`, `docs/design-system.md` |
| Routes / contrats d'endpoints | `api-spec` | `docs/api_reference.md` |
| `mobile/`, Capacitor, comportements natifs | `mobile-build` | — |
| `desktop/`, Electron, packaging bureau | `desktop-build` | `docs/desktop.md` |
| Docker, CI/CD, migrations de déploiement | `deployment` | `docs/deployment.md`, `docs/migrations.md` |

Journal de dev : `docs/development_journal.md` · Fonctionnalités : `docs/FEATURES.md`.

## Stack (résumé)

- **Backend** : Python 3.12 · Flask 3 · SQLAlchemy 2 (pattern DAO) · PostgreSQL 16 (prod) / SQLite (dev) · JWT (`flask-jwt-extended`) · Alembic · Pydantic v2 · Pytest.
- **Web** : Vue 3 (Composition API, `<script setup>`) · Vite 5 · TailwindCSS 3 + HeadlessUI · Pinia · Vue Router 4 · Axios · Tiptap, Mermaid.js, PDF.js · Vitest.
- **Mobile** : Capacitor 6 encapsule le build web (un seul codebase `web/`). iOS 16+ / Android 10+.
- **Bureau** : Electron encapsule le build web (`desktop/`, electron-builder). Windows / macOS / Linux.
- **IA** : Gemini (Blurting / feuille blanche).

```
[Bureau: Electron] ─┐
[Mobile: Capacitor] ─┴ wraps → [Web: Vue + Vite] ←→ [API REST: Flask] ←→ [PostgreSQL]
```

## Modules

Flashcards (SM-2) · Notes (Markdown/WYSIWYG) · Diagrammes · PDF · Classeurs (arborescence) · Dashboard (sessions, stats, objectifs).

## Architecture en couches — règle stricte

```
Request → Middleware → API (route) → Service → DAO → Model → PostgreSQL
```

- **DAO** : ne connaît que modèles SQLAlchemy + session. N'importe **jamais** un service.
- **Service** : ne connaît que DAO + schémas Pydantic. **Jamais** de SQL direct.
- **Route** : **aucune** logique métier. Valide (Pydantic), délègue au service, renvoie `jsonify` + code HTTP.
- **Middleware** : transversal, pas de logique applicative.

SOLID : un DAO = une entité ; un service = une logique métier ; DAO injecté dans le service (jamais d'import direct) ; schémas Pydantic requête/réponse séparés.

## Isolation des données (règle absolue)

Tout DAO qui liste filtre par `user_id`. Vérifier l'appartenance avant tout update/delete.
Aucune ressource d'un utilisateur n'est accessible par un autre. Toutes les routes sont
protégées par JWT **sauf** `auth/*` et `health`.

## Conventions

| Contexte | Convention |
|---|---|
| Python | `snake_case` (vars/fns), `PascalCase` (classes), fichiers `snake_case.py` |
| TypeScript | `camelCase` (vars/fns), `PascalCase` (classes/composants) |
| Fichiers Vue | `PascalCase.vue` · composables `useX.ts` · stores `x.ts` · services `xService.ts` |
| Endpoints | `kebab-case` (`/study-sessions`), préfixe `/api/v1/` |
| Env | `SCREAMING_SNAKE_CASE` |

**Commits** — Conventional Commits : `feat(scope): …`, `fix(auth): …`, `refactor(dao): …`, `docs`, `test`, `chore`.
**Branches** : `main` (prod, protégée — PR obligatoire), `develop`, `feature/*`, `fix/*`, `release/*`.

## Codes HTTP & erreurs

200 lecture · 201 création · 204 sans contenu · 400 validation · 401 non auth · 403 interdit · 404 introuvable · 409 conflit · 500 serveur.

Format d'erreur unique : `{ "error": { "code", "message", "details": {} } }` (handler global).

## Interdictions strictes

- ❌ Logique métier dans les routes Flask
- ❌ SQL direct dans les services
- ❌ Appels API dans `components/ui/`
- ❌ `any` en TypeScript
- ❌ `console.log` / `print` de debug *(un hook PostToolUse le signale)*
- ❌ Secrets en dur — utiliser `.env` *(un hook PostToolUse le signale)*
- ❌ Endpoints sans JWT (sauf auth + health)

## Checklist avant PR

**Process** : commit après chaque modification · `docs/` mis à jour · `docs/development_journal.md` enrichi.
**Backend** : routes sans logique métier · filtrage `user_id` · bons codes HTTP · schémas Pydantic req/rép · tests (coverage ≥ 80 %) · migration Alembic si modèle modifié · aucun secret en dur.
**Web** : `<script setup lang="ts">` · API seulement dans stores/services · responsive 375px + 1440px · mode sombre · états loading/error/empty.
**Mobile** : `usePlatform()` pour le conditionnel · `npx cap sync` après build · testé Android + iOS.
**Global** : commit conforme · pas de debug · `.env.example` à jour si nouvelle variable.

---

*Détail architectural complet historisé via git (ancien AGENTS.md monolithique) et réparti
entre `.claude/skills/` et `docs/`. Toute décision d'archi majeure doit être reflétée ici
ET dans le skill/doc concerné.*
