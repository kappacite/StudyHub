---
phase: 5
plan: 1
wave: 1
gap_closure: false
depends_on: []
---

# Plan 5.1: Cycle 7 - Interactions tactiles (Appui long et Création de liens)

## Objective
Ce plan vise à finaliser le Cycle 7 (Interactions tactiles) de la refonte de l'éditeur de diagrammes. L'objectif est d'implémenter l'appui long (500ms) sur un élément pour activer le mode création de lien tactile, et de gérer le glisser pour tracer ce lien, tout en s'assurant que la suite de tests (actuellement >508 tests) reste verte.

## Context
Load these files for context:
- .gsd/SPEC.md
- .gsd/phases/5/RESEARCH.md
- web/src/diagram/DiagramCanvas.vue
- web/tests/diagram/DiagramCanvas.spec.ts

## Tasks

<task type="auto">
  <name>TDD: Implémentation du timer d'appui long pour la création de lien</name>
  <files>
    web/src/diagram/DiagramCanvas.vue
    web/tests/diagram/DiagramCanvas.spec.ts
  </files>
  <action>
    Ajouter la logique de détection de l'appui long (500ms) sur un élément SVG en tactile.
    
    Steps:
    1. Dans `DiagramCanvas.spec.ts`, ajouter un test (en utilisant `vi.useFakeTimers()`) qui simule un `touchstart` sur un élément et vérifie qu'après 500ms, l'état interne passe en mode création de lien (ex: `isCreatingLink` = true, `linkStartElement` défini). Si le doigt bouge (touchmove) avant 500ms ou est relâché (touchend), le timer doit être annulé.
    2. Dans `DiagramCanvas.vue`, instancier un `setTimeout` lors d'un `touchstart` sur une forme (si 1 seul doigt). 
    3. Gérer le `touchmove` et `touchend` pour annuler (`clearTimeout`) cet appui long si l'utilisateur bouge pour faire un simple glisser (pan/move) ou relâche trop tôt.
    
    AVOID: L'utilisation de variables globales. L'état doit être encapsulé dans la vue (refs).
    USE: `vi.useFakeTimers()` et `vi.advanceTimersByTime(500)` pour tester la temporisation.
  </action>
  <verify>
    cd web && npm run test -- DiagramCanvas.spec.ts
  </verify>
  <done>
    Les tests TDD passent : l'état bascule bien en mode création de lien après 500ms sans mouvement, et le timer est bien annulé en cas de déplacement.
  </done>
</task>

<task type="auto">
  <name>Implémentation du tracé de lien en tactile</name>
  <files>
    web/src/diagram/DiagramCanvas.vue
    web/tests/diagram/DiagramCanvas.spec.ts
  </files>
  <action>
    Permettre de tracer la ligne (fantôme) de création de lien suite à l'appui long, puis de finaliser la création du lien au relâchement.
    
    Steps:
    1. Ajouter un test Vitest vérifiant que lors d'un `touchmove` *après* avoir déclenché l'appui long, la position du curseur de lien est mise à jour (via `screenToWorld`).
    2. Ajouter un test Vitest vérifiant que lors du `touchend` sur une autre forme, une commande d'ajout de lien est émise.
    3. Dans `DiagramCanvas.vue`, modifier le gestionnaire `touchmove` pour que, si l'on est en mode création de lien (suite à l'appui long), on mette à jour la position cible du lien plutôt que de déplacer l'élément.
    4. Modifier le `touchend` pour finaliser la création du lien avec magnétisme si relâché sur une cible, ou l'annuler sinon.
  </action>
  <verify>
    cd web && npm run test -- DiagramCanvas.spec.ts
  </verify>
  <done>
    Les tests TDD passent. Un lien peut être créé en tactile en maintenant le doigt 500ms puis en glissant vers une autre forme.
  </done>
</task>

## Must-Haves
After all tasks complete, verify:
- [ ] L'appui long de 500ms déclenche la création de lien (équivalent de Maj+Drag).
- [ ] Le glisser tactile trace le lien.
- [ ] Le relâchement sur une forme crée le lien.

## Success Criteria
- [ ] All tasks verified passing
- [ ] Must-haves confirmed
- [ ] No regressions in tests (npm run test complet dans `web`)
