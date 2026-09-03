# Journal — diagrammes-modele-document

## 2026-09-03 (ouverture)

Chantier ouvert à la demande explicite de l'utilisateur (« entame le rework de l'outil de
diagramme »). Investigation a révélé que c'est la Phase 5 déjà entièrement spécifiée
(`docs/PROMPT_DEMARRAGE.md` §8), pas une retouche — signalé à l'utilisateur avant d'ouvrir
(le projet est encore en Phase 4), qui a confirmé vouloir le chantier complet Phase 5.

Ce chantier ne couvre que le premier cycle de la séquence imposée par §8.9 (« un chantier par
cycle ») : le modèle de document versionné et sa sérialisation, sans toucher à `Diagrams.vue`
ni au canevas existant. Détail complet de l'investigation, de la portée et des arbitrages de
modélisation : `CONTEXT.md`. Plan en 5 tâches TDD : `PLAN.md`. Prochaine action : Task 1
(types `DiagramDocumentV1`/`DiagramElement`).
