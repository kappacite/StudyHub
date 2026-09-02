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
