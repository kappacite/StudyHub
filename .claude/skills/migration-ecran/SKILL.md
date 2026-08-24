---
name: migration-ecran
description: Procédure reproductible de refonte d'un écran (phase 4) — inventaire, états à couvrir, composition depuis les primitives, tests, capture d'écran, commit. À charger avant de migrer une vue.
---

# migration-ecran

Un écran par cycle (voir `AGENTS.md` §8 du prompt de démarrage pour l'ordre des écrans — le
plus structurant d'abord). Le subagent `migrateur-ecran` applique cette procédure et n'a pas le
droit de modifier les tokens : s'il en manque un, il remonte le besoin plutôt que d'improviser.

## Étapes

1. **Inventaire de l'existant** — lire la vue actuelle en entier
   (`web/src/views/<Section>/<Nom>.vue`) et lister exhaustivement : chaque élément
   d'interface, chaque action utilisateur possible, chaque appel API déclenché. Cette liste
   devient les assertions des tests à l'étape 3 — rien ne doit être perdu en route sans
   validation explicite (règle d'or : ne rien supprimer sans que l'utilisateur l'ait validé ;
   sinon, le signaler dans `ETAT.md` sans le retirer).
2. **Comportement attendu, état par état**, écrit dans `ETAT.md` avant le premier test :
   **vide** (aucune donnée), **chargement**, **erreur** (API en échec), **dense** (beaucoup de
   données), **hors ligne** (si applicable côté mobile/Capacitor).
3. **Tests et rouge** — un test par fonctionnalité recensée à l'étape 1, plus un test par état
   de l'étape 2. Constater l'échec pour la bonne raison (skill `cycle-tdd`).
4. **Composition** — uniquement à partir des primitives (`web/src/components/ui/`, tokens du
   design system une fois la phase 3 faite). Aucun style local, aucune couleur/rayon/ombre en
   dur.
5. **Copie** — verbes actifs, casse de phrase, vocabulaire constant sur un même flux (le bouton
   "Publier" produit "Publié"). Erreurs : ce qui s'est passé + comment réparer, sans
   s'excuser. Écran vide = invitation à agir, pas constat de vide.
6. **Refactor à tests verts.**
7. **Capture d'écran** clair/sombre × desktop (1440px)/mobile (375px) — exception TDD pour le
   rendu purement visuel, pas pour le comportement (états, focus, clavier) qui reste testé.
8. **Mise à jour `ETAT.md`** (écran migré, coché) puis **commit** (`feat(ui): …`).

## Non négociable

Contraste AA (y compris états colorés SM-2, jamais seule porteuse d'info — forme/libellé/icône
en renfort), cibles tactiles ≥ 44px, `safe-area-inset` iOS, `prefers-reduced-motion` avec
chemin dégradé fonctionnel, 60 fps sur Android milieu de gamme pour toute animation.
