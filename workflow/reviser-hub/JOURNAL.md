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
