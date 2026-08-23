# Revue technique — Architecture — StudyHub

> Phase 2 (lecture seule). Constats sourcés `fichier:ligne`, aucune correction appliquée.
> Référence : `docs/PROMPT_DEMARRAGE.md` §5, `AGENTS.md` §4, skill `backend-patterns` /
> `frontend-patterns`. Prolonge le constat brut de `docs/audit/00-CARTOGRAPHIE.md` §2.6
> (courts-circuits DAO) en le qualifiant : localisation précise, impact, gravité, effort.
> Généré le 2026-08-23.

## Légende

Gravité **S1** critique → **S4** cosmétique. Effort **XS/S/M/L**.

---

## Constats

### ARCH-01 — Service et route court-circuitent le DAO (`db.session` / `.query()` directs), systémique

**Emplacement** : `db.session` référencé hors `backend/app/dao/` dans 23 fichiers de routes
(`backend/app/api/v1/*.py`, quasi tous — la plupart des occurrences sont des instanciations de
DAO au niveau module, ex. `backend/app/api/v1/decks.py:17-19`, pas des requêtes directes) et
6 fichiers de services. Requêtes ORM directes (`.query(`) dans 13 fichiers de services :
`backend/app/services/stats_service.py`, `note_service.py`, `planning_service.py`,
`group_service.py`, `focus_service.py`, `evaluation_service.py`, `exam_service.py`,
`community_service.py`, `engagement_service.py`, `class_management_service.py`,
`class_qa_service.py`, `class_service.py`, `analytics_service.py`.

**Description** : la règle « le DAO est le seul endroit qui parle SQLAlchemy » (skill
`backend-patterns`) est massivement non respectée dans la couche service. Chaque service listé
construit ses propres requêtes ORM au lieu de les déléguer à un DAO, ce qui duplique la logique
de requêtage et rend la couche DAO non représentative du schéma d'accès réel aux données.

**Impact** : toute évolution du modèle de données (renommage de colonne, ajout d'un filtre
`user_id`, changement de stratégie d'eager loading) doit être répercutée dans chaque service au
lieu d'un seul DAO — risque d'oubli et d'incohérence entre chemins d'accès à la même entité.

**Gravité** : S2. **Effort** : L (remise en conformité progressive, service par service).
**Piste** : lors de toute modification touchant un de ces services, extraire la requête vers le
DAO correspondant plutôt que d'ajouter une nouvelle requête inline (pas de reprise big-bang).

---

### ARCH-02 — Routes publiques résolvent la ressource par requête ORM directe, sans service ni DAO

**Emplacement** :
- `backend/app/api/v1/binders.py:151` — `_db.session.query(Binder).filter_by(id=..., is_public=True).first()`
- `backend/app/api/v1/notes.py:128` — `_db.session.query(Note).filter_by(share_token=token, is_public=True).first()`
- `backend/app/api/v1/packages.py:36` — `db.session.query(Binder).filter(Binder.id == binder_id, Binder.is_public == True).first()`
- `backend/app/api/v1/classes.py:193` — `db.session.query(ClassInsight).filter(...).order_by(...).first()`

**Description** : ces quatre routes n'instancient ni DAO ni service — elles importent le modèle
et `db` directement dans le corps de la fonction (`from app.models.binder import Binder` /
`from app.extensions import db as _db`, imports locaux à la fonction, pattern répété aux quatre
endroits) et exécutent la requête en ligne. C'est le court-circuit le plus complet de la couche
(route → Model directement, sans passer ni par Service ni par DAO).

**Impact** : ce sont précisément les points d'entrée de partage public — la surface la plus
sensible côté sécurité (voir `docs/audit/01-SECURITE.md`) — qui échappent le plus à la
discipline d'architecture censée centraliser la vérification d'accès. Un futur changement de
règle de visibilité (ex. ajout d'une expiration de lien) doit être répété à quatre endroits.

**Gravité** : S2. **Effort** : M. **Piste** : ajouter une méthode dédiée par DAO concerné
(`get_public_by_id`, `get_by_share_token`) et un service `SharingService` unique qui centralise
la résolution des ressources publiques pour les quatre types de contenu.

---

### ARCH-03 — Logique métier (traversée récursive d'arbre) codée dans le corps de la route

**Emplacement** : `backend/app/api/v1/packages.py:36-64` (fonction interne `collect_contents`,
définie et appelée dans le handler `get_public_package`).

**Description** : la route définit une fonction récursive qui parcourt `binder.children`,
`binder.notes`, `binder.decks`, `binder.diagrams`, `binder.pdfs` pour construire la réponse.
C'est une règle métier (« comment agréger le contenu visible d'un classeur public et de ses
sous-classeurs ») écrite directement dans le contrôleur, en violation directe de « aucune
logique métier en route » (`AGENTS.md` §4, `backend/CLAUDE.md`).

**Impact** : logique non réutilisable (dupliquée si un futur endroit doit lister le même
contenu), non testable unitairement sans passer par le client de test Flask complet.

**Gravité** : S2. **Effort** : S. **Piste** : déplacer `collect_contents` dans
`CommunityService` (ou un nouveau `BinderContentService`), la route ne fait plus que déléguer et
sérialiser.

---

### ARCH-04 — Risque N+1 dans la traversée récursive de `packages.py`, par contournement des conventions d'eager loading du DAO

**Emplacement** : `backend/app/api/v1/packages.py:50-64`.

**Description** : les DAO du projet chargent systématiquement les relations en eager loading
(`joinedload`/`selectinload` présents dans 10 des 15 DAO — `binder_dao.py`, `note_dao.py`,
`deck_dao.py`, `diagram_dao.py`, `pdf_dao.py`, etc.). La requête de `ARCH-02`/`ARCH-03`
contourne entièrement cette couche : `binder` est chargé par une requête ORM nue sans option de
chargement, puis chaque accès à `b.notes`, `b.decks`, `b.diagrams`, `b.pdfs`, `b.children` dans
la récursion déclenche un lazy-load — un aller-retour base par relation et par niveau de
classeur imbriqué.

**Impact** : coût proportionnel à la profondeur et à la largeur de l'arborescence du classeur
public exploré ; potentiellement sévère sur un classeur de marketplace profondément imbriqué (à
chiffrer précisément en phase performance — voir `docs/audit/03-PERFORMANCE.md`).

**Gravité** : S2. **Effort** : S (une fois la requête déplacée en DAO comme proposé en ARCH-02,
il suffit d'y ajouter les options d'eager loading déjà standard ailleurs). **Piste** : DAO
dédié avec `joinedload`/`selectinload` sur les cinq relations, ou passage par les DAO existants
(`NoteDAO`, `DeckDAO`, etc.) déjà équipés.

---

### ARCH-05 — Le service commit directement la session au lieu de déléguer au DAO, systémique

**Emplacement** (échantillon représentatif, liste non exhaustive) :
`backend/app/services/class_service.py:342,364,384,414,509,565,886,930` (8 occurrences dans ce
seul fichier) ; `community_service.py:168` ; `note_service.py:162,174` ; `revision_service.py:304,371,416` ;
`flashcard_service.py:179,225` ; `engagement_service.py:200,229,237` ; `class_management_service.py:114,154,176` ;
`class_qa_service.py:84,121` ; `tag_service.py:79,88` ; `import_service.py:104`.

**Description** : `backend/CLAUDE.md` est explicite — « le DAO commit ; le service ne fait pas
de commit manuel hors DAO ». Au moins 12 fichiers de service appellent `.commit()` directement
(`db.session.commit()`, `self._db.commit()`, ou via l'attribut `.db` d'un DAO injecté,
ex. `self._flashcard_dao.db.commit()`), contournant la responsabilité transactionnelle que la
règle attribue au DAO.

**Impact** : le point de commit devient imprévisible (certains DAO commitent en interne, certains
services recommitent par-dessus) — risque de commits partiels si une opération multi-DAO échoue
entre deux appels `.commit()` distincts, et de sessions laissées ouvertes en cas d'exception
avant un commit attendu.

**Gravité** : S3. **Effort** : L (revue transaction par transaction, certains commits multiples
dans une même méthode — ex. `class_service.py` — peuvent masquer une opération qui devrait être
atomique). **Piste** : centraliser le commit dans les méthodes DAO d'écriture ; pour les
opérations multi-DAO, un commit unique en fin de méthode de service via une session partagée
plutôt qu'un commit par DAO.

---

### ARCH-06 — Services « fourre-tout » dépassant largement la responsabilité unique

**Emplacement** : `backend/app/services/class_service.py` (930 lignes),
`backend/app/services/ai_service.py` (820 lignes).

**Description** : à titre de comparaison, le troisième service le plus long
(`revision_service.py`) fait 418 lignes — moins de la moitié. `class_service.py` mélange gestion
de classe, insights IA, notifications et logique d'appartenance (repéré via les occurrences de
`.commit()` et `.query()` dispersées à travers tout le fichier lors de cet audit).

**Impact** : un service de cette taille est difficile à faire évoluer en TDD par petits cycles
(phase 3+) et concentre le risque de régression — toute modification de `class_service.py`
touche potentiellement plusieurs responsabilités non liées.

**Gravité** : S3. **Effort** : L. **Piste** : découper par sous-domaine (ex. `ClassInsightService`
déjà partiellement séparable — voir `ClassInsight` model utilisé ligne 191-207 de
`classes.py` — `ClassMembershipService`, `ClassNotificationService`) ; ne pas entreprendre ce
découpage en phase 2 (audit seul), le planifier comme prérequis avant d'ajouter des tests TDD sur
ce fichier en phase 3+.

---

### ARCH-07 — Composants Vue très au-delà du seuil de 300 lignes

**Emplacement** (10 vues sur ~466 fichiers `.vue`, triées par taille) :
`web/src/views/Notes/NoteEdit.vue` (3024 lignes — 10× le seuil), `views/Reviews/Reviews.vue`
(1878), `views/Diagrams/Diagrams.vue` (1789 — connu et déjà noté comme laissé tel quel jusqu'à la
phase 5 par `docs/ui-redesign-plan.md`), `views/Classes/TeacherDashboard.vue` (1064),
`views/Binders/Binders.vue` (780), `views/Notes/Blurting.vue` (631), `views/Notes/NoteQuiz.vue`
(566), `views/Dashboard/Dashboard.vue` (533), `views/Decks/Decks.vue` (518),
`views/Groups/GroupDetail.vue` (498).

**Description** : `AGENTS.md`/spec phase 2 fixe implicitement 300 lignes comme repère de
composant Vue surchargé (mélange affichage, état local, appels service, logique métier). Onze
vues au moins dépassent ce seuil, `NoteEdit.vue` le dépassant d'un ordre de grandeur.

**Impact** : ces vues seront les cycles les plus coûteux de la phase 4 (migration écran par
écran, skill `migration-ecran`) — un inventaire des fonctionnalités avant migration y sera
particulièrement long, et le risque de régression fonctionnelle lors de la réécriture y est le
plus élevé.

**Gravité** : S3. **Effort** : L par écran (traité nativement par la phase 4, pas un chantier
séparé). **Piste** : aucune correction en phase 2 — mais l'ordre de migration de la phase 4
(`docs/PROMPT_DEMARRAGE.md` §7) devrait tenir compte de cette taille pour le séquencement interne
de chaque écran (découpage en sous-composants avant réécriture visuelle plutôt qu'en un seul
passage sur 3000 lignes).

---

### ARCH-08 — Store Pinia à la limite du seuil de taille

**Emplacement** : `web/src/stores/revision.ts` (323 lignes), `stores/decks.ts` (294 lignes).

**Description** : pas de store franchement « fourre-tout » comme redouté par la spec (le plus
gros, `revision.ts`, reste sous 350 lignes et son périmètre — état de session de révision SM-2 —
est cohérent). Signalé pour mémoire, pas comme un problème avéré.

**Gravité** : S4. **Effort** : S (si un futur ajout à `revision.ts` le fait croître encore,
envisager d'en extraire la logique de timer/pause dans un composable dédié, comme cela a déjà
été fait pour `stores/pomodoro.ts`).

---

### ARCH-09 — Détection de plateforme ad hoc au lieu de `usePlatform()`

**Emplacement** : `web/src/stores/pomodoro.ts:4` et `:54` (`Capacitor.isNativePlatform()`),
`web/src/composables/useClassNotifications.ts:1` et `:11` (idem).

**Description** : `web/CLAUDE.md`/skill `frontend-patterns` imposent `usePlatform()` (qui expose
`isNative`) comme unique point de détection de plateforme, précisément pour éviter la dispersion
d'imports `@capacitor/core` dans des fichiers métier. Ces deux fichiers importent `Capacitor`
directement.

**Impact** : mineur isolément, mais c'est le genre d'écart qui se recopie — un futur fichier
imitera le motif existant plutôt que la règle documentée.

**Gravité** : S4. **Effort** : XS. **Piste** : remplacer les deux appels par
`usePlatform().isNative`.

---

### ARCH-10 — Réponse HTTP partiellement non modélisée en Pydantic

**Emplacement** : `backend/app/api/v1/packages.py:66-71` (`get_public_package`).

**Description** : la réponse mélange un champ validé par schéma (`binder`, via
`BinderResponse.model_validate`) et des listes de chaînes construites à la main
(`notes`, `decks`, `diagrams`, `pdfs` — simples titres extraits par `collect_contents`, sans
schéma de sortie dédié). `backend/CLAUDE.md` demande une modélisation Pydantic systématique en
sortie.

**Impact** : contrat de réponse implicite, non documenté par un schéma — un renommage de champ
ou un changement de forme (ex. inclure l'id en plus du titre) ne sera pas détecté par le
typage statique côté backend.

**Gravité** : S3. **Effort** : S. **Piste** : introduire un `PublicPackageResponse` Pydantic
listant des objets `{id, title}` au lieu de chaînes nues (résoudrait aussi une petite perte
d'information : le frontend ne peut pas lier un titre affiché à sa ressource sans l'id).

---

### ARCH-11 — Vérification d'appartenance dupliquée en ligne plutôt que centralisée, cohérence à vérifier

**Emplacement** : motif `if <entité>.user_id != user_id: raise ForbiddenError(...)` répété à
34 occurrences dans 20 fichiers de service. Un utilitaire partagé existe déjà et couvre l'accès
via classeur partagé : `check_binder_access` (`backend/app/utils/security.py`), utilisé dans
9 services (`revision_service.py`, `revision_stats_service.py`, `note_service.py`,
`pdf_service.py`, `flashcard_service.py`, `deck_service.py`, `diagram_service.py`,
`binder_items_service.py`, `binder_service.py`). Onze autres services vérifient l'appartenance
en ligne sans passer par cet utilitaire, par exemple `backend/app/services/quiz_service.py:58`
et `:128`.

**Description** : **à confirmer, pas certain** — deux lectures possibles. Soit ces onze services
couvrent des ressources qui n'ont légitimement pas de mode de partage via classeur (auquel cas la
vérification en ligne est correcte et `check_binder_access` n'y a simplement pas sa place). Soit
certaines de ces ressources (ex. un quiz rattaché à un deck, `quiz_service.py:125-129`) sont
en réalité accessibles à un collaborateur via un classeur partagé pour le deck mais pas pour le
quiz qui en dépend — une incohérence fonctionnelle, pas seulement stylistique.

**Impact** : si la deuxième lecture est correcte, un utilisateur ayant un accès partagé
en écriture sur un classeur pourrait se voir refuser l'accès à des quiz qui devraient suivre le
même partage que le deck. **Vérification proposée** : tester manuellement (ou via un test
d'intégration ciblé) l'accès à un quiz depuis un compte ayant uniquement un accès partagé au
classeur contenant le deck source.

**Gravité** : S3 (si confirmé — S4 si le comportement actuel est intentionnel). **Effort** : S.
**Piste** : si confirmé, faire passer les services concernés par `check_binder_access` ; sinon,
documenter explicitement dans chaque service pourquoi la ressource n'est pas partageable.

---

### ARCH-12 — Calcul de pagination dupliqué dans 8 routes

**Emplacement** : `math.ceil(total / per_page)` répété dans `backend/app/api/v1/diagrams.py`,
`packages.py`, `decks.py`, `flashcards.py`, `binders.py`, `notes.py`, `pdfs.py`, `revision.py`
(une occurrence par fichier).

**Description** : petite duplication mécanique — même calcul, même garde `if total > 0 else 0`
recopiés à huit endroits au lieu d'un helper partagé ou d'un schéma `PaginationMeta` avec une
factory.

**Gravité** : S4. **Effort** : XS. **Piste** : `app/schemas/common.py` (ou équivalent) avec un
constructeur `PaginationMeta.from_total(total, page, per_page)`.

---

## Points vérifiés sans anomalie

- **Migrations Alembic** : un seul head confirmé sur les 26 fichiers de
  `backend/migrations/versions/` (une inspection initiale automatisée avait signalé deux têtes
  apparentes ; vérification manuelle : faux positif dû à un style de guillemets différent —
  `down_revision = "c23a7429e6f8"` avec guillemets doubles dans
  `f4a8d9e2c731_add_tags_system.py:13` — pas une branche réelle). Chaîne linéaire, pas de
  divergence.
- **Eager loading côté DAO** : 10 des 15 DAO utilisent `joinedload`/`selectinload`
  explicitement — la couche DAO elle-même n'est pas le siège d'un problème N+1 systémique ; le
  seul cas identifié (ARCH-04) provient d'un contournement complet de cette couche, pas d'un
  oubli en son sein.

## Résumé

12 constats : 0 S1 · 4 S2 (ARCH-01 à 04) · 5 S3 (ARCH-05, 06, 07, 10, 11) · 3 S4 (ARCH-08, 09,
12). Note : ARCH-11 est provisoire (S3 sous réserve de confirmation, S4 sinon — voir
constat). Aucun fichier hors `docs/audit/` modifié pour produire cet audit.
