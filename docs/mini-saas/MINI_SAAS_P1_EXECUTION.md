# P1 — Outbound Keycloak Admin helper (execution)

Phase **P1** of [`MINI_SAAS_GENERAL_PLAN.md`](./MINI_SAAS_GENERAL_PLAN.md). Baseline: [`MINI_SAAS_FINDINGS.md`](./MINI_SAAS_FINDINGS.md). **P1 only.**

**Goal:** One fail-closed client-credentials helper: GET-merge-PUT `enabled`, session logout, execute-actions (`client_id=app-web` + SPA `redirect_uri`).

**Push:** first-push

Do not ask Continue?. After each Deliverable, next heading. After the ship gate, open Next immediately.

## Decisions locked for P1

- Q1 / Q14 / Q15: helper only. No product path yet except tests.
- Lives in `backend/app/services/integrations/` (outbound httpx). Not next to `keycloak_provisioning.py`.
- Raise on HTTP/role/timeout errors. No `None`/`False` swallow.
- GET-merge-PUT for `enabled` (Keycloak 26 PUT is a full representation).
- `execute-actions-email`: `client_id=settings.keycloak_frontend_client_id` (`app-web`) + `redirect_uri = (settings.app_public_url or "http://localhost:5173").rstrip("/") + "/login"` (KEYCLOAK_SETUP / MAILGUN_SETUP).
- No Keycloak user create/delete.

## Out of scope for P1

- Wiring approve/reject/suspend/password-reset → **P3**
- Live realm roles / SMTP / Q20
- Directory APIs → **P2**

## P1.1 — Client and token

**What:** Async httpx client against `{keycloak_url}/admin/realms/{realm}`. Client-credentials token via `{keycloak_url}/realms/{realm}/protocol/openid-connect/token` using `keycloak_client_id` + `keycloak_client_secret`. Raise on non-2xx / timeout. No `return None`.
**Files:** `backend/app/services/integrations/keycloak_admin.py` (new), `backend/app/services/integrations/__init__.py`, `backend/tests/unit/test_keycloak_admin.py` (new)
**Deliverable:** `cd backend && pipenv run pytest tests/unit/test_keycloak_admin.py -q -k token`

## P1.2 — GET-merge-PUT `enabled`

**What:** GET user by Keycloak id, set `enabled`, PUT the merged representation. Raise on 403/404/5xx/timeout.
**Files:** `backend/app/services/integrations/keycloak_admin.py`, `backend/tests/unit/test_keycloak_admin.py`
**Deliverable:** `cd backend && pipenv run pytest tests/unit/test_keycloak_admin.py -q -k enabled`

## P1.3 — Logout and execute-actions

**What:** `POST …/users/{id}/logout`. `PUT …/users/{id}/execute-actions-email` with body `["UPDATE_PASSWORD"]` or `["VERIFY_EMAIL"]` and query `client_id` + `redirect_uri` as locked. Raise on failure. No SMTP in this phase.
**Files:** `backend/app/services/integrations/keycloak_admin.py`, `backend/tests/unit/test_keycloak_admin.py`
**Deliverable:** `cd backend && pipenv run pytest tests/unit/test_keycloak_admin.py -q -k 'logout or execute'`

## P1.4 — Fail-closed contract tests

**What:** Mocked httpx: 403, timeout, 5xx → raise; no `False`/`None`. Helper is unused by routers this phase.
**Files:** `backend/tests/unit/test_keycloak_admin.py`
**Deliverable:** `cd backend && pipenv run pytest tests/unit/test_keycloak_admin.py -q`

**Phase gate:**

```bash
cd backend && pipenv run ruff check --fix . && pipenv run ruff check . && pipenv run pytest tests/unit/test_keycloak_admin.py tests/unit/test_keycloak_provisioning.py -q
cd frontend && npm run lint && npm test -- --run src/lib/api.test.ts
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
5. Commit: feat(mini-saas): P1 Keycloak Admin helper
6. No PR yet — skip Revy.
7. Push (opens PR; includes P0 commit). Title: feat(mini-saas): Keycloak Admin helper and victim UX. Use ship-changes **from Push onward** (already committed — do not commit again).
8. Confirm PR URL. Revy starts — do not fetch or fix comments yet.
9. Open Next immediately.

**Next:** [`MINI_SAAS_P2_EXECUTION.md`](./MINI_SAAS_P2_EXECUTION.md)
