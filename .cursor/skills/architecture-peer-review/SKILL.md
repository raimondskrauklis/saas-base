---
name: architecture-peer-review
description: >-
  After an architecture or implementation plan is drafted, perform a careful
  peer review against the real codebase. Use when cross-checking a single
  findings, general, or design doc. For per-phase execution file sets, use
  execution-peer-review instead. Writes findings to plan-folder/reviews/
  architecture-peer-review/ — chat is summary + link only.
---

# Architecture peer review

Read-only review of **one** baseline doc set (findings + general plan, or a standalone design spec). **Not** for per-phase execution files — use **`execution-peer-review`** (reviews P0…Pn **one file at a time** with per-file gap tables).

**Forbidden:** edit findings, general plan, or execution files; fix gaps; run `phase-execution`; create commits.

**Allowed:** create or update files under `<plan-folder>/reviews/architecture-peer-review/` only.

**Sibling:** `execution-peer-review` — execution file set after `create-execution-plan`.

---

## Entry

User attaches:

- **Plan folder** (preferred), or
- **General plan** / findings / design doc path(s).

Optional user hints:

- **Re-review / pass 2+** — after a fix agent updated findings or general plan.
- **Delta only** — re-review only sections the user lists or that changed since last pass.

Discover baseline paths:

- `*_FINDINGS.md` in plan folder (if present)
- `*_GENERAL_PLAN.md` under `general/` or plan folder
- Linked design docs cited in the plan header

Announce once in chat: plan folder, docs reviewed, pass number.

**Do not** read execution files unless the user explicitly asks to cross-check execution against general plan (that is `execution-peer-review`).

---

## Review artifact (required)

All findings go to disk — chat is a **short summary + link**, not the SSOT.

### Layout

```
<plan-folder>/
  reviews/
    architecture-peer-review/
      README.md              ← pass index (create on first pass)
      pass-01-YYYY-MM-DD.md  ← one file per full review pass
      pass-02-YYYY-MM-DD.md
```

**Plan folder examples:** `docs/utils/line-count-review/calculators/market_calculator/`, `docs/agents/foo/`.

### Pass file naming

- First pass: `pass-01-YYYY-MM-DD.md` (today’s date, UTC or user locale).
- Each **full** re-review: **new** file, increment pass (`pass-02-…`). Never overwrite a prior pass file.
- **Delta** re-review: append `## Delta re-review` to the **latest** pass file **or** create `pass-NN-YYYY-MM-DD-delta.md` if the delta is large.

### `README.md` index (update every pass)

| Pass | File | Date | Scope | Critical | High | Block next step |
|------|------|------|-------|----------|------|-----------------|
| 1 | [pass-01-…](./pass-01-2026-08-02.md) | 2026-08-02 | findings + general | 0 | 4 | no |

Link to findings + general plan. Status line: `Latest pass: N — BLOCK create-execution-plan: yes/no` (or other named next step).

### Pass file header (required)

```markdown
# Architecture peer review — pass N

**Plan folder:** `docs/…/market_calculator/`  
**Date:** YYYY-MM-DD  
**Scope:** full | delta (sections …)  
**Reviewer:** architecture-peer-review skill  
**Baseline:** [FINDINGS.md](…), [GENERAL_PLAN.md](…), codebase paths cited below  

## Verdict

Review complete: X critical, Y high, Z medium/low.  
**BLOCK create-execution-plan:** yes/no — one-line reason.

## Prior pass

Link to pass N-1 if re-review; note what the fix agent was asked to address.

## Rollup (critical / high)

| Severity | Section | Title |
|:---|:---|:---|

## Per-section findings

…
```

### Chat response (after writing files)

1. One sentence: pass number, scope, BLOCK yes/no.
2. **Link** to the pass file (relative path from repo root).
3. Link to `reviews/architecture-peer-review/README.md` index.
4. List **critical/high** titles only (no full tables in chat).
5. If BLOCK: what must be fixed before `create-execution-plan`; suggest fix agent reads pass file.

---

## Re-review modes

| Mode | When | What to read | Output |
|------|------|--------------|--------|
| **Full** | First review, or user says “full re-review” | Findings + general plan (+ linked specs) | New `pass-NN-…md` |
| **Delta** | User says “re-review after fixes” | Changed sections + prior pass | Delta section or new delta file |
| **Spot** | User names one general-plan phase | That `## Pn` block only | Subsection under latest pass |

**Delta rules:**

- Re-read prior pass findings for scoped sections; mark each **resolved / open / new**.
- Do not re-copy unchanged clean sections verbatim — one line `**Pn — no new gaps** (verified unchanged).`
- If a “fixed” item is still broken, escalate severity.

**Iteration loop (typical):**

```
create-findings → create-general-plan → architecture-peer-review (pass 1)
  → fix agent (edits findings / general plan per pass-01)
  → architecture-peer-review (pass 2, delta or full)
  → … until BLOCK: no → create-execution-plan → execution-peer-review
```

---

## Review workflow

1. Read findings (locked decisions, grep claims, test inventory).
2. Read general plan phase blocks (`## P0`, `## P1`, …) in order.
3. For **each phase block**, grep/read **repo paths cited** (monolith, consumers, precedent wave, tests).
4. Cross-check against:
   - Findings locked table and decisions registry
   - Precedent wave general plan + shipped package (e.g. W3 `price/`)
   - Real import consumers, LOC, dispatch maps, stub metadata
5. **Append findings to the pass file** (per-section template below).
6. Finish verdict + rollup; update `reviews/architecture-peer-review/README.md`.

Mark **verified** (with path) vs **assumption** if not read.

**Questions:** only if blocking — collect in pass file `## Open questions` (max 3).

---

## Per-section output template

Use general-plan phase ids (`P0.0`, `P0`, `P1`, …) or spec section headings.

```markdown
## Pn — (phase title from general plan)

| Severity | Area | Finding |
|:---|:---|:---|
| critical | codebase | … |
| high | general plan | … |
| medium | findings | … |
| low | clarity | … |

**Verified OK:** (1–3 bullets)
```

**Severity:** critical = wrong behavior / rework if implemented; high = contradicts findings or precedent wave; medium = missing gate, vague deliverable, execution-contract gap; low = wording.

**Cross-cutting section:** locked decisions table parity, wave gate commands, push strategy, `active_program` slug.

---

## General-plan contract checklist

| Check | |
|:---|:---|
| Header links findings + calculator track / precedent PR | |
| Locked table matches findings (indicator set, CALC-02/03, stubs, public API) | |
| P0.0 before code — `active_program`, review-context paths, BUGBOT links | |
| P0 `_legacy` delegation + import alias if monolith class name collides | |
| P0 delegation smoke test before first push (stub indicator) | |
| Helper extraction phase names monolith↔`_helpers` transition (mirror precedent) | |
| DI / cross-feature consumers (`*_peer_resolver`, constant exports) — when imports switch | |
| Stub indicators move as-is (`not_implemented` metadata path) | |
| Large indicators single-module policy stated (SQL + verdict co-located) | |
| Delete monolith phase lists all import consumers (grep-verified) | |
| Calculator test floor before monolith delete | |
| P6 doc/corpus grep gate command inlined or linked with glob exclusions | |
| Push strategy + batch push phases explicit | |
| Wave gate pytest paths exist or named **new** | |
| No TBD / no open options in decisions table | |

---

## Codebase verification

- Monolith LOC and dispatch map match findings table.
- Precedent package layout exists (`price/`, `network/`, …).
- Import consumers from findings grep still accurate.
- Test files cited in findings — existence and whether they import the calculator class.
- `review-context.json` state vs planned `active_program`.
- Stale docs referencing old paths (flag for P6, not blocking).

---

## Anti-patterns

- Dump full per-section tables in chat instead of the pass file.
- Skim general plan without grep on cited backend paths.
- Edit findings or general plan to fix findings (report only).
- Overwrite prior pass files.
- Review execution files in bulk (use `execution-peer-review`).

**Invoke with:** plan folder + findings/general paths + “architecture peer review” / “re-review pass 2 after fixes”.
