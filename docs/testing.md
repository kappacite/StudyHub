# Stratégie de tests & gate anti-régression — StudyHub

Ce document décrit la stratégie de tests et le mécanisme qui **empêche de fusionner
une version qui casse les fonctionnalités existantes**.

## Flux de contribution (obligatoire)

`main` est protégée : **aucun push direct**. Toute modification passe par une PR.

```
feature/* ──PR──▶ develop ──PR──▶ main
                    │                │
                    └── CI requise verte avant merge ──┘
```

La CI (`.github/workflows/ci.yml`) s'exécute sur chaque PR et push vers
`main`/`develop`. Les checks doivent être **verts** pour fusionner.

## Pyramide de tests

| Niveau | Outil | Portée | État |
|---|---|---|---|
| Unitaire backend | pytest | Services (SM-2, parseurs), schémas Pydantic, DAO | ✅ partiel |
| Intégration backend | pytest + test_client | Endpoints route→service→dao→db, isolation `user_id`, codes HTTP | ✅ 96 tests |
| Non-régression backend | pytest (`test_regression.py`) | Parcours critiques figés | ✅ |
| Migrations | `flask db upgrade` sur PostgreSQL vierge | Chaîne Alembic complète | ✅ (CI) |
| Unitaire/composant frontend | Vitest + @vue/test-utils + happy-dom | Stores, composables, composants | ✅ socle (3 fichiers) |
| E2E / non-régression | Playwright | Parcours utilisateur bout-en-bout | ⏳ phase 3 |

## Lancer les tests en local

### Backend
```bash
cd backend
pip install -r requirements-dev.txt          # une fois
pytest                                        # tous les tests
pytest --cov=app --cov-report=term-missing    # avec couverture
```
Les tests tournent sur **SQLite en mémoire** (cf. `tests/conftest.py`) : rapides et
isolés, aucune base externe requise.

### Gate de couverture
Plancher CI actuel : **78 %** (baseline mesurée : 79 %, cible : **80 %+**).
La CI échoue sous le plancher (`pytest --cov-fail-under=78`). Configuration dans
`backend/pyproject.toml`.

### Frontend
```bash
cd web
npm ci                 # une fois
npm run test           # mode watch (vitest)
npm run test:run       # une passe (utilisé par la CI)
npm run test:coverage  # avec couverture
```
Environnement **happy-dom**, tests dans `web/tests/` (exclus du build `vue-tsc`).
Pas encore de plancher de couverture frontend (phase 4). ESLint : phase 4 également
(le code existant contient de nombreux `console.*`/`any` à traiter d'abord).

## Jobs CI

| Job | Rôle |
|---|---|
| `Backend · tests & coverage` | pytest + gate de couverture (SQLite mémoire) |
| `Backend · migrations (PostgreSQL)` | applique toutes les migrations sur une base Postgres vierge — attrape les régressions de migration |
| `Frontend · typecheck & build` | `vue-tsc` (typecheck) + build de production |
| `Frontend · unit tests (Vitest)` | tests unitaires/composants frontend |

## Feuille de route

- **Phase 0** ✅ — Socle couverture backend (pytest-cov, seuil, config).
- **Phase 1** ✅ — CI (backend + migrations + build front) + protection de branche / flux PR.
- **Phase 2** ✅ — Outillage frontend (Vitest + @vue/test-utils + happy-dom) + premiers tests (composable, composant, store). ESLint/MSW reportés en phase 4.
- **Phase 3** ⏳ — E2E Playwright sur les parcours critiques.
- **Phase 4** ⏳ — Durcissement : couverture front, hook `pre-push`, fabriques backend, montée du plancher à 80 %+.
