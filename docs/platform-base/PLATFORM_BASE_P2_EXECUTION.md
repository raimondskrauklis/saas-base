# P2 — Port user provisioning (#32) (execution)

Phase **P2** of [`PLATFORM_BASE_GENERAL_PLAN.md`](./PLATFORM_BASE_GENERAL_PLAN.md). Baseline: [`PLATFORM_BASE_FINDINGS.md`](./PLATFORM_BASE_FINDINGS.md). **P2 only.**

**Goal:** Webhook-primary + JIT Keycloak → Postgres provisioning on the shell.

**Push:** local

Do not ask Continue?. After each Deliverable, next heading. After the ship gate, open Next immediately.

## Decisions locked for P2

- Port behaviour of `../revy` `ed773f4` onto this tree. Resolve conflicts toward `provision_user_from_keycloak()`.
- Alembic **full** ids: `2026_07_26_1900_0010_keycloak_webhook_deliveries` parent `2026_07_25_2340_0009_impersonation_sessions`; then `2026_07_26_1910_0011_keycloak_webhook_deliveries_received_at_idx`. Do **not** keep `0019` / `0020` / `0018`.
- vymalo `0.10.0-rc.1` on `deploy/keycloak/config/Dockerfile` (not present today).
- `webhooks/__init__.py` at this tag is Stripe-only — add Keycloak; do not import a GitHub webhook module.
- Tests to adapt: `test_keycloak_provisioning.py`, `test_keycloak_webhook.py`, `test_keycloak_webhook_verify.py`, `test_keycloak_webhooks.py`, `test_bootstrap_config.py`, plus #32 edits to `test_auth_impersonation.py` and `AuthContext.test.tsx`.
- Empty DBs only. Never Revy staging. Q15: `alembic -x test=true` on template `TEST_DATABASE_URL`.

## Out of scope for P2

- Keeping review-era revision ids → **out**
- Generic brand / `.cursor/rules` → **P3**
- Mode A smoke / tag → **P4**
- Copying `docs/authorization/` from Revy into this template

## P2.1 — Alembic webhook tables

**What:** Hand-written only. Copy table/index DDL from `ed773f4` files `2026_07_26_1900_0019_*` and `2026_07_26_1910_0020_*`. Rewrite `revision` / `down_revision` to the Q6 ids. Do not `--autogenerate`. **Pause LOOP** after this subphase. Operator: `pipenv run alembic -x test=true upgrade head` on the template test DB (Q15).
**Files:** `backend/alembic/versions/2026_07_26_1900_0010_keycloak_webhook_deliveries.py` (new), `backend/alembic/versions/2026_07_26_1910_0011_keycloak_webhook_deliveries_received_at_idx.py` (new)
**Deliverable:** `cd backend && pipenv run alembic heads` shows `2026_07_26_1910_0011_keycloak_webhook_deliveries_received_at_idx` only; `rg -n '0018_github_pull_request|0019_keycloak_webhook' backend/alembic/versions && exit 1 || true`; `pipenv run alembic -x test=true current` when `TEST_DATABASE_URL` is set

## P2.2 — Provisioning service and Keycloak webhook

**What:** Port `provision_user_from_keycloak()`, `/api/v1/webhooks/keycloak`, models, integrations, bootstrap guard, config flags from #32. Merge into shell `auth.py` / `users.py` / `invitations.py` / `main.py` / `config.py` toward #32 behaviour. Register the Keycloak router next to Stripe.
**Files:** `backend/app/services/keycloak_provisioning.py` (new), `backend/app/services/keycloak_webhooks.py` (new), `backend/app/services/users.py`, `backend/app/services/invitations.py`, `backend/app/integrations/keycloak_webhook.py` (new), `backend/app/api/v1/webhooks/keycloak.py` (new), `backend/app/api/v1/webhooks/__init__.py`, `backend/app/models/keycloak_webhook_delivery.py` (new), `backend/app/models/__init__.py`, `backend/app/core/auth.py`, `backend/app/core/bootstrap.py`, `backend/app/core/config.py`, `backend/app/main.py`, `backend/tests/unit/test_keycloak_provisioning.py` (new), `backend/tests/unit/test_keycloak_webhook.py` (new), `backend/tests/unit/test_keycloak_webhook_verify.py` (new), `backend/tests/unit/test_keycloak_webhooks.py` (new), `backend/tests/unit/test_bootstrap_config.py` (new or port)
**Deliverable:** `cd backend && pipenv run pytest tests/unit/test_keycloak_provisioning.py tests/unit/test_keycloak_webhook.py tests/unit/test_keycloak_webhook_verify.py tests/unit/test_keycloak_webhooks.py tests/unit/test_bootstrap_config.py tests/unit/test_auth_impersonation.py -q`

## P2.3 — Keycloak image listener

**What:** Pin vymalo `0.10.0-rc.1` on the template KC Dockerfile and matching env/README from #32. Not already in this tree.
**Files:** `deploy/keycloak/config/Dockerfile`, `deploy/keycloak/config/.env.example`, `deploy/keycloak/config/README.md`
**Deliverable:** `rg -n '0.10.0-rc.1' deploy/keycloak/config/Dockerfile`

## P2.4 — Frontend toasts and i18n

**What:** Port #32 `AuthContext.tsx` / tests and EN+LV strings for provisioning toasts. No Irbene names.
**Files:** `frontend/src/contexts/AuthContext.tsx`, `frontend/src/contexts/AuthContext.test.tsx` (new), `frontend/src/i18n/locales/en.json`, `frontend/src/i18n/locales/lv.json`
**Deliverable:** `cd frontend && npm test`

**Phase gate:**

```bash
cd backend && pipenv run ruff check --fix . && pipenv run ruff check . && pipenv run pytest tests/unit/ -q
cd frontend && npm run lint && npm test
cd backend && pipenv run alembic heads | grep -q '2026_07_26_1910_0011_keycloak_webhook_deliveries_received_at_idx'
```

## LOOP ship gate

Do not ask Continue?. After this gate, open the Next file immediately.
Pause LOOP only if a subphase above said Pause LOOP (migration).

1. Branch — not main (`feat/platform-base`)
2. Lint (`cd backend && pipenv run ruff check --fix . && pipenv run ruff check .`; `cd frontend && npm run lint`)
3. Phase gate above — green
4. Bugbot:
REPEAT until Bugbot CLOSE:
  1. Invoke review-bugbot (run_in_background: false)
  2. Diff: uncommitted changes
  3. Custom Instructions: VERB FIND + this phase locked decisions + .cursor/BUGBOT.md
  4. Fix blockers; re-lint if code changed
END REPEAT
5. Commit: feat(platform-base): P2 port Keycloak user provisioning
6. Do not push.
7. Update README status row.
8. Open Next immediately.

**Next:** [`PLATFORM_BASE_P3_EXECUTION.md`](./PLATFORM_BASE_P3_EXECUTION.md)
