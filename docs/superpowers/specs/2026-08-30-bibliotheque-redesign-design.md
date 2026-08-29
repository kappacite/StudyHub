# Constat — Bibliothèque : les vraies maquettes Direction A n'ont jamais été consultées

Date : 2026-08-30. Statut : investigation faite en chat à la demande explicite de
l'utilisateur ("il semblerait que pour cette section aussi tu n'as pas vérifié le canvas").
**Ce document ne déclenche aucune implémentation** — il sert de base à un futur chantier
(`workflow/bibliotheque-redesign/`, `Statut : planifie`).

## Méthode

Même procédure que la correction `reviser-hub` (mémoire `extract-claude-design-mockup`) :
extraction des fichiers `.dc.html` pertinents depuis l'artefact Claude Design publié
(`https://claude.ai/code/artifact/366dcc95-8da4-41dd-8bbd-1e625a68e2c5`), lecture directe,
comparaison structurelle avec le code Vue actuel. Fichiers extraits et lus en entier :
`Bibliotheque.dc.html`, `Notes.dc.html`, `PDFs.dc.html`, `Diagrams.dc.html`,
`RevisionSetDetail.dc.html`, `RevisionSetModal.dc.html`, `RevisionItemModal.dc.html`.

## Recoupement avec un chantier déjà planifié : `ecrans-peripheriques-visuels`

**Correction importante faite après une première version de ce document** : `PDFs.vue` et
`Diagrams.vue` sont déjà explicitement dans le périmètre du chantier `ecrans-peripheriques-visuels`
(`workflow/ecrans-peripheriques-visuels/PLAN.md`, non commencé) — *« Migrer PDF (`PDFs.vue`) »*
et *« Migrer Diagrammes — coquille uniquement (`Diagrams.vue`) »*. Ce chantier utilise le skill
`migration-ecran`, dont la procédure inclut déjà la consultation de la vraie maquette (mémoire
`migration-ecran-verify-mockup`). **Ce document garde l'analyse PDFs/Diagrams ci-dessous à titre
de contribution pour ce chantier existant** (éviter à qui l'ouvrira de redériver la comparaison),
mais **le chantier issu de ce spec (`bibliotheque-redesign`) ne touche PAS `PDFs.vue`/`Diagrams.vue`**
— seulement `Binders.vue`, qui n'est couvert par aucun chantier planifié existant.

## Verdict : confirmé, avec une nuance importante

Contrairement à `reviser-hub` (jamais consulté du tout), l'historique montre **deux
situations différentes selon l'écran** :

1. **`Binders.vue` (écran `Bibliothèque`, `PDFs.vue`, `Diagrams.vue`) : jamais consulté.**
   Le commit fondateur de l'architecture actuelle
   (`77ff833`, *« feat(ui): refacto UI Lot S2 (cœur) — Bibliothèque en SplitView + contenu
   typé »*, 2026-06-21) et son document `docs/ui-redesign-plan.md` ne mentionnent la
   maquette, le canvas, ou `.dc.html` **nulle part**. Aucun chantier ultérieur touchant ces
   3 fichiers ne l'a fait non plus.
2. **`RevisionSetDetail.vue`/`RevisionSetModal.vue` (chantier `bibliotheque-ensembles`,
   2026-08-28) : consulté, mais partiellement.** Le spec de ce chantier
   (`docs/superpowers/specs/2026-08-28-bibliotheque-ensembles-design.md`) cite explicitement
   `RevisionSetDetail.dc.html`, `RevisionSetModal.dc.html` et le **concept** de bascule
   Notes/Révision de `Notes.dc.html` — et documente une **décision utilisateur explicite et
   assumée** de passer de 2 onglets (maquette) à 3 (Notes/Révision/Autres, pour ne pas perdre
   Diagrammes/PDF). Ce n'est pas un oubli : c'est un écart choisi et tracé. En revanche, le
   spec ne mentionne jamais `Bibliotheque.dc.html` (l'écran de plus haut niveau, liste des
   classeurs) ni la question de savoir si l'architecture SplitView (arbre + onglets)
   elle-même correspond à une maquette — elle a été reprise telle quelle du chantier S2
   sans être requestionnée.

**Conclusion : oui, comme pour `reviser-hub`, une partie substantielle de la section
Bibliothèque n'a jamais été comparée aux vraies maquettes — mais l'ampleur et la nature de
l'écart varient par écran (détaillé ci-dessous), et une partie du travail déjà fait
(`RevisionSetDetail`/`RevisionSetModal`) n'est pas concernée.**

## Écran par écran

### `Bibliotheque.dc.html` vs `Binders.vue` (racine, aucun classeur sélectionné) — écart majeur

La maquette est une simple **grille de cartes classeur** (3 colonnes) : icône dossier,
nom, `N decks · M notes`, dernière activité, liseré de couleur, bouton « Nouveau classeur ».
Aucun arbre, aucun onglet, aucune liste de contenu — c'est un écran de sélection, point.

`Binders.vue` actuel, même à la racine (`currentBinderId === null`), affiche un `SplitView`
complet : colonne gauche = arbre des sous-dossiers, colonne droite = contenu typé
(Notes/Révision/Autres) des éléments **non rangés** (`binder_id === null`). Structure
entièrement différente — la maquette ne montre jamais de vue "racine avec contenu non
rangé", elle montre uniquement la liste des classeurs eux-mêmes.

### `Notes.dc.html` vs `Binders.vue` (à l'intérieur d'un classeur) — écart partiel, en partie assumé

La maquette montre, une fois **dans** un classeur (fil d'ariane
`BIBLIOTHÈQUE / CHIMIE ORGANIQUE`) : un simple **bascule à 2 boutons** Notes/Révision, une
**liste à une colonne** (pas de colonne latérale) — Notes : titre, extrait, badge chapitre,
date ; Révision : icône type, nom d'ensemble, `N éléments · dernier passage`, mini-icônes
des types présents, badge `N dues`, 3 boutons (réviser/éditer/supprimer). **Aucun deck
classique n'apparaît dans cette liste** — uniquement des ensembles de révision.

Le chantier `bibliotheque-ensembles` a repris le concept de bascule (→ 3 onglets, décision
tracée) mais a conservé, sans les requestionner :
- **La colonne latérale (arbre des sous-dossiers)** : absente de la maquette à tout niveau
  de navigation dans un classeur, jamais mentionnée dans le spec de ce chantier comme un
  point à vérifier.
- **La fusion visuelle Decks + Ensembles dans l'onglet Révision** : la maquette ne montre
  que des ensembles ; les decks classiques n'apparaissent nulle part dans `Notes.dc.html`.
  Décision documentée (« fusion visuelle uniquement »), mais jamais comparée à la maquette
  elle-même sur ce point précis.
- **Filtre par tags, menu « Ajouter », modale « Élément existant », partage
  communauté/classe** : aucun de ces éléments n'apparaît dans la maquette — probablement des
  fonctionnalités réelles ajoutées après la conception initiale (comme les 4 outils IA de
  `Reviser.dc.html` dans `reviser-hub`), pas nécessairement à supprimer, mais jamais
  auditées une à une pour savoir si elles doivent vivre ailleurs.

### `PDFs.dc.html` vs `PDFs.vue` — écart majeur, nature différente

La maquette montre un **lecteur PDF intégré** : panneau latéral gauche = liste des PDF du
classeur courant ; zone principale = **visionneuse de page avec surlignage et prise de note
inline**, navigation page par page. C'est un outil de lecture/annotation active.

`PDFs.vue` actuel est une **grille de cartes** (comme un mini-`Bibliotheque.dc.html`) :
import, filtre par tag, une carte par PDF avec actions modifier/supprimer — **aucune
visionneuse ni annotation intégrée**. Fonctionnellement, c'est une bibliothèque de fichiers,
pas un lecteur. Écart le plus profond des 4 écrans : il ne s'agit pas d'une différence de
disposition mais de l'absence d'une fonctionnalité entière (lecture/annotation en place).

### `Diagrams.dc.html` vs `Diagrams.vue` — écart de present­ation, fonctionnalité présente

La maquette montre une **galerie** (grille de vignettes, comme les classeurs) : miniature
du diagramme, titre, date de modification, bouton « Nouveau diagramme ». Simple écran de
sélection avant d'ouvrir un éditeur (qui n'a pas de maquette dédiée dans le canvas).

`Diagrams.vue` actuel saute directement à un **layout 2 panneaux actifs** (liste compacte à
gauche + canvas d'édition à droite, bascule Visuel/Mermaid) — jamais de vue "galerie" pure.
Contrairement à PDFs, la fonctionnalité d'édition existe bel et bien (l'éditeur n'a
simplement pas de maquette à suivre) ; l'écart porte sur l'écran d'**entrée** (galerie vs.
éditeur immédiat), pas sur une fonctionnalité manquante.

### `RevisionSetDetail.vue` / `RevisionSetModal.vue` — presumé correct, à revérifier vite

Déjà comparé et ajusté par `bibliotheque-ensembles` avec des décisions tracées
(regroupement visuel par type, pas de 3ᵉ niveau de hiérarchie). **Pas un objectif de
redesign de ce futur chantier** — seulement une vérification visuelle rapide en fin de
plan pour confirmer qu'aucune régression ne s'est glissée depuis (screens partagés avec
d'autres chantiers, ex. les icônes de type ajoutées par `reviser-hub`).

## Ce qui n'est PAS tranché ici (décisions pour le futur chantier)

- **Portée du PDF** : construire un vrai lecteur/annotateur (investissement significatif,
  fonctionnalité entièrement nouvelle) ou accepter la grille actuelle comme simplification
  assumée et mettre à jour la maquette de référence en conséquence ? C'est un choix produit,
  pas un simple alignement visuel — à trancher explicitement avec l'utilisateur avant
  d'écrire le plan détaillé (brainstorming).
- **Sort de l'arbre de sous-dossiers** : le retirer pour coller à la maquette (impact : plus
  aucune navigation visuelle dans une hiérarchie de classeurs imbriqués, à remplacer par
  quoi ?) ou le garder comme fonctionnalité réelle ajoutée après coup (comme les liens
  « Mes decks »/« Examen blanc » conservés dans `reviser-hub`) ?
- **Sort du contenu "non rangé" à la racine** : la maquette ne montre jamais cet état ; il
  faut décider où il vit si la racine devient une simple grille de classeurs.
- **Onglet "Autres" (Diagrammes+PDF)** : décision déjà tracée et assumée par
  `bibliotheque-ensembles` — a priori à conserver telle quelle, sauf si le futur chantier
  trouve une meilleure option compatible avec la grille/galerie des maquettes respectives.

## Recommandation (pour amorcer le brainstorming du futur chantier)

**Périmètre de `bibliotheque-redesign` : `Binders.vue` uniquement** (racine + contenu d'un
classeur). PDFs/Diagrams restent le territoire de `ecrans-peripheriques-visuels`, qui a
déjà tout ce qu'il faut ci-dessus pour ne pas répéter l'erreur de `reviser-hub` quand il sera
ouvert (à condition de le rappeler explicitement dans son propre `CONTEXT.md` — fait dans ce
commit).

Traiter `bibliotheque-redesign` comme `reviser-hub-redesign` : ouvrir avec
`superpowers:brainstorming` pour trancher les points ci-dessus avec l'utilisateur (arbre de
sous-dossiers, contenu non rangé, sort de l'onglet Autres), puis `superpowers:writing-plans`
pour le détail TDD tâche par tâche. Le plan `docs/superpowers/plans/2026-08-30-bibliotheque-redesign.md`
esquisse une décomposition possible mais **ne doit pas être exécuté sans ce brainstorming**.
Contrairement à `reviser-hub-redesign` (déviations presque toutes visuelles, tranchées
unilatéralement avec raisonnement écrit), l'arbre de sous-dossiers et le contenu non rangé
touchent à la navigation même de l'app — pas de simples choix de mise en page.
