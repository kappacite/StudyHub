# Plan — bibliotheque-notes-listes

Une case = une tâche atomique. TDD (skill `cycle-tdd`) : le test précède le code.
Ordre choisi : du plus structurant (en-tête/onglets, qui conditionne la silhouette) vers le
plus local (lignes), puis vérification visuelle réelle.

- [x] Task 1 — `Tabs.vue` : variante « bascule » (conteneur surélevé, thumb) sans casser la
  variante pastilles utilisée par les autres écrans. Prop `variant` avec défaut = existant.
- [x] Task 2 — `Binders.vue` en-tête : titre dynamique « Notes » / « Révision » selon
  l'onglet dans un classeur (« Bibliothèque » à la racine), sur-titre mono majuscule à la
  place du fil d'Ariane texte, un seul bouton primaire visible, le reste replié dans un menu.
- [x] Task 3 — `Binders.vue` racine : sous-titre `N classeurs · N notes · N decks` sur le
  `PageHeader` (agrégation client-side, même principe que `cardAggregate`).
- [x] Task 4 — `BinderCard.vue` : liseré gauche 4px + rayon 4px, densité verticale alignée
  sur la maquette. Rebrancher l'accentuation de la carte la plus récemment active.
- [x] Task 5 — Lignes de notes : extrait tronqué (1 ligne, depuis `content`), pastille de tag,
  date relative alignée à droite (réutiliser `formatDayDiffLabel` déjà dans `Binders.vue`),
  icône globe si `is_public`. Séparateurs pointillés, suppression du second titre interne.
  Ajouter `is_public` au type `Note` du store s'il manque côté front.
- [ ] Task 6 — Lignes d'ensemble : bouton ▶ Réviser en première position, stats/détacher/
  supprimer repliés dans un menu par ligne, phrase d'explication au-dessus de la liste.
- [ ] Task 7 — Largeur : 920px pour la liste de contenu dans un classeur, grille racine
  inchangée (`wide`). Vérifier qu'aucun autre consommateur de `PageContainer` ne change.
- [ ] Task 8 — Barre de filtre par tags : la sortir de la bande pleine largeur (absente de la
  maquette) sans perdre la fonctionnalité — décider entre repli dans l'en-tête et affichage
  conditionnel (uniquement si des tags existent).
- [ ] Task 9 — Vérification visuelle réelle contre les maquettes (racine / classeur Notes /
  classeur Révision × clair-sombre × 375-1440px) + non-régression de la suite de tests.
