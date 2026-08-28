# Plan — backend-ensembles-heterogenes

- [x] Écrire la spec détaillée (modèle de données cible, sort des `Deck`/`Flashcard` existants,
  contrat de `validate_item_payload`/`check_answer` par type) via `superpowers:brainstorming`
  puis `superpowers:writing-plans` —
  `docs/superpowers/specs/2026-08-28-backend-ensembles-heterogenes-design.md` +
  `docs/superpowers/plans/2026-08-28-backend-ensembles-heterogenes.md`
- [x] Migration Alembic : déplacement du champ `type` de `RevisionSet` vers `RevisionItem`
  (`c1d2e3f4a5b6`, commit `1146955`). Vérifiée en pratique par l'auto-migration au démarrage du
  conteneur backend (log : `Running upgrade 4e6e094d2711 -> c1d2e3f4a5b6`) ; la vérification
  poussée « aucune dérive modèle/migration » (plan détaillé, Task 1 step 7,
  `flask db migrate -m "check"`) n'a pas pu être exécutée à froid sur un Postgres propre dans
  cette session — le volume Docker local (`backend-ensembles-heterogenes_pgdata`) est resté dans
  un état incohérent (stampé `4e6e094d2711` mais sans aucune table applicative, séquelle de
  l'instabilité Docker de la session précédente) et sa remise à zéro (`docker compose down -v`)
  est bloquée par le hook de garde. Signalé au contrôleur — à confirmer par un humain (ou une
  session avec l'autorisation explicite) avant la clôture définitive du chantier.
- [x] Décision du sort des `Deck`/`Flashcard` existants : **explicitement différé**. Découverte en
  brainstormant : une vraie fusion toucherait 47 fichiers backend (tous les sous-systèmes
  majeurs) — bien plus large que ce chantier. Aucune ligne `Deck`/`Flashcard` n'est migrée ici ;
  chaque sous-système consommateur devient son propre chantier futur. Détail :
  `docs/superpowers/specs/2026-08-28-backend-ensembles-heterogenes-design.md`.
- [x] Réécriture de `validate_item_payload` (dispatch par type d'item, cas `flashcard` ajouté,
  commit `44cdd10`) — et câblage réel dans `create_item`/`update_item`/`grade_item`/`answer_item`
  pour dispatcher sur `item.type` plutôt que `rset.type` (commit `9c29185`).
- [x] Réécriture de `check_answer` (dispatch par type d'item, cas `flashcard` ajouté,
  commit `44cdd10`) — câblage réel `grade_item` idem (commit `9c29185`).
- [x] Suite de tests backend complète verte, coverage ≥ 80 % — vérifié via le venv Python local de
  secours (SQLite en mémoire, `create_all()`) : 85 % de couverture globale, 18/18 tests
  `test_revision.py` verts. 5 échecs pré-existants et sans rapport (`test_import.py`,
  `PermissionError` sur `tempfile.mkstemp()`, spécifique à ce venv Windows local — absent en
  environnement Docker/CI Linux, non introduit par ce chantier).
- [ ] Mise à jour de `docs/api_reference.md` si des contrats d'endpoint changent (a priori non —
  seul un champ optionnel est ajouté, non-cassant, à confirmer en fin de plan)
