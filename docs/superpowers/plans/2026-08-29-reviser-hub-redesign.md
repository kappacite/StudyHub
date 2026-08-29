# Reviser-hub Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct the reviser-hub chantier's frontend to actually match the validated Direction A mockups (never consulted during the original implementation), while keeping the already-correct, mockup-independent backend stats fix from the original plan.

**Architecture:** `Reviews.vue` is rebuilt from a tabbed multi-purpose hub into a lean unified "due items" feed (matches `Reviser.dc.html`) sourced from a new backend aggregation of `RevisionItem` due-items added to the existing `focus_service.py`. The 4 AI-tool tabs and the deck-management section it currently also hosts are relocated to their rightful, already-existing homes (`NoteFeynman.vue` — new, mirrors 3 sibling note-scoped screens; `Decks.vue` — already exists, gains the one missing piece). `RevisionSetStats.vue` and `RevisionBinderStats.vue` are rebuilt to match their own mockups.

**Tech Stack:** Flask 3 / SQLAlchemy 2 / Pydantic v2 (backend), Vue 3 `<script setup>` / TypeScript / Pinia (frontend), pytest (backend tests), Vitest + @vue/test-utils (frontend tests).

**Spec:** `docs/superpowers/specs/2026-08-29-reviser-hub-redesign.md` (corrects/extends `docs/superpowers/specs/2026-08-29-reviser-hub-design.md` — read both; the redesign spec is authoritative wherever they conflict).

**Mockup source files** (extracted from the published Claude Design canvas — see spec for the extraction procedure and full artifact URL; re-extract if these paths are gone, they're scratch, not committed):
- `C:\Users\denoe\AppData\Local\Temp\claude\C--Users-denoe-Documents-Projets-StudyHub\7989288f-bdab-487c-b7fd-913c45f96b5c\scratchpad\Reviser.dc.html`
- `...\scratchpad\RevisionSetStats.dc.html`
- `...\scratchpad\RevisionBinderStats.dc.html`

Every frontend task in this plan requires the implementer to **read the relevant mockup file directly** before writing any template code — this plan describes structure and data contracts, not exact pixel values; the mockup is the visual source of truth. Map mockup CSS variables to real project tokens per the mapping already documented in the `extract-claude-design-mockup` reference (mockup `--accent` → project `primary`, mockup `--highlight` → project `accent`, `--success`/`--danger` → same names) and the `design-system` skill.

## Global Constraints

- TDD strict where the plan calls for a test-first step; some frontend tasks in this plan are primarily structural (a near-total component rewrite) — for those, write the test(s) that lock in the new structure's key behaviors (data fetched, navigation targets, conditional rendering) before or alongside the rewrite, and state clearly in the report which behaviors are tested.
- `<script setup lang="ts">` only, no `any`. API calls only in stores/services, never directly in components.
- Never fabricate data that doesn't exist. Where the mockup shows a metric with no backing data (session duration, cumulative study time for revision items), omit it or substitute a real available metric — never hardcode a fake value. Each task below states explicitly what to do for its screen's gaps.
- Conventional Commits, French commit body.
- **Never `git push`** — blocked by a PreToolUse hook in this repo; the human pushes.
- This repo has PostToolUse hooks (`format_backend.py`, `format_web.py`) that auto-reformat any Python/Vue/TS file on first touch via Edit — expect large diffs from this on first-touch files, it's not scope creep, don't fight it.

---

### Task 1: Backend — `focus_service` gains a due revision-items block

**Files:**
- Modify: `backend/app/services/focus_service.py` (`get_today_items`)
- Modify: `backend/app/schemas/focus_schema.py` (`FocusItemSchema.type`)
- Test: `backend/tests/test_focus.py` (check this file exists; if the focus service has its own differently-named test file, use that instead — grep for `get_today_items` usages in `backend/tests/` first)

**Interfaces:**
- Produces: `FocusItemSchema.type` widens from `Literal['deck', 'note', 'assignment']` to also include `'revision_set'`. A new query block in `get_today_items` adds one `FocusItemSchema` **per revision set that has at least one due item** (grouped by set, matching the existing `deck_items` pattern which groups by deck rather than by individual card — do not emit one item per `RevisionItem`).
- Consumed by: Task 4 (`Reviews.vue`'s due-feed reads `FocusItem.type === 'revision_set'` rows).

Read `get_today_items`'s existing `deck_items`/`note_items`/`assignment_items` blocks first (`backend/app/services/focus_service.py:18-165`) — this task adds a 4th block following the exact same shape, not a rewrite of the function.

- [ ] **Step 1: Write the failing test**

Add to the relevant backend test file (create `backend/tests/test_focus.py` if none exists covering `focus_service`/`GET /focus/today` today — check first with `grep -rl "focus/today\|get_today_items" backend/tests/`):

```python
def test_focus_today_includes_due_revision_set(client, auth_headers):
    """Un ensemble de révision avec un item dû doit apparaître dans /focus/today,
    groupé par ensemble (une ligne, pas une par item) -- avant ce correctif,
    focus_service ignorait entièrement RevisionSet/RevisionItem."""
    from datetime import datetime, timedelta

    set_id = client.post(
        "/api/v1/revision/sets", json={"name": "Droit constit"}, headers=auth_headers
    ).json["id"]
    item = client.post(
        f"/api/v1/revision/sets/{set_id}/items",
        json={"type": "vf", "payload": {"assertion": "Vrai ?", "correct": True}},
        headers=auth_headers,
    ).json
    # L'item vient d'être créé avec next_review = maintenant (dû par défaut) --
    # confirmer explicitement via l'API plutôt que de supposer l'implémentation.

    resp = client.get("/api/v1/focus/today", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json
    revision_items = [i for i in body["items"] if i["type"] == "revision_set"]
    assert len(revision_items) == 1
    assert revision_items[0]["id"] == str(set_id)
    assert revision_items[0]["count"] >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_focus.py::test_focus_today_includes_due_revision_set -v` (adjust path if you placed the test elsewhere)
Expected: FAIL — `revision_items` is empty, `focus_service` doesn't query `RevisionItem` at all yet.

- [ ] **Step 3: Write the implementation**

In `backend/app/schemas/focus_schema.py`, widen `FocusItemSchema.type`:

```python
type: Literal['deck', 'note', 'assignment', 'revision_set']
```

In `backend/app/services/focus_service.py`, add a new block inside `get_today_items`, after the existing `deck_items`/`note_items` construction and before `items = deck_items + note_items` (adapt the final concatenation to include the new list — read the exact surrounding lines first, they may have shifted from what's shown here since Task numbering in the *other* already-merged plan touched this file's siblings, not this one):

```python
        # 4. Ensembles de révision (D8/reviser-hub) : un item par ENSEMBLE ayant
        #    au moins un item dû, pas un par item (même principe que deck_items).
        from app.models.revision import RevisionSet, RevisionItem

        due_revision_items = (
            db.session.query(RevisionItem)
            .join(RevisionSet)
            .filter(RevisionSet.user_id == user_id, RevisionItem.next_review <= now)
            .all()
        )
        items_by_set: Dict[int, list] = {}
        for it in due_revision_items:
            items_by_set.setdefault(it.set_id, []).append(it)

        revision_set_items = []
        revision_set_count = 0
        total_late_revision = 0
        if items_by_set:
            sets_by_id = {
                s.id: s
                for s in db.session.query(RevisionSet)
                .filter(RevisionSet.id.in_(items_by_set.keys()))
                .all()
            }
            for set_id, due_items in items_by_set.items():
                rset = sets_by_id.get(set_id)
                if rset is None:
                    continue
                count = len(due_items)
                revision_set_count += count
                late_items = [i for i in due_items if i.next_review < one_day_ago]
                is_late = len(late_items) > 0
                total_late_revision += len(late_items)
                revision_set_items.append(FocusItemSchema(
                    type="revision_set",
                    id=str(set_id),
                    title=rset.name,
                    count=count,
                    is_late=is_late,
                    last_session_ago_days=None,
                ))
```

Update the final assembly and totals to include this new block (`items = deck_items + note_items + revision_set_items` or fold into the existing `all_items` construction alongside `assignment_items` — match whichever variable the current code funnels everything through; adjust `total_due`/`late_count` in the final `FocusTodayResponse(...)` to add `revision_set_count`/`total_late_revision` to the existing sums).

- [ ] **Step 4: Run test to verify it passes**

Run the same command as Step 2. Expected: PASS.

- [ ] **Step 5: Run the full backend suite**

Run: `cd backend && .venv/Scripts/python.exe -m pytest -q`
Expected: green (aside from the known pre-existing, unrelated Windows-only `test_import.py` failures — see `workflow/bibliotheque-ensembles/JOURNAL.md` if you need to confirm these are pre-existing, don't spend time re-diagnosing them).

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/focus_service.py backend/app/schemas/focus_schema.py backend/tests/test_focus.py
git commit -m "feat(reviser-hub): focus_service inclut les ensembles de revision dus"
```

---

### Task 2: Frontend — widen `FocusItem.type`, create the shared due-item type-badge util

**Files:**
- Modify: `web/src/services/focusService.ts` (`FocusItem.type`)
- Modify: `web/src/utils/revisionItemTypeMeta.ts` (created by the already-merged original plan's Task 5 — re-read it first, it's still there)
- Test: none new (pure type change + a small pure-function addition covered by whichever component test consumes it in Task 4)

**Interfaces:**
- Produces: `FocusItem.type` includes `'revision_set'`. A new exported helper for the due-feed's `.type-badge`-style pill (read the mockup's `.type-badge` CSS class and the 3 example badges — `Deck`, `Série QCM`, `Feuille blanche` — for the exact visual language: small, uppercase, mono font, colored background per source) — name and exact shape decided by whichever implementer does Task 4, since it's consumed there; this task only widens the TS type.

- [ ] **Step 1: Widen the type**

In `web/src/services/focusService.ts`, change:

```ts
export interface FocusItem {
  type: 'deck' | 'note' | 'assignment' | 'revision_set'
  ...
}
```

(leave every other field unchanged)

- [ ] **Step 2: Type-check**

Run: `cd web && npx vue-tsc -b`
Expected: no new errors from this change alone (existing `FocusItem.type` consumers use exhaustive-ish `if/else` on `'deck'|'note'|'assignment'` in a couple of places — e.g. `Reviews.vue`'s current `studyItem()` — grep `focusStore\.\|FocusItem` across `web/src` to find every consumer and confirm none silently mishandles the new variant; Task 4 rewrites `Reviews.vue`'s consumer anyway).

- [ ] **Step 3: Commit**

```bash
git add web/src/services/focusService.ts
git commit -m "feat(reviser-hub): FocusItem accepte le type revision_set"
```

---

### Task 3: Frontend — `NoteFeynman.vue`, extracted from `Reviews.vue`

**Files:**
- Create: `web/src/views/Notes/NoteFeynman.vue`
- Modify: `web/src/router/index.ts` (new route `notes/:id/feynman`)
- Test: Create `web/tests/views/Notes/NoteFeynman.spec.ts`

**Interfaces:**
- Consumes: `POST /feynman/analyze`, `GET /feynman/tasks/:id` (existing backend endpoints, unchanged, already used by the code being moved).
- Produces: route `notes/:id/feynman`, name `NoteFeynman` — a nav link/button to this route from wherever `Notes.vue`/`NoteEdit.vue` link to the sibling `NoteQuiz`/`NoteEvaluation`/`Blurting` routes (check how those 3 are linked to today — likely a menu/button set on the note's own screen — and add a 4th entry there for consistency; this is a small addition, not this task's main deliverable, but don't leave Feynman unreachable).

The full Feynman logic being extracted currently lives in `web/src/views/Reviews/Reviews.vue`: template lines ~683-941, script lines ~1815-2020 (`feynmanStep`, `feynmanDraft`, `feynmanTimer`, `feynmanWordCount`, `feynmanSubjectTitle`, `feynmanResult`, `feynmanAnalyzing`, `feynmanError`, `startFeynman`, `evaluateFeynman`, `applyFeynmanResult`, plus the shared `formatTimer`/`startTimer`/`stopTimer` helpers). Read that exact code in the current file before starting — it is the literal source, don't reinvent the flow.

**Key difference from the extracted code**: `Reviews.vue`'s version has a config step where the user picks a note from `notesStore.notes` (`selectedNoteId`). In the new note-scoped screen, the note is already known from `route.params.id` — follow `web/src/views/Notes/Blurting.vue`'s pattern exactly (`const noteId = ref(route.params.id as string)`, `onMounted` fetches `GET /notes/${noteId}` for the title, no note-picker UI). The Feynman flow becomes 2 steps, not 3: `work` (draft + timer, shown immediately on mount instead of after a "commencer" click on a config screen — or keep a minimal "commencer" button if `Blurting.vue`/`NoteQuiz.vue` do the same for consistency, check their pattern) then `results`.

- [ ] **Step 1: Read the source**

Read `web/src/views/Reviews/Reviews.vue` template lines 683-941 and script lines 1815-2020 in full. Read `web/src/views/Notes/Blurting.vue` in full for the note-context/route-param/API-fetch pattern to mirror.

- [ ] **Step 2: Write the failing test**

Create `web/tests/views/Notes/NoteFeynman.spec.ts` modeled on whatever pattern `web/tests/views/Notes/` uses for its sibling screens if a `Blurting.spec.ts`/`NoteQuiz.spec.ts` already exists (check first, follow that file's mocking structure exactly — `api` mock via `vi.hoisted`, router with memory history, Pinia). At minimum, test:

```ts
it("charge le titre de la note depuis l'API au montage", async () => {
  // api.get('/notes/42') mocked to return { id: 42, title: 'Ma note' }
  // mount NoteFeynman at route /notes/42/feynman
  // assert wrapper.text() contains 'Ma note'
})

it("soumet l'explication et affiche le score renvoye par l'IA", async () => {
  // api.post('/feynman/analyze') mocked to return { status: 'SUCCESS', result: { clarity_score: 82, jargon: [], gaps: [], feedback: 'Bien', suggestion: '' } }
  // type into the draft textarea, click submit
  // assert wrapper.text() contains '82' and 'Bien'
})
```

(Write these as real, complete test bodies once you've read the sibling test file's exact mount helper — don't leave them as pseudocode; the two bullets above describe intent, the brief's other sibling test file is your literal template for the mock/mount boilerplate.)

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd web && npx vitest run tests/views/Notes/NoteFeynman.spec.ts`
Expected: FAIL — the component doesn't exist yet.

- [ ] **Step 4: Write the implementation**

Create `NoteFeynman.vue` by porting the read template/script from Step 1, adapted for route-param note context (no picker), following `Blurting.vue`'s structural pattern (imports, `<script setup lang="ts">`, page chrome). Keep the AI-analysis logic (`evaluateFeynman`, `applyFeynmanResult`, the polling loop) byte-faithful to the original — it's already correct and tested-by-production-use, only the note-selection mechanism changes.

Add the route in `web/src/router/index.ts`, next to the 3 sibling note routes:

```ts
{
  path: 'notes/:id/feynman',
  name: 'NoteFeynman',
  component: () => import('../views/Notes/NoteFeynman.vue'),
  meta: { requiresAuth: true },
},
```

Add a link to it wherever the note screen currently links to `Blurting`/`NoteQuiz`/`NoteEvaluation` (grep for `notes/${` router-link/push patterns in `Notes.vue`/`NoteEdit.vue` to find the exact spot).

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd web && npx vitest run tests/views/Notes/NoteFeynman.spec.ts`
Expected: PASS.

- [ ] **Step 6: Type-check**

Run: `cd web && npx vue-tsc -b`
Expected: no errors.

- [ ] **Step 7: Commit**

```bash
git add web/src/views/Notes/NoteFeynman.vue web/tests/views/Notes/NoteFeynman.spec.ts web/src/router/index.ts
git commit -m "feat(reviser-hub): extrait la methode Feynman en ecran dedie notes/:id/feynman"
```

(This task does NOT yet remove the Feynman tab from `Reviews.vue` — that happens in Task 6 when the whole file is rebuilt, so Feynman stays reachable via both paths in the interim if these tasks are reviewed independently.)

---

### Task 4: Frontend — relocate AI-flashcard-generation to `Decks.vue`

**Files:**
- Modify: `web/src/views/Decks/Decks.vue` (gains the generation modal/flow)
- Test: extend or create `web/tests/views/Decks/Decks.spec.ts` (check if one exists first)

**Interfaces:**
- Consumes: whatever backend endpoint `Reviews.vue`'s current "Générer depuis Notes / Classeurs" button hits (read `Reviews.vue`'s `openGenerateModal`/`genSourceType`/`genDeckTarget`/generation-submit function — search for the function that actually calls `api.post(...)` for generation, likely something like `/flashcards/generate` or similar; read the real endpoint from the current code, don't guess it).
- Produces: the same generation capability, reachable from `/decks` instead of `/reviser`.

`Reviews.vue`'s current "Decks de Répétition Espacée" section (`showGenerateModal`, `genSourceType`, `genNoteId`, `genBinderId`, `genDeckTarget`, `genNewDeckName`, `genExistingDeckId`, `genCoverage`, `genStatusMessage`, `openGenerateModal`, and the actual generation submit function — read the file to find its exact name) is the only piece of that section not already covered by `Decks.vue` (deck listing, deck creation via `decksStore.createDeck` are already there, confirmed).

- [ ] **Step 1: Read the source**

Read `Reviews.vue`'s "Decks de Répétition Espacée" template block and its script state/functions (search for `showGenerateModal` to find both). Read `Decks.vue` in full to find where a new "Générer depuis Notes / Classeurs" button and modal fit naturally (likely next to the existing "Nouveau deck" affordance).

- [ ] **Step 2: Write the failing test**

Add a test to `Decks.spec.ts` (create if none exists, following the mocking pattern of a sibling views test) asserting the generation entry point is reachable and submits to the correct endpoint — mirror whatever assertion style the existing `Decks.spec.ts` uses if present, or a minimal mount+click+assert-api-call test if not.

- [ ] **Step 3: Run test to verify it fails**

Expected: FAIL — the button/modal doesn't exist in `Decks.vue` yet.

- [ ] **Step 4: Write the implementation**

Port the generation modal template + script logic into `Decks.vue`, wired to a new button. Keep the generation logic itself byte-faithful — only its host component changes.

- [ ] **Step 5: Run test to verify it passes, then the full suite**

Run: `cd web && npx vitest run tests/views/Decks/Decks.spec.ts && npx vitest run && npx vue-tsc -b`
Expected: all green.

- [ ] **Step 6: Commit**

```bash
git add web/src/views/Decks/Decks.vue web/tests/views/Decks/Decks.spec.ts
git commit -m "refactor(reviser-hub): deplace la generation de flashcards IA vers Decks.vue"
```

(Like Task 3, this doesn't yet remove the section from `Reviews.vue` — Task 6 does, once both new homes exist and are verified.)

---

### Task 5: Frontend — `RevisionSetStats.vue`, rebuilt to match `RevisionSetStats.dc.html`

**Files:**
- Modify: `web/src/views/Reviews/RevisionSetStats.vue` (near-total rewrite)
- Modify: `backend/app/services/revision_stats_service.py` + `backend/app/schemas/revision_schema.py` if the SM-2 grade-distribution bar needs a new field (see below)
- Test: replace `web/tests/views/Reviews/RevisionSetStats.spec.ts` (already exists from the original, wrong-scope plan — its 3 tests about the "Mixte" badge and per-item icon are about content that survives in spirit but not in the old layout; rewrite the file to test the new structure, keep the underlying assertions — Mixte badge, per-item type visibility — where they still apply to the new layout)

**Interfaces:**
- Consumes: `SetStats` (frontend, `web/src/stores/revision.ts` — already has `type`, `items[]` with `.type` per item from the original plan's Tasks 1/6, still valid).
- Produces: none new beyond what already exists, unless Step 3 below determines a new backend field is needed for the grade-distribution bar.

Read `C:\Users\denoe\AppData\Local\Temp\claude\C--Users-denoe-Documents-Projets-StudyHub\7989288f-bdab-487c-b7fd-913c45f96b5c\scratchpad\RevisionSetStats.dc.html` in full before starting — it is the structural and visual source of truth for this task. Structure to build (see spec's § `RevisionSetStats.dc.html`):

1. Header: breadcrumb-style small label, set name as title, item-count + description subtitle, "Réviser cette série" button.
2. 2-column grid: (a) hero success-rate card with trend + SM-2 grade-distribution mini bar chart; (b) progression-over-time card (weekly buckets) + a stat trio.
3. Session-history card.

**Data availability, decided per the spec — do not deviate without re-reading the spec's reasoning:**
- Hero success rate, trend: derivable from `SetStats.avg_success_rate`/existing fields — check what's already returned and whether a "trend" (delta vs. a prior period) needs a new backend computation; if the mockup's "+5 pts" trend requires comparing to a prior window and no such data exists, **omit the trend delta** rather than fabricate it (same principle as the duration/session gaps below) — note this in your report as a deliberate omission, not a bug.
- SM-2 grade-distribution bar (4 buckets: Enc./Diff./Bien/Fac.): derivable from the individual `grade` values already stored per `StudySession` (1-5 scale, per `RevisionGradeRequest`/SM-2 convention — check `invariants-sm2` skill or `backend/app/services/spaced_repetition.py` for the exact grade semantics before bucketing). This needs a **new backend aggregation** — the current `RevisionSetStats` schema has no grade-histogram field. Add one: a `grade_distribution: dict[int, int]` (grade value → count) or 4 named buckets — decide the exact shape by re-reading `spaced_repetition.py`'s grade scale first (this plan doesn't presume the exact 1-5 → 4-bucket mapping, that's this task's job to get right from the real SM-2 implementation, not the mockup's illustrative "Enc./Diff./Bien/Fac." labels alone). Add this as a new field on `RevisionSetStats` populated by `RevisionStatsService.get_set_stats`, computed from the same `by_item`/`sessions` data already fetched there (no new query — the sessions are already loaded, just tally `grade` values instead of only using them for `success_rate`).
- Progression over time (6-week trend): derivable by bucketing existing `StudySession.created_at`/`grade` by week. New backend computation needed, same principle — add to the same response, computed from data already fetched, no new query.
- "Cartes mûres" stat: already available (`mastered_count`/`items_count`). "Temps cumulé": **not tracked** (`duration_seconds` is always `0` for revision-item sessions) — omit this stat or substitute a real one (e.g. total review count) per the spec's explicit instruction not to fabricate data. "Série en cours" (streak): check whether a per-set streak concept exists anywhere in the codebase (search for "streak" in `backend/app/services/`) before deciding to compute a new one or omit it.
- Session-history table: approximate by grouping `StudySession` rows for the set's items by calendar day (`created_at.date()`), one row per day with count of reviews and average/aggregate score % that day — **omit a duration column**, the mockup's "Durée" column has no backing data.

Given the amount of new backend surface this task uncovers (grade distribution + weekly trend + session-day grouping, all computed from already-fetched data, no new queries), expect this task's backend portion to be substantial — write it as its own sub-steps with its own TDD cycle before touching the Vue file.

- [ ] **Step 1: Read the sources**

Read the mockup file. Read `backend/app/services/spaced_repetition.py` for the real grade scale. Read the current `RevisionStatsService.get_set_stats`/`_aggregate_set` (already correct for the item-type fix, don't break that) to find where to tally grade/week buckets from data already in scope.

- [ ] **Step 2: Backend — write failing tests for the new stats fields**

Add tests to `backend/tests/test_revision_stats.py` asserting `GET /stats/sets/:id` returns a grade-distribution field and a weekly-progression field with sane shapes, computed from a fixture with several graded reviews spread across different grades/weeks (use `freezegun` or manually construct `StudySession` rows with explicit `created_at` via direct DB access in the test, following the pattern of other tests in this file that need to control timing — check if `freezegun` is already a dependency first via `requirements-dev.txt`; if not, construct timestamps directly).

- [ ] **Step 3: Run tests to verify they fail, then implement, then verify they pass**

Standard RED→GREEN cycle, same tooling as every other backend task in this plan family (`.venv/Scripts/python.exe -m pytest ...`).

- [ ] **Step 4: Frontend — widen `SetStats` (in `web/src/stores/revision.ts`) with the new fields**, matching the backend schema exactly.

- [ ] **Step 5: Frontend — write failing component tests for the new layout**

Rewrite `web/tests/views/Reviews/RevisionSetStats.spec.ts` to test the new structure: hero success rate renders, grade-distribution bars render (count matches buckets), session-history rows render grouped by day, Mixte/concrete-type badge still shows correctly (carry forward this assertion from the old test file, it's still valid), editing an item still works (carry forward from old test file).

- [ ] **Step 6: Run tests to verify they fail, then implement the new template, then verify they pass**

- [ ] **Step 7: Full suite + type-check**

Run: `cd backend && .venv/Scripts/python.exe -m pytest -q` and `cd web && npx vitest run && npx vue-tsc -b`

- [ ] **Step 8: Commit**

```bash
git add backend/app/services/revision_stats_service.py backend/app/schemas/revision_schema.py backend/tests/test_revision_stats.py web/src/stores/revision.ts web/src/views/Reviews/RevisionSetStats.vue web/tests/views/Reviews/RevisionSetStats.spec.ts
git commit -m "feat(reviser-hub): RevisionSetStats reconstruit selon la maquette validee"
```

---

### Task 6: Frontend — `RevisionBinderStats.vue`, rebuilt to match `RevisionBinderStats.dc.html`

**Files:**
- Modify: `web/src/views/Reviews/RevisionBinderStats.vue` (near-total rewrite)
- Test: replace `web/tests/views/Reviews/RevisionBinderStats.spec.ts`

**Interfaces:**
- Consumes: `BinderStats` (unchanged from the original plan's Task 6 widening), `decksStore` + `GET /stats/decks/:id` (existing, already used elsewhere e.g. `Reviews.vue`'s current `fetchDecksStats`) for the classic-deck side of the merged breakdown.

Read `C:\Users\denoe\AppData\Local\Temp\claude\C--Users-denoe-Documents-Projets-StudyHub\7989288f-bdab-487c-b7fd-913c45f96b5c\scratchpad\RevisionBinderStats.dc.html` in full first. Structure per the spec's § `RevisionBinderStats.dc.html`:

1. Header + "Réviser le classeur" button (unchanged concept from before).
2. 4-card stat grid: cartes totales, cartes maîtrisées (+%), temps total d'étude (**omit or substitute — not tracked**, same principle as Task 5), série en cours (check for existing streak data before computing new).
3. **"Répartition par deck et série"**: one row per classic Deck (in this binder) AND per RevisionSet (in this binder), each with its own mastery % bar, merged and sorted by mastery descending — **frontend-only merge**, no backend change: fetch the binder's decks (however `Binders.vue` currently does it — check that component for the exact call) with their per-deck stats (`GET /stats/decks/:id`, already used in `Reviews.vue` today), fetch `GET /revision/binders/:id/stats` as today, combine both lists client-side.
4. Keep the existing "Répartition par type" widget (already correctly fixed by the original plan's backend Task 4) as a secondary section below — per the spec's explicit decision, this is additive, not a replacement.

- [ ] **Step 1: Read the sources**

Read the mockup file. Read `Binders.vue` for the existing pattern of fetching decks scoped to a binder (reuse, don't reinvent). Read `Reviews.vue`'s current `fetchDecksStats` for the `/stats/decks/:id` call shape.

- [ ] **Step 2: Write failing component tests**

Rewrite `RevisionBinderStats.spec.ts`: assert the merged deck+set list renders both kinds of rows sorted by mastery, assert the existing type-breakdown widget still renders (carry forward from old test file), assert Mixte badge still shows on heterogeneous set rows (carry forward).

- [ ] **Step 3: Run tests to verify they fail**

- [ ] **Step 4: Implement**

Fetch decks for the binder + their stats (parallel with the existing `revisionStore.fetchBinderStats` call, `Promise.all`), merge client-side, render per the mockup structure.

- [ ] **Step 5: Run tests to verify they pass, then full suite + type-check**

- [ ] **Step 6: Commit**

```bash
git add web/src/views/Reviews/RevisionBinderStats.vue web/tests/views/Reviews/RevisionBinderStats.spec.ts
git commit -m "feat(reviser-hub): RevisionBinderStats reconstruit selon la maquette validee"
```

---

### Task 7: Frontend — `Reviews.vue` rebuilt as the unified due-items feed

**Files:**
- Modify: `web/src/views/Reviews/Reviews.vue` (total rewrite — from ~1880 lines of tabs/AI-tools/deck-management down to the due-feed alone)
- Test: replace `web/tests/views/Reviews/Reviews.spec.ts` (already exists from the original, wrong-scope plan — its 3 tests are about the tab structure being removed; rewrite entirely)

**Interfaces:**
- Consumes: `focusStore` (already fetches `/focus/today` today; now also carries `'revision_set'`-typed items per Task 1/2), `RevisionType`/`RevisionSet` types (unchanged).
- Produces: none new — this is the last task touching this file's public surface (nothing else in this plan imports from `Reviews.vue`).

**This task depends on Tasks 1-4 being done first** (backend focus data, the type widening, and both relocation targets existing) — do not start it before those are merged, since removing the AI-tabs/deck-management section here would orphan that functionality if its new home doesn't exist yet.

Read `C:\Users\denoe\AppData\Local\Temp\claude\C--Users-denoe-Documents-Projets-StudyHub\7989288f-bdab-487c-b7fd-913c45f96b5c\scratchpad\Reviser.dc.html` in full first. Structure per the spec:

1. Page header (title "Réviser", subtitle).
2. Summary banner: icon, count sentence, late-count sub-sentence, "Tout réviser" button (the app already has `focusStore.startUnifiedReview()`/`continueReview()` wired for this — reuse, don't reinvent, check the current `Reviews.vue` for how the existing summary banner at the top of the file already does this, it survives this rewrite conceptually).
3. "En retard" section: rows from `focusStore.items` where `is_late`, each with a `.type-badge`-style pill (per Task 2's badge — `Deck`/`Série QCM`/`Vrai-Faux`/etc./`Feuille blanche` depending on `FocusItem.type` and, for `'revision_set'` items, the set's dominant/actual item type), name, meta line, "Réviser" button navigating to the right study route (`/decks/:id/study` for `type: 'deck'`, `/revision/sets/:id/study` for `type: 'revision_set'` — **or** `/revision/sets/:id/run` if that specific set is homogeneous-QCM, matching the existing `openSet()` logic's `set.type === 'qcm' ? 'run' : 'study'` branch — you'll need the set's own `type` for this, either already present on the `FocusItem` or fetched via `revisionStore.sets` lookup by id, decide which is cleaner once you're in the code).
4. "Aujourd'hui" section: same row shape, items due today not late.
5. "À venir" section: same row shape, but a static "DEMAIN"/"N JOURS" label instead of a button (the mockup doesn't show upcoming *revision-set* items specifically since `focus_service` doesn't forecast beyond today for anything — check whether `focusStore.forecast`/`GET /focus/forecast` already covers this for decks, and whether extending it to revision-sets is in scope here or a reasonable omission; if `/focus/today` genuinely only returns due-today+overdue items for every source today, **the "À venir" section may need to stay empty or be omitted** rather than fabricate upcoming items — decide based on what `focus_forecast` actually returns when you read it, don't guess).

**What is explicitly removed from this file**: the `categories`/`activeTab`/`currentTabs` tab system, all 5 "Classiques" per-type set-listing tabs (Bibliothèque already covers this, per the *original* plan's own correctly-scoped reasoning — that part of the original design didn't need correcting, only the *hub* screen's own layout did), the 4 AI tool tab bodies (moved to `NoteFeynman.vue`/existing routes in Tasks 1-4... wait, Tasks 3), the "Decks de Répétition Espacée" section (moved to `Decks.vue` in Task 4).

- [ ] **Step 1: Read the sources**

Read the mockup file in full. Read the CURRENT `Reviews.vue` in full once more (it will have changed shape from earlier tasks touching sibling files, but not itself yet) to identify exactly what survives (the top summary banner's data-fetching, `focusStore` usage) vs. what's deleted.

- [ ] **Step 2: Write failing component tests**

Write `web/tests/views/Reviews/Reviews.spec.ts` from scratch: mock `focusStore`'s underlying API calls to return a mix of `deck`/`revision_set`/`note` items across late/today; assert each section renders the right items; assert the "Réviser" button on a `revision_set` row navigates to `/revision/sets/:id/study` (and to `/revision/sets/:id/run` for a homogeneous-QCM one — set up both fixture cases); assert the removed tabs/AI-sections are genuinely gone (`wrapper.text()` does not contain e.g. "Méthode Feynman").

- [ ] **Step 3: Run tests to verify they fail**

- [ ] **Step 4: Implement**

Rewrite the file. This is the single largest deletion in this plan — go carefully, and if you find yourself unsure whether a piece of currently-live logic (e.g. `getCleanText`/`extractKeywords`/`stopWords` — check whether these are Feynman-only, already moved in Task 3, or shared with something still live) is safe to delete, grep for its usage across the WHOLE `web/src` tree first, not just within this file, before removing it — if it's still referenced elsewhere, extract it to a shared location instead of deleting it.

- [ ] **Step 5: Run tests to verify they pass, then full suite + type-check**

Run: `cd web && npx vitest run && npx vue-tsc -b`

- [ ] **Step 6: Commit**

```bash
git add web/src/views/Reviews/Reviews.vue web/tests/views/Reviews/Reviews.spec.ts
git commit -m "feat(reviser-hub): Reviews.vue devient le flux du unifie selon la maquette validee"
```

---

### Task 8: Real visual verification against the mockups + close the chantier

**Files:** none (manual/scripted verification) — plus chantier bookkeeping.

This supersedes the original plan's Task 11 for the 3 rebuilt screens (`Reviser`/`Reviews.vue`, `RevisionSetStats.vue`, `RevisionBinderStats.vue`) — this time the check is against the actual mockups, side by side, not just "no regression."

- [ ] **Step 1: Set up the native environment**

Same procedure as the original plan's Task 11 (venv + SQLite backend, Vite frontend, no Docker) — reuse that section verbatim if the environment from the earlier session was torn down, adjusting ports if anything else is running.

- [ ] **Step 2: Create test data covering every row/section type the mockups show**

At least: one overdue Deck, one due-today Deck, one homogeneous QCM revision set (reviewed and unreviewed items), one heterogeneous revision set (reviewed items of ≥2 types), one due note for blurting (if easy to set up — otherwise note its absence in the report).

- [ ] **Step 3: Compare each rebuilt screen against its mockup, side by side, light + dark, desktop + mobile**

For each of `Reviser`/`Reviews.vue`, `RevisionSetStats.vue`, `RevisionBinderStats.vue`: open the `.dc.html` mockup file directly in a browser tab alongside the real running app at the equivalent screen, and check structurally — same sections present, same data shown in the same places, real numbers where the mockup shows illustrative ones. Screenshot both for the record if convenient, but the structural comparison is the actual check, not a pixel diff.

Also verify: `NoteFeynman.vue` reachable and functional from a note, `Decks.vue`'s relocated generation modal reachable and functional, no dead links to the old Feynman-tab/generation-modal locations inside the now-rebuilt `Reviews.vue`.

- [ ] **Step 4: Tear down the environment**

- [ ] **Step 5: Update chantier tracking**

Update `workflow/reviser-hub/PLAN.md`/`JOURNAL.md` and `workflow/JOURNAL.md` to reflect this correction — don't silently overwrite the existing entries documenting the original mistake, append to them (the mistake and its correction are both part of the real history, consistent with this project's existing convention of recording corrections rather than erasing them — see `workflow/bibliotheque-ensembles/JOURNAL.md`'s own "Correction de ce constat" precedent).

- [ ] **Step 6: Commit**

```bash
git add workflow/reviser-hub/PLAN.md workflow/reviser-hub/JOURNAL.md workflow/JOURNAL.md
git commit -m "docs(reviser-hub): verification visuelle contre les vraies maquettes, chantier pret a cloturer"
```

Then follow the `gestion-chantier` skill's closing procedure (ask the user to push, open the PR, wait for CI, merge) — same as any other chantier close-out.
