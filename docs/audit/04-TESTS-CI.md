# Audit — Tests & CI (phase 2)

> Revue technique en lecture seule. Chaque constat : identifiant, emplacement `fichier:ligne`,
> description factuelle, impact, gravité **S1 (critique) → S4 (cosmétique)**, effort
> **XS/S/M/L**, piste de correction **non appliquée**. Aucune correction faite dans ce document.

## 1. Aptitude au TDD — mesures chiffrées

Le TDD (obligatoire à partir de la phase 3, `CLAUDE.md`) ne tient que si la boucle rouge/vert
est rapide. Chiffres mesurés en conditions réelles :

| Suite | Run complet | Run ciblé (1 fichier) | Source |
|---|---|---|---|
| Backend `pytest` (SQLite) | **56,4 s** (0 échec) | **2,9 s** (`tests/test_tags.py`) | `docs/ENVIRONNEMENT.md` (mesuré arm64 natif, même image Docker `studyhub-backend:latest` toujours en cache ; aucun fichier de test backend modifié depuis cette mesure — `git log -- backend/` confirmé) |
| Backend `pytest` (PostgreSQL réel) | 4 min 3 s — **12 échecs** | — | `docs/ENVIRONNEMENT.md`, voir TEST-01 |
| Frontend `vitest` | **2,9 s** (17 fichiers, 69 tests, 0 échec) | **2,6 s** (`tests/stores/notifications.spec.ts`) | **Re-mesuré à l'instant** (`npx vitest run`, Node v24.18.0 natif, hors conteneur) — cohérent avec `docs/ENVIRONNEMENT.md` (7,8 s / 2,8 s, même nombre de fichiers et de tests) |

**Verdict** : boucle exploitable pour le TDD sur les deux runtimes — run ciblé backend et
frontend tous deux < 3 s, très en dessous du seuil « quelques secondes » du prompt de
démarrage §5. `npm run test` (sans `run`) lance Vitest en mode watch par défaut — mode watch
exploitable confirmé côté frontend. Côté backend, aucun mode watch n'est configuré
(`pytest-watch`/`pytest-xdist --looponfail` absents de `requirements-dev.txt`) — non
bloquant vu la vitesse d'un run ciblé, mais un `pytest --lf` (dernier échec) ou un watcher
raccourcirait encore la boucle. Voir TEST-07.

Isolation : `clean_db` (`backend/tests/conftest.py:21-27`) recrée et détruit tout le schéma à
chaque test (`db.create_all()`/`db.drop_all()`, autouse, scope function) — isolation réelle,
pas de fuite d'état observée entre tests. `app` est en scope `session` (`conftest.py:7`) mais
ne porte pas de données, seulement la config Flask — sans risque de fuite.

## 2. CI existante — vérification (pas supposition)

`.github/workflows/ci.yml` confirme la description de la phase 1 : **6 jobs**, tous déclenchés
sur `push`/`pull_request` vers `main`/`develop`, `concurrency` avec annulation des runs
obsolètes (`ci.yml:11-13`) :

| Job | Rôle | Constat |
|---|---|---|
| `backend-tests` | pytest + coverage SQLite | `--cov-fail-under=80` réel (`ci.yml:41`) — gate bloquante confirmée |
| `backend-tests-postgres` | pytest contre PostgreSQL réel | **rouge en l'état** — voir TEST-01 |
| `migrations` | migrations à blanc + garde anti-drift | `flask db migrate` + échec si autogenerate produit un fichier (`ci.yml:137-145`) — garde réelle, pas déclarative |
| `frontend-build` | typecheck (`vue-tsc -b`) + build Vite | pas de coverage concernée |
| `frontend-tests` | `npm run test:run` (Vitest) | **aucune gate de couverture** — voir TEST-02 |
| `e2e` | Playwright, Chromium seul | 5 specs (`web/tests-e2e/*.spec.ts`) — voir TEST-04 pour la couverture réelle des parcours |

La CI est donc bien mature comme annoncé, avec une exception réelle (TEST-01) et une lacune
documentée mais non comblée (TEST-02).

## 3. Constats

### TEST-01 — Job CI `backend-tests-postgres` rouge en permanence (12 échecs)
**Emplacement** : `.github/workflows/ci.yml:43-83` (job) ; `backend/tests/conftest.py:21-27`
(fixture `clean_db` en cause) ; détail des 12 échecs déjà consigné dans
`docs/ENVIRONNEMENT.md:61-72`.
**Description** : `clean_db` construit le schéma de test via `db.create_all()` (métadonnées
SQLAlchemy), qui ne pose pas les objets définis uniquement en SQL brut dans les migrations
Alembic — au moins un index GIN de recherche full-text. Contre PostgreSQL réel, les requêtes
qui en dépendent échouent (`IntegrityError`, résultats de recherche vides). Confirmé identique
sur arm64, donc probablement aussi sur les runners CI amd64.
**Impact** : le job `backend-tests-postgres` est rouge sur toute PR/push depuis au moins la
phase 1, sans qu'aucune régression réelle n'en soit la cause. Un job CI rouge en permanence sur
la branche protégée `main` cesse d'être un signal — soit il n'est en pratique plus regardé
(une vraie régression PostgreSQL passerait inaperçue), soit il bloque toute fusion si le job
est requis dans la protection de branche. Dans les deux cas, la gate perd sa valeur.
**Gravité** : **S1** — CI cassée durablement dégrade la confiance dans tous les autres verts.
**Effort** : **M** — deux pistes possibles, non appliquées : (a) construire le schéma de test
via `flask db upgrade` (migrations réelles) au lieu de `db.create_all()` pour ce job seulement,
ou (b) déplacer la définition de l'index GIN dans un event SQLAlchemy (`__table_args__`) pour
qu'il soit posé aussi par les métadonnées ORM. (a) est plus fidèle à la prod, (b) est plus
rapide à écrire.

### TEST-02 — Aucune gate de couverture frontend en CI
**Emplacement** : `web/vitest.config.ts:12-18` (commentaire explicite : « Pas de seuil pour
l'instant ... phase 4 ») ; `.github/workflows/ci.yml:168-187` (job `frontend-tests` lance
`npm run test:run`, jamais `npm run test:coverage`) ; `web/package.json` (script
`test:coverage` existe mais n'est appelé nulle part en CI).
**Description** : contrairement au backend (`--cov-fail-under=80`), rien n'empêche une PR de
faire baisser la couverture frontend — la mesure elle-même n'est même pas produite en CI.
**Impact** : régression de couverture silencieuse côté frontend, notamment sur les 35 vues
(aucune n'a de test, voir TEST-04) et les 6 stores non testés (TEST-03).
**Gravité** : **S3** — lacune déjà documentée et sciemment différée (`docs/testing.md`,
commentaire `vitest.config.ts:16-17`), pas un oubli caché ; reste un vrai trou avant la phase 4.
**Effort** : **S** — ajouter `test:coverage` au job CI avec un seuil bas et progressif plutôt
que d'attendre la phase 4 pour l'introduire d'un coup.

### TEST-03 — 6 stores Pinia sur 12 sans aucun test
**Emplacement** : `web/src/stores/{auth,focus,groups,planning,pomodoro,tags}.ts` — aucun
fichier correspondant dans `web/tests/stores/` (seuls `binders`, `decks`, `notes`,
`notifications`, `pdf`, `revision` ont un spec).
**Description** : `auth.ts` (117 lignes) gère le cycle de vie du token JWT côté client
(stockage, expiration présumée, état de connexion) sans aucun test unitaire — c'est le store
dont une régression a l'impact utilisateur le plus large (déconnexions intempestives, session
qui ne se rafraîchit pas). `planning`/`pomodoro`/`focus` touchent aux mécaniques de streak et
de temps d'étude, cœur du produit.
**Impact** : une régression sur la persistance ou l'expiration du token, ou sur le calcul de
session de focus, ne serait détectée qu'en usage réel ou en E2E (si le parcours y est couvert
— ce qui n'est pas le cas pour `auth`, voir TEST-05).
**Gravité** : **S2**.
**Effort** : **S** par store (gabarit déjà disponible :
`web/tests/stores/notifications.spec.ts`, skill `cycle-tdd`).

### TEST-04 — Zéro test frontend (unitaire ou E2E) sur le partage public et la marketplace
**Emplacement** : `web/tests-e2e/*.spec.ts` (5 fichiers : `diagrams-editor`, `guards`,
`note-navigation`, `render-check`, `reviews-ai-flashcards`) — aucun ne mentionne
`marketplace`, `/share/` ou « partage » ; `web/src/views` (35 vues, 0 test) — aucune vue de
partage public ou de marketplace testée, ni unitairement ni en intégration.
**Description** : ce sont deux des quatre chemins critiques explicitement désignés par le
prompt de démarrage §5 (« tests manquants sur les chemins critiques ... clonage marketplace »,
partage public). Le **backend** couvre bien ce périmètre
(`test_public_class_follow.py`, `test_shared_class_decks_diagrams.py`,
`test_shared_class_notes.py`, `test_shared_revision_sets.py`, `test_community.py`) — le trou
est spécifiquement côté frontend.
**Impact** : une régression de rendu, de routage ou d'appel API sur l'écran de partage public
ou de clonage marketplace ne serait détectée par aucun test automatisé, seulement en usage
réel — ce sont pourtant des écrans exposés à des utilisateurs non authentifiés (partage
public), donc plus visibles en cas de casse.
**Gravité** : **S2**.
**Effort** : **M** — au minimum un scénario E2E par chemin (accès à un lien de partage public,
clonage d'un classeur marketplace), gabarits Playwright existants à suivre
(`web/tests-e2e/helpers.ts`).

### TEST-05 — Le parcours de connexion réussie n'est pas testé E2E
**Emplacement** : `web/tests-e2e/guards.spec.ts:5-13` — les deux seuls tests vérifient (a) la
redirection d'un visiteur non authentifié vers `/login`, (b) la présence du champ mot de passe
sur `/login`. Aucun test ne soumet le formulaire avec des identifiants valides et ne vérifie
l'arrivée sur `/dashboard`.
**Description** : le nom du fichier (« garde d'authentification ») annonce un périmètre plus
large que ce qu'il couvre réellement — la garde de redirection est testée, la connexion
elle-même ne l'est pas.
**Impact** : mineur si le store `auth` est par ailleurs testé unitairement (voir TEST-03,
actuellement non plus) ; combiné à TEST-03, la connexion réussie n'a aujourd'hui aucune
couverture automatisée.
**Gravité** : **S3**.
**Effort** : **XS** — un test de plus dans le même fichier.

### TEST-06 — Outillage de test déclaré mais inexploité (`factory-boy`, `freezegun`)
**Emplacement** : `backend/requirements-dev.txt:9` (`factory-boy==3.3.1`) et `:11`
(`freezegun==1.5.1`) ; zéro occurrence de `factory` ou de `freeze_time`/`freezegun` dans
`backend/tests/*.py` (recherche exhaustive). Construction de données de test faite à la main,
fixture par fixture (ex. `test_user`, `backend/tests/conftest.py:33-48`).
**Description** : deux dépendances de test dédiées sont installées sans être utilisées. Pour
`freezegun` en particulier, plusieurs tests sensibles à la date/l'heure dépendent de l'horloge
réelle : `datetime.utcnow()` en `tests/test_spaced_repetition.py:39`,
`tests/test_stats_dashboard.py:35` (calcul du « jour du jour » pour un test de streak/heatmap),
`tests/test_planning_advance.py:20,31,58`.
**Impact** : risque de flakiness théorique près d'un changement de jour (minuit UTC) sur les
tests de streak/planification ; absence de scénario testant explicitement un jour donné fixe
(ex. bascule de fuseau, changement d'heure) alors que `invariants-sm2` définit précisément
cette notion. Probabilité faible en pratique (fenêtre d'une poignée de secondes autour de
minuit), mais évitable à coût nul vu la dépendance déjà installée.
**Gravité** : **S4**.
**Effort** : **S** — introduire `@freeze_time` sur les tests listés ; adopter `factory-boy`
au moins pour `test_user` réduirait la duplication observée entre fixtures similaires dans
plusieurs fichiers de test (non quantifié précisément ici, à confirmer par l'architecte
backend si jugé pertinent pour `02-ARCHITECTURE.md`).

### TEST-07 — Pas de mode watch/relance rapide côté backend
**Emplacement** : `backend/requirements-dev.txt` — ni `pytest-watch`, ni `pytest-xdist`
(`--looponfail`), ni équivalent.
**Description** : contrairement au frontend (`vitest` en mode watch par défaut via
`npm run test`), relancer les tests backend après chaque modification nécessite de retaper la
commande. Le run ciblé restant à 2,9 s (TEST — section 1), l'impact réel est faible.
**Impact** : friction mineure sur la boucle TDD backend, pas un blocage.
**Gravité** : **S4**.
**Effort** : **XS** — ajouter `pytest-watch` (ou documenter `pytest --lf -x` en boucle courte)
à `requirements-dev.txt`.

## Résumé

7 constats : 1×S1 (TEST-01), 2×S2 (TEST-03, TEST-04), 2×S3 (TEST-02, TEST-05), 2×S4 (TEST-06,
TEST-07). Aucun constat S1 ou S2 ne remet en cause l'aptitude au TDD elle-même (boucle rapide,
isolation réelle confirmée) — TEST-01 remet en cause la fiabilité du signal CI PostgreSQL,
TEST-03/04 sont des trous de couverture sur des chemins nommés explicitement par le prompt de
démarrage. Durées mesurées : backend 56,4 s / 2,9 s (complet/ciblé), frontend 2,9 s / 2,6 s
(complet/ciblé, re-mesuré en direct).
