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

## [2026-06-14] Rework Espace Professeur — PR 5 : gestion de classe

Cinquième et dernière étape : outiller le professeur pour piloter sa classe.

### Ajouts et modifications

#### 👥 Gestion (class_management_service.py)
* **`get_roster`** : trombinoscope agrégé (rôle, date d'inscription, devoirs complétés, dernière activité) — requêtes bornées, professeurs en tête.
* **`regenerate_invite`** : nouveau code d'invitation (invalide l'ancien).
* **`distribute_binder`** : clone un classeur dans le compte de **chaque élève** (réutilise `CommunityService.clone_package` pour le clone profond notes/decks/cartes/tags), partage d'abord le classeur à la classe si besoin, et notifie les élèves. Résilient (échecs comptés, pas bloquants).

#### 🌐 API (classes.py)
* `GET /classes/:id/members`, `POST /classes/:id/invite/regenerate`, `POST /classes/:id/distribute`.
* Le **retrait de membre** et le **changement de rôle** réutilisent les endpoints groupes existants (les classes sont des groupes).

#### 🖥️ Frontend
* `TeacherDashboard` : onglet **Élèves** (roster + retrait), bouton de **régénération** du code d'invitation, et action **Distribuer** par classeur (onglet Cours & Classeurs).

#### 🧪 Tests
* `test_class_management.py` : roster (+ interdiction élève), régénération (ancien code invalidé, interdiction élève), distribution (copie clonée chez l'élève + notification), interdictions (élève → 403, classeur d'autrui → 404).

### Décisions d'architecture
1. **Réutilisation maximale** : on s'appuie sur la gestion de membres des groupes et sur le clone profond de la marketplace plutôt que de dupliquer la logique.
2. **Distribution = copie personnelle** (fork), distincte du partage en lecture : chaque élève reçoit un classeur modifiable dans son espace.

---

### 🎓 Bilan du rework Espace Professeur (PR 1 → 5)

La feature professeur est passée d'un système « un devoir = un classeur de flashcards » à une plateforme de cours complète : **devoirs multi-activités** (flashcards, QCM, examens, blurting, lecture) avec objectifs et soumission, **tableau de bord analytique** (complétion, scores, lacunes IA), **notation**, **engagement** (annonces, classement, badges, notifications) et **gestion de classe** (roster, invitations, distribution de cours). 5 migrations additives et rétro-compatibles, ~30 endpoints, couverture de tests étendue (backend + frontend).

## [2026-06-14] Rework Espace Professeur — PR 4 : engagement de classe

Quatrième étape : rendre la classe vivante et motivante.

### Ajouts et modifications

#### 🗣️ Annonces & fil (engagement_service.py)
* `post_announcement` : enregistre une annonce dans `GroupActivity` (type `announcement`) et notifie les élèves ; `get_feed` agrège annonces + activités (noms résolus en une requête).

#### 🏆 Classement & badges
* `get_leaderboard` (opt-in via `groups.leaderboard_enabled`) : par élève — devoirs complétés, score moyen, **streak** (jours consécutifs, calculé en une requête), **badges** (« Premier rendu », « Travailleur assidu », « Série de N jours », « Excellence ») et points. Tri par points.

#### 🔔 Notifications in-app
* Nouveau modèle **`Notification`** + blueprint `/api/v1/notifications` (liste, compteur non lues, marquer lue, tout marquer). Générées à la création d'un devoir et à la publication d'une annonce.

#### 🧱 Migration
* `d9a4c5e6b7f8` : table `notifications` + `groups.leaderboard_enabled`.

#### 🖥️ Frontend
* **`NotificationBell.vue`** (cloche dans le header global) + store Pinia `notifications` + `notificationService` : badge de non lues, dropdown, marquage lu, sondage léger du compteur.
* `TeacherDashboard` : bouton **Annoncer** (modale) + **classement** dans l'onglet Tableau de bord.
* **`useClassNotifications.ts`** : rappels **locaux** de deadline (J‑1) programmés côté client sur mobile (`@capacitor/local-notifications`), no-op sur le web.

#### 🧪 Tests
* Backend `test_engagement.py` : annonce → fil + notification, nouveau devoir → notification, marquage lu, classement (actif/désactivé), **isolation** des notifications entre élèves.
* Frontend `notifications.spec.ts` : store (fetch, markRead, markAllRead).

### Décisions d'architecture
1. **Pas d'infra de push serveur** : notifications in-app persistées + rappels locaux mobiles côté client ; aucune dépendance FCM/APNs.
2. **Réutilisation de `GroupActivity`** pour les annonces (pas de nouveau modèle pour le fil).

## [2026-06-14] Rework Espace Professeur — PR 3 : analytics, lacunes IA & notation

Troisième étape : donner au professeur de la visibilité et une boucle de feedback.

### Ajouts et modifications

#### 📊 Analytics (analytics_service.py)
* **`get_class_overview`** : vue d'ensemble agrégée (nb élèves, devoirs, taux de complétion, score moyen, élèves actifs 7j, complétion par devoir) — **entièrement en requêtes ensemblistes bornées** pour éliminer le N+1 de l'ancien `get_class_materials_progress`.
* **`compute_weak_topics`** : classe les notes par taux d'erreur à partir des `EvaluationItem` ratés des élèves (data-driven, sans IA).

#### 🧠 Lacunes IA (Celery)
* **`AIService.summarize_class_gaps`** : résumé pédagogique en langage naturel (Gemini), best-effort — renvoie `None` sans clé/sur erreur (jamais bloquant).
* **Tâche `run_class_gap_analysis`** : agrège les lacunes + résumé (IA ou heuristique) et met en cache dans la nouvelle table **`class_insights`**. Dispatch via `dispatch_or_run` (repli synchrone).

#### ✍️ Notation
* Champs `teacher_score` / `teacher_feedback` / `graded_by` / `graded_at` sur `assignment_progress` (migration `c8e2b3d4f6a7`). `ClassService.grade_submission` + endpoint `PATCH /classes/:id/assignments/:aid/submissions/:student_id`.

#### 🌐 API (classes.py)
* `GET /classes/:id/analytics`, `GET`/`POST /classes/:id/insights`, `PATCH …/submissions/:student_id`.

#### 🖥️ Frontend
* `TeacherDashboard` : nouvel onglet **« Tableau de bord »** (KPI, complétion par devoir, panneau « Lacunes de la classe » avec bouton d'analyse IA).
* `AssignmentDetail` : colonne **Note (prof)** éditable (score + commentaire) par élève.

#### 🧪 Tests
* `test_teacher_analytics.py` : vue d'ensemble + accès réservé, notation (+ interdiction élève), lacunes (POST recalcule, GET renvoie le cache + résumé heuristique), et **budget de requêtes borné** (`assert_max_queries`, invariant au nombre d'élèves/devoirs).

### Décisions d'architecture
1. **Lacunes data-driven d'abord, IA en enrichissement** : le classement des notions ratées est déterministe et testable hors-ligne ; l'IA ne fait qu'ajouter un résumé, et son absence n'empêche jamais l'analyse.
2. **Cache `class_insights`** : on conserve la dernière analyse pour éviter de rappeler l'IA à chaque ouverture du tableau de bord.

## [2026-06-14] Rework Espace Professeur — PR 2 : devoirs riches multi-supports + UX

Deuxième étape : on branche la fondation de la PR 1 sur l'expérience réelle. Un devoir peut désormais combiner plusieurs activités de types variés, et l'élève les lance directement depuis ses devoirs.

### Ajouts et modifications

#### 🧠 Backend — Service & complétion (class_service.py)
* **Création multi-tâches** : `create_assignment` accepte une liste `tasks` (chaque tâche = `task_type` + `ref` cible + `goal` optionnel) ; la voie historique `binder_id` reste supportée (synthétise une tâche `flashcards`).
* **Résolution des cibles** : `_resolve_task_target` mappe chaque type vers un classeur (flashcards/exam) ou une note (quiz/blurting/read), avec vérification d'appartenance au professeur.
* **Recalcul de progression par type** : `recompute_task_for_user` dérive l'état de chaque tâche — flashcards depuis les `StudySession` du classeur (avec seuils `min_cards`/`min_score`), quiz/exam/blurting depuis la complétion du module sous-jacent (`Quiz`/`ExamSession`/`Evaluation`), `read` par validation manuelle. `recompute_assignment_for_user` recompose l'agrégat (soumission). Le hook flashcards (`trigger_assignment_progress_update`) cible désormais les tâches via `AssignmentTask`.
* **Soumission** : `submit_task` (élève) recalcule depuis le module et marque les lectures comme faites.

#### 🗄️ DAO
* `quiz_dao` / `exam_dao` / `evaluation_dao` : ajout de `get_best_completed_for_note` / `get_best_completed_for_binder` (meilleur score complété).

#### 🌐 API (classes.py)
* Nouvel endpoint `POST /classes/:id/assignments/:assignment_id/tasks/:task_id/submit`.

#### 🖥️ Frontend
* **`AssignmentBuilder.vue`** (nouveau) : modale de composition d'un devoir multi-tâches (ajout/retrait d'activités, choix du type et de la cible, objectifs flashcards). Intégrée au `TeacherDashboard`.
* **`StudentClassView.vue`** : chaque devoir affiche ses tâches avec un CTA de lancement dédié (Réviser / Passer le QCM / Examen / Blurting / Ouvrir) et un bouton de validation ; statut par tâche + agrégat.
* **`assignmentTasks.ts`** : util pur `taskLaunchRoute` centralisant le routage des tâches (testé unitairement).

#### 🧪 Tests
* Backend `test_rich_assignments.py` : création multi-tâches, vue élève, soumission lecture, complétion quiz dérivée du module, validation (devoir sans cible → 400), isolation (cible d'un autre utilisateur → 404).
* Frontend `assignmentTasks.spec.ts` : mapping des routes de lancement.

### Décisions d'architecture
1. **DAOs additionnels créés à la volée** : `ClassService` instancie les DAOs note/assignment/quiz/exam/evaluation depuis la session si non injectés, pour ne pas modifier les appelants existants (focus_service, routes).
2. **Complétion dérivée, pas saisie** : les scores de quiz/exam/blurting proviennent des modules existants (source unique de vérité) ; l'élève « soumet » pour rafraîchir, il ne saisit jamais un score.

## [2026-06-14] Rework Espace Professeur — PR 1 : fondation « devoirs multi-tâches »

Première étape du rework de la feature professeur (les 4 axes : devoirs riches, suivi/feedback, engagement, gestion de classe). Cette PR est **purement additive et rétro-compatible** : aucun changement d'UX ni d'API, on pose les fondations de données.

### Ajouts et modifications

#### 🗄️ Modèles (app/models/assignment.py)
* **`AssignmentTask`** : tâche polymorphe d'un devoir (`task_type` ∈ flashcards | quiz | exam | blurting | read). Référence polymorphe vers la cible via `ref_id` (PK interne), `ref_uuid` (UUID public si applicable) et `ref_label` (nom dénormalisé pour l'affichage sans jointure). Objectif configurable via `goal` (JSON, ex. `{"min_cards": 20, "min_score": 80}`).
* **`AssignmentTaskProgress`** : progression d'un élève par tâche (`status`, `score_pct`, `attempts`, `submitted_at`, `completed_at`, `payload`).
* **`Assignment` étendu** : `instructions`, `publish_at` (publication programmée), `allow_late` ; `binder_id` devient **nullable** (un devoir peut n'avoir que des tâches typées). Les colonnes historiques de `AssignmentProgress` (agrégat = « soumission ») sont conservées pour la rétro-compatibilité du flux mono-classeur.

#### 🏗️ DAO (app/dao/assignment_dao.py)
* Nouveau **`AssignmentDAO`** centralisant tous les accès SQL aux tables de devoirs — qui étaient auparavant inline dans `ClassService`, en violation de la séparation des couches. Méthodes CRUD pour assignments, tâches, progression par tâche et agrégat de soumission.

#### 🧱 Migration (b7d1a2c3e4f5_add_assignment_tasks)
* Étend `assignments`, crée `assignment_tasks` et `assignment_task_progress`, et **backfill** : chaque devoir mono-classeur existant est converti en une tâche `flashcards` ciblant son `binder_id`. Idempotente (gardes via inspector) et multi-dialecte (batch nommé pour SQLite).

#### 🧪 Tests (tests/test_assignment_tasks.py)
* Migration : création des tables/colonnes + backfill d'un devoir legacy → tâche flashcards. Round-trip complet de `AssignmentDAO`.
* *Découverte au passage* : `DevelopmentConfig.SQLALCHEMY_DATABASE_URI` est figé à l'import (attribut de classe), donc un override de config/env après `create_app` ne ré-isole pas la base. Les tests de migration patchent désormais l'attribut de classe avant `create_app` pour une base SQLite jetable réellement isolée.

### Décisions d'architecture
1. **Référence polymorphe sans FK** : `AssignmentTask.ref_id` ne porte pas de contrainte de clé étrangère (la cible appartient à plusieurs tables) ; la cohérence est garantie par la couche service, et `ref_uuid`/`ref_label` évitent les jointures à l'affichage.
2. **Pas de renommage de table** : `assignment_progress` reste l'agrégat « soumission » (renommé seulement sémantiquement) pour ne pas casser le flux existant ; la refonte recalculera cet agrégat à partir des `AssignmentTaskProgress`.

## [2026-06-10] Intégration de l'édition et du rendu de blocs de code dans l'éditeur de notes

### Ajouts et modifications

#### 📝 Éditeur de notes (NoteEdit.vue)
* **Barre d'outils d'édition** : Ajout d'une nouvelle section **Code** avec deux boutons : **En Ligne** (pour formater du code inline avec `` ` ``) et **Bloc Code** (pour insérer des blocs de code avec triple-backticks ` ``` ` et retour à la ligne).
* **Menu de sélection flottant** : Ajout d'un bouton d'insertion rapide **Bloc de code** (`{ }`) à côté de l'option de code en ligne existante pour faciliter la mise en forme du texte sélectionné.
* **Support dans `applySelectionTransform`** : Gestion du type `'bloc_code'` pour entourer le texte sélectionné par des balises de code de bloc Markdown.

#### 🎨 Design & Rendu (style.css)
* **Stylisation CSS** : Ajout de styles CSS pour les blocs de code `.markdown-body pre` (background sombre adapté au mode sombre, bordure fine, padding, angles arrondis et gestion de l'overflow horizontal) et les balises `.markdown-body code` (inline, couleur indigo spécifique et arrière-plan).
* **Compatibilité** : Ces styles profitent également à la consultation publique des notes via [PublicNote.vue](file:///home/robyn/Documents/Dev/StudyHub/web/src/views/Notes/PublicNote.vue).

* **Coloration Syntaxique (Highlight.js)** : Intégration de la bibliothèque `highlight.js` (thème `github-dark`) au parseur Markdown `marked` dans [NoteEdit.vue](file:///home/robyn/Documents/Dev/StudyHub/web/src/views/Notes/NoteEdit.vue) et [PublicNote.vue](file:///home/robyn/Documents/Dev/StudyHub/web/src/views/Notes/PublicNote.vue). Les blocs de code (ex: ` ```python ... `) bénéficient désormais d'une coloration syntaxique automatique de haute qualité pour plus de 100 langages.

* **Gestion des tabulations dans l'éditeur (NoteEdit.vue)** : Interception de la touche `Tab` sur le textarea de l'éditeur de notes pour insérer 2 espaces au niveau du curseur et préserver le focus, facilitant ainsi l'écriture de listes ou de codes indentés.
* **Résolution du scroll automatique en haut de page (router/index.ts)** : Ajout d'un comportement de défilement personnalisé (`scrollBehavior`) dans la configuration de Vue Router. Si le chemin de la route reste identique lors d'une action (comme lors du passage du mode Visualiser au mode Modifier via la query string `?edit=true`), la position de défilement est préservée au lieu de scroller vers le haut de la page.
* **Préservation des tabulations et espaces dans le rendu visuel (style.css)** : Ajout de la règle `white-space: pre-wrap;` sur le conteneur global `.markdown-body` pour s'assurer que les indentations, tabulations (les 2 espaces insérés via Tab) et multi-espaces manuels saisis par l'utilisateur soient fidèlement représentés dans la zone d'aperçu HTML et lors de la lecture/impression de la note.
