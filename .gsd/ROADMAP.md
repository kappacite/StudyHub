---
milestone: v1.0
version: 1.0.0
updated: 2026-09-08
---

# Roadmap — StudyHub

> **Current Phase:** Phase 5: Refonte Éditeur de Diagrammes en Canevas Libre
> **Status:** in-progress

## Must-Haves (from SPEC)

- [x] Socle conteneurisé multi-arch (amd64 / arm64) avec migrations automatiques Alembic
- [x] Audit complet sécurité, architecture, performance et CI/CD (Phase 2)
- [x] Design System Direction A « Fiche » avec primitives UI en TDD (Phase 3)
- [ ] Refonte UI intégrale des 33 vues applicatives (Phase 4)
- [ ] Refonte complète de l'éditeur de diagrammes en canevas libre SVG (Phase 5)
- [ ] Traitement du backlog technique consolidé de 35 constats (Phase 6)

---

## Phases

### Phase 1: Outillage Agentique & Multi-Architecture
**Status:** ✅ Complete
**Objective:** Mettre en place les gardes de code, la passation de contexte, les skills spécialisés et valider l'environnement conteneurisé multi-architecture.
**Deliverables:**
- Hooks de sécurité et de conformité TDD (`phase_guard`, `tdd_guard`, `stop_gate`)
- Skills de process agentique et documentation d'architecture unifiée (`AGENTS.md`)
- Validation multi-arch Docker native (amd64 et arm64)

---

### Phase 2: Revue Technique & Audit
**Status:** ✅ Complete
**Objective:** Réaliser un audit approfondi en lecture seule sur la sécurité, l'architecture, la performance et les tests/CI.
**Deliverables:**
- `docs/audit/01-SECURITE.md` (9 constats)
- `docs/audit/02-ARCHITECTURE.md` (12 constats)
- `docs/audit/03-PERFORMANCE.md` (7 constats)
- `docs/audit/04-TESTS-CI.md` (7 constats)
- `docs/audit/05-BACKLOG.md` (35 constats priorisés)

---

### Phase 3: Design System Direction A « Fiche »
**Status:** ✅ Complete
**Objective:** Définir la charte graphique « Fiche » (papier chaud, encre indigo, rehaut ocre), implémenter les tokens Tailwind et concevoir les 10 primitives UI en TDD strict.
**Deliverables:**
- Tokens graphiques complets (`tailwind.config.js`)
- Primitives UI accessibles et testées (`BaseButton`, `BaseInput`, `BaseCard`, `BaseModal`, `BaseTabs`, `BaseBadge`, `BaseTooltip`, `BaseToast`, `BaseEmptyState`, `BaseSkeleton`)
- Page interne de démonstration `/dev/design-system`

---

### Phase 4: Refonte UI Écran par Écran
**Status:** 🔄 In Progress
**Objective:** Migrer les vues de l'application vers les tokens et primitives du Design System Direction A, écran par écran, avec respect de la responsivité (375px / 1440px) et couverture de tests.
**Deliverables:**
- [x] Écran 1 : Coquille & Navigation (`AppNav`, `AppSidebar`)
- [x] Écran 2 : Accueil / Dashboard fusionné (`Accueil.vue`)
- [x] Écran 3 : Bibliothèque & Listes de Notes (`NotesList.vue`)
- [x] Écran 4 : Éditeur de Notes Markdown/LaTeX (`NoteEdit.vue`)
- [ ] Écran 5 : Blurting IA (`Blurting.vue`)
- [ ] Écrans 6+ : Decks, Sessions SM-2, Classes, Examens, Planning, Marketplace

---

### Phase 5: Refonte Éditeur de Diagrammes en Canevas Libre
**Status:** 🔄 In Progress
**Objective:** Remplacer l'ancien éditeur SVG contraint par un canevas libre infini avec pan, zoom, sélection, magnétisme, liens magnétiques et interactions tactiles/clavier (14 cycles).
**Deliverables:**
- [x] Cycle 1 : Modèle de document v1 & sérialisation JSON (`diagrammes-modele-document`)
- [x] Cycle 2 : Commandes, exécution et pile d'annulation Undo/Redo (`diagrammes-commandes-annulation`)
- [x] Cycle 3 : Canevas infini, panoramique et zoom géométrique centré (`diagrammes-canevas-pan-zoom`)
- [x] Cycle 4 : Placement, sélection multiple et magnétisme (`diagrammes-placement-selection`)
- [x] Cycle 5 : Liens d'ancrage magnétiques et routage (`diagrammes-liens-ancrage`)
- [x] Cycle 7 : Interactions tactiles (pincer, glisser, appui long) (`diagrammes-interactions-tactiles`)
- [ ] Cycle 8 : Conteneurs, texte libre, images, LaTeX
- [ ] Cycles 9 à 14 : Alignement automatique, export/import SVG/PNG/Mermaid, intégration vue de révision

---

### Phase 6: Backlog Technique Consolidé
**Status:** ⬜ Not Started
**Objective:** Traiter les 35 constats techniques identifiés lors de l'audit de Phase 2 (sécurité, performance, découplage DAO/Service, tests CI).
**Deliverables:**
- Correction des vulnérabilités S1 (SEC-01 clé secrète, SEC-02 fuite de notes privées, PERF-05 KaTeX bloquant)
- Éradication des 13 contournements de DAO dans les services backend
- Rétablissement de la CI PostgreSQL verte
