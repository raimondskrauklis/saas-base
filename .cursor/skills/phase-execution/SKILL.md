---
name: phase-execution
description: >-
  Run a full execution-plan LOOP from a pointed start file or plan folder:
  implement every subphase, follow that file's ship gate, continue through all
  phases without pausing. Use when the user attaches a plan folder or execution
  file and invokes phase-execution.
---

# Phase execution (LOOP)

**Entry:** user attaches a **plan folder** or **start execution file**.

**Config:** `.agent/manifest.json` — `flows`, `hosting`, `integrations`, `test_commands`, `review_context`, `default_scope`.

Discover order from that folder’s **README execution table** (then `*_GENERAL_PLAN.md`, then glob `*EXECUTION*.md`). Run start phase through last unless the user narrows (`only P0`, `through P2`).

Announce once: files, order, Push kinds from the README, hosting kind.

---

## Rule

Read **only** the current `*_Pn_EXECUTION.md`. Do what it says. Do not substitute this skill, README, or chat history for the ship gate.

- Subphases in order. Deliverable green → next heading immediately.
- Then the file’s **LOOP ship gate** (Bugbot REPEAT, commit, push kind).
- Then open **Next**. Do **not** ask “Continue?”.
- **Pause** only if a subphase says **Pause LOOP** (migration) or the user scoped the run.

Not on `main` / `master`. `ship-changes` only when this file’s gate says push.

---

## Hosting

Read `hosting.kind`.

| Kind | `first-push` | `batch` |
|------|----------------|---------|
| `github` | push + `gh pr create` unless **no pr** | commit + push; skip external review bot unless configured |
| `none` / no remote | commit only (same as `local`) | same — do not invent GitHub |
| remote but not GitHub | `git push -u` if remote exists | `git push`; skip `gh` |

---

## P0.0 (always, first LOOP)

Wire review SSOT + `.cursor/BUGBOT.md` even if the file has no JSON blob.

- SSOT path from `manifest.review_context.ssot`
- One `programs[]` entry
- `rule_packs` only if the repo has a packs directory (`manifest.review_context.rule_packs`). Otherwise omit.
- Bugbot: three **program** docs (execution, findings, general plan)

---

## If a file is thin (legacy)

Use this cadence only when the file has no Push kind / no ship gate:

```text
P0 local commit (no push) → P1 first-push (if hosting allows)
→ mid phases local → last: batch (push when CI green)
```

Prefer fixing the execution file over improvising.

---

## Lint

Use `test_commands` from the consumer manifest for each changed scope glob. Never assume pipenv.

---

## Local Bugbot (hard gate)

Mandatory before **each** LOOP commit and every push.

1. Invoke `review-bugbot` (`run_in_background: false`).
2. `Diff: uncommitted changes` or `branch changes`.
3. Fix blockers; re-lint if code changed.
4. Do not commit with unresolved blockers.

---

## After the last file

Chat summary: SHAs, PR URL or remote (if any), `active_program` null if the last file required it.

**Invoke:** attach folder or file + `/phase-execution`. **no pr** skips GitHub PR even on `github`.
