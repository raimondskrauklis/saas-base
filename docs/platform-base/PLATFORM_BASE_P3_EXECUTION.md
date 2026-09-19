# P3 — Generic platform identity (execution)

Phase **P3** of [`PLATFORM_BASE_GENERAL_PLAN.md`](./PLATFORM_BASE_GENERAL_PLAN.md). Baseline: [`PLATFORM_BASE_FINDINGS.md`](./PLATFORM_BASE_FINDINGS.md). **P3 only.**

**Goal:** A consumer can rename realm/hosts/app slug without leftover Revy product strings, and agents will not put GitHub installations back.

**Push:** local

Do not ask Continue?. After each Deliverable, next heading. After the ship gate, open Next immediately.

## Decisions locked for P3

- Q13 / Q14: retarget `.cursor/rules` **now** (not P1). Brand is `tokens.css` only. Domain is generic SaaS (workspaces, settings, billing) — not GitHub installations or review pipeline.
- Placeholders only: no Irbene / VIRAC names in this template.
- No `tokens.app.css`.
- Document an `<app>` replace list in `docs/platform-base/` (one short file).
- Grep must be empty or placeholder-only for the strings below.

## Out of scope for P3

- Designing Irbene brand → **P6**
- Rewriting gitignored `internal-docs` starter-pack
- Tag / Mode A → **P4**

## P3.1 — Cursor rules

**What:** Edit `00-core.mdc` and `app-color-tokens.mdc` (and `.cursorrules` pointer if it still says Revy product). No GitHub installations; no `tokens.revy.css`; no `REVY_PRODUCT_SLICE.md`. Theme: `--app-*` in `tokens.css`. `git-quick.md` still cites `REVY_PRODUCT_SLICE.md` — retarget or drop that line here.
**Files:** `.cursor/rules/00-core.mdc`, `.cursor/rules/app-color-tokens.mdc`, `.cursor/rules/git-quick.md`, `.cursorrules`
**Deliverable:** `rg -n 'tokens\.revy|GitHub installations|REVY_PRODUCT_SLICE' .cursor .cursorrules && exit 1 || true`

## P3.2 — App name, env, i18n, fixtures

**What:** Generic `<app>` for `app_name`, `keycloak_frontend_client_id`, `export_storage_path` (`/tmp/revy/exports` → `/tmp/app/exports` or similar placeholder), env examples (`VITE_KEYCLOAK_REALM=revy`, `KEYCLOAK_REALM=revy`), i18n product copy (account deactivate, etc.), Python fixtures `keycloak_realm="revy"` / `revy.createit.digital` in tests.
**Files:** `backend/app/core/config.py`, `backend/.env.example`, `frontend/.env.example`, `deploy/env-examples/**`, `frontend/src/i18n/locales/en.json`, `frontend/src/i18n/locales/lv.json`, `backend/tests/unit/test_keycloak_issuer.py`, `backend/tests/unit/test_auth_audience.py`, `backend/tests/unit/test_decode_access_token.py`, `backend/tests/unit/test_billing_config.py`
**Deliverable:** `rg -n 'app_name: str = "Revy"|keycloak_realm="revy"|keycloak_client_id.*revy-api|revy-web|/tmp/revy|KEYCLOAK_REALM=revy' backend frontend deploy && exit 1 || true`

## P3.3 — Docker, nginx, image names

**What:** Placeholder hosts/realm/volume/image (`revy.createit.digital`, `revy-keycloak`, `/mnt/revy_volume`, `revy[bot]`). Do not invent Irbene DNS.
**Files:** `deploy/nginx/**`, `deploy/keycloak/**`, docker-compose files at repo root if present, any `revy-keycloak` image name
**Deliverable:** `rg -n 'revy.createit.digital|revy\[bot\]|revy-keycloak|/mnt/revy' deploy && exit 1 || true`

## P3.4 — Replace list and P3 grep

**What:** Write `docs/platform-base/APP_REPLACE.md` listing realm, hosts, `app_name`, client ids, image names, export path. Then run the full P3 grep (empty or placeholder-only).
**Files:** `docs/platform-base/APP_REPLACE.md` (new), `AGENTS.md`, `README.md` if they still claim Revy product
**Deliverable:**

```bash
test -f docs/platform-base/APP_REPLACE.md
rg -n 'revy.createit.digital|revy\[bot\]|KEYCLOAK_REALM=revy|keycloak_realm="revy"|app_name.*Revy|revy-keycloak|/tmp/revy' backend frontend deploy .cursor AGENTS.md README.md && exit 1 || true
```

**Phase gate:**

```bash
cd backend && pipenv run ruff check --fix . && pipenv run ruff check . && pipenv run pytest tests/unit/ -q
cd frontend && npm run lint && npm test
rg -n 'revy.createit.digital|revy\[bot\]|KEYCLOAK_REALM=revy|keycloak_realm="revy"|app_name.*Revy|revy-keycloak|/tmp/revy' backend frontend deploy .cursor AGENTS.md README.md && exit 1 || true
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
5. Commit: feat(platform-base): P3 generic platform identity
6. Do not push.
7. Update README status row.
8. Open Next immediately.

**Next:** [`PLATFORM_BASE_P4_EXECUTION.md`](./PLATFORM_BASE_P4_EXECUTION.md)
