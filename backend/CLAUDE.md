# backend/ — StudyHub API Flask

> Portée : tout `backend/`. Skill `backend-patterns` pour le détail complet (charge-la avant
> d'éditer `app/`). `AGENTS.md` fait autorité en cas de doute.

- Flux obligatoire : `Middleware → API (route) → Service → DAO → Model → PostgreSQL`.
- `db.session` **jamais** hors `app/dao/`. Une route ou un service qui y accède directement est
  une non-conformité à corriger, pas un précédent à suivre (constat de cartographie,
  `docs/audit/00-CARTOGRAPHIE.md` §2.6 — remise en conformité traitée en phase 2, pas ici).
- Pydantic v2 en entrée **et** en sortie de chaque route — jamais de `dict` brut renvoyé.
- Transactions : le DAO commit ; le service ne fait pas de commit manuel hors DAO.
- Migration Alembic obligatoire si un modèle change ; **relue avant d'être appliquée**, jamais
  générée puis appliquée à l'aveugle. Nommage et cycle : skill `deployment`.
- Tests : `backend/tests/`, isolation transactionnelle. Coverage cible ≥ 80 % (CI bloquante).
