# Journal — bibliotheque-notes-listes

## 2026-09-02 (ouverture)

Chantier ouvert à la demande explicite de l'utilisateur (« c'est à ça que doit ressembler la
vue bibliothèque », puis « compare avec Claude in Chrome »).

Comparaison faite en deux passes :
1. **Lecture des sources** — artboards `.dc.html` extraits du bloc `appifact-doc` de
   l'artefact publié (`366dcc95-…`), lus en entier : `Bibliotheque.dc.html` et
   `Notes.dc.html` (titre canvas exact : « Notes — Liste (bascule Notes / Révision) »,
   page-3).
2. **Comparaison visuelle réelle** — Claude in Chrome, thème clair des deux côtés, 1440px :
   maquettes zoomées depuis le canvas, app servie en local (Flask + Vite), base seedée avec
   le jeu de données de la maquette. Confirme la lecture des sources et ajoute un écart que
   la lecture seule n'avait pas fait ressortir : la barre `FILTRER / Tous` pleine largeur
   occupe la bande que la maquette laisse vide, sur les deux vues.

Constat détaillé et arbitrages retenus : `CONTEXT.md`. Plan en 9 tâches : `PLAN.md`.

Note d'environnement : ni Docker Desktop ni venv/`node_modules` n'existaient sur cette
machine — environnement local monté de zéro (venv Python 3.14 malgré la cible 3.12,
`npm install`, SQLite dev, Redis absent → cache mémoire). Aucun de ces éléments n'est
committé.

Prochaine action : Task 1 (variante bascule de `Tabs.vue`).

## 2026-09-02 — Task 1 : variante « segmented » de `Tabs.vue`

`Tabs.vue` gagne une prop `variant` (`'pills'` par défaut, `'segmented'` nouveau). La forme
historique est strictement inchangée — `Tabs` est partagé par `ClassesLanding`,
`TeacherDashboard`, `GroupDetail` et `DesignSystemDemo`, dont aucun ne passe la prop.

Choix techniques :
- Le conteneur porte le fond et l'ombre en `segmented` (`bg-surface shadow-elev-1
  rounded-btn-primary`, soit le rayon 10px de la maquette) ; il reste nu en `pills`. Les
  classes sont calculées dans le `<script setup>` plutôt qu'en ternaires imbriqués dans le
  template — trois axes (conteneur, forme d'onglet, état actif/inactif) rendaient le template
  illisible.
- **Écart assumé avec la maquette** : elle dessine une bascule d'environ 35px de haut
  (padding 9px, police 13px). `components/CLAUDE.md` exige des cibles tactiles ≥ 44px, donc
  la variante pose `min-h-11` ; le padding horizontal et le rayon de la maquette sont gardés.
  La hauteur est le seul point où la règle d'accessibilité l'emporte sur le pixel de la
  maquette, et c'est un choix, pas un oubli.
- `rounded-lg` (8px) pour le thumb là où la maquette écrit 7px : pas de token à 7px et
  `web/CLAUDE.md` interdit les valeurs brutes/classes arbitraires.

TDD : 5 tests ajoutés (conteneur surélevé, forme non-pilule, thumb actif, émission,
cible tactile) + 1 test de non-régression sur le conteneur nu de la variante par défaut.
Rouge vérifié sur les deux tests structurants (conteneur et forme) avant implémentation.
Suite complète verte : 514/514, `vue-tsc -b` propre.

Commit : (ce commit). Prochain : Task 2 (en-tête — titre dynamique, sur-titre mono, un seul
bouton primaire, reste replié dans un menu).
