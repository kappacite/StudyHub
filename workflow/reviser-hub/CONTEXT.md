# Réviser — hub global

Statut : clos
Branche : feature/reviser-hub
PR : #130 (mergée)

## Pourquoi

`RevisionSetManage.vue`, `RevisionSetStats.vue`, `RevisionBinderStats.vue` et `Reviews.vue`
(renommé Réviser en phase 3) doivent être mis à jour pour refléter les types d'éléments migrés
par le chantier `backend-ensembles-heterogenes`.

## Comment

Migration visuelle + adaptation fonctionnelle de ces 4 vues (skill `migration-ecran`), une fois
le nouveau modèle de données disponible.

## Dépendances

Dépend entièrement du chantier `backend-ensembles-heterogenes`.

## Historique complet des décisions

`ETAT.md`, section « Plan global par flux... », flux 6.
