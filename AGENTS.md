# AGENTS.md — StudyHub : Application d'étude tout-en-un

> Ce fichier fait **autorité sur l'architecture et les décisions de conception**. En cas de
> contradiction avec un autre document (y compris `CLAUDE.md` ou un `docs/*.md`), c'est ce
> fichier qui a raison — et le document en écart doit être corrigé dans le même commit que celui
> qui l'a rendu faux.
>
> Les conventions de travail de l'agent (nommage, commits, checklist PR, interdictions
> opérationnelles) vivent dans `CLAUDE.md` et ne sont **pas** redites ici. Le détail par couche
> vit dans les skills (`.claude/skills/*/SKILL.md`) et `docs/*.md` — voir le tableau de routage
> dans `CLAUDE.md`.

---

## 1. Vue d'ensemble du projet

**StudyHub** est une application web, mobile et bureau qui centralise les outils d'un étudiant
du supérieur : flashcards (SM-2), notes Markdown/LaTeX, diagrammes, PDF annotés, classeurs,
dashboard de suivi — et un ensemble de modules pédagogiques plus larges que ce que documentait
la version précédente de ce fichier : classes et gestion enseignant, groupes d'étude, examens,
quiz, évaluations générées par IA, méthode Feynman, focus/pomodoro, planning de révision,
marketplace communautaire, notifications, recherche transverse, import Anki.

L'inventaire chiffré exact (nombre de modèles, DAO, services, blueprints, routes) est daté par
nature et n'est **pas** répété ici pour éviter qu'il ne devienne faux silencieusement — il vit
dans `docs/audit/00-CARTOGRAPHIE.md` (régénérée à chaque cartographie) et se recompte depuis le
code (`backend/app/models`, `backend/app/dao`, `backend/app/services`, `backend/app/api/v1`).

## 2. Choix technologiques

### Backend
- **Langage** : Python 3.12+ · **Framework** : Flask 3.x · **ORM** : SQLAlchemy 2.x (pattern DAO)
- **Base de données** : PostgreSQL 16 (prod) / SQLite (dev/tests)
- **Auth** : JWT via `flask-jwt-extended` · **Migrations** : Alembic via `flask-migrate`
  (auto-application versionnée au démarrage — voir skill `deployment`)
- **Validation** : Pydantic v2 · **Tests** : Pytest + pytest-flask
- **Tâches asynchrones** : Celery + Redis (évaluations/analyses IA longues) — `redis` et
  `worker` sont des services à part entière du `docker-compose.yml`, pas une brique optionnelle.
- **IA** : Gemini (blurting, génération de flashcards/quiz/évaluations, méthode Feynman)
- **Sécurité applicative** : Flask-Talisman (CSP, en-têtes), Flask-Limiter (rate limiting),
  CORS en liste blanche stricte (web + coques natives `app://-`, `capacitor://localhost`,
  `https://localhost`)

### Frontend Web
- **Framework** : Vue 3 (Composition API, `<script setup lang="ts">`) · **Build** : Vite 5
- **Style** : TailwindCSS 3 + HeadlessUI · **State** : Pinia · **Routing** : Vue Router 4
- **HTTP** : Axios (instance centralisée avec intercepteurs JWT/refresh)
- **Rendu de contenu** : `marked` + DOMPurify + highlight.js (Markdown), KaTeX (LaTeX)
- **Diagrammes** : éditeur SVG maison en glisser-déposer (pas de Mermaid.js en dépendance
  runtime) — à reconstruire en canevas libre en phase 5, voir section 9
- **PDF** : lecture intégrée sans dépendance PDF.js dans le bundle actuel
- **Tests** : Vitest + @vue/test-utils + Playwright (E2E)

### Mobile & Bureau
- **Mobile** : Capacitor **8** encapsule le build `web/` sans réécriture — un seul codebase
  `web/` produit le web ET la coque native. Projet natif généré dans `web/android` (pas de
  dossier `mobile/` à la racine). Cible iOS 16+ / Android 10+.
- **Bureau** : Electron encapsule le même build `web/`, packagé via electron-builder
  (`desktop/`), pour Windows/macOS/Linux.

```
[Bureau: Electron] ─┐
[Mobile: Capacitor] ─┴ wraps → [Web: Vue 3 + Vite] ←→ [API REST: Flask] ←→ [PostgreSQL]
                                                              ↕
                                                     [Redis + worker Celery]
```

## 3. Structure du dépôt (réelle)

```
studyhub/
├── AGENTS.md, CLAUDE.md, README.md
├── docker-compose.yml            ← un seul fichier, db+redis+backend+worker+frontend
├── deploy.sh, start.sh
├── backend/
│   ├── Dockerfile, requirements.txt, requirements-dev.txt, pyproject.toml
│   ├── migrations/versions/      ← Alembic, le head fait foi
│   ├── app/
│   │   ├── dao/                  ← accès données, filtré user_id, jamais d'import de service
│   │   ├── models/                ← entités SQLAlchemy
│   │   ├── services/              ← logique métier, DAO injecté
│   │   ├── schemas/               ← Pydantic, requête/réponse séparés
│   │   ├── middlewares/           ← JWT, rate limiting, erreurs, logging
│   │   ├── api/v1/                ← routes Flask, un blueprint par domaine, aucune logique métier
│   │   └── utils/
│   ├── tests/, scripts/, scratch/
├── web/
│   ├── Dockerfile, package.json, vite.config.ts, tailwind.config.js, capacitor.config.ts
│   ├── android/                   ← projet natif Capacitor déjà généré
│   ├── src/
│   │   ├── router/, stores/ (Pinia), services/ (Axios), composables/
│   │   ├── components/{ui,layout,notes,decks,dashboard,pdf,planning,classes}/
│   │   └── views/{Auth,Home,Dashboard,Decks,Notes,Diagrams,PDFs,Binders,Marketplace,
│   │                Classes,Groups,Exam,Focus,Planning,Reviews}/
│   ├── tests/, tests-e2e/ (Playwright)
├── desktop/                        ← coque Electron (build/, src/)
├── docs/                           ← référence par couche, voir table de routage CLAUDE.md
└── .claude/                        ← hooks, skills, agents (voir CLAUDE.md)
```

## 4. Architecture en couches

### Flux obligatoire pour tout code nouveau

```
Request → Middleware (JWT, rate limit, logging) → API (route) → Service → DAO → Model → PostgreSQL
```

- **DAO** : ne connaît que modèles SQLAlchemy + session. N'importe **jamais** un service.
- **Service** : ne connaît que DAO + schémas Pydantic. **Jamais** de requête SQL/ORM directe.
- **Route** : **aucune** logique métier. Valide (Pydantic), délègue au service, renvoie
  `jsonify` + code HTTP.
- **Middleware** : transversal, pas de logique applicative.

SOLID : un DAO = une entité ; un service = une logique métier ; DAO injecté dans le service
(jamais d'import direct) ; schémas Pydantic requête/réponse séparés. Gabarit complet de bout en
bout : skill `conventions-dao`.

### Statut réel de cette règle dans le code (constat de cartographie, pas un jugement)

La cartographie de phase 0 a détecté des court-circuits existants : accès à `db.session` hors
DAO dans une partie des routes et des services, requêtes `.query()` directes dans plusieurs
services. **La règle ci-dessus reste la cible pour tout code nouveau ou modifié** ; la remise en
conformité de l'existant est un constat de `docs/audit/02-ARCHITECTURE.md` (phase 2), pas un
chantier de la phase 1.

### Isolation des données (règle absolue)

Tout DAO qui liste des ressources filtre par `user_id`. Toute mutation vérifie l'appartenance
avant d'agir :

```python
def get_deck_or_404(self, deck_id: int, user_id: int) -> Deck:
    deck = self._deck_dao.get_by_id(deck_id)
    if not deck:
        raise ResourceNotFoundError("Deck introuvable")
    if deck.user_id != user_id:
        raise ForbiddenError("Accès interdit")
    return deck
```

Aucune ressource d'un utilisateur n'est accessible par un autre. Toutes les routes sont
protégées par JWT **sauf** `auth/*` et `health`.

### Erreurs

Format unique, handler global :

```json
{ "error": { "code": "RESOURCE_NOT_FOUND", "message": "Le deck demandé n'existe pas.", "details": {} } }
```

## 5. API REST

Préfixe `/api/v1/`, kebab-case, pagination standard (`page`, `per_page`, `sort`, `order`,
`search`). Spécification complète et à jour : `docs/api_reference.md` + skill `api-spec` —
**non redite ici** pour éviter la duplication constatée en phase 0 (ce fichier listait une
douzaine d'endpoints quand le dépôt en compte plus de deux cents répartis sur ~27 blueprints).

## 6. Déploiement

Topologie Docker, migrations et CI : skill `deployment` (référence canonique) +
`docs/migrations.md`. Ce fichier ne réplique pas le `docker-compose.yml` — la copie figée
qu'il contenait précédemment (deux fichiers dev/prod sans Redis ni Celery) ne correspondait
plus au fichier réel.

**Décision en cours (phase 1)** : l'environnement conteneurisé devient multi-architecture
(amd64/arm64 natifs, sans émulation). Voir `docs/ENVIRONNEMENT.md` une fois produit.

## 7. Discipline TDD (obligatoire à partir de la phase 3)

Le test précède l'implémentation, sans exception, à partir de la phase 3 (design system et
au-delà). Cycle, gabarits et anti-patterns interdits : skill `cycle-tdd`. Rappel des invariants
de l'algorithme SM-2 (ne pas réimplémenter sans les relire) : skill `invariants-sm2`.

## 8. Séquence de travail par phases

Ce dépôt avance par phases strictement ordonnées : 0 (reconnaissance) → 1 (outillage
agentique, en cours) → 2 (revue technique, lecture seule) → 3 (design system) → 4 (refonte UI
écran par écran) → 5 (refonte de l'éditeur de diagrammes). L'état courant, la checklist de la
phase active et le pointeur vers la phase suivante sont dans `ETAT.md` (racine, versionné) —
**c'est la source de vérité sur "où on en est"**, pas ce fichier.

Interdiction permanente, quelle que soit la phase : `git push`. Aucune commande de publication
distante n'est exécutée sans que l'utilisateur l'ait tapée lui-même.

## 9. Diagrammes — décision différée

La refonte de l'éditeur de diagrammes (canevas libre, Mermaid en format d'échange uniquement)
est **décidée mais pas encore implémentée**. Sa documentation architecturale définitive
(modèle de document versionné, raison du choix canevas-libre-vs-Mermaid-source-de-vérité)
remontera dans cette section au moment de la phase 5 — elle n'est pas anticipée ici pour éviter
de documenter une décision avant son implémentation.

---

*Toute décision d'architecture majeure doit être reflétée ici, dans le skill concerné, et dans
le `docs/*.md` correspondant — dans le même commit que le changement qui la motive.*
