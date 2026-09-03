# Notes (Notation IA, Blurting, Feynman), Planning vide, fuite de balisage, éditeur épuré

Statut : pr-ouverte
Branche : feature/notes-ia-planning-corrections
PR : #144

## Pourquoi

Demande explicite de l'utilisateur (2026-09-03), 6 points groupés en un seul message :
1. Fonction de Notation IA pour les notes (regarder le canevas)
2. Blurting (regarder le canevas)
3. Méthode Feynman (regarder le canevas)
4. Le planning de révision ne marche plus (toujours vide)
5. `<!--- sectionbody` qui s'affiche brut dans l'aperçu des notes depuis la bibliothèque
6. Refonte de l'interface de l'éditeur de notes — moins surchargée, boutons réorganisés

L'utilisateur a explicitement délégué tous les arbitrages de conception ("prend les décisions
d'arbitrage par toi-même, ne me demande rien") — aucune question en chat sur ce chantier,
toutes les décisions ci-dessous sont tranchées et documentées ici pour traçabilité.

## Investigation (avant tout code)

Canevas source : artefact Claude Design `https://claude.ai/code/artifact/366dcc95-8da4-41dd-8bbd-1e625a68e2c5`
(déjà utilisé par `bibliotheque-redesign`/`editeur-notes-notation-ia`), artboards lus en direct
dans le navigateur (le HTML statique de l'artefact ne contient pas le contenu des artboards,
chargé dynamiquement — extraction par capture d'écran zoomée, pas par lecture de fichier).

### 1. Notation IA (backend + frontend)

C'est exactement le volet backend explicitement différé par `editeur-notes-notation-ia` (#138,
mergé) : le bouton « Notation » existe déjà dans `NoteEdit.vue:618-627`, câblé `disabled` avec
le commentaire *« en attente du backend de notation IA (flux 2) »*. Canevas `Note — Notation
(IA)` : titre « Notation de la note », score en gros cercle (**8,2**, format décimal /10, pas
%), phrase de verdict (« Note solide et bien structurée »), deux colonnes « Points forts »
(vert) / « Améliorations » (orange), section « Suggestions » (paragraphe). Modèle de service
IA le plus proche dans le code actuel : `AIService.analyze_feynman`/`analyze_blurting`
(`backend/app/services/ai_service.py`, JSON structuré via `_generate_json_object`, flux
Celery + repli synchrone déjà standard sur `evaluation_service.py`/route dédiée).

### 2. Blurting

Écart déjà documenté dans les notes de `ecrans-peripheriques-visuels` (jamais commencé) :
canevas `Blurting.dc.html` = zone de texte libre + bouton « Analyser avec l'IA » + **une seule**
carte d'analyse (score /10, ex. 7,6, lacunes identifiées, suggestion). `Blurting.vue` actuel
(lu en entier) a une structure bien plus riche : jauge circulaire « Rétention » en %, bloc
« Bilan de votre tuteur » séparé, cartographie des concepts avec statut de mémorisation par
concept, et une colonne entière de génération + import de flashcards vers un deck. Couleurs en
grande partie brutes (`text-emerald-500`, `bg-rose-950/30`...), violation de la règle
« toujours un token » (`web/CLAUDE.md`).

**Arbitrage tranché** : ne pas supprimer la génération/import de flashcards (fonctionnalité
réelle et valable, absente du canevas mais pas un accident — un chantier précédent
(`bibliotheque-redesign`) a justement traité la perte accidentelle de fonctionnalité pendant
une refonte comme un défaut Critical, pas une simplification acceptable). Décision : retoner la
carte d'analyse primaire pour suivre la structure du canevas (score affiché en /10 à une
décimale au lieu du % actuel — harmonise avec Notation et Feynman ci-dessous — un seul bloc
« Analyse » cohérent au lieu de jauge+bilan séparés), remplacer toutes les couleurs brutes par
des tokens sémantiques, et conserver « Concepts clés » + « Flashcards suggérées/import » comme
section secondaire sous la carte d'analyse plutôt que dans une colonne séparée qui concurrence
visuellement le canevas. Aucun changement de schéma côté `AIService.analyze_blurting` (le
retention_score 0-100 existant est juste réaffiché divisé par 10) ni de route.

### 3. Méthode Feynman

`NoteFeynman.vue` (lu en entier) est déjà structurellement proche du canevas `Note — Méthode
Feynman (IA)` (texte libre → bouton « Analyser » → score + bilan + 3 blocs Jargon/Lacunes/
Suggestion) et utilise déjà des tokens sémantiques (`bg-accent-soft`, `bg-warning-soft`,
`bg-danger-soft`, `bg-success-soft`) — pas de violation de couleur brute détectée. Seul écart
notable : score affiché en `%` (`feynmanResult.score}}%`) au lieu du format `/10` à une
décimale du canevas. **Arbitrage** : petite tâche de vérification/harmonisation du format de
score uniquement (même changement que Blurting/Notation), pas de refonte structurelle.

### 4. Planning de révision toujours vide

Root cause confirmé en lisant `backend/app/services/planning_service.py` : `get_calendar()` et
`advance_review()` n'interrogent que `FlashcardDAO`/`DeckDAO` (`Flashcard.next_review`,
groupement par `deck_id`). Le système `RevisionItem`/`RevisionSet` (vf/qcm/association/ordre/
flashcard-en-ensemble), devenu le mode d'étude principal au fil des chantiers récents
(`bibliotheque-ensembles`, `reviser-hub`, `revision-flexibilite`, `revision-qcm-heterogene`),
n'est jamais agrégé. Un compte qui étudie surtout via des ensembles de révision (cas du compte
dev vérifié en Task 3 de `revision-qcm-heterogene` : que des `RevisionSet`, aucun `Deck`) voit
donc un planning à zéro cartes en permanence. Même classe de bug que celui trouvé et corrigé
pendant `reviser-hub` (stats vides faute d'agréger le bon type polymorphe).

**Arbitrage** : étendre `PlanningService.get_calendar()` pour agréger aussi les `RevisionItem`
dus (par `RevisionSet`, même principe de regroupement que par `deck_id` aujourd'hui — un jour
peut mélanger des decks et des ensembles dans son `breakdown`). `advance_review()` étendu de la
même façon pour permettre l'anticipation sur un `RevisionSet` en plus d'un `Deck`. Le contrat
de réponse (`PlanningDay`/`breakdown`) reste le même format, un item de breakdown gagne juste un
`kind: 'deck' | 'revision_set'` (ou équivalent) pour que le frontend route correctement le clic
« Réviser » (`studyDeckAdvance` doit distinguer `/decks/:id/study?advance=true` de
`/revision/sets/:id/study` selon le type).

### 5. `<!--- sectionbody` qui fuit dans l'aperçu bibliothèque

Root cause confirmé : `noteExcerpt()` (`web/src/views/Binders/Binders.vue:1272-1277`, ajouté par
`bibliotheque-notes-listes`) ne retire qu'un jeu fixe de caractères Markdown
(`#*_\`>`) — aucun traitement des commentaires HTML (`<!-- ... -->`). Recherche exhaustive dans
le code (`grep -r sectionbody`) : ce marqueur n'est produit par **aucun** service IA ni template
du dépôt — il vient forcément d'un contenu collé par l'utilisateur (export Word/Google Docs ou
autre) et enregistré tel quel dans `note.content`. Invisible en rendu normal (un commentaire
HTML ne s'affiche jamais dans le navigateur via `marked`), mais l'extrait brut de
`noteExcerpt()` ne passe jamais par un rendu HTML — juste des regex sur la chaîne — donc le
commentaire fuit tel quel.

**Arbitrage** : étendre la regex de `noteExcerpt()` pour retirer aussi les commentaires HTML
(`<!--[\s\S]*?-->`) avant le nettoyage Markdown existant. Fix localisé, un seul fichier.

### 6. Éditeur de notes — refonte moins surchargée

`NoteEdit.vue` (mode édition) lu en entier : Ligne 1 de l'en-tête cumule 9 contrôles (bascule
sidebar, titre, statut de sauvegarde, sélecteur de classeur, `TagSelector`, bascule
Contexte/Liens, bascule Aperçu, bouton Visualiser, bouton Partage, bouton Guide) ; Ligne 2
(barre de formatage) cumule 3 groupes de boutons (Format/LaTeX/Code), un bouton Définition, un
sélecteur d'insertion de diagramme. Mode lecture : 5 contrôles supplémentaires dans sa propre
barre (Retour, bascule Lecture/Révision Active, Modifier, Guide, Exporter PDF) + le bouton
Notation à côté du titre. Le canevas `NoteEdit.dc.html` (déjà vérifié conforme lors
d'`editeur-notes-notation-ia`) ne détaille pas le niveau de densité de cette barre d'outils —
pas de cible pixel-perfect à suivre ici, refonte guidée par jugement UX plutôt que par
comparaison canevas stricte (l'utilisateur demande explicitement une réorganisation, pas une
consultation du canevas pour ce point précis).

**Arbitrage** : regrouper par fréquence d'usage plutôt que supprimer des fonctions. Ligne 1 :
garder visibles Titre, statut de sauvegarde, Partage, Visualiser (usage fréquent) ; regrouper
Classeur/Tags/Contexte-Liens/Aperçu/Guide derrière un seul menu « Réglages » (icône, popover) —
6 éléments visibles au lieu de 9. Ligne 2 : les 3 groupes de boutons de formatage restent (usage
très fréquent, un menu les cacherait plus qu'il n'aiderait) mais Définition + Insertion de
diagramme (usage occasionnel) rejoignent un unique menu « Insérer » à droite de la barre. Mode
lecture : fusionner Guide dans le même menu « Réglages » que le mode édition pour cohérence,
garder Retour/bascule Lecture-Révision/Modifier/Exporter PDF visibles (usage fréquent). Aucune
fonctionnalité supprimée, uniquement regroupée. Vérification visuelle réelle obligatoire en fin
de tâche (375px/1440px, clair/sombre) — pas de cible canevas à comparer, donc pas de
`migration-ecran` classique, jugement direct dans l'app.

## Comment (plan détaillé : `PLAN.md`)

7 tâches TDD, ordonnées : corrections ciblées d'abord (planning, fuite HTML — gains rapides,
risque faible), puis Notation IA (backend, puis frontend), puis Blurting, puis Feynman
(harmonisation mineure), puis refonte de l'éditeur en dernier (la plus ouverte/visuelle).

## Dépendances

Aucune dépendance amont bloquante. Recoupements avec des chantiers existants, tous encore
`planifié`/non commencés, mis à jour dans leurs propres `CONTEXT.md` pour éviter la
duplication :
- `ecrans-peripheriques-visuels` : son entrée « Blurting — retonation visuelle seulement... »
  est traitée ici, pas là-bas (portée réelle bien plus large qu'une retonation, cf. ci-dessus).
  Sa note du 2026-08-30 sur Blurting reste la trace de l'investigation initiale.
- `editeur-notes-notation-ia` (clos) : son volet backend différé (« nécessite son propre
  brainstorming/spec ») est repris ici (Tâche 3).

### 7. Écran d'accueil — "Charge à venir (14j)" toujours à 0

Demande explicite de l'utilisateur (2026-09-03, après la Task 14) : même symptôme que le
planning (item 4) mais sur l'écran d'accueil (`Accueil.vue`). Investigation : `FocusService`
(`backend/app/services/focus_service.py`) a trois méthodes — `get_today_items()` (compteurs
"Aujourd'hui") agrège déjà `RevisionItem`/`RevisionSet` (section 3, corrigé lors de
`reviser-hub`, confirmé en lisant le code) ; `get_forecast()` (Charge à venir 14j) **n'agrège
que `Flashcard`/`Deck`**, jamais `RevisionItem`/`RevisionSet` — root cause exacte, même classe
de bug que le planning (Task 1). Un compte qui étudie surtout via des ensembles voit donc un
histogramme de charge à venir vide même s'il a des révisions programmées. `get_retention_by_subject`
(Rétention par matière) est également flashcard-only (`overdue_count` par classeur), mais ce champ
n'est pas rendu dans le template `Accueil.vue` (seuls `retention_pct`/`trend_7d`/`binder_name` le
sont) — hors périmètre, rien à corriger côté UI actuellement affiché.

**Arbitrage** : étendre `get_forecast()` pour additionner les `RevisionItem` dus par jour (même
fenêtre `days`), sans filtrage de type (contrairement aux `Flashcard`, un `RevisionItem` est déjà
un type de révision valide). Détail : `PLAN.md` Task 15.

## Historique complet des décisions

Ce fichier + `workflow/notes-ia-planning-corrections/JOURNAL.md`. Canevas source cité en tête
de la section Investigation ci-dessus.
