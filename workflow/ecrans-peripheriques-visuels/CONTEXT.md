# Écrans périphériques — migration visuelle pure

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
