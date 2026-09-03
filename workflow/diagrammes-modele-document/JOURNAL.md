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

## 2026-09-03 (Task 1 — types du document v1)

`web/src/diagram/document.ts` : union discriminée `DiagramElement` (`shape`/`link`/`stroke`/
`occlusion-mask`, discriminant `kind`) + `DiagramDocumentV1` (`schema_version: 1`,
`elements: DiagramElement[]`, `backgroundImage: string | null`) + `createEmptyDocument()`.
Tests : fabrique produit un document vide valide ; un switch exhaustif runtime sur les 4
variantes confirme que le discriminant `kind` narrowe correctement chaque type (accès aux
champs propres à chaque variante sans cast). `npm run build` (`vue-tsc -b`) propre — le
nouveau module type-check sans erreur bien que non encore importé nulle part (attendu, il
sera branché au cycle 3). Prochaine action : Task 2 (`migrateLegacyV0ToV1`).

## 2026-09-03 (Task 2 — migration v0 → v1)

`web/src/diagram/migrations.ts` : `migrateLegacyV0ToV1()` convertit `nodes`→`ShapeElement[]`,
`connections`→`LinkElement[]`, `masks`→`OcclusionMaskElement[]`, `drawings`→`StrokeElement[]`,
`backgroundImage` inchangé. Ids migrés préfixés par catégorie (`shape-<id>`, `link-<index>`,
`mask-<id>`, `stroke-<id>`) pour garantir l'absence de collision entre catégories (id
numérique v0 vs index de connexion, notamment). Valeurs par défaut sûres pour tout champ
optionnel manquant (`arrow: 'end'`, `dashed: false`, `label: ''`, dimensions à 0). Tests :
migration complète sans perte (un élément de chaque type) ; document vide/partiel sans
erreur ; unicité des ids entre catégories ; valeurs par défaut d'une connexion minimale.
Prochaine action : Task 3 (`parseDiagramDocument`/`serializeDiagramDocument`).

## 2026-09-03 (Task 3 — parse/serialize)

`web/src/diagram/document.ts` : `parseDiagramDocument()` distingue 4 cas (chaîne vide/null/
undefined → document vide ; `schema_version === 1` → retourné tel quel ; forme legacy
reconnaissable (`nodes`/`connections`/`masks`/`drawings` présents) → délégué à
`migrateLegacyV0ToV1` ; JSON invalide ou imprévu → document vide, dégradation silencieuse
plutôt qu'exception). `serializeDiagramDocument()` : `JSON.stringify` direct. Cycle
`document.ts <-> migrations.ts` assumé (types/`createEmptyDocument` d'un côté,
`migrateLegacyV0ToV1` de l'autre) — sans effet à l'exécution ESM, tout usage est différé dans
des corps de fonction. Tests : les 4 branches + un rondtrip `parse(serialize(doc)) === doc`
sur un document v1 non trivial. Suite complète + `npm run build` (`vue-tsc -b`) propres.
Prochaine action : Task 4 (corpus de non-régression de format).
