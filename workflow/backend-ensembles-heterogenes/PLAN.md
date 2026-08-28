# Plan — backend-ensembles-heterogenes

- [ ] Écrire la spec détaillée (modèle de données cible, sort des `Deck`/`Flashcard` existants,
  contrat de `validate_item_payload`/`check_answer` par type) via `superpowers:brainstorming`
  puis `superpowers:writing-plans` — format
  `docs/superpowers/plans/YYYY-MM-DD-backend-ensembles-heterogenes.md`
- [ ] Migration Alembic : déplacement du champ `type` de `RevisionSet` vers `RevisionItem`
- [ ] Décision + implémentation du sort des `Deck`/`Flashcard` existants
- [ ] Réécriture de `validate_item_payload` (dispatch par type d'item)
- [ ] Réécriture de `check_answer` (dispatch par type d'item)
- [ ] Suite de tests backend complète verte, coverage ≥ 80 %
- [ ] Mise à jour de `docs/api_reference.md` si des contrats d'endpoint changent
