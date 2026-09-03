# Diagrammes — commandes et annulation (Phase 5, cycle 2)

Statut : clos
Branche : feature/diagrammes-commandes-annulation
PR : #146

## Pourquoi

Cycle 2/14 de la refonte Phase 5 de l'outil de diagrammes (`docs/PROMPT_DEMARRAGE.md` §8),
demande explicite de l'utilisateur (« Fais tout » — poursuivre tous les cycles restants sans
re-demander confirmation à chaque fois). Contexte complet, séquence des 14 cycles, et
arbitrages de modélisation du cycle 1 : `workflow/diagrammes-modele-document/CONTEXT.md` (PR
#145, mergée) — non répété ici.

## Portée de ce chantier

§8.7 : « Chaque commande d'édition est spécifiée par un test avant d'exister. Invariant
d'annulation, testé par propriété : pour toute suite de commandes, annuler autant de fois
qu'il y a eu de commandes ramène à un document strictement identique à l'état initial. C'est
le test qui protège l'undo, et il doit être écrit en premier. »

Ce cycle construit l'infrastructure de commandes/annulation elle-même, avec le jeu minimal de
commandes génériques nécessaire pour la prouver — pas les gestes de canevas (cycle 3+) ni les
commandes de rangement (cycle 9), qui restent des chantiers séparés. Trois commandes
suffisent à couvrir le cas général (ajout, suppression, modification de champs) : `add-
element`, `remove-element`, `update-element`. Les commandes plus spécifiques (déplacement
explicite du cycle 4, ancrage de lien du cycle 5...) réutiliseront cette infrastructure sans
la modifier en profondeur.

## Arbitrage — mécanisme d'annulation

**Undo par snapshot du document, pas par commande inverse écrite à la main.** Chaque commande
appliquée capture le document `avant` en plus du document `après` (immutabilité déjà actée au
cycle 1 : `applyCommand` ne mute jamais, retourne toujours un nouveau `DiagramDocumentV1`).
Annuler restitue exactement l'objet `avant` capturé — garantie mécanique de l'invariant
d'annulation par construction, plutôt que par une fonction inverse par type de commande
(source d'erreurs subtiles si mal écrite, cf. discussion §8.7). C'est la même idée que le
`snapshotDoc`/`applySnapshot` déjà présent dans `Diagrams.vue` (pile de 50 JSON complets) —
ce cycle la remplace par une pile de commandes nommées et typées sur `DiagramDocumentV1`,
sans changer le principe qui fonctionnait déjà.

**Test par propriété : `fast-check` ajouté en devDependency.** Aucune librairie de test par
propriété n'existe dans `web/package.json` (vérifié) ; une boucle « génère N séquences
aléatoires à la main » n'offre ni le shrinking ni la reproductibilité par seed de `fast-check`,
qui est la référence de l'écosystème JS/TS pour exactement ce cas d'usage (invariant sur une
séquence arbitraire d'opérations). Justifie l'ajout d'une dépendance (règle 5 de l'échelle
ponytail : aucune dépendance déjà installée ne le fait aussi bien).

## Dépendances

Suit directement `diagrammes-modele-document` (cycle 1, PR #145 mergée) — réutilise
`DiagramDocumentV1`/`DiagramElement` sans modification de schéma. Aucune autre dépendance.

## Historique complet des décisions

Ce fichier + `workflow/diagrammes-commandes-annulation/JOURNAL.md`. Séquence complète des 14
cycles et spec canonique : voir `workflow/diagrammes-modele-document/CONTEXT.md` et
`docs/PROMPT_DEMARRAGE.md` §8.
