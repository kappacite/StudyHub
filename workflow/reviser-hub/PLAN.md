# Plan — reviser-hub

- [x] Attendre que `backend-ensembles-heterogenes` soit livré — mergé (PR #126) ; débloqué aussi
  par `bibliotheque-ensembles` (PR #128, mergée), dont `RevisionSetDetail.vue` retire le besoin
  de migrer `RevisionSetManage.vue`.
- [x] Écrire la spec + plan détaillé via `superpowers:brainstorming` puis
  `superpowers:writing-plans` — `docs/superpowers/specs/2026-08-29-reviser-hub-design.md` +
  `docs/superpowers/plans/2026-08-29-reviser-hub.md` (11 tâches TDD, exécutées en
  subagent-driven-development).
- [x] Correctif backend (Tasks 1-4) — `RevisionStatsService` filtrait les sessions par
  `rset.type` (type de l'*ensemble*) au lieu de `item.type` (type de l'*item*, discriminant
  polymorphe réel de `StudySession`) : les stats de tout ensemble hétérogène déjà révisé
  étaient silencieusement vides. Corrigé dans `get_item_stats`, `get_set_stats`,
  `get_binder_stats` + schémas Pydantic (`RevisionSetStats.type`/`RevisionSetSummary.type`
  nullable, `RevisionItemSummary.type` ajouté).
- [x] Extraction d'un utilitaire partagé `REVISION_ITEM_TYPE_META` (icônes/libellés par type
  d'item), refactor non-behaviorale de `RevisionSetDetail.vue`, réutilisé par
  `RevisionSetStats.vue` et `RevisionBinderStats.vue` (Task 5).
- [x] `RevisionSetStats.vue` : badge « Mixte » pour un ensemble hétérogène, icône de type par
  item, retrait d'un prop `locked-type` déjà inerte (Task 7).
- [x] `RevisionBinderStats.vue` : répartition par type reconstruite depuis le type réel de
  chaque item (pas de l'ensemble), badge « Mixte » sur les lignes d'ensemble (Task 8).
- [x] **`RevisionSetManage.vue` retiré, pas migré** (décision utilisateur en brainstorming) :
  fait doublon avec `RevisionSetDetail.vue` (chantier `bibliotheque-ensembles`), qui gère déjà
  nativement l'hétérogénéité. Route `/manage` redirige désormais vers `RevisionSetDetail`
  (Task 9).
- [x] `Reviews.vue` : 6ᵉ onglet « Mixte » (liste les ensembles `type: null`, renvoie vers
  `RevisionSetDetail.vue`), bouton « Gérer » repointé sur toutes les lignes vers
  `RevisionSetDetail.vue` au lieu de l'ancien `/manage` (Task 10).
- [x] Vérification visuelle clair/sombre × desktop/mobile — **faite dès cette clôture, pas
  différée** (leçon de `bibliotheque-ensembles`, où l'avoir différée avait caché un vrai bug
  bloquant). Environnement natif hors Docker : venv local + SQLite pour le backend, Vite dev
  pour le frontend, extension Chrome pour desktop clair/sombre, Playwright 375×812 pour mobile.
  A confirmé visuellement le correctif backend (stats à 100% de réussite sur un ensemble
  hétérogène réellement révisé, badges « Mixte », répartition par type correcte au niveau
  classeur, redirection `/manage` fonctionnelle) sans trouver de nouveau défaut. Détail complet
  dans le journal. `ETAT.md` §« Plan global par flux » précise ne plus être mis à jour au fil de
  l'exécution (suivi déplacé vers `workflow/`) — rien à y changer, cohérent avec
  `bibliotheque-ensembles`.
