# Bibliothèque — redesign selon les vraies maquettes Direction A

Statut : clos
Branche : feature/bibliotheque-redesign
PR : #132

## Pourquoi

Investigation faite en chat le 2026-08-30 à la demande explicite de l'utilisateur, sur le
modèle de la correction `reviser-hub` : `Binders.vue` (écran Bibliothèque) n'a jamais été
comparé aux vraies maquettes Direction A (`Bibliotheque.dc.html`, `Notes.dc.html`) — confirmé
via l'historique git (le commit fondateur `77ff833` et son `docs/ui-redesign-plan.md` ne
mentionnent jamais le canvas). `RevisionSetDetail.vue`/`RevisionSetModal.vue`
(chantier `bibliotheque-ensembles`) ont bien été vérifiés — hors scope ici, sauf vérification
rapide de non-régression en fin de chantier.

**Périmètre : `Binders.vue` uniquement.** `PDFs.vue`/`Diagrams.vue` montrent le même genre
d'écart (documenté dans le spec ci-dessous à titre de contribution), mais sont déjà dans le
périmètre du chantier planifié `ecrans-peripheriques-visuels` — pas dupliqués ici.

## Comment

Voir spec complet : `docs/superpowers/specs/2026-08-30-bibliotheque-redesign-design.md`
(constat écran par écran + § « Décisions actées en chat » : arbre de sous-dossiers retiré au
profit d'une grille récursive, contenu non rangé accessible via un classeur virtuel « Non
classé », onglet « Autres » conservé tel quel). Plan détaillé (4 tâches TDD, exécuté en
`subagent-driven-development`) : `docs/superpowers/plans/2026-08-30-bibliotheque-redesign.md`.

## Dépendances

Aucune dépendance technique bloquante identifiée.

## Historique complet des décisions

`docs/superpowers/specs/2026-08-30-bibliotheque-redesign-design.md`.
