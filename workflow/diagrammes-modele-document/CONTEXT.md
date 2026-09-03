# Diagrammes — modèle de document versionné (Phase 5, cycle 1)

Statut : ouvert
Branche : feature/diagrammes-modele-document
PR : (aucune)

## Pourquoi

Demande explicite de l'utilisateur (2026-09-03) : « entame le rework de l'outil de
diagramme ». Investigation avant ouverture (voir aussi le fil de discussion) : ce n'est pas
une retouche visuelle mais la **Phase 5** déjà entièrement spécifiée dans
`docs/PROMPT_DEMARRAGE.md` §8 (« Refonte de l'outil de diagrammes ») — un canevas libre à
reconstruire, pas à repeindre, parce que l'existant superpose un canevas SVG glisser-déposer
et un mode "Code Mermaid" qui ne peuvent pas rester synchronisés (Mermaid ne représente pas
une position manuelle de nœud). Le projet est actuellement en **Phase 4** (`ETAT.md`) ; ouvrir
ce chantier démarre donc la Phase 5 en avance sur la séquence documentée — validé
explicitement par l'utilisateur après qu'on le lui a signalé (question posée, réponse :
chantier complet Phase 5).

**Aucune maquette visuelle n'existe pour le canevas/éditeur** — seul l'écran de galerie
d'entrée a une maquette (`Diagrams.dc.html`, cf. note du 2026-08-30 dans
`workflow/ecrans-peripheriques-visuels/CONTEXT.md`, citée telle quelle : *« Diagrams.dc.html
montre une galerie (grille de vignettes) comme écran d'entrée, avant d'ouvrir un éditeur... qui
n'a pas de maquette propre »*). §8 de `PROMPT_DEMARRAGE.md` est donc la seule référence de
conception pour ce chantier et ceux qui suivront — de la prose d'architecture, pas des pixels.

## Portée de CE chantier (cycle 1 seulement)

§8.9 fixe la séquence et est explicite : **« Un chantier par cycle, chacun commité
séparément »**. L'ordre n'est pas négociable (reprendre le modèle après avoir construit
dessus coûte le double) :

1. **Modèle de document et sérialisation versionnée** ← CE CHANTIER
2. Commandes et annulation
3. Canevas, panoramique, zoom, rendu borné à la fenêtre de vue
4. Placement, sélection, magnétisme, guides d'alignement
5. Liens, ancrage, routage
6. Interactions clavier
7. Interactions tactiles
8. Conteneurs, texte libre, images, LaTeX
9. Commandes de rangement
10. Gabarits
11. Intégrations StudyHub (notes, flashcards, diagramme muet)
12. Import/export Mermaid
13. Export image et PDF
14. Partage et marketplace

Chaque point ci-dessus (2 à 14) sera son propre chantier `workflow/diagrammes-<étape>/`,
ouvert une fois le précédent clos. Ne pas anticiper leur contenu ici au-delà de ce qui est
nécessaire pour ne pas fermer de porte dans le modèle de données.

## Investigation de l'existant (avant tout code)

`backend/app/models/diagram.py` : colonne `code` (Text) commentée *"Code Mermaid.js"* — commentaire
obsolète, confirmé faux (aucune dépendance Mermaid dans `web/package.json`, déjà noté en
phase 1 de `PROMPT_DEMARRAGE.md` §8.1). En pratique le backend traite `code` comme une chaîne
opaque (aucune logique dépendante du contenu côté `diagram_service.py`/`app/api/v1/diagrams.py`)
— **aucun changement backend requis pour ce cycle**, le modèle de document est un sujet
frontend jusqu'à ce qu'un cycle ultérieur ait besoin de logique serveur dessus (recherche
plein texte sur le contenu, par exemple).

`web/src/views/Diagrams/Diagrams.vue` (1789 lignes, aucun test dédié) sérialise aujourd'hui
dans `code` un JSON ad hoc, non versionné, à 5 tableaux/champs parallèles :
- `nodes: VisualNode[]` — `{ id, label, type: 'rect'|'circle'|'diamond'|'ellipse'|'text'|'sticky', x, y, color, width?, height? }`
- `connections: Connection[]` — `{ from, to, label?, arrow?, dashed? }` (pas de points de routage manuels)
- `masks: Mask[]` — `{ id, x, y, width, height, label }` (occlusion d'image, ex. « masquer un schéma d'anatomie »)
- `backgroundImage: string | null` — une seule image de fond globale au canevas, pas un élément positionnable
- `drawings: PenStroke[]` — traits libres à main levée

L'undo/redo actuel (`snapshotDoc`/`applySnapshot`) est une pile de 50 snapshots JSON complets
— pas le modèle de commandes réversibles visé par §8.7/cycle 2, mais ça confirme que
l'historique est déjà un besoin réel, pas une nouveauté.

## Arbitrage — modèle de document v1

Décisions déléguées par l'utilisateur (mêmes termes que les chantiers précédents de cette
session : arbitrages tranchés et documentés ici, pas de question en chat sur ces détails
d'implémentation).

**Un seul tableau d'éléments, ordre = ordre d'empilement** — conforme à §8.3 (« pas un moteur
par type de diagramme, mais un seul canevas, un vocabulaire d'éléments ») :

```ts
interface DiagramDocumentV1 {
  schema_version: 1
  elements: DiagramElement[]   // array order = z-order
  backgroundImage: string | null  // reste un champ document, pas un élément (cf. ci-dessous)
}

type DiagramElement = ShapeElement | LinkElement | StrokeElement | OcclusionMaskElement

interface BaseElement {
  id: string        // uuid stable, jamais réutilisé après suppression
  x: number
  y: number
  width: number
  height: number
  rotation: number   // degrés, 0 par défaut — aucun élément actuel n'est tourné, mais le
                      // champ existe dès v1 pour ne pas re-migrer au cycle manipulation directe
  locked: boolean
}

interface ShapeElement extends BaseElement {
  kind: 'shape'
  shape: 'rect' | 'circle' | 'diamond' | 'ellipse' | 'text' | 'sticky'
  label: string
  color: string
}

interface LinkElement extends BaseElement {
  // x/y/width/height/rotation/locked de BaseElement non pertinents pour un lien
  // (pas de position propre) -- portés quand même pour l'uniformité du type, ignorés
  // par le rendu. Le cycle 5 (liens/ancrage/routage) décidera s'il faut les retirer
  // du type ou les réutiliser pour la boîte englobante du libellé.
  kind: 'link'
  fromId: string
  toId: string
  label: string
  arrow: 'end' | 'both' | 'none'
  dashed: boolean
  routingPoints: { x: number; y: number }[]  // vide aujourd'hui (v0 n'en a pas), le
                                               // cycle 5 les rendra éditables
}

interface StrokeElement extends BaseElement {
  kind: 'stroke'
  points: { x: number; y: number }[]
  color: string
  strokeWidth: number
}

interface OcclusionMaskElement extends BaseElement {
  kind: 'occlusion-mask'
  label: string
}
```

**Pourquoi pas déjà « container »/« texte libre »/« image posée »/LaTeX (§8.3)** : ces types
appartiennent au cycle 8, pas à celui-ci. Les ajouter maintenant serait de la spéculation
(YAGNI) et un bump de version supplémentaire à gérer sans bénéfice immédiat — le mécanisme de
version + migration mis en place ici (voir plus bas) est justement ce qui permettra de les
ajouter proprement en `schema_version: 2` le moment venu, sans casser les documents v1.

**Pourquoi `backgroundImage` reste un champ document et pas un `ImageElement`** : aujourd'hui
c'est une image unique, non déplaçable, non redimensionnable, liée à l'occlusion — sémantique
différente de l'« image posée sur le canevas » du cycle 8 (positionnable, dupliquable, etc.).
Les fondre prématurément forcerait une modélisation qui n'est pas encore justifiée par un
besoin réel ; séparer proprement main-tenant coûte moins cher qu'une fausse unification à
défaire plus tard.

**Migration des documents existants** : la base contient déjà de vrais diagrammes utilisateur
au format v0 (ad hoc, sans `schema_version`). `migrateLegacyV0ToV1()` doit convertir
`nodes → ShapeElement[]`, `connections → LinkElement[]` (routingPoints vide),
`masks → OcclusionMaskElement[]`, `drawings → StrokeElement[]`, `backgroundImage` inchangé —
sans perte. C'est le cas non-régression le plus important du chantier : les diagrammes réels
existants doivent continuer à s'ouvrir (cf. §8.8 : « les documents de toutes les versions
antérieures s'ouvrent encore »).

## Dépendances

Aucune dépendance amont bloquante. Recoupement avec `workflow/ecrans-peripheriques-visuels`
(statut `planifié`) : son point « Diagrammes — coquille uniquement (`Diagrams.vue`), pas le
canevas/moteur (hors périmètre phase 4, prévu phase 5) » reste une migration **visuelle pure**
de la galerie d'entrée, indépendante du modèle de données ici construit — les deux chantiers
ne se chevauchent pas et peuvent avancer dans n'importe quel ordre.

## Historique complet des décisions

Ce fichier + `workflow/diagrammes-modele-document/JOURNAL.md`. Spec canonique complète :
`docs/PROMPT_DEMARRAGE.md` §8 (à relire pour tout doute sur un cycle futur).
