---
name: ship-changes
description: >-
  Ship finished work: Bugbot on uncommitted changes, feature branch if needed,
  commit, then push/PR only when hosting allows. Use when the user says ship,
  commit and pr, push and open pr, or after an agent stopped with uncommitted fixes.
---

# Ship changes

**When:** work is done — user says *ship*, *commit and pr*, *bugbot commit push*, or agent stopped mid-task.

**Config:** `.agent/manifest.json` — `test_commands`, `hosting`, `integrations`, active program `scope`.

**Not:** merge, deploy, or default-branch commits.

---

## Steps

1. **Branch** — forbidden on `main` / `master` / default prod branch.
   - On forbidden branch → `git checkout -b feat/<short-topic>` (keep uncommitted work).
   - Else stay on current feature branch.
2. **Checks** — lint/tests for touched areas per manifest `test_commands` and program `scope`.
3. **Local Bugbot** — invoke **`review-bugbot`** on `uncommitted changes` (or `branch changes`). Fix blockers. **Do not commit if blockers remain.**
4. **Commit** — if there are uncommitted changes: `git add` relevant files; plain `git commit -m "…"` — **no** `Co-authored-by: Cursor`. If the tree is already clean, skip (no empty commit).
5. **Push / PR** — follow the active execution file’s **Push:** kind, or ad-hoc rules below. Honour `hosting.kind`.

### Push kinds

| Kind | GitHub | No GitHub / no remote |
|------|--------|------------------------|
| `local` | stop after commit | same |
| `first-push` | push; open PR (`gh pr create`) unless **no pr** | `git push` only if a remote exists |
| `batch` | never push while Revy is `pending`; fetch comments; fix; one push | `git push` if remote exists; skip `gh` / Revy |

**Ad-hoc** (no LOOP file): first push on a new branch = `first-push`. Later push on an open PR = `batch`. User **no pr** / **local only** → stop after commit.

Never force-push.

**Output:** branch, commit sha, PR URL or remote tracking status (or “local only”).

---

## Revy gate (GitHub only)

Skip this entire section unless `hosting.kind = github` and Revy runs on the PR (or `integrations.revy: true`).

```bash
gh pr checks <PR_NUMBER> 2>&1 | grep -iE 'revy|Revy'
```

| Revy check status | Action |
|-------------------|--------|
| `pending` / `in_progress` / `queued` | **Do not push.** Poll until settled. |
| `pass` / `fail` / `skipping` / `neutral` / no Revy row | Safe to push (if other gates green). |

**Batch:** idle → fetch unresolved `revybot` comments → fix → Bugbot CLOSE → commit → **one push**.

Dedicated poll loop: `babysit-revy-pr` when that skill is installed and the user asks.

---

## PR title pattern (GitHub)

```text
<type>(<program-slug>): <primary outcome in plain English>
```

Phase labels (`P0`–`P6`) belong on **commits**, not as the PR title alone. Skip this section when there is no PR.
