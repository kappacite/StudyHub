# Diagrammes — placement, sélection, magnétisme (Phase 5, cycle 4)

Statut : ouvert
Branche : feature/diagrammes-placement-selection
PR : (aucune)

## Pourquoi

Cycle 4/14 de la refonte Phase 5 (`docs/PROMPT_DEMARRAGE.md` §8), suite de
`diagrammes-canevas-pan-zoom` (cycle 3, PR #147 mergée). Séquence complète :
`workflow/diagrammes-modele-document/CONTEXT.md`. Premier cycle où les éléments deviennent
interactifs — jusqu'ici `DiagramCanvas.vue` n'affichait qu'en lecture seule.

## Portée de ce chantier (et ce qui en est explicitement exclu)

Titre du cycle 4 dans la séquence imposée (§8.9) : « Placement, sélection, magnétisme, guides
d'alignement ». Le §8.4 (« Fluidité ») décrit une liste plus large de manipulations directes
(poignées de redimensionnement, rotation, ordre de superposition, duplication au glisser,
copier-coller, sélection multiple au lasso, groupes, verrouillage) qui n'a **pas** de cycle
dédié dans la liste des 14 -- ambiguïté de la spec, tranchée ici : ce chantier couvre
strictement le contenu littéral de son titre (sélection simple d'un élément, déplacement par
glisser, magnétisme, guides d'alignement). Redimensionnement/rotation/z-order/duplication/
copier-coller/sélection multiple/groupes/verrouillage restent **hors périmètre**, à traiter
dans un cycle ultérieur (probablement à insérer dans la séquence, pas couvert tel quel par un
des 10 cycles restants) -- signalé pour ne pas être oublié, pas traité par surprise ici.

## Arbitrage — une seule commande par geste de glisser

Chaque `mousemove` pendant un glisser ne doit **pas** produire une commande dans
`DiagramHistory` (cf. cycle 2) : ça flooderait la pile d'annulation d'états intermédiaires
(annuler un glisser demanderait alors N pressions d'Annuler au lieu d'une seule). Position
« live » suivie dans un état local du composant pendant le geste ; une seule
`DiagramHistory.execute(doc, {type:'update-element', ...})` à la relâche de la souris, avec
la position finale (déjà magnétisée). C'est la même logique que « ranger la sélection » sera
pour le cycle 9 (§8.2.3 : une commande, annulable comme une autre) -- appliquée ici au geste
de déplacement le plus basique.

**Sélection** : état purement local à `DiagramCanvas.vue` (`selectedElementId`), **pas**
persisté dans `DiagramDocumentV1` -- la sélection n'est pas un fait du document, c'est un fait
de la vue courante (cf. cycle 1, vocabulaire du document : rien de tel n'y figure, à raison).

**Distinction clic / glisser-panoramique** : un `mousedown` sur le fond suivi d'un `mouseup`
sans dépassement d'un seuil de déplacement (quelques pixels) est un clic (désélectionne) ;
au-delà du seuil, c'est un panoramique (cycle 3, inchangé). Même logique pour un élément :
sous le seuil = sélection, au-delà = déplacement.

**Magnétisme et guides d'alignement** (§8.4) : fonctions pures et testables sans DOM (§8.7).
Magnétisme sur grille (pas fixe, ex. 10 unités) et sur les bords des autres éléments (le bord
gauche/droit/haut/bas/centre d'un élément déplacé s'aligne sur celui d'un voisin dans un seuil
de quelques pixels-écran). Désactivable au clavier pendant le geste (`Alt` maintenu) --
exigence explicite du §8.4.

## Dépendances

Suit `diagrammes-canevas-pan-zoom` (cycle 3, PR #147 mergée) et `diagrammes-commandes-
annulation` (cycle 2, PR #146 mergée) -- première utilisation réelle de
`DiagramHistory.execute()` depuis un geste utilisateur.

## Historique complet des décisions

Ce fichier + `workflow/diagrammes-placement-selection/JOURNAL.md`. Séquence complète des 14
cycles : `workflow/diagrammes-modele-document/CONTEXT.md`. Spec canonique :
`docs/PROMPT_DEMARRAGE.md` §8.
