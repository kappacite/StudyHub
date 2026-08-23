---
name: conventions-dao
description: Gabarit de bout en bout (modèle, DAO, service, route, schémas, tests) pour créer une nouvelle entité backend conforme. À charger avant d'ajouter un modèle/DAO/service/route complet.
---

# conventions-dao

Ce skill ne redit pas les règles (déjà dans skill `backend-patterns` et `AGENTS.md` §4) —
il pointe vers un **exemple réel et complet** déjà dans le dépôt à copier comme gabarit :
le module `Tag`, la plus petite tranche verticale entièrement conforme.

## Le gabarit — module `Tag`

| Couche | Fichier | Ce qu'il illustre |
|---|---|---|
| Modèle | `backend/app/models/tag.py` | Entité SQLAlchemy simple, `user_id` FK |
| DAO | `backend/app/dao/tag_dao.py` | Hérite `BaseDAO[Tag]` ; méthodes de requête nommées (`get_by_user`, `get_by_name`, `count_by_user`) ; **aucune** logique métier — juste des requêtes |
| Service | `backend/app/services/tag_service.py` | Toute la logique (normalisation, validation, limites, unicité) ; DAO injecté au constructeur ; lève les exceptions de `error_handler` (`ValidationError`, `ConflictError`, `ForbiddenError`, `ResourceNotFoundError`) — jamais de `jsonify` d'erreur à la main ; pattern `_get_x_or_404(id, user_id)` pour l'isolation |
| Schémas | `backend/app/schemas/tag_schema.py` | `TagCreateSchema`/`TagUpdateSchema` (champs optionnels sur update) séparés de `TagResponseSchema` (`ConfigDict(from_attributes=True)`) |
| Route | `backend/app/api/v1/tags.py` | Blueprint, DAO+service instanciés au niveau module, `@jwt_required_middleware`, `user_id = int(get_jwt_identity())`, `Schema.model_validate(request.get_json() or {})`, aucune logique métier dans la fonction de route |
| Tests | `backend/tests/test_tags.py` | Couvre le service via le client de test Flask (`client`, `auth_headers` de `conftest.py`) |

## Ce qui rend ce module exemplaire (à reproduire)

- **Gestion d'erreur uniforme** : `IntegrityError` de la contrainte d'unicité DB rattrapée en
  service et retraduite en `ConflictError` métier (`tag_service.py:34-36`) — le client HTTP ne
  voit jamais une trace SQLAlchemy.
- **Isolation systématique** : chaque méthode qui touche une ressource par id vérifie
  `tag.user_id != user_id` avant d'agir (`_get_tag_or_404`), y compris pour les opérations
  transverses (`_get_owned_entity_or_404` sur les entités taguées).
- **Validation métier hors Pydantic quand elle dépend d'état** (limite de 50 tags par
  utilisateur, unicité du nom) : vit dans le service, pas dans le schéma — un schéma Pydantic
  ne peut pas interroger la base.

## Procédure pour une nouvelle entité

1. Modèle SQLAlchemy avec `user_id` (sauf ressource globale).
2. DAO héritant `BaseDAO[Entity]`, méthodes de requête nommées par intention.
3. Schémas Create/Update (champs optionnels)/Response séparés.
4. Service : DAO injecté, logique métier, `_get_x_or_404`, exceptions `error_handler`.
5. Route : blueprint, JWT, validation Pydantic, délégation au service, code HTTP correct.
6. Migration Alembic si un modèle a changé (skill `deployment`).
7. Tests (skill `cycle-tdd`).
