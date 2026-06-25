# Journal de Développement — StudyHub

## [2026-06-22] UX — masquer « En attente de sauvegarde… » en révision active

En mode **Révision Active** d'une note (`notesStore.isReviewModeActive`), les cartes intégrées non
encore sauvegardées affichaient « En attente de sauvegarde… » (bruit visuel pendant la révision).
`renderSm2Buttons` (`NoteEdit.vue`) renvoie désormais `''` dans ce cas quand le mode révision est
actif ; le rappel reste affiché en mode Lecture/édition. Build + Vitest 66 verts.


## [2026-06-22] Fix — timeout trop court sur la génération de flashcards IA

**Symptôme** : la génération « avait l'air de marcher » puis affichait « IA indisponible ».
**Cause** : l'instance Axios a un `timeout` global de **10 s** (`api.ts`), or une génération Gemini
prend souvent 15-90 s → la requête est avortée côté front pendant que le backend (timeout urllib
90 s) travaille encore → branche réseau → repli + « IA indisponible ».
**Correctif** (`Reviews.vue`) : `api.post('/flashcards/generate', payload, { timeout: 120000 })`
(120 s, au-delà des 90 s backend) + message d'attente plus explicite (« jusqu'à une minute, ne
fermez pas la fenêtre »). Build + Vitest 66 verts ; E2E 23 verts.


## [2026-06-22] Fix UX — messages d'erreur précis pour la génération de flashcards IA

**Symptôme** : « IA indisponible » s'affichait même quand l'IA marchait. Diagnostic (logs
`backend.log`) : le `catch` du front basculait en repli local pour **toute** réponse non-2xx, alors
que les vrais échecs étaient un **401** (jeton JWT expiré, durée 1 h) et un **400** (note de 4
caractères → « source sans texte exploitable »). Le pipeline IA lui-même est OK (vérifié en live :
`POST /flashcards/generate` → 200 + 11 cartes sur une note de 1907 caractères).

**Correctif** (`Reviews.vue`, `executeFlashcardGeneration`) : distinction des cas dans le `catch` via
`err.response.status` (sans `any`, cast typé) :
- **401** → « Votre session a expiré. Reconnectez-vous… » (pas de repli)
- **429** → « Trop de générations… patientez »
- **400** → message renvoyé par le backend (source vide)
- **502 / réseau** → repli sur l'extraction locale + « IA indisponible » (comportement légitime conservé)

**Tests** : `reviews-ai-flashcards.spec.ts` étendu (401/429/400/502). Build + Vitest 66 verts ;
E2E 23 verts.


## [2026-06-22] Feature — génération de flashcards par IA (Notes / Classeurs)

**Besoin** : le bouton « Générer depuis Notes / Classeurs » (vue Révisions) extrayait les cartes par
simples motifs regex côté client. Désormais il **utilise l'IA** (Gemini) pour rédiger des
questions/réponses ciblées.

**Backend** :
- `AIService.generate_flashcards(source_text, count=0, subject="")` — nouvel appel Gemini (même
  patron que `generate_quiz`) : prompt anti-injection (`<source_text>`), atomicité des cartes,
  nombre adaptatif selon la taille, sortie JSON `[{front, back}]` nettoyée.
- `FlashcardGenerationService(note_dao, binder_dao, ai_service)` : récupère le contenu **côté
  serveur** avec contrôle d'appartenance (note → contenu+titre ; classeur → agrégation des notes de
  l'utilisateur via `NoteDAO.get_by_binder_for_user`), tronque à 60 000 caractères, délègue à l'IA.
  Ne crée pas les cartes.
- Endpoint `POST /api/v1/flashcards/generate` (`flashcards_global_bp`), JWT + `20/h`/utilisateur.
  Erreurs : 400 (vide), 403/404 (appartenance), 502 `AI_GENERATION_FAILED`.
- Tests `test_flashcard_generation.py` (note, classeur agrégé, vide→400, 404, 403, 401) avec
  `AIService.generate_flashcards` mocké. Suite backend complète verte.

**Frontend** (`Reviews.vue`) : `executeFlashcardGeneration` appelle `/flashcards/generate` puis
réutilise la création de deck + dédoublonnage + insertion existants. **Repli** automatique sur
l'extraction locale par motifs si l'IA est indisponible (clé absente/réseau) — message distinct.
Encart explicatif IA dans la modale. E2E `reviews-ai-flashcards.spec.ts`.

Build + Vitest 66 verts ; E2E 19 verts. ⚠️ Rendu visuel non vérifié en headless.


## [2026-06-22] Feature — éditeur de diagrammes : multi-sélection + alignement (incrément 7)

**Incrément 7** (`Diagrams.vue`, frontend only) : sélection multiple de nœuds et alignement de groupe.
- **Modèle de sélection refactoré** : `selectedNodeId` (primaire, pour panneau/resize/édition/liage)
  + `selectedNodeIds: number[]` (groupe). Helpers `selectSingleNode` / `toggleNodeSelection` /
  `clearNodeSelection` / `isNodeSelected` ; tous les anciens `selectedNodeId.value = …` passent par
  ces helpers (sélections mutuellement exclusives node/masque/lien/tracé conservées).
- **Maj+clic** sur un nœud : (dé)sélection sans déplacement. **Maj+glisser** sur le fond : sélection
  par rectangle (marquee, nœuds dont le **centre** est dans la zone) ; le glisser simple reste un pan.
- **Multi-déplacement** : décalages de chaque nœud sélectionné capturés au mousedown
  (`dragOffsets`), déplacés ensemble (avec snap-grille). `Suppr` efface tout le groupe.
- **Alignement** (panneau « N éléments sélectionnés », ≥2) : gauche/centre/droite et haut/milieu/bas,
  **bords-conscients** via `effectiveSize()` (taille explicite ou défaut par forme `NODE_DEFAULT_SIZE`).
- La poignée de redimensionnement n'apparaît que pour une sélection **unique**.

**Rétro-compat** : rien à persister (sélection = état de vue), JSON `code` inchangé. Modes masque/pen
intacts. **Tests** : `diagrams-editor.spec.ts` étendu (multi-sélection + alignement, suppression
clavier de groupe). Build + Vitest 66 verts ; E2E 18 verts. ⚠️ Rendu visuel non vérifié en headless.
**Roadmap diagrammes complète** (incréments 1→7).


## [2026-06-22] Feature — éditeur de diagrammes : crayon main levée (incrément 6)

**Incrément 6** (`Diagrams.vue`, frontend only) : annotation au crayon (freehand).
- **Nouveau mode** `drawingMode = 'pen'` (exclusif avec `mask`/`select`) ; bascule + palette de
  4 couleurs (rouge/bleu/vert/encre) dans le panneau d'outils. Cliquer-glisser trace une polyligne ;
  les points sont échantillonnés (> 2 px monde) puis lissés (`stroke-linecap/linejoin=round`).
- **Modèle** : nouveau champ `drawings: PenStroke[]` (`{id, points[], color, width}`) dans le JSON
  `code` — **optionnel** (`data.drawings || []`) → rétro-compatible. Rendu via `<polyline>` en
  coordonnées monde (suivent pan/zoom).
- **Sélection/suppression** : en mode select, clic sur un tracé (hit-area élargie) → panneau
  « Tracé sélectionné » + suppression ; `Suppr` géré ; intégré à l'historique undo/redo et au
  nettoyage de sélection mutuel.
- Persisté par `saveDiagram`, parsé/réinitialisé dans `selectDiagram`.

**Note technique (tests)** : le canevas peut être hors viewport → les tests souris doivent
`scrollIntoViewIfNeeded()` avant `boundingBox()` (sinon clics hors écran). `data-testid="diagram-canvas"`
ajouté.

**Rétro-compat** : champ `drawings` optionnel, mode masque intact.
**Tests** : `diagrams-editor.spec.ts` étendu (tracé au crayon via souris). Build + Vitest 66 verts ;
E2E 16 verts. ⚠️ Rendu visuel non vérifié en headless.
**Roadmap terminée** (incréments 1→6). Reste optionnel : multi-sélection + alignement de groupes.


## [2026-06-22] Feature — éditeur de diagrammes : annuler / rétablir (incrément 5)

**Incrément 5** (`Diagrams.vue`, frontend only) : historique undo/redo.
- **Pile d'historique** : snapshots JSON de `{nodes, connections, masks, backgroundImage}` capturés
  via un `watch` profond **débouncé (350 ms)** → un point d'historique par geste fini (drag/resize
  continus regroupés). Capacité 50, troncature de la branche « rétablir » à chaque nouvelle action.
- **Restauration** : `applySnapshot()` réassigne l'état sous garde `isApplyingHistory` (évite la
  ré-entrance du watcher) et nettoie les sélections ; déduplication par égalité de snapshot.
- **Commandes** : barre flottante haut-gauche du canevas (↶/↷, désactivées via `canUndo`/`canRedo`)
  + raccourcis `Ctrl/⌘+Z` (annuler), `Ctrl/⌘+Maj+Z` / `Ctrl+Y` (rétablir), ignorés en saisie texte.
- Historique (ré)initialisé à chaque sélection de diagramme.

**Rétro-compat** : aucun changement du schéma `code` (l'historique est en mémoire). Mode masque intact.
**Tests** : `diagrams-editor.spec.ts` étendu (annuler/rétablir un ajout de forme). Build + Vitest 66
verts ; E2E 15 verts. ⚠️ Rendu visuel non vérifié en headless.
**Reste** : crayon main levée (incrément 6), multi-sélection + alignement (incrément 7).


## [2026-06-22] Feature — éditeur de diagrammes : redimensionnement + alignement grille (incrément 4)

**Incrément 4** (`Diagrams.vue`, frontend only) :
- **Redimensionnement des nœuds** : `VisualNode` gagne `width?`/`height?` (optionnels). Une poignée
  bas-droite (`cursor-nwse-resize`) apparaît sur le nœud sélectionné *redimensionnable* (rect,
  ellipse, post-it). Le redimensionnement est **ancré au centre** (`width = 2·(worldX − node.x)`),
  taille min 40px ; `sizeStyle()` applique la taille en inline-style par-dessus les classes Tailwind
  par défaut (donc nœuds existants inchangés).
- **Alignement sur la grille** : bascule dans la palette (`snapToGrid`, état de vue, défaut off).
  Quand actif, le déplacement *et* le redimensionnement s'accrochent au pas de 20px (`snapVal()`).
- Le redimensionnement réutilise `screenToWorld()` (correct sous pan/zoom) et est branché en tête de
  `onCanvasMouseMove`/`onCanvasMouseUp` ; réinitialisé à la sélection d'un diagramme.

**Rétro-compat** : `width`/`height` optionnels, anciens diagrammes inchangés ; mode masque intact.
**Tests** : `diagrams-editor.spec.ts` étendu (poignée de resize au focus + bascule grille). Build +
Vitest 66 verts ; E2E 14 verts. ⚠️ Rendu visuel non vérifié en headless.
**Reste** : multi-sélection + alignement (incrément 5), undo/redo + crayon (incrément 6).


## [2026-06-22] Feature — éditeur de diagrammes : nouvelles formes + édition des liens (incrément 3)

**Incrément 3** (`Diagrams.vue`, frontend only) :
- **3 nouvelles formes** ajoutées à la palette : **ellipse** (domaine), **texte libre** (sans cadre,
  couleur d'encre) et **post-it** (note jaune, `<textarea>` multi-lignes). `VisualNode.type` élargi
  (`NodeShape`), `addNode` factorisé via `NODE_DEFAULT_LABEL`. Le sélecteur de couleur est masqué
  pour texte/post-it (non pertinent).
- **Édition des liens** : `Connection` gagne `label?`, `arrow?` (`end`/`both`/`none`), `dashed?`
  (tous optionnels → défaut rétro-compatible `connArrow()=end`, trait plein, sans libellé). Le panneau
  « Lien sélectionné » expose : champ libellé (rendu en `<text>` SVG au milieu du trait, halo
  `stroke-surface`), sélecteur de flèche (segmented) et bascule plein/pointillé. Marqueurs SVG
  `marker-start`/`marker-end` pilotés par `arrow` (le marqueur unique `#arrow` à `auto-start-reverse`
  sert aux deux extrémités).

**Rétro-compat** : champs ajoutés tous optionnels, anciens diagrammes inchangés ; mode masque intact.
**Tests** : `diagrams-editor.spec.ts` étendu (ajout forme texte libre + sélection lien & libellé).
Build + Vitest 66 verts ; E2E 12 verts. ⚠️ Rendu visuel non vérifié en headless.


## [2026-06-22] Feature — éditeur de diagrammes : pan + zoom (incrément 2)

**Incrément 2** (`Diagrams.vue`, frontend only) : le canevas devient une « feuille de papier »
déplaçable et zoomable.
- **Conteneur « monde »** : un `<div>` recevant `transform: translate(panX,panY) scale(zoom)`
  (origine `0 0`) enveloppe le SVG (image de fond, connexions, masques) **et** les nœuds. La grille
  est désormais un fond CSS du viewport (`background-position`/`-size` suivant pan/zoom) → effet
  infini, plus de `<pattern>` SVG.
- **Pan** : glisser le fond (désélection au relâchement *sans* déplacement, seuil 3px) ou molette
  (deltaX/deltaY).
- **Zoom** : `Ctrl/⌘ + molette` (zoom vers le curseur) + barre flottante `−` / `%` (reset) / `+`
  (zoom vers le centre). Bornes 0,3×–3×.
- **Refacto coordonnées** : helper unique `screenToWorld(clientX,clientY)` utilisé par le drag de
  nœud (offset monde) et le dessin de masque. Le drag n'est plus delta-`clientX` mais position
  monde + offset → correct quel que soit le zoom/pan. Clamp élargi (−3000…6000) pour la feuille.
- La vue est **réinitialisée** à chaque sélection de diagramme ; **non persistée** dans le JSON
  `code` (état de vue uniquement) → rétro-compat totale, mode masque intact.

**Tests** : `tests-e2e/diagrams-editor.spec.ts` étendu (contrôles de zoom + reset). Build + Vitest 66
verts ; E2E 10 verts. ⚠️ Rendu visuel non vérifié en headless.


## [2026-06-22] Feature — éditeur de diagrammes : édition inline + suppression de lien (incrément 1)

**Besoin** : rendre l'éditeur de diagrammes plus complet/flexible (façon « feuille de papier »).
Livré par incréments en PR séparées. Roadmap : (1) édition inline + suppression de lien + raccourci
`Suppr` ; (2) pan/zoom ; (3) nouvelles formes + édition des liens ; (4) redimensionnement + snap +
multi-sélection ; (5) undo/redo + crayon.

**Incrément 1** (`Diagrams.vue`, frontend only, aucun changement de schéma `code`) :
- **Édition inline du texte** : double-clic sur un nœud (rect/cercle/losange) → input superposé
  (directive locale `v-focus`), validation à `Entrée`/`blur`, annulation à `Échap`. Le champ de la
  barre latérale reste disponible.
- **Sélection/suppression de lien** : les connexions deviennent cliquables (trait de clic élargi
  invisible de 14px), le lien sélectionné passe en rose et s'épaissit ; panneau latéral « Lien
  sélectionné » (origine → cible) avec bouton supprimer.
- **Raccourci clavier `Suppr`/`Backspace`** : efface le nœud / masque / lien sélectionné (ignoré
  pendant la saisie dans un input/textarea/contenteditable).
- Sélections mutuellement exclusives (nœud ↔ masque ↔ lien) ; reset à la sélection d'un diagramme.

**Rétro-compat** : aucun champ ajouté au JSON `code`, le mode masque (occlusion) est intact.
**Tests** : nouveau `tests-e2e/diagrams-editor.spec.ts` (rendu des nœuds + édition inline au
double-clic). Build + Vitest 66 verts ; E2E 9 verts. ⚠️ Rendu visuel non vérifié en headless.


## [2026-06-22] Feature — réviser un dossier entier

**Besoin** : pouvoir réviser tout un classeur d'un coup (cartes dues de tous ses decks).

**Backend** : nouvel endpoint `GET /binders/<id>/study` → `FlashcardService.get_binder_study_cards`
agrège, via la relation `binder.decks`, les cartes dues (réutilise `get_study_cards` deck par deck,
avec son filtrage de types et ses contrôles d'appartenance). Chaque carte renvoie son `deck_id`.
Tests `test_binder_study.py` (agrégation multi-decks, exclusion des autres classeurs, isolation
inter-utilisateurs).

**Frontend** : route `StudyBinder` (`/bibliotheque/:id/reviser`) réutilisant le runner
`StudyDeck.vue` en **mode dossier** (fetch `/binders/:id/study`, titre = nom du dossier, retour vers
le dossier). Bouton **« Réviser ce dossier »** dans l'en-tête de la Bibliothèque (visible quand le
dossier contient des decks). `rateCard` notifie désormais le SM-2 via `currentCard.deck_id` (et non
un id de route) — correct en mode deck, dossier (multi-decks) **et** révision anticipée (corrige un
bug latent où la révision anticipée multi-decks notifiait le mauvais deck).

Build + Vitest 66 verts ; suite backend complète verte.


## [2026-06-22] UX — cartes de la vue Planning « semaine » trop étroites

**Symptôme** : en vue semaine, les cartes-jours sont trop étroites.

**Cause** : `WeekCalendar` forçait `md:grid-cols-7` (7 colonnes côté à côte ⇒ ≈1/7 de largeur),
et le nom de deck était tronqué dur à `max-w-[80px]`.

**Fix** : grille responsive plafonnée à **4 colonnes** (`sm:2 lg:3 xl:4`) — la semaine s'étale sur
2 rangées mais chaque carte est ≈1/4 de largeur (bien plus lisible). Le nom de deck prend la largeur
disponible (`flex-1 min-w-0`) au lieu de `max-w-[80px]`. Build + Vitest 66 verts. ⚠️ Rendu non
vérifié en headless.


## [2026-06-22] Fix fonctionnel — créer un diagramme depuis la Bibliothèque

**Symptôme** : aucun moyen de créer un diagramme.

**Cause racine** : l'éditeur `/diagrams` possède bien un bouton « Nouveau diagramme », mais il
était **inatteignable** : la nav pointe vers la Bibliothèque, dont le menu « Ajouter » ne proposait
que Sous-dossier / Élément existant / Note (pas Diagramme), et la section Diagrammes vide n'offrait
aucune création. De plus, cliquer un diagramme existant routait vers `/diagrams` **sans son id**
(ouvrait le premier, pas le bon).

**Fix** (`Binders.vue`) : entrée « Diagramme » ajoutée au menu « Ajouter » → `addDiagram()` crée un
diagramme rattaché au dossier courant (`binder_id` résolu côté service) puis ouvre l'éditeur via
`/diagrams?id=…`. Clic sur un diagramme existant corrigé pour passer son id. Build + Vitest 66 verts.


## [2026-06-22] Fix fonctionnel — création de la première classe (œuf/poule)

**Symptôme** : aucun moyen de créer une classe.

**Cause racine** : dans `ClassesLanding`, l'onglet « Enseignant » (qui héberge le bouton
« Créer une classe ») n'était affiché que si `isTeacher` = l'utilisateur administre **déjà** une
classe. Un nouvel utilisateur sans classe ne pouvait donc jamais accéder à l'onglet → ne pouvait
jamais en créer une.

**Fix** : l'onglet « Enseignant » est désormais **toujours visible** (son empty state invite déjà à
créer un premier espace). `isTeacher` ne sert plus qu'à choisir l'onglet par défaut. Suppression de
la rétrogradation `?tab=teacher → student`. Build + Vitest 66 verts.


## [2026-06-22] Fix fonctionnel — rattachement deck ↔ classeur (binder_uuid)

**Symptôme** : ajouter un deck à un dossier via « Ajouter › Élément existant » semblait
sans effet — le deck n'apparaissait jamais dans le classeur après validation.

**Cause racine** : `DeckResponse.binder_id` lit `Field(validation_alias="binder_uuid")`, mais
le modèle `Deck` était le **seul** modèle rattachable (note/diagram/pdf/revision/exam/group) à
ne PAS exposer la propriété `binder_uuid`. Résultat : l'API renvoyait toujours `binder_id: null`
pour les decks ; le filtre client de la Bibliothèque (`deck.binder_id === currentBinderId`) ne
matchait jamais. Le rattachement en base fonctionnait pourtant (le filtrage serveur
`GET /decks?binder_id=` était correct — d'où le test existant vert qui masquait le bug).

**Fix** : ajout de la propriété `binder_uuid` sur `Deck` (mirroir de Note/Diagram). Test de
régression `test_attached_deck_response_exposes_binder_uuid` (assert `deck.binder_id == UUID`
après attach). Suite backend complète verte. Aucune migration (pas de schéma DB modifié).


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

---

## [2026-06-15] Suppression des decks fantômes — cartes d'évaluation proposées en opt-in

### Contexte
Le « deck fantôme » créait automatiquement des flashcards depuis une note, par deux voies : la synchronisation déterministe des balises (`[def:]`, `{{qcm:}}`…) et le bouclage SM-2 des évaluations IA (items ratés). Décision produit : **plus aucune flashcard ne doit être créée automatiquement depuis une note**. À la place, une évaluation IA *propose* des cartes pour les thèmes ratés, que l'utilisateur ajoute (ou non) à un deck réel de son choix.

### Backend
* **Modèles** : suppression de `Deck.note_id` (+ relations `Note.deck`/`Note.flashcards`). Champ `flashcards` retiré de `NoteResponse`.
* **Migration `e1f2a3b4c5d6`** : drop de `decks.note_id`. Non destructif — les decks fantômes existants sont détachés et renommés (retrait du préfixe `[Phantom] Note: `), leurs cartes conservées comme decks normaux. Idempotente, compatible SQLite/PostgreSQL (batch).
* **`note_service`** : suppression de `_sync_phantom_deck` et de tous ses appels ; le service ne dépend plus des DAO deck/flashcard.
* **`diagram_service`** : suppression de la re-synchronisation des notes.
* **`community_service`** : le clone d'un package clone les decks normaux (plus de cas fantôme).
* **`evaluation_service`** : la complétion ne crée plus de cartes ; elle renvoie `proposed_cards` (items ratés). Nouvelle méthode `create_flashcards_from_missed(user_id, eval_id, item_ids, deck_id)` (idempotente par deck, appartenance du deck vérifiée), exposée par `POST /evaluations/:id/flashcards` — calquée sur le flux existant des QCM.
* Les balises de note **restent** et continuent d'alimenter la génération des évaluations IA.

### Frontend
* **`NoteEvaluation.vue`** : à la complétion, liste des cartes proposées (cases à cocher) + sélecteur de deck (existant ou nouveau) + boutons « Ajouter au deck » / « Non merci », puis confirmation avec accès au deck. `evaluationService.ts` : type `ProposedCard`, champ `proposed_cards`, méthode `addFlashcards`.
* **`NoteEdit.vue`** : le mode « Révision Active » (blocs de révision interactifs intégrés aux notes) est **conservé**. L'interactivité (révéler les trous, répondre aux QCM/VF/ordre/assoc) repose sur l'état client `placeholderStates`, indépendant des cartes fantômes. Comme la note ne porte plus de cartes (`note.flashcards` absent → `cardId` nul partout), les boutons de notation SM-2 (qui notaient les cartes fantômes) ne s'affichent plus et aucun `PATCH /flashcards/:id/review` n'est déclenché depuis une note. Guide mis à jour. Texte mis à jour dans `Reviews.vue`.

### Tests
* Suppression des tests fantômes (`test_note_phantom_deck_sync`, `test_ai_card_survives_phantom_deck_resync`, `test_diagram_occlusion_sync`, assertions de renforcement) ; ajout des tests de proposition à la complétion, d'ajout opt-in à un deck (idempotence) et d'isolation (deck d'un autre utilisateur). MAJ `test_community` / `test_regression` / `test_placeholders`. Backend, `vue-tsc` et Vitest verts.

---

## [2026-06-15] Classeur — dossier de révision thématique (items typés + ajout unifié)

### Contexte
Refonte de la fonction Classeur : la rendre plus instinctive pour y ajouter du contenu et permettre d'y mettre plus que des notes & flashcards. Décision validée : les QCM / Vrai-Faux / Ordre / Association sont des **items typés au sein d'un « jeu de révision »** (extension des decks/flashcards), planifiés en répétition espacée SM-2.

### Backend
* **`Flashcard`** : ajout de `card_type` (basic | qcm | vf | ordre | assoc) et `payload` (JSON structuré). `front`/`back` restent renseignés (résumé énoncé/réponse) pour la recherche et le repli d'étude. Migration additive `f2b3c4d5e6a7` (idempotente, SQLite/PostgreSQL).
* Schémas (`FlashcardCreate`/`Update`/`Response`) + `FlashcardService` (création/màj) acceptent `card_type`/`payload`. Aucune modif du flux SM-2 (la planification est par carte). Tests : carte basic par défaut, création QCM typée listée + étudiable, rejet d'un type invalide.

### Frontend
* **`RevisionItemModal.vue`** : composition d'un item typé (carte/QCM/VF/ordre/assoc) avec choix ou création du jeu de révision cible ; construit `front`/`back` + `payload`.
* **`TypedStudyCard.vue`** : étude interactive des items typés (sélection pour QCM/VF avec feedback de justesse ; « Révéler » pour ordre/assoc) ; déclenche l'auto-évaluation SM-2 du parent.
* **`StudyDeck.vue`** : rend `TypedStudyCard` pour les items typés (sinon la carte recto/verso), réutilise les boutons de notation SM-2.
* **`Binders.vue`** : menu unifié **« + Ajouter »** (sous-dossier, note, jeu de révision, carte, QCM, VF, ordre, association), section « Jeux de révision » (compteur d'items + ajout rapide), création directe depuis le classeur (note → éditeur, jeu de révision, items typés).
* `stores/decks.ts` : types `CardType`/`CardPayload`, `Flashcard.card_type/payload`, `createCard` rétro-compatible (params type/payload optionnels).

### Tests
* Backend (cartes typées) verts ; `vue-tsc` clean ; Vitest 25/25 (ajout `tests/stores/decks.spec.ts`).

### À suivre (hors périmètre de cette itération)
* Surfacer diagrammes & PDFs dans le menu d'ajout / l'affichage du classeur (ils se rattachent déjà aux classeurs mais via leurs propres vues).
* Permettre la création d'items typés aussi depuis la vue Decks.

## [2026-06-15] Socle de révision (D3c) — ensembles typés indépendants + réconciliation PR #48

Mise en œuvre du socle A0 de `docs/REFACTO_FONCTIONNALITES.md`. **Décision D3c** : le `Deck`/`Flashcard` reste strictement recto/verso ; les autres types de révision (QCM, vrai/faux, association, définition, ordre) deviennent des entités indépendantes portées par `RevisionSet`/`RevisionItem`.

### Backend
* Modèles **`RevisionSet`** (homogène, typé, rattaché à un classeur, `tuning_default`) et **`RevisionItem`** (payload validé par type, état SM-2 par item, `tuning`). Relations `User`/`Binder`.
* **`/api/v1/revision`** : CRUD ensembles + items, étude (`/study`), réponse SM-2 (`/study/answer/:id`). DAO + service + schémas Pydantic, validation de payload par type, isolation `user_id`.
* **SM-2** : paramètre `tuning` (multiplicateur d'intervalle, plancher 1 jour) — `calculate_sm2(..., tuning=tuning_ensemble*tuning_item)`.
* **`StudySession`** : colonnes `item_id`/`item_type` (suivi unifié des éléments de révision, base des stats D5).
* **Flashcards ramenées à recto/verso** : retrait de `card_type`/`payload` des schémas et du `FlashcardService` (annulation du mélange PR #48).
* **Migrations** : `a1b2c3d4e5f6` (tables + colonnes, additive/idempotente) et `b2c3d4e5f6a7` (réconciliation : déplace les cartes typées des decks vers des `RevisionSet` homogènes, fonction `reconcile()` testable, idempotente). Probe de drift OK (seuls faux positifs GIN SQLite).

### Frontend
* **`stores/revision.ts`** : CRUD ensembles/items typés + étude.
* **`RevisionItemModal.vue`** réconcilié : `basic` → flux deck (flashcard), autres types → ensembles de révision (choix/création d'un ensemble du **même** type).
* **`StudyDeck.vue`** : retrait du flux typé (les decks ne contiennent plus que du recto/verso) ; **`TypedStudyCard.vue`** supprimé (réintroduit en A2–A6 depuis le store révision).
* **`stores/decks.ts`** : `Flashcard` recto/verso pur, `createCard(deckId, front, back)`.
* **`Binders.vue`** : menu d'ajout pointant vers les types d'ensembles (ajout de « Définition »).

### Tests
* Backend 203/203 (ajout `tests/test_revision.py` : ensembles homogènes, rejet de type invalide, tuning, étude/SM-2 + `StudySession` unifiée, isolation, migration de réconciliation idempotente).
* `vue-tsc` clean ; Vitest 26/26 (`decks.spec.ts` recto/verso + `revision.spec.ts`).

### À suivre
* A1–A6 : éditeurs/étude par type depuis le store révision ; A7/A8 : stats par élément/classeur (D5) ; C2 : réorg de l'onglet Révisions.

## [2026-06-15] A1 — Flashcard avancée : mode inversé, tuning par carte & courbe d'apprentissage

Implémentation de A1 (`docs/REFACTO_FONCTIONNALITES.md`), remappée sur `Deck`/`Flashcard` (D3c).

### Backend
* **`Deck`** : `reversed` (D7) et `tuning_default` (D4). **`Flashcard`** : `tuning` par carte et `reverse_of_id` (miroir verso→recto).
* **Mode inversé matérialisé** : création/édition/suppression d'une carte gèrent son miroir (contenu synchronisé, suppression en cascade) ; la bascule `reversed` du deck (PUT) crée/retire les miroirs. Les miroirs ont un état SM-2 distinct, sont **étudiés séparément** et **exclus** des listes/compteurs de gestion.
* **SM-2 par carte** : intervalle × (`deck.tuning_default` × `card.tuning`).
* **Courbe d'apprentissage** : `GET /decks/:id/cards/:card_id/history` → série (date, grade) depuis `StudySession`.
* Migration additive/idempotente `c3d4e5f6a7b8`. Tests : miroir matérialisé, bascule on/off, suppression cascade, tuning allonge l'intervalle, historique. Suite 209/209, drift OK.

### Frontend
* `stores/decks.ts` : `Deck.reversed/tuning_default`, `Flashcard.tuning/reverse_of_id`, `createDeck`/`updateDeck`/`updateCard` étendus (rétro-compatibles), `fetchCardHistory`.
* `Decks.vue` : toggle **Mode inversé** + slider fine-tuning par défaut (modale deck), slider tuning par carte (modale carte), badge « ⇄ Inversé » sur la grille, bouton **courbe** par carte.
* **`LearningCurve.vue`** : sparkline SVG (zéro dépendance) — grades dans le temps, seuil de réussite, moyenne.
* Tests : `decks.spec` (reversed/tuning_default, tuning updateCard, fetchCardHistory). vue-tsc clean, Vitest 26/26, build OK.

## [2026-06-15] A2 — QCM scoré (D6)

Implémentation de A2 (`docs/REFACTO_FONCTIONNALITES.md`) sur le socle de révision.

### Backend
* **Passage scoré** : `POST /revision/sets/:id/run` (réservé au type `qcm`). Correction pondérée par **points** par question, **réponses multiples** en **tout-ou-rien**, score/total/pourcentage + détail par question (bonnes réponses, sélection).
* **Mise à jour SM-2 par question** au passage (réussi → grade 5, raté → 1 ; tuning ensemble × item) + `StudySession` unifiée (`item_id`/`item_type=qcm`).
* Schémas `RevisionRun*`. Pas de changement de modèle (aucune migration). Tests : score mono/multi, tout-ou-rien, SM-2/sessions, rejet hors-QCM. Suite 207/207.

### Frontend
* `RevisionItemModal` : champ **barème (points)** pour le QCM + indice réponses multiples.
* `stores/revision.ts` : `runQcm`, `fetchSet`, types `RunResult`/`RunAnswer`.
* **`QcmRun.vue`** (route `/revision/sets/:id/run`) : passage interactif (cases à cocher), correction, score pondéré + feedback par question (bonnes réponses révélées).
* `Binders.vue` : section **« Ensembles de révision »** (par type, compteur d'items) avec lancement du QCM.
* Tests : `revision.spec` (runQcm). vue-tsc clean, Vitest 26/26, build OK.

## [2026-06-15] A3–A6 — Étude typée : Vrai/Faux, Association, Définition, Ordre

Implémentation groupée (le plan autorise A3+A4–A6 ensemble) de l'**étude + correction + SM-2** pour les types restants, sur le socle de révision. Les éditeurs existaient déjà (socle) ; il manquait l'expérience d'étude.

### Backend
* **Correction par type** (`check_answer`) : VF (verdict), Association (appariement **ordre indifférent**, partiel/erroné = faux), Ordre (suite **stricte**).
* **`POST /revision/sets/:id/study/grade/:item_id`** : corrige (vf/association/ordre), met à jour **SM-2** (réussi → 5, raté → 2) + `StudySession` unifiée, renvoie `{correct, item}`. La **Définition** reste en **auto-évaluation** via l'endpoint `answer` générique.
* Schémas `RevisionGrade*`. Aucune migration. Tests : verdict VF, association ordre-indifférent + partiel=faux, ordre strict, rejet du type non corrigeable, définition self-eval. Suite 212/212.

### Frontend
* **`RevisionStudy.vue`** (route `/revision/sets/:id/study`) : étude carte-par-carte selon le type — VF (verdict + justification), Définition (révéler + auto-éval À revoir/Moyen/Acquis), Association (appariement par menus), Ordre (réordonnancement ▲▼) — avec correction, feedback et progression.
* `stores/revision.ts` : `gradeItem`.
* `Binders.vue` : les ensembles non-QCM lancent désormais l'étude générique (QCM → passage scoré).
* Tests : `revision.spec` (gradeItem). vue-tsc clean, Vitest 27/27, build OK.

## [2026-06-15] A7 — Statistiques par élément de révision (indicateurs D5)

Stats actionnables fondées sur des indicateurs reconnus (modèle DSR/FSRS, courbe d'oubli d'Ebbinghaus, True Retention & sangsues d'Anki). Pas de migration : `StudySession.item_id`/`item_type` (posés au socle) servent de source d'historique.

### Backend
* **`revision_stats_service`** — indicateurs dérivés de SM-2/`StudySession` : **difficulté D** ∈ [1,10] (de l'ease factor), **récupérabilité R** ∈ [0,1] (Ebbinghaus `R=exp(-t/S)`), **stabilité S** (= intervalle), **rétention réelle** (True Retention sur items mûrs), **sangsues** (échecs ≥ 4), **maturité** (intervalle ≥ 21 j), **date de maîtrise** (projection SM-2), nb de révisions, % réussite, échéances.
* **`GET /stats/items/:id`** (item + série historique) et **`GET /stats/sets/:id`** (agrégats + **verdicts actionnables** + résumé par item). Agrégat en **2 requêtes** (anti-N+1, `test_*_query_budget`).
* Méthodes DAO `StudySessionDAO.get_for_item(s)`. Schémas `RevisionItemStats`/`RevisionSetStats`/`RevisionItemSummary`. Suite 219/219.

### Frontend
* `stores/revision.ts` : `fetchSetStats`, `fetchItemStats` + types.
* **`RevisionSetStats.vue`** (`/revision/sets/:id/stats`) : cartes KPI (maîtrise, rétention réelle vs cible, réussite, échéances, sangsues, difficulté), **verdicts**, liste d'éléments (badges sangsue/mûr/à réviser) avec détail dépliable (**mini-courbe SVG** + stabilité/échecs/maîtrise).
* `Binders.vue` : bouton **stats** par ensemble.
* Tests : `revision.spec` (fetchSetStats/fetchItemStats). vue-tsc clean, Vitest 28/28, build OK.

### Portée
* A7 couvre les **éléments de révision** (qcm/vf/assoc/def/ordre) via `item_id`. Les flashcards ont déjà leur courbe (A1) + `/stats/decks/:id` ; l'unification complète flashcards↔items (écriture `item_id` côté flashcard) est laissée à un futur passage.

## [2026-06-15] A8 — Statistiques par classeur (clôt la Partie A)

Agrégation des stats de révision à l'échelle d'un classeur (et de son sous-arbre), réutilisant le service A7.

### Backend
* **`GET /stats/binders/<uuid>`** (option `?descendants=false`) : agrège tous les `RevisionSet` du classeur + descendants. Renvoie maîtrise, rétention réelle (True Retention), réussite moyenne, sangsues, à-réviser, difficulté moyenne, **répartition par type**, **ensembles à surveiller** (sangsues puis faible maîtrise) et liste complète.
* Refactor de `RevisionStatsService` : extraction de **`_aggregate_set`** (logique par ensemble partagée avec `get_set_stats`) + **`get_binder_stats`**. Accès vérifié par `check_binder_access` (propriétaire **ou** classe partagée). Sous-arbre via `BinderDAO.get_descendants`.
* **Anti-N+1** : `RevisionSetDAO.get_by_binders`, `RevisionItemDAO.get_by_sets`, sessions chargées en **une requête par type** présent (≤ 5). `test_binder_stats_query_budget` borne le nombre de requêtes.
* Schémas `RevisionBinderStats`/`RevisionSetSummary`/`RevisionTypeBreakdown`. **Aucune migration** (pas de changement de modèle).

### Frontend
* `stores/revision.ts` : `fetchBinderStats(binderId, includeDescendants)` + types `BinderStats`/`SetSummary`/`TypeBreakdown`.
* **`RevisionBinderStats.vue`** (`/revision/binders/:id/stats`) : KPI globaux, bascule « inclure les sous-classeurs », barres de **répartition par type**, ensembles **à surveiller** et liste cliquable (→ stats par ensemble A7).
* `Binders.vue` : bouton **« Stats »** dans l'en-tête du classeur.

### Tests
* Backend `test_stats_binder.py` : agrégation multi-ensembles/types, inclusion du sous-arbre (+ `descendants=false`), isolation entre utilisateurs, budget de requêtes. Suite **229/229**.
* Front : `revision.spec` (fetchBinderStats avec/sans sous-arbre). vue-tsc clean, **Vitest 33/33**.

### Portée
* Couvre les **ensembles de révision**. Les decks de flashcards conservent `/stats/decks/:id` ; leur intégration à la vue classeur pourra suivre l'unification flashcards↔items évoquée en A7. **Partie A (Révision) désormais complète.**

## [2026-06-15] C1 — Classeur : rattacher/détacher des éléments existants

Le classeur n'est plus seulement un lieu de **création** : on peut y déplacer des éléments déjà existants, et les en retirer sans les supprimer.

### Backend
* **`BinderItemsService`** (orchestration transverse) : `attach(user_id, binder_id, items)` et `detach(user_id, items)` pour `note`/`deck`/`set`/`diagram`/`pdf`. Vérifie l'appartenance de chaque élément **et** l'accès en écriture au classeur (`check_binder_access`). Aucune SQL directe (passe par les DAO + `binder_id`).
* Endpoints **`POST /binders/:id/items`** (attache) et **`POST /binders/:id/items/detach`** (détache → `binder_id = NULL`, sans suppression). Schémas `BinderItemRef`/`BinderItemsRequest`. Pas de migration.

### Frontend
* `stores/binders.ts` : `attachItems`/`detachItems` + types `BinderItemRef`/`BinderItemType`.
* `Binders.vue` : entrée **« Élément existant »** dans le menu « + Ajouter » ouvrant une **modale multi-sélection** (notes, jeux de révision, ensembles non rangés ou d'un autre classeur) ; bouton **« détacher »** (icône `FolderMinus`) par ligne, distinct de la suppression.

### Tests
* Backend `test_binder_items.py` : attache (note/deck/ensemble), détache conserve l'élément, rejet d'un type inconnu (400), isolation (élément d'autrui → 403/404, classeur d'autrui → 403/404). Suite **234/234**.
* Front : `binders.spec` (attachItems/detachItems → bons endpoints). vue-tsc clean, **Vitest 35/35**.

### Reste
* Afficher les **diagrammes et PDF** directement dans la vue classeur (le backend attach/détache les gère déjà ; seul l'affichage/sélecteur UI manque). Suite du plan : **C2** (réorg de l'onglet Révisions).

## [2026-06-15] C2 — Onglet Révisions réorganisé (Classiques vs IA)

`Reviews.vue` passait des onglets à plat mélangeant tout. On structure en deux catégories.

### Frontend
* **Sélecteur de catégorie** (`Classiques` / `IA`) + **sous-onglets** dynamiques (`currentTabs`).
* **Classiques** : Flashcards (panneau existant) + un panneau générique par type d'ensemble (`set-qcm`, `set-vf`, `set-association`, `set-definition`, `set-ordre`). Chaque ensemble : bouton **Étudier/Lancer** (`/revision/sets/:id/run|study`), **Stats** (`/revision/sets/:id/stats`, A7) et un volet **Réglages** (renommer, slider **fine-tuning** `tuning_default`, sélecteur **classeur**, **supprimer**).
* **IA** : regroupe les panneaux existants (évaluation IA, feuille blanche, Feynman, auto-QCM).
* `stores/revision.ts` : `updateSet` accepte désormais `binder_id` (rattachement depuis les réglages). `onMounted` charge aussi `fetchSets()`.

### Tests
* `revision.spec` : `updateSet` transmet name/tuning_default/binder_id. vue-tsc clean, **Vitest 36/36**. E2E `/reviews` se rend sans erreur.

### Reste / suite
* Frontend uniquement, pas de migration. **Parties A et C bouclées** (hors affichage diagrammes/pdfs dans le classeur). Suite du plan : **Partie B** — B3 (devoirs sur ensembles de révision), B4 (Q&A élèves), B5 (stats de groupe étendues).

## [2026-06-15] B3 — Devoirs ciblant un ensemble de révision

Les devoirs (déjà multi-tâches) peuvent désormais cibler un **ensemble de révision typé** (qcm/vf/association/définition/ordre), en plus des classeurs et notes.

### Backend
* `TASK_TYPES` + `TASK_TARGET_KIND` étendus avec **`revision`** (cible `revision_set`). `_resolve_task_target` résout l'ensemble par `id` et vérifie l'appartenance au professeur (→ `ref_id=set.id`, `ref_label=set.name`).
* **Complétion dérivée** (`_revision_state`) : à partir des `StudySession` des items de l'ensemble (`item_id`/`item_type`), nombre d'items révisés vs objectif `min_items` + `min_score` (% réussite). Branchée dans `recompute_task_for_user` ; l'élève « soumet » la tâche pour rafraîchir (comme quiz/exam/blurting).
* Pas de migration : `task_type` est une colonne `String` sans contrainte d'énum.

### Frontend
* `AssignmentBuilder` : nouveau type **« Ensemble de révision »** (cible `set`, prop `sets`) + champs d'objectif (items min., score min.). `TeacherDashboard` fournit `setOptions` et charge `fetchSets()`.
* Lancement élève : `taskLaunchRoute` route `revision` → `/revision/sets/:id/study` (via `ref_id`) ; `RevisionStudy` **redirige les QCM** vers leur passage scoré (`/run`). CTA « Réviser » dans `StudentClassView` (`TASK_META.revision`).

### Tests
* Backend `test_assignment_revision` : création/résolution de la tâche, complétion dérivée d'une session d'étude, isolation (ensemble d'autrui → 404). Suite **237/237**.
* Front : `assignmentTasks.spec` (route revision par `ref_id`). vue-tsc clean, **Vitest 37/37**.

### Suite
* **B4** — Questions des élèves (Q&A) : introduit un nouveau modèle + migration. Puis **B5** (stats de groupe étendues).

## [2026-06-15] B4 — Questions des élèves (Q&A)

Un canal de questions élève → professeur dans chaque classe, avec notifications.

### Backend
* Modèle **`ClassQuestion`** (`group_id`, `author_id`, `body`, `answer`, `answered_by`, `status` `open`/`answered`, `created_at`, `answered_at`) — réponse unique (pas de thread). Enregistré dans `models/__init__`. **Migration idempotente** `a7c1d2e3f4b5` (création de table + index, multi-dialecte).
* **`ClassQAService`** : `post_question` (membre), `list_questions` (prof = toutes, élève = les siennes), `answer_question` (prof uniquement → statut `answered`). Endpoints `GET/POST /classes/:id/questions`, `POST /classes/:id/questions/:qid/answer`.
* **Notifications** : type `question` aux professeurs (owner/admin) à la création ; type `answer` à l'auteur à la réponse (réutilise `Notification`).

### Frontend
* `classService` : `listQuestions`/`postQuestion`/`answerQuestion` + type `ClassQuestion`.
* `StudentClassView` : section « Poser une question » (sélecteur de classe via `getMyClasses` + champ + fil des questions avec réponses).
* `TeacherDashboard` : nouvel onglet **« Questions »** (inbox par classe, réponse inline, badge statut).

### Tests
* Backend `test_class_qa` : post + visibilité prof/élève, isolation entre élèves, réponse + statut, élève ne peut répondre (403), notifications prof & élève. Suite **242/242**.
* Front : `classQuestions.spec` (endpoints). vue-tsc clean, **Vitest 40/40**.

### Suite
* **B5** — Stats de groupe étendues (temps moyen de révision, réussite globale, avancement par élève) : **dernier item** du plan de refonte.

## [2026-06-15] B5 — Statistiques de groupe étendues

Le tableau de bord professeur intègre les métriques de **révision** (au-delà des seuls devoirs).

### Backend
* `AnalyticsService.get_class_overview` enrichi : **temps moyen de révision** (somme `StudySession.duration_seconds` / élèves), **taux de réussite global** (Σ `cards_correct` / Σ `cards_reviewed`) et **avancement par élève** (`StudentStatSchema` : devoirs terminés, score moyen, minutes de révision, réussite).
* **Agrégats SQL bornés** : +3 requêtes constantes (noms, study group-by user, progress group-by user) — le test de budget (`assert_max_queries`) reste vert, coût indépendant du nombre d'élèves.

### Frontend
* `classService` : `ClassOverview` enrichi (`avg_study_minutes`, `study_success_rate`, `students[]` + type `StudentStat`).
* `TeacherDashboard` (onglet Tableau de bord) : 2 KPI supplémentaires (« Révision moy. », « Réussite révisions ») + **tableau par élève** (devoirs faits, score, temps, réussite).

### Tests
* Backend `test_class_overview_revision_metrics` (temps/réussite/par-élève) + non-régression du budget de requêtes. Suite **242**. vue-tsc clean, **Vitest 40**.

### Suite
* B5 n'était **pas** le dernier item : B1 et B2 avaient été sautés (cf. section suivante).

## [2026-06-15] Compléments B2 / B1 / C1 / A9 (clôture réelle du plan)

À la relecture des cases du plan, **B1** et **B2** n'étaient pas livrés et **C1**/**A9** avaient des cases ouvertes. Bouclés ici :
* **B2** (`feature/teacher-share-binder`) — partage de classeur par référence vérifié (test « élément ajouté après partage visible de l'élève ») + endpoint `GET /groups/binders/:uuid/classes` et UI « Partager à la classe » + badge dans `Binders.vue`.
* **B1** (`feature/teacher-courses`) — dépôt de cours (note) dans un classeur de cours partagé (`POST /classes/:id/course-binder`) ; partage **PDF en lecture seule** étendu en miroir des notes.
* **C1 affichage** (`feature/binder-diagrams-pdfs`) — sections Diagrammes & PDF dans la vue classeur + attache/détache de ces types.
* **A9** (`docs/revision-active-notes`) — vérif cohérence du balisage (self-test sans persistance) ; **correction d'un bug** : l'aide in-app documentait `ordre`/`assoc`/`vf` avec de mauvais séparateurs ; doc utilisateur `docs/revision-active-notes.md`.

### 🎉 Plan de refonte réellement terminé
* Toutes les cases A/B/C du plan `REFACTO_FONCTIONNALITES.md` sont cochées.

## [2026-06-15] Upload PDF réel (feature supplémentaire)

Le module PDF était entièrement **simulé** côté front (données factices, aucun appel à l'API `/pdfs` pourtant réelle). Branché en vrai.

### Backend
* Ajout de `PUT /pdfs/:id` (renommage) : `PDFService.update_pdf` (écriture refusée sur un cours partagé en lecture seule).

### Frontend
* `stores/pdf.ts` réécrit sur l'API réelle : `fetchPdfs`, `uploadPdf` (multipart), `renamePdf`, `removePdf`, `openPdf` (charge le fichier en **blob** via l'instance Axios authentifiée — le stream `/file` est protégé par JWT — puis `URL.createObjectURL`), `closePdf` (révoque l'URL), `setPdfTags`.
* `PDFs.vue` : liste réelle, import, suppression, modale **renommer + tags** (tags via `setTagsForEntity('pdfs', …)`), badge « Cours partagé » (lecture seule, sans actions). `PdfReader.vue` réécrit en visionneuse `<iframe>` (+ ouvrir dans un onglet).
* Retrait des **annotations simulées** (aucun backend) plutôt que de livrer du factice.

### Tests
* Backend `test_pdfs` (upload multipart, listing, renommage, stream fichier, suppression, rejet non-PDF). Suite **250**.
* Front `pdf.spec` (store : fetch/upload/rename/open-blob/delete). vue-tsc clean, **Vitest 50**.

## [2026-06-15] Création des éléments de révision déplacée vers le menu Révisions

Demande : ne plus **créer** les éléments de révision depuis le menu classeur — seulement les **rattacher**. Création déplacée dans `Reviews.vue`.

### Frontend
* `Reviews.vue` : bouton **« Nouvelle carte »** (onglet Flashcards) et **« Créer »** (onglets QCM / V-F / Association / Définition / Ordre) ouvrant `RevisionItemModal` avec `binderId=null` (élément créé non rangé). Message d'état vide mis à jour (« Cliquez sur Créer »).
* `Binders.vue` : retrait des entrées de création du menu « + Ajouter » (ne reste que Sous-dossier, Note, **Élément existant**), du bouton « + Item » et du « Ajouter un item » par deck ; suppression de `RevisionItemModal`, de la modale deck et des fonctions/états associés. Le classeur ne fait plus qu'**organiser** (créer dossiers/notes, rattacher/détacher l'existant).
* Le rattachement d'un élément existant à un classeur reste inchangé (modale « Ajouter un élément existant »).

### Tests
* Aucune régression : vue-tsc clean, **Vitest 50**. Frontend uniquement, pas de migration.

## [2026-06-15] Corrections prof/élève — ensembles partagés & complétion

Deux bugs signalés sur la fonctionnalité professeur :
* **#5 — ensembles de révision d'un classeur partagé invisibles des élèves.** `RevisionService.get_sets` ne filtrait que par `user_id`. Ajout (en miroir des notes/PDF) : le listing global inclut désormais les ensembles des classeurs partagés (racines partagées + descendants) en **lecture seule** (`RevisionSetResponse.read_only`), via `RevisionSetDAO.get_by_binders`. `get_set` marque aussi `read_only` quand l'utilisateur n'est pas propriétaire. Front : `read_only` exposé dans le store ; `Reviews.vue` masque les réglages (renommer/tuning/supprimer) et affiche un badge « Cours partagé » sur ces ensembles (l'étude/lancement reste). `Binders.vue` les montre dans le classeur partagé (détache déjà masqué pour non-propriétaire).
* **#4 — devoir ciblant un ensemble vide marqué « fait ».** `_revision_state` renvoyait `done` (100 %) quand l'ensemble n'a aucun item. Corrigé en `todo` (rien à réviser ⇒ à faire).

### Tests
* Backend `test_shared_revision_sets` (ensemble partagé visible read_only + isolation non-membre ; devoir sur ensemble vide = todo). Suite **252**. vue-tsc clean, Vitest 50. Pas de migration.

### Séparation des rôles prof/élève (#1, #2, #3)
* **Backend** : `ClassResponseSchema.my_role` (rôle de l'utilisateur courant dans la classe), peuplé par `get_my_classes` depuis `members_assoc`.
* **#1/#2** : `TeacherDashboard.loadClasses` ne liste que les classes animées (`my_role ∈ {owner, admin}`) → un élève n'y voit plus la gestion ni les onglets vides (état vide existant réutilisé).
* **#3** : `StudentClassView` (« Mes Devoirs ») gagne un **tableau de bord perso** : série, temps de révision, taux de réussite (depuis `/stats/overview`) et nombre de devoirs terminés — les stats de l'élève.
* Tests : backend `test_my_classes_exposes_role`, suite **253**. vue-tsc clean, Vitest 50.

## [2026-06-16] Élève : voir ses classes (suite séparation des rôles)

Régression de la séparation : après avoir retiré les classes non animées de l'Espace Professeur, un élève ne voyait plus sa classe **nulle part** (la vue Groupes exclut les classes via `is_class`, et `StudentClassView` n'affichait que les devoirs).
* `StudentClassView` : nouvelle section **« Mes classes »** listant les classes où l'utilisateur est inscrit comme élève (`my_role` member/follower), avec un raccourci « Question » (ouvre le fil Q&A de la classe). Le contenu partagé (cours/ensembles) reste accessible via Classeurs / Révisions.
* Frontend uniquement, pas de migration. vue-tsc clean, Vitest 50.

## [2026-06-16] Inversion : « Mes Classes » devient la vue principale

La vue élève est recentrée sur les classes : `StudentClassView` s'intitule désormais **« Mes Classes »** (nav + titre + breadcrumb), avec les **devoirs** en **section interne** (« Mes devoirs ») sous la liste des classes et le tableau de bord perso. Auparavant c'était l'inverse (« Mes Devoirs » avec une section classes). Frontend uniquement, pas de migration. vue-tsc clean, Vitest 50.

## [2026-06-16] Refacto UI — Lot 0 : fondations (tokens + motion + primitives)

Démarrage du refacto UI complet (direction **Soft & Friendly** : neutres *warm*, accents
pastel, arrondis ; animations **subtiles & rapides**). Approche **incrémentale** : couche
centralisée d'abord, migration des vues par lots ensuite. Doc : `docs/design-system.md`.

* **Tokens** : couleurs centralisées en CSS custom properties (`--sh-*`) dans `src/style.css`
  (`:root` clair + `.dark` sombre, palette warm : app `#FAFAF9`/`#17171D`), exposées comme
  tokens Tailwind sémantiques dans `tailwind.config.js` (`bg-app`, `bg-surface(-soft)`,
  `border-line(-soft)`, `text-ink(/-muted/-subtle)`, `primary(/-strong/-soft)`, `accent`,
  `success/warning/danger/info` + `-soft`). Ombres douces (`shadow-soft*`), `prefers-reduced-motion`
  neutralisé globalement. `body` et scrollbars passés sur les tokens.
* **Motion** : `@vueuse/motion` (plugin dans `main.ts`) + presets `useMotionPresets.ts`
  (`fadeUp`, `fadeUpOnce`, `pop`, `listItem(i)`), durées 200-300 ms ease-out.
* **Primitives** `src/components/ui/base/` (typées, sans appel API) : `BaseButton`, `BaseCard`,
  `BaseBadge`, `BaseInput`, `BaseField`, `BaseToggle`, `BaseModal` (HeadlessUI), `BaseEmptyState`,
  `BaseSkeleton`, `StatCard` + barrel `index.ts`.
* Aucune vue migrée à ce stade (effet global limité au fond/typo via tokens). vue-tsc clean,
  `npm run build` OK. Pas de migration backend.

## [2026-06-16] Refacto UI — Lot 1 : shell + Dashboard + Auth (vitrine)

Première migration visible, sur les écrans les plus vus.
* **Shell** `components/layout/AppLayout.vue` : sidebar/header passés sur les tokens
  (`bg-surface`, `border-line`, `text-ink*`, nav active `bg-primary-soft text-primary`),
  toggle dark mode remplacé par `BaseToggle`, bouton login par `BaseButton`. Zen/immersive,
  persistance `sh_theme` et responsive inchangés.
* **Dashboard** `views/Dashboard/Dashboard.vue` : cartes → `BaseCard`, stats → `StatCard`
  (accents sémantiques), boutons → `BaseButton`, heatmap/forecast/objectif/maturité recolorés
  sur tokens (rampe `bg-primary/30→/50→/75→primary`), `quickActions` factorisé, motion
  `fadeUp`/`listItem`. `FocusWidget` conservé (carte vibrante déjà cohérente, indépendante du mode).
* **Auth** `Login.vue` + `Register.vue` : `BaseCard`/`BaseField`/`BaseInput`/`BaseButton`,
  icônes Lucide (Mail/Lock/User), alertes en `danger-soft`, halos de fond en `primary`/`accent`.
* vue-tsc clean, `npm run build` OK, Vitest 50. Pas de migration backend.

---

## [2026-06-21] Refacto UI — Lots T / S0 / S1 / S2 (cœur) + correctif ensembles partagés

Consolidation et sauvegarde du chantier de refonte structurelle resté en working tree
(build + tests verts mais non commité). Découpé en commits cohérents sur
`feature/ui-refactor-s0` ; aucun push.

* **Correctif backend (`revision_service.py`)** : un élève qui révise un **ensemble
  partagé** (cours) ne modifie plus l'échéancier SM-2 du propriétaire. L'état par item
  (`next_review`/`interval`/`ease`) reste celui du prof ; l'élève voit tous les items
  (`get_by_set`) et seule sa `StudySession` est enregistrée. Couvre étude SM-2, QCM typés
  et autres types. +3 tests (`test_shared_revision_sets.py`).
* **Lot T — re-theming** : direction visuelle « White/Pink × Material épuré » (primaire
  Pink 400 `#F06292`, `danger` redevient rouge distinct). Tokens (`style.css` +
  `tailwind.config.js`), primitives `ui/base/` (Button/Card/Modal) et composants `ui/*`
  (NotificationBell, PomodoroTimer, SearchModal, TagSelector). `docs/design-system.md` MAJ.
* **Lot S0 — socle structurel** : primitives présentationnelles `PageContainer`,
  `PageHeader`, `Tabs`, `ListRow`, `SplitView` (+ tests `web/tests/ui/`). Routing 5 sections
  canoniques (accueil/bibliotheque/reviser/classes/planning) + redirects des anciennes routes
  liste, routes feuilles préservées. Nav `AppLayout` 5 sections + Communauté (actif par
  préfixe). `ClassesLanding` (onglets Enseignant/Élève/Groupes). Anti-stranding temporaire
  « examen blanc » (Reviews).
* **Lot S1 — Accueil** : `views/Home/Accueil.vue` (fusion Dashboard + Focus, action-first) —
  hero + CTA « Continuer à réviser », file `focus.items`, panneau « Aujourd'hui », progression.
* **Lot S2 (cœur) — Bibliothèque** : `Binders.vue` refondu en `SplitView` (arbre + contenu
  typé en `ListRow`, tokens `cat-*`), `PageHeader` (fil d'Ariane), `Tabs` par type (`?type=`).
  Toutes les features préservées (owner/lecture-seule, clone, attache/détache, partage
  communauté + classe, stats, filtres tags).
* **Lot S2 (feuilles)** : `Notes.vue` et `PDFs.vue` ré-agencés (PageHeader + BaseCard/BaseModal +
  tokens, accents `cat-note`/`cat-pdf`, badge « Cours partagé » préservé) ; `Diagrams.vue` —
  tête `PageHeader` + bascule Visuel/Mermaid + filtres tokenisés, **corps de l'éditeur laissé tel
  quel** (couleurs fonctionnelles en data + canevas SVG). **Restent pour S7** : `NoteEdit` (zen)
  et le corps éditeur de `Diagrams`.
* Vérif : `npm run build` OK (vue-tsc strict), Vitest **66**, backend `test_shared_revision_sets`
  **3** ✅. Pas de migration backend. Branche `feature/ui-refactor-s0` **poussée**.

---

## [2026-06-21] Refacto UI — Lot S3 (cœur) : Réviser

PR #73 (Lots 0/1/T/S0/S1/S2) mergée sur `main` (CI 6 checks verts, dont E2E Playwright).
Enchaînement sur S3 (branche `feature/ui-refactor-s3`).

* **`Reviews.vue`** (route `reviser`) : `PageContainer` + `PageHeader` ; sélecteurs catégories
  (Classiques/IA) et sous-onglets déplacés en `#actions` et **tokenisés** (primary/surface/ink).
* **Bandeau « À réviser maintenant »** branché sur le store `focus` (réutilise le pattern d'`Accueil`) :
  `totalDue`/`lateCount`, CTA **« Tout réviser »** → `focus.startUnifiedReview()` puis route vers
  l'item actif. **Entrée Examen** (`/exam/setup`) intégrée au bandeau ; code anti-stranding S0 retiré.
* **Reste pour S7** : onglet Flashcards en `ListRow` (Étudier/Stats/⋯) et re-skin des corps d'onglets
  IA (feuille blanche/Feynman/quiz) + runners.
* Vérif : `npm run build` OK (vue-tsc strict), Vitest **66** ✅. Aucun changement backend.

---

## [2026-06-21] Refacto UI — Lot S4 (cœur) : Classes (vues élève)

S3 (PR #74) mergé. Enchaînement S4 (branche `feature/ui-refactor-s4`).

* **`StudentClassView.vue`** : wrapper page autonome (`min-h-screen bg-slate-50 p-6`) retiré (monté
  dans `ClassesLanding`) ; sous-en-tête + cartes stats + filtres + liste devoirs migrés en tokens.
  Couleurs de **statut** mappées sémantiquement : done→`success`, late→`danger`, in_progress→`info`,
  todo→neutre (`accentBarClass` ajouté). Q&A tokenisé. Accent sky→`primary`.
* **`GroupsList.vue`** : wrapper page retiré ; cartes en `BaseCard`, modales create/join en
  `BaseModal`/`BaseField`, accent violet/purple→`primary`. Logique (create/join/copy/nav) inchangée.
* **Restent pour S7** : `TeacherDashboard` (1064 l / 136 couleurs brutes), `GroupDetail`,
  `AssignmentDetail`/`AssignmentBuilder` — gros et complexes, migration prudente.
* Vérif : `npm run build` OK (vue-tsc strict), Vitest **66** ✅. Aucun changement backend.

---

## [2026-06-21] Refacto UI — Lot S5 (complet) : Planning

S4 (PR #75) mergé. Enchaînement S5 (branche `feature/ui-refactor-s5`).

* **`PlanningPage.vue`** : `PageContainer` + `PageHeader` ; toggle Semaine/Mois + bouton Aujourd'hui +
  navigation période déplacés en `#actions` et tokenisés. Cartes résumé en `BaseCard`, carte guide
  en dégradé `primary→primary-strong`. Modale de révision anticipée → `BaseModal` (anciennes
  animations custom retirées). Store `planning` inchangé.
* **`WeekCalendar.vue` / `MonthCalendar.vue`** : tokenisés ; couleurs de **charge** mappées
  sémantiquement (`<10`→success, `≤25`→warning, `>25`→danger) ; surbrillance « aujourd'hui »
  indigo→`primary` ; tooltip du mois laissé volontairement sombre.
* **Lot complet** (pas de report S7). Vérif : `npm run build` OK (vue-tsc strict), Vitest **66** ✅.
  Aucun changement backend.

---

## [2026-06-21] Refacto UI — Lot S6 (cœur) : Communauté / Public

S5 (PR #76) mergé. Enchaînement S6 (branche `feature/ui-refactor-s6`).

* **`PublicLayout.vue`** : coquille publique tokenisée (header sticky, nav, footer) ; logo + CTA
  « Espace Personnel » indigo/purple→`primary` (via `BaseButton`) ; bascule thème conservée.
* **`Marketplace/Home.vue`** : landing — hero indigo→`primary`, 6 cartes feature factorisées en
  `v-for` avec accents par tokens (`cat-deck`/`success`/`cat-diagram`/`cat-pdf`/`accent`/`info`),
  bandeau stats `bg-primary`. CTA → `BaseButton`.
* **`Marketplace/Explore.vue`** : barre recherche + filtres + grilles packs/cours en `BaseCard`,
  badges/tags tokenisés, bouton « Suivre » done→`success`. Logique (search/follow/pagination) inchangée.
* **Restent pour S7** : `Marketplace/PackagePreview` et `Notes/PublicNote` (pages de détail).
* Vérif : `npm run build` OK (vue-tsc strict), Vitest **66** ✅. Aucun changement backend.

---

## [2026-06-21] Refacto UI — Lot S7 (slice) : pages publiques de détail

S6 (PR #77) mergé. Slice S7 (branche `feature/ui-refactor-s7`) : finir la section Communauté.

* **`Marketplace/PackagePreview.vue`** : tokenisé (sidebar `BaseCard`, sommaire, bandeau lecture
  seule→`warning`, bouton import→`BaseButton`) ; route post-clone `/binders`→`/bibliotheque`.
* **`Notes/PublicNote.vue`** : chrome tokenisée (méta, lien de partage `BaseButton`, blocs
  contexte→`warning`/définitions→`success`, article, CTA→`primary`). Le HTML généré par
  `renderMarkup` (placeholders QCM/VF/assoc à couleurs fonctionnelles) est **laissé tel quel**.
* `prefers-reduced-motion` déjà présent dans `style.css` (rien à ajouter).
* **Restent (revue visuelle requise)** : `TeacherDashboard`, `GroupDetail`, `AssignmentDetail`/
  `Builder`, `NoteEdit` (zen), corps éditeur `Diagrams`, onglets Reviews (Flashcards/IA) + runners ;
  puis audits dark/AA/responsive/Capacitor.
* Vérif : `npm run build` OK (vue-tsc strict), Vitest **66** ✅. Aucun changement backend.

---

## [2026-06-21] Refacto UI — Lot S7 (suite) : feuilles de détail Classes

S7-slice (PR #78) mergé. Continuation : `GroupDetail` + `AssignmentDetail`.

* **`Groups/GroupDetail.vue`** : page réécrite en tokens (en-tête, 4 onglets Classeurs/Activité/
  Membres/Progression, modale partage) ; violet→`primary`, rôles→`accent`/`info`/`primary`/neutre,
  permissions/scores→`success`/`warning`/`danger`, rangs→`accent`/`warning`. Corrigé
  `/binders/:id`→`/bibliotheque/:id`. Logique (partage/rôles/exclusion/quitter) inchangée.
* **`Classes/AssignmentDetail.vue`** : page réécrite en tokens (en-tête, 4 cartes stats, table de
  progression + notation prof) ; statuts→`success`/`info`/neutre, scores→`success`/`warning`/`danger`,
  accents→`primary`/`accent`. Back→`/classes?tab=teacher`. Notation inchangée.
* Vérif : `npm run build` OK (vue-tsc strict), Vitest **66** ✅. Aucun changement backend.

---

## [2026-06-21] Refacto UI — Lot S7 (suite) : AssignmentBuilder

* **`components/classes/AssignmentBuilder.vue`** : modale de création de devoir réécrite en tokens
  (amber→`primary` pour cohérence avec les autres vues Classes ; slate→tokens ; red→`danger`).
  Logique (composition multi-activités, objectifs, création) inchangée.
* **Arrêt volontaire sur `TeacherDashboard`** (1064 l / 136 couleurs brutes / 6 sous-onglets dont
  analytics) : pas de mapping mécanique propre, plus gros risque visuel du projet → à migrer avec
  **revue visuelle humaine**, comme `NoteEdit` (zen), corps éditeur `Diagrams`, onglets/runners `Reviews`.
* Vérif : `npm run build` OK (vue-tsc strict), Vitest **66** ✅. Aucun changement backend.

---

## [2026-06-21] Refacto UI — Lot S8 : TeacherDashboard (reprise du « reste »)

Reprise de la boucle sur les morceaux reportés (risque visuel assumé, validation a posteriori).

* **`Classes/TeacherDashboard.vue`** : migration complète en tokens sémantiques. Mapping :
  amber/orange **marque** (loaders, icônes de chrome, boutons, onglet actif, bandeau, barre de
  complétion)→`primary` ; amber **statut** (échéance proche, score moyen)→`warning` ; amber
  **gamification** (rang #1 leaderboard, tag « IA »)→`accent` ; vert→`success`, rouge→`danger`,
  bleu **+ indigo** (« déposer un cours », unifié avec son déclencheur)→`info` ; barres de
  progression en cours→`primary`, terminé→`success`. Slate : 900/white→`ink`, 400/500/600→
  `ink-muted`, captions→`ink-subtle` ; fonds page→`app`, panneaux→`surface-soft`, modales→
  `surface`, inputs→`surface-soft` ; bordures→`line`/`line-soft`. `placeholder-slate-400` conservé
  (convention S7). Logique (onglets, CRUD classes/devoirs, analytics, Q&A) **inchangée**.
* **Bug pré-existant corrigé** : classes Tailwind invalides présentes dans `main`
  (`slate-455`, `slate-350`, `slate-105`, `slate-750`, `green-650`, `blue-650`) — vestiges d'un
  remplacement numérique mal ciblé d'une passe antérieure, rendues mortes (aucun style généré).
  Remplacées par des tokens valides ; **règle retenue : jamais de remplacement de fragment numérique**.
* **Restent (revue visuelle requise)** : `NoteEdit` (zen), corps éditeur `Diagrams` (couleurs nœuds
  en data), onglets/runners `Reviews` ; puis audits dark/AA/responsive 375 px/Capacitor.
* Vérif : `npm run build` OK (vue-tsc strict), Vitest **66** ✅. Aucun changement backend.

---

## [2026-06-21] Refacto UI — Lot S8 (suite) : NoteEdit (template, modes préservés)

* **`Notes/NoteEdit.vue`** (2693 l) : **seul le `<template>` (l. 1-1016) est migré** en tokens.
  Famille de marque de l'éditeur **indigo→`primary`** ; emerald→`success`, rose→`danger`,
  amber→`warning`, purple→`accent`, blue→`info` ; slate→`ink`/`surface`/`line` (fonds doux→
  `*-soft`). Migration par **tokens complets** (script jeté, jamais de fragment numérique — cf.
  classes mortes corrigées en S8/Teacher).
* **Laissés intacts (volontaire)** : tout le `<script>` (l. 1018-2582) qui assemble des **couleurs
  fonctionnelles pilotées par données** (échelle de difficulté SM-2 bleu→rose, variantes de modale
  `iconBg`/`confirmBg`) — même règle que le HTML de rendu de `PublicNote` et les couleurs de nœuds
  de `Diagrams`. **Scrims de modale `bg-slate-900/50|60`** conservés (overlay sombre translucide,
  identique en clair/sombre). `placeholder-slate-*` conservés (convention S7).
* Mode édition plein écran (font-mono, l. 52-384) et bascule Lecture/Révision Active : chrome
  tokenisée, **comportement/layout inchangés**.
* **Restent (revue visuelle requise)** : corps éditeur `Diagrams` (couleurs nœuds en data),
  onglets/runners `Reviews` ; puis audits dark/AA/responsive 375 px/Capacitor.
* Vérif : `npm run build` OK (vue-tsc strict), Vitest **66** ✅. Aucun changement backend.

---

## [2026-06-21] Refacto UI — Lot S8 (suite) : Diagrams (chrome, canevas préservé)

* **`Diagrams/Diagrams.vue`** (926 l) : **seul le `<template>` (l. 1-496) est migré** en tokens.
  Marque éditeur **indigo→`primary`** ; emerald→`success`, amber→`warning`, **rose→`danger`**
  (boutons supprimer / erreurs) ; slate→`ink`/`surface`/`line`. Sélection de nœud `ring-indigo`→
  `ring-primary`, `ring-offset-slate-900`→`ring-offset-surface`.
* **Canevas SVG & données préservés (volontaire)** : palette de nœuds `const colors` (dans le
  `<script>`, hors périmètre), bindings `node.color`/`color.bg`, **masques d'occlusion**
  (`fill-rose-*`/`stroke-rose-*` — rendu de révision, jamais mappés), connecteurs `#6366f1` et
  inline-styles hex (attributs SVG, non-classes), grille (`text-slate-200/50`). Règle : on ne mappe
  **jamais** `fill-`/`stroke-`/`decoration-` ici. Scrims `bg-slate-900/<op>` et `placeholder-slate-*`
  conservés.
* **Restent (revue visuelle requise)** : onglets/runners `Reviews` (Flashcards `ListRow` + corps IA) ;
  puis audits dark/AA/responsive 375 px/Capacitor.
* Vérif : `npm run build` OK (vue-tsc strict), Vitest **66** ✅. Aucun changement backend.

---

## [2026-06-21] Refacto UI — Lot S8 (suite) : Reviews — hub

* **`Reviews/Reviews.vue`** (1773 l) : **`<template>` (l. 1-945) migré** en tokens. Marque
  **indigo→`primary`** ; emerald→`success`, rose→`danger`, amber→`warning`, blue/sky→`info`,
  violet/purple→`accent` ; slate→`ink`/`surface`/`line`. Les ternaires de **statut sémantique**
  (échéance>0→`warning`/`success`, correct→`success`/erreur→`danger`, statut génération→`danger`/
  normal) sont tokenisés (ce ne sont pas des palettes de données). Corrige 2 résidus : classe morte
  `bg-indigo-55`→`bg-primary-soft`, `accent-indigo-600`→`accent-primary` (curseur de réglage).
* **Laissé intact** : `<script>` (l. 947+), notamment les constructeurs de classes de **surlignage
  correct/incorrect** (blurting/feynman, l. 1442) — rendu piloté par données. Scrims + placeholders
  conservés.
* **Restent (revue visuelle requise)** : runners/stats `Reviews` (`RevisionStudy`, `QcmRun`,
  `RevisionBinderStats`/`SetStats`, `RevisionItemModal`, `AnkiImportModal`, `LearningCurve`) ;
  puis audits dark/AA/responsive 375 px/Capacitor.
* Vérif : `npm run build` OK (vue-tsc strict), Vitest **66** ✅. Aucun changement backend.

---

## [2026-06-21] Refacto UI — Lot S8 (fin code) : Reviews — runners/stats/modales

* Migration `<template>` (tokens) de **7 fichiers du module Révision** : `RevisionStudy`, `QcmRun`,
  `RevisionBinderStats`, `RevisionSetStats`, `RevisionItemModal`, `AnkiImportModal`, `LearningCurve`.
  Marque **indigo→`primary`** ; emerald→`success`, rose→`danger`, amber→`warning`, blue→`info` ;
  slate→`ink`/`surface`/`line`. Détails : CTA « Suivant » du runner (fond sombre neutre)→`primary` ;
  cases à cocher `accent-indigo/emerald-600`→`accent-primary`/`accent-success` ; scrim de modale
  `bg-slate-950/40` **préservé**.
* **Fin de la migration mécanique S8.** Tout le périmètre « gros/complexes » est tokenisé
  (TeacherDashboard, NoteEdit, Diagrams, Reviews hub + runners). **Restent uniquement les audits
  transverses NON automatisables** (revue humaine) : dark mode, contraste AA des pastels, responsive
  375 px, smoke test Capacitor.
* Vérif : `npm run build` OK (vue-tsc strict), Vitest **66** ✅. Aucun changement backend.

---

## [2026-06-21] Refacto UI — Lot S8 (extension) : Decks + StudyDeck (reliquats S3)

* Reliquats de couleurs brutes repérés en cartographiant Reviews : **`Decks/Decks.vue`** (~186) et
  **`Decks/StudyDeck.vue`** (~93) n'avaient été migrés que partiellement en S3. Templates migrés en
  tokens : marque **indigo→`primary`** ; emerald→`success`, slate→`ink`/`surface`/`line` ;
  utilitaires `accent-indigo-*` (checkbox/range)→`accent-primary`.
* **Préservé** : boutons de notation **SM-2** de `StudyDeck` (`ratingButtons`, `<script>` l. 161 —
  échelle 0-5 rouge→vert pilotée par données, `:class="score.class"`), comme l'échelle SM-2 de
  `NoteEdit`. Scrims + `placeholder-*` conservés.
* Vérif : `npm run build` OK (vue-tsc strict), Vitest **66** ✅. Aucun changement backend.

---

## [2026-06-21] Refacto UI — Lot S8 (couverture app) : modules jamais migrés

Un balayage repo-wide a révélé des **modules entiers restés à l'ancien thème** (indigo/emerald/rose
bruts dans les templates), hors plan S0→S7. Migration en tokens, **une sous-PR par module**
(templates seuls ; données/`<script>`/canevas/scrims préservés ; indigo→`primary`, emerald→
`success`, rose→`danger`, amber→`warning`, blue/sky→`info`, violet/purple→`accent`).

* **Module Notes-runners** : `NoteQuiz` (566), `NoteEvaluation` (264), `Blurting` (274).
  Spinner `NoteQuiz` corrigé (`border-primary/30 border-t-primary`) ; `dark:hover:bg-slate-700`
  (nuance hors set) → `dark:hover:bg-line`. Vérif : build OK, Vitest **66** ✅.
* **Module Exam** : `ExamSession` (437), `ExamResults` (233), `ExamSetup` (190). CTA sombre de
  `ExamSession`→`primary` ; hovers slate hors set (`650`, `700/50`)→`*-line`. Vérif : build OK,
  Vitest **66** ✅.
* **Module Focus** : `FocusPage` (188), `FocusWidget` (90). SVG de marque du widget→
  `fill-primary`/`stroke-primary`. Tooltip sombre délibéré `bg-slate-950` de `FocusPage` laissé tel
  quel (pas de token « surface inversée »). Vérif : build OK, Vitest **66** ✅.
* **Divers** : `PdfReader` (37), `Login` (65), `Register` (72), `MonthCalendar` (90),
  `AppLayout` (194). Nuance morte `slate-855`→`surface-soft` (MonthCalendar). Vérif : build OK,
  Vitest **66** ✅.
* **✅ Couverture app complète.** Balayage repo-wide final : **tous les templates `.vue` sont
  tokenisés**, à l'exception **volontaire** des scrims de modale (`bg-slate-9x0/<op>`), des masques
  d'occlusion `Diagrams` (`fill-rose-*`), du tooltip inversé `FocusPage` (`bg-slate-950`), et des
  couleurs **pilotées par données / `<script>` / canevas** (échelles SM-2, surlignage correct/
  incorrect, palette de nœuds) — toutes préservées intentionnellement.
* **Reste uniquement** : audits transverses NON automatisables (revue humaine) — dark mode,
  contraste AA des pastels, responsive 375 px, smoke test Capacitor.

---

## [2026-06-24] Application bureau — démarrage (Electron)

Nouvelle coque **bureau** (`desktop/`) qui réutilise le build web (`web/`) sans
réécriture, sur le modèle de la coque mobile Capacitor. Objectif : déploiement bureau
rapide, un seul codebase front.

* **`desktop/`** : `src/main.ts` (BrowserWindow sécurisée — `contextIsolation`/`sandbox`,
  liens externes → `shell.openExternal`), `src/preload.ts` (pont `window.studyhub`
  `{ isDesktop, version }`), `electron-builder.yml` (cibles Linux AppImage+deb / Windows
  NSIS / macOS dmg), icône dérivée de `web/public/favicon.svg`.
* **Dev** : serveur Vite (`localhost:5173`, HMR). **Prod** : `web/dist` copié hors asar
  (`extraResources`) et servi par `electron-serve` sous `app://-` (import dynamique ESM
  depuis le main CJS).
* **3 adaptations** : router en `createWebHashHistory` si `VITE_DESKTOP=true`
  (`web/src/router/index.ts`, web inchangé) ; `usePlatform()` expose `isDesktop` ;
  `VITE_API_BASE_URL` pointe le backend prod (pas de Nginx en desktop).
* **Backend** : origine `app://-` ajoutée à la whitelist `CORS_ALLOWED_ORIGINS`
  (`backend/app/__init__.py`).
* **Docs** : `docs/desktop.md`, skill `desktop-build`, carte projet `CLAUDE.md`.
* **Reste** : icône définitive, signature/notarisation macOS + signature Windows,
  build Win/mac en CI. Vérifier l'`Origin` réelle au 1er lancement packagé.

---

## [2026-06-24] Application mobile — matérialisation de la coque Capacitor (Android)

Les plugins `@capacitor/*` étaient déjà dépendances de `web/` (et `usePlatform()` les
utilisait), mais aucune coque native n'existait : pas de CLI, pas de `capacitor.config`,
pas de projet natif. Cette étape **matérialise** la coque mobile, sur le modèle du
desktop (réutilisation du build web, un seul codebase front).

* **Enracinement dans `web/`** (choix idiomatique Capacitor : config + CLI + plugins
  dans le même package). Ajout devDeps : `@capacitor/cli`, `@capacitor/android`,
  `cross-env` ; alignement de tout l'écosystème Capacitor en **8.4.1**.
* **`web/capacitor.config.ts`** : appId `com.studyhub.app`, `webDir: 'dist'`,
  `androidScheme: 'https'`. Projet natif généré dans **`web/android`** (`cap add` +
  `cap sync` ; 4 plugins détectés : filesystem, haptics, local-notifications,
  preferences). `cap doctor` ✅.
* **Différence vs desktop** : servi en `https://localhost` (vraie origine HTTP) →
  history HTML5 conservée (**pas de hash**, aucun changement de router). API pointée
  vers le backend prod via `build:mobile` (pas de Nginx).
* **Backend** : origines `https://localhost` (Android) et `capacitor://localhost` (iOS)
  ajoutées à la whitelist `CORS_ALLOWED_ORIGINS`.
* **Scripts `web/`** : `build:mobile`, `cap:sync`, `cap:android`.
* **Docs** : `docs/mobile.md`, skill `mobile-build` corrigé (Cap 6→8, emplacement réel),
  carte projet + stack `CLAUDE.md` (Cap 6→8).
* **Différé** : compilation APK (SDK Android / CI), icône & splash, plateforme iOS
  (Mac), tests émulateur/appareil. Vérifier les origines CORS réelles au 1er run natif.

---

## [2026-06-24] Fix — un devoir terminé ne passait pas en « fait »

**Symptôme** : un élève termine un devoir (QCM / examen blanc / blurting notamment) mais
le statut reste « à faire ».

**Cause** : le statut « fait » est stocké et n'est mis à jour que par un recalcul
(`recompute_*`). Or ce recalcul n'était déclenché que (1) à la révision d'une carte
flashcard et (2) par le bouton manuel « vérifier » (`submit_task`). **Aucun hook** sur
la complétion d'un quiz/examen/blurting, et `get_my_assignments` lisait le statut
**stocké sans recalculer**. La correspondance des clés `ref_id`↔modules était correcte
(ce n'était pas un bug de mapping).

**Correctif** (`backend/app/services/class_service.py`) :
- `get_my_assignments` **recalcule à la lecture** chaque devoir depuis l'état réel des
  modules (un seul commit après la boucle) → couvre tous les types de tâches d'un coup,
  sans dépendre d'une validation manuelle ni d'un hook par module.
- Effet de bord révélé puis corrigé : `_flashcards_state` marquait un **classeur vide**
  comme « fait » — incohérent avec les ensembles de révision vides (#4). Aligné sur le
  principe « cible vide ⇒ à faire » pour éviter qu'un devoir flashcards sur classeur vide
  passe « fait » au simple affichage.
- Test de non-régression : `test_quiz_task_marked_done_on_read_without_manual_submit`
  (QCM complété ⇒ devoir « fait » sans `submit`). Suite backend complète verte.

---

## [2026-06-25] Fix #2 — la copie/sauvegarde de note échappait le Markdown en HTML

**Symptôme** : en copiant (ou simplement en sauvegardant) une note, certains caractères
étaient transformés en entités HTML (`>` → `&gt;`, `<` → `&lt;`), cassant l'affichage —
notamment les citations Markdown (`> …`) et les comparaisons (`a > b`).

**Cause** : les notes sont stockées en **Markdown brut** (l'éditeur est un textarea
Markdown) et rendues côté client via `marked` + `DOMPurify` (vraie barrière XSS, au
rendu). Or `note_service` faisait passer ce Markdown dans `sanitize_html` (bleach), un
sanitizer **HTML** qui échappe la ponctuation structurelle du Markdown. La copie
rendait le symptôme visible car elle ré-assainissait un contenu déjà stocké.

**Correctif** (`backend/app/utils/html_sanitizer.py`) : `sanitize_html` ne fait plus
d'échappement HTML. Défense en profondeur ciblée seulement : suppression des blocs/balises
exécutables (`script`, `iframe`, `style`, `object`…), des gestionnaires `on*` inline et
des URIs `javascript:`/`data:`/`vbscript:`. La ponctuation Markdown (`>`, `<`, `&`) est
laissée intacte. La sanitisation XSS finale reste assurée par `DOMPurify` au rendu.

**Tests** : `tests/test_notes.py` réécrit — vecteurs XSS toujours neutralisés, + 2
régressions (`test_note_preserves_markdown_punctuation`,
`test_copy_note_does_not_double_escape`). Suite backend complète verte.
