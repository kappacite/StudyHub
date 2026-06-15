# REFACTO_FONCTIONNALITES.md — Plan d'implémentation StudyHub

> Plan de suivi étape par étape de la refonte **Révision / Professeur / UI**.
> Document vivant : cocher les cases au fur et à mesure et tenir le **Journal d'avancement** (§5).

## Légende des statuts
- ✅ **Fait** — déjà en place dans le code.
- 🟡 **Partiel** — existe mais à compléter / adapter.
- ⬜ **À faire** — non implémenté.
- ♻️ **À refondre** — existe mais doit être retravaillé suite à une décision d'archi.

## Conventions transverses (rappel AGENTS.md)
- **Commits** : Conventional Commits (`feat(...)`, `fix(...)`, `refactor(...)`, `test(...)`, `docs(...)`). Un commit par étape cohérente.
- **Branches** : `feature/<sujet>` à partir de `main` à jour. 1 sous-partie ≈ 1 PR (sauf socle).
- **PR** : description claire, checklist AGENTS.md §13, lien vers la sous-partie de ce plan.
- **CI obligatoire (déjà en place, doit rester verte)** :
  - `Backend · tests & coverage` (coverage ≥ 80 %)
  - `Backend · tests (PostgreSQL)`
  - `Backend · migrations (PostgreSQL)` — **garde anti-drift** : tout changement de modèle ⇒ migration Alembic additive + idempotente, sinon échec.
  - `Frontend · typecheck & build` (`vue-tsc -b`)
  - `Frontend · unit tests (Vitest)`
  - `Frontend · E2E (Playwright)`
- **Migrations** : additives, idempotentes (guard `inspector`), compatibles SQLite **et** PostgreSQL (`batch_alter_table`). Tester `flask db upgrade` + probe de drift (ignorer les faux positifs GIN `*_search_idx` propres à SQLite).
- **Backend** : respect strict DAO → Service → Route ; isolation `user_id` ; schémas Pydantic in/out.

---

## 0. Décisions d'architecture (à valider AVANT la Phase 1)

> ⚠️ Ces décisions conditionnent tout le reste. À confirmer avec le porteur produit.

- **D1 — Élément de révision = entité indépendante typée.**
  Le **deck** reste dédié aux **flashcards** (recto/verso) : un deck = un ensemble de flashcards révisées ensemble (cf. **D3c**). Pour les autres types, on introduit un modèle générique **`RevisionSet`** (ensemble nommé, homogène, rattaché à un classeur) + **`RevisionItem`** (item d'un ensemble, avec état SM-2 individuel). `RevisionSet.type ∈ {qcm, vf, association, definition, ordre}`. Un ensemble est **homogène** (un seul type). QCM/VF/assoc/def/ordre sont ainsi des entités indépendantes, et **non** des « flashcards ».
- **D2 — Le mot « flashcard » est réservé au recto/verso.** Dans l'UI et le domaine, « flashcard » = `type=flashcard` uniquement. Les autres types ont leur propre nom (QCM, Vrai/Faux, Association, Définition, Ordre).
- **D3 — Réconciliation de la PR #48 (♻️) — décision : D3c (retenu).** La PR #48 avait introduit `Flashcard.card_type ∈ {basic,qcm,vf,ordre,assoc}` + `payload` dans des **decks mixtes** — **incompatible avec D1/D2** (un deck ne contient que des flashcards recto/verso). Décision du porteur produit :
  - **Le `Deck`/`Flashcard` reste strictement flashcard (recto/verso)** : on **annule le mélange** de la PR #48 (retour à `card_type=basic` uniquement, plus de `payload` typé dans les flashcards).
  - **Les autres types vivent dans de nouvelles tables `revision_sets` / `revision_items`** (génériques, homogènes, typées, SM-2 par item, `payload` validé par type).
  - **Migration de réconciliation** : tout item `card_type ≠ basic` créé par la PR #48 est **transféré** vers un `RevisionSet` homogène du bon type ; les decks redeviennent homogènes (flashcards).
  - Alternatives écartées : **D3a** (généraliser `Deck` en `RevisionSet` via `element_type`) — rejetée car elle dilue la notion de deck/flashcard que le produit veut garder pure ; **D3b** (tout migrer `Deck`/`Flashcard` vers les nouvelles tables) — rejetée car coûteuse et inutile (les flashcards sont déjà bien servies par `Deck`/`Flashcard`).
  > **Conséquence** : deux familles parallèles — `Deck`/`Flashcard` (flashcards) et `RevisionSet`/`RevisionItem` (qcm/vf/assoc/def/ordre). Les couches transverses (SM-2, `StudySession`, stats, partage, clone, devoirs) doivent traiter les deux de façon **uniforme** via une abstraction « élément de révision ». Le reste du plan suppose **D3c**.
- **D4 — Fine-tuning SM-2.** Paramètre `tuning` (float, défaut 1.0) **par item** (« s'acharner sur une carte ») et `tuning_default` **par ensemble**. Applique un multiplicateur sur l'intervalle SM-2 (`<1` = plus fréquent, `>1` = plus espacé).
- **D5 — Statistiques de révision (objectif : stats actionnables).** Le porteur produit veut des stats **précises et pertinentes** : en les lisant, l'étudiant doit comprendre **ce qui est acquis, ce qui résiste, et quoi faire**. On s'appuie sur des indicateurs **connus et éprouvés** de la science de la mémoire / répétition espacée, pas seulement sur des compteurs bruts.
  - **Source unique d'historique** : `StudySession` (déjà `grade`, `created_at`, `duration_seconds`). Généraliser `flashcard_id` → `item_id` (+ discriminant de type) pour couvrir flashcards **et** `RevisionItem`.
  - **Cadre de référence** : modèle **DSR** popularisé par **FSRS** (Free Spaced Repetition Scheduler, utilisé par Anki) — trois variables par item :
    - **Stabilité (S)** : nb de jours pour que la probabilité de rappel retombe à 90 %. ↑ = mémoire bien consolidée.
    - **Difficulté (D)** : complexité intrinsèque de l'item (échelle ~1–10). ↑ = dur à stabiliser.
    - **Récupérabilité (R)** : probabilité de rappel **à l'instant t**, décroît depuis la dernière révision selon la **courbe d'oubli d'Ebbinghaus** (`R ≈ exp(-t/S)`). C'est ce qui dit « à réviser maintenant ».
  - **On garde SM-2 comme planificateur** (existant), mais on **dérive les indicateurs DSR/FSRS depuis l'historique `StudySession`** (S ≈ proxy de l'intervalle, D ≈ inverse de l'ease factor, R calculée à la volée). FSRS reste une **évolution future possible du planificateur** (note d'archi, hors scope).
  - **Indicateurs actionnables** (le cœur de la demande) :

    | Indicateur | Définition (nom connu) | Ce qu'il dit à l'étudiant |
    |---|---|---|
    | **Rétention réelle** | % réussite (grade ≥ 3) sur items **mûrs** — « True Retention » (Anki) | Mon planning est-il bien calibré ? (cible ~85–90 %) |
    | **Récupérabilité actuelle** | R (FSRS) par item | Quoi réviser **aujourd'hui** (items dont R passe sous la cible) |
    | **Sangsues / points noirs** | « Leeches » (Anki) : items échoués ≥ N fois / S faible malgré bcp de révisions | **Ce qui ne va pas** : à reformuler, scinder, ré-apprendre |
    | **Taux de rechute** | « Lapse rate » : % d'items mûrs oubliés | Planning trop espacé ou items trop durs |
    | **Maturité / maîtrise** | % d'items à intervalle ≥ seuil (ex. 21 j) ; **date de maîtrise estimée** (projection S) | Progression réelle vers l'ancrage long terme |
    | **Difficulté (D)** | par item / agrégée par ensemble | Quel contenu est intrinsèquement le plus dur |
    | **Vitesse de réponse** | latence médiane (`duration_seconds`) + tendance | Rappel **fluide** vs fragile (correct mais lent) |
    | **Courbe d'apprentissage / d'oubli** | accuracy par répétition + courbe d'Ebbinghaus par item/ensemble | Visualiser la consolidation et l'oubli |
    | **Charge à venir** | prévision des révisions dues / jour (« review forecast ») | Anticiper et lisser l'effort |
    | **Régularité** | heatmap + streak (existants) | Constance = facteur clé de mémorisation |

  - **Restitution UI** : ne pas se contenter d'afficher des nombres — surfacer des **verdicts** (« 3 sangsues à reformuler », « rétention 78 % < cible : espacement trop agressif », « 12 cartes à risque aujourd'hui »). Détail par item, par ensemble (A7), par classeur (A8).
  - **Références à vérifier** : FSRS / modèle DSR (open source, doc Anki), courbe d'oubli d'**Ebbinghaus**, **SM-2** (SuperMemo), métriques **True Retention** & **Leeches** (Anki), **Half-Life Regression** (Duolingo) pour la notion de demi-vie de mémoire.
- **D6 — QCM scoré.** Un QCM (ensemble) contient des questions ; chaque question porte `points` (défaut 1) et supporte **bonnes réponses uniques OU multiples** (`payload.options[].correct` multiple). Un « passage » de QCM produit un score pondéré.
- **D7 — Mode inversé (flashcards).** Option `reversed` au niveau **ensemble flashcard** : génère aussi des items d'étude verso→recto (état SM-2 distinct). Décision : items inversés matérialisés (`RevisionItem` lié `reverse_of`) **ou** virtuels à l'étude. Recommandé : matérialisés pour un suivi SM-2 propre.

---

## 1. État des lieux (existant, juin 2026)

| Domaine | Existant | Réf. |
|---|---|---|
| Classeurs | Arbre `Binder` (parent/children), notes/decks/diagrams/pdfs, tags, public/clone communautaire. Menu « + Ajouter » + items typés (PR #48 ♻️). | `models/binder.py`, `views/Binders/Binders.vue` |
| Flashcards | `Deck` + `Flashcard` (recto/verso, `card_type`+`payload` ♻️), SM-2 `calculate_sm2`. Étude `StudyDeck.vue` (+ `TypedStudyCard`). | `services/flashcard_service.py`, `services/spaced_repetition.py` |
| Stats | `/stats/overview|sessions|heatmap|decks/:id|dashboard`. `StudySession(flashcard_id, grade, ...)`. | `api/v1/stats.py`, `models/study_session.py` |
| Révision IA | Évaluation IA (note), Auto-QCM (`Quiz`), Blurting, Feynman. Onglets à plat. | `views/Reviews/Reviews.vue`, `models/quiz.py`, `models/evaluation.py` |
| Professeur | `Group(is_class)`, `GroupBinder` (partage par référence), `Assignment`+`AssignmentTask` (`flashcards|quiz|exam|blurting|read`), `AssignmentProgress` (+notation), analytics, engagement, `Notification`, `ClassInsight`. | `services/class_*`, `models/assignment.py`, `models/group.py` |
| Révision active notes | Balisage `{{qcm}}/{{vf}}/{{trou}}/[def]` + mode « Révision Active » inline (révéler/répondre). | `views/Notes/NoteEdit.vue`, `utils/placeholder_parser.py` |
| Fait depuis (A0→A8 + C1 + C2) | Socle `revision_sets`/`revision_items` (A0) ; flashcard avancée — inversé/tuning/courbe (A1) ; QCM scoré (A2) ; VF/association/définition/ordre (A3–A6) ; stats par élément/ensemble (A7) ; **stats par classeur (A8)** ; **rattacher/détacher des éléments existants (C1)** ; **onglet Révisions Classiques/IA (C2)**. **Parties A et C (hors affichage diagrammes/pdfs) complètes.** | cf. §5 |
| Manquant | Affichage diagrammes/pdfs dans le classeur (reste de C1) ; stats de groupe étendues (B5). | — |

---

# PARTIE A — RÉVISION

## A0. Socle — modèle générique d'élément de révision (♻️ refonte PR #48)

**Objectif** : poser les tables `revision_sets` (homogène, typé, rattaché à un classeur) + `revision_items` (génériques, SM-2 par item) pour QCM/VF/assoc/déf/ordre, **annuler le mélange de la PR #48** dans `Deck`/`Flashcard`, et exposer une abstraction « élément de révision » commune aux deux familles. (Décision **D3c**, cf. §0.)

**État actuel** : ✅ **Fait** (PR #49 `feature/revision-foundation`, 2026-06-15). Tables `revision_sets`/`revision_items`, réconciliation de la PR #48 et `tuning` SM-2 en place. _Nuance : l'abstraction transverse côté **devoirs** reste à brancher (cf. B3)._

**Étapes (backend)**
- [x] Décision **D3c** actée (cf. §0) : `Deck`/`Flashcard` = flashcards uniquement ; nouvelles tables `revision_sets`/`revision_items` pour les autres types.
- [x] Nouveaux modèles `RevisionSet` (`name`, `type ∈ {qcm,vf,association,definition,ordre}`, `binder_id`, `tuning_default` Float 1.0, `is_public`, clone/partage alignés sur `Deck`) et `RevisionItem` (`set_id`, `payload` JSON validé par type, état SM-2 : `ease_factor`, `interval`, `repetitions`, `due_date`, `tuning` Float 1.0).
- [x] **Réconciliation PR #48** : migration qui (1) transfère chaque `Flashcard.card_type ≠ basic` vers un `RevisionSet` homogène + `RevisionItem`, (2) restaure `Deck`/`Flashcard` en recto/verso pur (`card_type=basic`, retrait de l'usage `payload`). Additive, idempotente (guard `inspector`), SQLite + PostgreSQL. _(migrations `a1b2c3d4e5f6`, `b2c3d4e5f6a7`)_
- [x] `revision_service.py` : CRUD ensembles typés + items ; rejet d'un item de type ≠ ensemble ; application du `tuning` (`tuning_set * tuning_item`).
- [x] `spaced_repetition.calculate_sm2` : paramètre `tuning: float = 1.0` appliqué à l'intervalle final (partagé par flashcards et items).
- [x] Abstraction « élément de révision » transverse : `StudySession.item_id` (+ type), étude, stats, partage/clone traitent `Flashcard` **et** `RevisionItem` uniformément (cf. D5/A7). _(devoirs : voir B3, non branché)_
- [x] Schémas Pydantic : `RevisionSetCreate/Update/Response`, `RevisionItemCreate/Update/Response` (payload validé par type).

**Étapes (frontend)**
- [x] `stores/revision.ts` : CRUD ensembles typés + items (`type`, `tuning`).
- [x] Réconcilier `RevisionItemModal.vue` (PR #48) : un ensemble = un seul type ; les flashcards passent par le flux deck existant, les autres types par `revision_sets`.

**Tests à définir**
- Backend : création d'ensembles homogènes par type ; rejet d'un item de type ≠ ensemble ; **migration de réconciliation** (deck PR #48 mixte → flashcards pures + RevisionSets, idempotence) ; `tuning` modifie l'intervalle.
- Frontend : `revision` store envoie `type`/`tuning` ; flashcards inchangées.

**Commits** : `feat(revision): tables revision_sets/revision_items (socle)` · `refactor(decks): retrait du mélange typé PR #48 (flashcards pures)` · `feat(revision): paramètre tuning SM-2`.
**PR** : `feature/revision-foundation`. **CI** : tous checks + drift guard OK.

## A1. Flashcard (recto/verso)

**Objectif** : flashcards = recto/verso uniquement, + mode inversé + courbe + tuning.

**État actuel** : ✅ **Fait** (PR #55, ex-#51 `feature/flashcard-advanced`, 2026-06-15). _Implémenté sur `Deck`/`Flashcard` (D3c), pas sur `RevisionItem` : `Deck.reversed`/`tuning_default`, `Flashcard.tuning`/`reverse_of_id`, miroir matérialisé, endpoint history sur `decks/:id/cards/:card_id`. Migration `c3d4e5f6a7b8`._

**Étapes**
- [x] (backend) `reversed` sur l'ensemble flashcard : à la création/édition, matérialiser/retirer les cartes miroir (`reverse_of_id`). Étude planifie recto→verso et verso→recto séparément. _(porté sur `Deck`/`Flashcard`, pas `RevisionItem`)_
- [x] (backend) Endpoint courbe d'apprentissage par carte : `GET /decks/:id/cards/:card_id/history` → série `(date, grade)` depuis `StudySession`.
- [x] (frontend) Toggle « mode inversé » à la création/édition d'un deck.
- [x] (frontend) Composant `LearningCurve.vue` (sparkline SVG sans dépendance) sur la fiche carte.
- [x] (frontend) Réglage `tuning` par carte (slider « réviser plus/moins souvent »).

**Tests** : inversé crée les items réciproques ; suppression nettoie les inversés ; history renvoie la série ordonnée ; tuning persiste et change l'échéance.
**Commits** : `feat(flashcard): mode inversé`, `feat(flashcard): courbe d'apprentissage`, `feat(flashcard): tuning par carte`.
**PR** : `feature/flashcard-advanced`.

## A2. QCM (entité indépendante)

**Objectif** : QCM = ensemble de questions ; réponses uniques **ou** multiples ; points par question.

**État actuel** : ✅ **Fait** (PR #56, ex-#52 `feature/revision-qcm`, 2026-06-15). Passage scoré pondéré + multi tout-ou-rien, SM-2 par question, `QcmRun.vue`.

**Étapes**
- [x] (backend) `payload` qcm : `options[].correct` multiple + `points` (int, défaut 1) par question. Validation : ≥2 options, ≥1 correcte.
- [x] (backend) Logique de correction : score = somme pondérée ; tout-ou-rien sur multi. Endpoint « passage » : `POST /revision/sets/:id/run` → score pondéré + détail par question, et mise à jour SM-2 par item.
- [x] (frontend) Éditeur QCM (barème/points dans `RevisionItemModal`) — distinct du flux flashcard.
- [x] (frontend) Étude QCM : sélection (mono/multi), barème, score final pondéré (`QcmRun.vue`).

**Tests** : score pondéré (mono & multi) ; rejet question sans bonne réponse ; points custom respectés.
**Commits** : `feat(qcm): points & réponses multiples`, `feat(qcm): passage scoré`.
**PR** : `feature/revision-qcm`.

## A3. Vrai / Faux

**Objectif** : entité Vrai/Faux indépendante (ensemble d'affirmations + verdict + justification).

**État actuel** : ✅ **Fait** (PR #53 `feature/revision-typed-study`, 2026-06-15). Étude VF dans `RevisionStudy.vue` + SM-2.

**Étapes** : [x] éditeur VF dédié · [x] étude VF (verdict + feedback + justification) · [x] SM-2 par item.
**Tests** : correction verdict ; justification révélée à la complétion.
**Commits** : `feat(vf): entité vrai/faux`. **PR** : `feature/revision-vf` (peut être groupée avec A4–A6).

## A4. Association

**Objectif** : entité Association (lier des éléments entre eux).

**État actuel** : ✅ **Fait** (PR #53 `feature/revision-typed-study`, 2026-06-15). Appariement ordre-indifférent dans `RevisionStudy.vue` + SM-2.

**Étapes** : [x] éditeur paires gauche/droite · [x] étude par appariement interactif (menus) + correction (ordre indifférent) · [x] SM-2.
**Tests** : correction d'appariement (ordre indifférent) ; appariement partiel.
**Commits** : `feat(association): entité association`. **PR** : `feature/revision-assoc`.

## A5. Définition

**Objectif** : entité Définition (terme → définition).

**État actuel** : ✅ **Fait** (socle A0 #49 + étude PR #53 `feature/revision-typed-study`, 2026-06-15). Type `definition` au socle, auto-évaluation (révéler + answer) dans `RevisionStudy.vue` + SM-2.

**Étapes** : [x] type `definition` au socle · [x] éditeur terme/définition · [x] étude (révéler la définition, auto-éval) · [x] SM-2.
**Tests** : création/affichage ; SM-2.
**Commits** : `feat(definition): entité définition`. **PR** : `feature/revision-definition`.

## A6. Ordre

**Objectif** : entité Ordre (remettre une suite d'actions dans le bon ordre).

**État actuel** : ✅ **Fait** (PR #53 `feature/revision-typed-study`, 2026-06-15). Réordonnancement ▲▼ + correction stricte dans `RevisionStudy.vue` + SM-2.

**Étapes** : [x] éditeur étapes ordonnées · [x] étude : éléments en désordre + réordonnancement (▲▼) + correction stricte · [x] SM-2.
**Tests** : correction d'ordre exact ; présentation mélangée déterministe en test.
**Commits** : `feat(ordre): entité ordre`. **PR** : `feature/revision-ordre`.

## A7. Statistiques par élément de révision

**Objectif** : par item ET par ensemble : nb de révisions, % réussite, % rétention, date de maîtrise estimée, courbe.

**État actuel** : ✅ **Fait** (PR #54 `feature/stats-elements`, 2026-06-15). `revision_stats_service`, endpoints item/ensemble, `RevisionSetStats.vue`.

**Étapes**
- [x] (backend) `StudySession.item_id` (+ discriminant de type) couvrant flashcards **et** `RevisionItem` (posé au socle A0).
- [x] (backend) Calcul des indicateurs **D5** depuis l'historique : rétention réelle (True Retention, mûrs), récupérabilité **R** (Ebbinghaus), stabilité **S** & difficulté **D** (proxys SM-2), sangsues (leeches), maturité, date de maîtrise (projection SM-2), séries historiques.
- [x] (backend) `GET /stats/items/:id` (indicateurs + série) et `GET /stats/sets/:id` (agrégats ensemble, **SQL** anti-N+1).
- [x] (frontend) Panneau stats par élément : KPI + mini-courbe SVG + **verdicts actionnables** (`RevisionSetStats.vue`).

**Tests** : calculs (%réussite, %rétention) sur jeu de sessions fixé ; date de maîtrise déterministe ; isolation `user_id`.
**Commits** : `feat(stats): stats par item et par ensemble`. **PR** : `feature/stats-elements`.

## A8. Statistiques par classeur

**Objectif** : vue d'avancement/rétention agrégée de tous les éléments d'un classeur (et sous-arbre).

**État actuel** : ✅ **Fait** (PR `feature/stats-binder`, 2026-06-15). `GET /stats/binders/:id` (réutilise `revision_stats_service`), `RevisionBinderStats.vue`, bouton « Stats » dans `Binders.vue`. _Périmètre : ensembles de révision ; les decks de flashcards gardent `/stats/decks/:id` (à unifier plus tard si besoin)._

**Étapes**
- [x] (backend) `GET /stats/binders/:id` (UUID) : agrégat sur tous les ensembles du classeur **+ descendants** (option `?descendants=false`), via `RevisionStatsService.get_binder_stats` ; **agrégats bornés** (1 req. sets + 1 req. items + 1 req. sessions par type) → `test_binder_stats_query_budget`.
- [x] (frontend) Vue « Stats » du classeur (`RevisionBinderStats.vue`) : avancement global (KPI), rétention moyenne, **répartition par type**, **ensembles à surveiller** + liste complète ; accès via bouton dans `Binders.vue`.

**Tests** : agrégation multi-ensembles/types ; inclusion du sous-arbre (+ `descendants=false`) ; budget de requêtes ; isolation entre utilisateurs. Front : `revision.spec` (fetchBinderStats).
**Commits** : `feat(stats): tableau de bord par classeur`. **PR** : `feature/stats-binder`.

## A9. Mode révision active sur les notes (balisage)

**Objectif** : consolider l'existant (révéler/répondre inline) ; ne crée **aucune** entité de révision automatiquement (cf. mémoire `no-auto-flashcards-from-notes`).

**État actuel** : ✅ fonctionnel (mode « Révision Active » conservé).

**Étapes** : [ ] vérifier la cohérence après A0 (le balisage reste un self-test inline + alimente les évals IA, sans persistance). [ ] doc utilisateur.
**Tests** : non-régression du parser de balises (`test_placeholders`).
**Commits** : `docs(revision): clarifier la révision active des notes`. **PR** : incluse dans la doc finale.

---

# PARTIE B — PROFESSEUR

## B1. Déposer des cours

**Objectif** : un prof dépose un « cours » (note et/ou PDF) visible par la classe.

**État actuel** : 🟡 partage de classeur par référence existe (`GroupBinder`).

**Étapes**
- [ ] (décision) « cours » = note/PDF rangés dans un classeur partagé à la classe (réutilise `GroupBinder`) plutôt qu'une nouvelle entité.
- [ ] (backend) Endpoint(s) prof : déposer/retirer un cours dans le classeur de classe ; visibilité élèves (lecture seule, déjà géré côté accès).
- [ ] (frontend) Espace prof : « Déposer un cours » (upload PDF / créer note dans le classeur de classe).

**Tests** : un élève voit le cours en lecture seule ; isolation hors-classe.
**Commits** : `feat(teacher): dépôt de cours`. **PR** : `feature/teacher-courses`.

## B2. Déposer un classeur (auto-mis à jour)

**Objectif** : partager un classeur à la classe, **auto-actualisé** quand le prof y ajoute des éléments.

**État actuel** : ✅ `GroupBinder` partage **par référence** ⇒ auto-update natif.

**Étapes** : [ ] (backend) vérifier que l'ajout d'éléments dans un classeur déjà partagé est immédiatement visible des élèves (test). [ ] (frontend) UI « Partager ce classeur à la classe » + indicateur « partagé ».
**Tests** : ajout d'un élément après partage ⇒ visible élève sans ré-action prof.
**Commits** : `feat(teacher): partage de classeur auto-actualisé`. **PR** : `feature/teacher-share-binder`.

## B3. Déposer des devoirs (QCM, flashcards, …)

**Objectif** : devoir = tâches typées (réviser un ensemble, passer un QCM…).

**État actuel** : ✅ **Fait** (PR `feature/teacher-assignments-revision`, 2026-06-15).

**Étapes**
- [x] (backend) `TASK_TYPES` étendu avec **`revision`** (cible = `RevisionSet`). `TASK_TARGET_KIND["revision"]="revision_set"` ; `_resolve_task_target` résout l'ensemble (appartenance prof) → `ref_id=set.id`, `ref_label=set.name`. Complétion **dérivée** des `StudySession` des items de l'ensemble (`_revision_state`) avec objectif `{min_items, min_score}`.
- [x] (frontend) `AssignmentBuilder` : type **« Ensemble de révision »** (cible `set`) + objectif (items min., score min.) ; `TeacherDashboard` fournit `setOptions`. Lancement élève : `taskLaunchRoute` → `/revision/sets/:id/study` (les QCM y sont redirigés vers leur passage scoré). `StudentClassView` : CTA « Réviser ».

**Tests** : backend `test_assignment_revision` (création/résolution, complétion dérivée d'une session, isolation cible d'autrui → 404) ; front `assignmentTasks.spec` (route revision par `ref_id`). vue-tsc clean.
**Commits** : `feat(teacher): devoirs sur ensembles de révision`. **PR** : `feature/teacher-assignments-revision`.

## B4. Questions des élèves (Q&A) — NOUVEAU

**Objectif** : un élève pose une question au prof ; le prof répond ; notifications.

**État actuel** : ✅ **Fait** (PR `feature/teacher-qa`, 2026-06-15).

**Étapes**
- [x] (backend) Modèle **`ClassQuestion`** (group_id, author_id, body, answer, answered_by, status `open|answered`, created_at, answered_at) — réponse unique (pas de thread). Migration idempotente `a7c1d2e3f4b5`.
- [x] (backend) Endpoints : `POST /classes/:id/questions` (élève poste), `GET /classes/:id/questions` (prof = toutes, élève = les siennes), `POST /classes/:id/questions/:qid/answer` (prof répond → clôt). `ClassQAService`, isolation classe.
- [x] (backend) Notifications (`Notification`) : type `question` aux professeurs à la création, type `answer` à l'auteur à la réponse.
- [x] (frontend) Élève : section « Poser une question » (sélecteur de classe + fil) dans `StudentClassView`. Prof : onglet **« Questions »** (inbox + réponse inline) dans `TeacherDashboard`. `classService.listQuestions/postQuestion/answerQuestion`.

**Tests** : backend `test_class_qa` (post + visibilité prof/élève, isolation entre élèves, réponse + statut, élève ne peut répondre → 403, notifications prof/élève) ; front `classQuestions.spec`. vue-tsc clean.
**Commits** : `feat(teacher): questions des élèves (Q&A)`, `test(teacher): isolation Q&A`.
**PR** : `feature/teacher-qa`.

## B5. Statistiques du groupe de classe

**Objectif** : avancement des élèves, taux de réussite, temps moyen de révision.

**État actuel** : 🟡 analytics prof + `ClassInsight` existent (lacunes IA, progression devoirs).

**Étapes**
- [ ] (backend) Étendre l'analytics : temps moyen de révision (`StudySession.duration_seconds`), taux de réussite global, avancement par élève/ensemble — **agrégats SQL** + budget de requêtes.
- [ ] (frontend) `TeacherDashboard` : KPIs groupe + tableau par élève.

**Tests** : agrégats sur jeu fixé ; isolation classe ; budget requêtes.
**Commits** : `feat(teacher): stats de groupe (réussite, temps, avancement)`. **PR** : `feature/teacher-group-stats`.

---

# PARTIE C — UI

## C1. Classeur — gestion simple (rattacher des éléments existants)

**Objectif** : créer un classeur puis **y rattacher des éléments déjà existants** ; gérer visibilité, renommer, retirer/ajouter des éléments.

**État actuel** : ✅ **Fait** (PR `feature/binder-manage`, 2026-06-15). Attache/détache existant ; visibilité ✅ ; renommer ✅ (update). _Reste : affichage des diagrammes/PDF **dans** la vue classeur (backend déjà compatible)._

**Étapes**
- [x] (backend) Endpoints d'**attache/détache** : `POST /binders/:id/items` et `POST /binders/:id/items/detach` déplacent note/deck/ensemble/diagramme/pdf vers/hors d'un classeur (`binder_id`), sans suppression. `BinderItemsService`, vérifs d'appartenance (élément **et** classeur via `check_binder_access`).
- [x] (frontend) Modale « **Ajouter un élément existant** » (sélecteur multi) dans `Binders.vue` : notes, jeux de révision (decks), ensembles non rangés / d'un autre classeur. _(diagrammes/pdfs : backend prêt, à exposer quand ils seront affichés dans le classeur)_
- [x] (frontend) Retirer un élément du classeur (**détache**, ne supprime pas) — bouton dédié par ligne, distinct de la suppression.
- [ ] (frontend) Afficher **tous** les types dans le classeur (diagrammes, pdfs manquants à l'affichage).
- [x] (frontend) Renommer le classeur (via update) ; rappel visibilité public/privé (bouton Partager).

**Tests** : attache (note/deck/ensemble), détache conserve l'élément, rejet type inconnu (400), isolation (élément d'autrui, classeur d'autrui). Front : `binders.spec` (attachItems/detachItems).
**Commits** : `feat(binder): rattacher/détacher des éléments existants`, `feat(binder): affichage complet des contenus`.
**PR** : `feature/binder-manage`.

## C2. Onglet Révisions — Classiques vs IA

**Objectif** : deux catégories. **Classiques** (flashcard, qcm, vf, association, définition, ordre) en sous-catégories gérables (nom, fine-tuning, association classeur) + stats. **IA** (auto-QCM, feuille blanche, Feynman, évaluation IA).

**État actuel** : ✅ **Fait** (PR `feature/reviews-reorg`, 2026-06-15).

**Étapes**
- [x] (frontend) Réorganiser `Reviews.vue` : 2 catégories (**Classiques / IA**) avec sélecteur + sous-onglets ; Classiques = sous-onglets par type (Flashcards, QCM, V/F, Association, Définition, Ordre).
- [x] (frontend) Par type : liste des ensembles avec **gestion** (renommer, **fine-tuning** `tuning_default`, **rattacher à un classeur**, supprimer) et accès **étude/lancement**.
- [x] (frontend) Accès au **panneau stats par élément** (réutilise A7 : bouton « Stats » → `RevisionSetStats.vue`).
- [x] (frontend) Catégorie **IA** : regroupe évaluation IA / feuille blanche / Feynman / auto-QCM (panneaux existants).

**Tests** : Vitest `revision.spec` (updateSet name/tuning/binder). vue-tsc clean, E2E `/reviews` rendu OK.
**Commits** : `feat(reviews): catégories Classiques/IA + sous-catégories`, `feat(reviews): gestion & stats par élément`.
**PR** : `feature/reviews-reorg` (dépend de A7).

---

## 3. Séquencement des PR (ordre de dépendances)

1. **`feature/revision-foundation`** (A0) — socle obligatoire (bloque tout le reste de A et C2).
2. En parallèle après le socle : **`feature/revision-qcm`** (A2), **`feature/revision-vf`** (A3), **`feature/revision-assoc`** (A4), **`feature/revision-definition`** (A5), **`feature/revision-ordre`** (A6), **`feature/flashcard-advanced`** (A1).
3. **`feature/stats-elements`** (A7) → **`feature/stats-binder`** (A8).
4. **`feature/binder-manage`** (C1) — indépendant, peut démarrer tôt.
5. **`feature/reviews-reorg`** (C2) — après A7.
6. Professeur : **`feature/teacher-share-binder`** (B2), **`feature/teacher-courses`** (B1), **`feature/teacher-assignments-revision`** (B3, après socle), **`feature/teacher-qa`** (B4), **`feature/teacher-group-stats`** (B5).
7. **`docs/...`** final (A9 + doc utilisateur + MAJ `docs/FEATURES.md` + journal).

## 4. CI / Qualité (par PR)
- Tous les checks listés en tête doivent être **verts**.
- Chaque modèle modifié ⇒ migration + **probe de drift** local avant push (sinon échec `migrations (PostgreSQL)`).
- Coverage backend ≥ 80 % ; ajouter les tests nommés de chaque sous-partie.
- `vue-tsc -b` sans erreur (attention `noUnusedLocals`/`noUnusedParameters`).
- Mettre à jour `docs/FEATURES.md` (changelog) + `docs/development_journal.md` à chaque PR (checklist AGENTS.md §13).

---

## 5. Journal d'avancement

> Chronologique, le plus récent en bas. Une ligne par action concrète (création de branche, commit, PR, merge, décision).

- **2026-06-15** — Création de `REFACTO_FONCTIONNALITES.md` (ce plan). État des lieux établi ; décisions d'architecture D1–D7 posées (en attente de validation, notamment **D3a** réconciliation de la PR #48 : QCM/VF/etc. deviennent des entités indépendantes, le mot « flashcard » est réservé au recto/verso). Aucune implémentation démarrée.
- **2026-06-15** — Décisions validées par le porteur produit : **D3c retenu** (le `Deck`/`Flashcard` reste strictement flashcard recto/verso ; nouvelles tables `revision_sets`/`revision_items` pour qcm/vf/association/définition/ordre ; réconciliation = annuler le mélange typé de la PR #48). **D4** (tuning par item), **D6** (QCM tout-ou-rien configurable), **D7** (mode inversé matérialisé) confirmés. **D5 enrichi** : stats actionnables fondées sur des indicateurs connus (modèle DSR/FSRS — stabilité/difficulté/récupérabilité, courbe d'oubli d'Ebbinghaus, True Retention & sangsues d'Anki, SM-2 conservé comme planificateur). Plan déplacé dans `docs/` et commité sur `docs/refacto-plan` (`main` protégé par convention). Toujours aucune implémentation de code.
- **2026-06-15** — **A0 livré** (PR #49 `feature/revision-foundation`, mergée). Tables `revision_sets`/`revision_items`, `revision_service`, `tuning` SM-2, `StudySession.item_id`/`item_type`, migrations `a1b2c3d4e5f6` (socle) + `b2c3d4e5f6a7` (réconciliation PR #48, idempotente). Front : `stores/revision.ts`, `RevisionItemModal` réconcilié.
- **2026-06-15** — **A1 livré** (PR #55, ex-#51 `feature/flashcard-advanced`, mergée). Mode inversé matérialisé + `tuning` + courbe d'apprentissage, **portés sur `Deck`/`Flashcard`** (D3c) plutôt que `RevisionItem` : `Deck.reversed`/`tuning_default`, `Flashcard.tuning`/`reverse_of_id`, `GET /decks/:id/cards/:card_id/history`, `LearningCurve.vue` (SVG). Migration `c3d4e5f6a7b8`.
- **2026-06-15** — **A2 livré** (PR #56, ex-#52 `feature/revision-qcm`, mergée). QCM scoré : `POST /revision/sets/:id/run`, pondération `points`, multi tout-ou-rien, SM-2 par question, `QcmRun.vue`. Pas de migration.
- **2026-06-15** — **A3–A6 livrés** (PR #53 `feature/revision-typed-study`, mergée). Étude + correction + SM-2 de VF / Association (ordre indifférent) / Définition (auto-éval) / Ordre (strict), `RevisionStudy.vue` + `POST /revision/sets/:id/study/grade/:item_id`. Pas de migration.
- **2026-06-15** — **A7 livré** (PR #54 `feature/stats-elements`, mergée). `revision_stats_service` (D : difficulté, R : Ebbinghaus, S : stabilité, True Retention, sangsues, maturité, date de maîtrise), `GET /stats/items/:id` + `GET /stats/sets/:id` (anti-N+1), `RevisionSetStats.vue` (KPI + verdicts + mini-courbe). Pas de migration.
- **2026-06-15** — **Note de process** : merge de la pile de PR (#49→#54). #51/#52 fermées en cascade par GitHub (suppression de leur branche de base) → recréées en #55/#56 vers `main`. Les enfants ont ensuite été re-ciblés sur `main` **avant** merge du parent pour éviter la cascade. Conflits limités à `docs/FEATURES.md` / `docs/development_journal.md` (ajouts conservés des deux côtés). **Reste : A8 (prochain), puis C1/C2 et extensions B3/B4/B5.**
- **2026-06-15** — **A8 livré** (`feature/stats-binder`). `GET /stats/binders/<uuid>` (option `?descendants=false`) agrège tous les ensembles de révision d'un classeur et de son sous-arbre ; refactor de `RevisionStatsService` (`_aggregate_set` partagé, accès via `check_binder_access`, anti-N+1 : 1 req. sets + 1 req. items + 1 req. sessions/type). Front : `RevisionBinderStats.vue` (KPI, répartition par type, ensembles à surveiller, liste) + bouton « Stats » dans `Binders.vue`. Pas de migration. Tests : backend 229 (dont `test_stats_binder` : agrégation, sous-arbre, isolation, budget), vue-tsc clean, Vitest 33. **Partie A désormais complète ; suite : C1/C2 puis B3/B4/B5.**
- **2026-06-15** — **C1 livré** (`feature/binder-manage`). Rattacher/détacher des éléments existants : `BinderItemsService` + `POST /binders/:id/items` et `POST /binders/:id/items/detach` (note/deck/ensemble/diagramme/pdf), vérifs d'appartenance élément **et** classeur. Front : modale « Ajouter un élément existant » (multi-select notes/decks/ensembles) + bouton « détacher » par ligne dans `Binders.vue` ; store `attachItems`/`detachItems`. Pas de migration. Tests : backend 234 (`test_binder_items` : attache, détache, type inconnu, double isolation), vue-tsc clean, Vitest 35. **Reste de C1 : afficher diagrammes/pdfs dans le classeur. Suite : C2.**
- **2026-06-15** — **C2 livré** (`feature/reviews-reorg`). Réorganisation de `Reviews.vue` en deux catégories **Classiques** (Flashcards + QCM/V-F/Association/Définition/Ordre en sous-onglets) et **IA** (évaluation, feuille blanche, Feynman, auto-QCM). Pour chaque type : liste des ensembles avec étude/lancement, stats (A7), et réglages (renommer, fine-tuning `tuning_default`, rattacher à un classeur, supprimer). Store `updateSet` accepte désormais `binder_id`. Frontend uniquement, pas de migration. Tests : vue-tsc clean, Vitest 36, E2E `/reviews` OK. **Parties A et C (hors affichage diagrammes/pdfs) bouclées ; suite : B3/B4/B5.**
- **2026-06-15** — **B3 livré** (`feature/teacher-assignments-revision`). Type de tâche **`revision`** ciblant un `RevisionSet` typé : `TASK_TYPES`/`TASK_TARGET_KIND` étendus, `_resolve_task_target` (appartenance prof), complétion **dérivée** des `StudySession` des items (`_revision_state`, objectif `{min_items, min_score}`). Front : `AssignmentBuilder` (cible « ensemble de révision » + objectif), `TeacherDashboard` (`setOptions`), `taskLaunchRoute` → `/revision/sets/:id/study` (QCM redirigé vers run via `RevisionStudy`), CTA élève « Réviser ». Pas de migration (`task_type` est un `String`). Tests : backend 237 (`test_assignment_revision`), vue-tsc clean, Vitest 37. **Suite : B4 (Q&A élèves).**
- **2026-06-15** — **B4 livré** (`feature/teacher-qa`). Questions des élèves : modèle **`ClassQuestion`** (réponse unique, statut `open`/`answered`) + migration idempotente `a7c1d2e3f4b5` ; `ClassQAService` + endpoints `POST/GET /classes/:id/questions` et `POST .../:qid/answer` (isolation : élève = ses questions, prof = toutes) ; notifications `question` (→ profs) et `answer` (→ auteur). Front : section Q&A dans `StudentClassView` (sélecteur de classe + poser + fil), onglet « Questions » dans `TeacherDashboard` (inbox + réponse inline), `classService` Q&A. Tests : backend 242 (`test_class_qa`), vue-tsc clean, Vitest 40. **Suite : B5 (stats de groupe étendues) — dernier item du plan.**
