# Design — Reviser-hub : stats et hub de révision pour les ensembles hétérogènes

Date : 2026-08-29. Statut : validé par l'utilisateur en chat, en attente de
relecture du présent document avant passage à `writing-plans`.

Chantier : `workflow/reviser-hub/` (flux 6 d'`ETAT.md` § « Plan global par
flux — extension révision hétérogène + assistant IA »). Dépend de
`bibliotheque-ensembles`, mergé (PR #128, `af20f00`) : `RevisionSetDetail.vue`,
`RevisionSetTypeItems.vue`, `RevisionItemModal.vue` (6 types), `RevisionStudy.vue`
(dispatch par `item.type`) existent déjà et gèrent nativement les ensembles
hétérogènes.

## Pourquoi

`Reviews.vue`, `RevisionSetStats.vue` et `RevisionBinderStats.vue` ont été
explicitement laissés hors périmètre par `bibliotheque-ensembles` (territoire
`reviser-hub`). Ils assument encore qu'un ensemble a un type unique
(`RevisionSet.type` non nul) : un ensemble hétérogène y est soit invisible,
soit mal affiché, soit — pour les stats — silencieusement vide.

## Exploration faite avant de figer le périmètre

- **`RevisionSetManage.vue` (`/revision/sets/:id/manage`) est retiré, pas
  adapté.** Décision utilisateur : il fait fonctionnellement la même chose
  que `RevisionSetDetail.vue` (CRUD des items d'un ensemble), qui gère déjà
  l'hétérogénéité par construction (regroupement par type ; pour un ensemble
  homogène, un seul groupe s'affiche — équivalent fonctionnel exact). Le
  périmètre passe donc de 4 à **3 écrans** : `Reviews.vue`,
  `RevisionSetStats.vue`, `RevisionBinderStats.vue`.
- **`Reviews.vue` (1878 lignes) — rôle confirmé, pas de refonte de
  périmètre.** Décision utilisateur : les 5 onglets « Classiques » (un par
  `RevisionType` homogène) restent des listes d'ensembles homogènes
  filtrés — inchangé. Un **6ᵉ onglet « Mixte »** liste les ensembles
  hétérogènes (`type: null`) ; chaque ligne renvoie vers
  `RevisionSetDetail.vue` (`/revision/sets/:id`) — aucune nouvelle logique de
  regroupement à écrire ici, réutilisation pure de l'écran déjà construit.
  Les onglets IA (évaluation, feuille blanche, Feynman, quiz) et Flashcards :
  non touchés.
- **Bug backend réel trouvé, plus profond qu'un problème de schéma.**
  `StudySession.item_id`/`item_type` forment un couple polymorphe sans FK
  (« discrimine la source » — commentaire du modèle) : `item_type` n'est
  **pas** un filtre redondant, c'est un discriminant nécessaire. Or les 3
  points d'appel de `revision_stats_service.py` passent tous **`rset.type`**
  (le type de l'*ensemble*) là où il faut le type propre de chaque *item* —
  `get_item_stats` (`self._session_dao.get_for_item(item.id, rset.type)`),
  `get_set_stats` (un seul appel batché `get_for_items(item_ids, rset.type)`
  pour tout l'ensemble), `get_binder_stats` (`ids_by_type.setdefault(s.type,
  ...)`, groupe par type d'*ensemble*). Pour un ensemble homogène les deux
  valeurs coïncident, ce qui masque le bug. Pour un ensemble hétérogène,
  `rset.type` vaut `None`, `item_type == None` ne matche aucune session
  réelle (`item_type` n'est jamais null en pratique) : **les stats d'un
  ensemble hétérogène déjà révisé sont aujourd'hui silencieusement vides**
  (0 review partout), pas juste mal formées. Corrigé en même temps que le
  problème de schéma (`RevisionSetStats.type` non-nullable) — même fichier,
  même chantier, cf. § Backend.
- **`RevisionTypeBreakdown` (classeur) doit grouper par type d'*item*, pas
  par type d'*ensemble*.** Décision utilisateur : un ensemble hétérogène a
  des items de plusieurs types, donc `sets_count` par type devient « nombre
  d'ensembles ayant au moins un item de ce type » (un ensemble hétérogène
  compte dans plusieurs buckets simultanément — cohérent avec la réalité de
  ses items).
- **`item_label(set_type: str, payload: dict)` a un paramètre `set_type`
  déjà mort** (jamais utilisé dans le corps, seul `payload` sert) — nettoyage
  mineur à faire en passant, pas une correction de bug.
- **Aucune maquette existante** pour ces 3 écrans côté canevas Direction A
  (vérifié : pas de fichier `.dc.html` dans le dépôt, aucune mention dans
  `docs/`). `docs/ui-redesign-plan.md` confirme que ces 3 fichiers ont déjà
  reçu une migration mécanique des tokens de design (S8, indigo→`primary`
  etc.) — la charte visuelle est à jour, seule l'adaptation fonctionnelle à
  l'hétérogénéité manque.

## Périmètre

### Modifié

- `backend/app/schemas/revision_schema.py`
- `backend/app/services/revision_stats_service.py`
- `web/src/views/Reviews/Reviews.vue`
- `web/src/views/Reviews/RevisionSetStats.vue`
- `web/src/views/Reviews/RevisionBinderStats.vue`
- `web/src/router/index.ts` (route `/manage` supprimée ou redirigée)

### Supprimé

- `web/src/views/Reviews/RevisionSetManage.vue` + son fichier de test
  associé (retiré, pas migré — cf. décision ci-dessus).

### Explicitement hors périmètre

- `run_qcm` / passage scoré QCM (toujours au niveau de l'ensemble,
  `rset.type === 'qcm'`) — risque déjà accepté par `bibliotheque-ensembles`,
  non rouvert ici.
- Tout endpoint de suppression/action en masse par type — aucun n'existe,
  aucun n'est requis par ce chantier (les 3 écrans en scope sont en lecture
  seule côté stats, `Reviews.vue` ne fait que lister/naviguer).
- Refonte visuelle/tokens des 3 écrans (déjà faite, S8).

## Backend

### `revision_schema.py`

- `RevisionSetStats.type: str` → `str | None` (reflète `RevisionSet.type`
  nullable depuis D8, jamais aligné pour les schémas de stats).
- `RevisionSetSummary.type: str` → `str | None` (même raison, utilisé par
  `RevisionBinderStats.sets`/`weakest_sets`).
- `RevisionTypeBreakdown.type: str` — reste `str` non nul : après le passage
  au groupement par type d'*item* (jamais null en pratique), chaque clé du
  breakdown est un vrai type concret, il n'y a plus de bucket « mixte ».
- `RevisionItemSummary` gagne `type: str` (jamais null, un item a toujours
  un type concret) — nécessaire pour afficher l'icône/badge par item dans
  `RevisionSetStats.vue`.

### `revision_stats_service.py`

- `get_item_stats` : `self._session_dao.get_for_item(item.id, rset.type)` →
  `self._session_dao.get_for_item(item.id, item.type)`.
- `_aggregate_set` : `RevisionItemSummary(...)` gagne `type=item.type` ;
  `item_label(rset.type, item.payload)` → `item_label(item.payload)`
  (suppression du paramètre mort, cf. exploration).
- `get_set_stats` : la requête de sessions doit être groupée par type
  d'*item*, pas passée en un seul appel avec `rset.type`. Remplacer par le
  même motif que `get_binder_stats` (ci-dessous) à l'échelle d'un ensemble :
  grouper `item_ids` par `item.type`, un appel `get_for_items` par type
  distinct présent (≤ 6, généralement 1 pour un ensemble homogène), fusionner
  les résultats dans `by_item`. `RevisionSetStats(..., type=rset.type, ...)`
  inchangé (accepte déjà `None` après le changement de schéma).
- `get_binder_stats` : `ids_by_type.setdefault(s.type, []).append(it.id)`
  (groupe par type d'ensemble) → `ids_by_type.setdefault(it.type,
  []).append(it.id)` (groupe par type d'item) — correction d'une ligne, le
  reste de la boucle de fetch des sessions est déjà écrit pour itérer sur
  des groupes par type. `by_type_acc.setdefault(rset.type, [0, 0, 0])`
  (accumulateur du breakdown, actuellement par ensemble) devient une boucle
  interne sur les types *présents dans les items de cet ensemble* plutôt
  qu'une seule entrée par ensemble — un ensemble hétérogène incrémente
  `sets_count`/`items_count`/`mastered_count` dans chacun des buckets de
  types que ses items couvrent réellement (détail exact de la boucle
  imbriquée par item plutôt que par ensemble à trancher au moment du plan,
  sur la base des `item_summaries` déjà calculés par `_aggregate_set`, qui
  portent déjà `type` après le changement ci-dessus — pas de nouvelle
  requête nécessaire, uniquement une réorganisation de l'agrégation déjà en
  mémoire).

## Frontend

### `Reviews.vue`

- Nouvel onglet `Mixte` ajouté à la liste des onglets « Classiques »
  existants (même composant d'onglet, même style).
- `typedSets` (actuellement `revisionStore.sets.filter(s => s.type ===
  currentSetType.value)`) : pour l'onglet Mixte, filtre sur `s.type ===
  null` au lieu d'un `RevisionType`.
- Chaque ligne de l'onglet Mixte : nom, nombre d'éléments, dernier passage
  (mêmes champs que les lignes des onglets existants, réutilisation du
  même sous-composant/template de ligne si un est déjà extrait — sinon
  duplication minimale, à trancher au moment du plan selon la taille du
  diff). Clic → `router.push('/revision/sets/${set.id}')`
  (`RevisionSetDetail.vue`) au lieu du `/manage` actuel.
- Bouton « Gérer » : repointé de `/revision/sets/:id/manage` vers
  `/revision/sets/:id` (`RevisionSetDetail.vue`) sur **toutes** les lignes
  (onglets existants inclus, pas seulement Mixte) — même bouton, même
  libellé, seule la destination change. Cohérence : un seul chemin de
  gestion des items pour tout ensemble, homogène ou non. Le bouton « Stats »
  (`/revision/sets/:id/stats`) reste inchangé sur toutes les lignes, y
  compris Mixte.
- Pas de bouton « Créer » sur l'onglet Mixte (le `v-if="currentSetType"`
  existant le masque déjà naturellement, `currentSetType` valant `null` sur
  cet onglet) — création d'un ensemble hétérogène déjà possible depuis
  Bibliothèque, décision de ne pas dupliquer ce point d'entrée ici.
- `set.type === 'qcm' ? 'Lancer' : 'Étudier'` : inchangé pour les 5 onglets
  existants (jamais atteint pour l'onglet Mixte, `set.type` y est toujours
  `null` — le bouton de lancement de l'onglet Mixte pousse simplement vers
  `/revision/sets/:id/study`, jamais `/run`, cohérent avec le fait qu'un
  ensemble hétérogène ne peut jamais être un passage QCM scoré pur).

### `RevisionSetStats.vue`

- En-tête : badge de type actuel (`stats.type`) — affiche `Mixte` quand
  `stats.type === null`, même convention que `TeacherDashboard.vue`
  (`s.type ? s.type.toUpperCase() : 'MIXTE'`).
- Liste des items : reste une liste plate triable (pas de regroupement par
  type — le but de cet écran est de faire remonter les items individuels
  faibles/sangsues, un regroupement le desservirait). Chaque ligne gagne une
  icône/badge de type (`it.type`, désormais toujours renseigné par le
  backend), réutilisant le set d'icônes déjà utilisé dans
  `RevisionSetDetail.vue`.
- Édition d'un item depuis cette liste : `RevisionItemModal` accepte déjà
  `props.editItem?.type || props.lockedType || ...` — le type de l'item
  édité prime toujours sur `lockedType` en édition (correctif déjà fait par
  `bibliotheque-ensembles`, le sélecteur de type est d'ailleurs masqué en
  édition, `v-if="!isEdit && !lockedType"`). `:locked-type="stats?.type"`
  est donc déjà inerte pour ce flux, pas un bug fonctionnel — juste du code
  mort trompeur (laisse penser que `stats.type` pilote le type affiché).
  Retiré simplement (prop supprimée de l'appel), pas remplacé.

### `RevisionBinderStats.vue`

- `TYPE_LABELS: Record<RevisionType, string>` (5 entrées, sans `flashcard`)
  doit devenir `Record<RevisionItemType, string>` (6 entrées, + `Flashcards`)
  — le breakdown groupe désormais par type d'*item* réel (cf. § Backend),
  qui inclut `flashcard`, jamais couvert par `RevisionType` (type
  *homogène* d'ensemble, 5 valeurs seulement, `flashcard` ne peut jamais
  être le type d'un ensemble homogène). `typeLabel()` n'a plus besoin de
  gérer un cas « mixte » pour ce tableau (chaque clé est un type concret,
  jamais null) — seul le badge par ensemble (ci-dessous) doit gérer `null`.
- « Répartition par type » : consomme directement `by_type` (déjà groupé
  par item côté backend) — aucun changement de logique d'affichage, la
  donnée en entrée est simplement correcte pour la première fois pour un
  classeur contenant des ensembles hétérogènes.
- Badges de type sur les lignes ensemble (`weakest_sets`, `sets`) :
  `typeLabel(s.type)` doit gérer `s.type === null` → `Mixte` (même
  convention que `RevisionSetStats.vue`), au lieu du rendu vide actuel
  (`TYPE_LABELS[null]` est `undefined`, `undefined || null` s'affiche
  vide).

### `router/index.ts`

- Route `revision/sets/:id/manage` (`RevisionSetManage`) : supprimée. Si un
  lien externe/historique existe encore vers cette URL, ajouter une
  redirection vers `revision/sets/:id` (`RevisionSetDetail`) plutôt qu'un
  404 sec — à confirmer au moment du plan si un tel lien est trouvé ailleurs
  dans le code (la recherche préalable n'en a trouvé aucun en dehors de
  `Reviews.vue`, qui est lui-même modifié par ce chantier).

## États à couvrir (skill `migration-ecran` étape 2, par composant)

Chargement/erreur/vide déjà établis comme pattern à chaque écran de la
phase 4 (`BaseEmptyState` + retry). `Reviews.vue`, `RevisionSetStats.vue`,
`RevisionBinderStats.vue` ont déjà leurs états existants — à retester avec
les nouvelles données (type nullable, onglet Mixte, breakdown par item),
pas de nouveaux états à inventer.

## Tests

TDD strict (phase ≥ 3) :
- Backend, `test_revision_stats.py` (ou fichier existant équivalent, à
  vérifier au moment du plan) : un test reproduisant le bug avant correctif
  (ensemble hétérogène avec ≥ 2 types d'items révisés, `get_set_stats`
  retourne `reviewed_items > 0` et des `item_summaries` non vides avec le
  bon `type` par item) ; idem `get_item_stats` et `get_binder_stats`
  (breakdown par type reflète les items réels, pas les ensembles).
  Non-régression sur un ensemble homogène existant (comportement identique
  à avant).
- `Reviews.vue` : onglet Mixte liste bien les ensembles `type: null` et
  eux seuls, navigation vers `RevisionSetDetail.vue`, non-régression des 5
  onglets existants et du bouton « Gérer » retiré.
- `RevisionSetStats.vue` : badge Mixte, icône de type par item, édition
  d'item ouvre `RevisionItemModal` avec le bon type par item (pas un type
  unique pour tout l'écran).
- `RevisionBinderStats.vue` : badge Mixte sur une ligne d'ensemble
  hétérogène, breakdown par type reflète bien les items (test avec un
  classeur mêlant ensembles homogènes et hétérogènes).
- Suite complète + `vue-tsc -b` + suite backend complète à chaque étape
  (pattern des chantiers précédents).
- Vérification visuelle réelle clair/sombre × desktop/mobile en fin de
  plan — **faite en environnement natif hors Docker cette fois dès le
  départ** (leçon de `bibliotheque-ensembles` : ne pas la différer).

## Ce qui n'est pas fait ici

- `RevisionSetManage.vue` n'est pas adapté, il est supprimé (cf. décision).
- `run_qcm` reste au niveau de l'ensemble, non touché.
- Aucune nouvelle agrégation serveur au-delà de la correction du groupement
  existant (pas de nouvel endpoint).
- Pas de fusion/refonte de la navigation entre `Reviews.vue` et
  `Bibliothèque` au-delà de l'onglet Mixte — les deux écrans continuent de
  coexister avec leurs rôles actuels (décision utilisateur : adapter, pas
  simplifier/rediriger).

## Risque accepté

Le nouveau groupement de `RevisionTypeBreakdown` par type d'item (au lieu
de type d'ensemble) change la sémantique de `sets_count` par type dans la
réponse API `GET /revision/binders/:id/stats` — un ensemble hétérogène peut
désormais apparaître dans plusieurs buckets. Aucun consommateur externe de
cet endpoint identifié en dehors de `RevisionBinderStats.vue` (recherche à
confirmer au moment du plan) ; accepté comme un changement de comportement
correctif, pas un breaking change à versionner.
