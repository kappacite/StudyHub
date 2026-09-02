# Éditeur de notes, mode Zen, Assistant IA & Notation de la note

Statut : ouvert
Branche : feature/editeur-notes-notation-ia
PR : (aucune)

## Pourquoi

Écran 4 de la refonte phase 4 (`web/src/views/Notes/NoteEdit.vue`), étendu le 2026-08-27 pour
couvrir l'Assistant IA à 3 méthodes (Évaluation mixte, Feuille blanche, Feynman) et un nouveau
bouton « Notation » distinct — note la qualité de la fiche sur 100, à ne pas confondre avec
l'Évaluation mixte qui note la performance de l'élève sur des exercices générés.

## Ruling du 2026-08-30 : abandon de l'ancienne branche `feature/noteedit-migration`

L'utilisateur a demandé d'ouvrir ce chantier ("commence le chantier sur la refonte de
l'éditeur, assure-toi de respecter le canvas"). Investigation avant toute action (lecture
seule, worktree `.worktrees/noteedit-migration` conservé intact) :

- `feature/noteedit-migration` (créée le 25/08) a déjà 15 commits — bien plus avancée que ce
  que ce fichier laissait penser. Mais **conflit majeur confirmé** : `reviser-hub` (mergé PR
  #130, depuis) a réécrit 2477 des 3499 lignes de `NoteEdit.vue`, exactement la même zone
  (en-tête, section lecture, modale IA) que les tâches déjà faites sur cette branche. Un
  rebase/merge produirait un conflit massif et largement irrésolvable — les deux réécritures
  sont structurellement incompatibles.
- Les 2 derniers commits de cette branche (`7f2c4a6`, `5a807bb`, tous deux `ETAT.md`) sont
  obsolètes : leur contenu (audit des écrans manquants, décision de restructuration de la
  révision) a été remplacé par `d6c0e09` (28/08, sur `main`), qui a éclaté ce même plan en 6
  chantiers `workflow/` — dont celui-ci — et une bonne part de la restructuration décrite a
  depuis été livrée par `bibliotheque-ensembles`/`reviser-hub`/`revision-flexibilite`.
- Le stash `749ea6c` (jamais appliqué, "amendement noteedit-migration-plan... à reprendre lors
  de la réconciliation") contenait une réécriture de la Task 4 (NoteSidebar à 3 méthodes,
  retrait de "Générer un quiz" du panneau) **explicitement motivée par une vérification du
  canevas Direction A** — et une Task 5 complète pour construire `NoteFeynman.vue` de zéro,
  aujourd'hui redondante (Feynman déjà livré par `reviser-hub`, vérifié conforme au canevas
  dans un chantier antérieur). Contenu exact archivé (le stash lui-même est local, non
  transférable d'une machine à l'autre) :
  `workflow/editeur-notes-notation-ia/reference-stash-2026-08-30-noteedit-migration-plan-amendment.patch`.
- `NoteSidebar.vue` tel que committé sur la vieille branche a toujours l'ANCIENNE liste
  d'activités (Blurting/Générer un quiz/Évaluer la note) — jamais corrigée avant le stash.

**Vérification directe du vrai canevas** (`NoteEdit.dc.html`, extrait de l'artefact Claude
Design le 2026-08-30) : confirme exactement ce que le stash avait déjà déduit. La maquette
montre une **sidebar** (296px, pas une modale) "Assistant IA" avec exactement 3 boutons —
« Évaluation mixte », « Méthode de la feuille blanche », « Méthode Feynman » — et un bouton
« Notation » séparé dans l'en-tête (à côté du titre, pas dans la sidebar). `main` actuel
(`NoteEdit.vue:501-509`, `:1498-1534`) a toujours l'ancienne modale « Réviser avec l'IA » à 4
activités (blurting/quiz/evaluation/feynman) — écart réel confirmé, pas une supposition.

**Ruling : la vieille branche `feature/noteedit-migration` et son stash sont traités comme
référence de conception (déjà vérifiée contre le canevas pour la Task 4), pas comme base de
merge littérale.** Nouvelle branche `feature/editeur-notes-notation-ia` ouverte depuis `main`
à jour. L'ancien worktree/branche est laissé intact (rien de détruit, juste plus utilisé comme
base). Coût si ce ruling est faux : nul — l'ancienne branche reste disponible pour
consultation, aucune perte.

Vérifié aussi sur `main` actuel : aucune des 3 modales (`NoteEditHelpModal`/`NoteInputModal`/
`NoteEvaluationModal`) n'a été extraite par `reviser-hub` — les tâches d'extraction restent
valides. Le fichier contient encore de nombreuses valeurs de style brutes (`bg-[#070913]`,
`text-slate-500`, `bg-pink-50`, `text-[9px]`...) — les tâches de retonage restent nécessaires.
Le canevas montre un fil d'ariane (« BIBLIOTHÈQUE / CHIMIE ORGANIQUE / NOTES ») absent de l'état
actuel (seulement un bouton « Retour aux notes ») — écart réel confirmé.

## Comment

Deux volets :
- **Backend** (flux 2 d'`ETAT.md`) : nouvelle méthode `ai_service` de notation de fiche + route
  dédiée. Nécessite son propre brainstorming/spec (`superpowers:brainstorming` puis
  `superpowers:writing-plans`) avant implémentation — pas fait dans ce chantier, le bouton
  Notation reste désactivé en attendant. Indépendant du chantier `backend-ensembles-heterogenes`.
- **Frontend** : nouveau plan détaillé écrit contre l'état réel de `main` et le vrai canevas —
  `docs/superpowers/plans/2026-08-30-editeur-notes-redesign.md` (10 tâches TDD, reprend et
  adapte les décisions de conception déjà vérifiées de l'ancien plan/stash).

## Dépendances

Aucune dépendance amont. Le bouton Notation (volet frontend) reste désactivé tant que le volet
backend (non planifié dans ce chantier) n'a pas livré sa cible.

## Historique complet des décisions

`ETAT.md`, section « Plan global par flux ». Ancien plan (référence de conception uniquement,
pas exécuté tel quel) : `docs/superpowers/plans/2026-08-25-noteedit-migration-plan.md`. Nouveau
plan exécutable : `docs/superpowers/plans/2026-08-30-editeur-notes-redesign.md`. Détail complet
de la réconciliation : `workflow/editeur-notes-notation-ia/JOURNAL.md`.
