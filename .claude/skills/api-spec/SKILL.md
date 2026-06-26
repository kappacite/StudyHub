---
name: api-spec
description: Contrat des endpoints REST StudyHub (préfixe /api/v1, conventions kebab-case, pagination, codes HTTP, format d'erreur). À charger avant de créer/modifier une route ou un contrat d'endpoint.
---

# api-spec

Référence canonique exhaustive : `docs/api_reference.md` (liste complète des routes et payloads).
Ce skill = les règles de contrat à respecter pour toute nouvelle route.

## Conventions de route

- Préfixe **`/api/v1/`**. Chemins en **kebab-case** (`/study-sessions`, `/decks/<id>/study`).
- Toutes les routes sont **JWT-protégées** (`@jwt_required_middleware`) **sauf** `auth/*` et `health`.
- Verbes : `GET` lecture · `POST` création · `PUT` remplacement · `PATCH` modification partielle
  (ex. toggle `visibility`) · `DELETE` suppression.

## Codes HTTP

200 lecture · 201 création · 204 sans contenu · 400 validation · 401 non auth · 403 interdit ·
404 introuvable · 409 conflit · 500 serveur.

## Format de réponse

- **Listes paginées** :
  ```json
  { "data": [ ... ], "pagination": { "page", "per_page", "total", "pages" } }
  ```
  Query params : `?page=1&per_page=20`, plus filtres (`?binder_id=`, `?search=`, `?tag_id=`).
- **Ressource unique** : l'objet sérialisé (`Schema.model_dump()`), code adapté.
- **Erreur** (handler global, format unique) :
  ```json
  { "error": { "code": "RESOURCE_NOT_FOUND", "message": "...", "details": {} } }
  ```

## Forme canonique d'une route

```python
@bp.route("", methods=["POST"])
@jwt_required_middleware
def create_x():
    user_id = int(get_jwt_identity())
    data = XCreate.model_validate(request.get_json() or {})   # validation Pydantic
    result = x_service.create_x(user_id, data)                # délégation
    return jsonify(result.model_dump()), 201                  # jsonify + code
```

Aucune logique métier dans la route : valider, déléguer au service, renvoyer. La logique
d'autorisation/appartenance vit dans le service (voir skill `backend-patterns`).

## Modules existants (résumé)

`auth` · `users/me` · `binders` (arborescence, `?parent_id`, `/visibility`, `/public/<id>`) ·
`decks` (+`/study`, `/study/answer/<card_id>` SM-2) · `decks/<id>/cards` · `notes`
(+`/visibility`, `/public/<token>`) · `packages` (marketplace, `/clone`) · `blurting` ·
`evaluations` (génération IA async + `/tasks/<task_id>`) · `diagrams` · `pdfs` (+`/file`) ·
`stats` (`/overview`, `/sessions`, `/heatmap`, `/decks/<id>`). Détails et payloads : `docs/api_reference.md`.

Toute nouvelle route doit être ajoutée à `docs/api_reference.md` dans la même PR.
