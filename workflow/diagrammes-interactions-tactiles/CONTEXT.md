# Diagrammes — interactions tactiles (Phase 5, cycle 7)

Statut : ouvert
Branche : feature/diagrammes-interactions-tactiles
PR : (aucune)

## Pourquoi

Cycle 7/14 de la refonte Phase 5 (`docs/PROMPT_DEMARRAGE.md` §8), suite de
`diagrammes-interactions-clavier` (cycle 6, PR #150 mergée). Séquence complète :
`workflow/diagrammes-modele-document/CONTEXT.md`.

§8.4 : « Tactile de premier rang : pincer pour zoomer, appui long, cibles ≥ 44 px, aucun
conflit avec le défilement de page ni le geste de retour natif. Attention au conflit propre au
canevas libre : distinguer un déplacement d'élément d'un panoramique du canevas au doigt
demande une règle explicite, à décider et à tester sur appareil réel, pas en émulation
navigateur. »

## Investigation

`DiagramCanvas.vue` (cycles 3-6) n'écoute que des événements souris (`mousedown`/`mousemove`/
`mouseup`/`wheel`) -- aucun événement tactile n'est géré aujourd'hui. Le `<svg>` porte déjà
`class="... touch-none ..."` depuis le cycle 3 (`touch-action: none`), qui empêche le
navigateur de intercepter les gestes tactiles pour son propre défilement/zoom/retour natif --
la condition « aucun conflit » du §8.4 est donc déjà en place structurellement, il reste à
implémenter la gestion tactile elle-même.

**Limite honnête, à ne pas dissimuler** : cet environnement n'a ni appareil tactile réel ni
émulateur mobile. §8.4 exige explicitement une vérification « sur appareil réel, pas en
émulation navigateur » pour la règle de distinction déplacement/panoramique. Ce chantier
implémente et teste (événements `Touch`/`TouchEvent` synthétiques, §8.7 : les interactions ne
relèvent pas de l'exception écran-capture) la logique, mais **la sensation réelle (pincer,
cibles ≥ 44 px, absence de conflit avec le geste de retour natif) reste non vérifiée sur
matériel réel** -- signalé explicitement à l'utilisateur en fin de chantier plutôt que déclaré
vérifié à tort.

## Arbitrage — écouteurs tactiles additifs, pas une bascule vers Pointer Events

Option envisagée : remplacer `mousedown`/`mousemove`/`mouseup` par les Pointer Events
(`pointerdown`/`pointermove`/`pointerup`), qui unifient souris et tactile dans une seule API.
**Écartée pour ce chantier** : ça imposerait de réécrire tous les gestionnaires souris des
cycles 3-6 et de mettre à jour la totalité des déclenchements `mousedown`/`mousemove`/
`mouseup` déjà présents dans `DiagramCanvas.spec.ts` (nombreux tests déjà verts) -- un
changement à grande surface pour un seul chantier, risque disproportionné par rapport au
bénéfice. Retenu à la place : des écouteurs `touchstart`/`touchmove`/`touchend` **additifs**,
appelant la même logique de décision (seuil clic/glisser, magnétisme) que les gestionnaires
souris via des fonctions pures partagées -- pas de duplication de la décision, seulement du
branchement d'événements. Une unification complète vers Pointer Events reste une piste valable
si maintenir deux jeux de gestionnaires devient pénible en pratique (à revisiter, pas
maintenant -- YAGNI).

## Portée

- **Glisser à un doigt** : panoramique du fond ou déplacement d'un élément sélectionné, même
  règle seuil clic/glisser que la souris (cf. cycles 3-4).
- **Pincer à deux doigts** : zoom centré sur le point médian des deux doigts, réutilise
  `zoomAt` (cycle 3).
- **Appui long sur un élément** : équivalent tactile de `Maj` + glisser (cycle 5, aucune touche
  modificatrice possible au doigt) -- entre en mode création de lien, un glissé vers un autre
  élément puis le relâchement crée le lien.
- **Cibles ≥ 44 px** : les formes créées (clavier cycle 6, souris) ont déjà une taille par
  défaut de 50×50 -- satisfait sans changement de code pour les créations actuelles. Pas
  d'application/redimensionnement automatique pour des formes plus petites (le
  redimensionnement reste hors périmètre depuis le cycle 4) -- à garder en tête pour les
  gabarits du cycle 10.

## Dépendances

Suit `diagrammes-interactions-clavier` (cycle 6, PR #150 mergée). Réutilise `zoomAt`/`panBy`
(cycle 3), `computeAlignmentSnap`/`snapToGrid` (cycle 4), `add-element` (cycle 2, création de
lien par appui long).

## Historique complet des décisions

Ce fichier + `workflow/diagrammes-interactions-tactiles/JOURNAL.md`. Séquence complète des 14
cycles : `workflow/diagrammes-modele-document/CONTEXT.md`. Spec canonique :
`docs/PROMPT_DEMARRAGE.md` §8.
