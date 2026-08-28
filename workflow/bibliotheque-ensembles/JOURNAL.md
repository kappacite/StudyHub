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
319/319 tests verts, `vue-tsc -b` propre sur tous les fichiers du périmètre (3 erreurs
résiduelles, toutes dans `Reviews.vue`/`RevisionSetManage.vue`, pré-existantes et hors
périmètre — territoire `reviser-hub`).

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
