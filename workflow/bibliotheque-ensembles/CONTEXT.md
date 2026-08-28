# Bibliothèque / classeur — ensembles hétérogènes

Statut : planifié
Branche : (aucune)
PR : (aucune)

## Pourquoi

`Binders.vue` (renommé Bibliothèque en phase 3) doit exposer la bascule Notes/Révision et la
liste des ensembles de révision hétérogènes, plus l'écran de détail d'un ensemble et ses
modales de gestion.

## Comment

- `Binders.vue` : bascule Notes/Révision, liste d'ensembles hétérogènes.
- Nouveaux composants : `RevisionSetDetail.vue`, `RevisionSetModal.vue`, `RevisionItemModal.vue`
  (6 types d'éléments : Flashcards, QCM, Vrai/Faux, Association, Définition, Ordre).

**Note de correspondance à ne pas reperdre** : l'artboard du canevas nommé `Notes.dc.html`
correspond à `web/src/views/Binders/Binders.vue`, pas à `web/src/views/Notes/Notes.vue`
(liste plate de toutes les notes, filtrable par classeur).

## Dépendances

Dépend entièrement du chantier `backend-ensembles-heterogenes` (le type d'élément doit exister
côté `RevisionItem` avant de pouvoir composer ces écrans).

## Historique complet des décisions

`ETAT.md`, section « Plan global par flux... », flux 3 et flux 4.
