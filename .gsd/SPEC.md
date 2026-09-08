# SPEC.md — Project Specification

> **Status**: `FINALIZED`
>
> ⚠️ **Planning Lock**: No code may be written until this spec is marked `FINALIZED`.

## Vision
StudyHub est une application d'apprentissage actif tout-en-un destinée aux étudiants de l'enseignement supérieur. Elle centralise et harmonise les outils de travail intellectuel : répétition espacée (SM-2), notes Markdown/LaTeX avec auto-test inline (« Révision Active »), cartographie conceptuelle par diagrammes SVG en canevas libre, lecture et annotation de PDF, et un écosystème pédagogique complet (classes, devoirs, groupes, examens, tuteur IA via Google Gemini).

---

## Goals

1. **Répétition Espacée SM-2 Robuste** : Planification automatique d'intervalles de révision, gestion stricte des invariants (Ease Factor ≥ 1.3, multiplicateur de fine-tuning) et sessions de révision multi-formats (flashcards classiques, QCM, ensembles hétérogènes).
2. **Notes Actives & Documents Pédagogiques** : Éditeur Markdown avec KaTeX et masquage actif inline (`{{trou::reponse}}`), liseuse PDF avec isolation stricte des données privées (`user_id`).
3. **Éditeur de Diagrammes en Canevas Libre** : Outil visuel SVG natif avec panoramique infini, zoom centré, magnétisme, interactions clavier et tactiles complètes (gestes pincer/glisser, appui long), et modèle de document versionné (v1).
4. **Collaboration & Modules Pédagogiques** : Gestion des classes et devoirs côté enseignant/étudiant, espaces de groupes de travail, marketplace communautaire de fiches et ensembles de révision.
5. **Assistance & Évaluations IA** : Modules de blurting guidé, méthode Feynman, notation analytique et quiz auto-générés propulsés par l'API Google Gemini, traités via Celery/Redis avec repli synchrone transparent.
6. **Codebase Frontend Unique & Multiplateforme** : Codebase Vue 3 / Vite unique encapsulé nativement pour le Web, le Mobile (Capacitor 8) et le Bureau (Electron 33).

---

## Non-Goals (Out of Scope)

- **Mermaid comme moteur de canevas** : Mermaid.js n'est utilisé que comme format d'échange / import-export, jamais comme runtime du canevas libre.
- **Publication automatique (git push)** : Aucune commande `git push` n'est jamais exécutée de manière autonome par un agent.
- **Logique métier dans les contrôleurs** : Aucune logique métier ou requête ORM directe n'est tolérée dans les routes Flask (`api/v1/`).
- **Contournement des DAO** : Tout accès persistant passe impérativement par le pattern DAO avec filtrage systématique du `user_id`.

---

## Constraints

- **Backend** : Python 3.12+, Flask 3.0, SQLAlchemy 2.0, PostgreSQL 16 (prod) / SQLite (dev/tests), Alembic (`flask-migrate`), Pydantic v2, JWT extended, Celery 5.4 + Redis 7.
- **Frontend** : Vue 3 (Composition API `<script setup lang="ts">`), Vite 5, Tailwind CSS 3 (Design System Direction A « Fiche »), Pinia, Vue Router 4, Axios, KaTeX, Marked + DOMPurify.
- **Mobile & Bureau** : Capacitor 8 (Android/iOS), Electron 33 (Windows/macOS/Linux).
- **Discipline TDD** : Tests unitaires/intégration préalables à toute implémentation (`cycle-tdd`), aucune régression de couverture.
- **Sécurité** : Isolation étanche multi-tenant par `user_id`, Flask-Talisman (CSP), Flask-Limiter.

---

## Success Criteria

- [x] Architecture conteneurisée multi-arch vérifiée et documentée (amd64 + arm64).
- [x] Design System Direction A « Fiche » implanté avec primitives UI validées en TDD.
- [ ] Refonte complète des écrans applicatifs sur les tokens du Design System (Phase 4).
- [ ] Refonte complète de l'éditeur de diagrammes en canevas libre (Phase 5, 14 cycles).
- [ ] Résorption des constats critiques et majeurs du backlog technique (Phase 6).
