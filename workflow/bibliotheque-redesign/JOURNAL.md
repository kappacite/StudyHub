# Journal — bibliotheque-redesign

## 2026-08-30 (planification, pas encore ouvert)

Chantier créé en `Statut : planifie` suite à une investigation en chat demandée explicitement
par l'utilisateur ("il semblerait que pour cette section aussi tu n'as pas vérifié le canvas").
Vérifié : oui pour `Binders.vue` (jamais consulté depuis sa création, commit `77ff833`,
2026-06-21) ; non pour `RevisionSetDetail.vue`/`RevisionSetModal.vue` (déjà vérifiés par
`bibliotheque-ensembles`, décisions tracées dans leur spec).

Recoupement trouvé et corrigé en cours de route : une première version de ce chantier incluait
`PDFs.vue`/`Diagrams.vue` dans son périmètre — retiré après avoir découvert que ces 2 fichiers
sont déjà explicitement dans le plan du chantier `ecrans-peripheriques-visuels` (non commencé),
qui utilise le skill `migration-ecran` (consultation de la vraie maquette déjà native à sa
procédure). L'analyse mockup-vs-code de ces 2 écrans reste dans le spec de ce chantier à titre
de contribution pour qui ouvrira `ecrans-peripheriques-visuels`, mais aucune tâche de code ne
les concerne ici.

Spec complet : `docs/superpowers/specs/2026-08-30-bibliotheque-redesign-design.md`. Plan
brouillon (pas prêt à exécuter, requiert un brainstorming préalable) :
`docs/superpowers/plans/2026-08-30-bibliotheque-redesign.md`.

Aucune implémentation lancée, conformément à la demande explicite de l'utilisateur.

## 2026-08-30 (deuxième passe : les 5 écrans d'une note)

Demande explicite de l'utilisateur : "intègre bien tous les écrans de la partie bibliothèque -
notes sur le canvas". Extension de l'investigation à `NoteEdit.vue` et ses 4 outils IA
(Blurting, NoteQuiz, NoteEvaluation, NoteFeynman), chacun avec sa propre maquette. Résultat par
écran (détail complet dans le spec, § « Écrans d'une note ») :

- `NoteEdit.vue` : déjà pris en charge correctement (`editeur-notes-notation-ia`, maquette
  citée dès le début de son plan) — rien à faire ici.
- `NoteFeynman.vue` : déjà vérifié correct (`reviser-hub`, Task 3) — rien à faire ici.
- `Blurting.vue` : écart réel trouvé (rétention/bilan tuteur/cartographie des concepts/
  flashcards suggérées — rien de tout ça dans la maquette, qui ne montre qu'une carte simple
  clarté+jargon+lacunes+suggestion). Signalé à `ecrans-peripheriques-visuels`, dont le
  "retonation seulement" sous-estime probablement cet écart.
- `NoteQuiz.vue` : globalement aligné sur un examen rapide, non vérifié en profondeur, orphelin
  (aucun chantier ne le réclame) — risque jugé faible.
- `NoteEvaluation.vue` : **collision de nom découverte** — la maquette `NoteEvaluation.dc.html`
  correspond en fait à la future fonctionnalité « Notation » de `editeur-notes-notation-ia`
  (pas encore construite), pas à l'écran `NoteEvaluation.vue` qui existe déjà (implémente une
  fonctionnalité différente, l'Évaluation mixte). Note ajoutée au `CONTEXT.md` de ce chantier.

Toujours aucun code touché — uniquement de la documentation (spec + notes croisées dans les
`CONTEXT.md` des chantiers concernés). Le périmètre d'exécution de `bibliotheque-redesign`
reste `Binders.vue` uniquement ; ces 5 écrans n'y entrent pas.

## 2026-08-30 (décisions actées, chantier ouvert)

Utilisateur : "Détaille aussi leurs tâches et ensuite commence l'implémentation
bibliotheque-redesign". Détail des tâches ajouté aux `PLAN.md` de `ecrans-peripheriques-visuels`
et `editeur-notes-notation-ia` (toujours sans les exécuter). Pour ce chantier-ci : 2 décisions
produit tranchées en chat (`AskUserQuestion`, options recommandées retenues) :
- Arbre de sous-dossiers retiré, remplacé par une grille récursive (sous-classeurs affichés
  comme cartes au niveau courant, navigation par clic + fil d'ariane).
- Contenu non rangé accessible via un classeur virtuel « Non classé » sur la grille racine.

Plan détaillé écrit (4 tâches TDD) : `docs/superpowers/plans/2026-08-30-bibliotheque-redesign.md`.
Branche `feature/bibliotheque-redesign` créée depuis `main` à jour (worktree
`.worktrees/bibliotheque-redesign`) — renommée depuis la branche `docs/plan-bibliotheque-redesign`
qui portait les commits de planification (jamais poussée, donc renommage sans risque).
Chantier passé de `Statut : planifie` à `ouvert`. Exécution démarrée en
`subagent-driven-development`, suite ci-dessous.

## 2026-08-30 (exécution des 4 tâches, vérification visuelle, prêt à clôturer)

Les 4 tâches du plan exécutées via `subagent-driven-development` (implémenteur frais + revue
par tâche + revue finale). Détail complet dans le ledger
`.superpowers/sdd/2026-08-30-bibliotheque-redesign/progress.md`.

- Task 1 (commit `df54090`) : `BinderCard.vue` + `binderAggregate()` (fonction pure, comptes +
  dernière activité). Icône livre confirmée conforme à la maquette (`lucide-vue-next` `Book`).
- Task 2 (commit `850665e`, tâche à plus haut risque) : `SplitView` remplacé par la grille
  récursive. Distinction `filterBinderId`/`currentBinderId` correctement isolée (5 points
  d'usage, testée). Bug réel trouvé et volontairement différé à Task 3 : le bouton « Retirer du
  classeur » restait actif sur « Non classé ».
- Task 3 (commit `b21d1d3`) : bug de Task 2 corrigé (`canDetach = isOwner && isRealBinderId`),
  non-régression vérifiée sur les 11 fonctionnalités liées aux classeurs (détache, partage,
  tags, clone, bannière lecture seule…).
- Task 4 : vérification visuelle réelle (environnement natif, données de test créées via API,
  captures Playwright root/classeur/Non-classé × mobile/desktop × clair/sombre). Conforme aux
  maquettes et aux 2 décisions actées en chat. Non-régression live confirmée sur la fusion
  Deck+RevisionSet de `bibliotheque-ensembles` dans l'onglet Révision.
  Nouveau défaut trouvé en vérifiant à 375px (hors périmètre du plan mais exposé par lui) :
  `PageHeader.vue` (composant partagé) ne passait pas ses actions à la ligne, provoquant un
  débordement dès qu'un classeur affiche beaucoup de boutons (Task 2 en a ajouté un 6e).
  Corrigé (commit `0ddfaf1`, `flex-wrap` ajouté, testé) — bénéficie à tout écran utilisant
  `PageHeader` avec plusieurs actions, pas seulement celui-ci.

Environnement natif de vérification démonté (processus des ports 5052/5173 arrêtés). Les 4
tâches sont marquées complètes dans `PLAN.md`. Reste : revue finale de branche complète
(`subagent-driven-development`), puis clôture (`gestion-chantier`).

## 2026-08-30 (revue finale de branche, tour de correction, chantier clos)

Revue finale de branche (opus, base `23a5a8e` → `6f28aba`) : **avec corrections**. Confirmé
solide : distinction `filterBinderId`/`currentBinderId` réellement testée, isolation du
classeur virtuel vérifiée sur les 8 actions concernées, changement `PageHeader` vérifié sûr
pour ses 9 consommateurs réels. 3 constats Important + 4 Minor retenus (bon marché, chacun
justifié par une convention explicite du projet) :

1. Affichage des tags de classeur disparu partout (régression réelle — `TagBadge` retiré lors
   du passage arbre → grille, jamais réintégré dans `BinderCard`).
2. Couverture de test de l'invariant central de Task 3 (masquage sur « Non classé ») ~1/8
   seulement — seul le bouton détacher était testé.
3. Section « Sous-classeurs » vide en permanence sur tout classeur feuille — absente du
   mockup.
4-7. `highlighted` mort sur `BinderCard` + chrome codé à la main au lieu de composer
   `BaseCard` (violation d'une règle explicite de `components/CLAUDE.md`) ; garde
   défense-en-profondeur manquante sur `createFolder()` (cohérence avec `detachItem`/
   `confirmAttach`) ; commentaire explicatif sur le `flex-wrap` de `PageHeader`.

Constats mineurs restants explicitement écartés avec justification (perf `cardAggregate`,
suppression de sous-classeur nécessitant navigation — déjà documentée en commentaire,
`RevisionSet.updated_at` optionnel — corriger proprement toucherait 17 fichiers de test hors
périmètre, no-op silencieux sous filtre par tag actif — limitation préexistante, décalage de
fuseau horaire — même limitation déjà écartée par `reviser-hub`, `SplitView` orphelin — laissé
en histoire). Détail complet, avec vérifications directes de chaque constat contre le code
réel : `.superpowers/sdd/2026-08-30-bibliotheque-redesign/progress.md`.

**Tour de correction 1/5** (commits `e37fa41`/`6f174ca`/`44635b0`) : 6/7 corrigés proprement,
407/407 tests, `vue-tsc -b` propre. La re-revue ciblée a trouvé une **régression réelle**
introduite par la correction n°3 : la fusion des conditions avait fait sauter la garde qui
excluait la racine, faisant apparaître en permanence le titre « Sous-classeurs » au-dessus de
la grille racine (qui n'est pas une liste de sous-classeurs — `childrenAtCurrentLevel` contient
toujours la carte virtuelle "Non classé" à la racine, donc son `.length > 0` restait vrai).
Corrigée directement par le contrôleur (diagnostic déjà exact et complet fourni par la
re-revue, correction d'une ligne) : garde `v-if="currentBinderId !== null"` restaurée sur le
titre seul, test de régression ajouté (vérifié RED sans le correctif, GREEN avec), commit
`1257b8a`. Les 7 constats de la revue finale sont désormais tous réellement traités.

Chantier clos (code). 4 tâches d'implémentation + revue finale + 2 tours de correction, tous
conclus propres. Aucune fonctionnalité existante cassée (audit direct des 11 fonctionnalités
liées aux classeurs en Task 3, vérification visuelle live en Task 4). Prochaine action :
demander à l'utilisateur de pousser `feature/bibliotheque-redesign`, puis ouvrir la PR.
