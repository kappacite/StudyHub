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

## [2026-06-01] Initialisation et développement complet du Frontend Web

### Ajouts et modifications

#### ⚙️ Configuration & Infrastructure
* Initialisation du projet Vue.js 3 + TypeScript via Vite dans [web/](file:///home/robyn/Documents/Dev/StudyHub/web).
* Installation et configuration de TailwindCSS v3 avec le design system défini dans [AGENTS.md](file:///home/robyn/Documents/Dev/StudyHub/AGENTS.md) (couleurs personnalisées, dark mode, typographie Inter).
* Configuration du routage avec **Vue Router 4** gérant les guards d'accès authentifié.
* Intégration de **Pinia** pour la gestion de l'état (Decks, Notes, Binders, Auth).
* Simulation de l'état d'authentification asynchrone persisté dans le local storage pour découpler le frontend.

#### 🗂️ Modules applicatifs
* **Classeurs (Binders)** : Explorateur de dossiers interactif affichant récursivement les classeurs et documents associés (Notes et Decks).
* **Flashcards (Decks)** : Liste des decks de cartes mémoire et interface de révision avec animation flip 3D en pur CSS, avec intégration de l'algorithme d'apprentissage espacé **SM-2** (0 à 5).
* **Notes** : Liste et éditeur WYSIWYG supportant simultanément le Markdown (`marked.js`) et le LaTeX (`katex.js`). Ajout des **Espaces Intelligents** sous la forme d'un classeur/feuille unifié vertical (sections contextuelles en haut, liens croisés en bas). Intégration d'un système de **Définitions en Info-bulle** (tooltip) : l'utilisateur sélectionne un terme, lui associe une définition en un clic (syntaxe `[terme]{def:définition}`), et celle-ci s'affiche dans une infobulle interactive au survol en mode lecture. De plus, un **Mode Zen sans distraction** (plein écran) a été implémenté : lors de la prise de note, les barres latérale et supérieure se masquent automatiquement pour laisser place à une feuille de papier digitale épurée, et réapparaissent de manière fluide par glissement sur simple survol des bords gauche et haut de l'écran.
* **Diagrammes** : Éditeur visuel interactif en drag and drop codé en SVG (permettant de créer, nommer, colorer des formes et tracer des liaisons dynamiques à la main), doublé du mode Mermaid.js textuel.
* **PDFs** : Visualiseur de documents A4 avec simulation d'import, gestion du zoom, de la pagination, et un système d'annotations géoréférencées (X/Y) épinglées sur les pages.

#### 📄 PDF et Impression
* Intégration d'une feuille de style d'impression `@media print` masquant l'interface utilisateur pour générer un rendu PDF propre de la note via `window.print()`.

### Décisions d'architecture
1. **Rendu hybride Markdown/LaTeX/Définitions** : Remplacement temporaire des équations LaTeX et des définitions inline par des identifiants alphanumériques uniques avant la compilation Markdown afin de préserver l'intégrité du code LaTeX et du code HTML des info-bulles lors du parsing Markdown.
2. **Coordonnées relatives centrées pour le Canvas** : Stockage du centre des formes dans l'éditeur de diagrammes pour simplifier l'alignement et l'actualisation dynamique des flèches SVG lors du déplacement.
3. **Mode Zen non intrusif** : Utilisation d'interrupteurs réactifs basés sur la route active (`NoteEdit`) pour appliquer des styles de positionnement `fixed` et de masquage CSS fluide (transitions Tailwind), couplés à des zones de déclenchement invisibles (triggers de survol de 12px) aux extrémités gauche et haute du viewport pour garantir une navigation fluide sans altérer la mise en page sous-jacente.

---

## [2026-06-09] Développement de la collaboration (Partage, Marketplace) et de la révision par Feuille Blanche IA

### Ajouts et modifications

#### 🌐 Partage Public & Espace Communautaire (Marketplace)
*   **Partage Public de Notes** : Ajout d'un interrupteur de visibilité publique dans l'éditeur. Côté backend, cela génère un `share_token` unique cryptographiquement et expose une route publique accessible sans jeton JWT `/notes/public/<token>`.
*   **Consultation en Lecture Seule** : Création de la vue ([PublicNote.vue](file:///home/robyn/Documents/Dev/StudyHub/web/src/views/Notes/PublicNote.vue)) reprenant le moteur de rendu Markdown/KaTeX et un design épuré incitant à la création de compte.
*   **Espace Communautaire (Marketplace)** : Permet aux utilisateurs de publier des dossiers complets (classeurs / binders) thématiques. Les autres membres peuvent filtrer par tags ou rechercher par mot-clé, inspecter la structure à plat du classeur (titres de notes, decks) et le cloner dans leur propre espace en un clic. Le clonage (fork) incrémente le compteur `fork_count` du package original et sauvegarde une trace de l'auteur original (`original_author_id`).

#### 🧠 Révision Blurting (Feuille Blanche) Assistée par IA
*   **Intégration de Gemini** : Mise en place d'un service d'analyse IA ([ai_service.py](file:///home/robyn/Documents/Dev/StudyHub/backend/app/services/ai_service.py)) exploitant les modèles génératifs de Google Gemini pour évaluer les restitutions écrites.
*   **Vue de révision Blurting** : Création de la vue interactive ([Blurting.vue](file:///home/robyn/Documents/Dev/StudyHub/web/src/views/Notes/Blurting.vue)) avec minuteur. L'IA compare la saisie de l'étudiant avec le contenu réel de la note de cours et retourne un score de couverture, un retour personnalisé, la liste des notions clés oubliées et des flashcards sur mesure pour pallier ces lacunes.
*   **Génération de Flashcards en Lot** : Permet à l'étudiant d'enregistrer directement les flashcards suggérées par l'IA dans le deck de son choix en une seule requête `POST /blurting/create-flashcards`.

#### 🗄️ Auto-migrations de Base de Données au Lancement
*   **Gestion programmatique d'Alembic** : Ajout d'un gestionnaire de démarrage dans la factory Flask ([__init__.py](file:///home/robyn/Documents/Dev/StudyHub/backend/app/__init__.py)) qui applique automatiquement les nouvelles migrations SQL au démarrage du serveur en production ou en développement.
*   **Résolution des contraintes d'intégrité en production** : Création d'une migration intermédiaire Alembic gérant l'introduction de colonnes `NOT NULL` (comme `is_public`) sur des tables existantes en insérant des valeurs par défaut puis en appliquant la contrainte de non-nullité.
*   **Support multi-dialectes (Postgres/SQLite)** : Ajustement des scripts Alembic pour utiliser des opérations batch nommées (`fk_binders_original_author_id`) afin de supporter les contraintes complexes sous SQLite.

### Décisions d'architecture
1. **Rendu hybride KaTeX et MathJax sur notes publiques** : Conservation de l'isolation du parseur pour s'assurer que les notes publiques bénéficient de la même fidélité visuelle sans exiger de session d'authentification.
2. **Double relation User-Binder** : Création d'une clé étrangère distincte `original_author_id` sur la table des classeurs pour préserver la paternité originale d'un cours même après de multiples clones successifs.
3. **Mise à jour idempotente au démarrage** : L'auto-migration s'appuie sur le contexte applicatif et filtre les contextes CLI et tests unitaires pour éviter des conflits de verrous SQL ou des lenteurs de chargement.

## [2026-06-10] Intégration de l'édition et du rendu de blocs de code dans l'éditeur de notes

### Ajouts et modifications

#### 📝 Éditeur de notes (NoteEdit.vue)
* **Barre d'outils d'édition** : Ajout d'une nouvelle section **Code** avec deux boutons : **En Ligne** (pour formater du code inline avec `` ` ``) et **Bloc Code** (pour insérer des blocs de code avec triple-backticks ` ``` ` et retour à la ligne).
* **Menu de sélection flottant** : Ajout d'un bouton d'insertion rapide **Bloc de code** (`{ }`) à côté de l'option de code en ligne existante pour faciliter la mise en forme du texte sélectionné.
* **Support dans `applySelectionTransform`** : Gestion du type `'bloc_code'` pour entourer le texte sélectionné par des balises de code de bloc Markdown.

#### 🎨 Design & Rendu (style.css)
* **Stylisation CSS** : Ajout de styles CSS pour les blocs de code `.markdown-body pre` (background sombre adapté au mode sombre, bordure fine, padding, angles arrondis et gestion de l'overflow horizontal) et les balises `.markdown-body code` (inline, couleur indigo spécifique et arrière-plan).
* **Compatibilité** : Ces styles profitent également à la consultation publique des notes via [PublicNote.vue](file:///home/robyn/Documents/Dev/StudyHub/web/src/views/Notes/PublicNote.vue).
