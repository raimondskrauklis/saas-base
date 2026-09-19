---
name: execution-peer-review
description: >-
  Peer-review execution plan files one phase at a time (P0, P1, …) against the
  codebase, findings, and general plan. Writes findings to plan-folder/reviews/
  for iterative fix-and-re-review. Read-only on execution files. Use before
  phase-execution or after a fix pass on execution plans.
---

# Execution peer review

Read-only review of **per-phase execution files** before `phase-execution`. **Not** a bulk skim — review **one file, report, then next file**.

**Sibling:** `architecture-peer-review` — single plan/spec doc. Use that for findings or general plan only; use **this skill** for the execution file set.

**Forbidden:** edit execution files, general plan, or findings; fix gaps; run `phase-execution`; create commits.

**Allowed:** create or update files under `<plan-folder>/reviews/execution-peer-review/` only.

---

## Entry

User attaches:

- **Plan folder** (preferred), or
- **`README.md`** with execution table, or
- A single execution file (review that file only).

Optional user hints:

- **Re-review / pass 2+** — after a fix agent updated execution files.
- **Delta only** — re-review only phases listed by user or changed since last pass (see Re-review modes).

Discover the ordered file list from **`README.md` execution table** (same as `phase-execution`). If no README, glob `*EXECUTION*.md` in folder and sort by phase id.

Announce once in chat: plan folder, phase count, file list, LOOP order, **pass number**.

**Optional baseline read (once, before P0):** `*_FINDINGS.md`, `*_GENERAL_PLAN.md` — for locked decisions and phase goals. Do **not** read all execution files upfront.

---

## Review artifact (required)

All findings go to disk — chat is a **short summary + link**, not the SSOT.

### Layout

```
<plan-folder>/
  reviews/
    execution-peer-review/
      README.md              ← pass index (create on first pass)
      pass-01-YYYY-MM-DD.md  ← one file per full review pass
      pass-02-YYYY-MM-DD.md
```

**Plan folder examples:** `documents/line-count-hardening/wave-2/`, `docs/agents/foo/`.

### Pass file naming

- First pass: `pass-01-YYYY-MM-DD.md` (today’s date, UTC or user locale).
- Each **full** re-review: **new** file, increment pass (`pass-02-…`). Never overwrite a prior pass file.
- **Delta** re-review: append section `## Delta re-review` to the **latest** pass file **or** create `pass-NN-YYYY-MM-DD-delta.md` if the delta is large — prefer new delta file when >3 phases change.

### `README.md` index (update every pass)

| Pass | File | Date | Scope | Critical | High | Block LOOP |
|------|------|------|-------|----------|------|------------|
| 1 | [pass-01-…](./pass-01-2026-08-02.md) | 2026-08-02 | P0–P17 full | 0 | 8 | no |

Link to plan folder README execution table. Status line: `Latest pass: N — BLOCK phase-execution: yes/no`.

### Pass file header (required)

```markdown
# Execution peer review — pass N

**Plan folder:** `documents/…/wave-2/`  
**Date:** YYYY-MM-DD  
**Scope:** full | delta (Pn, Pm, …)  
**Reviewer:** execution-peer-review skill  
**Baseline:** findings + general plan + codebase paths cited below  

## Verdict

Review complete: N files, X critical, Y high, Z medium/low.  
**BLOCK phase-execution:** yes/no — one-line reason.

## Prior pass

Link to pass N-1 if re-review; note what the fix agent was asked to address.

## Per-phase findings

…
```

### Chat response (after writing files)

1. One sentence: pass number, scope, BLOCK yes/no.
2. **Link** to the pass file (relative path from repo root).
3. Link to `reviews/execution-peer-review/README.md` index.
4. List **critical/high** titles only (no full tables in chat).
5. If BLOCK: what must be fixed before `phase-execution`; suggest fix agent reads pass file.

---

## Re-review modes

| Mode | When | What to read | Output |
|------|------|--------------|--------|
| **Full** | First review, or user says “full re-review” | Every execution file in LOOP order | New `pass-NN-…md` |
| **Delta** | User says “re-review after fixes” + optional phase list | Only changed execution files + prior pass file for carry-forward | Delta section or `pass-NN-…-delta.md` |
| **Spot** | User names one phase | That execution file only | Add subsection under latest pass or small delta file |

**Delta rules:**

- Re-read **prior pass** findings for scoped phases; mark each prior finding **resolved / open / new**.
- Do not re-copy unchanged clean phases verbatim — one line `**Pn — no new gaps** (verified unchanged).`
- If a “fixed” item is still broken, escalate severity.

**Iteration loop (typical):**

```
create-execution-plan → execution-peer-review (pass 1)
  → fix agent (edits execution files per pass-01)
  → execution-peer-review (pass 2, delta or full)
  → … until BLOCK: no → phase-execution
```

---

## One file at a time (strict)

For **each** execution file in scope:

1. **Read only this execution file** (+ grep/read **repo paths cited in this file**).
2. Cross-check **this phase** against:
   - Matching **general plan** `## Pn` block
   - **Findings** locked decisions
   - **`create-execution-plan` contract** (checklist below)
   - **Prior phases** only via what *this file* claims
3. **Append findings to the pass file** (per-file template below) — do not wait until end.
4. **Then** open the next execution file.

If a file is clean: `**Pn — no gaps found.**` + one line verified.

---

## Per-file output template

```markdown
## Pn — `<relative/path/to/FILE.md>`

| Severity | Area | Finding |
|:---|:---|:---|
| critical | codebase | … |
| high | general plan | … |
| medium | execution contract | … |
| low | clarity | … |

**Verified OK:** (1–3 bullets)
```

**Severity:** critical = wrong behavior / rework if implemented; high = contradicts findings or general plan; medium = missing gate, vague deliverable, scope leak; low = wording.

**Questions:** only if blocking — max 1–2 per file; put in pass file §Open questions.

---

## Execution contract checklist (per file)

| Check | |
|:---|:---|
| Header links general plan + findings | |
| **Goal** + **decisions locked** for this phase | |
| **Out of scope** lists later phases | |
| **3–6 subphases** (flag if >8) | |
| Each subphase: `**What**` / `**Files**` / `**Deliverable**` — **no** `**Stop:**` / “do not start Pn+1” (except `Pause LOOP` on a migration subphase) | |
| **Deliverable** includes verify command or concrete assertion | |
| **Phase gate** — copy-paste `pytest` / `npm test` block | |
| **`LOOP ship gate` inlined** — full Bugbot REPEAT (not “run Bugbot”); not “see README” / “see skill” | |
| **Bugbot** — `REPEAT until CLOSE` in this file | |
| **Push policy** — header `Push:` is `local` / `first-push` / `batch`; ship gate matches; P0 local; P1 first-push; last is batch | |
| **Revy** — `first-push` does not drain comments; `batch` fetches **before** push + WHILE after | |
| **P0.0** — `rule_packs` + pack `paths[]` (`description: "rules"`) match `scope`; `rule_packs_catalog` kept; Bugbot three program docs only | |
| **Migration** subphase flagged + handwritten-only + Pause LOOP if Alembic | |
| **Human gate** if spike/ops/sign-off | |
| **Next** → following execution file | |
| No TBD / no open options / no “choose A or B” | |
| FE phase has frontend gate when `frontend/` touched | |
| **Closeout** — last file is `batch` with gap table + doc sync + `active_program` clear, unless general plan already split Revy/doc/gap | |

---

## Codebase verification (per file)

- Paths in **Files** exist (or correctly named new files).
- Migrations: revision chain plausible; no `--autogenerate` assumed.
- APIs, services, models, hooks, components match real names.
- Test paths in **Deliverable** / phase gate exist or named **new** in subphase.
- Flag stale line numbers, renamed symbols, wrong module paths.

Mark **verified** (with path) vs **assumption** if not read.

---

## After last file

Finish pass file **Verdict** + rollup table of critical/high. Update `reviews/execution-peer-review/README.md`.

---

## Anti-patterns

- Dump full per-phase tables in chat instead of the pass file.
- Read all `*_EXECUTION.md` files, then one combined gap list.
- Skip a phase because “similar to P2”.
- Edit execution files to fix findings.
- Overwrite prior pass files.

**Invoke with:** plan folder README + “execution peer review” / “re-review pass 2 after fixes” / “delta review P1 P4”.
