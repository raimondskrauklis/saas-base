---
name: create-execution-plan
description: >-
  Write all per-phase execution plan files from a GENERAL_PLAN in one pass (or
  one phase when updating): README execution table, 3–6 subphases each, phase
  gates, self-contained LOOP ship gates. Use when creating execution docs from
  findings + general plan.
---

# Create Execution Plan

**Input:** findings + `*_GENERAL_PLAN.md` in a plan folder.

**Output (one session, no code):** one `*_Pn_EXECUTION.md` per general-plan phase + README execution table.

**Next step after full pass:** user attaches the folder + `execution-peer-review`, then `phase-execution`.

The executing agent reads **only that phase file**. If a step is not in the file, they will skip it. **Paste a full ship gate — never “follow phase-execution” or “run Bugbot until clean”.**

Read consumer `.agent/manifest.json` → `hosting` and `test_commands`. If `hosting.kind` is not `github`, paste ship-gate tails **without** `gh`: `first-push` and `batch` are `git push` when a remote exists, otherwise commit-only. Lint lines must use this repo's `test_commands`, not pipenv-by-default. P0.0 SSOT path is `manifest.review_context.ssot` (often `.agent/review-context.json`).

---

## Cadence (put this in the README Push column)

| Phase | `Push:` | What the ship gate must say |
|-------|---------|-----------------------------|
| P0 | `local` | Commit. Do not push. Open next file immediately. |
| P1 | `first-push` | Commit. Push (opens PR, includes P0). Revy starts. Do **not** drain comments. Open next file. |
| P2 … last-impl−1 | `local` | Commit. Do not push. Revy is running on the PR — leave it. |
| Last impl, or last file if small program (~P3–P6) | `batch` | Commit this phase. Poll Revy idle. **Fetch all unresolved comments (including outdated). Fix what still applies to HEAD. Re-fetch once. Then one push** (fixes + unpushed work). Then WHILE on the new tip. |

Do not invent a fourth kind. Do not open the PR on P0. Do not push every phase.

**Default closeout:** fold gap + doc sync into the **last** file (`Push: batch`). Write separate Revy / doc / gap files only when the general plan already lists them (large full-stack).

---

## Every execution file must contain

1. Header: goal, **`Push:`** `local` | `first-push` | `batch`, locked decisions, out of scope, **Next** link (or **none**).
2. Subphases (3–6): **What** / **Files** / **Deliverable** (exact test command). No `**Stop:**`. No open options.
3. P0.0 on P0 only: wire `manifest.review_context.ssot` + `.cursor/BUGBOT.md` (one `programs[]` entry). Set `rule_packs` from `scope` only if `manifest.review_context.rule_packs` is configured (any `backend/` path including tests → `platform`+`backend`; any `frontend/` path → `platform`+`frontend`; both → all three; neither → `[]`). List pack files on `paths[]` with `description: "rules"`. Keep `rule_packs_catalog`. Do not ask which packs. Bugbot stays three program docs.
4. Migration subphase: `hand-written only` + **`Pause LOOP` after this subphase** (only pause).
5. **Phase gate:** copy-paste pytest / npm.
6. **`## LOOP ship gate`:** paste **one** block below that matches `Push:`. Fill in commit message, test paths, Next file. Keep the REPEAT/WHILE text verbatim.

Also write: *Do not ask Continue?. After each Deliverable, next heading. After the ship gate, open Next immediately.*

---

## Ship gates — paste one per file

Shared prefix (every kind) — keep the REPEAT text:

```text
## LOOP ship gate

Do not ask Continue?. After this gate, open the Next file immediately.
Pause LOOP only if a subphase above said Pause LOOP (migration).

1. Branch — not main
2. Lint (from backend/: pipenv run ruff check --fix . && pipenv run ruff check .)
3. Phase gate above — green
4. Bugbot:
REPEAT until Bugbot CLOSE:
  1. Invoke review-bugbot (run_in_background: false)
  2. Diff: uncommitted changes
  3. Custom Instructions: VERB FIND + this phase locked decisions + .cursor/BUGBOT.md
  4. Fix blockers; re-lint if code changed
END REPEAT
5. Commit: feat(<program-slug>): P<n> <short goal>
```

Then **exactly one** tail:

### Tail `local`

```text
6. Do not push.
7. Update README status row.
8. Open Next immediately.
```

### Tail `first-push`

```text
6. No PR yet — skip Revy.
7. Push (opens PR; includes P0 commit). Title: feat(<program-slug>): <outcome, not "P1">. Use ship-changes **from Push onward** (already committed — do not commit again).
8. Confirm PR URL.
9. Open Next immediately.
```

### Tail `batch`

```text
6. Ensure CI/checks are green. Fix what still applies to current HEAD. Skip obsolete with a one-line note. Lint + Bugbot CLOSE. Commit fixes.
7. One push: fixes + this phase + any unpushed local commits. Never force-push.
8. After push, confirm checks pass.
9. Open Next immediately (or Next: none if this is the last file).
```

On the **last** file, add: clear `active_program` → `null` only after gap table has no fix-now rows. Keep `rule_packs_catalog`.

---

## Body template (not a ship gate)

```markdown
# docs/.../<TOPIC>_P0_EXECUTION.md

# P0 — <title> (execution)

Phase **P0** of [`<GENERAL_PLAN>.md`](./...). Baseline: [`<FINDINGS>.md`](./...). **P0 only.**

**Goal:** one line.
**Push:** local

## Decisions locked for P0
- locked bullets — no options

## Out of scope for P0
- item → **P1**

## P0.0 — Program PR review context
**What:** `.agent/review-context.json` + `.cursor/BUGBOT.md`. One `programs[]` entry. `rule_packs` only if the repo has a packs directory (`manifest.review_context.rule_packs`). Keep `rule_packs_catalog`. Bugbot: three program docs only. Do not ask which packs.
**Files:** those two paths
**Deliverable:** `python -m json.tool .agent/review-context.json`

Example (backend-only):

```json
{
  "active_program": "<slug>",
  "programs": [
    {
      "id": "<slug>",
      "scope": ["backend/**"],
      "rule_packs": ["platform", "backend"],
      "paths": [
        { "path": ".cursor/rules/platform.md", "description": "rules" },
        { "path": ".cursor/rules/backend.md", "description": "rules" },
        { "path": "docs/.../README.md", "description": "execution" },
        { "path": "docs/.../FINDINGS.md", "description": "findings" },
        { "path": "docs/.../GENERAL_PLAN.md", "description": "general plan" }
      ]
    }
  ],
  "rule_packs_catalog": {
    "platform": ".cursor/rules/platform.md",
    "backend": ".cursor/rules/backend.md",
    "frontend": ".cursor/rules/frontend.md"
  }
}
```

## P0.1 — …
**What:** … (repeat the locked decision that applies here)
**Files:** `backend/...`
**Deliverable:** `cd backend && pipenv run pytest tests/unit/... -q`

**Phase gate:** copy-paste pytest

## LOOP ship gate
<paste prefix + `local` tail>
**Next:** [`..._P1_EXECUTION.md`](./...)
```

---

## README

| Phase | File | Push | Status |
|:---|:---|:---|:---|
| P0 — … | link | local | pending |
| P1 — … | link | first-push | pending |
| P2 — … | link | local | pending |
| Pn — closeout | link | batch | pending |

Linear order for `phase-execution`. If the general plan allows parallel work, still pick one order.

**Size:** 3–6 subphases per file (max 8). One phase = one commit. Split the general plan if a phase would exceed that — do not write a 12-subphase file.

**Tests:** `tests/unit/` default. HTTP route/schema change → ≤3 `tests/api/` tests in that wave; else gap row `API smoke | N/A`.

---

## Last file (default closeout)

Subphases: gap table → optional code fixes → platform doc grep (`| Doc | Change |`) → operator README + `active_program` null (keep `rule_packs_catalog`). **Push: batch** (paste that tail, including WHILE).

Do not skip gap or doc sync.

---

## Do not

- One file for all phases
- Ship gate only in README / “same as P2” / “see skill”
- `**Stop:**` or “do not start P1”
- Peer-review or implement in this session
- Extra Revy/doc/gap files unless the general plan already has them

**Done when:** every general-plan phase has a file; README Push column matches headers; each ship gate has a real Bugbot REPEAT; P0 is local, P1 is first-push, last is batch.
