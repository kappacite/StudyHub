# Bibliothèque Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild `web/src/views/Binders/Binders.vue` so it actually matches the validated
Direction A mockups (`Bibliotheque.dc.html`, `Notes.dc.html`) — the current `SplitView`
(permanent folder-tree sidebar + tabbed content) was never checked against them when it was
built (commit `77ff833`, 2026-06-21). Replace it with a recursive grid of binder cards at
every level, with the existing Notes/Révision/Autres toggle content shown below the grid when
inside an actual binder (or the new virtual "Non classé" pseudo-binder).

**Architecture:** `Binders.vue` keeps its route (`bibliotheque/:id?`) and most of its existing
logic (tag filter, attach/detach modal, community/class sharing, `RevisionSetModal` CRUD) —
those are real features added after the mockup was designed, not being removed. What changes
is purely the top-level layout: `SplitView` (tree + tabs) is replaced by a card grid (children
of the current level) followed by the existing tab content (only rendered when the current
level is an actual binder or the virtual "Non classé" entry, never at true root).

**Tech Stack:** Vue 3 `<script setup lang="ts">`, Vitest + `@vue/test-utils`, existing Direction
A primitives (`BaseCard`, `PageHeader`, `Tabs`, `ListRow`, etc.). No backend changes — all
counts/aggregates are computed client-side from stores already fetched on mount, same principle
used everywhere else in this app.

**Spec:** `docs/superpowers/specs/2026-08-30-bibliotheque-redesign-design.md` — read in full
before starting. § "Décisions actées en chat" has the 3 product decisions this plan implements
(tree → grid, unfiled content → virtual "Non classé" card, "Autres" tab kept as-is).

## Global Constraints

- TDD strict — write the failing test first for every behavioral change.
- `<script setup lang="ts">` only, no `any`. API calls only in stores/services — this plan adds
  no new API calls (everything is computed from data already fetched by the existing
  `onMounted` `Promise.all`), so this should be easy to keep, but double-check no task
  introduces one.
- No raw style values (`web/CLAUDE.md`) — reuse existing tokens/primitives (`cat-*` category
  colors already used elsewhere in this file for Notes/Deck/RevisionSet/Diagram/PDF icons).
- Never fabricate data: "Dernière activité" on a binder card is computed from real
  `updated_at`/`created_at` timestamps of its direct children (see Task 1's exact rule) — a
  binder with zero direct children shows no activity line (or "Aucune activité", not a fake
  date).
- Counts and "dernière activité" are computed from **direct children only**, not recursive
  over sub-binders (see spec's design decision) — a deliberate simplification given the
  mockup shows no nested-binder example to derive an aggregate convention from.
- The virtual "Non classé" entry is not a real `Binder` record — it must never be sent to
  `bindersStore.createBinder`/`updateBinder`/`deleteBinder`, must never appear in the
  attach/detach modal's binder-target list, and must not break the breadcrumb (which reads
  `bindersStore.binders` to build its trail — it needs a special case).
- Conventional Commits, French commit body. Never `git push`.
- This repo has PostToolUse hooks that auto-reformat Python/Vue/TS files on first touch —
  expect some formatting noise on first-touch files, not scope creep.

---

### Task 1: Extract `BinderCard.vue` + client-side aggregate computation

**Files:**
- Create: `web/src/components/binders/BinderCard.vue`
- Create: `web/tests/components/binders/BinderCard.spec.ts`
- Modify: `web/src/views/Binders/Binders.vue` (add the aggregate-computation logic; the card
  itself is not wired into the template yet — that's Task 2)

**Interfaces:**
- `BinderCard.vue` props: `{ binder: { id: string, name: string, readOnly?: boolean }, deckCount: number, noteCount: number, lastActivityLabel: string | null }`. Emits `click`. Matches
  `Bibliotheque.dc.html`'s card exactly: folder icon in a colored circle, name, `N decks · M notes`
  in mono, `Dernière activité : {{label}}` (or nothing if `lastActivityLabel` is `null`), a
  colored left border (use `border-l-primary` or equivalent token for the first/most-recent
  card if you want to echo the mockup's single-highlighted-card treatment — check the mockup:
  only ONE card has a highlight-colored border in the example, the rest have a neutral
  `--line` border; simplest faithful reading is "today's most recent" gets the accent border,
  everything else gets a neutral one — implement this as a prop `highlighted: boolean` decided
  by the parent, not hardcoded inside the card).
- Aggregate computation (in `Binders.vue`, exported as a plain function or composable so the
  test can call it directly, e.g. `binderAggregate(binderId: string | null): { deckCount, noteCount, lastActivityLabel }`):
  - `deckCount` = `decksStore.decks.filter(d => d.binder_id === binderId).length`
  - `noteCount` = `notesStore.notes.filter(n => n.binder_id === binderId).length`
  - `lastActivityLabel`: collect `updated_at` from notes with that `binder_id`, `updated_at`
    from revision sets with that `binder_id`, and `created_at` from decks with that `binder_id`
    (decks have no `updated_at` field — confirmed by reading `stores/decks.ts`) into one list,
    take the max, format exactly like the existing `setAggregate()`'s `lastPassageLabel` pattern
    already in this file ("aujourd'hui" / "hier" / "il y a N jours") — reuse that day-diff
    logic rather than reimplementing it, extract it to a shared helper if it's currently
    private to `setAggregate`. If the list is empty, return `null` (no fabricated date).

- [ ] **Step 1: Read the sources**

Read `Bibliotheque.dc.html` in full (card markup, colors, spacing). Read `Binders.vue`'s
current `setAggregate()` function (~line 793) for the day-diff formatting pattern to reuse.

- [ ] **Step 2: Write the failing tests**

`BinderCard.spec.ts`: renders name, deck/note counts, activity label when provided; renders no
activity line when `lastActivityLabel` is `null`; emits `click`. A second test block (in
`Binders.spec.ts` if it exists, or a new one) for the aggregate function: given fixture
decks/notes/sets with known `binder_id`/timestamps, asserts the correct counts and the correct
"aujourd'hui"/"hier"/"il y a N jours" label, and asserts `null` for a binder with zero children.

- [ ] **Step 3: Run tests to verify they fail**

- [ ] **Step 4: Implement** `BinderCard.vue` and the aggregate function.

- [ ] **Step 5: Run tests to verify they pass, then type-check**

Run: `cd web && npx vitest run tests/components/binders/BinderCard.spec.ts && npx vue-tsc -b`

- [ ] **Step 6: Commit**

```bash
git add web/src/components/binders/BinderCard.vue web/tests/components/binders/BinderCard.spec.ts web/src/views/Binders/Binders.vue
git commit -m "feat(bibliotheque): ajoute BinderCard et le calcul d'agregats client-side"
```

---

### Task 2: Replace `SplitView` with the recursive grid — root level + navigation

**Files:**
- Modify: `web/src/views/Binders/Binders.vue`
- Modify: `web/tests/views/Binders/Binders.spec.ts` (check if it exists first — if not, this
  task creates it; if it does, expect to rewrite large parts of it, the old tests assert the
  `SplitView`/tree structure being removed)

**Interfaces:**
- New computed `childrenAtCurrentLevel`: at true root (`currentBinderId === null`), returns
  `bindersStore.binders.filter(b => b.parent_id === null)` **plus** the virtual "Non classé"
  entry (a plain object literal, not a `Binder`, e.g. `{ id: 'non-classe', name: 'Non classé', virtual: true }`) — placed first or last, your call, note the choice in your report. At any
  real binder level, returns `bindersStore.binders.filter(b => b.parent_id === currentBinderId)`
  (no virtual entry — only the true root has unfiled content). When `currentBinderId === 'non-classe'`, this computed returns an empty array (the virtual entry has no children of its
  own — it's a flat filter, not a hierarchy node).
- The existing `currentBinderId` ref, `goTo()`, and the `watch` syncing it from `route.params.id`
  all need to treat `'non-classe'` as a valid, non-`fetchMissingBinder`-triggering value (the
  existing `watch(currentBinderId, ...)` calls `fetchMissingBinder` for any non-null id not
  already in the store — add a guard so it skips this for `'non-classe'`).
- `currentNotes`/`currentDecks`/`currentSets` (existing computeds, used by the tab content)
  already filter by `binder_id === currentBinderId.value` — for `'non-classe'` to work
  correctly with these unchanged, `currentBinderId.value` needs to resolve to `null` when the
  route segment is `'non-classe'` for the PURPOSE of those 3 filters, but resolve to the string
  `'non-classe'` for the purpose of routing/breadcrumb/grid-children logic. Decide the cleanest
  way to handle this dual meaning (e.g., a separate computed `filterBinderId` that's `null` when
  `currentBinderId === 'non-classe'` else equal to `currentBinderId`, used only by the 3 content
  filters) rather than overloading one ref with two meanings implicitly — this is exactly the
  kind of subtle bug this task's tests must catch.
- Breadcrumb (`breadcrumbItems` computed, ~line 1099): add a special case for
  `currentBinderId.value === 'non-classe'` → `[{ label: 'Racine', to: '/bibliotheque' }, { label: 'Non classé' }]` (no `to` on the last segment, matching the existing pattern for the
  current page). Do not let it fall into the `bindersStore.binders.find(...)` loop, which
  would find nothing and silently produce a wrong trail.
- Root level (`currentBinderId === null`): render ONLY the grid — no tabs, no tab content, no
  attach modal trigger for content types tied to a specific binder (the "Ajouter" menu's
  Note/Diagramme items don't make sense at true root, since nothing typed can attach to
  `binder_id === null` — check what the current `addNote()`/`addDiagram()` do when
  `currentBinderId.value === null` today; if they already handle `null` gracefully by creating
  unfiled content, that behavior can stay reachable from **inside** "Non classé" instead of at
  true root — decide and note in your report). "Nouveau classeur" (`openCreateModal`, currently
  in the left tree's header) becomes the grid's primary action button, matching the mockup.
- Any real binder OR `'non-classe'`: render the grid of direct sub-binders (empty for
  `'non-classe'`) ABOVE the existing tab content (Notes/Révision/Autres — unchanged internals).

- [ ] **Step 1: Read the sources**

Read the full current `Binders.vue` template (especially the `SplitView` block ~line 156-487)
and script (`currentSubBinders`, `currentBinderId` watchers, `breadcrumbItems`, `goTo`,
`addNote`/`addDiagram`, the "Ajouter" menu). Read `Notes.dc.html` again for exactly what sits
below the sub-binder grid when inside a real binder.

- [ ] **Step 2: Write failing component tests**

Cover: root shows only the grid (top-level binders + "Non classé" card with correct
aggregates), no tab content visible at root; clicking a binder card navigates to
`/bibliotheque/:id`; inside a real binder with sub-binders, both the sub-binder grid AND the
tab content render; clicking "Non classé" navigates to `/bibliotheque/non-classe` and shows
tab content filtered to `binder_id === null` with NO sub-binder grid section rendered; the
breadcrumb reads "Racine / Non classé" for that route without crashing.

- [ ] **Step 3: Run tests to verify they fail**

- [ ] **Step 4: Implement**

Remove the `SplitView` wrapper and its `#left` slot (folder tree). Add the grid section
(reusing `BinderCard.vue` from Task 1) rendering `childrenAtCurrentLevel`. Keep the existing
`#right`-slot content (Notes/Révision/Autres tabs) but gate its rendering on
`currentBinderId.value !== null` (true root shows no tabs at all). Wire the `filterBinderId`
distinction described above into `currentNotes`/`currentDecks`/`currentSets`.

- [ ] **Step 5: Run tests to verify they pass, then full suite + type-check**

Run: `cd web && npx vitest run && npx vue-tsc -b`

- [ ] **Step 6: Commit**

```bash
git add web/src/views/Binders/Binders.vue web/tests/views/Binders/Binders.spec.ts
git commit -m "feat(bibliotheque): remplace le SplitView par la grille recursive de classeurs"
```

---

### Task 3: Non-regression on existing binder-scoped features

**Files:**
- Modify: `web/src/views/Binders/Binders.vue` (only if Task 2 broke something here — this task
  is primarily verification, not new code)
- Modify: `web/tests/views/Binders/Binders.spec.ts`

**Interfaces:** none new — this task verifies that everything the original `77ff833` commit
message promised ("owner vs lecture-seule, clone, attache/détache, partage communauté + partage
classe, stats binder, filtres tags") still works identically after Task 2's structural change,
since none of it was supposed to change.

- [ ] **Step 1: Read the sources**

Re-read every modal and its trigger in the current `Binders.vue` (share, class-share, attach,
create-folder) to confirm each one's trigger button still has a sensible home in the new
layout (e.g. the "Stats"/"Partager"/"Classe"/"Réviser ce dossier" buttons in `PageHeader`'s
`#actions` slot were already binder-scoped and gated on `currentBinderId !== null` — confirm
this still reads correctly for `'non-classe'`, which has no real binder to share/stat).

- [ ] **Step 2: Write failing tests for any gap found**

For each binder-scoped action, assert it's hidden (not just non-functional) when
`currentBinderId === 'non-classe'` (no `RevisionBinderStats`, no community/class sharing — "Non
classé" isn't a real binder and can't be shared or stat'd) — the read-only banner, clone
button, tag filter, and attach/detach modal should still work identically for real binders.

- [ ] **Step 3: Run tests to verify they fail, then fix, then verify they pass**

- [ ] **Step 4: Full suite + type-check**

- [ ] **Step 5: Commit**

```bash
git add web/src/views/Binders/Binders.vue web/tests/views/Binders/Binders.spec.ts
git commit -m "fix(bibliotheque): masque les actions specifiques a un classeur reel sur Non classe"
```

---

### Task 4: Real visual verification against the mockups + close the chantier

**Files:** none (manual/scripted verification) — plus chantier bookkeeping.

- [ ] **Step 1: Set up the native environment**

Same procedure as `reviser-hub-redesign`'s Task 8 (venv + SQLite backend launched via direct
`app.run()` — not `flask run`, which auto-loads the repo-root `.env` — Vite frontend, no
Docker).

- [ ] **Step 2: Create test data covering every card/section type**

At least: 2-3 top-level binders with varying deck/note counts and recent activity, one binder
with a sub-binder (to verify the recursive grid), some unfiled notes/decks/sets (to populate
"Non classé" with a non-zero count), one binder with zero content (to verify "Aucune activité"
renders instead of a fake date).

- [ ] **Step 3: Compare against the mockups, side by side, light + dark, desktop + mobile**

Root grid vs. `Bibliotheque.dc.html`; inside a binder (with and without sub-binders) vs.
`Notes.dc.html`; "Non classé" entry (no direct mockup, but should look structurally identical
to a real binder's content view, just with a different header). Also verify: tag filter,
attach modal, sharing modals, "Réviser ce dossier", stats link — all still reachable and
functional from within a real binder.

- [ ] **Step 4: Tear down the environment**

- [ ] **Step 5: Update chantier tracking**

`workflow/bibliotheque-redesign/PLAN.md`/`JOURNAL.md`, `workflow/JOURNAL.md` — append, per this
project's established convention (see `reviser-hub`'s precedent).

- [ ] **Step 6: Commit**

```bash
git add workflow/bibliotheque-redesign/PLAN.md workflow/bibliotheque-redesign/JOURNAL.md workflow/JOURNAL.md
git commit -m "docs(bibliotheque): verification visuelle contre les vraies maquettes, chantier pret a cloturer"
```

Then follow the `gestion-chantier` skill's closing procedure (ask the user to push, open the
PR, wait for CI, merge) — same as any other chantier close-out.
