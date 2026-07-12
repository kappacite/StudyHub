---
name: backend-patterns
description: Patterns du backend Flask StudyHub (DAO/Service/API/Model, isolation user_id, Pydantic, erreurs, migrations). À charger avant de toucher à backend/app/.
---

# backend-patterns

Référence canonique : `docs/backend.md`. Ce skill = le strict nécessaire pour écrire du
code conforme. Architecture stricte :

```
Request → Middleware → API (route) → Service → DAO → Model → PostgreSQL
```

## Règles non négociables

- **DAO** (`app/dao/`) : hérite de `BaseDAO[T]`, ne connaît que modèles SQLAlchemy + `db.session`.
  N'importe **jamais** un service. Seul endroit où l'on écrit du SQLAlchemy.
- **Service** (`app/services/`) : porte toute la logique métier, manipule des schémas Pydantic.
  **Jamais** de SQL direct. Les DAO sont **injectés** dans le constructeur (pas d'import-instanciation).
- **Route** (`app/api/v1/`) : **aucune** logique métier. Valide le corps avec Pydantic
  (`Schema.model_validate(request.get_json() or {})`), délègue au service, renvoie
  `jsonify(...), <code>`. Décorée `@jwt_required_middleware`, `user_id = int(get_jwt_identity())`.
- **Middleware** : transversal (auth JWT, logging, error handler). Pas de logique applicative.

SOLID : un DAO = une entité ; un service = une logique métier ; schémas requête/réponse séparés.

## Isolation des données (absolu)

Tout DAO qui liste **filtre par `user_id`** (`BaseDAO.get_all` le fait déjà). Avant tout
update/delete : vérifier l'appartenance. Pattern type dans le service :

```python
def _get_x_or_404(self, x_id, user_id, write_required=False):
    x = self._x_dao.get_by_id(x_id)
    if not x:
        raise ResourceNotFoundError("X introuvable.")
    if x.user_id != user_id:
        # accès partagé éventuel via classeur
        check_binder_access(self._x_dao.db, x.binder_id, user_id, write_required=write_required)
    return x
```

Aucune ressource d'un utilisateur n'est accessible par un autre. Toutes les routes sont
JWT-protégées **sauf** `auth/*` et `health`.

## Erreurs (handler global)

Lève les exceptions de `app/middlewares/error_handler.py` — ne `jsonify` jamais une erreur
à la main :
`ValidationError` (400) · `UnauthorizedError` (401) · `ForbiddenError` (403) ·
`ResourceNotFoundError` (404) · `ConflictError` (409). Format de sortie unique :
`{ "error": { "code", "message", "details": {} } }`.

Codes HTTP : 200 lecture · 201 création · 204 sans contenu · 400/401/403/404/409 · 500.

## Schémas Pydantic v2

`DeckCreate` / `DeckUpdate` (champs optionnels) / `DeckResponse` séparés.
Réponses : `model_config = ConfigDict(from_attributes=True)` + `Schema.model_validate(model)`.
Les champs dérivés (ex. `card_count`) sont injectés par le service, pas par le DAO.

## Migrations & tests

- Modèle modifié ⇒ migration Alembic obligatoire (la CI bloque sinon). Voir skill `deployment`.
- Tests : SQLite en mémoire. `cd backend && source venv/bin/activate && python -m pytest`.
  Coverage cible ≥ 80 %.

## Interdits

❌ logique métier en route · ❌ SQL dans un service · ❌ DAO important un service ·
❌ `print()` de debug (un hook le signale) · ❌ secret en dur · ❌ route sans JWT (hors auth/health).
