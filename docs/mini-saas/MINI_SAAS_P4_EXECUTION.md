# P4 — Admin users UI (execution)

Phase **P4** of [`MINI_SAAS_GENERAL_PLAN.md`](./MINI_SAAS_GENERAL_PLAN.md). Baseline: [`MINI_SAAS_FINDINGS.md`](./MINI_SAAS_FINDINGS.md). **P4 only.** Last implementation phase.

**Goal:** `/admin/users` is a directory (filter, search, load-more); detail route with impersonate CTA and send-password-reset; dashboard shows `users_suspended`.

**Push:** batch

Do not ask Continue?. After each Deliverable, next heading. After the ship gate, open Next immediately.

## Decisions locked for P4

- Model on `WorkspacesPage.tsx` (`QuietInput`, `QuietSelect`, load-more). EN+LV `t()`. `--app-*` only.
- Approve/reject only on `pending_approval` rows. Password-reset button calls `POST /api/v1/admin/users/{id}/send-password-reset` (fail closed, no silent skip).
- Q11: `users_suspended` card + i18n on `AdminDashboardPage` in the same grid as `users_pending_approval`.
- Q7: detail `/admin/users/:userId`; impersonate CTA uses existing W7 modal/rules; hide when not `impersonate_allowed`.
- Q4: drop `GET /pending` once FE uses the new list. No unused alias.
- No in-app password/email edit. Do not merge with `/settings/team`.

## Out of scope for P4

- Live SMTP / realm clicks → **Q20**
- Revy drain beyond this file’s batch gate → leftover comments **P5**
- Tag `saas-base-v3` → **P6**

## P4.1 — Directory page

**What:** Replace queue-only `AdminUsersPage` with cursor directory: status filter, search, load-more. Client calls `GET /api/v1/admin/users`. Approve/reject stay on pending rows. Update `AdminUsersPage.test.tsx` (stop `fetchPendingUsers`).
**Files:** `frontend/src/features/admin/pages/AdminUsersPage.tsx`, `frontend/src/features/admin/api.ts`, `frontend/src/features/admin/pages/AdminUsersPage.test.tsx`, `frontend/src/features/admin/components/PendingUsersTable.tsx` (delete if unused), `frontend/src/i18n/locales/en.json`, `frontend/src/i18n/locales/lv.json`
**Deliverable:** `cd frontend && npm test -- --run AdminUsersPage`

## P4.2 — Detail, impersonate, password-reset

**What:** Route `/admin/users/:userId` next to `workspaces/:workspaceId`. Show memberships; impersonate CTA when `impersonate_allowed`; send-password-reset button → P3 POST. EN+LV. Fail closed (toast, no silent skip).
**Files:** `frontend/src/features/admin/routes.tsx`, `frontend/src/features/admin/pages/UserDetailPage.tsx` (new), `frontend/src/features/admin/pages/UserDetailPage.test.tsx` (new), `frontend/src/features/admin/api.ts`, `frontend/src/i18n/locales/en.json`, `frontend/src/i18n/locales/lv.json`
**Deliverable:** `cd frontend && npm test -- --run UserDetailPage`

## P4.3 — Dashboard `users_suspended` card

**What:** Add KPI card + EN/LV keys. Extend `AdminKpis` type and `AdminDashboardPage.test.tsx` mocks with `users_suspended`.
**Files:** `frontend/src/features/admin/pages/AdminDashboardPage.tsx`, `frontend/src/features/admin/pages/AdminDashboardPage.test.tsx`, `frontend/src/features/admin/api.ts`, `frontend/src/i18n/locales/en.json`, `frontend/src/i18n/locales/lv.json`
**Deliverable:** `cd frontend && npm test -- --run AdminDashboardPage`

## P4.4 — Drop `GET /pending`

**What:** Remove `GET /api/v1/admin/users/pending`, `list_pending_users`, and FE `fetchPendingUsers`. Directory `?status=pending_approval` is the Mode B queue. Keep UUID `GET /{user_id}` and approve/reject POSTs.
**Files:** `backend/app/api/v1/admin/users.py`, `backend/app/services/users.py`, `backend/tests/unit/test_admin_users.py`, `frontend/src/features/admin/api.ts`
**Deliverable:** `cd backend && pipenv run pytest tests/unit/test_admin_users.py tests/api/test_admin_users.py -q; rg -n 'users/pending|list_pending_users|fetchPendingUsers' backend frontend; test $? -eq 1`

**Phase gate:**

```bash
cd backend && pipenv run ruff check --fix . && pipenv run ruff check . && pipenv run pytest tests/unit/test_admin_users.py tests/unit/test_admin_kpis.py tests/api/test_admin_users.py -q
cd frontend && npm run lint && npm test -- --run AdminUsersPage UserDetailPage AdminDashboardPage
rg -n 'users/pending|list_pending_users|fetchPendingUsers' backend frontend; test $? -eq 1
```

## LOOP ship gate

Do not ask Continue?. After this gate, open the Next file immediately.
Pause LOOP only if a subphase above said Pause LOOP (migration).

1. Branch — not main (`feat/mini-saas`)
2. Lint (from backend/: `pipenv run ruff check --fix . && pipenv run ruff check .`; from frontend/: `npm run lint`)
3. Phase gate above — green
4. Bugbot:
REPEAT until Bugbot CLOSE:
  1. Invoke review-bugbot (run_in_background: false)
  2. Diff: uncommitted changes
  3. Custom Instructions: VERB FIND + this phase locked decisions + .cursor/BUGBOT.md
  4. Fix blockers; re-lint if code changed
END REPEAT
5. Commit: feat(mini-saas): P4 admin users directory UI
6. Fetch Revy first (comments from the P1 PR — include outdated / unresolved, not only Files-changed):
REPEAT until Revy status is NOT pending/in_progress/queued:
  gh pr checks <PR> 2>&1 | grep -iE 'revy|Revy' || true
  IF pending/in_progress/queued: poll again (do not push, do not ask)
END REPEAT
   gh pr view <PR> --comments
   gh api repos/<owner>/<repo>/pulls/<PR>/comments --paginate --jq '.[] | select(.user.login|test("revy";"i"))'
   Fix what still applies to current HEAD. Skip obsolete with a one-line note. Lint + Bugbot CLOSE. Commit Revy fixes.
   Re-fetch comments once. If new actionable arrived: fix → lint + Bugbot CLOSE → commit (still the same upcoming push).
7. One push: Revy fixes + this phase + any unpushed local commits. Never force-push. Never push while Revy is pending.
8. After push, Revy reviews the combined tip (new cycle — required):
WHILE actionable Revy comments OR Revy running after push:
  fetch → fix → lint + gate → Bugbot until CLOSE → poll idle → commit → push → poll
END WHILE
9. Open Next immediately.

**Next:** [`MINI_SAAS_P5_EXECUTION.md`](./MINI_SAAS_P5_EXECUTION.md)
