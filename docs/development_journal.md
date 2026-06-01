# Journal de Développement — StudyHub

Ce document répertorie chronologiquement les travaux, correctifs, décisions d'architecture et changements apportés au projet StudyHub.

---

## [2026-06-01] Initialisation et développement complet du Backend Flask

### Ajouts et modifications

#### ⚙️ Configuration & Infrastructure
* Création du fichier [requirements.txt](file:///home/robyn/Documents/Dev/StudyHub/backend/requirements.txt) listant l'ensemble des dépendances (Flask, SQLAlchemy, Flask-JWT-Extended, Flask-Migrate, Pydantic v2, pytest).
  * *Ajustement :* Utilisation de versions flexibles pour `psycopg2-binary>=2.9.9` et `SQLAlchemy>=2.0.35` afin de garantir la compatibilité et d'éviter les erreurs de compilation avec l'interpréteur Python 3.14 installé sur l'hôte.
* Création du [Dockerfile](file:///home/robyn/Documents/Dev/StudyHub/backend/Dockerfile) multi-stage (base, development, production) conformément à [AGENTS.md](file:///home/robyn/Documents/Dev/StudyHub/AGENTS.md).
* Initialisation de la configuration Flask ([config.py](file:///home/robyn/Documents/Dev/StudyHub/backend/app/config.py)), des extensions ([extensions.py](file:///home/robyn/Documents/Dev/StudyHub/backend/app/extensions.py)) et de la factory Flask ([__init__.py](file:///home/robyn/Documents/Dev/StudyHub/backend/app/__init__.py)).
  * *Correctif :* Renommage de la variable locale de l'instance Flask `app` en `flask_app` dans la factory pour éviter que les imports de type `from app.xxx import ...` n'écrasent la variable locale par le module Python racine `app`.

#### 🗄️ Modèles de base de données (SQLAlchemy)
Création des entités SQLAlchemy dans [app/models/](file:///home/robyn/Documents/Dev/StudyHub/backend/app/models) :
* `User` : structure de compte avec mot de passe haché.
* `Binder` : dossiers récursifs permettant d'organiser le contenu d'un utilisateur.
* `Deck` & `Flashcard` : cartes mémoire configurées pour l'apprentissage par répétition espacée.
* `Note` & `Diagram` : supports d'études (textes riches et codes Mermaid.js).
* `PDFDocument` : métadonnées des documents PDF.
* `StudySession` : historique des sessions d'étude pour alimenter le Dashboard.

#### 🏗️ Couche d'accès aux données (DAO)
Création des interfaces CRUD dans [app/dao/](file:///home/robyn/Documents/Dev/StudyHub/backend/app/dao) :
* `BaseDAO` : classe générique fournissant les méthodes CRUD communes.
* `UserDAO`, `BinderDAO`, `DeckDAO`, `FlashcardDAO`, `NoteDAO`, `DiagramDAO`, `PDFDAO`, `StudySessionDAO` : spécialisations implémentant les requêtes filtrées et paginées.

#### 🛡️ Middlewares transversaux
* `auth_middleware.py` : Décorateur JWT de protection des routes et surcharge des réponses d'erreurs de token (expired, invalid, missing) pour correspondre au format normalisé.
* `error_handler.py` : Capture et traduction unifiée de toutes les exceptions (`AppError`, `PydanticValidationError`, `HTTPException`, etc.) en JSON standardisé.
* `request_logger.py` : Logger HTTP mesurant le temps de réponse de chaque endpoint.

#### 📝 Validation & Schémas (Pydantic v2)
* Implémentation des schémas Pydantic dans [app/schemas/](file:///home/robyn/Documents/Dev/StudyHub/backend/app/schemas) pour valider de façon stricte les entrées/sorties de l'API.

#### 🧠 Logique métier (Services)
Développement des services d'orchestration dans [app/services/](file:///home/robyn/Documents/Dev/StudyHub/backend/app/services) :
* `AuthService` & `UserService` : Inscription, connexion, rafraîchissement JWT et RGPD.
* `spaced_repetition.py` : Algorithme SM-2 de réévaluation des intervalles, répétitions consécutives et facteurs de facilité de révision.
* `BinderService`, `DeckService`, `FlashcardService`, `NoteService`, `DiagramService`, `PDFService`, `StatsService`.

#### 🌐 Points d'accès (API Routes v1)
* Exposition de l'ensemble des routes sous `/api/v1` : `auth`, `users`, `binders`, `decks`, `flashcards`, `notes`, `diagrams`, `pdfs`, `stats` et `health`.
* Toutes les routes sont protégées et isolées hermétiquement par `user_id`.

#### 🧪 Validation de Qualité
* Mise en place de 13 tests de couverture dans [tests/](file:///home/robyn/Documents/Dev/StudyHub/backend/tests) (`test_auth.py`, `test_binders_and_decks.py`, `test_flashcards_study.py`, `test_stats_dashboard.py`).
* Exécution réussie de pytest sous Python 3.14 (100% de succès).

### Décisions d'architecture
1. **SQLite en mode mémoire pour les tests** : Choix d'utiliser `sqlite://` en mémoire dans la configuration de test pour assurer une isolation totale entre chaque exécution et une vitesse d'exécution optimale (tests exécutés en moins de 8 secondes).
2. **Calcul du taux de rétention** : Pour correspondre aux données disponibles dans la table minimale `study_sessions`, le taux de rétention d'un deck est calculé en comparant le nombre de cartes retenues (dont la date de prochaine révision `next_review` est supérieure à l'heure courante) sur le nombre total de cartes du deck.

---
