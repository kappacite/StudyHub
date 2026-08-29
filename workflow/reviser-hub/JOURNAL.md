# Journal — reviser-hub

## 2026-08-28

Chantier ouvert : migration du flux 6 (`ETAT.md` § « Plan global par flux », 2026-08-27) vers
le système de suivi par chantiers. Aucun travail fait — bloqué sur
`backend-ensembles-heterogenes`. Commit : à suivre.

## 2026-08-29 (activation, brainstorming, plan)

Chantier réactivé : `backend-ensembles-heterogenes` et `bibliotheque-ensembles` (débloquant),
tous deux mergés. Branche `feature/reviser-hub` créée depuis `main` à jour, worktree
`.worktrees/reviser-hub`.

Brainstorming (chemin architectural, `superpowers:brainstorming`) : exploration a révélé que le
service de stats backend (`revision_stats_service.py`) n'avait jamais été adapté aux ensembles
hétérogènes — `RevisionSetStats.type`/`RevisionSetSummary.type` non-nullables dans les schémas
alors que `RevisionSet.type` l'est depuis D8, et surtout **`StudySession.item_type` est un
discriminant polymorphe réel** (pas de FK, `item_id` seul ne suffit pas) que les 3 points d'appel
du service filtraient avec `rset.type` (type de l'*ensemble*) au lieu de `item.type` (type de
l'*item*) — pour un ensemble hétérogène, `rset.type` vaut `None`, qui ne matche jamais aucune
session réelle. **Les stats de tout ensemble hétérogène déjà révisé sont silencieusement vides
depuis la livraison de `bibliotheque-ensembles`**, pas seulement mal formées. Décisions
utilisateur actées en cours de route :
- `RevisionSetManage.vue` retiré (pas migré) — fait doublon avec `RevisionSetDetail.vue`, déjà
  hétérogène-natif. Périmètre réduit de 4 à 3 écrans frontend.
- `Reviews.vue` : 6ᵉ onglet « Mixte » (pas de refonte de son rôle vis-à-vis de Bibliothèque).
- Répartition par type au niveau classeur : regroupement par type d'*item* (un ensemble
  hétérogène compte dans plusieurs buckets), pas par type d'ensemble.

Spec : `docs/superpowers/specs/2026-08-29-reviser-hub-design.md`. Plan détaillé (11 tâches TDD) :
`docs/superpowers/plans/2026-08-29-reviser-hub.md`.

## 2026-08-29 (exécution — subagent-driven-development, 10 tâches de code)

Exécuté tâche par tâche (implémenteur frais + revue dédiée par tâche). Toutes approuvées sans
tour de correction (0 finding Critical/Important sur l'ensemble des 10 tâches), quelques minors
parqués (paramètres morts déjà nettoyés en cours de route, nom de variable cosmétique laissé en
l'état, redondance de type déjà mandatée par le plan) — détail dans le ledger
`.superpowers/sdd/2026-08-29-reviser-hub/progress.md`.

**Incident opérationnel (Task 5, 1ʳᵉ tentative)** : un implémenteur (modèle rapide) est resté
bloqué 47 minutes sans aucune progression observable (aucun processus node/npm actif, aucun
fichier créé). Arrêté (`TaskStop`), vérifié qu'aucun commit/état parasite n'avait été laissé,
`npm ci` exécuté manuellement par le contrôleur (18 secondes — confirme que ce n'était pas un
install réellement lent) puis re-dispatché avec dépendances déjà installées : terminé en moins de
2 minutes. Cause racine non identifiée, sans conséquence sur le résultat final.

**Revue de la Task 6 (widen des interfaces TS)** : le plan prédisait `vue-tsc -b` propre après
cette tâche seule, mais 4 erreurs réelles sont apparues dans `RevisionSetStats.vue`/
`RevisionBinderStats.vue` (non encore adaptés). Vérifié que les 4 erreurs correspondaient
exactement aux écarts que les Tasks 7-8 (déjà prévues) allaient combler — accepté comme état
intermédiaire attendu, pas un défaut. Confirmé résolu : Task 8 rapporte `vue-tsc -b` propre sur
toute la branche.

**Revue de la Task 10 (`Reviews.vue`, plus gros fichier du plan, ~1880 lignes, zéro couverture de
test préexistante)** : diff de ~1600 lignes dû au hook de formatage (premier contact avec ce
fichier). Revue dédiée avec vérification mécanique explicite (analyse de profondeur de balises +
diff normalisé espaces/guillemets) de non-régression sur les 9 autres onglets — un faux positif
détecté puis résolu (décalage d'indentation pré-existant, corrigé par Prettier, pas un changement
de structure DOM). Approuvé sans réserve.

## 2026-08-29 (vérification visuelle réelle, faite dès cette clôture)

Environnement natif (hors Docker, comme pour `bibliotheque-ensembles`) : venv Python local +
SQLite pour le backend (port 5052), Vite dev pour le frontend (port 5173, whitelist CORS déjà en
place), extension Chrome connectée pour desktop clair/sombre, script Playwright pour la fenêtre
mobile 375×812 (le redimensionnement de fenêtre du navigateur s'est de nouveau avéré non
fonctionnel sur cette machine — même contournement que `bibliotheque-ensembles`).

Données de test créées via l'API : un classeur, un ensemble hétérogène (flashcard + vrai/faux,
les deux réellement notés via `/study/answer` et `/study/grade`) et un ensemble homogène QCM
(non noté, pour vérifier la non-régression).

**Confirmé visuellement, sans nouvelle anomalie** :
- Onglet « Mixte » de `Reviews.vue` liste l'ensemble hétérogène seul ; l'onglet QCM reste
  inchangé (non-régression) ; bouton « Gérer » ouvre bien `RevisionSetDetail.vue`.
- `/revision/sets/1/manage` redirige bien vers `/revision/sets/1` (Task 9).
- **`RevisionSetStats.vue` sur l'ensemble hétérogène : badge « Mixte », icône par item, et surtout
  « Réussite moy. 100 % » avec les deux items à 100 % — preuve visuelle directe du correctif
  backend (avant Tasks 2-4, ces deux items révisés seraient remontés à 0 révision malgré les
  appels `/study/answer`/`/study/grade` réussis).** Sur l'ensemble QCM homogène : badge « QCM »
  (pas « Mixte »), item non révisé correctement à 0 %.
- `RevisionBinderStats.vue` : « Répartition par type » montre Flashcards/QCM/Vrai-Faux à 1
  ensemble chacun — l'ensemble hétérogène compte bien dans Flashcards ET Vrai/Faux
  simultanément (Task 4). Badge « Mixte » sur sa ligne dans les listes d'ensembles.
- Les trois écrans identiques en clair et en mobile (375×812).

**Écart pré-existant noté, hors périmètre** : sur mobile, l'en-tête de `RevisionSetStats.vue` et
`RevisionBinderStats.vue` affiche le nom de route JS brut (« RevisionSetStats »,
« RevisionBinderSt… » tronqué) au lieu d'un libellé français — le même défaut que
`bibliotheque-ensembles` avait trouvé et corrigé pour 3 *autres* routes
(`web/src/components/layout/AppLayout.vue::currentRouteName`). Ces deux routes existaient déjà
avant ce chantier et n'ont jamais été ajoutées à cette table — pas une régression de ce chantier,
mais un gap pré-existant qui traîne. Non corrigé ici (hors périmètre du plan), à corriger dans un
futur chantier touchant ces écrans.

Suite complète backend/frontend verte tout au long (voir ledger), `vue-tsc -b` propre. Chantier
prêt à clôturer.

## 2026-08-29 (correction — vraies maquettes jamais consultées, refonte, clôture)

Constat utilisateur en chat : la clôture ci-dessus n'avait jamais ouvert les vraies maquettes
Direction A (répétition exacte de l'erreur documentée dans la mémoire
`migration-ecran-verify-mockup` : « ne jamais conclure "pas de restructuration nécessaire" sans
avoir ouvert la vraie maquette »). Les 4 fichiers `.dc.html` pertinents ont été extraits de
l'artefact Claude Design publié et lus en entier. Correction actée dans
`docs/superpowers/specs/2026-08-29-reviser-hub-redesign.md` et exécutée via le plan
`docs/superpowers/plans/2026-08-29-reviser-hub-redesign.md` (8 tâches TDD,
`subagent-driven-development`, chaque tâche avec sa propre revue spec+qualité).

**Exécution (8 tâches, résumé — détail complet dans le plan ci-dessus et le ledger SDD)** :
correctif `focus_service` (ensembles de révision dus, groupés par ensemble), `NoteFeynman.vue`
créé, génération IA déplacée vers `Decks.vue`, `RevisionSetStats.vue` et `RevisionBinderStats.vue`
reconstruits selon leurs maquettes respectives (nouvelle agrégation backend : répartition SM-2,
progression 6 semaines, historique par jour), `Reviews.vue` reconstruit en flux unifié
(2503→381 lignes, tabs/IA/gestion-decks retirés — tous relogés ailleurs, vérifié par grep sur tout
`web/src`).

**3 tours de correction, tous conclus propres** :
- Task 4 (génération IA sur `Decks.vue`) et Task 6 (`RevisionBinderStats.vue`) : un appel API
  direct (`api.post`/`api.get`) avait été introduit dans le composant — violation de la règle
  projet « API uniquement dans stores/services ». Corrigé en ajoutant une méthode dédiée au store
  concerné (`decksStore.generateFlashcards()`, `decksStore.fetchDeckStats()`).
- Task 5 (`RevisionSetStats.vue`) : colonne « Révisions » renommée « Cartes vues » (fidélité
  maquette), 3 seuils de couleur de taux de réussite différents dans le même fichier unifiés en un
  seul (`>=70`, util partagé `successRate.ts`), section « Éléments » (édition d'item, absente de
  la maquette) retirée — elle faisait doublon avec `RevisionSetDetail.vue`/`RevisionSetTypeItems.vue`,
  qui gèrent déjà cette fonctionnalité nativement.
- Task 7 (`Reviews.vue`) : après retrait de la section gestion-de-decks, `/decks` n'avait plus
  aucun point d'entrée de navigation (le seul lien restant vivait dans une vue morte, jamais
  routée). Corrigé en ajoutant un lien secondaire « Mes decks » dans le bandeau, symétrique au lien
  « Examen blanc » déjà conservé pour la même raison.

Un vrai bug pré-existant corrigé en passant (effet de bord de la Task 7, pas un objectif du plan) :
`studyItem()` dans l'ancien `Reviews.vue` n'avait aucune branche pour `type: 'revision_set'` —
cliquer sur un ensemble de révision dû dans la file unifiée ne faisait donc rien. La revue de la
Task 7 (modèle le plus capable, vu l'ampleur de la suppression) a vérifié ce point en confirmant
que le nouveau code reproduit exactement la logique de routage de l'ancien `openSet()`.

**Vérification visuelle réelle contre les vraies maquettes (Task 8)** — environnement natif hors
Docker (venv Python local + SQLite, port 5052 ; Vite dev, port 5173 ; extension Chrome pour le
clair/sombre desktop ; script Playwright dédié pour 375×812, le redimensionnement de fenêtre du
navigateur s'étant à nouveau avéré non fonctionnel sur cette machine — même contournement que
`bibliotheque-ensembles`). Note technique : `flask run` charge automatiquement le `.env` racine du
dépôt (Postgres, pour Docker) en remontant l'arborescence depuis le worktree — contourné en
lançant `app.run()` directement (sans le CLI Flask) plutôt que `flask run`.

Données de test créées via l'API : un classeur, un ensemble hétérogène (flashcard + vrai/faux,
réellement noté via `/study/answer`/`/study/grade`, 100% de réussite), un ensemble QCM homogène
non révisé, un classeur avec 2 decks (un en retard, un dû aujourd'hui, un troisième horodaté dans
le futur pour peupler la section « À venir »).

**Confirmé visuellement, côte à côte avec les maquettes, clair/sombre × desktop/mobile, sans
trouver de nouveau défaut** :
- `Reviser.dc.html` vs `Reviews.vue` : bandeau résumé, sections En retard/Aujourd'hui/À venir,
  badges de type, liens secondaires « Mes decks »/« Examen blanc » — structure conforme.
- Routage vérifié en cliquant réellement : ensemble QCM homogène → `/revision/sets/:id/run` ;
  deck → `/decks/:id/study` ; lien « Mes decks » → `href="/decks"` confirmé dans le DOM.
- `RevisionSetStats.dc.html` vs `RevisionSetStats.vue` : badge « Mixte », 100% de réussite réel
  (preuve directe que le correctif backend d'origine tient toujours), barres SM-2 (1 item en
  « Facile »), progression 6 semaines, historique « Cartes vues » — pas de section « Éléments ».
- `RevisionBinderStats.dc.html` vs `RevisionBinderStats.vue` : 4 cartes stat, liste fusionnée
  deck+ensemble triée par maîtrise (0% de maîtrise cohérent — un item noté une fois n'est pas
  encore « mûr », distinct du taux de réussite à 100%), « Répartition par type » conservée en
  complément.
- Redirection `/revision/sets/:id/manage` → `/revision/sets/:id` toujours fonctionnelle (Task 9 de
  l'ancien plan, non touchée par cette correction).

**Écart pré-existant reconfirmé, toujours hors périmètre** : sur mobile, l'en-tête de
`RevisionSetStats.vue` et `RevisionBinderStats.vue` affiche encore le nom de route JS brut au lieu
d'un libellé français (même gap que documenté à la clôture initiale ci-dessus — `AppLayout.vue::
currentRouteName` n'a jamais été mis à jour pour ces 2 routes, aucune des 8 tâches de cette
correction n'y touchait).

Suite complète verte tout au long (voir ledger `.superpowers/sdd/2026-08-29-reviser-hub-redesign/progress.md`
pour le détail tâche par tâche), `vue-tsc -b` propre. Chantier prêt à clôturer — cette fois contre
les vraies maquettes.

## 2026-08-29 (Task 9 — durée de révision réelle, demande utilisateur post-clôture)

L'utilisateur a demandé, après la clôture ci-dessus, d'ajouter la durée de révision dans les
statistiques comme le montrent les maquettes (« Temps cumulé », colonne « Durée » de l'historique
de sessions, « Temps total d'étude » au niveau classeur) — délibérément omise dans les Tasks 5-6
car `StudySession.duration_seconds` était codé en dur à `0` à chaque point de création (jamais
suivi). Ajoutée comme Task 9 du plan, exécutée en TDD (subagent-driven-development, 1 seul tour :
revue immédiatement propre, 0 Critical/Important).

**Backend** : `RevisionItemAnswer`/`RevisionGradeRequest`/`RevisionRunRequest` gagnent
`duration_seconds` (optionnel, défaut `0` — omission = toujours `0`, jamais inventé).
`answer_item`/`grade_item` utilisent la durée réelle reçue ; `run_qcm` reçoit une durée totale pour
tout le passage et la répartit sur ses items via `divmod` (ex. 100s/3 questions → [34,33,33],
somme exacte, testé). `revision_stats_service.py` ajoute `total_duration_seconds` (ensemble et
classeur) et `SessionHistoryDay.duration_seconds`, tous calculés à partir des sessions déjà
chargées (aucune requête de plus).

**Frontend** : `RevisionStudy.vue` et `QcmRun.vue` chronomètrent réellement le temps passé
(`Date.now()` au montage/changement d'item, calcul à la soumission) et l'envoient via
`revisionStore` (aucun nouvel appel API direct introduit dans un composant — vigilance explicite
après les 2 précédents tours de correction sur ce point). `formatDuration` (nouvel utilitaire
partagé) formate « 2h 15 » / « 8 min » à l'identique des maquettes. `RevisionSetStats.vue` : trio
passé à 3 colonnes (ajout « Temps cumulé »), historique gagne une colonne « Durée ».
`RevisionBinderStats.vue` : **décision du contrôleur** — « Temps total d'étude » ajouté comme 5ᵉ
carte plutôt que de remplacer « Taux de réussite moyen » (déjà réel, déjà approuvé en Task 6) dans
son emplacement exact de la maquette ; supprimer un contenu déjà validé juste pour coller au
nombre de cartes de la maquette n'en valait pas la peine.

Revue : spec ✅, qualité Approved, 0 Critical/Important. Les deux points à enjeu réel (l'arithmétique
`divmod` et le filtrage `user_id` des nouvelles agrégations) ont été vérifiés indépendamment à la
main par le relecteur, pas seulement pris sur la foi du rapport. 1 écart pré-existant signalé (hors
scope de cette tâche) : `StudySessionDAO.get_for_items` ne filtre pas par `user_id` — un ensemble
partagé (« cours ») peut déjà mélanger les sessions de plusieurs élèves dans les stats du
propriétaire ; ce n'est pas une régression de cette tâche (tous les autres agrégats de ce service
en héritent déjà), mais mérite un futur audit dédié de `revision_stats_service.py`.

**Vérification visuelle réelle** (environnement natif redémarré brièvement, même procédure) : un
nouvel item créé et noté avec une durée explicite de 135s via l'API confirme `total_duration_seconds:
135` et `session_history[0].duration_seconds: 135` côté backend ; côté frontend, `RevisionSetStats.vue`
affiche bien « 2 min » dans le trio ET dans la colonne Durée de l'historique, `RevisionBinderStats.vue`
affiche la 5ᵉ carte « Temps total d'étude : 2 min · Depuis la création » sans avoir supprimé aucune
des 4 cartes existantes — confirme visuellement que la décision « ajouter, pas remplacer » est bien
ce qui a été livré.

## 2026-08-30 (revue finale de branche, tour de correction, chantier prêt pour la PR)

Revue finale de toute la branche (31 commits à l'époque, Opus, 6 passes déclarées) contre `main`,
per `superpowers:subagent-driven-development`. Verdict : **1 Critical, 4 Important, 9 Minor.**

**Critical** : `FocusItem.type` élargi (Task 1/2) pour inclure `'revision_set'`, mais seul
`Reviews.vue` (Task 7) savait le traiter. 5 autres consommateurs vivants ne géraient pas cette
valeur — exactement le balayage que le brief de la Task 2 demandait explicitement, fait en lecture
apparemment sans suite sur tout l'arbre : `Accueil.vue`/`FocusPage.vue` (bouton « Réviser » inerte,
icône/libellé qui retombent sur la branche *assignment* — un ensemble de révision dû affichait
l'icône et le texte d'un devoir sur l'écran le plus visité de l'appli), `FocusWidget.vue` (CTA du
tableau de bord inerte), `StudyDeck.vue`/`Blurting.vue` (`handleNextFocusItem` sans branche —
cassait la file unifiée « Tout réviser » en plein vol, le curseur ayant déjà avancé). Aucune revue
de tâche ne pouvait l'attraper : la casse vivait entièrement hors de la liste de fichiers de
chaque tâche, et `vue-tsc -b` restait vert car chaque site est une chaîne `if/else if`, pas un
`switch` exhaustif.

**Important** : (2) le nouveau `total_duration_seconds` (Task 9) aggrave un écart préexistant de
`StudySessionDAO` (aucun filtre `user_id`) — les autres champs affectés sont des ratios bornés qui
dégénèrent vers une moyenne de classe sur un ensemble « cours » partagé, mais une somme de durée
est non bornée et se présente comme une affirmation à la première personne (« Temps total d'étude
— Depuis la création »), avec fuite secondaire du temps d'étude des autres élèves. (3)
`RevisionBinderStats.vue` filtrait les decks par `binder_id` direct uniquement, alors que la moitié
« ensembles » de la même vue fusionnée (et le bouton « Inclure les sous-classeurs ») est
descendants-inclusive — sous-compte et rend le bouton incohérent sur tout classeur avec
sous-classeurs. (4) `RevisionSetStats.vue` et `RevisionBinderStats.vue` avaient toutes deux perdu
leur état d'erreur pendant la refonte (Round 2) — page blanche sur échec réseau. (5)
`NoteFeynman.vue` (Task 3, écrit avant les 2 tours de correction de ce même défaut sur cette
branche) appelait `api.*` directement depuis le composant, plus un `any` explicite.

**Tour de correction** (1 seul dispatch couvrant Critical + les 4 Important + 3 Minors bon marché
directement liés — `run_qcm` écrivait `item_type=rset.type` au lieu de `item.type` ; le bouton
« Réviser cette série » de `RevisionSetStats.vue` ignorait la branche QCM `/run` ; le chrono de
`QcmRun.vue` démarrait avant le chargement réseau) : 4 commits, suite complète verte (backend
319/324, les 5 échecs `test_import.py` Windows préexistants et non liés ; frontend 384/384,
`vue-tsc -b` propre). Re-revue ciblée : **les 8 constats ADDRESSÉS, aucune casse nouvelle
Critical/Important.** Attention particulière portée aux deux points à enjeu réel — vérifié
indépendamment que l'utilitaire partagé `focusItemTarget.ts` route correctement QCM vs non-QCM
sur les 5 fichiers réellement corrigés (pas seulement la revendication du commit), et que le
scoping `user_id` de `StudySessionDAO` ne casse pas le cas légitime (un propriétaire d'ensemble
partagé voit toujours ses propres sessions) — deux nouveaux tests d'isolation cross-utilisateur
vérifient les *valeurs*, pas seulement les codes 403/404, dont un dédié spécifiquement au nouveau
`total_duration_seconds`.

2 Minors relevés, tous deux classés sans suite (ni bloquants ni correctifs nécessaires) : une
incohérence entre `StudyDeck.vue` (corrige incidemment aussi le cas `assignment`) et
`Blurting.vue` (le laisse tel quel) — inoffensif, route vers la vraie destination existante, pas
une route morte ; et une garde `!== null` sur `binder_id` qui préserve exactement le comportement
antérieur, notée seulement pour référence future.

**Chantier prêt pour la PR.** Revue finale propre, ledger complet dans
`.superpowers/sdd/2026-08-29-reviser-hub-redesign/progress.md` (supprimé après cette clôture,
l'historique git fait foi comme pour les chantiers précédents).
