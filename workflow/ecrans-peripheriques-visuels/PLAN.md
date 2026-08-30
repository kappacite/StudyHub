# Plan — ecrans-peripheriques-visuels

> Détail ajouté le 2026-08-30 suite à l'investigation `bibliotheque-redesign`
> (`docs/superpowers/specs/2026-08-30-bibliotheque-redesign-design.md`) — comparaison directe
> aux vraies maquettes Direction A pour Blurting/PDF/Diagrammes. Dépendance Blurting→Feynman
> déjà levée (`NoteFeynman.vue` livré par `reviser-hub`). **Toujours pas ouvert, pas de
> `superpowers:brainstorming` fait sur ces 3 écrans** — ce détail sert à cadrer une future
> ouverture, pas à l'exécuter directement (contrairement à Blurting/PDF, Diagrammes/Marketplace/
> Auth n'ont pas de décision produit réelle en jeu, un cycle `migration-ecran` standard suffit).

- [ ] **Migrer Blurting (`Blurting.vue`)** — écart réel trouvé, pas une simple retonation :
  - Garder tel quel (maquette ne le montre pas, mais fonctionnalité réelle utile) : le score
    de « Rétention » (distinct du score de clarté /10 de la maquette), le bloc « Bilan de
    votre tuteur », les flashcards suggérées par l'IA.
  - À aligner sur la maquette (`Blurting.dc.html`) : structure de la carte d'analyse
    (clarté /10, jargon à simplifier, lacunes identifiées, suggestion) — vérifier si ces
    champs existent déjà côté données (`resultData.retention_score`? `general_feedback`?) ou
    s'il faut une correspondance de nommage plutôt qu'un nouveau contrat API.
  - **Décision à trancher avant d'écrire les étapes TDD** : la « cartographie des concepts »
    (statut de mémorisation par concept) reste-t-elle une section séparée en plus de la carte
    de la maquette, ou est-elle fusionnée dans la liste « Lacunes identifiées » de la maquette ?
    Pas tranché ici — nécessite un brainstorming léger à l'ouverture de ce chantier.
- [ ] **Migrer PDF (`PDFs.vue`)** — décision produit réelle avant tout TDD :
  - Option A : construire un vrai lecteur/annotateur selon `PDFs.dc.html` (panneau latéral
    liste + visionneuse avec surlignage/note inline, navigation page par page) — nouvelle
    fonctionnalité, nécessite de choisir une techno de rendu PDF (ex. `pdf.js`), plan TDD à
    part entière une fois la techno choisie.
  - Option B : garder la grille de fichiers actuelle (import/liste/tags) comme simplification
    assumée, documenter que `PDFs.dc.html` ne sera pas suivi pour ce produit.
  - **Ne pas commencer ce point sans avoir tranché A vs B avec l'utilisateur.**
- [ ] **Migrer Diagrammes — coquille uniquement (`Diagrams.vue`)** :
  - Ajouter une vue « galerie » d'entrée (grille de vignettes + titre + date de modification +
    bouton « Nouveau diagramme »), sur le modèle de `Diagrams.dc.html` — écran de sélection
    avant d'ouvrir l'éditeur 2-panneaux existant (Visuel/Mermaid), qui lui reste inchangé
    (aucune maquette dédiée pour l'éditeur, seulement pour l'écran d'entrée).
  - Fichiers probables : `web/src/views/Diagrams/Diagrams.vue` (probable scission galerie vs.
    éditeur, comme pour `Binders.vue`/`bibliotheque-redesign`), tests associés.
- [ ] Migrer Marketplace (`Marketplace/Home.vue`, `Explore.vue`, `PackagePreview.vue`)
- [ ] Migrer la page de note publique (`Notes/PublicNote.vue`)
- [ ] Migrer Auth (`Auth/Login.vue`, `Auth/Register.vue`)
- [ ] Vérification visuelle clair/sombre × desktop/mobile pour chaque vue, mise à jour `ETAT.md`
