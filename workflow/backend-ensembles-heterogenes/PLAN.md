# Plan — backend-ensembles-heterogenes

- [x] Écrire la spec détaillée (modèle de données cible, sort des `Deck`/`Flashcard` existants,
  contrat de `validate_item_payload`/`check_answer` par type) via `superpowers:brainstorming`
  puis `superpowers:writing-plans` —
  `docs/superpowers/specs/2026-08-28-backend-ensembles-heterogenes-design.md` +
  `docs/superpowers/plans/2026-08-28-backend-ensembles-heterogenes.md`
- [ ] Migration Alembic : déplacement du champ `type` de `RevisionSet` vers `RevisionItem`
- [x] Décision du sort des `Deck`/`Flashcard` existants : **explicitement différé**. Découverte en
  brainstormant : une vraie fusion toucherait 47 fichiers backend (tous les sous-systèmes
  majeurs) — bien plus large que ce chantier. Aucune ligne `Deck`/`Flashcard` n'est migrée ici ;
  chaque sous-système consommateur devient son propre chantier futur. Détail :
  `docs/superpowers/specs/2026-08-28-backend-ensembles-heterogenes-design.md`.
- [ ] Réécriture de `validate_item_payload` (dispatch par type d'item)
- [ ] Réécriture de `check_answer` (dispatch par type d'item)
- [ ] Suite de tests backend complète verte, coverage ≥ 80 %
- [ ] Mise à jour de `docs/api_reference.md` si des contrats d'endpoint changent (a priori non —
  seul un champ optionnel est ajouté, non-cassant, à confirmer en fin de plan)
