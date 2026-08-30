# Journal — editeur-notes-notation-ia

## 2026-08-30 (ouverture, réconciliation de l'ancienne branche)

Demande utilisateur : "commence le chantier sur la refonte de l'éditeur. assure-toi de
respecter le canvas."

Investigation avant toute action (fork, lecture seule sur `.worktrees/noteedit-migration`) :
la branche `feature/noteedit-migration` (25/08) a déjà 15 commits — bien plus avancée que ce
que `CONTEXT.md` laissait penser. Mais conflit majeur confirmé : `reviser-hub` (mergé depuis) a
réécrit 2477 des 3499 lignes de `NoteEdit.vue`, exactement la même zone. Rebase/merge
impraticable. Les 2 derniers commits de cette branche (`ETAT.md`) sont obsolètes, remplacés par
`d6c0e09` et les chantiers mergés depuis. Un stash jamais appliqué (`749ea6c`, "amendement
noteedit-migration-plan... à reprendre lors de la réconciliation") contenait une correction de
la Task 4 (NoteSidebar à 3 méthodes) déjà motivée par une vérification du canevas — confirmée
exacte en extrayant `NoteEdit.dc.html` moi-même : la maquette montre bien une sidebar (pas une
modale) à exactement 3 méthodes (Évaluation mixte/Feuille blanche/Feynman, sans "Générer un
quiz") + un bouton "Notation" séparé dans l'en-tête. `main` actuel a toujours l'ancienne modale
à 4 activités — écart réel confirmé, pas une supposition.

Ruling : traiter l'ancienne branche/stash comme référence de conception (déjà vérifiée contre
le canevas pour sa Task 4), pas comme base de merge littérale. Nouvelle branche
`feature/editeur-notes-notation-ia` ouverte depuis `main` à jour. Ancien worktree/branche
laissés intacts (rien détruit). Vérifié aussi : aucune des 3 modales à extraire n'a été faite
par `reviser-hub` (tâches d'extraction toujours valides) ; de nombreuses valeurs de style
brutes subsistent (tâches de retonage réelles, pas préventives) ; le fil d'ariane du canevas
est absent de l'état actuel (écart réel confirmé).

Nouveau plan détaillé écrit contre l'état réel de `main` (10 tâches TDD) :
`docs/superpowers/plans/2026-08-30-editeur-notes-redesign.md`. Volet backend (Notation de la
note, flux 2) laissé hors périmètre — nécessite son propre brainstorming, bouton Notation
ajouté désactivé en attendant. Chantier passé de `planifié` à `ouvert`. Exécution démarrée en
`subagent-driven-development`, suite ci-dessous.
