# Backend — type au niveau de l'item de révision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Déplacer le concept de `type` de `RevisionSet` (homogène) vers
`RevisionItem` (par item), ajouter le type `"flashcard"`, sans casser le
frontend actuel ni toucher `Deck`/`Flashcard`.

**Architecture:** Migration Alembic additive (nouvelle colonne
`revision_items.type`, backfill depuis le `type` de l'ensemble parent,
`revision_sets.type` devient nullable) ; `validate_item_payload`/
`check_answer` dispatchent désormais sur le type de l'item ; `create_item`
retombe sur le type de l'ensemble si aucun type explicite n'est fourni
(rétrocompatibilité totale avec le frontend actuel, qui n'envoie jamais de
`type` à la création d'un item).

**Tech Stack:** Flask 3, SQLAlchemy 2, Alembic, Pydantic v2, pytest
(`backend/tests/`, fixtures `client`/`auth_headers`/`app` de `conftest.py`,
DB SQLite en mémoire via `db.create_all()` — la logique de backfill de la
migration n'est donc pas exercée par pytest, seule sa forme SQL est revue
à la main, cf. Global Constraints).

**Spec:** `docs/superpowers/specs/2026-08-28-backend-ensembles-heterogenes-design.md`

## Global Constraints

- **Rétrocompatibilité stricte** : tout appel actuel du frontend non migré
  (`Reviews.vue`, `RevisionSetManage.vue`, `RevisionSetStats.vue`,
  `RevisionStudy.vue`, `RevisionBinderStats.vue`) doit continuer à
  fonctionner à l'identique — aucun de ces fichiers n'est modifié par ce
  plan.
- **Aucune ligne `Deck`/`Flashcard` touchée.** Aucun des 8 sous-systèmes
  consommateurs (`class_service`, `community_service`, `deck_service`,
  `evaluation_service`, `exam_service`, `flashcard_service`,
  `focus_service`, `import_service`, `planning_service`, `quiz_service`,
  `stats_service`) n'est modifié.
- **`GRADABLE_TYPES` est vérifié contre `item.type`** dans `grade_item`
  (pas `rset.type`) — nécessaire dès ce chantier car
  `RevisionItemCreate.type` explicite permet de créer un item divergent
  du type de son ensemble (ex. `"flashcard"` dans un set `"vf"`) ; garder
  le gate sur `rset.type` noterait silencieusement un tel item avec la
  mauvaise logique de correction. `answer_item` utilise de même
  `item.type` pour `StudySession.item_type` (coût nul sur les données
  réelles actuelles, correct par construction).
- **`run_qcm` reste inchangé** (gate sur `rset.type == "qcm"` au niveau de
  l'ensemble, sans filtrage par item) — risque analogue accepté
  explicitement (cf. spec, « Risque accepté ») plutôt que de redessiner
  le passage scoré dans ce chantier.
- TDD strict (phase 4 du projet, ≥ 3) : le test précède le code à chaque
  étape, sans exception.
- Migration Alembic idempotente (guard `inspector`), compatible SQLite et
  PostgreSQL (`batch_alter_table`), suivant le style de
  `backend/migrations/versions/a1b2c3d4e5f6_revision_sets_foundation.py`.
  Tête de migration actuelle : `4e6e094d2711`.
- Coverage backend ≥ 80 % (garde CI bloquante) maintenu.
- Après ce plan : `workflow/backend-ensembles-heterogenes/PLAN.md` a
  toutes ses cases cochées sauf la mise à jour de
  `docs/api_reference.md` (à faire seulement si un contrat d'endpoint
  change — ce n'est pas le cas ici, seul un champ optionnel est ajouté).

---

### Task 1: Migration Alembic + modèles SQLAlchemy

**Files:**
- Create: `backend/migrations/versions/c1d2e3f4a5b6_revision_item_type.py`
- Modify: `backend/app/models/revision.py`
- Test: `backend/tests/test_revision.py` (ajout, pas de nouveau fichier)

**Interfaces:**
- Produces : `RevisionItem.type` (colonne `String(20)`, nullable au niveau
  DB) ; `RevisionSet.type` reste `String(20)` mais `nullable=True` désormais
  (était `nullable=False`). Consommé par la Task 2.

- [ ] **Step 1: Écrire le test qui doit passer après la migration/modèle (modèle, pas API)**

Dans `backend/tests/test_revision.py`, ajouter en fin de fichier (test au
niveau du modèle uniquement — ne dépend d'aucun câblage de service, donc
entièrement vérifiable dans cette tâche, sans attendre la Task 3) :

```python
def test_revision_item_type_column_persists(app, test_user):
    """Le modele RevisionItem porte desormais son propre type (D8)."""
    with app.app_context():
        from app.extensions import db
        from app.models.revision import RevisionSet, RevisionItem
        rset = RevisionSet(name="QCM", type="qcm", user_id=test_user["id"])
        db.session.add(rset)
        db.session.commit()
        item = RevisionItem(set_id=rset.id, type="qcm", payload={"question": "2+2 ?", "options": []})
        db.session.add(item)
        db.session.commit()
        db.session.refresh(item)
        assert item.type == "qcm"


def test_revision_set_type_is_nullable_at_model_level(app):
    """RevisionSet.type devient optionnel (ensembles heterogenes futurs)."""
    with app.app_context():
        from app.models.revision import RevisionSet
        col = RevisionSet.__table__.columns["type"]
        assert col.nullable is True
```

- [ ] **Step 2: Lancer les tests, confirmer l'échec pour la bonne raison**

Run: `docker compose exec -T backend pytest tests/test_revision.py -k "item_type_column_persists or type_is_nullable" -v`
Expected: `test_revision_item_type_column_persists` échoue avec
`TypeError: 'type' is an invalid keyword argument for RevisionItem`
(colonne absente du modèle) ; `test_revision_set_type_is_nullable_at_model_level`
échoue avec `assert False is True` (colonne encore `nullable=False`).

- [ ] **Step 3: Modifier le modèle SQLAlchemy**

Dans `backend/app/models/revision.py` :

```python
class RevisionSet(db.Model):
    ...
    __tablename__ = "revision_sets"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    # Type homogene de l'ensemble (cf. REVISION_SET_TYPES). Devenu optionnel
    # (D8) : NULL = ensemble heterogene (le type vit desormais au niveau de
    # RevisionItem). Tous les ensembles reels actuels restent homogenes et
    # renseignes -- ce champ n'est pas encore mis a NULL par un code reel.
    type = Column(String(20), nullable=True)
```

(Seule la ligne `type = Column(...)` change : `nullable=False` devient
`nullable=True`, avec le commentaire mis à jour en conséquence.)

```python
class RevisionItem(db.Model):
    ...
    id = Column(Integer, primary_key=True)
    set_id = Column(Integer, ForeignKey("revision_sets.id", ondelete="CASCADE"), nullable=False)
    # Type de l'item (D8) : qcm/vf/association/definition/ordre/flashcard.
    # Deplace depuis RevisionSet.type -- permet des ensembles heterogenes.
    # Nullable au niveau DB par prudence (retro-compatibilite du schema) ;
    # toujours renseigne en pratique par le service (backfill migration +
    # RevisionService.create_item).
    type = Column(String(20), nullable=True)
    payload = Column(JSON, nullable=False)
```

(Insérer la nouvelle colonne `type` juste après `set_id`, avant `payload`.)

- [ ] **Step 4: Lancer les tests, confirmer qu'ils passent**

Run: `docker compose exec -T backend pytest tests/test_revision.py -k "item_type_column_persists or type_is_nullable" -v`
Expected: 2/2 passent.

- [ ] **Step 5: Écrire la migration Alembic**

```python
"""revision item type (D8) : deplace type de revision_sets vers revision_items

Revision ID: c1d2e3f4a5b6
Revises: 4e6e094d2711
Create Date: 2026-08-28 12:00:00.000000

Ajoute revision_items.type (backfille depuis revision_sets.type pour les
lignes existantes -- tous les ensembles actuels sont homogenes) et rend
revision_sets.type nullable (ensembles heterogenes futurs, type porte par
l'item). Additif et idempotent (guard inspector), compatible SQLite et
PostgreSQL.
"""
from alembic import op
import sqlalchemy as sa


revision = 'c1d2e3f4a5b6'
down_revision = '4e6e094d2711'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    cols = {c["name"] for c in inspector.get_columns("revision_items")}
    if "type" not in cols:
        with op.batch_alter_table("revision_items", schema=None) as batch_op:
            batch_op.add_column(sa.Column("type", sa.String(length=20), nullable=True))

        op.execute(
            "UPDATE revision_items SET type = ("
            "SELECT revision_sets.type FROM revision_sets "
            "WHERE revision_sets.id = revision_items.set_id"
            ") WHERE type IS NULL"
        )

    with op.batch_alter_table("revision_sets", schema=None) as batch_op:
        batch_op.alter_column("type", existing_type=sa.String(length=20), nullable=True)


def downgrade():
    with op.batch_alter_table("revision_sets", schema=None) as batch_op:
        batch_op.alter_column("type", existing_type=sa.String(length=20), nullable=False)

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("revision_items")}
    if "type" in cols:
        with op.batch_alter_table("revision_items", schema=None) as batch_op:
            batch_op.drop_column("type")
```

- [ ] **Step 6: Vérifier la migration à la main (pytest ne l'exerce pas — `create_all()`, cf. Tech Stack)**

Run (conteneur backend démarré, `docker compose up -d db backend`) :
`docker compose exec -T backend flask db upgrade` puis
`docker compose exec -T backend flask db current`
Expected: la sortie de `flask db current` affiche `c1d2e3f4a5b6 (head)`,
sans erreur. Si des ensembles existent déjà en base de dev, vérifier
manuellement qu'au moins un item a bien `type` renseigné après upgrade
(`docker compose exec -T backend flask shell` puis
`RevisionItem.query.first().type`).

- [ ] **Step 7: Vérifier l'absence de dérive modèle/migration (garde CI "migrations")**

Run: `docker compose exec -T backend flask db migrate -m "check"` (sur la
base déjà à jour de l'étape 6)
Expected: Alembic répond qu'aucun changement n'est détecté (pas de nouveau
fichier de migration généré) — confirme que le modèle et la migration
correspondent exactement.

- [ ] **Step 8: Commit**

```bash
git add backend/app/models/revision.py backend/migrations/versions/c1d2e3f4a5b6_revision_item_type.py backend/tests/test_revision.py
git commit -m "feat(revision): deplace le type au niveau de l'item (migration + modeles)"
```

---

### Task 2: `validate_item_payload`/`check_answer` — dispatch par type d'item + cas flashcard

**Files:**
- Modify: `backend/app/services/revision_service.py`
- Modify: `backend/app/schemas/revision_schema.py`
- Test: `backend/tests/test_revision.py`

**Interfaces:**
- Consumes : `RevisionItem.type` (Task 1).
- Produces : `validate_item_payload(item_type: str, payload: dict) -> dict`
  et `check_answer(item_type: str, payload: dict, answer: dict) -> bool`
  acceptent désormais un type d'item incluant `"flashcard"`. Consommé par
  la Task 3.

- [ ] **Step 1: Écrire les tests des fonctions pures (rouge)**

Ajouter en tête de `backend/tests/test_revision.py` (le fichier n'importe
encore ni `pytest` ni ces deux symboles) :

```python
import pytest
from app.services.revision_service import validate_item_payload, check_answer
from app.middlewares.error_handler import ValidationError
```

Puis, en fin de fichier :

```python
def test_validate_flashcard_payload_accepts_front_back():
    payload = validate_item_payload("flashcard", {"front": "Chat", "back": "Cat"})
    assert payload == {"front": "Chat", "back": "Cat"}


def test_validate_flashcard_payload_rejects_missing_front():
    with pytest.raises(ValidationError):
        validate_item_payload("flashcard", {"back": "Cat"})


def test_validate_flashcard_payload_rejects_missing_back():
    with pytest.raises(ValidationError):
        validate_item_payload("flashcard", {"front": "Chat"})


def test_check_answer_flashcard_never_auto_corrects():
    # Comme "definition" : toujours False, jamais auto-corrige.
    assert check_answer("flashcard", {"front": "Chat", "back": "Cat"}, {}) is False
```

- [ ] **Step 2: Lancer les tests, confirmer l'échec pour la bonne raison**

Run: `docker compose exec -T backend pytest tests/test_revision.py -k "flashcard_payload or check_answer_flashcard" -v`
Expected: les 3 premiers tests échouent avec `ValidationError: Type d'ensemble de révision inconnu : flashcard.` (ou l'absence de levée pour le test "rejects" — `Failed: DID NOT RAISE`) ; le 4e passe déjà par accident (le `return False` par défaut couvre aussi le type inconnu) — le mentionner ne bloque pas, mais le confirmer explicitement à cette étape.

- [ ] **Step 3: Implémenter le cas `flashcard` dans `validate_item_payload`/`check_answer`**

Dans `backend/app/services/revision_service.py`, renommer le premier
paramètre `set_type` → `item_type` dans les deux fonctions (clarté :
c'est désormais le type de l'item, pas de l'ensemble) et ajouter le
nouveau cas :

```python
def validate_item_payload(item_type: str, payload: dict) -> dict:
    """Valide (et normalise légèrement) le payload d'un item selon son
    propre type. Lève ValidationError (400) si le contenu est incohérent."""
    if not isinstance(payload, dict):
        raise ValidationError("Le contenu de l'item est invalide.")

    if item_type == "qcm":
        question = (payload.get("question") or "").strip()
        options = payload.get("options")
        if not question:
            raise ValidationError("La question du QCM est obligatoire.")
        if not isinstance(options, list) or len(options) < 2:
            raise ValidationError("Un QCM doit comporter au moins deux options.")
        correct = [o for o in options if isinstance(o, dict) and o.get("correct")]
        if len(correct) < 1:
            raise ValidationError("Un QCM doit comporter au moins une bonne réponse.")
        points = payload.get("points", 1)
        if not isinstance(points, int) or points < 1:
            raise ValidationError("Le barème (points) doit être un entier positif.")

    elif item_type == "vf":
        if not (payload.get("assertion") or "").strip():
            raise ValidationError("L'affirmation est obligatoire.")
        if not isinstance(payload.get("correct"), bool):
            raise ValidationError("Le verdict (vrai/faux) est obligatoire.")

    elif item_type == "association":
        pairs = payload.get("pairs")
        if not isinstance(pairs, list) or len(pairs) < 2:
            raise ValidationError("Une association doit comporter au moins deux paires.")
        for p in pairs:
            if not isinstance(p, dict) or not (p.get("left") or "").strip() or not (p.get("right") or "").strip():
                raise ValidationError("Chaque paire doit avoir un terme et sa correspondance.")

    elif item_type == "definition":
        if not (payload.get("term") or "").strip():
            raise ValidationError("Le terme est obligatoire.")
        if not (payload.get("definition") or "").strip():
            raise ValidationError("La définition est obligatoire.")

    elif item_type == "ordre":
        steps = payload.get("steps")
        if not isinstance(steps, list) or len([s for s in steps if (s or "").strip()]) < 2:
            raise ValidationError("Un exercice d'ordre doit comporter au moins deux étapes.")

    elif item_type == "flashcard":
        if not (payload.get("front") or "").strip():
            raise ValidationError("Le recto de la flashcard est obligatoire.")
        if not (payload.get("back") or "").strip():
            raise ValidationError("Le verso de la flashcard est obligatoire.")

    else:
        raise ValidationError(f"Type d'item de révision inconnu : {item_type}.")

    return payload


def check_answer(item_type: str, payload: dict, answer: dict) -> bool:
    """Correction d'une réponse à l'étude pour les types auto-corrigeables.
    "flashcard" (comme "definition") n'est jamais auto-corrige -- retombe
    sur le defaut False ci-dessous (auto-evaluation cote client)."""
    if item_type == "vf":
        return isinstance(answer.get("value"), bool) and answer["value"] is bool(payload.get("correct"))

    if item_type == "association":
        expected = {p["left"]: p["right"] for p in payload.get("pairs", [])}
        submitted = answer.get("matches")
        return isinstance(submitted, dict) and submitted == expected

    if item_type == "ordre":
        expected = [s for s in payload.get("steps", []) if str(s).strip()]
        return answer.get("order") == expected

    return False
```

- [ ] **Step 4: Lancer les tests, confirmer qu'ils passent**

Run: `docker compose exec -T backend pytest tests/test_revision.py -k "flashcard_payload or check_answer_flashcard" -v`
Expected: 4/4 passent.

- [ ] **Step 5: Ajouter le type `RevisionItemType` et l'exposer dans les schémas**

Dans `backend/app/schemas/revision_schema.py`, après `RevisionType` :

```python
# Types d'ensembles génériques (cf. app.models.revision.REVISION_SET_TYPES).
RevisionType = Literal["qcm", "vf", "association", "definition", "ordre"]
# Types d'items (D8) : les 5 types d'ensemble + flashcard (item-only, ne
# peut pas etre le type homogene d'un RevisionSet, cf. RevisionType).
RevisionItemType = Literal["qcm", "vf", "association", "definition", "ordre", "flashcard"]
```

Modifier `RevisionSetResponse` (un seul champ change) :

```python
class RevisionSetResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    # Optionnel (D8) : None = ensemble heterogene (type porte par les items).
    # Aucun code actuel ne produit encore None -- tous les ensembles reels
    # restent homogenes et renseignes.
    type: Optional[str] = None
    ...
```

Modifier `RevisionItemCreate`, `RevisionItemUpdate`, `RevisionItemResponse` :

```python
class RevisionItemCreate(BaseModel):
    # Optionnel : si absent, retombe sur le type de l'ensemble parent
    # (retro-compatibilite totale avec le frontend actuel, qui n'envoie
    # jamais ce champ).
    type: Optional[RevisionItemType] = None
    payload: Dict[str, Any]
    tuning: float = Field(1.0, gt=0)
    position: int = 0


class RevisionItemUpdate(BaseModel):
    payload: Optional[Dict[str, Any]] = None
    tuning: Optional[float] = Field(None, gt=0)
    position: Optional[int] = None


class RevisionItemResponse(BaseModel):
    id: int
    set_id: int
    type: str
    payload: Dict[str, Any]
    tuning: float
    position: int
    ease_factor: float
    interval: int
    repetitions: int
    next_review: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

(`RevisionItemUpdate` ne gagne pas de champ `type` — changer le type d'un
item existant est hors périmètre de ce chantier, cf. spec.)

- [ ] **Step 6: Lancer toute la suite `test_revision*.py` pour confirmer l'absence de régression sur les schémas**

Run: `docker compose exec -T backend pytest tests/test_revision.py tests/test_revision_qcm.py tests/test_revision_stats.py tests/test_revision_typed_study.py tests/test_shared_revision_sets.py tests/test_assignment_revision.py -v`
Expected: tous verts (les schémas Pydantic n'ont encore aucun call site
qui leur passe un `type` d'item — Task 3 branche `create_item`/
`update_item`/`grade_item`/`answer_item` dessus).

- [ ] **Step 7: Commit**

```bash
git add backend/app/services/revision_service.py backend/app/schemas/revision_schema.py backend/tests/test_revision.py
git commit -m "feat(revision): ajoute le type flashcard a validate_item_payload/check_answer"
```

---

### Task 3: Câbler le type d'item dans `RevisionService` (create/update/grade/answer)

**Files:**
- Modify: `backend/app/services/revision_service.py`
- Test: `backend/tests/test_revision.py`

**Interfaces:**
- Consumes : `RevisionItemCreate.type` (Task 2), `validate_item_payload`/
  `check_answer` prenant `item_type` (Task 2).
- Produces : `RevisionItem.type` toujours renseigné à la création (repli
  sur `rset.type` si absent) ; `StudySession.item_type` reflète le type
  réel de l'item étudié.

- [ ] **Step 1: Écrire les tests de rétrocompatibilité et du nouveau flux explicite (rouge)**

Ajouter dans `backend/tests/test_revision.py` :

```python
def test_create_item_without_type_inherits_set_type(client, auth_headers):
    """Retro-compatibilite : le frontend actuel n'envoie jamais `type`."""
    set_id = client.post("/api/v1/revision/sets", json={
        "name": "VF", "type": "vf",
    }, headers=auth_headers).json["id"]
    item = client.post(f"/api/v1/revision/sets/{set_id}/items", json={
        "payload": {"assertion": "Le ciel est bleu.", "correct": True}
    }, headers=auth_headers)
    assert item.status_code == 201
    assert item.json["type"] == "vf"


def test_create_item_with_explicit_type_overrides_set_type(client, auth_headers):
    """Un futur ensemble heterogene pourra fournir un type d'item explicite."""
    set_id = client.post("/api/v1/revision/sets", json={
        "name": "Mixte (encore homogene cote set)", "type": "vf",
    }, headers=auth_headers).json["id"]
    item = client.post(f"/api/v1/revision/sets/{set_id}/items", json={
        "type": "flashcard",
        "payload": {"front": "Chat", "back": "Cat"},
    }, headers=auth_headers)
    assert item.status_code == 201
    assert item.json["type"] == "flashcard"


def test_grade_item_rejects_flashcard_item_even_in_gradable_set(client, auth_headers):
    """item.type doit primer sur rset.type pour le gate GRADABLE_TYPES --
    sinon un item flashcard divergent dans un ensemble vf serait note via
    la logique vf (bug silencieux : `payload.get("correct")` vaut None,
    `bool(None)` vaut False, la reponse serait jugee fausse mais avec un
    code 200 au lieu du 400 attendu pour un type non corrigeable)."""
    set_id = client.post("/api/v1/revision/sets", json={
        "name": "VF", "type": "vf",
    }, headers=auth_headers).json["id"]
    item = client.post(f"/api/v1/revision/sets/{set_id}/items", json={
        "type": "flashcard",
        "payload": {"front": "Chat", "back": "Cat"},
    }, headers=auth_headers).json

    graded = client.post(
        f"/api/v1/revision/sets/{set_id}/items/{item['id']}/grade",
        json={"answer": {"value": True}}, headers=auth_headers,
    )
    assert graded.status_code == 400


def test_answer_item_records_item_type_not_set_type(client, auth_headers, app):
    """answer_item doit journaliser item.type (pas rset.type) dans
    StudySession -- verifie via un item de type explicite divergent du
    type de son ensemble (seul cas ou l'ancien code produirait une valeur
    differente)."""
    set_id = client.post("/api/v1/revision/sets", json={
        "name": "VF", "type": "vf",
    }, headers=auth_headers).json["id"]
    item = client.post(f"/api/v1/revision/sets/{set_id}/items", json={
        "type": "flashcard",
        "payload": {"front": "Chat", "back": "Cat"},
    }, headers=auth_headers).json

    client.post(
        f"/api/v1/revision/sets/{set_id}/items/{item['id']}/answer",
        json={"score": 4}, headers=auth_headers,
    )
    with app.app_context():
        from app.models.study_session import StudySession
        sess = StudySession.query.filter_by(item_id=item["id"]).first()
        assert sess.item_type == "flashcard"
```

- [ ] **Step 2: Lancer les tests, confirmer l'échec pour la bonne raison**

Run: `docker compose exec -T backend pytest tests/test_revision.py -k "create_item_without_type or create_item_with_explicit_type or grade_item_rejects_flashcard or answer_item_records_item_type" -v`
Expected (code actuel : `create_item` appelle encore `validate_item_payload(rset.type, data.payload)`, sans tenir compte de `data.type`) :
- `test_create_item_with_explicit_type_overrides_set_type`,
  `test_grade_item_rejects_flashcard_item_even_in_gradable_set` et
  `test_answer_item_records_item_type_not_set_type` échouent **tous les
  trois à la même ligne de mise en place** (`item = client.post(...).json["id"]` /
  `.json`) : le payload flashcard `{front, back}` est validé contre le
  type `"vf"` de l'ensemble (champ `"assertion"` requis absent) → la
  création de l'item répond 400 → accès à une clé `"id"` absente du
  corps d'erreur → `KeyError: 'id'`. C'est la bonne raison d'échec (le
  type explicite n'est pas encore câblé) même si la ligne qui échoue
  n'est pas l'assertion finale du test.
- `test_create_item_without_type_inherits_set_type` : payload valide pour
  `"vf"`, la création réussit still coté validation, mais
  `RevisionItemResponse.type` (désormais `str` requis, Task 2) reçoit
  `None` depuis la colonne DB (jamais affectée par `create_item` avant ce
  step) — la sérialisation de la réponse échoue. Confirmer le mode
  d'échec exact affiché par pytest (erreur de validation Pydantic
  propagée, selon la configuration d'erreurs de l'app) ; ce n'est pas
  une assertion Python classique mais c'est bien un échec pour la bonne
  raison.

- [ ] **Step 3: Câbler `create_item`, `update_item`, `grade_item`, `answer_item`**

Dans `backend/app/services/revision_service.py`, remplacer `create_item` :

```python
    def create_item(self, user_id: int, set_id: int, data: RevisionItemCreate) -> RevisionItemResponse:
        rset = self._get_set_or_404(set_id, user_id, write_required=True)
        item_type = data.type if data.type is not None else rset.type
        payload = validate_item_payload(item_type, data.payload)
        item = RevisionItem(
            set_id=set_id,
            type=item_type,
            payload=payload,
            tuning=data.tuning,
            position=data.position,
        )
        created = self._item_dao.create(item)
        return RevisionItemResponse.model_validate(created)
```

Remplacer `update_item` (valide désormais contre le type déjà stocké sur
l'item, pas contre celui de l'ensemble) :

```python
    def update_item(self, user_id: int, set_id: int, item_id: int, data: RevisionItemUpdate) -> RevisionItemResponse:
        self._get_set_or_404(set_id, user_id, write_required=True)
        item = self._get_item_or_404(item_id, set_id, user_id, write_required=True)
        if "payload" in data.model_fields_set and data.payload is not None:
            item.payload = validate_item_payload(item.type, data.payload)
        if data.tuning is not None:
            item.tuning = data.tuning
        if data.position is not None:
            item.position = data.position
        updated = self._item_dao.update(item)
        return RevisionItemResponse.model_validate(updated)
```

(`rset` n'est plus utilisé dans `update_item` que pour l'autorisation —
`self._get_set_or_404(...)` sans l'assigner à une variable inutilisée.)

Remplacer `answer_item` (utilise `item.type` pour `StudySession`, plus
`rset.type`) :

```python
    def answer_item(self, user_id: int, set_id: int, item_id: int, score: int) -> RevisionItemResponse:
        rset = self._get_set_or_404(set_id, user_id, write_required=False)
        item = self._get_item_or_404(item_id, set_id, user_id, write_required=False)

        if rset.user_id == user_id:
            tuning = (rset.tuning_default or 1.0) * (item.tuning or 1.0)
            ease_factor, interval, repetitions, next_review = calculate_sm2(
                score=score,
                ease_factor=item.ease_factor,
                interval=item.interval,
                repetitions=item.repetitions,
                tuning=tuning,
            )
            item.ease_factor = ease_factor
            item.interval = interval
            item.repetitions = repetitions
            item.next_review = next_review
            updated = self._item_dao.update(item)
        else:
            updated = item

        study_session = StudySession(
            user_id=user_id,
            module=rset.type,
            duration_seconds=0,
            cards_reviewed=1,
            cards_correct=1 if score >= 3 else 0,
            item_id=item.id,
            item_type=item.type,
            grade=score,
        )
        self._item_dao.db.add(study_session)
        self._item_dao.db.commit()

        return RevisionItemResponse.model_validate(updated)
```

(Seul `item_type=rset.type` devient `item_type=item.type` ; `module=rset.type`
reste inchangé — c'est un regroupement au niveau de l'ensemble, hors
périmètre.)

Remplacer `grade_item` (fetch l'item avant de vérifier le type
corrigeable, et utilise `item.type`) :

```python
    def grade_item(self, user_id: int, set_id: int, item_id: int, answer: dict) -> RevisionGradeResult:
        """Corrige une réponse à un item auto-corrigeable (vf/association/ordre) et
        met à jour SM-2 (réussi → 5, raté → 2). La définition/flashcard reste en self-eval."""
        rset = self._get_set_or_404(set_id, user_id, write_required=False)
        item = self._get_item_or_404(item_id, set_id, user_id, write_required=False)
        if item.type not in GRADABLE_TYPES:
            raise ValidationError("Ce type d'item n'est pas corrigé automatiquement.")

        is_correct = check_answer(item.type, item.payload or {}, answer or {})
        grade = 5 if is_correct else 2

        if rset.user_id == user_id:
            ease_factor, interval, repetitions, next_review = calculate_sm2(
                score=grade,
                ease_factor=item.ease_factor,
                interval=item.interval,
                repetitions=item.repetitions,
                tuning=(rset.tuning_default or 1.0) * (item.tuning or 1.0),
            )
            item.ease_factor = ease_factor
            item.interval = interval
            item.repetitions = repetitions
            item.next_review = next_review
            updated = self._item_dao.update(item)
        else:
            updated = item

        self._item_dao.db.add(StudySession(
            user_id=user_id,
            module=rset.type,
            duration_seconds=0,
            cards_reviewed=1,
            cards_correct=1 if is_correct else 0,
            item_id=item.id,
            item_type=item.type,
            grade=grade,
        ))
        self._item_dao.db.commit()

        return RevisionGradeResult(correct=is_correct, item=RevisionItemResponse.model_validate(updated))
```

- [ ] **Step 4: Lancer les tests ciblés, confirmer qu'ils passent**

Run: `docker compose exec -T backend pytest tests/test_revision.py -k "create_item_without_type or create_item_with_explicit_type or grade_item_rejects_flashcard or answer_item_records_item_type" -v`
Expected: 4/4 passent.

- [ ] **Step 5: Lancer toute la suite backend pour confirmer l'absence de régression globale**

Run: `docker compose exec -T backend pytest --cov=app --cov-report=term-missing`
Expected: 100 % des tests verts, coverage ≥ 80 % (garde CI). Porter une
attention particulière à `tests/test_revision_qcm.py` (utilise
`rset.type`, inchangé) et `tests/test_revision_stats.py` (lit
`RevisionSetStats.type`/`RevisionItemSummary` — non touchés par ce plan).

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/revision_service.py backend/tests/test_revision.py
git commit -m "feat(revision): create_item/update_item/grade_item/answer_item operent par type d'item"
```

---

### Task 4: Vérification finale et clôture du point de plan

**Files:**
- Modify: `workflow/backend-ensembles-heterogenes/PLAN.md`
- Modify: `workflow/backend-ensembles-heterogenes/JOURNAL.md`
- Modify: `workflow/JOURNAL.md`

**Interfaces:** aucune (bookkeeping).

- [ ] **Step 1: Suite complète + coverage, une dernière fois à froid**

Run: `docker compose exec -T backend pytest --cov=app --cov-report=term-missing`
Expected: tous verts, coverage ≥ 80 %.

- [ ] **Step 2: Confirmer qu'aucun fichier hors périmètre n'a été touché**

Run: `git diff --stat main..HEAD` (depuis la worktree/branche de ce
chantier)
Expected: seuls `backend/app/models/revision.py`,
`backend/app/schemas/revision_schema.py`,
`backend/app/services/revision_service.py`,
`backend/migrations/versions/c1d2e3f4a5b6_revision_item_type.py`,
`backend/tests/test_revision.py` apparaissent (plus les fichiers
`workflow/` de ce step). Aucun fichier `Deck`/`Flashcard`/`decks.py` et
aucun des 8 services listés dans les Global Constraints.

- [ ] **Step 3: Cocher les cases de `workflow/backend-ensembles-heterogenes/PLAN.md`**

Cocher toutes les cases sauf « Mise à jour de `docs/api_reference.md` si
des contrats d'endpoint changent » — aucun contrat n'a changé (seul un
champ optionnel `type` a été ajouté à `RevisionItemCreate`/`Response`,
non-cassant, la référence API documente déjà les champs existants sans
lister leur optionnalité exhaustive ; laisser cette case non cochée avec
une note explicite plutôt que de cocher à tort).

- [ ] **Step 4: Ajouter l'entrée de journal du chantier**

Dans `workflow/backend-ensembles-heterogenes/JOURNAL.md`, ajouter une
entrée décrivant : le déplacement de `type` vers l'item, la découverte
que la duplication qcm/vf/ordre avec `Flashcard.card_type` était du code
mort (pas une vraie fusion nécessaire), la découverte du vrai périmètre
(47 fichiers) qui a justifié le report de la fusion `Deck`/`Flashcard`
à des chantiers futurs distincts, et le choix de rétrocompatibilité
(`RevisionSet.type` conservé, `RevisionItemCreate.type` optionnel).
Référencer les 3 commits de ce plan (Task 1/2/3).

- [ ] **Step 5: Mettre à jour l'index global `workflow/JOURNAL.md`**

Ligne d'historique : chantier terminé (code), prêt pour la clôture (PR)
selon la procédure de la skill `gestion-chantier`. Mettre à jour la ligne
de statut de `backend-ensembles-heterogenes` dans la section « Chantiers
ouverts ».

- [ ] **Step 6: Commit**

```bash
git add workflow/backend-ensembles-heterogenes/PLAN.md workflow/backend-ensembles-heterogenes/JOURNAL.md workflow/JOURNAL.md
git commit -m "docs(backend-ensembles-heterogenes): cloture du plan, pret pour PR"
```
