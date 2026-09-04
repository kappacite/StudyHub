# Diagrammes — liens, ancrage, routage (Phase 5, cycle 5)

Statut : ouvert
Branche : feature/diagrammes-liens-ancrage
PR : (aucune)

## Pourquoi

Cycle 5/14 de la refonte Phase 5 (`docs/PROMPT_DEMARRAGE.md` §8), suite de
`diagrammes-placement-selection` (cycle 4, PR #148 mergée). Séquence complète :
`workflow/diagrammes-modele-document/CONTEXT.md`.

**Constat de départ** : `LinkElement` existe dans le modèle de document depuis le cycle 1
(`fromId`/`toId`/`label`/`arrow`/`dashed`/`routingPoints`), et `migrateLegacyV0ToV1` migre
déjà les anciennes connexions vers ce type -- mais `DiagramCanvas.vue` ne rend que les
éléments `kind: 'shape'`. Un document migré contenant des liens les charge silencieusement
sans jamais les afficher. Ce cycle corrige ça : rendu des liens, calcul d'ancrage sur le bord
d'une forme (pas son centre), et création d'un lien par geste.

## Portée de ce chantier (et exclusions explicites)

- **Ancrage** : point où un lien touche le bord d'une forme, pas son centre. Fonction pure,
  testable sans DOM (§8.7).
- **Rendu** : les liens existants du document s'affichent, avec flèche/pointillés selon leurs
  champs, et un tracé passant par leurs `routingPoints` s'il y en a (déjà dans le modèle,
  jamais rendus jusqu'ici).
- **Création d'un lien** : `Maj` maintenu + glisser d'une forme vers une autre crée un
  `LinkElement` via `DiagramHistory.execute({type:'add-element', ...})` -- réutilise la
  commande générique du cycle 2, aucun nouveau type de commande nécessaire.

**Exclu de ce cycle** (comme le cycle 4 a explicitement exclu redimensionnement/rotation/etc.,
même logique ici) :
- Édition interactive des points de routage (en ajouter en glissant sur le tracé, en déplacer
  un existant) : le modèle et le rendu supportent déjà `routingPoints` s'il y en a, mais aucun
  geste ne permet encore d'en créer ou d'en déplacer un depuis ce chantier. Un lien migré
  depuis le cycle 1 n'a jamais de `routingPoints` (§ absent du format v0), donc l'absence de
  cette interaction ne régresse rien d'existant -- juste une capacité du modèle pas encore
  exposée à l'utilisateur, à traiter dans un futur cycle.
- Réancrage automatique quand une forme liée est supprimée : un lien dont `fromId`/`toId` ne
  correspond plus à aucune forme devient orphelin. Décision : le rendu l'ignore silencieusement
  (pas d'exception, pas d'affichage cassé) plutôt que de le supprimer automatiquement ou de le
  signaler -- nettoyage explicite laissé à un futur cycle (probablement rattaché à la
  suppression elle-même, pas encore implémentée : le cycle 4 n'a pas non plus de suppression
  d'élément interactive).

## Arbitrage — ancrage simplifié sur le rectangle englobant

L'ancrage utilise le rectangle englobant de la forme (`elementBounds`, déjà existant depuis le
cycle 3) pour toutes les formes, y compris cercle/ellipse -- pas d'intersection elliptique
précise. Le point d'ancrage d'un cercle atterrit donc légèrement au coin de sa boîte
englobante plutôt que exactement sur son contour dans les angles obliques. Simplification
assumée : l'écart visuel est mineur (quelques pixels sur un petit cercle) et une intersection
elliptique exacte ajoute de la complexité géométrique sans bénéfice proportionné à ce stade --
à corriger si un besoin réel se présente (ex. un gabarit du cycle 10 où ça se voit).

## Dépendances

Suit `diagrammes-placement-selection` (cycle 4, PR #148 mergée) -- réutilise la sélection/le
geste de glisser déjà en place, et `DiagramHistory.execute()` (cycle 2) pour la création de
lien (commande `add-element` existante, pas de nouveau type).

## Historique complet des décisions

Ce fichier + `workflow/diagrammes-liens-ancrage/JOURNAL.md`. Séquence complète des 14 cycles :
`workflow/diagrammes-modele-document/CONTEXT.md`. Spec canonique : `docs/PROMPT_DEMARRAGE.md`
§8.
