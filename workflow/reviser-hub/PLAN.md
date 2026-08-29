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

## Correction — les vraies maquettes Direction A n'avaient pas été consultées

Constat post-clôture (revue utilisateur) : la clôture ci-dessus n'avait jamais ouvert les vraies
maquettes Direction A (`Reviser.dc.html`, `RevisionSetStats.dc.html`, `RevisionBinderStats.dc.html`,
`RevisionSetManage.dc.html`, extraites de l'artefact Claude Design publié) — répétition de l'erreur
documentée dans la mémoire `migration-ecran-verify-mockup`. Correctif détaillé :
`docs/superpowers/specs/2026-08-29-reviser-hub-redesign.md` (corrige/étend le spec original) et
`docs/superpowers/plans/2026-08-29-reviser-hub-redesign.md` (8 tâches TDD, subagent-driven-development).

- [x] **Task 1-2 (backend + frontend)** : `focus_service.get_today_items` gagne un 4ᵉ bloc
  (ensembles de révision dus, groupés par ensemble comme `deck_items`) ; `FocusItem.type` élargi
  à `'revision_set'` côté frontend.
- [x] **Task 3** : `NoteFeynman.vue` créé (route `notes/:id/feynman`), extrait de l'onglet Feynman
  de `Reviews.vue` (absent de la maquette `Reviser.dc.html`, qui n'a aucun onglet IA).
- [x] **Task 4** : génération de flashcards IA déplacée vers `Decks.vue`
  (`decksStore.generateFlashcards()`).
- [x] **Task 5** : `RevisionSetStats.vue` reconstruit selon `RevisionSetStats.dc.html` — nouvelle
  agrégation backend (répartition par notation SM-2, progression 6 semaines, historique par jour),
  retrait de la section « Éléments » (doublon de `RevisionSetDetail.vue`/`RevisionSetTypeItems.vue`,
  absente de la maquette).
- [x] **Task 6** : `RevisionBinderStats.vue` reconstruit selon `RevisionBinderStats.dc.html` —
  liste fusionnée decks + ensembles triée par maîtrise, « Répartition par type » conservée en
  complément.
- [x] **Task 7** : `Reviews.vue` reconstruit en flux unifié « ce qui est dû » (2503→381 lignes) —
  onglets/tabs, 5 onglets classiques, 4 outils IA et gestion de decks retirés (tous relogés
  ailleurs, vérifié par grep sur tout `web/src`). Corrige au passage un vrai bug pré-existant :
  `studyItem()` n'avait aucune branche pour `type: 'revision_set'`.
- [x] **Task 8** : vérification visuelle réelle contre les vraies maquettes (pas seulement
  non-régression) — voir journal pour le détail.

Chaque tâche a eu sa revue dédiée (spec + qualité) ; 3 tâches ont nécessité un tour de correction
(Task 4 et 6 : appel API direct introduit dans un composant, contraire à la règle « API uniquement
dans stores/services » ; Task 5 : libellé de colonne non conforme à la maquette, 3 seuils de
couleur différents pour un même concept unifiés en un seul, section « Éléments » retirée ; Task 7 :
`/decks` avait perdu son seul point d'entrée de navigation après le retrait de la gestion de decks).
Détail complet des rulings et des revues : ledger `.superpowers/sdd/2026-08-29-reviser-hub-redesign/progress.md`
(supprimé après clôture, l'historique git fait foi).
