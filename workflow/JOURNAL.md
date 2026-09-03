# Journal global — workflow

Chantier actif : aucun

## Chantiers ouverts

- `ecrans-peripheriques-visuels` — pas commencé, indépendant (voir ses notes du 2026-08-30 :
  `PDFs.vue`/`Diagrams.vue` divergent de leurs maquettes ; dépendance Blurting→Feynman déjà
  levée ; écart Blurting probablement structurel, pas juste une retonation ; tâches détaillées
  le même jour)
- `classes-examens-planning` — pas commencé, indépendant

## Historique

- 2026-09-03 — [revision-qcm-heterogene] **PR #142 ouverte**
  (`feature/revision-qcm-heterogene` → `main`,
  https://github.com/kappacite/StudyHub/pull/142). Chantier `pr-ouverte`. 3 tâches complètes
  (backend `GRADABLE_TYPES`/`check_answer`, frontend bloc de template QCM dans
  `RevisionStudy.vue`, vérification visuelle réelle). Backend ciblé 54/54, frontend complet
  538/538, build clean. Suite backend complète tentée séparément : 2 échecs préexistants sans
  rapport, environnement Windows (`test_pdfs.py` crash natif `python-magic`, `test_import.py`
  `PermissionError` de verrou de fichier) — non bloquants pour ce chantier. Prochaine action :
  attendre la revue/CI, puis merger.

- 2026-09-03 — [revision-qcm-heterogene] Chantier ouvert. Root cause identifié en
  investigation avant tout code (garde `rset.type` au lieu de `item.type`, exclusion
  systématique des QCM dans `RevisionStudy.vue`) ; approche A retenue en brainstorming
  (étendre le flux générique GRADABLE_TYPES plutôt que les endpoints QCM dédiés). 3 tâches.
  Prochain : Task 1 (backend).

- 2026-09-03 — [bibliotheque-notes-listes] **PR #140 mergée dans `main`** (squash, `4d361a4`),
  CI verte (6/6 checks). Chantier `clos`. Prochaine action : ouvrir le chantier révision QCM
  (root cause déjà identifié en investigation : garde backend sur `rset.type` au lieu de
  `item.type` dans `check_qcm_answer`/`answer_qcm_item`, et `RevisionStudy.vue` qui exclut
  systématiquement les QCM d'un ensemble hétérogène — limitation différée deux fois
  [`backend-ensembles-heterogenes`, `reviser-hub`], jamais traitée).

- 2026-09-03 — [bibliotheque-notes-listes] Task 8 (barre de filtre par tags -- conditionnée
  à la racine, corrige un bug latent où elle s'affichait sans effet dans un classeur)
  terminée. 537/537 tests, `vue-tsc` propre. Prochain, dernière tâche : Task 9 (vérification
  visuelle complète + non-régression finale).

- 2026-09-03 — [bibliotheque-notes-listes] Task 7 (largeur : colonne étroite dans un
  classeur, grille racine inchangée) terminée. 535/535 tests, `vue-tsc` propre, vérifié
  visuellement. Prochain : Task 8 (barre de filtre par tags).

- 2026-09-03 — [bibliotheque-notes-listes] Task 6 (lignes d'ensemble -- bouton Réviser, menu
  par ligne, phrase d'explication) terminée. 533/533 tests, `vue-tsc` propre, vérifié
  visuellement. Prochain : Task 7 (largeur 920px dans un classeur).

- 2026-09-03 — [bibliotheque-notes-listes] Task 5 (lignes de notes -- extrait, tag, date,
  globe, séparateurs pointillés) terminée. 530/530 tests, `vue-tsc` propre, vérifié
  visuellement. Prochain : Task 6 (lignes d'ensemble de révision).

- 2026-09-03 — [bibliotheque-notes-listes] Tasks 3+4 (sous-titre agrégé racine, liseré/rayon
  + accent de `BinderCard`) terminées. 525/525 tests, `vue-tsc` propre. Prochain : Task 5
  (lignes de notes).

- 2026-09-03 — [bibliotheque-notes-listes] Task 2 (en-tête de `Binders.vue` : titre dynamique,
  sur-titre mono, menu « … ») terminée. 519/519 tests, `vue-tsc` propre, vérifié visuellement.
  Prochain : Task 3 (sous-titre agrégé sur la grille racine).

- 2026-09-02 — [bibliotheque-notes-listes] Task 1 (variante « segmented » de `Tabs.vue`)
  terminée. 514/514 tests, `vue-tsc` propre. Prochain : Task 2 (en-tête de `Binders.vue`).

- 2026-09-02 — [bibliotheque-notes-listes] chantier ouvert. Vue liste de la Bibliothèque
  (dans un classeur) recomparée à `Notes.dc.html` par lecture des sources ET comparaison
  visuelle réelle via Claude in Chrome. `bibliotheque-redesign` (#132) avait traité
  l'architecture de l'écran, pas la densité des lignes ni la silhouette de l'en-tête.
  9 tâches. Prochain : Task 1 (variante bascule de `Tabs.vue`).

- 2026-09-02 — [editeur-notes-notation-ia] **PR #138 mergée dans `main`** (squash, `770cffe`),
  CI verte (6/6 checks, après correctif d'un test E2E cassé par la refonte sidebar — voir le
  journal du chantier). Chantier `clos`. Volet backend « Notation de la note » (flux 2) reste
  hors périmètre, à planifier séparément. Ancienne branche `feature/noteedit-migration`
  (référence de conception, non fusionnée) toujours locale uniquement — pas encore poussée sur
  `origin`, à faire si une reprise depuis une autre machine en a besoin. Prochaine
  action : choisir le prochain chantier à ouvrir (`ecrans-peripheriques-visuels`,
  `classes-examens-planning`, ou planifier le volet backend Notation).

- 2026-08-30 — [editeur-notes-notation-ia] **Chantier ouvert, ancienne branche réconciliée.**
  Demande utilisateur : "commence le chantier sur la refonte de l'éditeur, assure-toi de
  respecter le canvas." Investigation a révélé que `feature/noteedit-migration` (15 commits)
  est en conflit majeur irrésolvable avec `reviser-hub` (2477/3499 lignes de `NoteEdit.vue`
  réécrites indépendamment). Ruling : nouvelle branche depuis `main` à jour, ancienne branche
  traitée comme référence de conception (son stash jamais appliqué avait déjà correctement
  identifié, via le canevas, que la modale IA doit devenir une sidebar à 3 méthodes — confirmé
  en extrayant `NoteEdit.dc.html` moi-même). Nouveau plan (10 tâches TDD) :
  `docs/superpowers/plans/2026-08-30-editeur-notes-redesign.md`. Volet backend (Notation)
  laissé hors périmètre, nécessite son propre brainstorming. Exécution démarrée en
  `subagent-driven-development`.

## Historique

- 2026-08-30 — [notation-sm2-4-paliers] **PR #136 mergée dans `main`** (squash, `79dc362`),
  CI verte (6/6 checks). Chantier `clos`. Prochaine action : choisir le prochain chantier à
  ouvrir (`editeur-notes-notation-ia`, `ecrans-peripheriques-visuels` ou
  `classes-examens-planning`).

- 2026-08-30 — [notation-sm2-4-paliers] **Chantier ouvert et exécuté.** Demande utilisateur
  suite aux captures du chantier `revision-flexibilite` : boutons de notation manuelle passés
  de 3 (À revoir/Moyen/Acquis, 1/3/5) à 4 paliers alignés sur le graphique de stats existant
  (Encore/Difficile/Bien/Facile, 1/2/4/5 — choix du score « Bien » tranché en chat,
  `AskUserQuestion`). TDD, 436/436 tests frontend, `vue-tsc -b` propre. Prochaine action :
  revue et clôture.

## Historique

- 2026-08-30 — [revision-flexibilite] **PR #134 mergée dans `main`** (squash, `067eef0`), CI
  verte (6/6 checks). Chantier `clos`. Prochaine action : choisir le prochain chantier à ouvrir
  (`editeur-notes-notation-ia`, `ecrans-peripheriques-visuels` ou `classes-examens-planning`).

- 2026-08-30 — [revision-flexibilite] **Chantier clos (code).** Revue finale de branche
  (opus) : « avec corrections » — 3 Important (garde anti double-soumission manquante dans la
  réécriture QCM/notation manuelle, asymétrie de garde QCM sur `item.type` vs `rset.type`
  permettant une correction fabriquée, sélecteurs d'association modifiables pendant la
  correction) + 2 Minor retenus. Tour de correction : l'agent a échoué en fin de tâche (limite
  de session API) après avoir déjà tout écrit — vérifié directement par le contrôleur (chaque
  diff relu, 2 suites complètes ré-exécutées indépendamment : 435/435 frontend, 336/341
  backend), tout confirmé correct. Commit `d474ce8`. Détail complet :
  `workflow/revision-flexibilite/JOURNAL.md`. Prochaine action : demander à l'utilisateur de
  pousser `feature/revision-flexibilite`, puis ouvrir la PR.
- 2026-08-30 — [revision-flexibilite] **8 tâches exécutées, vérification visuelle faite,
  chantier prêt à clôturer.** Backend : scission check/commit pour la notation manuelle
  vf/association/ordre (Task 1) et QCM par question (Task 2, suppression du passage groupé
  devenu mort), `include_not_due` pour réviser hors échéancier (Task 3, 2 tours de correction —
  tous deux sur un test de non-régression, jamais sur le code de production), agrégat
  `next_review_at` dans les stats (Task 4). Frontend : notation manuelle vf/association/ordre
  (Task 5), réécriture complète de `QcmRun.vue` en navigation question par question + révision
  libre (Task 6, tâche la plus grosse du chantier), bouton « Réviser quand même » sur
  `RevisionStudy.vue` + date optimale dans les stats (Task 7). Vérification visuelle réelle
  (Task 8) : les 4 demandes confirmées fonctionnelles en direct (captures d'écran, desktop +
  mobile 375px + mode sombre), 424/424 tests frontend + 335/340 backend (5 échecs pré-existants
  sans rapport). Détail complet : `workflow/revision-flexibilite/JOURNAL.md`. Prochaine action :
  revue finale de branche, puis demander à l'utilisateur de pousser
  `feature/revision-flexibilite` et ouvrir la PR.
- 2026-08-30 — [revision-flexibilite] **Chantier ouvert.** 4 demandes utilisateur sur le
  système SM-2 : notation manuelle généralisée (vf/association/ordre/qcm, actuellement déduite
  automatiquement), QCM révisable librement (3 axes confirmés en chat : filtre d'échéance,
  navigation question par question, rejeu d'une question déjà répondue), révision possible hors
  échéancier (« rien à réviser aujourd'hui »), prochaine date de révision optimale dans les
  stats d'ensemble. Investigation complète en fork avant plan. 2 clarifications tranchées en
  chat (`AskUserQuestion`) : périmètre exact du blocage QCM (les 3 axes retenus), impact SM-2
  normal pour la révision libre (pas de mode entraînement séparé). Plan détaillé (8 tâches TDD) :
  `docs/superpowers/plans/2026-08-30-revision-flexibilite.md`. Périmètre : `RevisionSet`/
  `RevisionItem` uniquement, decks de flashcards hors scope (non mentionnés, déjà dotés d'une
  notation manuelle). Exécution démarrée en `subagent-driven-development`.

- 2026-08-30 — [bibliotheque-redesign] **PR #132 mergée dans `main`** (squash, `c222b23`), CI
  verte (6/6 checks). Chantier `clos`. Prochaine action : choisir le prochain chantier à ouvrir
  (`editeur-notes-notation-ia`, `ecrans-peripheriques-visuels` ou `classes-examens-planning`).
- 2026-08-30 — [bibliotheque-redesign] **PR #132 ouverte** (`feature/bibliotheque-redesign` →
  `main`, https://github.com/kappacite/StudyHub/pull/132). Chantier `pr-ouverte`. Prochaine
  action : attendre la CI, puis merger.

- 2026-08-30 — [bibliotheque-redesign] **Chantier clos (code).** Revue finale de branche
  (opus) : « avec corrections » — 3 Important (tags de classeur disparus de partout, invariant
  de masquage sur « Non classé » sous-testé à 1/8, section « Sous-classeurs » vide affichée en
  permanence) + 4 Minor bon marché retenus. Tour de correction 1/5 : 6/7 corrigés proprement ;
  la re-revue ciblée a trouvé une régression réelle introduite par la correction du 3e constat
  (titre « Sous-classeurs » apparaissant en permanence à la racine), corrigée directement par
  le contrôleur (une ligne, RED→GREEN vérifié), commit `1257b8a`. Détail complet :
  `workflow/bibliotheque-redesign/JOURNAL.md`. Prochaine action : demander à l'utilisateur de
  pousser `feature/bibliotheque-redesign`, puis ouvrir la PR.
- 2026-08-30 — [bibliotheque-redesign] **4 tâches exécutées, vérification visuelle faite,
  chantier prêt à clôturer.** `subagent-driven-development` : Task 1 (`BinderCard.vue` +
  agrégats, commit `df54090`), Task 2 (grille récursive remplaçant `SplitView`, commit
  `850665e` — bug réel trouvé et volontairement différé : « Retirer du classeur » restait actif
  sur « Non classé »), Task 3 (bug de Task 2 corrigé + non-régression sur 11 fonctionnalités
  liées aux classeurs, commit `b21d1d3`), Task 4 (vérification visuelle native contre les
  vraies maquettes, conforme ; nouveau défaut trouvé et corrigé — `PageHeader.vue`, composant
  partagé, ne passait pas ses actions à la ligne à 375px, commit `0ddfaf1`). Détail complet :
  `workflow/bibliotheque-redesign/JOURNAL.md`. Prochaine action : revue finale de branche, puis
  demander à l'utilisateur de pousser `feature/bibliotheque-redesign` et ouvrir la PR.
- 2026-08-30 — [bibliotheque-redesign] **Chantier ouvert**, décisions produit tranchées en chat
  (arbre de sous-dossiers → grille récursive ; contenu non rangé → classeur virtuel « Non
  classé » ; onglet « Autres » conservé). Tâches détaillées aussi pour
  `ecrans-peripheriques-visuels` et `editeur-notes-notation-ia` (toujours pas exécutées).
  Branche `feature/bibliotheque-redesign` créée depuis `main` à jour. Plan détaillé (4 tâches
  TDD) : `docs/superpowers/plans/2026-08-30-bibliotheque-redesign.md`. Exécution démarrée en
  `subagent-driven-development`.

- 2026-08-30 — [bibliotheque-redesign] **Deuxième passe** (demande explicite de l'utilisateur :
  "intègre bien tous les écrans de la partie bibliothèque - notes sur le canvas") : extension
  de l'investigation aux 5 écrans atteints depuis une note. `NoteEdit.vue` déjà pris en charge
  correctement par `editeur-notes-notation-ia` (maquette citée dès la 1ère ligne de son plan) ;
  `NoteFeynman.vue` déjà vérifié correct (`reviser-hub`) ; `Blurting.vue` montre un écart réel
  (concepts+flashcards+rétention absents de la maquette) sous-estimé par le "retonation
  seulement" de `ecrans-peripheriques-visuels` (note ajoutée là-bas) ; `NoteQuiz.vue`
  globalement aligné, orphelin, risque faible ; **découverte principale** — `NoteEvaluation.dc.html`
  correspond en réalité à la future fonctionnalité « Notation » de `editeur-notes-notation-ia`
  (note de la fiche sur 100), pas à l'écran `NoteEvaluation.vue` existant (qui implémente
  l'Évaluation mixte, une fonctionnalité différente) — collision de nom, note ajoutée au
  `CONTEXT.md` de ce chantier pour ne pas la perdre avant qu'il soit ouvert. Spec mise à jour :
  `docs/superpowers/specs/2026-08-30-bibliotheque-redesign-design.md` (§ « Écrans d'une note »).
  Toujours aucune implémentation lancée.

- 2026-08-30 — [bibliotheque-redesign] Chantier créé en `Statut : planifie` (investigation
  demandée en chat, sur le modèle de la correction `reviser-hub`) : `Binders.vue` n'a jamais
  été comparé aux vraies maquettes Direction A (confirmé depuis son commit fondateur,
  `77ff833`, 2026-06-21). `RevisionSetDetail.vue`/`RevisionSetModal.vue` déjà vérifiés
  (`bibliotheque-ensembles`), hors scope. `PDFs.vue`/`Diagrams.vue` montrent le même écart
  mais restent le territoire de `ecrans-peripheriques-visuels` (déjà planifié, note ajoutée
  là-bas) — pas dupliqués ici. Spec :
  `docs/superpowers/specs/2026-08-30-bibliotheque-redesign-design.md`. Plan brouillon (pas
  prêt à exécuter, requiert `superpowers:brainstorming` sur l'arbre de sous-dossiers et le
  contenu non rangé à la racine) : `docs/superpowers/plans/2026-08-30-bibliotheque-redesign.md`.
  Aucune implémentation lancée, sur demande explicite de l'utilisateur. Prochaine action :
  brainstorming avec l'utilisateur pour ouvrir ce chantier, ou choisir un autre chantier.

- 2026-08-30 — [reviser-hub] **PR #130 mergée dans `main`** (squash, `358e5b0`), CI verte (6/6
  checks — le job E2E Playwright avait cassé sur le 1ᵉʳ run sur un test jamais migré après le
  déplacement de la génération IA vers `Decks.vue` par ce même chantier, corrigé le jour même).
  Chantier `clos`. Prochaine action : choisir le prochain chantier à ouvrir
  (`editeur-notes-notation-ia`, `ecrans-peripheriques-visuels` ou `classes-examens-planning`).
- 2026-08-30 — [reviser-hub] **PR #130 ouverte** (`feature/reviser-hub` → `main`,
  https://github.com/kappacite/StudyHub/pull/130). Chantier `pr-ouverte`. Prochaine action :
  attendre la revue humaine / CI, puis merger.
- 2026-08-30 — [reviser-hub] **Revue finale de branche + tour de correction, chantier prêt pour
  la PR.** 1 Critical trouvé (un type élargi — `FocusItem.type` + `'revision_set'` — câblé dans un
  seul consommateur sur 6, cassant le bouton « Réviser » sur `Accueil.vue`/`FocusPage.vue`/
  `FocusWidget.vue` et la file unifiée sur `StudyDeck.vue`/`Blurting.vue` ; aucune revue de tâche
  ne pouvait le voir, hors de toute liste de fichiers déclarée) + 4 Important (scoping `user_id`
  manquant sur les nouvelles stats de durée ; classeurs/decks avec des périmètres
  descendants incohérents ; état d'erreur perdu sur 2 écrans refondus ; appel API direct + `any`
  dans un nouveau composant). 1 seul tour de correction (4 commits), re-revue ciblée propre.
  Détail complet : `workflow/reviser-hub/JOURNAL.md`. Prochaine action : demander à l'utilisateur
  de pousser `feature/reviser-hub`, puis ouvrir la PR.
- 2026-08-29 — [reviser-hub] **Task 9 ajoutée post-clôture** (demande utilisateur en chat) : durée
  de révision réelle dans les statistiques (« Temps cumulé », colonne « Durée », « Temps total
  d'étude » classeur), jusque-là omise faute de suivi réel. Chronométrage réel côté frontend
  (`RevisionStudy.vue`/`QcmRun.vue`), répartition `divmod` pour le passage QCM groupé, aucune
  fabrication (omission = toujours `0`). 1 tour, revue immédiatement propre. 1 écart pré-existant
  signalé hors scope : `StudySessionDAO` ne filtre pas par `user_id` (mélange de sessions
  multi-élèves déjà possible sur un ensemble partagé, pas une régression de cette tâche). Vérifié
  visuellement en direct (durée réelle postée via l'API, rendue correctement sur les 2 écrans).
  Détail complet : `workflow/reviser-hub/JOURNAL.md`. Prochaine action : revue finale de branche,
  puis demander à l'utilisateur de pousser `feature/reviser-hub` et ouvrir la PR.
- 2026-08-29 — [reviser-hub] **Correction et reclôture** : la clôture précédente (ci-dessous)
  n'avait jamais consulté les vraies maquettes Direction A — répétition de l'erreur documentée
  dans la mémoire `migration-ecran-verify-mockup`. Correction complète via
  `docs/superpowers/plans/2026-08-29-reviser-hub-redesign.md` (8 tâches TDD,
  subagent-driven-development, 3 tours de correction tous conclus propres) : `Reviews.vue`
  reconstruit en flux unifié « ce qui est dû » (2503→381 lignes), `RevisionSetStats.vue` et
  `RevisionBinderStats.vue` reconstruits selon leurs maquettes respectives, Feynman et la
  génération de flashcards IA relogés (`NoteFeynman.vue`, `Decks.vue`). Un vrai bug pré-existant
  corrigé en passant (routage manquant pour un ensemble de révision dû dans la file unifiée).
  Vérification visuelle réelle refaite dès cette clôture, cette fois côte à côte avec les vraies
  maquettes, clair/sombre × desktop/mobile — aucun nouveau défaut. Détail complet :
  `workflow/reviser-hub/JOURNAL.md`. Prochaine action : demander à l'utilisateur de pousser
  `feature/reviser-hub`, puis ouvrir la PR.
- 2026-08-29 — [reviser-hub] Chantier `code clos` : 11 tâches TDD (subagent-driven-development),
  toutes approuvées sans tour de correction. Correctif backend réel trouvé et corrigé (stats
  silencieusement vides pour tout ensemble hétérogène révisé — filtrage par type d'ensemble au
  lieu de type d'item sur le discriminant polymorphe de `StudySession`). `RevisionSetManage.vue`
  retiré (doublon de `RevisionSetDetail.vue`). Vérification visuelle réelle faite dès cette
  clôture (pas différée). Détail complet : `workflow/reviser-hub/JOURNAL.md`. Prochaine action :
  demander à l'utilisateur de pousser `feature/reviser-hub`, puis ouvrir la PR.
- 2026-08-29 — [bibliotheque-ensembles] **PR #128 mergée dans `main`** (squash, `af20f00`),
  CI verte (6/6 checks). Chantier `clos`. Prochaine action : choisir le prochain chantier à
  ouvrir (`editeur-notes-notation-ia`, `reviser-hub`, `ecrans-peripheriques-visuels` ou
  `classes-examens-planning`).
- 2026-08-29 — [bibliotheque-ensembles] Vérification visuelle réelle faite (environnement natif
  hors Docker, à la demande explicite de l'utilisateur : venv Python local + SQLite pour le
  backend, Vite dev pour le frontend, extension Chrome pour desktop clair/sombre, Playwright
  375×812 pour mobile). A trouvé et corrigé un bug bloquant réel introduit par ce chantier
  (`RevisionService.answer_item`/`.grade_item` posaient `module=rset.type`, `None` pour un
  ensemble hétérogène → 500 sur toute tentative de révision réelle d'un tel ensemble ;
  `NOT NULL` sur `study_sessions.module` jamais couvert par un test avant celui-ci) et un
  défaut mineur (3 nouvelles routes absentes de la table de titres mobiles de `AppLayout.vue`).
  Détail complet, dont le diagnostic CSP hors-périmètre du `.env` racine de l'utilisateur :
  `workflow/bibliotheque-ensembles/JOURNAL.md`. Plan du chantier désormais 100% coché.
  Prochaine action : demander à l'utilisateur de pousser `feature/bibliotheque-ensembles` puis
  ouvrir la PR.
- 2026-08-28 — [bibliotheque-ensembles] Chantier clos (code) : 11 tâches TDD faites (dont 2
  ajoutées en cours d'exécution suite à des découvertes réelles — `TeacherDashboard.vue`
  cassé par la nullabilité de `RevisionSet.type`, type `flashcard` manquant dans
  `RevisionItemModal.vue`), un tour de correction sur `Binders.vue` (2 constats critiques :
  perte de fonctionnalité dans la fusion Decks+Ensembles, seuil de cartes dues affaibli).
  Portée finale confirmée propre (`git diff --stat`), 319/319 tests verts. Vérification
  visuelle non faite (environnement de dev partagé, risque d'interférence jugé supérieur au
  bénéfice) — écart documenté. Prochaine action : revue finale de branche, puis push + PR.
- 2026-08-28 — [bibliotheque-ensembles] Chantier activé, branche `feature/bibliotheque-ensembles`
  créée depuis `main` à jour (worktree `.worktrees/bibliotheque-ensembles`). Choisi comme
  prochain chantier (recommandation) : premier de l'ordre numérique des flux après le socle
  backend (flux 3, juste après flux 1), fraîchement débloqué, sans ambiguïté à réconcilier
  (contrairement à `editeur-notes-notation-ia`, dont le volet frontend est déjà partiellement
  implémenté sur une branche non mergée — laissé de côté pour l'instant). Prochain point : spec +
  plan détaillé via brainstorming.
- 2026-08-28 — [backend-ensembles-heterogenes] **PR #126 mergée dans `main`** (squash,
  `d2b6305`), CI verte (6/6 checks, dont « Backend · migrations (PostgreSQL) » qui valide la
  migration à froid — confirme a posteriori que la vérification manuelle passée localement
  n'était pas nécessaire). Chantier `clos`. `bibliotheque-ensembles` et `reviser-hub` débloqués.
  Prochaine action : choisir le prochain chantier à ouvrir.
- 2026-08-28 — [backend-ensembles-heterogenes] Chantier clos (code) : Task 4 terminée sur
  décision utilisateur explicite de passer la vérification Postgres manuelle (couverture SQLite
  85% jugée suffisante). Toutes les tâches du plan détaillé faites, commit `0e54608`. Prochaine
  action : demander à l'utilisateur de pousser `feature/backend-ensembles-heterogenes` puis ouvrir
  la PR (procédure `gestion-chantier`).
- 2026-08-28 — [backend-ensembles-heterogenes] Reprise après redémarrage : Tasks 1 et 2
  s'avèrent déjà faites (committées avant l'arrêt, journal pas mis à jour). Task 3 exécutée en
  TDD (câblage `item.type` dans `create_item`/`update_item`/`grade_item`/`answer_item`, bug de
  plan corrigé au passage — mauvaises URLs de test), commit `9c29185`, 85 % coverage. Task 4
  entamée : vérification Postgres réelle bloquée par un volume Docker local incohérent (séquelle
  de l'instabilité de la session précédente) — sa remise à zéro est bloquée par le hook de garde,
  reste à trancher par un humain. Détail complet :
  `workflow/backend-ensembles-heterogenes/JOURNAL.md`.
- 2026-08-28 — [backend-ensembles-heterogenes] Arrêt avant redémarrage PC (Docker Desktop
  instable). Aucun code touché, rien à perdre. Worktree `.worktrees/backend-ensembles-heterogenes`
  prête, venv local de secours documenté si Docker reste capricieux après redémarrage.
  Prochaine action : reprendre `subagent-driven-development` à la Task 1. Détail complet :
  `workflow/backend-ensembles-heterogenes/JOURNAL.md`.
- 2026-08-28 — [backend-ensembles-heterogenes] Spec + plan écrits (4 tâches TDD). Découverte
  majeure : la fusion Deck/Flashcard toucherait 47 fichiers backend, reportée à des chantiers
  futurs distincts — ce chantier se limite au socle schéma (`type` au niveau de l'item, ajout
  du type `flashcard`). Prochain point : Task 1 (migration Alembic + modèles).
- 2026-08-28 — [backend-ensembles-heterogenes] Chantier activé (premier de l'ordre fixé,
  flux 1, bloquant). Branche `feature/backend-ensembles-heterogenes` créée depuis `main`
  à jour. Prochain point : écrire la spec détaillée du modèle de données cible.
- 2026-08-28 — 6 chantiers ouverts, migrés depuis `ETAT.md` § « Plan global par flux —
  extension révision hétérogène + assistant IA (2026-08-27) ». Aucun travail d'implémentation
  migré : tous les flux étaient déjà « pas commencé » ou « plan écrit, exécution pas
  commencée » — seule l'organisation en chantiers change, aucune décision fonctionnelle
  réécrite. Détail du regroupement et des correspondances flux→chantier dans le `CONTEXT.md`
  de chaque chantier. Commit : à suivre.
