# Classes, Groupes, Devoirs, Examens, Planning — migration visuelle

Statut : planifié
Branche : (aucune)
PR : (aucune)

## Pourquoi

Écrans indépendants des flux 1-6, pure migration visuelle. `ETAT.md` signale lui-même que ces
écrans n'avaient jamais été formellement ajoutés à l'ordre des écrans de la phase 4 — lacune de
planification comblée par l'ouverture de ce chantier.

## Comment

Un cycle `migration-ecran` par vue :
- `Classes/ClassesLanding.vue` (onglets Enseignant/Élève/Groupes)
- `Classes/AssignmentDetail.vue`
- `Groups/GroupDetail.vue`
- `Exam/ExamSetup.vue`, `Exam/ExamSession.vue`, `Exam/ExamResults.vue`
- `Planning/PlanningPage.vue`

## Dépendances

Aucune sur les autres chantiers de cette liste.

## Historique complet des décisions

`ETAT.md`, section « Plan global par flux... », flux 8.
