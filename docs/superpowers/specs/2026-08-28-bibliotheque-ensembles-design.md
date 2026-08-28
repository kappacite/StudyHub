# Design — Frontend : Bibliothèque et ensembles de révision hétérogènes

Date : 2026-08-28. Statut : validé par l'utilisateur en chat, en attente de
relecture du présent document avant passage à `writing-plans`.

Chantier : `workflow/bibliotheque-ensembles/` (flux 3 et 4 d'`ETAT.md` §
« Plan global par flux — extension révision hétérogène + assistant IA »).
Dépend de `backend-ensembles-heterogenes` (flux 1), mergé (PR #126,
`d2b6305`) : `RevisionItem.type` existe, `RevisionSet.type` est optionnel,
le type `flashcard` est disponible côté item.

## Pourquoi

`Binders.vue` (renommé Bibliothèque en phase 3) doit exposer la bascule
Notes/Révision de la maquette Direction A et la liste des ensembles de
révision désormais hétérogènes (un ensemble peut mélanger flashcards, QCM,
vrai/faux, association, définition, ordre). Le backend le permet depuis le
2026-08-28 ; aucune interface ne le permet encore.

## Exploration faite avant de figer le périmètre (changé deux fois en
cours de route, cf. historique du chat)

- **`RevisionSetManage.vue` (`/revision/sets/:id/manage`) n'est PAS le futur
  écran de détail hétérogène** — sa maquette (`RevisionSetManage.dc.html`,
  breadcrumb « RÉVISER / SETS », nav active sur Réviser) est l'ancien écran
  homogène pré-hétérogène, utilisé par `Reviews.vue`. Il reste le
  territoire de `reviser-hub` (flux 6), non touché ici.
- **`RevisionSetDetail.dc.html` existe séparément** (nav active sur
  Bibliothèque, breadcrumb « BIBLIOTHÈQUE / … / RÉVISION ») — c'est le vrai
  écran neuf de ce chantier. Ses lignes affichent un compte par type
  (« Flashcards · 42 cartes », « QCM · 8 questions »...) plutôt qu'un item
  atomique par ligne. **Décision utilisateur** : c'est un regroupement
  visuel par type (libellé générique + compte), pas un troisième niveau de
  hiérarchie réel — aucun champ de données supplémentaire nécessaire, les
  noms de la maquette (« Mécanismes clés »...) sont de l'habillage
  illustratif.
- **`RevisionStudy.vue` (`/revision/sets/:id/study`) est cassé pour un
  ensemble hétérogène** : il lit `setType = set.type` une seule fois et
  choisit le template de rendu sur cette base (`v-if="setType === 'vf'"`,
  etc.) pour tous les items de la session — avec `set.type === null`,
  aucun template ne matche, et la branche `flashcard` n'existe même pas.
  **Décision utilisateur** : inclus dans ce chantier (dépendance dure du
  bouton « Réviser l'ensemble » que les deux écrans exposent), alors qu'il
  n'était revendiqué par aucun chantier existant.
- **`RevisionItemModal.vue` existe déjà** et gère déjà les 6 types de
  payload — mais son modèle de cible (`itemType` détermine la cible,
  filtrée par correspondance type↔ensemble) est incompatible avec un
  ensemble hétérogène. Adapté, pas remplacé.
- **`RevisionSetModal.dc.html` (nom + description) et
  `RevisionSetDetail.dc.html` n'ont pas d'équivalent dans le code actuel** —
  composants réellement neufs, pas de doublon.
- **Aucun gap backend** : `RevisionSet.description` existe déjà en base et
  dans les schémas Pydantic (vérifié), `updateSet`/`createSet` du store
  n'ont besoin que d'une extension de signature, pas d'un nouvel endpoint.

## Périmètre

### Modifié

- `web/src/stores/revision.ts`
- `web/src/components/decks/RevisionItemModal.vue`
- `web/src/views/Binders/Binders.vue`
- `web/src/views/Reviews/RevisionStudy.vue`

### Nouveau

- `web/src/components/decks/RevisionSetModal.vue`
- `web/src/views/Reviews/RevisionSetDetail.vue`
- `web/src/views/Reviews/RevisionSetTypeItems.vue`

### Explicitement hors périmètre (reste à `reviser-hub`, flux 6)

`Reviews.vue`, `RevisionSetManage.vue` (`/manage`), `RevisionSetStats.vue`,
`RevisionBinderStats.vue`. Aucun de ces fichiers n'est modifié par ce plan.

## Modèle de données côté frontend (`revision.ts`)

- `RevisionSet.type` : `RevisionType` → `RevisionType | null` (reflète le
  backend, `null` = ensemble hétérogène).
- Nouveau `RevisionItemType = RevisionType | 'flashcard'` (6 valeurs, item
  seulement — `RevisionType`, 5 valeurs, reste utilisé pour le type
  *homogène* d'un ensemble et pour le payload générique).
- `RevisionItem` gagne `type: RevisionItemType`, `created_at: string`,
  `updated_at: string` (nécessaires pour le libellé « dernier passage » par
  groupe de type dans `RevisionSetDetail.vue` — `updated_at` est mis à jour
  par le backend à chaque notation SM-2 d'un item, utilisé comme proxy de
  « dernier passage »).
- `RevisionItemPayload` gagne `front?: string; back?: string` (flashcard).
- `createSet(name, type: RevisionType | null, description?, binderId?,
  tuningDefault?)` — `type: null` pour un ensemble hétérogène créé depuis
  `RevisionSetModal`.
- `createItem(setId, payload, type?: RevisionItemType, tuning?)` — `type`
  transmis au backend (`RevisionItemCreate.type`), absent = comportement
  actuel inchangé (retombe sur le type de l'ensemble côté backend).

## Composants

### `RevisionItemModal.vue`

Le sélecteur de type (6 boutons) reste actif et libre quand `lockedSetId`
est fourni — retrait de la contrainte `lockedType` qui filtrait `targets`
par correspondance type↔ensemble. `submit()` passe désormais `itemType`
explicitement à `revisionStore.createItem`/`updateItem`. Le flux « nouvel
ensemble à la volée » (`targetChoice === NEW_TARGET`, sans `lockedSetId`)
reste inchangé — hors périmètre de ce chantier (utilisé par `Reviews.vue`),
mais continue de fonctionner puisque `createSet` accepte toujours un `type`
non nul dans ce cas.

### `RevisionSetModal.vue` (nouveau)

Props : `{ mode: 'create' | 'edit', binderId: string | null, set?:
RevisionSet }`. Champs : nom (obligatoire), description (optionnel).
Création : `revisionStore.createSet(name, null, description, binderId)` —
toujours hétérogène (`type: null`), décision utilisateur actée. Édition :
`revisionStore.updateSet(set.id, { name, description })`. Émet `created:
[RevisionSet]` / `updated: []` / `close: []`. Composé avec `BaseModal`,
`BaseField`, `BaseInput` (primitives existantes, aucune nouvelle).

### `RevisionSetDetail.vue` (nouveau, route `/revision/sets/:id`)

En-tête : fil d'ariane (classeur parent, lien vers `Binders.vue`), nom +
crayon (`RevisionSetModal` édition), description, bouton « Réviser
l'ensemble » (`/revision/sets/:id/study`, sans filtre). Sous cet en-tête :
une ligne par type d'item **présent** dans l'ensemble (calculée
côté client depuis `GET /revision/sets/:id/items`, groupé par
`item.type` — pas de nouvel endpoint d'agrégation nécessaire, les
ensembles restent de taille modeste) :
- icône + libellé générique du type (« Flashcards », « QCM », « Vrai /
  Faux »...), compte, « dernier passage » (`updated_at` le plus récent du
  groupe, ou « jamais » si tous `null`/jamais notés).
- 3 actions : **Réviser** (`/revision/sets/:id/study?type=<type>`, session
  filtrée à ce type) ; **Éditer** (navigue vers `RevisionSetTypeItems.vue`,
  route `/revision/sets/:id/items/:type`) ; **Supprimer** (confirmation
  « Supprimer les N <type> de cet ensemble ? », boucle client sur
  `revisionStore.deleteItem` pour chaque item du groupe — pas de endpoint
  de suppression en masse côté backend, jugé suffisant vu la taille
  réaliste d'un ensemble personnel).
Bouton « Ajouter un élément » : ouvre `RevisionItemModal` avec
`lockedSetId` (type libre, cf. ci-dessus).
État vide (aucun item) : `BaseEmptyState`, action « Ajouter un élément ».
États chargement/erreur : même pattern que les écrans 2-4 (`BaseEmptyState`
+ retry sur échec de `GET .../items`).

### `RevisionSetTypeItems.vue` (nouveau, route
`/revision/sets/:id/items/:type`)

Reprend le pattern éprouvé de `RevisionSetManage.vue` (liste + modale +
suppression) mais filtré à un seul type au sein d'un ensemble
potentiellement hétérogène : charge `GET .../items`, filtre côté client sur
`item.type === route.params.type`, affiche un intitulé lisible par item
(réutilise `itemLabel()` — logique à dupliquer localement ou extraire en
utilitaire partagé, décidé au moment du plan selon la taille du diff).
`RevisionItemModal` ouvert avec `lockedSetId` **et** `lockedType` = le type
de la route (ici la contrainte de type reste voulue : cette sous-page ne
gère qu'un seul type à la fois). Fil d'ariane retourne vers
`RevisionSetDetail.vue`.

### `RevisionStudy.vue` (modifié)

- `onMounted` : ne route plus vers `/run` uniquement si `set.type ===
  'qcm'` **et absence de filtre `?type=`** — un ensemble hétérogène
  (`set.type === null`) ne peut de toute façon jamais matcher `'qcm'` ici,
  donc ce garde-fou reste correct tel quel sans modification.
- `items` filtré côté client sur `route.query.type` si présent (études
  filtrées par type depuis `RevisionSetDetail`), sinon tous les items de
  `fetchStudyItems` (étude mixte, tous types).
- Le gabarit de rendu par item bascule de `v-if="setType === '...'"`
  (unique pour toute la session) à `v-if="current.type === '...'"`
  (réévalué à chaque item) — chaque branche existante (`vf`, `definition`,
  `association`, `ordre`) reste inchangée dans son contenu, seule la
  condition change de source.
- **Nouvelle branche `flashcard`** : recto (`payload.front`), bouton
  « Révéler le verso », puis verso (`payload.back`) + auto-évaluation 1/3/5
  (À revoir/Moyen/Acquis) — calque exact du gabarit `definition` existant
  (même famille non auto-corrigée côté backend, `check_answer("flashcard",
  ...)` retourne toujours `False`).
- L'étiquette d'en-tête (`TYPE_LABELS[setType] || 'Révision'`) devient
  générique (« Révision · {{ setName }} », sans dépendre d'un type unique)
  quand la session est mixte (pas de `?type=`) ; garde le libellé
  spécifique quand `?type=` est présent.

### `Binders.vue` (modifié)

- Les 6 onglets actuels (Tout/Notes/Decks/Ensembles/Diagrammes/PDF)
  deviennent **3 onglets** : **Notes**, **Révision** (fusion Decks +
  Ensembles, hétérogène), **Autres** (Diagrammes + PDF, décision
  utilisateur explicite pour ne perdre aucune fonctionnalité malgré
  l'absence de ces types dans la maquette à 2 onglets). Dossiers (colonne
  gauche, `SplitView`) et filtre par tag inchangés, indépendants des
  onglets.
- Section Révision : une ligne par ensemble (`revisionStore.sets` +
  anciens `decksStore.decks` fusionnés visuellement — **décision à
  documenter dans le plan** : les `Deck`/`Flashcard` classiques restent un
  système séparé côté backend (hors périmètre du chantier backend), donc
  cette fusion est **visuelle uniquement** dans la liste, chaque ligne
  gardant sa navigation propre (`/decks/:id/study` pour un deck existant,
  `/revision/sets/:id` pour un ensemble) — pas de tentative de les unifier
  en un seul type de données.
- Bouton primaire contextuel (remplace le bouton statique actuel) : «
  Nouvelle note » (onglet Notes) / « Nouvel ensemble » (onglet Révision,
  ouvre `RevisionSetModal` création) / label adapté (onglet Autres). Le
  menu « Ajouter » existant (Sous-dossier, Élément existant) reste
  disponible tel quel, quel que soit l'onglet actif — inchangé.
- Ligne d'ensemble : icône générique, nom, « N éléments · dernier passage
  {…} », mini-icônes des types présents (calculées côté client depuis
  `GET .../items` par ensemble affiché, même principe que
  `RevisionSetDetail.vue` — aucune agrégation serveur nouvelle, cf. « Ce
  qui n'est pas fait ici »), badge « N dues »
  si `> 0` (calcul déjà fait ailleurs dans l'app pour les decks, à
  retrouver/réutiliser). 3 actions : Réviser (`/revision/sets/:id/study`),
  Éditer (`RevisionSetModal` édition), Supprimer (`revisionStore.deleteSet`
  + confirmation, pattern déjà utilisé par `Reviews.vue`). Clic sur la
  ligne (hors icônes) → `RevisionSetDetail.vue`.

## États à couvrir (skill `migration-ecran` étape 2, par composant)

Chargement/erreur/vide déjà établis comme pattern à chaque écran de la
phase 4 (`BaseEmptyState` + retry) — appliqué à `RevisionSetDetail.vue`
(échec `GET .../items`) et `RevisionSetTypeItems.vue`. `Binders.vue` a déjà
ses états (chargement global, dossier vide) — pas de nouveau code, à
retester avec la nouvelle structure à 3 onglets.

## Tests

TDD strict (phase ≥ 3), un fichier de test par composant nouveau/modifié,
suite complète + `vue-tsc -b` à chaque étape (pattern des écrans 1-4) :
- `revision.ts` : tests des nouvelles signatures (`createSet` avec `type:
  null`, `createItem` avec `type` explicite).
- `RevisionItemModal.vue` : sélecteur de type visible et fonctionnel avec
  `lockedSetId` fourni (régression : vérifier que le flux existant sans
  `lockedSetId`, utilisé par `Reviews.vue`, n'est pas cassé).
- `RevisionSetModal.vue` : mode création (type: null) et édition, deux
  tests dédiés.
- `RevisionSetDetail.vue` : groupement par type, actions par ligne
  (réviser filtré/éditer/supprimer en masse avec confirmation), état
  vide/erreur.
- `RevisionSetTypeItems.vue` : filtrage par type, CRUD d'item verrouillé
  sur ce type.
- `RevisionStudy.vue` : dispatch par `item.type` sur une session mixte
  (au moins 2 types différents dans les items de test), branche
  `flashcard` (révéler + auto-éval), filtre `?type=`, non-régression sur
  les 4 branches existantes (vf/definition/association/ordre) et sur la
  redirection QCM.
- `Binders.vue` : 3 onglets, fusion Decks+Ensembles dans Révision, bouton
  primaire contextuel, non-régression sur Dossiers/tags/Diagrammes/PDF
  (juste déplacés sous « Autres », comportement inchangé).
- Vérification visuelle réelle clair/sombre × desktop/mobile en fin de
  plan (pattern établi, étape 7 de `migration-ecran`).

## Ce qui n'est pas fait ici

- `Reviews.vue`, `RevisionSetManage.vue`, `RevisionSetStats.vue`,
  `RevisionBinderStats.vue` : aucun changement (territoire `reviser-hub`).
- `Deck`/`Flashcard` (système classique) : aucune fusion de données avec
  `RevisionSet`/`RevisionItem` — la fusion dans `Binders.vue` est purement
  visuelle (liste commune), pas une migration de modèle.
- `run_qcm` / passage scoré QCM : toujours au niveau de l'ensemble
  (`rset.type === 'qcm'`), non adapté ici — risque déjà accepté
  explicitement dans le spec backend, non rouvert.
- Aucune agrégation serveur nouvelle : les compteurs par type
  (`RevisionSetDetail.vue`, mini-icônes de `Binders.vue`) sont calculés
  côté client depuis la liste d'items déjà exposée — à confirmer au moment
  du plan que ça reste performant pour la taille réelle des ensembles.

## Risque accepté

Suppression en masse par type (`RevisionSetDetail.vue`) : boucle
client de N appels `DELETE` individuels plutôt qu'un endpoint de
suppression en masse — accepté pour la taille réaliste d'un ensemble
personnel, à revoir si des ensembles de plusieurs centaines d'items
apparaissent en pratique.
