# Revue technique phase 2 — Performance et scalabilité

> Phase 2 (revue technique, **lecture seule**). Chaque constat : identifiant, emplacement
> `fichier:ligne`, description factuelle, impact concret, gravité **S1 (critique) → S4
> (cosmétique)**, effort **XS/S/M/L**, piste de correction **non appliquée**. Généré le
> 2026-08-23.
>
> **Note de méthode** — `docs/design-system.md`, `docs/ui-redesign-plan.md` et
> `docs/performance-audit.md` sont traités comme non acquis pour cette phase (arbitrage
> phase 1, `ETAT.md`). Un audit de performance antérieur existe déjà
> (`docs/performance-audit.md`, 2026-06-13, PR #10→#18) et revendique la plupart de ses
> constats résolus — il n'a **pas** été pris pour argent comptant : les points pertinents ont
> été revérifiés dans le code réel. Un point qu'il avait explicitement **reporté** (non
> corrigé) est reconfirmé encore ouvert ci-dessous (PERF-08).
>
> La stack réelle (cartographie phase 0) n'a pas Tiptap/Mermaid/PDF.js — les points du prompt
> de démarrage qui en parlaient ont été adaptés à ce qui existe vraiment : `marked` + KaTeX
> côté rendu, pas de worker PDF.js.

---

## Constats

### PERF-01 — Streak calculé en Python sur l'historique complet, au lieu d'un agrégat SQL
**Emplacement** : `backend/app/services/stats_service.py:134-159` (`_calculate_streak`)

**Description** : charge *tous* les `StudySession` (toutes colonnes) des 365 derniers jours
via `get_sessions()` (pas de projection), matérialise chaque ligne en objet ORM, puis
reconstruit un `set` de dates en Python pour compter le streak. Le même besoin est déjà résolu
proprement ailleurs dans le code : `engagement_service.py:99-132` (`_streaks`, leaderboard de
classe) fait la même chose avec une requête `SELECT DISTINCT date(created_at) ...` — un seul
aller-retour, aucune matérialisation de ligne complète.

**Impact** : pour un utilisateur assidu (plusieurs sessions/jour sur un an), des centaines de
lignes complètes (durée, cartes revues, grade…) sont rapatriées et désérialisées en ORM pour
n'en extraire qu'une date. Coût réseau + mémoire + CPU applicatif superflu, répété à chaque
appel.

**Atténuant** : la route `/api/v1/stats/overview` est cachée 300 s (`cache_route`,
`backend/app/utils/cache.py:8`) et invalidée uniquement à l'écriture d'une session
(`study_session.py` listeners `after_insert/update/delete`) — donc pas recalculé à chaque
chargement de dashboard, mais bien à chaque nouvelle session d'étude (le moment le plus
fréquent).

**Gravité** : S3. **Effort** : S.

**Piste** : remplacer par le même motif que `engagement_service._streaks` — une requête
`func.date(created_at)` + `.distinct()`, sans charger les colonnes inutiles.

---

### PERF-02 — Stats de deck calculées en itérant toutes les cartes en Python
**Emplacement** : `backend/app/services/stats_service.py:94-132` (`get_deck_stats`)

**Description** : `cards = deck.cards` charge la relation complète (toutes colonnes de
toutes les flashcards du deck), puis `retention_rate`, `next_review` et `cards_to_review` sont
calculés par des boucles/`sum`/`min` Python sur cette liste, alors que ce sont trois agrégats
(`COUNT`, `MIN`, `COUNT FILTER`) exprimables en une seule requête SQL group-by/agrégat sur
`flashcards`, qui bénéficierait de l'index déjà présent `ix_flashcards_deck_id_next_review`
(`backend/app/models/flashcard.py:14`).

**Impact** : pour un deck volumineux (import massif, cours complet), chaque appel matérialise
l'intégralité des cartes (texte recto/verso, JSON `payload`) juste pour compter/dater. Même
atténuant Redis que PERF-01 (`/api/v1/stats/decks/{id}` caché 300 s,
`backend/app/api/v1/stats.py:66`).

**Gravité** : S3. **Effort** : S.

**Piste** : requête agrégée unique (`COUNT`, `MIN(next_review)`, `COUNT(CASE WHEN
next_review <= :now)`) sur `flashcards` filtrée par `deck_id`, sans charger les lignes.

---

### PERF-03 — Chemin de notation d'une carte (SM-2) : deux commits + cascade synchrone non bornée
**Emplacement** : `backend/app/services/flashcard_service.py:190-234` (`review_card`) et
`backend/app/services/class_service.py:889-929` (`trigger_assignment_progress_update`)

**Description** : `review_card` — appelée à **chaque carte notée**, l'action la plus répétée
de toute l'application (dizaines de fois par session de révision) — effectue :
1. `flashcard_dao.update(card)` → commit implicite (`BaseDAO.update`, `backend/app/dao/base_dao.py:29-31`, commit systématique) ;
2. `db.add(study_session); db.commit()` → un **second** commit séparé pour la même action utilisateur ;
3. `trigger_assignment_progress_update(...)` exécutée en synchrone dans la requête HTTP, qui :
   - remonte la hiérarchie des classeurs parent par parent avec une requête `db_session.get(Binder, ...)` **par niveau** (`class_service.py:903-908`, boucle `while`) ;
   - puis, pour chaque devoir concerné, appelle `recompute_assignment_for_user` (`class_service.py:927-928`) — coût non borné par le nombre de devoirs actifs de l'élève sur ce classeur.

**Impact** : latence doublée au minimum (deux allers-retours transactionnels au lieu d'un) sur
le chemin le plus chaud de l'appli, plus une cascade de requêtes séquentielles proportionnelle
à la profondeur de classeurs × nombre de devoirs actifs, exécutée en bloquant la réponse HTTP à
l'élève qui vient de répondre à une carte. Sous charge (plusieurs élèves d'une classe en
révision simultanée), c'est le point qui scale le moins bien.

**Confirmation croisée** : ce constat recoupe un point **explicitement reporté** dans l'audit
antérieur (`docs/performance-audit.md` §4.5, item A3 : « progression de classeur — récursion
N+1 → CTE récursive / agrégat unique », marqué « Reporté (PR dédiée, plus risquée) », jamais
traité). Ce n'est donc pas une régression récente : c'est une dette connue depuis juin 2026,
toujours ouverte. Le même moteur (`recompute_assignment_for_user`) est aussi invoqué en boucle
séquentielle (une requête `get_by_id` groupe + une requête assignments par appartenance) dans
`class_service.py:456-499` (liste des devoirs d'un élève).

**Gravité** : S2. **Effort** : M (toucher au commit unique nécessite une variante non
committante du DAO ou une transaction explicite au niveau service ; la cascade de progression
nécessite l'agrégat/CTE déjà identifié en juin).

**Piste** : (a) un seul commit pour update-carte + insertion-session (DAO en mode
« flush sans commit » + commit au niveau service) ; (b) remplacer la remontée `while` +
requêtes par devoir par une requête ensembliste (CTE récursive Postgres sur `binders`, ou
préchargement de toute la chaîne d'ancêtres en une fois) comme déjà recommandé en juin.

---

### PERF-04 — File de cartes à réviser non bornée (pas de `LIMIT`/pagination)
**Emplacement** : `backend/app/dao/flashcard_dao.py:75-84` (`get_cards_to_study`), appelée
depuis `backend/app/services/flashcard_service.py:112-114` (`get_study_cards`)

**Description** : la requête qui construit la file de révision d'un deck (`next_review <=
now()`) n'a ni `LIMIT` ni offset — elle renvoie **toutes** les cartes dues, quel que soit leur
nombre, puis le service boucle en Python dessus pour filtrer par type (`original_text`
startswith, `{{vf::}}`, `{{qcm::}}`…).

**Impact** : un deck volumineux jamais révisé (import massif, reprise après une longue pause)
peut avoir des milliers de cartes dues simultanément → une seule requête HTTP renvoie
l'intégralité du contenu texte de toutes ces cartes en une réponse, avant même que
l'utilisateur en révise une seule. Pic mémoire côté serveur et poids de réponse imprévisible.

**Gravité** : S2. **Effort** : S.

**Piste** : plafonner à une taille de session raisonnable côté DAO (`LIMIT`, ex. 50-100
cartes), avec un ordre déterministe (`next_review ASC`) pour prioriser les plus en retard.

---

### PERF-05 — Rendu Markdown+LaTeX de la note relancé en entier à chaque frappe, sans mémoïsation
**Emplacement** : `web/src/views/Notes/NoteEdit.vue:381,562` (appels dans le template) et
`web/src/views/Notes/NoteEdit.vue:1640-1671` (`renderMarkup`)

**Description** : `renderMarkup(noteBody)` est appelé **directement dans le template**
(`v-dompurify-html="renderMarkup(noteBody)"`), pas via un `computed()`. Vue ré-exécute donc
cette fonction à **chaque cycle de rendu du composant** (pas seulement quand `noteBody`
change), soit typiquement à chaque frappe dans l'éditeur. La fonction :
1. fait plusieurs passes `String.replace` par regex sur le texte **entier** de la note ;
2. appelle `katex.renderToString(...)` **de façon synchrone, bloquante**, pour **chaque**
   formule `$$...$$` et `$...$` trouvée dans tout le document — y compris les formules
   éloignées du curseur et non modifiées par la frappe en cours ;
3. sanitise le résultat via `v-dompurify-html`.

**Impact** : sur une note longue et riche en LaTeX (cas d'usage central du produit — rédaction
scientifique), chaque caractère tapé déclenche un re-parsing complet + un re-rendu KaTeX de
*toutes* les formules du document sur le thread principal, sans debounce ni cache par formule.
C'est directement le point « rendu bloquant le thread principal » identifié dans le brief de
phase 2, et il touche le parcours desktop le plus utilisé (rédaction longue session). Risque de
lag d'saisie perceptible proportionnel au nombre de formules × longueur du document.

**Gravité** : S1. **Effort** : M.

**Piste** : (a) passer par un `computed(() => renderMarkup(noteBody.value))` mémoïsé pour
éviter les recalculs hors changement réel de `noteBody` ; (b) au-delà, mémoïser le rendu KaTeX
par formule (cache `Map<string, string>` sur le texte de la formule, invalidé seulement si la
formule elle-même change) pour éviter de re-rendre des formules inchangées ; (c) envisager un
debounce sur la frappe avant re-rendu si (a)+(b) ne suffisent pas.

---

### PERF-06 — Appels Gemini synchrones et bloquants dans la requête HTTP pour flashcards/quiz, incohérent avec le reste
**Emplacement** : `backend/app/api/v1/flashcards.py:23`, `backend/app/api/v1/quizzes.py:29`
(instanciation directe d'`AIService()` au niveau route/service, sans passage par
`app/tasks.py`) — à comparer à `backend/app/api/v1/blurting.py`,
`backend/app/api/v1/feynman.py`, `backend/app/api/v1/classes.py`,
`backend/app/api/v1/evaluations.py` qui dispatchent via Celery
(`.delay`/`apply_async`, `app/utils/task_dispatch.py`).

**Description** : chaque appel HTTP à Gemini dans `ai_service.py` a un timeout de 90 s (`app/
services/ai_service.py:134,260,355,578,737`, 60 s ligne 813) et est effectué avec
`urllib.request.urlopen` **synchrone**. La génération de flashcards et de quiz appelle
`AIService` directement dans le service/route, donc dans le worker WSGI qui traite la requête
— alors que le projet dispose déjà de Celery+Redis et l'utilise pour d'autres fonctionnalités
IA équivalentes (blurting, feynman, insights de classe).

**Impact** : un worker Flask synchrone (gunicorn) reste bloqué jusqu'à 90 s par génération de
flashcards/quiz. Sous charge modérée (plusieurs utilisateurs qui génèrent des flashcards en
même temps), le pool de workers peut s'épuiser et bloquer *tout le reste du trafic* (y compris
les endpoints qui n'ont rien à voir avec l'IA) — scénario de dégradation en cascade classique
d'un serveur synchrone sans isolation des tâches longues.

**Gravité** : S2. **Effort** : M.

**Piste** : aligner flashcards/quiz sur le même motif Celery que blurting/feynman — dispatcher
la génération en tâche asynchrone, endpoint de polling ou webhook/SSE pour le résultat, comme
déjà fait ailleurs dans la même base de code.

---

### PERF-07 — Chunk KaTeX de 1,21 Mo (393 Ko gzip) chargé y compris par les visiteurs anonymes d'une note publique
**Emplacement** : `web/vite.config.ts` (aucune config de chunking manuel), mesuré via
`npm run build` le 2026-08-23 → `dist/assets/katex.min-*.js` : **1 214,21 Ko brut / 393,36 Ko
gzip**, à comparer au chunk principal `index-*.js` (224,51 Ko / 85,14 Ko gzip). Import statique
dans `web/src/views/Notes/NoteEdit.vue:1141` et `web/src/views/Notes/PublicNote.vue`.

**Description** : le découpage par route (33 `import()` dynamiques dans `web/src/router/
index.ts`, aucune vue importée statiquement) fonctionne correctement — KaTeX n'est **pas**
présent dans le chunk principal, comme le supposait le prompt de démarrage. Il forme son propre
chunk isolé, chargé uniquement quand `NoteEdit` ou `PublicNote` sont visités. Le problème n'est
pas le découpage mais la **taille du chunk lui-même** : `docs/ENVIRONNEMENT.md:82` avait déjà
relevé l'avertissement Vite « bundle > 500 kB », confirmé ici avec la mesure précise.

**Impact** : `PublicNote.vue` sert les pages de **partage public** — le point d'entrée le plus
susceptible d'être visité par un inconnu sur mobile via un lien partagé, sans avoir de compte
ni de motivation forte à attendre. 393 Ko gzip (avant décompression/parsing/exécution JS) sur
ce chemin précis est un coût direct sur le taux de rebond d'un lien partagé, en particulier sur
réseau mobile ou appareil d'entrée de gamme (contrainte déjà posée pour la phase 3 : « 60 fps
sur Android milieu de gamme »).

**Gravité** : S3. **Effort** : L (dépend d'une bibliothèque tierce — pas de fix mécanique
local ; nécessite d'évaluer un sous-ensemble KaTeX plus léger ou un rendu côté serveur pour les
pages publiques).

**Piste** : pour `PublicNote.vue` spécifiquement (lecture seule, pas d'édition), envisager un
rendu KaTeX précalculé côté serveur au moment du partage (HTML statique stocké), évitant de
livrer la bibliothèque JS entière à un lecteur anonyme qui ne fait que lire.

---

## Points vérifiés sans anomalie

- **Index** : `ix_flashcards_deck_id_next_review` (`deck_id`, `next_review`) et
  `ix_study_sessions_user_id_created_at` (`user_id`, `created_at`) existent et couvrent
  exactement les filtres utilisés par les requêtes de révision et de heatmap
  (`backend/app/models/flashcard.py:14`, `backend/app/models/study_session.py:9`). Aucun index
  manquant identifié sur ces deux tables pour les accès actuels.
- **Découpage par route (frontend)** : chargement paresseux effectif sur toutes les vues
  (`web/src/router/index.ts`, 33 `import()`, 0 import statique de vue).
- **Agrégation du dashboard** : `get_dashboard_stats` (`backend/app/services/
  stats_service.py:161-259`) calcule KPIs, répartition de maturité et prévision à 7 jours via
  des requêtes `GROUP BY`/`COUNT` SQL, pas de boucle Python sur les cartes — contraste net avec
  PERF-01/02 dans le même fichier.
- **Cache Redis sur les stats** : `@cache_route(timeout=300)` posé sur les 4 routes de
  `stats.py`, invalidation ciblée par utilisateur (et deck) à l'écriture d'une session
  (`invalidate_stats_cache`, `backend/app/utils/cache.py:58-64`) — atténue directement PERF-01
  et PERF-02.

---

## Résumé

| Gravité | Nombre |
|---|---|
| S1 | 1 (PERF-05) |
| S2 | 3 (PERF-03, PERF-04, PERF-06) |
| S3 | 3 (PERF-01, PERF-02, PERF-07) |
| S4 | 0 |

Mesure de bundle la plus significative : chunk `katex.min` **1,21 Mo brut / 393 Ko gzip**
(PERF-07), isolé du chunk principal mais chargé jusque sur les pages de partage public
anonymes.
