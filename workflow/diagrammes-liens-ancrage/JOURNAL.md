# Journal — diagrammes-liens-ancrage

## 2026-09-04 (ouverture)

Chantier ouvert immédiatement après la clôture de `diagrammes-placement-selection` (PR #148
mergée). Cycle 5/14 — les liens existent dans le modèle depuis le cycle 1 (et sont déjà migrés
depuis le format v0) mais n'ont jamais été rendus par `DiagramCanvas.vue`. Ce cycle corrige ça
et ajoute la création de lien par geste. Exclusions explicites (édition de points de routage,
nettoyage de lien orphelin) documentées dans `CONTEXT.md`. Plan en 4 tâches : `PLAN.md`.
Prochaine action : Task 1 (ancrage).

## 2026-09-04 (Task 1 — ancrage)

`web/src/diagram/anchoring.ts` : `computeAnchorPoint(bounds, towardPoint)` -- rayon
centre→cible croisant le rectangle englobant, dégénère proprement vers le centre si la cible
coïncide avec lui (évite `0 * Infinity = NaN`). 4/4 tests verts. Prochaine action : Task 2
(rendu des liens).

## 2026-09-04 (Task 2 — rendu des liens)

`DiagramCanvas.vue` : `renderedLinks` résout `fromId`/`toId` dans `props.document.elements`
complet (pas `visibleElements` culled -- un lien reste affiché même si une de ses formes est
hors-champ), applique l'override de glisser en cours (`dragPreview`) pour qu'un lien suive sa
forme pendant un déplacement (cycle 4), ignore silencieusement un lien orphelin. Tracé
`<polyline>` (ancres + `routingPoints` s'il y en a), pointillé selon `dashed`. 15/15 tests
composant verts. Prochaine action : Task 3 (création d'un lien par geste).

## 2026-09-04 (Task 3 — création d'un lien par geste)

`DiagramCanvas.vue` : `onElementMouseDown` bifurque sur `event.shiftKey` -- `startLinking()`
au lieu du déplacement du cycle 4. À la relâche, résout la forme sous le curseur
(`screenToWorld` + `pointInBounds`, aucune forme candidate exclut la forme de départ elle-
même) ; si trouvée, crée un `LinkElement` via `history.execute({type:'add-element', ...})`
(commande générique du cycle 2, réutilisée telle quelle). Sans cible valide : aucune commande,
aucun événement émis. 19/19 tests composant verts, 71/71 tests diagrammes. Prochaine action :
Task 4 (vérification finale, clôture).

## 2026-09-04 (Task 4 — vérification finale, clôture du cycle 5)

Suite frontend complète : 643/643 (11 nouveaux pour ce chantier). `npm run build` propre.
`Diagrams.vue` toujours non modifié. Rappel de passation (exclusions déjà notées dans
`CONTEXT.md`) : édition interactive des points de routage et nettoyage des liens orphelins
restent à traiter dans un futur cycle. Passation pour le cycle 6 (interactions clavier) :
sélection/déplacement/création de lien existent désormais tous à la souris -- le cycle 6 doit
leur donner un équivalent clavier (créer/naviguer/renommer/supprimer sans souris, §8.4 :
« construire une carte conceptuelle de trente nœuds sans toucher la souris »). Chantier clos
(code). Prochaine action : pousser `feature/diagrammes-liens-ancrage`, ouvrir la PR.
