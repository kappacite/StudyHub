# Journal — bibliotheque-ensembles

## 2026-08-28 (activation)

Chantier activé (`Statut : planifié → ouvert`, branche `feature/bibliotheque-ensembles` créée
depuis `main` à jour, worktree `.worktrees/bibliotheque-ensembles`). Dépendance
`backend-ensembles-heterogenes` levée (PR #126 mergée, CI verte dont la garde migrations
PostgreSQL). Prochain point du plan : écrire la spec détaillée (inventaire `Binders.vue`,
maquette `Notes.dc.html`, états, contrat des 3 nouveaux composants) via
`superpowers:brainstorming` puis `superpowers:writing-plans`.

## 2026-08-28 (brainstorming — 2 corrections de périmètre en cours de route)

Exploration du code réel avant de figer le périmètre a corrigé deux suppositions initiales :
`RevisionSetManage.vue` (`/manage`) n'est **pas** le futur écran de détail — sa maquette
(`RevisionSetManage.dc.html`) est l'ancien écran homogène pré-hétérogène, territoire
`reviser-hub`, non touché ici. Le vrai écran neuf est `RevisionSetDetail.dc.html` (extrait du
canevas, nav active « Bibliothèque »), dont les lignes groupent les items **par type** (pas un
item atomique par ligne) — décision utilisateur actée : regroupement visuel, pas un 3ᵉ niveau
de hiérarchie. `RevisionStudy.vue` ajouté au périmètre (décision utilisateur) car dépendance
dure du bouton « Réviser l'ensemble » que ces écrans exposent — il ne fonctionnait pas du tout
pour un ensemble hétérogène (dispatch par `set.type` unique au lieu de `item.type`).

Spec : `docs/superpowers/specs/2026-08-28-bibliotheque-ensembles-design.md`, committée avec
tous les écarts d'exploration documentés.

## 2026-08-28 (plan détaillé, 9 tâches initiales)

Plan écrit : `docs/superpowers/plans/2026-08-28-bibliotheque-ensembles.md`. Un gap backend
trouvé en écrivant le plan (`RevisionSetCreate.type` obligatoire, rejetterait la création d'un
ensemble hétérogène) — corrigé comme petite Task 1 dans ce même plan plutôt qu'un chantier
séparé (correctif d'une ligne, aucune migration).

## 2026-08-28 (exécution — subagent-driven-development, 11 tâches au final)

Exécuté task par task (implémenteur frais + revue dédiée par tâche, un tour de correction sur
la Task 9). Deux tâches ajoutées en cours de route, non prévues au plan initial, toutes deux
des découvertes réelles faites par les implémenteurs/revues, pas des extensions de confort :

- **Task 9 (`TeacherDashboard.vue`)** : la revue de la Task 2 (store, `RevisionSet.type`
  devenu nullable) a fait remonter un vrai risque de plantage dans un écran totalement
  étranger à ce chantier (`s.type.toUpperCase()` non protégé) — ajoutée comme tâche dédiée
  plutôt qu'ignorée, vu le coût d'un plantage sur un écran enseignant. *(Renommée Task 10 après
  l'ajout suivant.)*
- **Task 7 (`RevisionItemModal.vue` — type `flashcard` manquant)** : l'implémenteur de la Task
  6 a découvert que `RevisionItemModal.vue` n'avait aucune gestion du type `flashcard` (la
  Task 3 n'avait branché que le transport du type choisi, jamais ajouté le type lui-même à la
  liste/au formulaire) — sans ce correctif, un des 6 types que ce chantier existe pour
  supporter était tout simplement impossible à créer via l'interface. Investigation
  complémentaire a trouvé un second bug latent connexe (sélectionner « Carte »/Deck avec un
  ensemble verrouillé créait silencieusement un Deck sans rapport plutôt que d'ajouter à
  l'ensemble) — corrigé dans la même tâche.

**Un tour de correction (Task 9, `Binders.vue`)** : la revue a trouvé 2 constats critiques —
la fusion visuelle Decks+Ensembles avait fait disparaître les actions « Retirer du classeur »
(decks ET ensembles) et « Statistiques » (ensembles), violant la contrainte « zéro
fonctionnalité supprimée » du plan (erreur dans mon propre brief de tâche, pas de
l'implémenteur) ; et le calcul du badge « N dues » avait été discrètement affaibli (seuil de
24h au lieu de « en retard maintenant ») pour contourner un test instable au lieu de corriger
le fixture du test. Les deux corrigés et re-vérifiés en un tour, aucun résidu.

**Portée finale confirmée propre** (`git diff --stat main..HEAD`) : uniquement les fichiers
prévus — aucun de `Reviews.vue`/`RevisionSetManage.vue`/`RevisionSetStats.vue`/
`RevisionBinderStats.vue` touché, aucune ligne `Deck`/`Flashcard` touchée. Suite complète
319/319 tests verts, `vue-tsc -b` propre sur tous les fichiers du périmètre.

**Correction de ce constat (revue finale de branche).** Les 3 erreurs `vue-tsc` résiduelles
dans `Reviews.vue`/`RevisionSetManage.vue` n'étaient **pas** pré-existantes sur `main` : le
rapport de la tâche 2 avait prouvé (via `git stash`) que la ligne de base était à zéro erreur.
Elles ont été **introduites par ce chantier**, par le passage de `RevisionSet.type` à
`RevisionType | null` (tâche 2), et la branche ne compilait donc pas. Elles sont désormais
corrigées par des gardes de nullité minimales (élargissement de la signature de `openSet`,
`?? undefined` sur `:locked-type`, garde sur `typeLabel`), sans redessiner ni l'un ni l'autre
de ces deux écrans — qui restent du territoire `reviser-hub`.

**Vérification visuelle réelle — non faite.** Tentative sérieuse : conteneurs Docker
disponibles (`docker ps`) appartiennent à un environnement de dev déjà en cours (frontend sur
le port 80, en service depuis plusieurs heures) partagé avec d'autres travaux — monter un
environnement isolé pour cette worktree (port différent, base différente) sans risquer
d'interférer était jugé plus coûteux que le bénéfice à ce stade, sachant que chaque écran a
déjà été vérifié par un montage réel du composant (`@vue/test-utils`, assertions DOM sur le
texte/les attributs rendus, pas des mocks internes) et deux tours de revue indépendante par
tâche. Écart assumé et documenté, cohérent avec le traitement déjà accepté sur d'autres
chantiers de ce projet quand l'environnement de capture n'était pas fiable — à combler dans
une session ultérieure si l'environnement se stabilise, avant un merge définitif si possible.

**Prochaine étape** : revue finale de branche entière (le modèle le plus capable), puis
procédure de clôture de chantier (push, PR).

## 2026-08-29 (vérification visuelle réelle — comble l'écart laissé ouvert)

Reprise du chantier pour combler le seul point restant du plan. L'environnement Docker partagé
était de nouveau libre (`docker ps` vide), mais l'utilisateur a explicitement demandé de ne
pas passer par Docker pour cette vérification (accident de configuration constaté au passage :
son `.env` à la racine du dépôt pointe `DATABASE_URL` vers l'hôte `db` du réseau Docker interne,
introuvable en dehors — et le frontend Docker qu'il avait lancé pour tester servait une image
**périmée** avec `VITE_API_BASE_URL=http://localhost:5000` baké au build, d'où les rejets CSP
`connect-src 'self'` qu'il observait : correctif communiqué, hors périmètre de ce chantier).

Environnement natif monté à la place, isolé de tout ce qui tournait déjà : venv Python dans
cette worktree (`backend/.venv`, `cryptography` récent pris à la place de la version épinglée
— pas de roue arm64 pour l'ancienne sur cette machine ; `psycopg2-binary` exclu, inutile en
SQLite dev), backend Flask natif port 5050 (`DATABASE_URL` SQLite explicite pour court-circuiter
le `.env` racine repéré ci-dessus, que le chargement amont de Flask/dotenv remonte sinon depuis
`backend/`), Vite dev natif port 5173 (whitelist CORS déjà en place côté backend). Compte de
test créé via l'API, navigateur réel (extension Chrome) pour desktop clair/sombre, script
Playwright ad hoc (déjà une dépendance du dépôt, `web/tests-e2e`) pour la fenêtre mobile
375×812 — le redimensionnement de la fenêtre Chrome elle-même s'est avéré bloqué sur cette
machine (`resize_window` rapporte un succès mais `window.innerWidth` ne bouge jamais).

**Bug bloquant réel trouvé et corrigé** (`9d1e5d3` — à confirmer au commit) : la création d'un
ensemble hétérogène puis sa révision réelle (`Réviser l'ensemble`, self-eval flashcard/définition,
correction auto vf/association/ordre) plantait systématiquement en 500
(`sqlite3.IntegrityError: NOT NULL constraint failed: study_sessions.module`). Cause :
`RevisionService.answer_item` et `.grade_item` posaient `module=rset.type`, jamais mis à jour
pour tenir compte de la nullabilité de `RevisionSet.type` introduite par ce chantier même (D8) —
tous les tests existants créaient des ensembles *homogènes* (`type` renseigné), aucun ne
couvrait un ensemble réellement hétérogène bout en bout via les endpoints d'étude, donc rien ne
l'attrapait. C'est précisément le type de régression que l'étape de vérification visuelle
différée était censée intercepter. Corrigé en TDD (2 tests ajoutés reproduisant le crash sur
`type: None` avant le correctif, `module=rset.type or item.type` ensuite) — suite complète
`test_revision.py` verte (21/21), suite backend complète verte sauf 5 échecs pré-existants et
sans rapport (`test_import.py`, verrou de fichier temporaire Windows sur `NamedTemporaryFile`,
environnement local uniquement).

**Défaut mineur trouvé et corrigé** : les 3 nouvelles routes de ce chantier
(`RevisionSetDetail`, `RevisionSetTypeItems`, `RevisionStudy`) étaient absentes de la table de
traduction du titre d'en-tête mobile (`AppLayout.vue::currentRouteName`), qui affichait donc le
nom de route brut JS tronqué (ex. `RevisionSetTypeI…`). Ajout des 3 libellés français, en
évitant l'apostrophe (piège déjà présent dans le code existant : la classe Tailwind
`capitalize` traite tout caractère après une apostrophe comme un nouveau mot, ce qui aurait
donné `L'Ensemble` au lieu de `l'ensemble`).

**Vérifié visuellement, sans anomalie** : bascule Notes/Révision/Autres, création d'ensemble
hétérogène (`RevisionSetModal`), les 6 types dans `RevisionItemModal` (dont `flashcard`,
correctif de la Task 7), regroupement par type dans `RevisionSetDetail` (icônes dédiées),
`RevisionSetTypeItems`, dispatch de révision par type dans `RevisionStudy` (flashcard,
définition en self-eval ; vf, association, ordre en correction auto), exclusion des QCM de la
révision par item avec message dédié (`?type=qcm`), le tout en clair et sombre sur desktop et
en 375×812 sur mobile (écrans + les 2 modales).

Suite complète frontend verte (325/325), `vue-tsc -b` propre. Chantier prêt à clôturer.

## 2026-08-29 (clôture)

Toutes les cases de `PLAN.md` cochées. Prochaine étape : demander à l'utilisateur de pousser
`feature/bibliotheque-ensembles`, puis ouvrir la PR (confirmation utilisateur préalable).
