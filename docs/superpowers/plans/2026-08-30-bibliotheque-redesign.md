# Bibliothèque Redesign — Draft Plan (NOT ready to execute)

> **Statut : brouillon, décisions produit en attente.** Ce plan décompose le travail probable
> une fois les questions ouvertes du spec (`docs/superpowers/specs/2026-08-30-bibliotheque-redesign-design.md`,
> § « Ce qui n'est PAS tranché ici ») résolues avec l'utilisateur. **Ne pas dispatcher ces
> tâches en `subagent-driven-development` avant un `superpowers:brainstorming` explicite qui
> tranche Task 0 ci-dessous.** Contrairement à `reviser-hub-redesign` (déviations presque
> toutes visuelles, tranchées unilatéralement avec raisonnement écrit), l'arbre de
> sous-dossiers et le contenu non rangé touchent à la navigation même de l'app — pas de
> simples choix de mise en page.

**Périmètre : `Binders.vue` uniquement** (écran Bibliothèque, racine + contenu d'un classeur).
`PDFs.vue`/`Diagrams.vue` sont déjà dans le périmètre du chantier planifié
`ecrans-peripheriques-visuels` (skill `migration-ecran`, qui inclut nativement la
consultation de la vraie maquette) — pas dupliqués ici, voir le spec § « Recoupement avec un
chantier déjà planifié ».

**Contexte** : investigation faite en chat (2026-08-30) suite à une question directe de
l'utilisateur — confirmé que `Binders.vue` n'a jamais été comparé aux vraies maquettes
Direction A (`Bibliotheque.dc.html`, `Notes.dc.html`), contrairement à
`RevisionSetDetail.vue`/`RevisionSetModal.vue` (chantier `bibliotheque-ensembles`, déjà
vérifiés, décisions tracées, hors scope ici).

**Spec** : `docs/superpowers/specs/2026-08-30-bibliotheque-redesign-design.md` — lire en
entier avant de commencer le brainstorming, il documente précisément où et pourquoi l'écart
existe pour chaque écran.

---

### Task 0 (préalable, pas une tâche de code) : Brainstorming — trancher les décisions produit

À faire avec l'utilisateur, `superpowers:brainstorming`, avant toute autre tâche :

1. **Arbre de sous-dossiers** (colonne gauche `SplitView`) : retiré pour coller à la maquette
   (aucune des deux maquettes, `Bibliotheque.dc.html` ni `Notes.dc.html`, ne le montre) ou
   conservé comme fonctionnalité réelle ajoutée après coup ? Si conservé : où vit-il
   visuellement si la racine devient une grille de classeurs (Task 1) ?
2. **Contenu non rangé à la racine** (notes/decks/ensembles/diagrammes/PDF avec
   `binder_id === null`) : où et comment y accéder si la racine devient une simple grille de
   classeurs sans onglets de contenu ?
3. **Onglet « Autres »** (Diagrammes+PDF, décision déjà tracée par `bibliotheque-ensembles`
   pour ne pas perdre de fonctionnalité malgré son absence de `Notes.dc.html`) : conserver
   tel quel (probable), sachant que le contenu de cet onglet (`Diagrams.vue`/`PDFs.vue`) sera
   redessiné séparément par `ecrans-peripheriques-visuels` — ce chantier n'a besoin que de
   décider si l'onglet lui-même survit, pas de refondre ce qu'il contient.

Sortie attendue : un spec de correction (`*-bibliotheque-redesign-corrected.md` ou équivalent,
suivant le pattern `reviser-hub-redesign`) qui remplace les décisions ouvertes de ce document
par des décisions tranchées, avant d'écrire les tâches TDD détaillées des Tasks 1-3 ci-dessous.

---

### Task 1 (esquisse) : `Binders.vue` — écran racine reconstruit selon `Bibliotheque.dc.html`

Grille de cartes classeur (3 colonnes desktop) : icône, nom, `N decks · M notes`, dernière
activité, liseré de couleur, bouton « Nouveau classeur ». Remplace le `SplitView` actuel
**uniquement à la racine** (`currentBinderId === null`) — le comportement à l'intérieur d'un
classeur est Task 2. Dépend de la décision Task 0.1/0.2 (arbre, contenu non rangé) pour savoir
si quelque chose doit survivre en dehors de la grille elle-même.

Fichiers probables : `web/src/views/Binders/Binders.vue` (probablement scindé en 2 vues —
liste racine vs. contenu d'un classeur — plutôt qu'un seul fichier avec `v-if` sur
`currentBinderId`, à trancher au moment du plan détaillé selon la taille résultante de chaque
partie), `web/src/stores/binders.ts` (si des champs d'agrégation manquent — nombre de decks/
notes par classeur, déjà peut-être calculable côté client depuis les stores existants, à
vérifier avant d'ajouter un endpoint).

### Task 2 (esquisse) : Contenu d'un classeur reconstruit selon `Notes.dc.html`

Bascule 2 boutons Notes/Révision (+ « Autres » conservé par décision Task 0.3), liste à une
colonne sans colonne latérale (sous réserve de la décision Task 0.1 sur l'arbre). Onglet
Révision : ensembles de révision uniquement dans le style de la maquette (icône type, nom,
`N éléments · dernier passage`, mini-icônes, badge dues, 3 actions) — les decks classiques
soit fusionnés visuellement comme aujourd'hui (déjà décidé par `bibliotheque-ensembles`, pas
à retrancher sans nouvelle raison), soit revus si Task 0 en décide autrement.

Fichiers probables : `web/src/views/Binders/Binders.vue` (ou son successeur post-Task 1),
tests associés.

### Task 3 (esquisse) : Vérification visuelle réelle + vérification rapide de `RevisionSetDetail.vue`/`RevisionSetModal.vue`

Même procédure que `reviser-hub-redesign` Task 8 (environnement natif, comparaison côte à
côte avec les vraies maquettes, clair/sombre × desktop/mobile). Inclut une vérification
rapide (pas un redesign) de `RevisionSetDetail.vue`/`RevisionSetModal.vue` pour confirmer
qu'aucune régression visuelle ne s'est glissée depuis leur dernière vérification par
`bibliotheque-ensembles`.

---

## Ce que ce brouillon ne fait PAS

Il ne donne pas d'étapes TDD précises (fichiers de test exacts, code à écrire) comme
`reviser-hub-redesign` — c'est délibéré : les décisions de Task 0 (arbre de sous-dossiers,
contenu non rangé) touchent à la navigation même de l'app, pas seulement à la mise en page.
Écrire des étapes précises maintenant risquerait de devoir les jeter si le brainstorming change
la structure retenue.
