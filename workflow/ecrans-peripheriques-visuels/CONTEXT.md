# Écrans périphériques — migration visuelle pure

Statut : planifié
Branche : (aucune)
PR : (aucune)

## Pourquoi

Écrans 5 à 9 de l'ordre historique de la phase 4, indépendants des flux 1-6 (aucun changement
de schéma de données) : pure migration visuelle vers le design system.

## Comment

Un cycle `migration-ecran` par vue, dans n'importe quel ordre (peuvent avancer en parallèle) :
- PDF (`PDFs.vue`, lecture/annotations)
- Diagrammes — coquille uniquement (`Diagrams.vue`), pas le canevas/moteur (hors périmètre
  phase 4, prévu phase 5)
- Marketplace (`Marketplace/Home.vue`, `Explore.vue`, `PackagePreview.vue`,
  `Notes/PublicNote.vue`)
- Auth (`Auth/Login.vue`, `Auth/Register.vue`) — aucune route Réglages/Profil n'existe,
  confirmé en phase 3, ne pas en inventer une

## Dépendances

Aucune sur les autres chantiers de cette liste, sauf Blurting qui doit suivre la Tâche 5 du
chantier `editeur-notes-notation-ia` (méthode Feynman).

## Historique complet des décisions

`ETAT.md`, section « Plan global par flux... », flux 7 ; ordre des écrans historique de la
phase 4 (section « Ordre des écrans »).

## Note ajoutée le 2026-08-30 (chantier `bibliotheque-redesign`)

Investigation faite pour un autre chantier (`bibliotheque-redesign`,
`docs/superpowers/specs/2026-08-30-bibliotheque-redesign-design.md`) a confirmé, en comparant
directement aux vraies maquettes Direction A, que `PDFs.vue` et `Diagrams.vue` divergent
fortement de leurs maquettes respectives :
- `PDFs.dc.html` montre un **lecteur/annotateur intégré** (surlignage, note ancrée, navigation
  page par page) — `PDFs.vue` actuel est une simple grille de fichiers (import/liste/tags),
  aucune lecture ni annotation en place. Écart de fonctionnalité, pas seulement de mise en
  page — à trancher avant d'exécuter la tâche « Migrer PDF » ci-dessus : vrai lecteur (coût
  réel) ou grille actuelle acceptée comme simplification assumée.
- `Diagrams.dc.html` montre une **galerie** (grille de vignettes) comme écran d'entrée, avant
  d'ouvrir un éditeur — cohérent avec le « coquille uniquement » déjà noté ci-dessus : ajouter
  cette vue galerie en amont de l'éditeur existant (qui n'a pas de maquette propre) satisferait
  la maquette sans toucher au canevas/moteur.

Utiliser ces deux constats au moment d'ouvrir ce chantier plutôt que de redériver la
comparaison — les fichiers `.dc.html` sont ré-extractibles via la procédure de la mémoire
`extract-claude-design-mockup` si besoin de les revoir en détail.

## Note ajoutée le 2026-09-03 (retrait de Blurting du périmètre)

Blurting (`Blurting.vue`) retiré de ce chantier — son écart réel avec le canevas (cf. note
ci-dessous du 2026-08-30) s'est avéré bien plus large qu'une retonation (génération/import de
flashcards à conserver, structure à recomposer) et a été traité comme sa propre tâche dans le
chantier `notes-ia-planning-corrections` (2026-09-03), avec Notation IA et Feynman. Ne pas
retraiter Blurting ici.

## Note ajoutée le 2026-08-30 (deuxième passe, écrans de note)

Deux constats supplémentaires, mêmes investigation et spec que ci-dessus :

1. **La dépendance « Blurting doit suivre la Tâche 5 de `editeur-notes-notation-ia` (méthode
   Feynman) » est déjà levée** : cette tâche (extraire `NoteFeynman.vue`) a été livrée entre
   temps par un chantier différent (`reviser-hub`, Task 3 de sa redesign), pas par
   `editeur-notes-notation-ia`. `NoteFeynman.vue` existe déjà dans `main`, vérifié conforme à
   `NoteFeynman.dc.html`. Rien n'empêche donc plus de commencer Blurting dès que ce chantier
   sera ouvert.
2. **« Retonation visuelle seulement, le contenu ne change pas » sous-estime probablement
   l'écart réel sur Blurting.** Comparé directement à `Blurting.dc.html` (texte libre + bouton
   « Analyser avec l'IA » + une seule carte d'analyse : score de clarté /10, jargon, lacunes,
   suggestion), `Blurting.vue` actuel a une structure bien plus riche et différente : score de
   « Rétention » (pas le même concept que la clarté de la maquette), un bloc « Bilan de votre
   tuteur », une cartographie des concepts du cours avec statut de mémorisation par concept, et
   une colonne entière de flashcards suggérées par l'IA — rien de tout ça n'existe dans la
   maquette. Ce n'est pas qu'une question de tokens de couleur (retonation) : c'est un écart de
   structure et de fonctionnalités. À reconsidérer au moment d'écrire le plan détaillé de ce
   chantier — potentiellement un vrai brainstorming comme pour `bibliotheque-redesign`, pas un
   simple cycle `migration-ecran` de retonation.
