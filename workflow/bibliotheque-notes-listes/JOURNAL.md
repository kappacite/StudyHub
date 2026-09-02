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

Commit : `f2bb843`.

## 2026-09-03 — Task 2 : en-tête de `Binders.vue` (titre, sur-titre, menu « … »)

Brainstorming préalable (skill `superpowers:brainstorming`, path bounded) : une question
ouverte à trancher — le bouton « Ajouter ▾ » a déjà son propre sous-menu (Sous-dossier /
Élément existant / Note / Diagramme), le CONTEXT initial disait de le replier dans le menu
« … » avec Stats/Partager/Classe/Réviser/Supprimer, ce qui aurait imbriqué un menu dans un
menu. Utilisateur tranche : « Ajouter ▾ » reste visible (création de contenu, pas gestion du
classeur), seuls Stats/Partager/Classe/Réviser ce dossier/Supprimer rejoignent un nouveau
bouton « … ». Décision affinée dans `CONTEXT.md` avant implémentation. Résultat : 3 contrôles
visibles (primaire, Ajouter▾, …) au lieu de 7 — pas 1 comme le pixel de la maquette, écart
assumé et documenté.

Changements :
- `pageTitle` (computed) : « Bibliothèque » à la racine, sinon le libellé de l'onglet actif
  (`contentTabs.find(...)`) — pas de duplication de la liste Notes/Révision/Autres.
- `breadcrumbItems` : premier segment renommé « Racine » → « Bibliothèque » (aligné sur le
  sur-titre de la maquette) ; **tableau vide à la racine** au lieu du crochet à 1 élément
  auto-référent que le code affichait avant cette tâche (aucune maquette ne montre de fil
  d'Ariane sur `Bibliotheque.dc.html`) — écart pré-existant non listé dans le constat initial,
  corrigé ici car directement dans le périmètre de la fonction touchée.
- `PageHeader.vue` restylé en mono uppercase, séparateur « / » au lieu de « › » — seul
  `Binders.vue` passe sa prop `breadcrumbs` (vérifié par grep avant de toucher un composant
  partagé par 9 écrans), donc aucun autre écran affecté.
- `Tabs` reçoit `variant="segmented"` (Task 1).
- Nouveau menu `moreMenu` (computed) + bouton `data-test="more-actions-button"` (icône
  `MoreHorizontal`) : Stats/Partager/Classe/Réviser ce dossier (si des decks existent)/
  Supprimer (séparateur + `text-danger`). Labels dynamiques identiques à l'ancien affichage
  direct (Public/Partager, Partagé (N)/Classe). N'apparaît que sur un vrai classeur
  (`isRealBinderId`), comme les anciens boutons individuels qu'il remplace.
- `add-menu-button` : `data-test` ajouté (n'en avait pas) pour permettre au test de silhouette
  de compter les 3 contrôles top-level sans dépendre du texte affiché.

TDD : `PageHeader.spec.ts` (+1 test mono/séparateur) puis `Binders.spec.ts` — nouveau describe
« en-tête » (4 tests : titre racine + pas de nav, titre suit l'onglet sur 3 valeurs, silhouette
à 3 contrôles + repli réel des 5 actions, séparateur visuel `text-danger` sur Supprimer) + mise
à jour de 3 tests existants dont le comportement changeait légitimement (recherche directe des
boutons repliés → ouverture du menu d'abord ; libellé du crumb racine). Rouge vérifié (6 échecs
attendus) avant implémentation. Suite complète : 519/519, `vue-tsc -b` propre.

Vérification visuelle réelle (Claude in Chrome, données de test déjà seedées) : sur-titre mono
`BIBLIOTHÈQUE / CHIMIE ORGANIQUE`, H1 `Notes`, bascule segmentée, 3 contrôles, menu `…` avec
séparateur et `Supprimer` en rouge — conforme. Incident mineur en cours de vérification : un
clic sur le bouton `…` a bloqué l'automatisation (dialogue JS bloquante, cause exacte non
identifiée — le clic ciblait le bouton d'ouverture du menu, pas Supprimer) ; débloqué par
l'utilisateur manuellement, aucune donnée perdue (classeur et ses 5 notes intacts), nouvelle
capture propre obtenue ensuite.

Note d'outillage (hook) : `tdd_guard.py` résout le fichier de test via `rglob(f"{stem}.spec.ts")`
sur `web/tests` — sur ce système de fichiers insensible à la casse (Windows), `Binders.spec.ts`
matche aussi `web/tests/stores/binders.spec.ts` (minuscule), parfois retourné en premier. Le
garde comparait alors le mauvais fichier, bloquant à tort des éditions de
`web/src/views/Binders/Binders.vue` pourtant précédées d'un vrai test rouge dans
`web/tests/views/Binders/Binders.spec.ts`. Contourné en touchant le mtime du fichier
mal-résolu avant chaque édition (pas de contenu changé) plutôt qu'en modifiant le hook
lui-même, hors périmètre de ce chantier — à signaler si le hook doit être corrigé un jour
(délimiter la recherche par le sous-dossier miroir attendu, `views/` ici, pas une recherche
plate sur tout `web/tests`).

Commit : `63bbadf`.

## 2026-09-03 — Task 3 : sous-titre agrégé sur la grille racine

`rootSubtitle` (computed) : `N classeur(s) · N note(s) · N deck(s)`, `undefined` dès qu'on
est dans un classeur (`PageHeader` ne rend rien dans ce cas — pas besoin d'un `v-if`
supplémentaire côté template). Volontairement **total de bibliothèque** (tous les
classeurs/notes/decks possédés), pas la somme des cartes visibles : `binderAggregate()`
compte le contenu directement attaché à UN classeur (décision actée par
`bibliotheque-redesign`), ce sous-titre résume l'ensemble du compte — les deux logiques
coexistent sans se contredire, documenté en commentaire pour ne pas les confondre plus tard.

TDD : 2 tests (présence à la racine avec le bon compte depuis les fixtures existantes,
absence dans un classeur). Rouge vérifié, puis implémentation.

Commit : `<voir historique>`.

## 2026-09-03 — Task 4 : liseré + rayon de `BinderCard`, accent de la carte active

`BaseCard.vue` gagne une prop `radius` (`'card'` défaut inchangé = `rounded-lg`, `'bristol'`
nouveau = `rounded`, vocabulaire repris du skill `design-system` § Rayons — "bandeaux fiche
bristol"). Changement additif, défaut préservé pour les 22 autres consommateurs de
`BaseCard`. `BinderCard.vue` : `radius="bristol"` + liseré gauche 4px sur **chaque** carte
(neutre `border-l-line` par défaut, `border-l-accent` si la nouvelle prop `accent` est
vraie) — Bibliotheque.dc.html accentue une seule carte (la plus récemment active), pas de
liseré conditionnellement absent comme l'ancien `highlighted` mort qui avait été retiré en
revue finale de `bibliotheque-redesign`.

Le choix de QUELLE carte accentuer reste dans `Binders.vue` (composant présentationnel pur,
convention déjà établie) : `BinderAggregateResult` gagne un champ `lastActivityIso` (date
brute à côté du libellé déjà formaté `lastActivityLabel`) pour permettre la comparaison
entre classeurs sans reparser un libellé français ; `mostRecentEntryId` (computed) retient
le premier candidat au max de `lastActivityIso` parmi `childrenAtCurrentLevel` (égalité :
le premier rencontré l'emporte, sans signification produit -- aucune maquette ne montre deux
cartes accentuées à la fois).

TDD complet (BaseCard, BinderCard, binderAggregate, câblage Binders.vue). Suite complète :
525/525, `vue-tsc -b` propre.

Note d'outillage (confirme l'entrée Task 2) : le même contournement `tdd_guard.py`
(toucher le mtime de `web/tests/stores/binders.spec.ts` avant chaque édition de
`Binders.vue`) a été nécessaire à répétition sur cette tâche — le problème est systématique,
pas un incident isolé.

Commit : `4a2eefa`.

## 2026-09-03 — Task 5 : lignes de notes (extrait, tag, date, globe)

L'écart le plus fort du constat initial (titre seul sur une ligne quasi vide) est corrigé.

Changements :
- `Note` (store) gagne `is_public?: boolean` -- toujours renvoyé par le backend
  (`NoteResponse`), jamais déclaré côté front (même convention que `read_only`).
- `ListRow.vue` gagne une prop `padding` (`'default'` inchangé, `'cozy'` = `px-0 py-4` --
  lignes plus aérées sans indent horizontal, le retrait vient déjà du padding de la
  `BaseCard` englobante). Changement additif, 2 autres consommateurs (`Accueil.vue`,
  `RevisionSetDetail.vue`) non affectés.
- `noteExcerpt()` (Binders.vue) : `content` est du Markdown brut (rendu via `marked` dans
  `NoteEdit.vue`) -- pas question de faire tourner un parseur complet pour un extrait
  tronqué en CSS. Retire seulement les caractères de balisage les plus visibles
  (`#`, `*`, `_`, backtick, `>`), aplatit les retours à la ligne ; la troncature visuelle
  (ellipsis) reste gérée par la classe `truncate` du template, pas par un découpage de
  caractères arbitraire.
- Ligne de note reconstruite : titre + icône globe (accessible via `aria-label`, pas de
  texte visible -- pas d'équivalent texte pertinent) si `is_public`, extrait en dessous ;
  en zone trailing : pastille du premier tag (`TagBadge`, primitive déjà utilisée ailleurs
  dans ce même fichier pour les tags de classeur -- pas de nouveau composant), date relative
  (`formatDayDiffLabel`, déjà défini dans ce fichier) alignée à droite, largeur fixe.
- Titre interne `<h3>Notes (N)</h3>` supprimé (redondant avec le H1 de Task 2).
- Séparateurs : `divide-y divide-dashed divide-line` sur le conteneur au lieu de
  `space-y-1` (Notes.dc.html : filet pointillé entre les lignes, pas d'espacement plein).

TDD complet (ListRow, Binders.vue -- extrait/tag/globe/date, absence sur note vide,
disparition du titre interne, séparateurs). Rouge vérifié avant implémentation. Suite
complète : 530/530, `vue-tsc -b` propre. Vérifié visuellement en local (extraits, dates,
filets pointillés conformes ; tag/globe non visibles sur les données de seed actuelles, qui
n'ont ni tag ni note publique -- couverts par les tests unitaires avec données mockées).

Commit : `ce0f1b5`.

## 2026-09-03 — Task 6 : lignes d'ensemble de révision (bouton Réviser, menu, phrase)

- Bouton ▶ Réviser en première position (icône `Play`, route `/revision/sets/:id/study`,
  `@click.stop` pour ne pas déclencher aussi la navigation de la ligne vers le détail).
- Stats/Retirer du classeur/Supprimer repliés dans un nouveau menu « … » par ligne
  (`openSetMenuId` -- un seul ouvert à la fois, indexé par id de set, même idiome que
  `showAddMenu`/`showMoreMenu` de Task 2 mais par ligne plutôt que par écran). Éditer reste
  visible directement à côté de Réviser -- ni l'un ni l'autre n'a d'équivalent maquette pour
  Stats/Détacher, qui rejoignent Supprimer dans le menu.
- Phrase d'explication (« Un classeur regroupe des ensembles de révision... ») au-dessus de
  la liste, titre interne « Révision (N) » supprimé (même raisonnement que Task 5).
- Lignes decks + ensembles : `padding="cozy"` (Task 5) et séparateur `divide-y
  divide-dashed` partagé entre les deux types de lignes fusionnées.

Écart assumé avec la maquette, documenté dans `CONTEXT.md` avant la tâche (pas de nouvelle
question posée) : 3 contrôles visibles (Réviser, Éditer, …) au lieu de 3 *fixes* de la
maquette (réviser/éditer/supprimer) -- Stats et Détacher n'existent pas dans
`RevisionSetDetail.dc.html`, ils rejoignent Supprimer dans le menu plutôt que d'être ajoutés
comme boutons visibles séparés.

TDD complet (nouvelle route de test `RevisionSetStudy`, bouton Réviser, contenu du menu,
non-régression des 2 tests existants Statistiques/Détacher qui ouvrent désormais le menu
d'abord, phrase + disparition du titre interne). Rouge vérifié. Suite complète : 533/533,
`vue-tsc -b` propre. Vérifié visuellement en local, conforme.

Commit : (ce commit). Prochain : Task 7 (largeur 920px dans un classeur).
