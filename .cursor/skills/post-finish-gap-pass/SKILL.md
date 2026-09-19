---
name: post-finish-gap-pass
description: >-
  Mandatory closeout: re-read plan vs shipped code, fix gaps or open follow-up
  phase, sync platform docs. Use as P5 execution phase after Revy review loop —
  not optional.
---

# Post-finish gap pass

**When:** dedicated **gap-closeout execution phase** — **after** implementation and **after** Revy review loop. Platform doc sync may be the **immediately prior** execution phase (recommended for multi-phase programs).

**Not:** full plan review (`execution-peer-review`) or stress-test (`devils-advocate`).

**Shipped as:** `*_GAP_CLOSEOUT_EXECUTION.md` or final `*_Pn_EXECUTION.md` — see `create-execution-plan` § Closeout.

---

## End-to-end closeout order (recommended)

```text
last impl phase (batch push)
  → Revy execution phase (WHILE babysit)
  → doc sync execution phase (| Doc | Change |)
  → gap closeout execution phase (this skill)
  → human merge
```

**Why gap last:** doc sync updates paths and status; gap pass verifies plan + findings + docs against shipped code in one pass. Revy must finish before doc sync so docs describe merged-ready code.

**Small programs:** gap + doc sync may share one execution file (subphases Pn.1–Pn.5 in `create-execution-plan`).

---

## Steps

1. Re-read `*_GENERAL_PLAN.md` + `*_FINDINGS.md` + all `*_P*_EXECUTION.md` vs **shipped code** (branch diff / PR).
2. Grep code + plan folder — drift, skipped deliverables, corners cut, LOC targets missed.
3. `| Gap | Severity | Action |` — fix **in-scope** now; if too large → add **P5.x fix subphase** or defer with README note (human approves defer).
4. **Platform doc sync** — if not done in prior execution phase: grep `docs/`, `corpus/`, `AGENTS.md`; update paths and architecture refs. When doc sync is its own phase (P7-style), gap phase only verifies doc phase completed and fixes doc-code contradictions.
5. **Operator doc sync** — execution README status, TARGETS PR log, scan reports, findings status.
6. Lint → full phase/wave gate → local Bugbot → Revy idle → push.
7. Clear `active_program` → `null`; human merge.

Skip only if program is doc-only with no code ship.

**Deliverable in execution file:** `| Doc | Change |` table + gap table (even when empty: “no gaps”).
