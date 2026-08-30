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
`RevisionSetDetail.dc.html`, `RevisionSetModal.dc.html`, `RevisionItemModal.dc.html`,
`NoteEdit.dc.html`, `Blurting.dc.html`, `NoteQuiz.dc.html`, `NoteEvaluation.dc.html`
(deuxième passe, demande explicite de l'utilisateur de couvrir tous les écrans de la section
« Bibliothèque → Notes », pas seulement l'écran liste).

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

## Écrans d'une note (`Bibliothèque → Notes → NoteEdit` et ses outils IA)

Deuxième passe demandée explicitement par l'utilisateur ("intègre bien tous les écrans de la
partie bibliothèque - notes sur le canvas") : les 5 écrans atteints depuis une note
(`NoteEdit.vue` et ses 4 outils IA — Évaluation, Feuille blanche/Blurting, Feynman, Quiz
Auto-QCM) ont chacun leur propre maquette. État réel, écran par écran :

### `NoteEdit.dc.html` vs `NoteEdit.vue` — déjà pris en charge ailleurs, hors scope ici

Chantier dédié **déjà ouvert et bien avancé** : `editeur-notes-notation-ia`, branche
`feature/noteedit-migration` (17 commits, dont `96e068c` *« ecran 4 (editeur de notes, mode
Zen) termine »*). Son plan (`docs/superpowers/plans/2026-08-25-noteedit-migration-plan.md`)
cite explicitement `NoteEdit.dc.html` comme référence dès sa première ligne de contexte —
**consulté correctement**, contrairement à `Binders.vue`. Ne pas dupliquer ce travail.

### `NoteFeynman.dc.html` vs `NoteFeynman.vue` — déjà vérifié correct

Construit par le chantier `reviser-hub` (Task 3 de sa redesign), directement à partir de
cette maquette (chronomètre, brouillon, score de clarté, jargon, lacunes, suggestion) — déjà
comparé et validé par une revue dédiée à l'époque. Rien à refaire.

### `Blurting.dc.html` vs `Blurting.vue` — écart réel, sous-estimé par son chantier actuel

La maquette montre un écran simple : texte libre rédigé de mémoire, bouton « Analyser avec
l'IA », puis une **seule carte d'analyse** — score de clarté `/10`, tags « Jargon à
simplifier », liste « Lacunes identifiées », un paragraphe de suggestion. Rien d'autre.

`Blurting.vue` actuel est **beaucoup plus riche** que la maquette : score de « Rétention »
(concept différent du score de clarté de la maquette), un bloc « Bilan de votre tuteur »
(citation), une **cartographie des concepts du cours** (liste extensible, chaque concept avec
un statut de mémorisation — maîtrisé/incorrect/oublié — et sa propre explication), et une
**colonne entière de flashcards suggérées générées par l'IA** à partir des lacunes détectées.
Aucun de ces éléments n'existe dans `Blurting.dc.html`.

**Ce chantier n'a pas vocation à trancher ce point** (hors périmètre, `Binders.vue` uniquement)
mais le signale : `ecrans-peripheriques-visuels` prévoit pour `Blurting.vue` une *« retonation
visuelle seulement, le contenu ne change pas »* — cette décision sous-estime probablement
l'écart réel, qui est structurel (fonctionnalités entières absentes de la maquette), pas
seulement une question de tokens de couleur. À reconsidérer quand ce chantier sera ouvert
(note ajoutée à son `CONTEXT.md` dans ce même commit).

### `NoteQuiz.dc.html` vs `NoteQuiz.vue` — globalement aligné, non vérifié en profondeur

La maquette montre un flux question par question (QCM ou Vrai/Faux), barre de progression
« Question 3/8 », choix à puces lettrées. `NoteQuiz.vue` actuel suit la même logique générale
(génération d'un quiz, progression, score final en %) — pas d'écart structurel évident sur un
examen rapide, mais pas vérifié ligne à ligne (contrairement aux autres écrans de ce document).
**Non réclamé par aucun chantier existant** — orphelin, à vérifier plus précisément le jour où
quelqu'un touche ces écrans, risque jugé faible.

### `NoteEvaluation.dc.html` vs `NoteEvaluation.vue` — collision de nom, la vraie maquette n'est pas celle qu'on croit

**Constat le plus important de cette deuxième passe.** `NoteEvaluation.dc.html` ne montre pas
un quiz : c'est l'écran **« Notation de la note »** — score global sur un cercle (`8,2`),
« Points forts » / « À améliorer », section « Suggestions ». C'est exactement la fonctionnalité
« Notation » décrite dans `workflow/editeur-notes-notation-ia/CONTEXT.md` (*« un nouveau bouton
« Notation » distinct — note la qualité de la fiche sur 100, à ne pas confondre avec
l'Évaluation mixte qui note la performance de l'élève sur des exercices générés »*) —
**une fonctionnalité pas encore construite**, dont le volet backend n'a même pas de spec
détaillée écrite (`workflow/editeur-notes-notation-ia/PLAN.md`, première case non cochée).

Le fichier `NoteEvaluation.vue` qui existe aujourd'hui dans le code implémente une **fonctionnalité
différente** : des questions générées par IA que l'élève répond, avec un score de performance en
% à la fin (l'« Évaluation mixte » citée ci-dessus) — **aucune maquette du canvas ne correspond
clairement à cet écran sous ce nom**. Autrement dit : le nom "NoteEvaluation" a été réutilisé pour
une fonctionnalité existante sans jamais remarquer qu'une vraie maquette portant ce nom existait
déjà pour une fonctionnalité différente et pas encore livrée.

**Conséquence pratique** : quand `editeur-notes-notation-ia` écrira la spec détaillée de sa
fonctionnalité « Notation » (son `PLAN.md`, tâche 1 du volet backend), elle dispose déjà d'une
maquette validée pour l'écran de résultat — `NoteEvaluation.dc.html` — qu'il ne faut pas
manquer. Note ajoutée à son `CONTEXT.md` dans ce même commit pour ne pas perdre cette
information avant que ce chantier soit ouvert.

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
classeur). PDFs/Diagrams restent le territoire de `ecrans-peripheriques-visuels`, et les 5
écrans d'une note (`NoteEdit`/Blurting/NoteQuiz/NoteEvaluation/NoteFeynman) sont soit déjà
pris en charge (`editeur-notes-notation-ia`, `reviser-hub`), soit signalés dans le
`CONTEXT.md` du chantier concerné pour ne pas se perdre (Blurting → `ecrans-peripheriques-visuels`,
Notation/`NoteEvaluation.dc.html` → `editeur-notes-notation-ia`) — pas dupliqués ici, notes
ajoutées dans ce même commit.

Traiter `bibliotheque-redesign` comme `reviser-hub-redesign` : ouvrir avec
`superpowers:brainstorming` pour trancher les points ci-dessus avec l'utilisateur (arbre de
sous-dossiers, contenu non rangé, sort de l'onglet Autres), puis `superpowers:writing-plans`
pour le détail TDD tâche par tâche. Le plan `docs/superpowers/plans/2026-08-30-bibliotheque-redesign.md`
esquisse une décomposition possible mais **ne doit pas être exécuté sans ce brainstorming**.
Contrairement à `reviser-hub-redesign` (déviations presque toutes visuelles, tranchées
unilatéralement avec raisonnement écrit), l'arbre de sous-dossiers et le contenu non rangé
touchent à la navigation même de l'app — pas de simples choix de mise en page.
