# Journal — bibliotheque-redesign

## 2026-08-30 (planification, pas encore ouvert)

Chantier créé en `Statut : planifie` suite à une investigation en chat demandée explicitement
par l'utilisateur ("il semblerait que pour cette section aussi tu n'as pas vérifié le canvas").
Vérifié : oui pour `Binders.vue` (jamais consulté depuis sa création, commit `77ff833`,
2026-06-21) ; non pour `RevisionSetDetail.vue`/`RevisionSetModal.vue` (déjà vérifiés par
`bibliotheque-ensembles`, décisions tracées dans leur spec).

Recoupement trouvé et corrigé en cours de route : une première version de ce chantier incluait
`PDFs.vue`/`Diagrams.vue` dans son périmètre — retiré après avoir découvert que ces 2 fichiers
sont déjà explicitement dans le plan du chantier `ecrans-peripheriques-visuels` (non commencé),
qui utilise le skill `migration-ecran` (consultation de la vraie maquette déjà native à sa
procédure). L'analyse mockup-vs-code de ces 2 écrans reste dans le spec de ce chantier à titre
de contribution pour qui ouvrira `ecrans-peripheriques-visuels`, mais aucune tâche de code ne
les concerne ici.

Spec complet : `docs/superpowers/specs/2026-08-30-bibliotheque-redesign-design.md`. Plan
brouillon (pas prêt à exécuter, requiert un brainstorming préalable) :
`docs/superpowers/plans/2026-08-30-bibliotheque-redesign.md`.

Aucune implémentation lancée, conformément à la demande explicite de l'utilisateur.
