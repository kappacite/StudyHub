# StudyHub — Application d'étude tout-en-un

> Règles **toujours actives**, courtes par construction (≤60 lignes). `AGENTS.md` fait autorité
> sur l'architecture — en cas de doute, c'est lui qui gagne. Détail par couche : **skills**
> (chargées à la demande) et `docs/`. Ne duplique pas ce contenu ici.

## Carte du projet — où trouver quoi

| Tu travailles sur… | Charge le skill | Référence canonique |
|---|---|---|
| `backend/` (dao, services, api, models, schemas) | `backend-patterns` | `docs/backend.md` |
| `web/src` (views, components, stores, services) | `frontend-patterns` | `docs/frontend.md`, `docs/design-system.md` |
| Routes / contrats d'endpoints | `api-spec` | `docs/api_reference.md` |
| `web/android`, Capacitor, comportements natifs | `mobile-build` | `docs/mobile.md` |
| `desktop/`, Electron, packaging bureau | `desktop-build` | `docs/desktop.md` |
| Docker, CI/CD, migrations, multi-arch | `deployment` | `docs/migrations.md`, `docs/ENVIRONNEMENT.md` |

Journal : `docs/development_journal.md` · Roadmap : `docs/FEATURES.md` · Phase courante : `ETAT.md`.

## Stack (détail : AGENTS.md §2)

Backend Python 3.12/Flask 3/SQLAlchemy 2 (DAO)/PostgreSQL·SQLite/JWT/Alembic/Pydantic v2/Celery+Redis.
Web Vue 3 `<script setup>`/Vite 5/Tailwind 3/Pinia/Vue Router 4/Axios/KaTeX/marked+DOMPurify.
Mobile Capacitor 8 (`web/android`) · Bureau Electron (`desktop/`) · IA Gemini.

## Architecture, isolation, TDD (détail complet : AGENTS.md §4, §7)

`Request → Middleware → API → Service → DAO → Model → PostgreSQL`. DAO n'importe jamais de
service ; service jamais de SQL/ORM direct ; route jamais de logique métier. Tout DAO qui liste
filtre par `user_id` ; vérifier l'appartenance avant update/delete. Routes protégées par JWT
**sauf** `auth/*` et `health`. **Dès que `ETAT.md` indique phase ≥ 3** : le test précède le code
sans exception (skill `cycle-tdd`) ; jamais de test affaibli pour le faire passer.

## Conventions

| Contexte | Convention |
|---|---|
| Python | `snake_case` (vars/fns), `PascalCase` (classes), fichiers `snake_case.py` |
| TypeScript | `camelCase` (vars/fns), `PascalCase` (classes/composants) |
| Fichiers Vue | `PascalCase.vue` · composables `useX.ts` · stores `x.ts` · services `xService.ts` |
| Endpoints | `kebab-case` (`/study-sessions`), préfixe `/api/v1/` |

**Commits** — Conventional Commits, corps en français. **Branches** : `main` protégée (PR obligatoire) · `develop` · `feature/*` · `fix/*`.

## Codes HTTP, erreurs, interdictions

200/201/204/400/401/403/404/409/500 (lecture/création/sans-contenu/validation/non-auth/interdit/introuvable/conflit/serveur). Erreur unique : `{ "error": { "code", "message", "details": {} } }`.
❌ Logique métier en route · SQL direct en service · appel API dans `components/ui/` · `any` TS ·
debug oublié/secret en dur *(hooks PostToolUse)* · endpoint sans JWT · **`git push`** en toute
circonstance *(hook PreToolUse bloquant)*.

## Checklist avant PR

Commit après chaque modif · `docs/` + journal + `ETAT.md` à jour.
**Backend** : pas de logique en route · `user_id` filtré · codes HTTP corrects · Pydantic req/rép · coverage ≥ 80 % · migration si modèle modifié.
**Web** : `<script setup lang="ts">` · API dans stores/services seulement · responsive 375/1440px · mode sombre · états loading/error/empty. **Mobile** : `usePlatform()` · `npx cap sync` · testé Android + iOS.

---

*Phases : 0 (reco) → 1 (outillage) → 2 (audit) → 3 (design) → 4 (UI) → 5 (diagrammes) — phase active : `ETAT.md`, détail complet des phases : `docs/PROMPT_DEMARRAGE.md`. Décision d'archi majeure → `AGENTS.md` + skill/doc concerné, même commit.*
