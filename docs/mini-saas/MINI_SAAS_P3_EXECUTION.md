# P3 — Lifecycle mutations (execution)

Phase **P3** of [`MINI_SAAS_GENERAL_PLAN.md`](./MINI_SAAS_GENERAL_PLAN.md). Baseline: [`MINI_SAAS_FINDINGS.md`](./MINI_SAAS_FINDINGS.md). **P3 only.**

**Goal:** Approve, reject, suspend, reactivate, and send-password-reset go through the helper; dual-write (Q22); audit; last-active-SA and self-suspend guards.

**Push:** local

Do not ask Continue?. After each Deliverable, next heading. After the ship gate, open Next immediately.

## Decisions locked for P3

- Q22: open transaction: mutate row → helper (raise) → `commit`. If commit fails after Admin `enabled` succeeded, restore KC `enabled`. Session logout is **not** undoable. **Q22 wrapper owns `commit`** — routers must not `session.commit()` again on approve/reject/suspend/reactivate.
- Approve `VERIFY_EMAIL` (when KC `emailVerified` is false) runs **before** PUT `enabled=true`. If execute-actions fails, do not PUT `enabled` and do not commit (row stays pending).
- Q5: forbid self-suspend; forbid suspend of the last remaining **active** `super_admin`.
- Q8 / Q13: audits `platform.user.approved` / `rejected` / `suspended` / `reactivated`. Reactivate `suspended`→`active` only.
- Q15: `POST /api/v1/admin/users/{id}/send-password-reset` → `UPDATE_PASSWORD`. Fail closed. Tests mock the helper. No live SMTP.
- SELECT FOR UPDATE on mutations (same as current approve/reject). `actor_user_id` on audit like `admin_workspaces.suspend_workspace`.

## Out of scope for P3

- FE / dashboard card / drop `/pending` → **P4**
- Reactivate from `rejected`/`deleted`; promote `super_admin`
- Live SMTP (Q20)

## P3.1 — Q22 dual-write

**What:** Shared helper used by status mutations: mutate row in the open session → Admin `enabled` (raise) → `commit`; on commit failure after Admin success, restore previous `enabled`. Do not restore logout. Routers for these mutations do **not** call `session.commit()`. Unit tests: helper raise → no commit; commit-fail → restore `enabled`.
**Files:** `backend/app/services/admin_users.py`, `backend/tests/unit/test_admin_users.py`
**Deliverable:** `cd backend && pipenv run pytest tests/unit/test_admin_users.py -q -k dual_write`

## P3.2 — Suspend and reactivate

**What:** `POST …/{user_id}/suspend` and `…/reactivate`. Suspend: `suspended` + `enabled=false` + logout + audit `platform.user.suspended`. Reactivate: only from `suspended` → `active` + `enabled=true` + audit `platform.user.reactivated`. Guards: actor `id != target`; count **active** SAs — last active SA cannot be suspended. Q22 on both.
**Files:** `backend/app/api/v1/admin/users.py`, `backend/app/services/admin_users.py`, `backend/tests/unit/test_admin_users.py`
**Deliverable:** `cd backend && pipenv run pytest tests/unit/test_admin_users.py -q -k 'suspend or reactivate'`

## P3.3 — Approve, reject, audits

**What:** Existing approve/reject go through Q22 (wrapper commits). Approve: if GET user `emailVerified` is false, `execute-actions-email` `VERIFY_EMAIL` **then** PUT `enabled=true`. If `VERIFY_EMAIL` fails, skip PUT and do not commit. Reject: `enabled=false` + logout. Audits `platform.user.approved` / `platform.user.rejected`. Mock helper in tests; do not call live SMTP.
**Files:** `backend/app/api/v1/admin/users.py`, `backend/app/services/users.py`, `backend/app/services/admin_users.py`, `backend/tests/unit/test_admin_users.py`
**Deliverable:** `cd backend && pipenv run pytest tests/unit/test_admin_users.py -q`

## P3.4 — Send password reset

**What:** `POST /api/v1/admin/users/{user_id}/send-password-reset` → helper `UPDATE_PASSWORD`. No status row. No audit. 4xx/5xx from helper → request fails (no silent skip). Tests mock helper.
**Files:** `backend/app/api/v1/admin/users.py`, `backend/app/services/admin_users.py`, `backend/tests/unit/test_admin_users.py`
**Deliverable:** `cd backend && pipenv run pytest tests/unit/test_admin_users.py -q -k password_reset`

**Phase gate:**

```bash
cd backend && pipenv run ruff check --fix . && pipenv run ruff check . && pipenv run pytest tests/unit/test_admin_users.py tests/unit/test_keycloak_admin.py tests/api/test_admin_users.py -q
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
5. Commit: feat(mini-saas): P3 user lifecycle mutations
6. Do not push.
7. Update README status row.
8. Open Next immediately.

**Next:** [`MINI_SAAS_P4_EXECUTION.md`](./MINI_SAAS_P4_EXECUTION.md)
