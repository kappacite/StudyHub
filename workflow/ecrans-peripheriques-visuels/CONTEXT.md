# Écrans périphériques — migration visuelle pure

Statut : planifié
Branche : (aucune)
PR : (aucune)

## Pourquoi

Écrans 5 à 9 de l'ordre historique de la phase 4, indépendants des flux 1-6 (aucun changement
de schéma de données) : pure migration visuelle vers le design system.

## Comment

Un cycle `migration-ecran` par vue, dans n'importe quel ordre (peuvent avancer en parallèle) :
- Blurting (`Blurting.vue`) — retonation visuelle seulement, le contenu ne change pas au-delà
  de la Tâche 5 du chantier `editeur-notes-notation-ia` (méthode Feynman)
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
