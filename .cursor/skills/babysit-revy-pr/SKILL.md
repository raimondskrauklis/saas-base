---
name: babysit-revy-pr
description: >-
  Poll Revy PR check until idle (120s), fetch revybot comments, fix valid
  findings, local Bugbot until clean, commit and push, loop until solved. Use
  when user says babysit revy, fix revy on pr, revy poll loop, or /babysit-revy-pr.
---

# Babysit Revy PR

Post-push loop for **Revy** on our PRs. Gates on the **Revy** GitHub check and `revybot` comments.

**Ship gate:** [ship-changes](../ship-changes/SKILL.md) · **Orchestration:** [docs/agents/ORCHESTRATION.md](../../../docs/agents/ORCHESTRATION.md)

**Config:** `.agent/manifest.json` → `test_commands`, `integrations`, program `scope` (SSOT: `.revy/review-context.json`).

**Not:** merge, CI triage, or push while Revy is running.

---

## Prerequisite

- **kp-platform:** Revy runs on PRs — invoke when user asks; no manifest flag required.
- **Revy product repos** (`integrations.revy: true`): same loop; see [code-review/product/revy/README.md](../../../code-review/product/revy/README.md).

If no Revy check row on the PR (app suspended), poll step is a no-op — still fetch comments and fix actionable items.

---

## When

- **In LOOP:** dedicated Revy execution phase in a batch-push program (`phase-execution` runs the `WHILE` from that file — primary path).
- **Ad hoc:** user says *babysit revy*, *fix revy on pr*, *revy poll loop*, `/babysit-revy-pr`, or gives a PR number/URL with Revy follow-up.

**Not** a substitute for local Bugbot before each commit in the LOOP. **Not** part of default one-shot `ship-changes` unless user asks.

---

## Outer loop (until solved)

Repeat until **no unresolved actionable Revy findings** remain **and** Revy check is idle (`pass` / `fail` / `skipping` / `neutral`):

```text
1. Resolve PR + branch (checkout head if needed)
2. Poll Revy idle (120s interval) — see below
3. Fetch Revy comments — see below
4. Triage → fix valid findings only
5. Lint + tests per manifest test_commands and program scope
6. Local Bugbot (review-bugbot) until clean
7. Commit + push (feature branch only; Revy idle first)
8. Go to step 2 (Revy re-runs after push)
```

**Solved:** no open `revybot` inline threads/comments requiring code changes, Revy idle, local Bugbot clean.

**Stop early (report):** Revy suspended (no check row), user says stop, or only non-actionable INFO with explicit skip rationale.

---

## Step 2 — Poll Revy idle (120s)

**Poll interval:** `120` seconds between status checks.

```bash
PR=$(gh pr view --json number -q .number)
gh pr checks "$PR" 2>&1 | grep -iE 'revy|Revy'
```

| Revy status | Action |
|-------------|--------|
| `pending` / `in_progress` / `queued` | Sleep 120s, poll again |
| `pass` / `fail` / `skipping` / `neutral` | **Idle** — fetch comments |
| No `Revy` row | Idle (app suspended) — fetch comments anyway |

Use `sleep 120` (Shell) between polls. Do not push during `pending` / `in_progress` / `queued`.

---

## Step 3 — Fetch Revy comments

**Prefer GraphQL** (thread resolved/outdated):

```bash
OWNER=$(gh repo view --json owner -q .owner.login)
NAME=$(gh repo view --json name -q .name)
PR=$(gh pr view --json number -q .number)

gh api graphql -f query='
query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100) {
        nodes {
          isResolved
          isOutdated
          comments(first: 20) {
            nodes { author { login } body path line originalLine }
          }
        }
      }
    }
  }
}' -f owner="$OWNER" -f name="$NAME" -F number="$PR"
```

**REST fallback** (inline review comments):

```bash
gh api "repos/$OWNER/$NAME/pulls/$PR/comments" \
  --jq '.[] | select(.user.login|test("revy";"i")) | {path, line, body}'
```

**Issue comments** (check summary / narrative):

```bash
gh pr view "$PR" --comments
gh api "repos/$OWNER/$NAME/issues/$PR/comments" \
  --jq '.[] | select(.user.login|test("revy";"i")) | {body}'
```

Filter: `author.login` matches `revy`, `revybot`, `revybot[bot]`; skip `isResolved` / outdated threads unless user asks to reopen.

---

## Step 4–7 — Fix, gate, ship

| Step | Rule |
|------|------|
| Triage | Fix valid bugs and pack anti-patterns on **touched files** (even unchanged lines). Skip file-wide restyle / ~150-line nits (state why). Prefer minimal diff. |
| Lint | Per manifest `test_commands` — e.g. `backend_lint_fix` then `backend_lint`; `frontend_lint` when TS/TSX touched |
| Tests | Targeted pytest / Vitest for touched modules; `backend_test` / `frontend_test` for broad regressions per scope |
| Bugbot | Invoke **`review-bugbot`** on `uncommitted changes`; [VALIDATE → CLOSE](../../../docs/agents/prompts/OUTPUT_FORMAT.md); fix blockers; re-run until clean |
| Commit | Plain message — no `--trailer`, no `Co-authored-by: Cursor` — e.g. `fix(line-count): address Revy findings on PR #<n>` |
| Push | Feature branch only; **never** while Revy `pending` / `in_progress` / `queued` — see [ship-changes Revy gate](../ship-changes/SKILL.md#revy-gate-before-push) |

After push, **always** re-enter poll loop (step 2) before declaring done.

---

## Output

Per iteration, short table:

| Severity | Location | Finding | Action |
|----------|----------|---------|--------|
| … | `path:line` | one line | fixed / skipped / pending Revy |

Final line: PR URL, last commit sha, Revy check status, open thread count.

---

## Do not

- Push while Revy is running.
- Commit on `main` / `master` / default prod branch.
- Push with open local Bugbot blockers.
- Empty commit unless re-triggering Revy after idle with no code changes (rare — see ship-changes).
