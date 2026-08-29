# Reviser-hub Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `Reviews.vue`, `RevisionSetStats.vue` and `RevisionBinderStats.vue` correctly handle heterogeneous revision sets (`RevisionSet.type: null`, items carrying their own type), and fix the backend stats service which silently returns empty/wrong data for any heterogeneous set today.

**Architecture:** Backend first (4 tasks: schema widening + 3 call sites in `revision_stats_service.py` that all currently key session lookups on `rset.type` instead of the item's own `item.type` — the root cause). Then frontend: extract a shared type→{label,icon} map (2nd consumer appearing), widen the mirrored TS interfaces, adapt the 3 screens, retire the now-redundant `RevisionSetManage.vue`, and finish with real visual verification in a native (non-Docker) environment.

**Tech Stack:** Flask 3 / SQLAlchemy 2 / Pydantic v2 (backend), Vue 3 `<script setup>` / TypeScript / Pinia (frontend), pytest (backend tests), Vitest + @vue/test-utils (frontend tests).

**Spec:** `docs/superpowers/specs/2026-08-29-reviser-hub-design.md`

## Global Constraints

- TDD strict: test written and run red before any implementation code (project phase ≥ 3, `CLAUDE.md`).
- `<script setup lang="ts">` only, no `any`. API calls only in stores/services, never in components (`web/CLAUDE.md`).
- DAO never imported by a service directly bypassing the service layer already in place; `db.session` never touched outside `app/dao/` (`backend/CLAUDE.md`) — not touched by this plan, no DAO changes needed.
- Pydantic v2 request/response on every route (already the case; this plan only widens existing schema fields, doesn't add routes).
- Coverage target ≥ 80% backend (CI-blocking) — not expected to be at risk, this plan adds tests for every changed line.
- Conventional Commits, French commit body.
- **Never `git push`** — blocked by a PreToolUse hook in this repo; the human pushes.

---

### Task 1: Backend schema — nullable set type, item type on summaries

**Files:**
- Modify: `backend/app/schemas/revision_schema.py:33-53` (`RevisionSetStats`, `RevisionSetSummary` classes are further down at lines ~184-219 and ~204-219 — see exact anchors below), `RevisionItemSummary` (lines 172-181)
- Test: `backend/tests/test_revision_stats.py`

**Interfaces:**
- Produces: `RevisionSetStats.type: str | None`, `RevisionSetSummary.type: str | None`, `RevisionItemSummary.type: str` (new field) — consumed by Tasks 2-4 (service) and Task 6 (frontend TS mirror).

- [ ] **Step 1: Write the failing test**

Append to `backend/tests/test_revision_stats.py`:

```python
def test_stats_schemas_accept_nullable_set_type_and_item_type():
    """RevisionSetStats/RevisionSetSummary.type doit accepter None (ensemble
    heterogene, D8) -- ces schemas de stats n'avaient jamais ete alignes avec
    RevisionSetResponse.type. RevisionItemSummary doit porter son propre type
    (necessaire pour l'afficher/le regrouper cote frontend, reviser-hub)."""
    from app.schemas.revision_schema import RevisionSetStats, RevisionSetSummary, RevisionItemSummary

    stats = RevisionSetStats(
        set_id=1, type=None, name="Mixte", items_count=0, reviewed_items=0,
        mastered_count=0, mastery_rate=0.0, avg_success_rate=0.0, true_retention=0.0,
        leeches_count=0, due_count=0, avg_difficulty=0.0, verdicts=[], items=[],
    )
    assert stats.type is None

    summary = RevisionSetSummary(
        set_id=1, type=None, name="Mixte", items_count=0, reviewed_items=0,
        mastered_count=0, mastery_rate=0.0, avg_success_rate=0.0, true_retention=0.0,
        leeches_count=0, due_count=0, avg_difficulty=0.0,
    )
    assert summary.type is None

    item_summary = RevisionItemSummary(
        item_id=1, type="flashcard", label="Chat", reviews=0, success_rate=0.0,
        difficulty=1.0, retrievability=0.0, is_leech=False, is_mature=False, due=False,
    )
    assert item_summary.type == "flashcard"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_revision_stats.py::test_stats_schemas_accept_nullable_set_type_and_item_type -v`
Expected: FAIL — `RevisionSetStats(type=None, ...)` raises `pydantic.ValidationError` (type is currently `str`, not nullable), and `item_summary.type` raises `AttributeError` (field doesn't exist yet).

- [ ] **Step 3: Write minimal implementation**

In `backend/app/schemas/revision_schema.py`, change `RevisionItemSummary`:

```python
class RevisionItemSummary(BaseModel):
    item_id: int
    type: str
    label: str
    reviews: int
    success_rate: float
    difficulty: float
    retrievability: float
    is_leech: bool
    is_mature: bool
    due: bool
```

Change `RevisionSetStats.type` and `RevisionSetSummary.type`:

```python
class RevisionSetStats(BaseModel):
    set_id: int
    type: str | None = None
    name: str
    ...
```

```python
class RevisionSetSummary(BaseModel):
    """Résumé d'un ensemble dans la vue agrégée d'un classeur (sans les items)."""

    set_id: int
    type: str | None = None
    name: str
    ...
```

(Keep every other field on all three classes unchanged — only the `type` lines and the new `RevisionItemSummary.type` line change.)

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_revision_stats.py::test_stats_schemas_accept_nullable_set_type_and_item_type -v`
Expected: PASS

- [ ] **Step 5: Run the full backend suite to check for regressions**

Run: `cd backend && .venv/Scripts/python.exe -m pytest -q`
Expected: same pass count as before this task, plus the one new test. No other test constructs these three schemas directly with positional/keyword args that would now be missing `type` on `RevisionItemSummary` (grep confirmed: only `revision_stats_service.py` constructs it, fixed in Task 3).

- [ ] **Step 6: Commit**

```bash
git add backend/app/schemas/revision_schema.py backend/tests/test_revision_stats.py
git commit -m "fix(reviser-hub): schemas de stats acceptent un type d'ensemble nul"
```

---

### Task 2: Backend — `get_item_stats` uses the item's own type, not the set's

**Files:**
- Modify: `backend/app/services/revision_stats_service.py:117-153` (`_compute_item_stats`, `get_item_stats`)
- Test: `backend/tests/test_revision_stats.py`

**Interfaces:**
- Consumes: `RevisionItemSummary.type: str` (Task 1, not used here but confirms schema is ready).
- Produces: `_compute_item_stats(self, item, sessions, now)` — signature drops the unused `item_type` param (was dead — never read in the body). Any future caller must not pass it.

- [ ] **Step 1: Write the failing test**

Append to `backend/tests/test_revision_stats.py`:

```python
def test_item_stats_on_heterogeneous_set_item(client, auth_headers):
    """Un ensemble reellement heterogene (type: None, cree sans 'type' dans le
    body, cf. test_create_set_without_type_is_heterogeneous) : les stats d'un
    item doivent refleter ses sessions reelles. Avant le correctif,
    get_item_stats passait rset.type (None) au DAO polymorphe
    (item_id/item_type discrimine la source, pas de FK) au lieu de item.type
    -- item_type == None ne matche jamais aucune session reelle, l'historique
    restait silencieusement vide."""
    set_id = client.post("/api/v1/revision/sets", json={"name": "Mixte"}, headers=auth_headers).json["id"]
    item = client.post(f"/api/v1/revision/sets/{set_id}/items", json={
        "type": "flashcard", "payload": {"front": "Chat", "back": "Cat"},
    }, headers=auth_headers).json

    client.post(f"/api/v1/revision/sets/{set_id}/study/answer/{item['id']}", json={"score": 4}, headers=auth_headers)

    stats = client.get(f"/api/v1/stats/items/{item['id']}", headers=auth_headers)
    assert stats.status_code == 200
    body = stats.json
    assert body["reviews"] == 1
    assert len(body["history"]) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_revision_stats.py::test_item_stats_on_heterogeneous_set_item -v`
Expected: FAIL — `body["reviews"] == 0`, `body["history"] == []` (the session was recorded with `item_type='flashcard'` but the query filtered on `item_type=None`, matching nothing).

- [ ] **Step 3: Write minimal implementation**

In `backend/app/services/revision_stats_service.py`, change the `_compute_item_stats` signature (drop the unused `item_type` parameter):

```python
    def _compute_item_stats(self, item: RevisionItem,
                            sessions: List[StudySession], now: datetime) -> RevisionItemStats:
```

(body unchanged — it never referenced `item_type`).

Change `get_item_stats`:

```python
    def get_item_stats(self, user_id: int, item_id: int) -> RevisionItemStats:
        item = self._item_dao.get_by_id(item_id)
        if not item:
            raise ResourceNotFoundError("Item de révision introuvable.")
        rset = self._get_set_or_404(item.set_id, user_id)
        sessions = self._session_dao.get_for_item(item.id, item.type)
        return self._compute_item_stats(item, sessions, datetime.utcnow())
```

(`rset` stays — still needed for the ownership/access check via `_get_set_or_404`, just no longer passed further.)

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_revision_stats.py -v`
Expected: PASS, including the pre-existing `test_item_stats_after_reviews` (homogeneous QCM set — `item.type` and `rset.type` coincide there, so it was already passing and stays green).

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/revision_stats_service.py backend/tests/test_revision_stats.py
git commit -m "fix(reviser-hub): get_item_stats filtre les sessions par le type de l'item, pas de l'ensemble"
```

---

### Task 3: Backend — `get_set_stats` groups session lookups by item type

**Files:**
- Modify: `backend/app/services/revision_stats_service.py:16-24` (`item_label`), `:157-198` (`_aggregate_set`), `:200-233` (`get_set_stats`)
- Test: `backend/tests/test_revision_stats.py`

**Interfaces:**
- Consumes: `RevisionItemSummary.type: str` (Task 1).
- Produces: `item_label(payload: dict) -> str` — signature drops the unused `set_type` param (dead, never read). `_aggregate_set` now populates `RevisionItemSummary.type` — Task 4 relies on this to rebuild the binder-level breakdown from already-computed item summaries instead of issuing new queries.

- [ ] **Step 1: Write the failing test**

Append to `backend/tests/test_revision_stats.py`:

```python
def test_set_stats_on_heterogeneous_set_counts_all_item_types(client, auth_headers):
    """Ensemble heterogene avec 2 types d'items notes : get_set_stats doit
    compter les deux. Avant le correctif, un seul appel de sessions groupe
    par rset.type (None) ne matchait aucune session reelle -> reviewed_items
    restait a 0 quel que soit le nombre de passages reels."""
    set_id = client.post("/api/v1/revision/sets", json={"name": "Mixte"}, headers=auth_headers).json["id"]
    flash = client.post(f"/api/v1/revision/sets/{set_id}/items", json={
        "type": "flashcard", "payload": {"front": "Chat", "back": "Cat"},
    }, headers=auth_headers).json
    vf = client.post(f"/api/v1/revision/sets/{set_id}/items", json={
        "type": "vf", "payload": {"assertion": "Le ciel est bleu.", "correct": True},
    }, headers=auth_headers).json

    client.post(f"/api/v1/revision/sets/{set_id}/study/answer/{flash['id']}", json={"score": 5}, headers=auth_headers)
    client.post(f"/api/v1/revision/sets/{set_id}/study/grade/{vf['id']}", json={"answer": {"value": True}}, headers=auth_headers)

    stats = client.get(f"/api/v1/stats/sets/{set_id}", headers=auth_headers)
    assert stats.status_code == 200
    body = stats.json
    assert body["type"] is None
    assert body["items_count"] == 2
    assert body["reviewed_items"] == 2
    types = {it["type"] for it in body["items"]}
    assert types == {"flashcard", "vf"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_revision_stats.py::test_set_stats_on_heterogeneous_set_counts_all_item_types -v`
Expected: FAIL — `reviewed_items == 0` (same root cause as Task 2, one level up), and `it["type"]` raises `KeyError` (`RevisionItemSummary.type` not populated in `_aggregate_set` yet).

- [ ] **Step 3: Write minimal implementation**

In `backend/app/services/revision_stats_service.py`, change `item_label` (drop the unused `set_type` param):

```python
def item_label(payload: dict) -> str:
    """Libellé court d'un item selon son type (pour les listes de stats)."""
    payload = payload or {}
    raw = (
        payload.get("question") or payload.get("assertion")
        or payload.get("term") or payload.get("title") or ""
    )
    raw = str(raw).strip() or "(sans titre)"
    return raw[:80]
```

In `_aggregate_set`, update the `RevisionItemSummary` construction (inside the `for item in items:` loop):

```python
            agg.item_summaries.append(RevisionItemSummary(
                item_id=item.id,
                type=item.type,
                label=item_label(item.payload),
                reviews=reviews,
                success_rate=item_success,
                difficulty=difficulty,
                retrievability=retrievability(item.interval, last_reviewed, now),
                is_leech=is_leech,
                is_mature=is_mature,
                due=is_due,
            ))
```

In `get_set_stats`, replace the single-type session fetch with a per-item-type grouped fetch (same pattern already used one level up in `get_binder_stats`):

```python
    def get_set_stats(self, user_id: int, set_id: int) -> RevisionSetStats:
        rset = self._get_set_or_404(set_id, user_id)
        now = datetime.utcnow()
        items = self._item_dao.get_by_set(set_id)

        # Sessions groupées par type d'ITEM réel (pas par type d'ensemble : un
        # ensemble hétérogène a des items de types différents, cf. D8/reviser-hub).
        ids_by_type: dict = {}
        for it in items:
            ids_by_type.setdefault(it.type, []).append(it.id)
        by_item: dict = {}
        for item_type, ids in ids_by_type.items():
            for sess in self._session_dao.get_for_items(ids, item_type):
                by_item.setdefault(sess.item_id, []).append(sess)

        agg = self._aggregate_set(rset, items, by_item, now)
        verdicts = self._build_verdicts(
            agg.items_count, agg.reviewed_items, agg.leeches_count, agg.due_count,
            agg.true_retention, agg.mature_reviews,
        )

        return RevisionSetStats(
            set_id=rset.id,
            type=rset.type,
            name=rset.name,
            items_count=agg.items_count,
            reviewed_items=agg.reviewed_items,
            mastered_count=agg.mastered_count,
            mastery_rate=agg.mastery_rate,
            avg_success_rate=agg.avg_success_rate,
            true_retention=agg.true_retention,
            leeches_count=agg.leeches_count,
            due_count=agg.due_count,
            avg_difficulty=agg.avg_difficulty,
            verdicts=verdicts,
            items=agg.item_summaries,
        )
```

(Only the session-fetching block and the `RevisionSetStats(...)` return actually change; the rest of the method body is unchanged from what's already there.)

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_revision_stats.py -v`
Expected: PASS, including `test_set_stats_query_budget` (existing — a homogeneous 6-item "vf" set now groups into exactly 1 type bucket, same single `get_for_items` call as before, budget `<= 6` unaffected) and `test_set_stats_aggregates_and_verdicts` (existing, homogeneous QCM set, unaffected).

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/revision_stats_service.py backend/tests/test_revision_stats.py
git commit -m "fix(reviser-hub): get_set_stats groupe les sessions par type d'item reel"
```

---

### Task 4: Backend — `get_binder_stats` breaks down by item type, not set type

**Files:**
- Modify: `backend/app/services/revision_stats_service.py:253-353` (`get_binder_stats`)
- Test: `backend/tests/test_stats_binder.py`

**Interfaces:**
- Consumes: `agg.item_summaries[].type` (Task 3) — the per-item type breakdown is rebuilt from data `_aggregate_set` already computes, no new query.
- Produces: `RevisionTypeBreakdown.type` values are now real item types (`qcm`, `vf`, `association`, `definition`, `ordre`, `flashcard` — 6 possible values, `flashcard` included), never a set-level type. `sets_count` per type now means "distinct sets with at least one item of this type" — a heterogeneous set can appear under several types simultaneously. Consumed by Task 8 (`RevisionBinderStats.vue`).

- [ ] **Step 1: Write the failing test**

Append to `backend/tests/test_stats_binder.py`:

```python
def test_binder_stats_breaks_down_heterogeneous_set_by_item_type(client, auth_headers):
    """Un ensemble heterogene doit apparaitre dans CHAQUE bucket de type que
    ses items couvrent reellement (pas invisible, pas un bucket unique
    'mixte') -- avant le correctif, le groupement par rset.type (None) faisait
    disparaitre ses sessions du breakdown."""
    binder_id = _binder(client, auth_headers, "Classeur")
    mixed_id = client.post("/api/v1/revision/sets", json={
        "name": "Mixte", "binder_id": binder_id,
    }, headers=auth_headers).json["id"]
    client.post(f"/api/v1/revision/sets/{mixed_id}/items", json={
        "type": "flashcard", "payload": {"front": "Chat", "back": "Cat"},
    }, headers=auth_headers)
    client.post(f"/api/v1/revision/sets/{mixed_id}/items", json={
        "type": "vf", "payload": {"assertion": "Vrai ?", "correct": True},
    }, headers=auth_headers)

    resp = client.get(f"/api/v1/stats/binders/{binder_id}", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json
    types = {b["type"]: b for b in body["by_type"]}
    assert types["flashcard"]["sets_count"] == 1
    assert types["vf"]["sets_count"] == 1
    assert types["flashcard"]["items_count"] == 1
    assert types["vf"]["items_count"] == 1
    summary_types = {s["set_id"]: s["type"] for s in body["sets"]}
    assert summary_types[mixed_id] is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_stats_binder.py::test_binder_stats_breaks_down_heterogeneous_set_by_item_type -v`
Expected: FAIL — `types` dict has key `None` (or is missing `"flashcard"`/`"vf"` entirely), not `"flashcard"`/`"vf"` — the breakdown is currently keyed by `rset.type` (`None` for this set), not by the items' real types.

- [ ] **Step 3: Write minimal implementation**

In `backend/app/services/revision_stats_service.py`, inside `get_binder_stats`, change the session-id grouping (one-line fix: group by item type, not set type):

```python
        # Sessions : une requête par type d'ITEM présent (≤ 6), pas par ensemble.
        ids_by_type: dict = {}
        for s in sets:
            for it in items_by_set.get(s.id, []):
                ids_by_type.setdefault(it.type, []).append(it.id)
```

(only `s.type` → `it.type` changes on that line; the rest of the fetch loop right after it is unchanged.)

Then replace the `by_type_acc` construction to accumulate per item type instead of per set type, using the `item_summaries` that `_aggregate_set` already computed (no new query — `item_summaries[].type` was wired in Task 3):

```python
        summaries: List[RevisionSetSummary] = []
        # type d'item -> {sets: set[int] (ids d'ensembles distincts), items: int, mastered: int}
        by_type_acc: dict = {}
        tot = _SetAggregate(set=binder)   # accumulateur global

        for rset in sets:
            agg = self._aggregate_set(rset, items_by_set.get(rset.id, []), by_item, now)
            summaries.append(RevisionSetSummary(
                set_id=rset.id, type=rset.type, name=rset.name,
                items_count=agg.items_count, reviewed_items=agg.reviewed_items,
                mastered_count=agg.mastered_count, mastery_rate=agg.mastery_rate,
                avg_success_rate=agg.avg_success_rate, true_retention=agg.true_retention,
                leeches_count=agg.leeches_count, due_count=agg.due_count,
                avg_difficulty=agg.avg_difficulty,
            ))
            tot.items_count += agg.items_count
            tot.reviewed_items += agg.reviewed_items
            tot.mastered_count += agg.mastered_count
            tot.leeches_count += agg.leeches_count
            tot.due_count += agg.due_count
            tot.mature_reviews += agg.mature_reviews
            tot.mature_successes += agg.mature_successes
            tot.success_rates.extend(agg.success_rates)
            tot.difficulties.extend(agg.difficulties)

            # Répartition par type d'ITEM (pas d'ensemble) : un ensemble
            # hétérogène compte dans chacun des types que ses items couvrent
            # réellement (D8/reviser-hub) — pas de nouvelle requête, réutilise
            # les item_summaries déjà calculés par _aggregate_set.
            for item_summary in agg.item_summaries:
                acc = by_type_acc.setdefault(item_summary.type, {"sets": set(), "items": 0, "mastered": 0})
                acc["sets"].add(rset.id)
                acc["items"] += 1
                if item_summary.is_mature:
                    acc["mastered"] += 1

        by_type = [
            RevisionTypeBreakdown(
                type=t, sets_count=len(a["sets"]), items_count=a["items"], mastered_count=a["mastered"],
                mastery_rate=round(a["mastered"] / a["items"] * 100, 1) if a["items"] else 0.0,
            )
            for t, a in sorted(by_type_acc.items())
        ]
```

(Everything below — `weakest`, `verdicts`, the final `RevisionBinderStats(...)` return — is unchanged.)

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_stats_binder.py -v`
Expected: PASS, including `test_binder_stats_aggregates_multiple_sets_and_types` (existing, two homogeneous sets of different types — grouping by item type instead of set type produces the same result for homogeneous sets, `sets_count == 1` each) and `test_binder_stats_query_budget` (existing, homogeneous-only scenario — same single distinct type "vf", same query count, budget `<= 8` unaffected).

- [ ] **Step 5: Run the full backend suite**

Run: `cd backend && .venv/Scripts/python.exe -m pytest -q`
Expected: all green (aside from the 5 pre-existing, unrelated Windows-only `test_import.py` failures documented in `workflow/bibliotheque-ensembles/JOURNAL.md` — a local `NamedTemporaryFile` locking issue, not present in CI).

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/revision_stats_service.py backend/tests/test_stats_binder.py
git commit -m "fix(reviser-hub): get_binder_stats repartit le breakdown par type d'item reel"
```

---

### Task 5: Frontend — extract the shared item-type icon/label map

**Files:**
- Create: `web/src/utils/revisionItemTypeMeta.ts`
- Modify: `web/src/views/Reviews/RevisionSetDetail.vue:145-178` (`TYPE_META` removed, imports adjusted)
- Test: (none new — this is a pure refactor; the existing `web/tests/views/Reviews/RevisionSetDetail.spec.ts` must keep passing unchanged, verified in Step 3)

**Interfaces:**
- Produces: `REVISION_ITEM_TYPE_META: Record<RevisionItemType, { label: string; icon: Component }>` — consumed by `RevisionSetDetail.vue` (this task), `RevisionSetStats.vue` (Task 7), `RevisionBinderStats.vue` (Task 8).

This is a refactor task, not new behavior — there is no new test to write first. The existing `RevisionSetDetail.spec.ts` is the regression check.

- [ ] **Step 1: Run the existing test to confirm the baseline is green**

Run: `cd web && npx vitest run tests/views/Reviews/RevisionSetDetail.spec.ts`
Expected: PASS (all 7 existing tests) — this is the baseline the refactor must not break.

- [ ] **Step 2: Create the shared module**

Create `web/src/utils/revisionItemTypeMeta.ts`:

```ts
import type { Component } from 'vue'
import { Layers, HelpCircle, Rows3, BookOpen, ListOrdered, Shuffle } from 'lucide-vue-next'
import type { RevisionItemType } from '../stores/revision'

export interface RevisionItemTypeMeta {
  label: string
  icon: Component
}

export const REVISION_ITEM_TYPE_META: Record<RevisionItemType, RevisionItemTypeMeta> = {
  flashcard: { label: 'Flashcards', icon: Layers },
  qcm: { label: 'QCM', icon: HelpCircle },
  vf: { label: 'Vrai / Faux', icon: Rows3 },
  definition: { label: 'Définition', icon: BookOpen },
  ordre: { label: 'Ordre', icon: ListOrdered },
  association: { label: 'Association', icon: Shuffle },
}
```

- [ ] **Step 3: Refactor `RevisionSetDetail.vue` to use it**

In `web/src/views/Reviews/RevisionSetDetail.vue`, remove the local `TYPE_META` constant and the now-unused icon imports, and import the shared map instead.

Change the imports block (remove `Layers, HelpCircle, Rows3, BookOpen, ListOrdered, Shuffle` from the `lucide-vue-next` import — they're only used inside the map that's moving out; keep `Play, Pencil, Trash2, Plus, AlertCircle`, still used directly in the template):

```ts
import {
  Play,
  Pencil,
  Trash2,
  Plus,
  AlertCircle,
} from 'lucide-vue-next'
import { REVISION_ITEM_TYPE_META } from '../../utils/revisionItemTypeMeta'
```

Remove the local `TYPE_META` block entirely:

```ts
const TYPE_META: Record<RevisionItemType, { label: string; icon: unknown }> = {
  flashcard: { label: 'Flashcards', icon: Layers },
  qcm: { label: 'QCM', icon: HelpCircle },
  vf: { label: 'Vrai / Faux', icon: Rows3 },
  definition: { label: 'Définition', icon: BookOpen },
  ordre: { label: 'Ordre', icon: ListOrdered },
  association: { label: 'Association', icon: Shuffle },
}
```

In the `typeGroups` computed, replace the two `TYPE_META[type]` reads with `REVISION_ITEM_TYPE_META[type]`:

```ts
const typeGroups = computed(() => {
  const byType = new Map<RevisionItemType, RevisionItem[]>()
  for (const item of items.value) {
    const list = byType.get(item.type) ?? []
    list.push(item)
    byType.set(item.type, list)
  }
  return Array.from(byType.entries()).map(([type, groupItems]) => ({
    type,
    items: groupItems,
    label: REVISION_ITEM_TYPE_META[type].label,
    icon: REVISION_ITEM_TYPE_META[type].icon,
    lastReviewedLabel: formatLastReviewed(groupItems),
  }))
})
```

- [ ] **Step 4: Run the test to confirm no regression**

Run: `cd web && npx vitest run tests/views/Reviews/RevisionSetDetail.spec.ts`
Expected: PASS, identical to Step 1 (output is byte-identical, only the source of the map moved).

- [ ] **Step 5: Type-check**

Run: `cd web && npx vue-tsc -b`
Expected: no errors.

- [ ] **Step 6: Commit**

```bash
git add web/src/utils/revisionItemTypeMeta.ts web/src/views/Reviews/RevisionSetDetail.vue
git commit -m "refactor(reviser-hub): extrait la table type->icone/libelle, un 2e ecran va la consommer"
```

---

### Task 6: Frontend — widen the stats TypeScript interfaces

**Files:**
- Modify: `web/src/stores/revision.ts:112-179` (`ItemSummary`, `SetStats`, `SetSummary`, `TypeBreakdown`)
- Test: (none new — pure type-level change; store behavior tests in `web/tests/stores/revision.spec.ts` are unaffected and re-run as a regression check)

**Interfaces:**
- Produces: `ItemSummary.type: RevisionItemType` (new field), `SetStats.type: RevisionType | null`, `SetSummary.type: RevisionType | null`, `TypeBreakdown.type: RevisionItemType` (widened from `RevisionType` — the breakdown now includes `flashcard`, which can never be a set's own homogeneous type but can be an item's type). Consumed by Task 7 (`RevisionSetStats.vue`) and Task 8 (`RevisionBinderStats.vue`).

- [ ] **Step 1: Run the existing store test to confirm the baseline is green**

Run: `cd web && npx vitest run tests/stores/revision.spec.ts`
Expected: PASS.

- [ ] **Step 2: Apply the type changes**

In `web/src/stores/revision.ts`, change `ItemSummary` (add `type`):

```ts
export interface ItemSummary {
  item_id: number
  type: RevisionItemType
  label: string
  reviews: number
  success_rate: number
  difficulty: number
  retrievability: number
  is_leech: boolean
  is_mature: boolean
  due: boolean
}
```

Change `SetStats.type` and `SetSummary.type`:

```ts
export interface SetStats {
  set_id: number
  type: RevisionType | null
  name: string
  items_count: number
  reviewed_items: number
  mastered_count: number
  mastery_rate: number
  avg_success_rate: number
  true_retention: number
  leeches_count: number
  due_count: number
  avg_difficulty: number
  verdicts: string[]
  items: ItemSummary[]
}

export interface SetSummary {
  set_id: number
  type: RevisionType | null
  name: string
  items_count: number
  reviewed_items: number
  mastered_count: number
  mastery_rate: number
  avg_success_rate: number
  true_retention: number
  leeches_count: number
  due_count: number
  avg_difficulty: number
}
```

Change `TypeBreakdown.type`:

```ts
export interface TypeBreakdown {
  type: RevisionItemType
  sets_count: number
  items_count: number
  mastered_count: number
  mastery_rate: number
}
```

- [ ] **Step 3: Run the test to confirm no regression**

Run: `cd web && npx vitest run tests/stores/revision.spec.ts`
Expected: PASS, unchanged.

- [ ] **Step 4: Type-check**

Run: `cd web && npx vue-tsc -b`
Expected: no errors yet — `RevisionSetStats.vue` and `RevisionBinderStats.vue` don't read `.type` in a way that breaks on widening (`str | null` and `RevisionType | RevisionItemType` widenings are backward-compatible with existing reads; Tasks 7-8 add the new null/flashcard handling).

- [ ] **Step 5: Commit**

```bash
git add web/src/stores/revision.ts
git commit -m "fix(reviser-hub): types stats frontend alignes sur le backend (type nullable, item.type)"
```

---

### Task 7: Frontend — `RevisionSetStats.vue` handles heterogeneous sets

**Files:**
- Modify: `web/src/views/Reviews/RevisionSetStats.vue`
- Test: Create `web/tests/views/Reviews/RevisionSetStats.spec.ts`

**Interfaces:**
- Consumes: `SetStats.type: RevisionType | null`, `ItemSummary.type: RevisionItemType` (Task 6), `REVISION_ITEM_TYPE_META` (Task 5).

- [ ] **Step 1: Write the failing tests**

Create `web/tests/views/Reviews/RevisionSetStats.spec.ts`:

```ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import RevisionSetStats from '../../../src/views/Reviews/RevisionSetStats.vue'

const SET = { id: 7, name: 'Ensemble', description: null, type: null, binder_id: null, tuning_default: 1, is_public: false, item_count: 2, read_only: false }

function itemSummary(id: number, type: string, overrides: Record<string, unknown> = {}) {
  return {
    item_id: id, type, label: `Item ${id}`, reviews: 1, success_rate: 100,
    difficulty: 1, retrievability: 1, is_leech: false, is_mature: false, due: false,
    ...overrides,
  }
}

const stub = { template: '<div />' }
function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/revision/sets/:id/stats', name: 'RevisionSetStats', component: stub }],
  })
}

async function mountStats(setType: string | null, items: ReturnType<typeof itemSummary>[]) {
  const pinia = createPinia()
  setActivePinia(pinia)
  api.get.mockImplementation((url: string) => {
    if (/\/stats\/sets\/\d+$/.test(url)) {
      return Promise.resolve({
        data: {
          set_id: 7, type: setType, name: 'Ensemble', items_count: items.length, reviewed_items: items.length,
          mastered_count: 0, mastery_rate: 0, avg_success_rate: 0, true_retention: 0, leeches_count: 0,
          due_count: 0, avg_difficulty: 1, verdicts: [], items,
        },
      })
    }
    if (/\/revision\/sets\/\d+$/.test(url)) return Promise.resolve({ data: { ...SET, type: setType } })
    if (/\/revision\/sets\/\d+\/items$/.test(url)) return Promise.resolve({ data: { data: [] } })
    return Promise.reject(new Error(`URL non mockée: ${url}`))
  })
  const router = createTestRouter()
  await router.push('/revision/sets/7/stats')
  await router.isReady()
  const wrapper = mount(RevisionSetStats, { global: { plugins: [pinia, router] } })
  await flushPromises()
  return wrapper
}

describe('RevisionSetStats', () => {
  beforeEach(() => vi.clearAllMocks())

  it("affiche Mixte quand l'ensemble est heterogene", async () => {
    const wrapper = await mountStats(null, [itemSummary(1, 'flashcard'), itemSummary(2, 'vf')])
    expect(wrapper.text()).toContain('Mixte')
  })

  it("affiche le libelle du type concret quand l'ensemble est homogene", async () => {
    const wrapper = await mountStats('qcm', [itemSummary(1, 'qcm')])
    expect(wrapper.text()).toContain('QCM')
    expect(wrapper.text()).not.toContain('Mixte')
  })

  it('affiche une icone de type par item', async () => {
    const wrapper = await mountStats(null, [itemSummary(1, 'flashcard'), itemSummary(2, 'vf'), itemSummary(3, 'qcm')])
    expect(wrapper.findAll('[data-test="item-type-icon"]')).toHaveLength(3)
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd web && npx vitest run tests/views/Reviews/RevisionSetStats.spec.ts`
Expected: FAIL — no "Mixte" text exists anywhere yet, no `[data-test="item-type-icon"]` elements exist yet.

- [ ] **Step 3: Write the implementation**

In `web/src/views/Reviews/RevisionSetStats.vue`, change the header block (replace the single `<span>` with a wrapping `<div>` holding two badges):

```html
    <div class="flex items-center justify-between text-sm font-semibold">
      <button @click="goBack" class="text-ink-muted hover:text-primary dark:text-ink-subtle flex items-center gap-1">
        <ChevronLeft class="w-4 h-4" /> Retour
      </button>
      <div v-if="stats" class="flex items-center gap-2">
        <span class="text-xs font-bold text-primary bg-primary-soft dark:bg-primary-soft dark:text-primary px-2.5 py-1 rounded-lg uppercase tracking-wider">
          Stats · {{ stats.name }}
        </span>
        <span data-test="set-type-badge" class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-surface-soft text-ink-muted dark:bg-surface-soft dark:text-ink-subtle">
          {{ setTypeLabel }}
        </span>
      </div>
    </div>
```

Change the item label span (add a type icon, wrap the label so `truncate` still works):

```html
                <span class="min-w-0 flex-1">
                  <span class="text-sm font-semibold text-ink dark:text-ink-subtle flex items-center gap-1.5">
                    <component :is="REVISION_ITEM_TYPE_META[it.type].icon" data-test="item-type-icon" class="w-3.5 h-3.5 text-ink-subtle shrink-0" />
                    <span class="truncate">{{ it.label }}</span>
                  </span>
                  <span class="flex flex-wrap gap-1.5 mt-1">
                    <span v-if="it.is_leech" class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-danger-soft text-danger dark:bg-danger-soft dark:text-danger">Sangsue</span>
                    <span v-if="it.is_mature" class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-success-soft text-success dark:bg-success-soft dark:text-success">Mûr</span>
                    <span v-if="it.due" class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-warning-soft text-warning dark:bg-warning-soft dark:text-warning">À réviser</span>
                  </span>
                </span>
```

Remove the now-inert `:locked-type` prop from the edit modal (the modal already prioritizes `editItem.type` over `lockedType` when editing — this prop was never actually read for this flow):

```html
    <RevisionItemModal
      v-if="showEditModal && editingItem"
      :binder-id="null"
      :decks="[]"
      :edit-item="editingItem"
      :locked-set-id="setId"
      @close="showEditModal = false"
      @updated="onItemSaved"
    />
```

In the `<script setup>` block, add the import and the `setTypeLabel` computed:

```ts
import { REVISION_ITEM_TYPE_META } from '../../utils/revisionItemTypeMeta'
```

```ts
const setTypeLabel = computed(() => {
  const t = stats.value?.type
  return t ? REVISION_ITEM_TYPE_META[t].label : 'Mixte'
})
```

(Place it near the other computed properties, e.g. right after the `canEdit` computed.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd web && npx vitest run tests/views/Reviews/RevisionSetStats.spec.ts`
Expected: PASS.

- [ ] **Step 5: Type-check**

Run: `cd web && npx vue-tsc -b`
Expected: no errors.

- [ ] **Step 6: Commit**

```bash
git add web/src/views/Reviews/RevisionSetStats.vue web/tests/views/Reviews/RevisionSetStats.spec.ts
git commit -m "feat(reviser-hub): RevisionSetStats affiche Mixte et une icone de type par item"
```

---

### Task 8: Frontend — `RevisionBinderStats.vue` handles heterogeneous sets

**Files:**
- Modify: `web/src/views/Reviews/RevisionBinderStats.vue`
- Test: Create `web/tests/views/Reviews/RevisionBinderStats.spec.ts`

**Interfaces:**
- Consumes: `SetSummary.type: RevisionType | null`, `TypeBreakdown.type: RevisionItemType` (Task 6), `REVISION_ITEM_TYPE_META` (Task 5).

- [ ] **Step 1: Write the failing tests**

Create `web/tests/views/Reviews/RevisionBinderStats.spec.ts`:

```ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import RevisionBinderStats from '../../../src/views/Reviews/RevisionBinderStats.vue'

function setSummary(id: number, type: string | null, overrides: Record<string, unknown> = {}) {
  return {
    set_id: id, type, name: `Ensemble ${id}`, items_count: 1, reviewed_items: 1,
    mastered_count: 0, mastery_rate: 0, avg_success_rate: 0, true_retention: 0,
    leeches_count: 0, due_count: 0, avg_difficulty: 1, ...overrides,
  }
}

const stub = { template: '<div />' }
function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/revision/binders/:id/stats', name: 'RevisionBinderStats', component: stub }],
  })
}

async function mountBinderStats(
  sets: ReturnType<typeof setSummary>[],
  byType: { type: string; sets_count: number; items_count: number; mastered_count: number; mastery_rate: number }[],
) {
  const pinia = createPinia()
  setActivePinia(pinia)
  api.get.mockImplementation((url: string) => {
    if (/\/stats\/binders\//.test(url)) {
      return Promise.resolve({
        data: {
          binder_id: 'b1', name: 'Classeur', include_descendants: true, sets_count: sets.length,
          items_count: sets.reduce((n, s) => n + (s.items_count as number), 0), reviewed_items: 0,
          mastered_count: 0, mastery_rate: 0, avg_success_rate: 0, true_retention: 0, leeches_count: 0,
          due_count: 0, avg_difficulty: 1, by_type: byType, sets, weakest_sets: sets, verdicts: [],
        },
      })
    }
    return Promise.reject(new Error(`URL non mockée: ${url}`))
  })
  const router = createTestRouter()
  await router.push('/revision/binders/b1/stats')
  await router.isReady()
  const wrapper = mount(RevisionBinderStats, { global: { plugins: [pinia, router] } })
  await flushPromises()
  return wrapper
}

describe('RevisionBinderStats', () => {
  beforeEach(() => vi.clearAllMocks())

  it("affiche Mixte pour un ensemble heterogene dans la liste des ensembles", async () => {
    const wrapper = await mountBinderStats([setSummary(1, null)], [])
    expect(wrapper.text()).toContain('Mixte')
  })

  it('affiche le libelle Flashcards dans la repartition par type', async () => {
    const wrapper = await mountBinderStats(
      [setSummary(1, null, { items_count: 2 })],
      [
        { type: 'flashcard', sets_count: 1, items_count: 1, mastered_count: 0, mastery_rate: 0 },
        { type: 'vf', sets_count: 1, items_count: 1, mastered_count: 0, mastery_rate: 0 },
      ],
    )
    expect(wrapper.text()).toContain('Flashcards')
    expect(wrapper.text()).toContain('Vrai / Faux')
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd web && npx vitest run tests/views/Reviews/RevisionBinderStats.spec.ts`
Expected: FAIL — first test fails because `typeLabel(null)` currently renders `undefined`/empty, not "Mixte". Second test fails because `TYPE_LABELS` has no `flashcard` key (`typeLabel('flashcard')` falls back to returning the raw string `'flashcard'`, not `'Flashcards'`).

- [ ] **Step 3: Write the implementation**

In `web/src/views/Reviews/RevisionBinderStats.vue`, replace the local `TYPE_LABELS`/`typeLabel` with the shared map:

```ts
import type { BinderStats, RevisionType, RevisionItemType } from '../../stores/revision'
import { REVISION_ITEM_TYPE_META } from '../../utils/revisionItemTypeMeta'
import { ChevronLeft } from 'lucide-vue-next'
```

Remove:

```ts
const TYPE_LABELS: Record<RevisionType, string> = {
  qcm: 'QCM', vf: 'Vrai/Faux', association: 'Association', definition: 'Définition', ordre: 'Ordre',
}
function typeLabel(t: RevisionType): string {
  return TYPE_LABELS[t] || t
}
```

Replace with:

```ts
function typeLabel(t: RevisionType | RevisionItemType | null): string {
  return t ? REVISION_ITEM_TYPE_META[t].label : 'Mixte'
}
```

(`bt.type` from the template is `RevisionItemType`, `s.type` is `RevisionType | null` — both call sites already pass through `typeLabel()` unchanged in the template, only the function body/signature changes.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd web && npx vitest run tests/views/Reviews/RevisionBinderStats.spec.ts`
Expected: PASS.

- [ ] **Step 5: Type-check**

Run: `cd web && npx vue-tsc -b`
Expected: no errors.

- [ ] **Step 6: Commit**

```bash
git add web/src/views/Reviews/RevisionBinderStats.vue web/tests/views/Reviews/RevisionBinderStats.spec.ts
git commit -m "feat(reviser-hub): RevisionBinderStats affiche Mixte et le libelle Flashcards"
```

---

### Task 9: Retire `RevisionSetManage.vue`

**Files:**
- Delete: `web/src/views/Reviews/RevisionSetManage.vue`
- Modify: `web/src/router/index.ts:140-145`

**Interfaces:**
- Produces: the route `revision/sets/:id/manage` now redirects to `RevisionSetDetail` instead of rendering a component. Consumed by Task 10 (the only remaining in-app link to `/manage` is in `Reviews.vue`, changed there directly rather than relying on this redirect).

No new automated test for this task: the redirect is a safety net for stale bookmarks/external links only (grep confirmed zero remaining in-app references once Task 10 lands — `RevisionSetManage.vue` has no existing spec file to delete either). It's verified manually in Task 11's visual check, and the full frontend suite (Step 3 below) confirms nothing else references the deleted file.

- [ ] **Step 1: Delete the component**

```bash
rm web/src/views/Reviews/RevisionSetManage.vue
```

- [ ] **Step 2: Change the router entry**

In `web/src/router/index.ts`, replace:

```ts
      {
        path: 'revision/sets/:id/manage',
        name: 'RevisionSetManage',
        component: () => import('../views/Reviews/RevisionSetManage.vue'),
        meta: { requiresAuth: true },
      },
```

with:

```ts
      {
        // RevisionSetDetail couvre déjà ce cas (regroupement par type, un
        // seul groupe pour un ensemble homogène) — écran retiré, reviser-hub.
        path: 'revision/sets/:id/manage',
        redirect: (to) => ({ name: 'RevisionSetDetail', params: to.params, query: to.query }),
      },
```

- [ ] **Step 3: Run the full frontend suite**

Run: `cd web && npx vitest run && npx vue-tsc -b`
Expected: all tests pass, no type errors — confirms no remaining import of the deleted file anywhere.

- [ ] **Step 4: Commit**

```bash
git add web/src/router/index.ts
git rm web/src/views/Reviews/RevisionSetManage.vue
git commit -m "refactor(reviser-hub): retire RevisionSetManage, redirige vers RevisionSetDetail"
```

---

### Task 10: Frontend — `Reviews.vue` gets a Mixte tab, "Gérer" repoints to `RevisionSetDetail`

**Files:**
- Modify: `web/src/views/Reviews/Reviews.vue`
- Test: Create `web/tests/views/Reviews/Reviews.spec.ts`

**Interfaces:**
- Consumes: `RevisionSet.type: RevisionType | null` (existing), nothing from Tasks 5-9 directly (this task doesn't touch stats).

- [ ] **Step 1: Write the failing tests**

Create `web/tests/views/Reviews/Reviews.spec.ts`:

```ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import Reviews from '../../../src/views/Reviews/Reviews.vue'

const HOMOGENEOUS_SET = { id: 1, name: 'QCM Bio', description: null, type: 'qcm', binder_id: null, tuning_default: 1, is_public: false, item_count: 3, read_only: false }
const MIXED_SET = { id: 2, name: 'Ensemble mixte', description: null, type: null, binder_id: null, tuning_default: 1, is_public: false, item_count: 5, read_only: false }

const stub = { template: '<div />' }
function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/reviser', name: 'Reviser', component: stub },
      { path: '/revision/sets/:id', name: 'RevisionSetDetail', component: stub },
      { path: '/revision/sets/:id/study', name: 'RevisionStudy', component: stub },
      { path: '/revision/sets/:id/run', name: 'QcmRun', component: stub },
      { path: '/revision/sets/:id/stats', name: 'RevisionSetStats', component: stub },
    ],
  })
}

async function mountReviews() {
  const pinia = createPinia()
  setActivePinia(pinia)
  api.get.mockImplementation((url: string) => {
    if (/^\/decks\?/.test(url)) return Promise.resolve({ data: { data: [] } })
    if (/^\/notes\?/.test(url)) return Promise.resolve({ data: { data: [] } })
    if (/^\/binders\?/.test(url)) return Promise.resolve({ data: { data: [] } })
    if (/^\/revision\/sets\?/.test(url)) return Promise.resolve({ data: { data: [HOMOGENEOUS_SET, MIXED_SET] } })
    if (/^\/focus\/today/.test(url)) return Promise.resolve({ data: { total_due: 0, late_count: 0, flashcard_count: 0, blurting_count: 0, assignment_count: 0, items: [] } })
    if (/^\/focus\/forecast/.test(url)) return Promise.resolve({ data: { forecast: [] } })
    if (/^\/focus\/retention/.test(url)) return Promise.resolve({ data: { by_subject: [] } })
    return Promise.reject(new Error(`URL non mockée: ${url}`))
  })
  const router = createTestRouter()
  await router.push('/reviser')
  await router.isReady()
  const wrapper = mount(Reviews, { global: { plugins: [pinia, router] } })
  await flushPromises()
  return { wrapper, router }
}

describe('Reviews - onglet Mixte', () => {
  beforeEach(() => vi.clearAllMocks())

  it("liste uniquement les ensembles heterogenes (type: null) dans l'onglet Mixte", async () => {
    const { wrapper } = await mountReviews()
    await wrapper.find('[data-test="tab-set-mixte"]').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Ensemble mixte')
    expect(wrapper.text()).not.toContain('QCM Bio')
  })

  it("le bouton Etudier de l'onglet Mixte navigue vers /study (jamais /run)", async () => {
    const { wrapper, router } = await mountReviews()
    await wrapper.find('[data-test="tab-set-mixte"]').trigger('click')
    await flushPromises()

    await wrapper.find('[data-test="study-set-2"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/revision/sets/2/study')
  })

  it('le bouton Gerer navigue vers RevisionSetDetail, plus vers /manage', async () => {
    const { wrapper, router } = await mountReviews()
    await wrapper.find('[data-test="tab-set-qcm"]').trigger('click')
    await flushPromises()

    await wrapper.find('[data-test="manage-set-1"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/revision/sets/1')
  })
})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd web && npx vitest run tests/views/Reviews/Reviews.spec.ts`
Expected: FAIL — `[data-test="tab-set-mixte"]` doesn't exist yet (no Mixte tab, no `data-test` attributes anywhere in this file yet).

- [ ] **Step 3: Write the implementation**

Add the `Mixte` tab entry to the `classic` category's `tabs` array:

```ts
const categories = [
  {
    id: 'classic', name: 'Classiques', tabs: [
      { id: 'flashcards', name: 'Flashcards' },
      { id: 'set-qcm', name: 'QCM' },
      { id: 'set-vf', name: 'Vrai / Faux' },
      { id: 'set-association', name: 'Association' },
      { id: 'set-definition', name: 'Définition' },
      { id: 'set-ordre', name: 'Ordre' },
      { id: 'set-mixte', name: 'Mixte' },
    ],
  },
  {
    id: 'ai', name: 'IA', tabs: [
      { id: 'evaluation', name: 'Évaluation IA' },
      { id: 'blank-sheet', name: 'Feuille Blanche' },
      { id: 'feynman', name: 'Méthode Feynman' },
      { id: 'quiz', name: 'Quiz Auto-QCM' },
    ],
  },
]
```

Replace the `currentSetType`/`currentSetTypeLabel`/`typedSets` computeds:

```ts
// Ensembles typés (Classiques hors flashcards) — 'set-mixte' est un
// pseudo-type (ensembles hétérogènes, type: null), pas un RevisionType.
const currentSetType = computed<RevisionType | null>(() =>
  activeTab.value.startsWith('set-') && activeTab.value !== 'set-mixte'
    ? (activeTab.value.slice(4) as RevisionType)
    : null,
)
const isMixteTab = computed(() => activeTab.value === 'set-mixte')
const currentSetTypeLabel = computed(() => {
  if (isMixteTab.value) return 'Mixte'
  return currentSetType.value ? SET_TYPE_LABELS[currentSetType.value] : ''
})
const typedSets = computed(() => {
  if (isMixteTab.value) return revisionStore.sets.filter(s => s.type === null)
  return currentSetType.value ? revisionStore.sets.filter(s => s.type === currentSetType.value) : []
})
```

In the template, change the panel's `v-if` (line ~169) to also show for the Mixte tab:

```html
<div v-if="currentSetType || isMixteTab" class="space-y-6">
```

Add a `data-test` to the tab button (in the "Sous-onglets de la catégorie active" loop):

```html
            <button
              v-for="tab in currentTabs"
              :key="tab.id"
              :data-test="`tab-${tab.id}`"
              @click="activeTab = tab.id"
              class="px-3.5 py-1.5 text-xs font-bold rounded-full transition-colors"
              :class="activeTab === tab.id ? 'bg-surface text-primary shadow-elev-1' : 'text-ink-muted hover:text-ink'"
            >{{ tab.name }}</button>
```

Change the empty-state message to not reference the (absent, on Mixte) "Créer" button:

```html
          <div v-if="typedSets.length === 0" class="text-center py-12 text-sm text-ink-subtle">
            {{ isMixteTab ? 'Aucun ensemble hétérogène. Créez-en un depuis la Bibliothèque.' : 'Aucun ensemble de ce type. Cliquez sur « Créer » pour en ajouter un.' }}
          </div>
```

Add `data-test` to the Étudier/Lancer button and repoint + add `data-test` to the Gérer button:

```html
                <button :data-test="`study-set-${set.id}`" @click="openSet(set)" class="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-white bg-primary hover:bg-primary-strong active:scale-95 transition-all">
                  <Compass class="w-3.5 h-3.5" /> {{ set.type === 'qcm' ? 'Lancer' : 'Étudier' }}
                </button>
                <button v-if="!set.read_only" :data-test="`manage-set-${set.id}`" @click="router.push(`/revision/sets/${set.id}`)" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-ink-muted dark:text-ink-subtle border border-line dark:border-line hover:bg-surface-soft dark:hover:bg-surface-soft transition-all" title="Gérer les éléments">
                  <Pencil class="w-3.5 h-3.5" /> Gérer
                </button>
```

(The `<Compass>` icon before "Lancer"/"Étudier" and the `<Pencil>` icon before "Gérer" stay exactly as they are — only `data-test` is added and the Gérer button's `@click` target changes from `` `/revision/sets/${set.id}/manage` `` to `` `/revision/sets/${set.id}` ``.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd web && npx vitest run tests/views/Reviews/Reviews.spec.ts`
Expected: PASS.

- [ ] **Step 5: Type-check**

Run: `cd web && npx vue-tsc -b`
Expected: no errors.

- [ ] **Step 6: Run the full frontend suite**

Run: `cd web && npx vitest run`
Expected: all green (no regression on any other tab of this file — none of the other tabs' template blocks were touched).

- [ ] **Step 7: Commit**

```bash
git add web/src/views/Reviews/Reviews.vue web/tests/views/Reviews/Reviews.spec.ts
git commit -m "feat(reviser-hub): Reviews.vue expose l'onglet Mixte, Gerer pointe vers RevisionSetDetail"
```

---

### Task 11: Real visual verification (native, non-Docker) + close the chantier

**Files:** none (manual/scripted verification only) — plus the usual chantier bookkeeping files.

This task exists because the previous chantier (`bibliotheque-ensembles`) deferred this step once and it turned out to hide a real blocking bug (see its journal). Do it now, don't defer it.

- [ ] **Step 1: Set up a native environment (no Docker)**

From `backend/`:

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install --quiet --upgrade pip
```

Install dependencies, excluding two packages that fail to build from source on this machine (Windows/arm64) and aren't needed for a SQLite-backed dev server — `psycopg2-binary` (Postgres driver, unused with SQLite) and the pinned `cryptography==42.0.7` (no arm64 wheel; a newer version does have one):

```bash
grep -v -iE "psycopg2|^cryptography==" requirements.txt > requirements_no_pg.txt
.venv/Scripts/python.exe -m pip install --quiet --only-binary=:all: cryptography
.venv/Scripts/python.exe -m pip install --quiet -r requirements_no_pg.txt
```

(If this machine isn't Windows/arm64, `pip install -r requirements.txt` directly may just work — try that first and only fall back to the above if it fails.)

Start the backend on a port unlikely to collide with anything else already running (check with `netstat -ano | grep LISTENING` first), with an explicit SQLite `DATABASE_URL` — **do not rely on the default**, a stray `.env` at the repo root (if the user has one from Docker experiments) gets picked up by Flask's dotenv search even when running from `backend/` and can inject a Postgres URL that only resolves inside a Docker network:

```bash
export FLASK_ENV=development
export FLASK_APP=wsgi:app
export DATABASE_URL="sqlite:///$(pwd)/studyhub_dev.db"
export REDIS_URL="redis://localhost:6399/0"
.venv/Scripts/python.exe -m flask run --port 5051 --debug
```

Wait for `http://localhost:5051/api/v1/health` to return 200 (auto-migration runs on startup, may take a few seconds).

From `web/`, point Vite's dev server at that backend (an absolute `VITE_API_BASE_URL` avoids the CSP issues that only apply to the production Nginx build anyway — irrelevant here, but keep the origin explicit):

```bash
echo "VITE_API_BASE_URL=http://localhost:5051" > .env
npm run dev -- --port 5174
```

(Port 5173 may already be in the backend's default CORS allow-list along with 3000 — check `backend/app/__init__.py`'s `CORS_ALLOWED_ORIGINS` default and pick a port from that list, or set `CORS_ALLOWED_ORIGINS` explicitly to include whichever port is actually used.)

- [ ] **Step 2: Create test data**

Register a user and log in via the UI (or via `curl -X POST http://localhost:5051/api/v1/auth/register ...` then log in through the browser). Through the UI:

1. In Bibliothèque → Révision, create a heterogeneous set ("Nouvel ensemble") and add at least 3 items of different types (e.g. one flashcard, one QCM, one vrai/faux) via `RevisionSetDetail.vue` → "Ajouter un élément".
2. Study the set once (`RevisionStudy.vue`) so at least one item has a real review recorded — this is what exercises the backend fix from Tasks 2-4 (an unreviewed set won't reveal whether stats aggregation is broken).
3. Also create one ordinary homogeneous set (e.g. type `qcm`) with at least one item, for comparison/non-regression checks.

- [ ] **Step 3: Check each changed screen, light + dark, desktop + mobile**

Desktop (browser at normal window size) and mobile (375×812 — use browser dev tools device emulation, or a quick Playwright script following the pattern already used in `bibliotheque-ensembles`'s worktree if the browser can't be resized):

- **`/reviser`**: the "Mixte" tab exists, lists only the heterogeneous set created in Step 2, "Étudier" launches `/study` (not `/run`), "Gérer" opens `RevisionSetDetail.vue` (not a 404, not the old manage screen). The 5 existing type tabs still work as before (homogeneous set still shows up under its own tab).
- **`/revision/sets/:id/stats`** on the heterogeneous set: header shows a "Mixte" badge; each item in the list shows a small type icon; the reviewed item shows a non-zero success rate / review count (proves the backend fix — before Task 2, this would show 0 reviews despite the real review from Step 2); editing an item still opens the modal with the *item's* own type preselected, not something else.
- **`/revision/sets/:id/stats`** on the homogeneous set: header shows the concrete type ("QCM"), not "Mixte" — non-regression check.
- **`/revision/binders/:id/stats`** (open from Bibliothèque's binder stats button, or navigate directly) on a binder containing both sets: "Répartition par type" shows real numbers for each type the heterogeneous set's items cover (not zero, not missing); the heterogeneous set's row shows a "Mixte" badge; the homogeneous set's row shows its real type.
- Visit `http://localhost:5174/revision/sets/<any-id>/manage` directly — confirm it redirects to `/revision/sets/<any-id>` instead of 404ing or showing a broken page.

- [ ] **Step 4: Tear down the environment**

```bash
# find and kill the two background processes (backend on 5051, frontend on 5174)
```

- [ ] **Step 5: Update the chantier's tracking files**

In `workflow/reviser-hub/PLAN.md`, check off every item and add a closing note referencing this plan's completion and what the visual check found (or didn't find — either way, document it, don't leave it silently "assumed fine").

In `workflow/reviser-hub/JOURNAL.md`, add a closing entry.

In `workflow/JOURNAL.md`, update the chantier's one-line status.

- [ ] **Step 6: Commit**

```bash
git add workflow/reviser-hub/PLAN.md workflow/reviser-hub/JOURNAL.md workflow/JOURNAL.md
git commit -m "docs(reviser-hub): verification visuelle faite, chantier pret a cloturer"
```

Then follow the `gestion-chantier` skill's closing procedure (ask the user to push, open the PR, wait for CI, merge).
