# Diagrammes — canevas, panoramique, zoom (Phase 5, cycle 3)

Statut : clos
Branche : feature/diagrammes-canevas-pan-zoom
PR : #147

## Pourquoi

Cycle 3/14 de la refonte Phase 5 (`docs/PROMPT_DEMARRAGE.md` §8), suite de
`diagrammes-commandes-annulation` (cycle 2, PR #146 mergée). Séquence complète : voir
`workflow/diagrammes-modele-document/CONTEXT.md`. **Premier cycle qui produit un rendu
visuel** — les deux précédents étaient de la logique pure non branchée sur l'écran.

## Investigation : architecture réelle du rendu existant (avant de choisir)

Correctif à la caractérisation du cycle 1 : `Diagrams.vue` n'est **pas** un canevas SVG pur.
Inspection DOM en direct (via Chrome) : les nœuds sont des `<div>` positionnés en absolu
(`class="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-grab..."`), et le
`<svg>` ne contient que 2 `<path>` (les liens). C'est un **hybride DOM+SVG** : divs pour les
formes (texte éditable, styles Tailwind directs), SVG pour les tracés de liens uniquement.

**Mesure de FPS tentée, non concluante** : diagrammes de test à 50/150/300/600 nœuds injectés
directement en base, tentative de mesure automatisée du coût par frame pendant un glisser
(événements `MouseEvent` synthétiques + `requestAnimationFrame`/microtask). Résultat : le
nœud ciblé ne bougeait jamais suite aux événements synthétiques (`moved: 0` constaté), signe
que la logique de glisser réelle dépend probablement de `event.buttons`/capture de pointeur
non reproduits fidèlement par un `MouseEvent` construit à la main dans cet environnement
d'automatisation — pas une mesure fiable de la performance réelle de l'app. Abandonné plutôt
que de s'acharner sur un outillage qui fausse la mesure. Fixtures de test supprimées après
coup.

**Conséquence sur la décision** : ça ne bloque pas ce cycle. Ce chantier ne construit ni
glisser-déposer ni sélection (cycle 4) — sa charge de travail réelle (panoramique, zoom) est
un unique changement de transformation (viewBox SVG ou `transform` CSS), un coût constant
**indépendant du nombre d'éléments**, à condition que le rendu soit borné à la fenêtre de vue
(§8.6 : « un canevas infini impose... de ne rendre que ce qui est visible »). C'est le
recadrage/glisser d'un élément individuel (cycle 4) qui aurait vraiment besoin d'un chiffre de
fps mesuré — reporté à ce moment-là, si le profilage réel de l'app (outils navigateur, pas de
la simulation d'événements) montre un besoin d'optimisation.

## Arbitrage — rendu : SVG, pas canevas 2D

**Décision** : SVG (dans la continuité du rendu de liens déjà existant), pas `<canvas>`.
Justifié par les besoins fonctionnels du module (§8.3/§8.5), plus décisifs ici qu'un chiffre
brut de fps :
- **LaTeX (KaTeX) dans les libellés** (§8.3) : KaTeX produit du HTML/MathML. L'intégrer dans
  un canevas 2D exige de rastériser en image ou de maintenir une superposition DOM parallèle
  — à ce stade autant faire du DOM/SVG directement.
- **Édition de texte en place, accessibilité** : `contenteditable`/`<input>` superposé,
  focus clavier, lecteurs d'écran — tous nativement disponibles en DOM/SVG, tous à
  réimplémenter à la main sur un canevas 2D (hit-testing, curseur de texte, etc.).
- **Styles via tokens Tailwind** (§8.6 : « aucun style local ») : s'applique directement à des
  éléments DOM/SVG, pas à un canevas 2D (qui dessine des pixels, pas des classes).
- **Continuité** : les liens sont déjà en SVG ; unifier sur SVG pour les formes évite de faire
  cohabiter deux systèmes de rendu.

**Le vrai levier de performance à grande échelle est le rendu borné à la fenêtre de vue**
(viewport culling), pas le choix SVG/canvas — un document de 10 000 éléments ne doit jamais
poser plus de nœuds DOM que ce qui est visible à l'écran. C'est la tâche centrale de ce cycle.

**Budget de bundle** : aucune dépendance ajoutée (§8.6 : fixer un plafond avant de choisir des
bibliothèques). La géométrie panoramique/zoom/culling est une fonction pure sur des
coordonnées (§8.7), quelques dizaines de lignes — pas de librairie pan-zoom nécessaire
(`d3-zoom` ou équivalent serait une dépendance non justifiée, règle 5 de l'échelle ponytail).

## Portée de ce chantier

- Modèle de caméra (`x`, `y`, `zoom`) + conversions écran↔monde, pures et testées.
- Rendu borné à la fenêtre de vue : calcul du rectangle visible en coordonnées monde, filtrage
  des éléments hors-champ.
- Recadrage sur tout le contenu (« recadrer sur tout », §8.4).
- Un composant `DiagramCanvas.vue` isolé (nouveau), rendu SVG avec viewBox piloté par la
  caméra, panoramique (glisser sur le fond) et zoom (molette). **Pas encore de sélection ni de
  déplacement d'élément** (cycle 4) — le canevas affiche les formes en lecture seule pour
  l'instant. Non routé dans l'application (comme les cycles 1-2, le socle continue de se
  construire en isolation ; `Diagrams.vue` reste inchangé jusqu'à ce que suffisamment de
  cycles soient prêts pour un remplacement réel).

## Dépendances

Suit `diagrammes-commandes-annulation` (cycle 2, PR #146 mergée) — consomme
`DiagramDocumentV1` (cycle 1) en lecture seule, n'a pas encore besoin de `DiagramHistory`
(pas de commande déclenchée par ce cycle).

## Historique complet des décisions

Ce fichier + `workflow/diagrammes-canevas-pan-zoom/JOURNAL.md`. Séquence complète des 14
cycles : `workflow/diagrammes-modele-document/CONTEXT.md`. Spec canonique :
`docs/PROMPT_DEMARRAGE.md` §8.
