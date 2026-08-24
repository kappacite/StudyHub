---
name: cycle-tdd
description: Forme canonique d'un cycle TDD sur StudyHub — gabarits pytest (DAO/service/route) et vitest (store Pinia/composant/intégration), conventions de nommage, anti-patterns interdits. À charger avant d'écrire un test, actif à partir de la phase 3 (voir ETAT.md).
---

# cycle-tdd

Rappel du cycle (détail complet des règles : `CLAUDE.md`, `AGENTS.md` §7) : **Réfléchir**
(comportement attendu, cas limites, écrit avant le premier test) → **Rouge** (le test échoue
pour la bonne raison, pas un `ImportError`) → **Vert** (minimum de code) → **Refactor** (à
tests verts). Un cycle = un comportement.

## Backend — pytest

Fixtures disponibles (`backend/tests/conftest.py`) : `app` (SQLite mémoire par défaut, ou
PostgreSQL si `TEST_DATABASE_URL`), `clean_db` (autouse — `create_all`/`drop_all` par test,
isolation garantie), `client` (client de test Flask), `test_user`/`auth_headers`.

- **DAO** : instancier directement avec `db.session` dans un `app.app_context()`, pas de
  requête HTTP — teste la requête SQL, pas la couche HTTP.
- **Service** : DAO réel contre la base de test (pas de mock du DAO — c'est le sujet
  d'intégration naturel, la base SQLite mémoire est déjà rapide et isolée) ; mock seulement les
  dépendances externes (appel Gemini, horloge via `freezegun` si le temps compte).
- **Route** : `client.post("/api/v1/...", json=..., headers=auth_headers)` — teste le code
  HTTP, le format de réponse, et l'isolation (un autre `user_id` ne doit rien voir).
- Gabarit complet réel à copier : `backend/tests/test_tags.py` (skill `conventions-dao` pour
  le module qu'il teste).

## Frontend — vitest

- **Store Pinia** : `setActivePinia(createPinia())` en `beforeEach`, mock du module
  `services/api` via `vi.hoisted` + `vi.mock` (jamais d'appel réseau réel). Gabarit :
  `web/tests/stores/notifications.spec.ts`.
- **Composant** : `mount()` de `@vue/test-utils` (**pas** Vue Testing Library — absent du
  dépôt), assertions sur `wrapper.text()`, `wrapper.find()`, `wrapper.emitted()`. Couvre états,
  variantes de props, interactions (`trigger('click')`), pas seulement le rendu par défaut.
  Gabarit : `web/tests/components/TagBadge.spec.ts`.
- **Intégration** (parcours critique) : Playwright, `web/tests-e2e/*.spec.ts`.

## Anti-patterns interdits

- Affaiblir une assertion pour faire passer un test (`toBeTruthy()` à la place d'une valeur
  précise attendue).
- Mocker le sujet testé lui-même (mocker le service alors que c'est le service qu'on teste).
- `sleep`/temporisation pour masquer une course — utiliser `await`/`flushPromises`/fixtures
  déterministes (`freezegun` côté backend).
- Adapter le test à une implémentation qui ne marche pas : le test est la spécification.

## Emplacement et nommage

Backend : `backend/tests/test_<module>.py`, fonctions `def test_<comportement>():`.
Frontend : `web/tests/{stores,components,composables,services,ui}/<Nom>.spec.ts`, miroir de
`web/src/`. E2E : `web/tests-e2e/<parcours>.spec.ts`.
