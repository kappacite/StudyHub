# Bibliothèque — alignement de la vue liste sur `Notes.dc.html`

Statut : ouvert
Branche : feature/bibliotheque-notes-listes
PR : (aucune)

## Pourquoi

Demande explicite de l'utilisateur le 2026-09-02 : *« le canvas Notes — Listes (bascule
Notes / Révision), c'est à ça que doit ressembler la vue bibliothèque (vue des dossiers, et
des notes/révisions dans le dossier) »*, puis *« compare avec Claude in Chrome »*.

Le chantier `bibliotheque-redesign` (PR #132, clos) a traité l'**architecture** de l'écran :
suppression du `SplitView`, grille récursive de classeurs, classeur virtuel « Non classé ».
Il n'a pas retraité le **contenu et la densité des lignes** une fois *dans* un classeur, ni
la silhouette de l'en-tête. La comparaison visuelle réelle (captures maquette + app côte à
côte, thème clair, 1440px, 2026-09-02) confirme que la racine est largement conforme et que
l'écart résiduel est concentré sur la vue « dans un dossier ».

## Constat (maquette `Notes.dc.html` / `Bibliotheque.dc.html` vs code réel)

Racine (`Bibliotheque.dc.html`) — proche, 3 écarts :
- sous-titre `N classeurs · N notes · N decks` sous le H1 : absent (`PageHeader` a la prop
  `subtitle`, jamais passée) ;
- liseré gauche 4px + rayon 4px sur `BinderCard` : absents (le `highlighted` mort avait été
  retiré en revue finale de #132, l'affordance elle-même n'a jamais été rebranchée) ;
- barre `FILTRER / Tous` pleine largeur : absente de la maquette, très visible dans l'app.

Dans un classeur (`Notes.dc.html`) — écart réel :
- H1 figé sur « Bibliothèque » ; la maquette affiche « Notes » / « Révision » selon l'onglet,
  avec un sur-titre mono majuscule `BIBLIOTHÈQUE / CHIMIE ORGANIQUE` ;
- 6 boutons dans l'en-tête contre 1 seul bouton primaire dans la maquette ;
- onglets = 3 pastilles à plat au lieu d'une bascule 2 positions dans un conteneur surélevé ;
- second titre interne « Notes (5) » / « Révision (3) » que la maquette n'a pas ;
- **lignes de notes quasi vides** : titre seul. La maquette a titre + icône globe si publique
  + extrait tronqué + pastille de tag + date relative alignée à droite, séparateurs pointillés.
  Écart le plus fort de l'écran ;
- lignes d'ensemble : structure bonne (tuile, `N élément(s) · dernier passage`, mini-icônes de
  types, badge `N dues`) mais pas de bouton « Réviser » ▶, que la maquette met en premier ;
- phrase d'explication « Un classeur regroupe des ensembles de révision ; chaque ensemble
  regroupe des éléments (flashcards, QCM, vrai/faux…) » absente ;
- largeur `max-w-7xl` (1280px) contre 920px dans la maquette.

## Arbitrages retenus (défauts proposés, non contestés au moment d'ouvrir)

Trois points touchent des décisions déjà tracées ailleurs. Défauts appliqués — à inverser sur
simple demande de l'utilisateur, avant que la tâche concernée soit faite :

1. **En-tête** (affiné en brainstorming avant Task 2, 2026-09-03) : « Ajouter ▾ » reste
   visible à côté du bouton primaire — c'est de la création de contenu, pas de la gestion du
   classeur, il a déjà son propre sous-menu et l'imbriquer dans un second menu aurait été une
   mauvaise UX. Stats / Partager / Classe / Réviser ce dossier / Supprimer passent dans un
   nouveau bouton « … ». Résultat : 3 contrôles visibles (primaire, Ajouter▾, …) au lieu de 7,
   pas 1 comme la maquette au pixel près — écart assumé, aucune fonctionnalité perdue.
2. **Decks dans l'onglet Révision** : fusion **conservée**. La maquette ne montre que des
   ensembles, mais la fusion est une décision explicite et assumée du chantier
   `bibliotheque-ensembles` ; la maquette lui est antérieure. Pas de raison nouvelle de la revoir.
3. **Actions de ligne d'ensemble** : on **ajoute** le bouton ▶ Réviser en première position
   (maquette) et on replie stats / détacher / supprimer dans un menu « … » par ligne — la
   maquette n'a pas d'équivalent pour stats et détacher, qui sont des fonctionnalités réelles.

Hors périmètre, inchangé : onglet « Autres » (Diagrammes + PDF) conservé tel quel (décision
tracée par `bibliotheque-ensembles`), `PDFs.vue` / `Diagrams.vue` / `Blurting.vue` (chantier
`ecrans-peripheriques-visuels`).

## Dépendances

Aucune. `Binders.vue`, `BinderCard.vue`, `Tabs.vue`, `PageHeader.vue` sont tous sur `main`.
`Tabs.vue` et `PageHeader.vue` sont partagés — toute évolution doit rester rétro-compatible
pour leurs autres consommateurs (9 pour `PageHeader`, cf. revue finale de #132).

## Méthode de vérification

Captures réelles maquette / app côte à côte via Claude in Chrome sur l'environnement local
(backend Flask + Vite), base seedée avec le jeu de données de la maquette (classeur « Chimie
organique », 5 notes, 3 ensembles couvrant flashcard/qcm/vf/association/definition/ordre).
Script de seed : scratchpad de session, à re-créer si besoin.
