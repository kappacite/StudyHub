# Journal — backend-ensembles-heterogenes

## 2026-08-28

Chantier ouvert : migration du flux 1 (`ETAT.md` § « Plan global par flux », 2026-08-27) vers
le système de suivi par chantiers. Aucun travail d'implémentation fait — seule la décision de
garder le canevas hétérogène est actée (2026-08-27, consignée dans `ETAT.md`). Commit : à
suivre.

## 2026-08-28 (activation)

Chantier activé (`Statut : planifié → ouvert`, branche `feature/backend-ensembles-heterogenes`
créée depuis `main` à jour). Premier chantier de l'ordre fixé (flux 1). Aucun travail
d'implémentation encore fait. Prochain point du plan : écrire la spec détaillée du modèle de
données cible.

## 2026-08-28 (spec + plan)

Brainstorming fait avant d'écrire le spec — découverte majeure en lisant le code réel :
- `Flashcard.card_type`/`payload` (qui semblaient dupliquer qcm/vf/ordre avec `RevisionSet.type`)
  sont du code mort : jamais lus/écrits ailleurs, absents des schémas Pydantic exposés,
  confirmé par le commentaire de `flashcard_schema.py` (décision D3c : flashcard = strictement
  recto/verso). Pas de vraie duplication à résoudre.
- Une vraie fusion `Deck`/`Flashcard` → `RevisionSet`/`RevisionItem` toucherait 47 fichiers
  backend (tous les sous-systèmes majeurs) — décision utilisateur : reporter cette fusion à des
  chantiers futurs distincts, un par sous-système. Ce chantier-ci se limite au socle schéma.
- `RevisionSet.type` est activement utilisé par le frontend non-migré (`Reviews.vue` et 4 autres
  vues) — conservé pour rétrocompatibilité totale, devient seulement optionnel.
- Bug trouvé en écrivant le plan détaillé (pas en implémentant) : `grade_item` doit vérifier
  `GRADABLE_TYPES` contre `item.type`, pas `rset.type` — sinon un item `flashcard` créé dans un
  ensemble `vf` (possible dès ce chantier via `RevisionItemCreate.type` explicite) serait noté
  silencieusement avec la mauvaise logique. Corrigé dans le spec et le plan avant exécution.

Spec : `docs/superpowers/specs/2026-08-28-backend-ensembles-heterogenes-design.md`.
Plan (4 tâches TDD) : `docs/superpowers/plans/2026-08-28-backend-ensembles-heterogenes.md`.
Commit : à suivre.
