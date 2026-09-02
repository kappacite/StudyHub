# Plan — refonte de l'éditeur de notes (NoteEdit.vue) selon le vrai canevas Direction A

Contexte complet : `workflow/editeur-notes-notation-ia/CONTEXT.md` (§ « Ruling du 2026-08-30 »
explique pourquoi ce plan repart de zéro contre `main` actuel plutôt que de reprendre
`feature/noteedit-migration`). Référence de conception (déjà vérifiée contre le canevas pour sa
Task 4, mais PAS exécutable telle quelle — numéros de ligne périmés depuis la réécriture
`reviser-hub`) : `docs/superpowers/plans/2026-08-25-noteedit-migration-plan.md`.

## Référence canevas (extraite le 2026-08-30, `NoteEdit.dc.html`)

L'écran montre : en-tête app standard (inchangé, hors scope) ; puis un fil d'ariane
`BIBLIOTHÈQUE / CHIMIE ORGANIQUE / NOTES` (mono, majuscules, gris) au-dessus du titre de la
note ; à droite du titre, un bouton **« Notation »** (bordure `--accent`, icône étoile) ;
en dessous, deux colonnes : la fiche (carte, barre d'outils avec 5 boutons d'icônes
gras/italique/titre/liste/formule, puis le corps de texte) à gauche (`flex:1`), et une
**sidebar de 296px** à droite contenant deux cartes empilées :
1. **« Assistant IA »** — sous-titre "S'entraîner sur cette note, à partir de son contenu.",
   puis exactement 3 boutons pleine largeur, alignés à gauche, icône+libellé : **« Évaluation
   mixte »**, **« Méthode de la feuille blanche »**, **« Méthode Feynman »**. Pas de 4e bouton
   « Générer un quiz ».
2. **« Métadonnées »** — Classeur / Tags / Modifiée.

## Global Constraints

- TDD sans exception (phase ≥ 3) : test avant code, doit échouer pour la bonne raison avant le
  correctif.
- **Chaque tâche commence par relire l'état ACTUEL de `NoteEdit.vue` sur cette branche** (le
  fichier fait 3499 lignes au 2026-08-30 ; les numéros de ligne ci-dessous sont des repères
  approximatifs constatés à cette date, pas une garantie — `grep`/lecture directe avant
  d'éditer, ne pas supposer qu'ils n'ont pas bougé d'une tâche à l'autre).
- `<script setup lang="ts">`, TypeScript strict, pas de `any`. Appels API uniquement dans
  stores/services. Aucune valeur de style brute (`#rrggbb`, `text-[Npx]`, couleurs Tailwind
  génériques `slate-*`/`pink-*`/`cyan-*`/`teal-*`/`sky-*` hors tokens du projet) — toujours un
  token du design system (`primary`/`accent`/`success`/`warning`/`danger`/`ink`/`surface`/...).
  Charger le skill `design-system` si besoin de la table de correspondance mockup→token.
  Confirmé au 2026-08-30 : `NoteEdit.vue` contient encore `bg-[#070913]`, `text-slate-500`,
  `bg-pink-50`, `bg-cyan-50`, `bg-teal-50`, `bg-sky-50`, plusieurs `text-[9px]`/`text-[10px]`/
  `text-[11px]` — ces tâches de retonage sont réelles, pas préventives.
- Ne pas supprimer `NoteQuiz.vue` ni sa route (`/notes/:id/quiz`) — seulement retiré du panneau
  Assistant IA (canevas), pas du code. Décision produit séparée à consigner dans `ETAT.md` si
  la suppression est actée plus tard, hors périmètre de ce chantier.
- Le bouton « Notation » est ajouté **désactivé** (info-bulle explicative) — sa cible
  (backend + vue de résultat) n'existe pas encore, c'est le flux 2 (hors périmètre de ce
  chantier). Pas de demi-mesure silencieuse (bouton actif qui 404).
- Responsive 375px/1440px + mode sombre systématique sur tout ce qui est retoné/ajouté.

## Task 1 : extraire `NoteEditHelpModal.vue` (modale Guide)

**Contexte actuel** : deux boutons déclenchent la même modale (`showHelpModal = true`), un en
mode édition et un en mode lecture (chercher `showHelpModal` dans `NoteEdit.vue` — 2 déclencheurs
+ le ref + le bloc modal lui-même, contenu statique d'aide sur les placeholders/split-screen).

**Fichiers** :
- Créer `web/src/components/notes/NoteEditHelpModal.vue` (composant présentationnel pur,
  `components/CLAUDE.md` : réutiliser `BaseModal` si un composant primitive existe déjà sous
  `components/ui/base/` — vérifier avant d'écrire un wrapper de modale à la main).
- Créer `web/tests/components/notes/NoteEditHelpModal.spec.ts`.
- Modifier `NoteEdit.vue` : remplacer le bloc modal inline par `<NoteEditHelpModal v-if="showHelpModal" @close="showHelpModal = false" />` (ou prop `open`/emit `update:open` si `BaseModal` a cette convention — vérifier), garder les 2 boutons déclencheurs inchangés.

**Interfaces** : composant sans dépendance store, contenu statique (le texte d'aide actuel),
emit `close`.

TDD : test du nouveau composant (rendu du contenu, emit `close` au clic du bouton fermer)
d'abord, puis extraction. Suite complète + `vue-tsc -b` en fin de tâche.

## Task 2 : extraire `NoteInputModal.vue` (modale de saisie générique)

**Contexte actuel** : `NoteEdit.vue` utilise une modale générique pour saisir le contenu de
plusieurs types d'insertion (définition, qcm, ordre, association, vrai/faux, diagramme — chercher
`applySelectionTransform` et ses branches `def`/`qcm`/`ordre`/`assoc`/`vf`/`diagramme`, et la
fonction `openModal()` qui pilote cette modale générique). Vérifier la forme exacte de son état
(quels refs pilotent son contenu/titre/champs) avant d'extraire — c'est plus complexe qu'une
modale statique, le composant extrait doit rester purement présentationnel (props pour le
titre/les champs à afficher, emit pour la soumission) sans logique métier de transformation
(qui reste dans `NoteEdit.vue`, seul le rendu de la modale est extrait).

**Fichiers** :
- Créer `web/src/components/notes/NoteInputModal.vue`.
- Créer `web/tests/components/notes/NoteInputModal.spec.ts`.
- Modifier `NoteEdit.vue` en conséquence.

TDD : mêmes règles que Task 1. Si le composant s'avère trop couplé pour rester présentationnel
pur (ex: il a vraiment besoin de connaître la logique de transformation par type), documente
la déviation dans ton rapport plutôt que de forcer une extraction artificielle — le contrôleur
tranchera si besoin.

## Task 3 : extraire `NoteEvaluationModal.vue` (modale d'évaluation SM-2)

**Contexte actuel** : la modale des boutons de notation SM-2 pendant la lecture active (grille
de boutons colorés — Facile/Bien/Difficile/etc., chercher autour de `renderSm2Buttons`/les
classes `sm2-btn-*`, la modale déclenchée par ces boutons). Même principe que Task 1/2 :
extraction présentationnelle pure.

**Fichiers** :
- Créer `web/src/components/notes/NoteEvaluationModal.vue`.
- Créer `web/tests/components/notes/NoteEvaluationModal.spec.ts`.
- Modifier `NoteEdit.vue` en conséquence.

TDD : mêmes règles. Attention à ne pas confondre avec `NoteEvaluation.vue` (écran séparé,
fonctionnalité « Évaluation mixte » — sans rapport avec cette modale de notation SM-2 pendant la
lecture active, malgré la proximité de nom).

## Task 4 : construire `NoteSidebar.vue` (remplace la modale IA) + bouton Notation désactivé

**C'est la tâche la plus importante côté conformité canevas — voir la référence canevas en tête
de ce plan pour l'exigence exacte.**

**Fichiers** :
- Créer `web/src/components/notes/NoteSidebar.vue`.
- Créer `web/tests/components/notes/NoteSidebar.spec.ts`.
- Modifier `NoteEdit.vue` :
  - Retirer le bouton « Réviser avec l'IA » (`@click="showAiModal = true"`, actuellement 2
    occurrences — mode édition ET mode lecture, vérifier les deux) et toute la modale
    `showAiModal`/son bloc HTML.
  - Retirer les refs/données devenues mortes : `showAiModal`, `aiActivities` (le tableau à 4
    entrées incluant `quiz` — confirmé présent à ce jour, chercher son emplacement actuel).
  - Ajouter `<NoteSidebar>` à côté de la fiche en mode lecture (la fiche doit passer de
    `max-w-4xl mx-auto` centré à une disposition en ligne avec la sidebar — un wrapper
    `max-w-6xl` + `flex gap-6 items-start` typiquement, la fiche gardant `flex-1 min-w-0` et la
    sidebar une largeur fixe ~296px/`w-72` selon les tokens Tailwind du projet). Le mode édition
    n'a pas de sidebar (hors scope canevas pour ce mode).
  - Ajouter le bouton « Notation » **désactivé** dans l'en-tête (à côté du titre de la note,
    comme le canevas), avec `title`/tooltip expliquant qu'il dépend du volet backend flux 2 pas
    encore livré — pas de route/action câblée dessus.

**Interfaces** :
- `NoteSidebar.vue` : présentationnel pur (aucun appel API/store direct — reçoit tout par
  props). Props : `binderName: string`, `tags: Tag[]` (`Tag` depuis `../../stores/tags`),
  `updatedAt: string`. Emit : `start-activity: [type: 'evaluation' | 'blurting' | 'feynman']`
  (exactement ces 3 valeurs, dans cet ordre pour l'affichage — pas `'quiz'`). Le parent
  (`NoteEdit.vue`) garde `startAiActivity(type)` comme handler unique, appelé depuis l'emit :
  `function startAiActivity(type: string) { router.push(\`/notes/${noteId.value}/${type}\`) }`.
- Libellés exacts (canevas) : « Évaluation mixte », « Méthode de la feuille blanche », «
  Méthode Feynman ». Sous-titre de la carte Assistant IA : « S'entraîner sur cette note, à
  partir de son contenu. ».
- Carte Métadonnées : Classeur (nom du classeur), Tags (badges, réutiliser `TagBadge.vue`
  existant), Modifiée (date formatée) — mêmes données que l'ancienne modale/le contexte actuel
  de la note, pas de nouvel appel API.

TDD : test du composant (affiche les 3 méthodes exactes, pas "Générer un quiz" ; emit
`start-activity` avec le bon type au clic de chaque carte ; affiche classeur/tags/date) avant
l'implémentation. Puis test d'intégration dans `NoteEdit.spec.ts`/le fichier de test concerné
vérifiant que le bouton Notation est bien présent et désactivé.

## Task 5 : vérifier le câblage Feynman (pas de reconstruction)

`NoteFeynman.vue` existe déjà (livré par `reviser-hub`, déjà vérifié conforme à
`NoteFeynman.dc.html` dans un chantier antérieur) et la route `/notes/:id/feynman` existe déjà
dans `web/src/router/index.ts`. Vérifie seulement que `NoteSidebar`'s emit `'feynman'` (Task 4)
route bien vers `/notes/${noteId}/feynman` via `startAiActivity` — pas de nouveau composant, pas
de nouvelle route. Un test d'intégration suffit (clic sur la carte Feynman → navigation vers la
bonne route).

## Task 6 : retoner l'en-tête/barre d'outils/popup de partage/tiroir réglages du mode édition

**Fichiers** : `web/src/views/Notes/NoteEdit.vue` (bloc mode édition — en-tête, barre de
formatage, popup de partage si présent, tiroir de réglages si présent — localiser précisément
en relisant le fichier, ne pas supposer les mêmes lignes que l'ancien plan du 25/08).

Remplace toute valeur de style brute par le token équivalent du design system (charger le skill
`design-system` pour la table mockup-var → token si besoin). Pas de nouveau test dédié (retonage
visuel pur d'éléments déjà testés ailleurs) — mais faire tourner la suite complète avant/après
pour confirmer l'absence de régression comportementale, et vérifier au passage qu'aucune
occurrence brute (`grep -n "text-\[\|bg-\[\|slate-\|pink-\|cyan-\|teal-\|sky-"`) ne subsiste
dans la zone retonée.

## Task 7 : retoner le HTML généré par `renderMarkup` (lecture active, boutons SM-2, diagrammes)

**Fichiers** : `web/src/views/Notes/NoteEdit.vue` (`renderSm2Buttons`, `renderMarkup`, et toute
fonction générant du HTML injecté via `v-dompurify-html`). Les classes `sm2-btn-*`
(`pink-50`/`cyan-50`/`teal-50`/`sky-50`/etc., confirmées présentes au 2026-08-30) sont
générées en JS (chaînes de template), pas du HTML statique dans le `<template>` — la
substitution doit se faire dans les fonctions qui construisent ces chaînes. Même principe de
non-régression que Task 6 (pas de nouveau test dédié, suite complète avant/après, grep de
vérification).

## Task 8 : corriger la lacune d'erreur silencieuse, ajouter le fil d'ariane, retoner l'en-tête du mode lecture

**Fichiers** : `web/src/views/Notes/NoteEdit.vue` (`loadNoteDetails`, en-tête du bloc mode
lecture). Trois changements distincts, un seul test dédié nécessaire (les 2 autres sont du
retonage) :

1. **Fil d'ariane** (écart réel confirmé contre le canevas) : le canevas montre
   `BIBLIOTHÈQUE / CHIMIE ORGANIQUE / NOTES` au-dessus du titre — mono, majuscules,
   `text-ink-muted`. L'état actuel n'a que le bouton « Retour aux notes », pas de fil d'ariane.
   Ajoute-le : classeur de la note (nom réel, pas fictif — via le store déjà utilisé pour
   charger la note) + « Notes » en dernier segment. Si le classeur est absent (note non
   classée), afficher un segment adapté plutôt qu'un texte vide ou fabriqué — cohérent avec
   la contrainte anti-fabrication du projet.
2. **État d'erreur de chargement** : suit le même pattern déjà utilisé sur `Accueil.vue`/
   `StudyDeck.vue` pour ce cycle de refonte (ref `loadError` booléen, affiché si
   `loadNoteDetails()` échoue, au lieu d'un échec silencieux).
3. Retonage du reste de l'en-tête du mode lecture (valeurs brutes restantes).

TDD pour le point 2 (état d'erreur) et le point 1 (fil d'ariane) — test avant code pour les
deux, écrit dans `web/tests/views/Notes/NoteEdit.spec.ts` (nouveau fichier si Task 9 ne l'a pas
encore créé — dans ce cas Task 9 le trouvera déjà présent et l'étendra, pas de duplication).

## Task 9 : suite de tests comportementaux complète pour `NoteEdit.vue`

**Fichiers** : `web/tests/views/Notes/NoteEdit.spec.ts` (étend le fichier commencé en Task 8 si
présent, le crée sinon).

Un test par élément/action/état non déjà couvert par les tests des Tasks 1-8 : chargement
(spinner puis contenu), bascule édition/lecture, sauvegarde auto, chaque transformation de
sélection (`def`/`qcm`/`ordre`/`assoc`/`vf`/`diagramme`), export PDF, lien entre notes, mode
Révision Active vs Lecture, etc. — même méthode que la procédure `migration-ecran` (un test par
item recensé), à partir d'un inventaire écran fait en début de tâche (relire tout le fichier
actuel, lister chaque élément interactif visible, cocher au fur et à mesure).

## Task 10 : vérification visuelle réelle + mise à jour `ETAT.md` + clôture

Même discipline que les chantiers précédents (`bibliotheque-redesign`, `revision-flexibilite`) :
environnement natif (backend + Vite, pas de Docker), données de test réelles, vérification en
direct (pas seulement via les tests) :
- Sidebar Assistant IA : exactement 3 méthodes, pas de « Générer un quiz ».
- Bouton Notation visible, désactivé, tooltip explicite.
- Fil d'ariane présent et correct.
- Feynman toujours accessible et fonctionnel (non-régression).
- `NoteQuiz.vue`/sa route toujours accessibles directement par URL (pas supprimés, juste
  retirés du panneau).
- Mode édition inchangé fonctionnellement, juste retoné visuellement.
- Responsive 375px/1440px + mode sombre sur les 2 modes (édition/lecture) et la sidebar.
- Aucune régression sur l'export PDF, le lien entre notes, la Révision Active.

Puis mise à jour `ETAT.md` (avancement de l'écran 4), `workflow/editeur-notes-notation-ia/
{PLAN,JOURNAL}.md`, `workflow/JOURNAL.md`, commit, revue finale de branche (modèle le plus
capable), boucle de correction si besoin, puis clôture `gestion-chantier` (push demandé à
l'utilisateur, PR, attente CI, merge, PR de clôture de suivi comme pour les chantiers
précédents).
