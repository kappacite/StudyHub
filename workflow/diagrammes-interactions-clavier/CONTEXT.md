# Diagrammes — interactions clavier (Phase 5, cycle 6)

Statut : ouvert
Branche : feature/diagrammes-interactions-clavier
PR : (aucune)

## Pourquoi

Cycle 6/14 de la refonte Phase 5 (`docs/PROMPT_DEMARRAGE.md` §8), suite de
`diagrammes-liens-ancrage` (cycle 5, PR #149 mergée). Séquence complète :
`workflow/diagrammes-modele-document/CONTEXT.md`.

§8.4 : « Création au clavier de bout en bout. On doit pouvoir construire une carte
conceptuelle de trente nœuds sans toucher la souris : créer un frère, créer un enfant, naviguer
entre éléments, renommer, supprimer. Un élément créé au clavier est placé automatiquement à
côté de son origine, sans chevauchement... Sans ça, personne ne schématise en cours. » Jusqu'ici
(cycles 3-5), toute interaction de `DiagramCanvas.vue` est à la souris -- ce cycle lui donne un
équivalent clavier complet.

## Raccourcis retenus

Convention outliner/carte mentale classique (Workflowy, FreeMind), sans conflit avec les
gestes souris existants (`Maj` = création de lien, cycle 5) :

- **Entrée** : créer un frère (nouvelle forme au même niveau que la sélection).
- **Tab** : créer un enfant (nouvelle forme + lien depuis la sélection).
- **Flèche droite/gauche** : naviguer vers l'élément suivant/précédent (ordre du tableau
  `elements` -- pas de navigation spatiale, plus simple et suffisant pour ce cycle).
- **F2** : renommer la sélection (entrée de texte superposée).
- **Suppr/Retour arrière** : supprimer la sélection.

Aucun raccourci n'agit si rien n'est sélectionné, sauf flèche droite/gauche qui sélectionne
alors le premier élément.

## Arbitrage — placement sans chevauchement

`computeSiblingPosition(originBounds, existingBounds[], gap)` : place le nouvel élément
immédiatement à droite de l'origine (`origin.maxX + gap`), puis le décale par incréments vers
la droite tant qu'il chevauche une forme existante. Algorithme volontairement simple (pas de
recherche de la position "la plus proche" dans toutes les directions) -- suffisant pour
l'exigence du §8.4 (pas de chevauchement), une disposition plus fine relève des commandes de
rangement (cycle 9).

**Créer un enfant = deux commandes, pas une** : ajouter la forme puis ajouter le lien sont deux
`DiagramHistory.execute()` séquentiels (le vocabulaire de commandes du cycle 2 n'a qu'un
`add-element` par élément, pas de commande composite). Rugosité UX assumée et documentée :
annuler une création d'enfant demande deux Annuler, pas un. Étendre `Command` à une variante
composite n'est pas justifié par un besoin réel pour l'instant (YAGNI) -- à revisiter si ça
s'avère gênant en usage réel.

## Arbitrage — renommage

Aucune édition de texte en place n'existe encore pour le libellé d'une forme (propriété
statique fixée à la création). `F2` affiche une entrée de texte HTML superposée au canevas
(position calculée depuis les coordonnées écran de la forme sélectionnée), pas une édition
SVG native -- **Entrée** commet via `update-element`, **Échap** annule sans commande. C'est
une solution minimale, pas l'éditeur de texte riche du cycle 8 (conteneurs/texte libre/
images/LaTeX) -- juste assez pour qu'un libellé créé au clavier ne reste pas générique.

## Dépendances

Suit `diagrammes-liens-ancrage` (cycle 5, PR #149 mergée) -- réutilise `add-element`/
`update-element`/`remove-element` (cycle 2, aucune nouvelle commande), `computeAnchorPoint`
(cycle 5, pour le lien créé par « créer un enfant »).

## Historique complet des décisions

Ce fichier + `workflow/diagrammes-interactions-clavier/JOURNAL.md`. Séquence complète des 14
cycles : `workflow/diagrammes-modele-document/CONTEXT.md`. Spec canonique :
`docs/PROMPT_DEMARRAGE.md` §8.
