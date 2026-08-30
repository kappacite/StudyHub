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
