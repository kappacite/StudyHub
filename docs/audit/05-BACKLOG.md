# Backlog consolidé — Revue technique phase 2

> Consolide `01-SECURITE.md`, `02-ARCHITECTURE.md`, `03-PERFORMANCE.md`, `04-TESTS-CI.md`.
> Aucune correction appliquée dans cette phase. Tri : gravité (S1→S4) puis effort croissant
> (XS→L). Généré le 2026-08-23.

## Table

| ID | Gravité | Effort | Constat | Source |
|---|---|---|---|---|
| SEC-01 | S1* | XS | Clés secrètes avec valeur de repli devinable (`config.py`) | [01](01-SECURITE.md#sec-01) |
| SEC-02 | S1 | S | Contenu privé exposé sous un classeur public (marketplace) | [01](01-SECURITE.md#sec-02) |
| PERF-05 | S1 | M | Rendu Markdown+LaTeX de `NoteEdit.vue` relancé en entier à chaque frappe | [03](03-PERFORMANCE.md#perf-05) |
| TEST-01 | S1 | M | Job CI `backend-tests-postgres` rouge en permanence (12 échecs) | [04](04-TESTS-CI.md#test-01) |
| SEC-03 | S2 | S | Refresh token jamais révoqué à la déconnexion | [01](01-SECURITE.md#sec-03) |
| ARCH-03 | S2 | S | Logique métier (traversée récursive) codée dans la route `packages.py` | [02](02-ARCHITECTURE.md#arch-03) |
| ARCH-04 | S2 | S | Risque N+1 dans la traversée récursive de `packages.py` | [02](02-ARCHITECTURE.md#arch-04) |
| PERF-04 | S2 | S | File de cartes à réviser non bornée (pas de `LIMIT`) | [03](03-PERFORMANCE.md#perf-04) |
| TEST-03 | S2 | S/store | 6 stores Pinia sans test, dont `auth` | [04](04-TESTS-CI.md#test-03) |
| SEC-05 | S2 | M | CSP `unsafe-inline`/`unsafe-eval` | [01](01-SECURITE.md#sec-05) |
| SEC-07 | S2 | M | Auto-migration sans garde-fou destructif | [01](01-SECURITE.md#sec-07) |
| ARCH-02 | S2 | M | Routes publiques résolvent la ressource par requête ORM directe (sans DAO/service) | [02](02-ARCHITECTURE.md#arch-02) |
| PERF-03 | S2 | M | Notation d'une carte SM-2 : deux commits + cascade synchrone non bornée | [03](03-PERFORMANCE.md#perf-03) |
| PERF-06 | S2 | M | Appels Gemini synchrones bloquants pour flashcards/quiz (incohérent avec Celery ailleurs) | [03](03-PERFORMANCE.md#perf-06) |
| TEST-04 | S2 | M | Zéro test frontend (unitaire ou E2E) sur partage public et marketplace | [04](04-TESTS-CI.md#test-04) |
| ARCH-01 | S2 | L | `db.session`/`.query()` directs hors DAO, systémique (13 fichiers de service) | [02](02-ARCHITECTURE.md#arch-01) |
| SEC-04 | S3 | XS | Fuite d'identifiants internes (`user_id`, `binder_id`) sur note publique | [01](01-SECURITE.md#sec-04) |
| SEC-08 | S3 | XS | Délimiteurs pseudo-XML non échappés dans les prompts Gemini | [01](01-SECURITE.md#sec-08) |
| TEST-05 | S3 | XS | Le parcours de connexion réussie n'est pas testé E2E | [04](04-TESTS-CI.md#test-05) |
| SEC-09 | S3 | S | Pas de limite de débit dédiée sur `/auth/login` | [01](01-SECURITE.md#sec-09) |
| ARCH-10 | S3 | S | Réponse HTTP partiellement non modélisée en Pydantic (`packages.py`) | [02](02-ARCHITECTURE.md#arch-10) |
| ARCH-11 | S3† | S | Vérification d'appartenance dupliquée (34 occurrences) — cohérence à confirmer | [02](02-ARCHITECTURE.md#arch-11) |
| PERF-01 | S3 | S | Streak calculé en Python sur l'historique complet au lieu d'un agrégat SQL | [03](03-PERFORMANCE.md#perf-01) |
| PERF-02 | S3 | S | Stats de deck calculées en itérant toutes les cartes en Python | [03](03-PERFORMANCE.md#perf-02) |
| TEST-02 | S3 | S | Aucune gate de couverture frontend en CI | [04](04-TESTS-CI.md#test-02) |
| SEC-06 | S3 | L | JWT (access + refresh) stockés en `localStorage` | [01](01-SECURITE.md#sec-06) |
| ARCH-05 | S3 | L | Le service commit directement au lieu de déléguer au DAO (12 fichiers) | [02](02-ARCHITECTURE.md#arch-05) |
| ARCH-06 | S3 | L | Services fourre-tout (`class_service.py` 930 l., `ai_service.py` 820 l.) | [02](02-ARCHITECTURE.md#arch-06) |
| ARCH-07 | S3 | L/écran | Composants Vue > 300 lignes (11 vues, `NoteEdit.vue` 3024 l.) | [02](02-ARCHITECTURE.md#arch-07) |
| PERF-07 | S3 | L | Chunk KaTeX 1,21 Mo/393 Ko gzip chargé même sur le partage public anonyme | [03](03-PERFORMANCE.md#perf-07) |
| ARCH-09 | S4 | XS | Détection de plateforme ad hoc au lieu de `usePlatform()` (2 fichiers) | [02](02-ARCHITECTURE.md#arch-09) |
| ARCH-12 | S4 | XS | Calcul de pagination dupliqué dans 8 routes | [02](02-ARCHITECTURE.md#arch-12) |
| TEST-07 | S4 | XS | Pas de mode watch/relance rapide côté backend | [04](04-TESTS-CI.md#test-07) |
| ARCH-08 | S4 | S | Store Pinia à la limite du seuil de taille (`revision.ts` 323 l.) | [02](02-ARCHITECTURE.md#arch-08) |
| TEST-06 | S4 | S | Outillage de test déclaré mais inexploité (`factory-boy`, `freezegun`) | [04](04-TESTS-CI.md#test-06) |

\* SEC-01 : gravité conditionnelle à la config de déploiement réelle, non vérifiable depuis le
code seul (voir 01-SECURITE.md).
† ARCH-11 : gravité provisoire, S4 si le comportement actuel s'avère intentionnel (voir
02-ARCHITECTURE.md).

**35 constats** : 4×S1 · 11×S2 · 15×S3 · 5×S4. Répartition par axe : sécurité 9, architecture
12, performance 7, tests/CI 7.

## À traiter avant la refonte UI

Non corrigés, ces points rendraient la phase 3/4 plus instable ou plus coûteuse à corriger
après coup — pas une liste à traiter en phase 2, une note de séquencement pour la suite :

1. **TEST-01** (S1) — la CI PostgreSQL est cassée depuis au moins la phase 1. Empiler des
   dizaines de commits `feat(design)`/`feat(ui)` par-dessus un job rouge permanent fait perdre
   toute valeur de signal à ce job avant même de commencer. À réparer en premier, indépendamment
   du reste — c'est un correctif isolé (index GIN), pas une refonte.
2. **PERF-05** (S1) — le rendu KaTeX bloquant de `NoteEdit.vue` touche exactement l'écran le
   plus volumineux à migrer (phase 4 §7, item 4 « Éditeur de notes »). Le corriger avant ou en
   ouverture de ce cycle évite de spécifier, en TDD, un comportement de rendu déjà connu comme
   défaillant — et le découplage `computed()`/mémoïsation qu'il impose facilite plutôt le
   découpage de `NoteEdit.vue` (**ARCH-07**, 3024 lignes) que la phase 4 devra de toute façon
   faire.
3. **SEC-02 / ARCH-02 / ARCH-03 / ARCH-04** (groupe lié) — même code (`packages.py`,
   `community_service.py`), même endpoints. SEC-02 est une fuite de données actives : redessiner
   visuellement l'écran marketplace/partage public (phase 4 §7, item 8) sans corriger l'exposition
   sous-jacente reviendrait à habiller une fuite active plutôt qu'à la fermer. La correction
   d'architecture proposée pour ARCH-02 (DAO dédié + service `SharingService`) résout les quatre
   constats en un seul geste : filtre `is_public` correct par enfant (SEC-02), requête déplacée
   hors route (ARCH-03), eager loading (ARCH-04).
4. **TEST-03 (store `auth`) / TEST-04 (partage public, marketplace)** (S2) — la procédure
   `migration-ecran` part d'un inventaire de l'existant pour écrire les tests de non-régression
   avant réécriture. Sans aucun test de départ sur l'authentification (premier écran migré,
   phase 4 §7 item 1) ni sur le partage public/marketplace (item 8), cet inventaire n'a rien à
   quoi se comparer — un filet minimal avant migration réduit le risque de perdre un
   comportement en route.
5. **SEC-01** (S1 conditionnel, XS) — coût de correction nul (`os.environ[...]` sans défaut) ;
   à vérifier/fermer avant que le volume de commits augmente en phase 3/4, plutôt que de laisser
   une hypothèse de configuration non confirmée traîner plus longtemps.

Le reste (ARCH-05/06/07 hors le point 2 ci-dessus, PERF-01/02/07, SEC-03/04/05/06/07/08/09,
TEST-02/05/06/07) est documenté mais ne bloque ni ne rend plus coûteuse la refonte UI en soi —
traitable au fil de l'eau ou en tâche de fond indépendante, au rythme choisi hors de ce
séquencement.
