# Design — Backend : type au niveau de l'item de révision (ensembles hétérogènes)

Date : 2026-08-28. Statut : validé par l'utilisateur en chat, en attente de
relecture du présent document avant passage à `writing-plans`.

Chantier : `workflow/backend-ensembles-heterogenes/` (flux 1 d'`ETAT.md` §
« Plan global par flux — extension révision hétérogène + assistant IA »).

## Pourquoi

Le canevas Direction A (Claude Design) modélise des ensembles de révision
hétérogènes : un même ensemble peut mélanger plusieurs types d'éléments
(Flashcards, QCM, Vrai/Faux, Association, Définition, Ordre). Décision
utilisateur du 2026-08-27 : garder le canevas tel quel, quitte à imposer
« une vraie migration de schéma plutôt qu'un ajout ». Aujourd'hui,
`RevisionSet.type` est **au niveau de l'ensemble** (homogène par construction
— décision d'archi antérieure « D3c ») : impossible de mélanger des types
dans un même ensemble sans déplacer `type` au niveau de l'**item**.

## Découverte faite en explorant le code (change le périmètre initial)

Le champ `type` existe déjà en double apparence : `RevisionSet.type` (5
valeurs : `qcm`/`vf`/`association`/`definition`/`ordre`) et
`Flashcard.card_type` (`basic`/`qcm`/`vf`/`ordre`/`assoc`). **Ce n'est pas
une vraie duplication** : `Flashcard.card_type`/`payload` sont du code mort
— jamais lus ni écrits ailleurs dans le backend, absents des schémas
Pydantic exposés (`FlashcardCreate`/`Update`/`Response`), et
`flashcard_schema.py` porte lui-même le commentaire confirmant la décision
D3c (« une flashcard est strictement recto/verso »).

En revanche, une vraie fusion `Deck`/`Flashcard` → `RevisionSet`/
`RevisionItem` toucherait **47 fichiers backend** répartis sur quasiment
tous les sous-systèmes (`class_service`, `community_service`,
`deck_service`, `evaluation_service`, `exam_service`, `flashcard_service`,
`focus_service`, `import_service` [Anki], `planning_service`,
`quiz_service`, `stats_service`) plus le frontend déjà migré
(`StudyDeck.vue`, `Decks.vue`). C'est plus gros à lui seul que les 9 écrans
UI combinés — **décomposé en chantiers séquentiels**, chacun avec son
propre plan/PR, ouverts plus tard. Ce chantier-ci ne couvre que le socle
schéma décrit ci-dessous ; il ne touche à aucune ligne `Deck`/`Flashcard`
existante ni à aucun des 8 sous-systèmes.

## Contrainte de rétrocompatibilité (découverte en explorant le frontend)

`RevisionSet.type` est **activement utilisé aujourd'hui** par le frontend
déjà en production (non migré vers le design system, mais fonctionnel) :
`Reviews.vue` (navigation `run` vs `study`, filtrage par type),
`RevisionSetManage.vue`/`RevisionSetStats.vue` (`locked-type`),
`RevisionStudy.vue` (branchement QCM), `RevisionBinderStats.vue`
(étiquettes). Supprimer purement `RevisionSet.type` casserait ces écrans
immédiatement. La conception ci-dessous le garde donc en place.

## Schéma cible

- **`RevisionItem` gagne une colonne `type`** (`String(20)`, nullable).
  Migration Alembic : backfill de tous les items existants avec le `type`
  de leur `RevisionSet` parent (opération interne aux tables
  `revision_items`/`revision_sets` déjà en place — aucune donnée
  `Deck`/`Flashcard` impliquée).
- **`RevisionSet.type` reste en place**, mais devient sémantiquement
  optionnel : renseigné = ensemble homogène (comportement actuel,
  inchangé) ; `NULL` = ensemble hétérogène (nouveau — pas encore créable
  tant que le chantier `bibliotheque-ensembles` n'a pas livré son UI, donc
  aucun set réel n'aura `NULL` avant ça). Colonne DB passe `nullable=True`
  (elle est actuellement `nullable=False`).
- **`RevisionItemCreate.type` devient optionnel** (`Optional[str] = None`).
  Si absent (tous les appels actuels du frontend non migré), `create_item`/
  `update_item` retombent sur le `type` de l'ensemble parent — **aucune
  régression sur le flux existant**. Si présent, il prime (futurs appels
  hétérogènes, une fois le frontend `bibliotheque-ensembles` livré).
- **`RevisionItemResponse` gagne le champ `type`** (reflète la colonne).
- **`validate_item_payload`/`check_answer` prennent le `type` de l'item**,
  pas de l'ensemble, et gagnent un 6ᵉ cas :
  - `"flashcard"` : payload `{front: str, back: str}` (les deux non vides).
    Jamais auto-corrigé — même famille que `"definition"` (auto-évaluation
    à l'étude, pas de `check_answer` dédié).
- **Correction faite en écrivant le plan détaillé** : `GRADABLE_TYPES`
  doit en fait être vérifié contre **`item.type`**, pas `rset.type`, dans
  `grade_item`. Raison trouvée en traçant le nouveau chemin `type`
  explicite (`RevisionItemCreate.type`) : rien n'empêche de créer un item
  `"flashcard"` dans un ensemble `"vf"` **dès ce chantier** (c'est
  justement ce que ce chantier rend possible) ; avec l'ancien gate sur
  `rset.type`, un tel item passerait la vérification (`"vf"` est
  corrigeable) puis `check_answer` recevrait un payload flashcard
  interprété comme un payload `vf` — notation silencieusement fausse, pas
  un cas hypothétique différé. `answer_item` (chemin non auto-corrigé)
  utilise de même `item.type` pour `StudySession.item_type` — coût nul
  (valeur identique à `rset.type` pour toute donnée réelle actuelle),
  correction par construction.
- **`run_qcm` reste inchangé** (gate toujours sur `rset.type == "qcm"` au
  niveau de l'ensemble) — même classe de risque théorique qu'un item
  divergent y soit mal traité, mais accepté explicitement (cf. « Risque
  accepté ») plutôt que de redessiner le mode passage scoré dans ce
  chantier ; `reviser-hub` s'en chargera avec la vraie UI d'ensembles
  mixtes.

## Flux de données (exemple : création d'un item)

1. Frontend actuel (non modifié par ce chantier) : `POST
   /revision-sets/{id}/items` sans champ `type` dans le corps.
2. `RevisionItemCreate.type` = `None` (valeur par défaut).
3. `RevisionService.create_item` : `item_type = data.type or rset.type`.
4. `validate_item_payload(item_type, data.payload)` — dispatch identique à
   avant (car `item_type == rset.type` dans ce flux), avec le nouveau cas
   `"flashcard"` disponible pour de futurs appels explicites.
5. `RevisionItem(type=item_type, payload=..., ...)` créé.

## Tests

TDD strict (phase ≥ 3). Suite `backend/tests/` existante pour
`revision_service`/`revision_dao`/route `revision-sets` — chaque
comportement listé ci-dessus reçoit un test avant le code :
- Backfill de migration : test de migration Alembic (upgrade puis
  vérification que chaque item a bien le `type` de son ensemble parent).
- `create_item`/`update_item` sans `type` → comportement identique à avant
  (non-régression, cas le plus important).
- `create_item`/`update_item` avec `type` explicite différent du type de
  l'ensemble → l'item prend le type explicite.
- `validate_item_payload("flashcard", {...})` : cas valide, cas invalide
  (front/back manquant).
- `check_answer("flashcard", ...)` : retourne `False` (jamais
  auto-corrigé, comme `"definition"` aujourd'hui).
- Coverage ≥ 80 % maintenu (garde CI existante).

## Ce qui n'est pas fait ici

- Aucune ligne `Deck`/`Flashcard` copiée ou touchée.
- Aucun des 8 sous-systèmes consommateurs de `Deck`/`Flashcard` modifié.
- Aucun changement frontend (`bibliotheque-ensembles`/`reviser-hub`
  restent responsables de l'UI des ensembles mixtes).
- `run_qcm`/`GRADABLE_TYPES` ne sont pas réécrits pour opérer par item —
  seulement rendus non-cassants pour l'existant.
- Pas de dépréciation de `Flashcard.card_type`/`payload` (code mort laissé
  tel quel, hors périmètre — signalé pour un futur nettoyage technique).

## Risque accepté

`RevisionSet.type` et `RevisionItem.type` peuvent temporairement diverger
si un futur code met à jour l'un sans l'autre — accepté car aucun chemin
actuel ne le permet (le seul créateur d'ensemble encore actif passe
toujours par le flux homogène ci-dessus) ; les chantiers frontend futurs
devront explicitement gérer la cohérence quand les ensembles mixtes
deviendront réellement créables.

`run_qcm` ne filtre pas par type d'item (contrairement à `grade_item`,
corrigé ci-dessus) : un item de type divergent (ex. `"flashcard"`) créé
dans un ensemble `"qcm"` et inclus dans un passage scoré serait traité
comme un QCM vide plutôt que de lever une erreur explicite. Accepté
explicitement — ce mode de passage scoré nécessite une vraie réflexion
sur son comportement face à un ensemble mixte, hors périmètre de ce
chantier ; `reviser-hub` s'en chargera avec la UI réelle.
