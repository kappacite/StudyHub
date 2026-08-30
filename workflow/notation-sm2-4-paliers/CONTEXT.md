# Notation manuelle — 4 paliers SM-2 (alignés sur le graphique de stats)

Statut : clos
Branche : feature/notation-sm2-4-paliers
PR : #136

## Pourquoi

Demande explicite de l'utilisateur après avoir vu les captures d'écran du chantier
`revision-flexibilite` : les boutons de notation manuelle (« À revoir/Moyen/Acquis », scores
1/3/5) ne correspondent à aucune échelle visible ailleurs dans l'app, alors que
`RevisionSetStats.vue` affiche déjà un graphique « PAR NOTATION SM2 » à 4 paliers (Encore/
Difficile/Bien/Facile — `GradeDistribution` backend : `again` 0-1, `hard` 2, `good` 3-4, `easy`
5). L'utilisateur veut que les boutons de notation reprennent ces 4 mêmes paliers.

## Comment

`SelfEvalButtons.vue` (composant partagé, 6 emplacements : flashcard/definition/vf/association/
ordre dans `RevisionStudy.vue`, QCM dans `QcmRun.vue`) passe de 3 à 4 boutons : Encore (1),
Difficile (2), Bien (4), Facile (5) — mêmes couleurs que le graphique (danger/accent/primary/
success). Seule ambiguïté réelle : le palier « Bien » couvre 2 valeurs (3 et 4) dans la
répartition existante — tranché en chat avec l'utilisateur (`AskUserQuestion`) : **4**, qui
laisse le facteur de facilité SM-2 inchangé (ni hausse ni baisse), plutôt que 3 (qui le ferait
légèrement baisser).

Changement purement présentationnel côté frontend, aucun changement de contrat backend (le
paramètre `score` était déjà libre entre 1 et 5 depuis `revision-flexibilite`, Task 1).

## Dépendances

Aucune. Indépendant des autres chantiers planifiés.

## Historique complet des décisions

Voir `workflow/notation-sm2-4-paliers/JOURNAL.md`.
