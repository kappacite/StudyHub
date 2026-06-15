# Révision active des notes (balisage)

> Guide utilisateur du mode **Révision Active** de l'éditeur de notes (A9 du plan de refonte).

## Principe

Vous pouvez incorporer des **questions interactives** directement dans le Markdown de vos
notes, à l'aide de balises. En basculant l'éditeur en mode **« Révision Active »**, ces
balises deviennent des mini-exercices que vous révisez **en place** (révéler / répondre).

Important :
- Le balisage est un **auto-test inline** : il **ne crée aucune entité de révision**
  persistante (ni flashcard, ni ensemble). Rien n'est enregistré dans vos jeux/ensembles.
- Les balises **alimentent aussi les évaluations IA** générées depuis la note
  (module d'évaluation), toujours sans persistance automatique.
- Pour des entités de révision durables et suivies (SM-2, stats), créez des
  **flashcards** (decks) ou des **ensembles de révision** (QCM, V/F, etc.) — voir le
  module Révisions. Le balisage des notes en est volontairement distinct.

## Les deux modes de l'éditeur

- **Lecture** : la note s'affiche normalement (le balisage est rendu lisible).
- **Révision Active** : chaque balise devient un exercice interactif (champ à révéler,
  boutons de réponse, appariement, réordonnancement…).

Le sélecteur Lecture / Révision Active se trouve dans la barre de l'éditeur. La barre
d'outils propose aussi des boutons pour **insérer** chaque type de balise sur la
sélection courante (la syntaxe générée est toujours celle ci-dessous).

## Syntaxe des balises

| Type | Syntaxe | Exemple |
|---|---|---|
| **Texte à trous** (Cloze) | `{{trou::mot caché}}` | `La capitale de la France est {{trou::Paris}}.` |
| **QCM** | `{{qcm::Question ?::Opt1\|*Bonne*\|Opt3}}` (bonne réponse entre `*`) | `{{qcm::Combien de continents ?::4\|5\|*6*\|7}}` |
| **Ordre / séquence** | `{{ordre::Titre::Étape 1 > Étape 2 > Étape 3}}` (séparateur `>`) | `{{ordre::Cycle de l'eau::Évaporation > Condensation > Précipitations}}` |
| **Association** | `{{assoc::Titre::Clé 1=Valeur 1 \| Clé 2=Valeur 2}}` (paires `clé=valeur` séparées par `\|`) | `{{assoc::Capitales::France=Paris \| Italie=Rome}}` |
| **Vrai / Faux** | `{{vf::Affirmation::Vrai/Faux::Justification}}` (séparateur `::`) | `{{vf::La Terre est plate::Faux::Elle a la forme d'un géoïde.}}` |
| **Définition** | `[terme]{def:définition}` | `[La PVM]{def:Python Virtual Machine, exécute le bytecode.}` |

### Points d'attention sur les séparateurs

Chaque type a son séparateur propre — c'est la source d'erreur la plus fréquente :
- **Ordre** : les étapes sont séparées par `>` (et non `|`).
- **Association** : chaque paire s'écrit `clé=valeur`, les paires sont séparées par `|`.
- **Vrai/Faux** : les trois champs (affirmation, réponse, justification) sont séparés
  par `::` (et non `|`).
- **QCM** : les options sont séparées par `|`, la bonne option est entourée d'astérisques `*`.

L'aide intégrée à l'éditeur (icône d'aide) reprend exactement cette syntaxe.

## Cohérence (note technique)

La syntaxe ci-dessus est la **référence unique**, partagée par :
- le rendu interactif du mode Révision Active (`web/src/views/Notes/NoteEdit.vue`),
- les boutons d'insertion de la barre d'outils,
- le parseur backend qui alimente les évaluations IA
  (`backend/app/utils/placeholder_parser.py`, couvert par `tests/test_placeholders.py`).

Toute évolution de la syntaxe doit être répercutée à ces trois endroits **et** dans ce document.
