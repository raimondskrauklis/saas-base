# P5 — Revy review (execution)

Phase **P5** of [`MINI_SAAS_GENERAL_PLAN.md`](./MINI_SAAS_GENERAL_PLAN.md). Baseline: [`MINI_SAAS_FINDINGS.md`](./MINI_SAAS_FINDINGS.md). **P5 only.**

**Goal:** PR findings on this program are idle or fixed.

**Push:** batch

Do not ask Continue?. After each Deliverable, next heading. After the ship gate, open Next immediately.

## Decisions locked for P5

- Q1–Q22 stay locked. Do not “fix” Revy by reopening dual-write, live SMTP, realm JSON, or irbene_gate copy.
- Fetch **all** unresolved comments including outdated. Skip obsolete with a one-line note.
- Never push while Revy is `pending` / `in_progress` / `queued`. Never force-push.

## Out of scope for P5

- New features
- Tag `saas-base-v3` / gap table / doc sync → **P6**
- irbene_gate copy

## P5.1 — Poll Revy idle

**What:** On the implementation PR opened at P1, poll until Revy is not pending/in_progress/queued. Do not push while waiting.
**Files:** none unless a check is stuck (then record in chat; do not skip)
**Deliverable:** `gh pr checks <PR> 2>&1 | grep -iE 'revy|Revy'` shows a completed conclusion (not pending)

## P5.2 — Fetch all Revy comments

**What:** `gh pr view` + `gh api` review comments paginated, including outdated / unresolved, not only Files-changed.
**Files:** none
**Deliverable:** comment list captured; each line marked apply / skip-obsolete

## P5.3 — Fix what still applies

**What:** Fix comments that still apply to HEAD and do not contradict Q1–Q22. Lint + phase-relevant tests for files touched.
**Files:** whatever Revy still flags on HEAD
**Deliverable:** `cd backend && pipenv run pytest tests/unit/test_admin_users.py tests/unit/test_keycloak_admin.py -q; cd frontend && npm test -- --run AdminUsersPage UserDetailPage AdminDashboardPage`

## P5.4 — Re-fetch and Bugbot

**What:** Re-fetch comments once. If new actionable arrived, fix then re-lint. Local Bugbot until CLOSE.
**Files:** as needed
**Deliverable:** second fetch has no new actionable; Bugbot CLOSE

**Phase gate:**

```bash
gh pr checks <PR> 2>&1 | grep -iE 'revy|Revy'
cd backend && pipenv run ruff check --fix . && pipenv run ruff check .
cd frontend && npm run lint
```

Revy conclusion must not be pending/in_progress/queued.

## LOOP ship gate

Do not ask Continue?. After this gate, open the Next file immediately.
Pause LOOP only if a subphase above said Pause LOOP (migration).

1. Branch — not main (`feat/mini-saas`)
2. Lint (from backend/: `pipenv run ruff check --fix . && pipenv run ruff check .`; from frontend/: `npm run lint`) — skip a tree only if this phase did not touch it
3. Phase gate above — green
4. Bugbot:
REPEAT until Bugbot CLOSE:
  1. Invoke review-bugbot (run_in_background: false)
  2. Diff: uncommitted changes
  3. Custom Instructions: VERB FIND + this phase locked decisions + .cursor/BUGBOT.md
  4. Fix blockers; re-lint if code changed
END REPEAT
5. Commit: feat(mini-saas): P5 Revy review
   If there is nothing to commit, do not create an empty commit; still run tails 6–9.
6. Fetch Revy first (comments from the P1 PR — include outdated / unresolved, not only Files-changed):
REPEAT until Revy status is NOT pending/in_progress/queued:
  gh pr checks <PR> 2>&1 | grep -iE 'revy|Revy' || true
  IF pending/in_progress/queued: poll again (do not push, do not ask)
END REPEAT
   gh pr view <PR> --comments
   gh api repos/<owner>/<repo>/pulls/<PR>/comments --paginate --jq '.[] | select(.user.login|test("revy";"i"))'
   Fix what still applies to current HEAD. Skip obsolete with a one-line note. Lint + Bugbot CLOSE. Commit Revy fixes.
   Re-fetch comments once. If new actionable arrived: fix → lint + Bugbot CLOSE → commit (still the same upcoming push).
7. One push: Revy fixes + this phase + any unpushed local commits. Never force-push. Never push while Revy is pending. If working tree is clean and branch is already pushed, skip the no-op push.
8. After push, Revy reviews the combined tip (new cycle — required if a push happened):
WHILE actionable Revy comments OR Revy running after push:
  fetch → fix → lint + gate → Bugbot until CLOSE → poll idle → commit → push → poll
END WHILE
9. Open Next immediately.

**Next:** [`MINI_SAAS_P6_EXECUTION.md`](./MINI_SAAS_P6_EXECUTION.md)
