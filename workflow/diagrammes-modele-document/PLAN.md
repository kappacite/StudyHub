# Plan — diagrammes-modele-document (Phase 5, cycle 1)

Une case = une tâche atomique. TDD (skill `cycle-tdd`) : le test précède le code, sans
exception (§8.7 de `docs/PROMPT_DEMARRAGE.md` — terrain le plus favorable au TDD du projet).
Détail de l'approche et des arbitrages : `CONTEXT.md`.

Aucun changement à `Diagrams.vue` dans ce cycle : le modèle vit en isolation
(`web/src/diagram/`), non encore branché sur l'éditeur existant. Le branchement réel se fera
au cycle 3 (canevas) quand il y aura quelque chose à rendre avec.

- [x] Task 1 — Types `DiagramDocumentV1`/`DiagramElement` (union discriminée `kind` : shape/
  link/stroke/occlusion-mask) dans `web/src/diagram/document.ts`, plus une fabrique
  `createEmptyDocument(): DiagramDocumentV1`. Tests : la fabrique produit un document valide
  (`schema_version: 1`, `elements: []`, `backgroundImage: null`) ; TypeScript seul ne suffit
  pas de test runtime pour de purs types, le test porte sur la fabrique et sur un exemple de
  chaque variante de `DiagramElement` construit à la main (vérifie que le discriminant `kind`
  distingue bien les variantes à la compilation ET runtime, ex. `switch` exhaustif).
- [x] Task 2 — `migrateLegacyV0ToV1(raw: unknown): DiagramDocumentV1` dans
  `web/src/diagram/migrations.ts`. Convertit le JSON ad hoc actuel (`nodes`/`connections`/
  `masks`/`backgroundImage`/`drawings`, cf. `CONTEXT.md`) vers `DiagramDocumentV1`, sans perte.
  Tests : un document v0 avec au moins un élément de chaque type (node, connection, mask,
  drawing, backgroundImage renseigné) migre en préservant toutes les valeurs (id, position,
  libellé, couleur, etc.) ; un document v0 vide/partiel (champs manquants, ex. pas de
  `drawings`) migre sans erreur vers des tableaux vides ; un id de nœud numérique (v0) devient
  un id stable (string) sans collision entre types (un node id=1 et une connection ne doivent
  jamais produire le même id final).
- [x] Task 3 — `parseDiagramDocument(raw: string | null | undefined): DiagramDocumentV1` et
  `serializeDiagramDocument(doc: DiagramDocumentV1): string` dans `web/src/diagram/document.ts`.
  `parseDiagramDocument` distingue : chaîne vide/`null`/`undefined` → document vide (fabrique
  Task 1) ; JSON avec `schema_version: 1` → validé et retourné tel quel ; JSON sans
  `schema_version` mais avec la forme v0 reconnaissable → délègue à `migrateLegacyV0ToV1` ;
  JSON invalide/imprévu → document vide (dégradation silencieuse, cohérent avec le
  comportement actuel de `Diagrams.vue` face à du JSON cassé) plutôt qu'une exception qui
  casserait l'ouverture de l'écran. Tests couvrant les 4 branches, plus un test de rondtrip
  (`parseDiagramDocument(serializeDiagramDocument(doc))` égale `doc` structurellement pour un
  document v1 non trivial).
- [ ] Task 4 — Corpus de non-régression de format (§8.8/§8.7 : « un corpus de documents
  sérialisés de chaque version doit continuer à s'ouvrir, un test par version de schéma »).
  Fixtures JSON dans `web/tests/diagram/fixtures/` : au moins 3 documents v0 réalistes
  (extraits/inspirés de vrais usages — un schéma nœuds+liens simple, un schéma avec occlusion
  d'image type anatomie, un schéma avec traits à main levée) commités tels quels. Test dédié
  qui charge chaque fixture, la fait passer par `parseDiagramDocument`, et vérifie qu'elle
  produit un `DiagramDocumentV1` valide sans exception. Ce test ne doit **jamais** être modifié
  pour supprimer une fixture existante — seulement en ajouter à mesure que de nouvelles
  versions de schéma apparaissent dans les cycles suivants (règle documentée en tête du fichier
  de test).
- [ ] Task 5 — Vérification finale : suite frontend complète verte, `npm run build` propre,
  aucune régression sur `Diagrams.vue` (le fichier n'est pas modifié par ce cycle — un `git
  diff` de contrôle confirme qu'aucune ligne n'y a changé). Clôture du chantier ; note de
  passation dans `JOURNAL.md` pour le prochain cycle (« commandes et annulation ») : le modèle
  `DiagramDocumentV1` et ses fonctions (`createEmptyDocument`, `parseDiagramDocument`,
  `serializeDiagramDocument`, `migrateLegacyV0ToV1`) sont le socle sur lequel les commandes
  d'édition s'appuieront (chaque commande transforme un `DiagramDocumentV1` en un autre,
  jamais de mutation en place — condition posée par l'invariant d'annulation testé par
  propriété du cycle 2).
