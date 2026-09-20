# P2 — Directory and detail APIs (execution)

Phase **P2** of [`MINI_SAAS_GENERAL_PLAN.md`](./MINI_SAAS_GENERAL_PLAN.md). Baseline: [`MINI_SAAS_FINDINGS.md`](./MINI_SAAS_FINDINGS.md). **P2 only.**

**Goal:** Super-admin cursor list + user detail, same contract as workspaces.

**Push:** local

Do not ask Continue?. After each Deliverable, next heading. After the ship gate, open Next immediately.

## Decisions locked for P2

- Q3: `require_super_admin()` + `require_impersonation_allowed()`.
- Q4 / Q12: `CursorParams`, `?status=`, `?search=` email/name ILIKE, order `created_at DESC, id DESC`. Default omit `deleted`. Keep `GET /pending` (drop in **P4**).
- Catalog B columns: `id`, `email`, `full_name`, `status`, `platform_role`, `created_at`. Not `keycloak_user_id` on the list.
- Q7 / Q11: detail includes memberships + impersonate eligibility (W7: not SA, must be `active`). `users_suspended` on `AdminKpisResponse` only — no FE card.
- Register `/pending` before `/{user_id}`. `/{user_id}` is UUID.

## Out of scope for P2

- Mutations / password-reset → **P3**
- Directory UI / dashboard card → **P4**
- Email/password fields

## P2.1 — Cursor list

**What:** `GET /api/v1/admin/users` copying `admin/workspaces.py` list. New `AdminUserListItem`. Service in `admin_users.py` (workspaces analogue). Keep `GET /pending` + `list_pending_users`.
**Files:** `backend/app/api/v1/admin/users.py`, `backend/app/services/admin_users.py` (new), `backend/app/schemas/admin.py`, `backend/tests/unit/test_admin_users.py`
**Deliverable:** `cd backend && pipenv run pytest tests/unit/test_admin_users.py -q`

## P2.2 — User detail

**What:** `GET /api/v1/admin/users/{user_id}`: user fields + memberships + `impersonate_allowed` from W7 rules (`impersonation.py` `_validate_impersonation_target`: not SA, status `active`). No email/password edit fields.
**Files:** `backend/app/api/v1/admin/users.py`, `backend/app/services/admin_users.py`, `backend/app/schemas/admin.py`, `backend/tests/unit/test_admin_users.py`
**Deliverable:** `cd backend && pipenv run pytest tests/unit/test_admin_users.py -q -k detail`

## P2.3 — `users_suspended` KPI field

**What:** Count `UserStatus.suspended` on `AdminKpisResponse`. Update `test_admin_kpis.py` scalar sequence (one extra count). No dashboard UI.
**Files:** `backend/app/schemas/admin.py`, `backend/app/services/admin_kpis.py`, `backend/tests/unit/test_admin_kpis.py`
**Deliverable:** `cd backend && pipenv run pytest tests/unit/test_admin_kpis.py -q`

## P2.4 — API smoke

**What:** ≤3 HTTP tests: list 200 for seeded super_admin; unauthenticated 401. Do not drop `/pending`.
**Files:** `backend/tests/api/test_admin_users.py` (new)
**Deliverable:** `cd backend && pipenv run pytest tests/api/test_admin_users.py -q`

**Phase gate:**

```bash
cd backend && pipenv run ruff check --fix . && pipenv run ruff check . && pipenv run pytest tests/unit/test_admin_users.py tests/unit/test_admin_kpis.py tests/api/test_admin_users.py -q
```

## LOOP ship gate

Do not ask Continue?. After this gate, open the Next file immediately.
Pause LOOP only if a subphase above said Pause LOOP (migration).

1. Branch — not main (`feat/mini-saas`)
2. Lint (from backend/: `pipenv run ruff check --fix . && pipenv run ruff check .`)
3. Phase gate above — green
4. Bugbot:
REPEAT until Bugbot CLOSE:
  1. Invoke review-bugbot (run_in_background: false)
  2. Diff: uncommitted changes
  3. Custom Instructions: VERB FIND + this phase locked decisions + .cursor/BUGBOT.md
  4. Fix blockers; re-lint if code changed
END REPEAT
5. Commit: feat(mini-saas): P2 user directory APIs
6. Do not push.
7. Update README status row.
8. Open Next immediately.

**Next:** [`MINI_SAAS_P3_EXECUTION.md`](./MINI_SAAS_P3_EXECUTION.md)
