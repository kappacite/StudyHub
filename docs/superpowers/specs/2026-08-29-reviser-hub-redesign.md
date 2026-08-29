# Correction — reviser-hub : les vraies maquettes Direction A n'avaient pas été consultées

Date : 2026-08-29. Statut : validé par l'utilisateur en chat. Ce document **corrige et étend**
`docs/superpowers/specs/2026-08-29-reviser-hub-design.md` — il ne le remplace pas entièrement,
voir § Ce qui reste valide de l'ancien spec.

## Constat

Le spec original affirmait « Aucune maquette existante pour ces 3 écrans côté canevas Direction
A (vérifié : pas de fichier `.dc.html` dans le dépôt) ». C'était faux : la recherche n'avait
porté que sur le dépôt local. Les maquettes réelles vivent dans l'artefact Claude Design publié
(`https://claude.ai/code/artifact/366dcc95-8da4-41dd-8bbd-1e625a68e2c5`, référencé depuis
`ETAT.md`/`docs/development_journal.md`), jamais ouvert pendant le brainstorming de ce chantier —
répétition exacte de l'erreur documentée dans la mémoire `migration-ecran-verify-mockup`
(« ne jamais conclure "pas de restructuration nécessaire" sans avoir ouvert la vraie maquette »).

Les 4 fichiers `.dc.html` pertinents ont été extraits et lus (procédure dans la mémoire
`extract-claude-design-mockup`) :
- `Reviser.dc.html` → `Reviews.vue`
- `RevisionSetStats.dc.html` → `RevisionSetStats.vue`
- `RevisionBinderStats.dc.html` → `RevisionBinderStats.vue`
- `RevisionSetManage.dc.html` → confirme la décision déjà prise (retiré, pas migré, cf. ci-dessous)

Copies locales pour référence pendant l'implémentation (re-extraire si besoin via le script dans
la mémoire `extract-claude-design-mockup` — ces fichiers ne sont pas commités, c'est un
scratch) :
`C:\Users\denoe\AppData\Local\Temp\claude\C--Users-denoe-Documents-Projets-StudyHub\7989288f-bdab-487c-b7fd-913c45f96b5c\scratchpad\{Reviser,RevisionSetStats,RevisionBinderStats,RevisionSetManage}.dc.html`

## `RevisionSetManage.dc.html` : décision existante confirmée, rien à changer

La maquette montre un éditeur nom/matière + une liste plate de « Questions du set » (une seule
paire question/réponse par ligne, aucun badge de type, breadcrumb « RÉVISER / SETS »). C'est
exactement l'écran homogène pré-hétérogène déjà identifié par `bibliotheque-ensembles` comme
obsolète, remplacé par `RevisionSetDetail.dc.html` (groupé par type, breadcrumb Bibliothèque).
**Aucun changement** : Task 9 (retrait de `RevisionSetManage.vue`, redirection vers
`RevisionSetDetail.vue`) reste correcte telle quelle.

## `Reviser.dc.html` : refonte complète, pas un patch des onglets existants

La maquette n'a **ni onglets, ni section IA, ni gestion de decks**. C'est un flux unifié « ce qui
est dû », toutes sources confondues (Deck classique, Série QCM/ensemble de révision, Feuille
blanche/blurting), en 3 sections :
- **Bandeau résumé** : icône, « N cartes et M séries vous attendent aujourd'hui », sous-texte
  sur le retard, bouton « Tout réviser ».
- **En retard** (`--danger`, liseré rouge) : items en retard, un badge de type par ligne
  (`.type-badge`, pastille mono/majuscule — voir la maquette pour les couleurs exactes par type),
  nom, méta (`N cartes · dernier passage il y a X jours`), bouton « Réviser ».
- **Aujourd'hui** (`--highlight`, liseré ocre) : même structure, items dus aujourd'hui non en
  retard.
- **À venir** (gris neutre) : mêmes lignes mais sans bouton actionnable, une étiquette « DEMAIN »
  / « N JOURS » à la place.

Chaque ligne clique vers l'écran d'étude adapté à sa source (`/decks/:id/study` pour un Deck,
`/revision/sets/:id/study` — ou `/run` si l'ensemble est homogène QCM — pour un ensemble de
révision).

**Décision utilisateur (option recommandée retenue)** : refonte fidèle à la maquette. Les 4
onglets IA (Évaluation, Feuille blanche, Feynman, Quiz Auto-QCM) et la section « Decks de
Répétition Espacée » (création/génération de decks) sont retirés de cet écran — la maquette ne
les montre pas. 3 des 4 ont déjà une route dédiée au contexte d'une note
(`notes/:id/evaluation` → `NoteEvaluation.vue`, `notes/:id/quiz` → `NoteQuiz.vue`,
`notes/:id/blurting` → `Blurting.vue`) : rien à faire pour ces trois, la fonctionnalité reste
accessible depuis Notes/Bibliothèque. **Feynman n'a pas de route dédiée aujourd'hui** — sa seule
existence actuelle est l'onglet retiré. Une maquette `NoteFeynman.dc.html` existe déjà dans le
même artefact (jamais implémentée) : ce chantier crée `web/src/views/Notes/NoteFeynman.vue` +
route `notes/:id/feynman`, à partir de cette maquette, pour ne perdre aucune fonctionnalité
réelle. La gestion de decks (création, génération IA) reste accessible via `Decks.vue`
(`/decks`, déjà l'écran dédié) — vérifié que la création y est déjà possible, aucune
fonctionnalité perdue.

### Gap backend : `focus_service.py` ne connaît pas les ensembles de révision

`FocusService.get_today_items` (source de `GET /focus/today`, déjà consommé par le bandeau
« focus » d'`Accueil.vue` et par `Reviews.vue`) agrège aujourd'hui `Deck`/`Flashcard`, `Note`
(blurting) et `Assignment` — chacun dans son propre bloc de requêtes, combinés en une seule liste
`FocusItemSchema` à la fin. **`RevisionSet`/`RevisionItem` n'y figurent pas du tout.**

Ce n'est **pas** la fusion `Deck`/`RevisionSet` à 47 fichiers déjà écartée par
`backend-ensembles-heterogenes` (`docs/superpowers/specs/2026-08-28-backend-ensembles-heterogenes-design.md`,
§ modèle cible) — cette fusion concernait un remplacement de schéma (`Flashcard` → `RevisionItem`
comme même table). Ici il s'agit d'ajouter un **4ᵉ bloc de requêtes en lecture seule**, exactement
sur le modèle des 3 blocs existants (`deck_items`/`note_items`/`assignment_items`), qui interroge
`RevisionItem`/`RevisionSet` et produit des `FocusItemSchema` au même format — aucune fusion de
modèle, aucun des 47 fichiers cités n'est concerné.

**Nouveau bloc `revision_items`** dans `FocusService.get_today_items` :
- Items dus : `RevisionItem.next_review <= now`, join `RevisionSet` sur `user_id == user_id`
  (même filtre d'appartenance que le reste de la méthode).
- Un `FocusItemSchema` par item dû, pas par ensemble (chaque item a son propre `next_review`) —
  `type="revision_item"` (nouvelle valeur, à ajouter à `FocusItemSchema.type` — actuellement
  `Literal['deck', 'note', 'assignment']` côté frontend `FocusItem`, à élargir).
- `title` : nom de l'ensemble parent + libellé du type d'item (réutiliser `item_label()` de
  `revision_stats_service.py` pour le texte de la question/carte, tronqué) — à trancher au moment
  du plan pour rester lisible sur une ligne (la maquette montre le nom du set, pas de l'item
  individuel : `count` agrège plutôt tous les items dus d'un même ensemble sous une seule ligne,
  à la manière du bloc `deck_items` existant qui groupe déjà par deck plutôt que par carte
  individuelle — **suivre ce même principe de groupement par ensemble**, pas par item, pour
  rester cohérent avec le motif déjà établi et avec la maquette qui montre une ligne par
  série/deck, jamais par carte).
- `is_late` : au moins un item du groupe avec `next_review` de plus de 24h (même seuil que le
  bloc `deck_items` existant, `one_day_ago`).
- `id` : id de l'ensemble (`RevisionSet.id`), cohérent avec le fait que le clic doit mener à
  `/revision/sets/:id/study`.

**Nouveau type de badge frontend** : la maquette distingue visuellement `Deck` / `Série QCM` /
`Feuille blanche` par un badge coloré (voir `.type-badge` dans le mockup pour les couleurs
exactes). Un item de révision peut être n'importe lequel des 6 types — le badge doit refléter le
type réel de l'ensemble concerné (nom générique du type dominant, ou « Série » générique si
mélange — à trancher au moment du plan selon ce qui reste lisible).

## `RevisionSetStats.dc.html` : refonte complète

Structure de la maquette (à relire directement dans le fichier extrait pour les valeurs
exactes — ne pas deviner) :
- En-tête : fil d'ariane mono « Réviser · Statistiques », titre = nom de l'ensemble, sous-titre
  (nombre d'items · description), bouton « Réviser cette série ».
- Grille 2 colonnes : (1) carte « Taux de réussite global » — gros pourcentage + tendance +
  phrase sur le nombre de sessions + facteur de facilité moyen, puis un mini bar-chart « Par
  notation SM2 » (4 barres : Enc./Diff./Bien/Fac. — dérivable directement des `grade` 1-5 déjà
  stockés par item, bucketing à définir au moment du plan) ; (2) carte « Progression dans le
  temps » — bar-chart 6 semaines + trio de stats (cartes mûres / temps cumulé / série en cours).
- Carte « Historique des sessions » — table date/cartes vues/score/durée.

**Écart assumé, pas de nouvelle infra de tracking** : `duration_seconds` vaut toujours `0` sur
chaque `StudySession` créée par `answer_item`/`grade_item` (jamais de vrai suivi de durée pour
les items de révision, contrairement au flux Deck/Flashcard qui poste une durée réelle via
`POST /stats/sessions`). Construire un vrai regroupement par « session d'étude » avec durée
réelle demanderait de faire remonter un suivi de session côté `RevisionStudy.vue` (écran d'un
autre chantier, hors périmètre ici) — **non fait**. Approximation retenue : grouper les
`StudySession` d'un ensemble par jour calendaire, afficher date/nombre de cartes vues/score % (
tout dérivable de ce qui existe), **omettre la colonne durée** plutôt que d'afficher une fausse
valeur à 0. « Temps cumulé » (trio de stats) : idem, omis ou remplacé par une métrique réelle
disponible (ex. nombre total de révisions) — à trancher au moment du plan, ne jamais inventer une
donnée.

Ce qui reste inchangé de l'ancien spec pour cet écran : le badge de type (Mixte / type concret)
en en-tête, le retrait du prop `locked-type` inerte — ces deux points s'intègrent dans la
nouvelle structure sans contradiction.

## `RevisionBinderStats.dc.html` : refonte complète

- 4 cartes stat en grille : Cartes totales / Cartes maîtrisées (+ %) / Temps total d'étude /
  Série en cours. « Temps total d'étude » a le même problème de donnée que ci-dessus (jamais
  tracké pour les ensembles de révision) — même traitement (omettre ou remplacer par une
  métrique réelle, ne pas inventer).
- **« Répartition par deck et série »** (pas « par type ») : une ligne par ensemble (deck
  classique OU ensemble de révision), avec sa propre barre de maîtrise %. La maquette mélange
  les deux domaines dans une seule liste. Comme `Binders.vue` (`bibliotheque-ensembles`) le fait
  déjà pour la liste des classeurs (fusion **visuelle uniquement**, deux sources de données
  combinées côté frontend, aucune fusion de modèle), ce composant peut interroger
  `GET /revision/binders/:id/stats` (ensembles) **et** les decks du classeur (`decksStore` +
  `GET /stats/decks/:id` par deck, déjà utilisé ailleurs dans le code, ex. `Reviews.vue`) puis
  fusionner les deux listes triées par maîtrise décroissante — aucun nouvel endpoint backend,
  agrégation frontend seule.
- La répartition par type d'item (déjà corrigée côté backend, Task 4) n'apparaît plus comme
  widget principal dans cette maquette — décision à prendre au moment du plan : soit on la retire
  de l'écran (fidélité totale à la maquette), soit on la garde en complément sous « Répartition
  par deck et série » (les deux ne sont pas contradictoires, juste la maquette n'en montre qu'un).
  **Retenu : la garder en complément**, en dessous — le correctif backend (Task 4) reste
  visible/utile, et rien dans la maquette n'interdit un widget supplémentaire ; seul le
  remplacement pur et simple de la maquette serait une régression d'information.

## Ce qui reste valide de l'ancien spec

- Tout le § Backend (Tasks 1-4) : le bug `item.type` vs `rset.type` est réel et indépendant des
  maquettes — aucun changement.
- Task 6 (élargissement des interfaces TS) : toujours nécessaire, inchangée.
- Task 9 (retrait de `RevisionSetManage.vue`) : confirmée par la maquette elle-même (ci-dessus).
- Task 5 (extraction d'un util partagé type→icône/libellé) : le *principe* reste bon (2+
  consommateurs), mais son **contenu** doit correspondre au style de badge de la maquette
  (`.type-badge`, mono/majuscule/couleur pleine) plutôt qu'à l'icône+libellé choisi précédemment
  sans référence — à revoir au moment du plan en relisant le CSS des maquettes.

## Tests

Même exigence TDD stricte qu'avant. Les tests déjà écrits pour les Tasks 1-4, 6, 9 restent
valides tels quels (comportement backend/schema inchangé par cette correction). Les tests
écrits pour les anciennes Tasks 5, 7, 8, 10 (structure d'onglets, badge "Mixte" sur l'ancienne
mise en page, etc.) seront remplacés par les nouveaux tests de la structure réelle — ne pas
essayer de les faire survivre artificiellement.

## Vérification visuelle

Toujours faite en environnement natif dès la clôture (pas différée) — cette fois en comparant
concrètement au rendu de la maquette extraite (côte à côte), pas seulement en vérifiant
l'absence de régression fonctionnelle.
