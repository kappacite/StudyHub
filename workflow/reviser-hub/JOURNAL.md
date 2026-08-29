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
