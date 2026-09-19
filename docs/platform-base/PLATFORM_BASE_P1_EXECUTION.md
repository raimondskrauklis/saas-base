# P1 — Strip Revy product from the shell (execution)

Phase **P1** of [`PLATFORM_BASE_GENERAL_PLAN.md`](./PLATFORM_BASE_GENERAL_PLAN.md). Baseline: [`PLATFORM_BASE_FINDINGS.md`](./PLATFORM_BASE_FINDINGS.md). **P1 only.**

**Goal:** Runtime tree is SaaS only — no GitHub installations, no Revy LLM/GitHub env, no `vector`, no review-pipeline corpus.

**Push:** first-push

Do not ask Continue?. After each Deliverable, next heading. After the ship gate, open Next immediately.

## Decisions locked for P1

- Q5 / Q6 / Q11 / Q13 / Q14 / Q15. Q16 is **P4** (not this phase). Playwright is parking lot (not this phase).
- Delete revision file `backend/alembic/versions/2026_07_24_0300_0004_github_installations.py`. Set `down_revision` on `2026_07_25_2217_0005_user_locale_timezone` to `"2026_07_24_0200_0003_invitations"` (full strings only).
- Strip live consumers, not only `features/installations/`. Keep `PlanSummaryWidget`. Rename `registerRevy.ts` → `registerPlatform.ts` / `registerPlatformExtensions`.
- Delete `tokens.revy.css` and the `@import` in `frontend/src/index.css`. Fold leftover `--rv-*` into `tokens.css`. Do **not** add `tokens.app.css`.
- Delete `docs/review-pipeline/`, `docs/starter-pack/REVY_PRODUCT_SLICE.md`, `docs/starter-pack/SCAFFOLD_P4_EXECUTION.md`. Retarget or drop those inbound links in `docs/starter-pack/README.md`.
- Product grep **P1 only:** `backend/` `frontend/` `deploy/` for `github_installation` / `features/installations` / `tokens.revy`, plus `test ! -d docs/review-pipeline`. Do **not** grep `.cursor/` and do **not** edit `.cursor/rules`.
- Keep Stripe, impersonation, items.

## Out of scope for P1

- Auth #32 / vymalo / webhook tables → **P2**
- `.cursor/rules`, `app_name`, nginx hostnames, `KEYCLOAK_REALM` genericize → **P3**
- Tag `saas-base-v2` / Mode A smoke → **P4**
- Copy into `../irbene_gate` → **P5–P6**

## P1.1 — Alembic: drop installations revision

**What:** Hand-written only. Delete `2026_07_24_0300_0004_github_installations`. Parent `0005` on `2026_07_24_0200_0003_invitations`. Do not `--autogenerate`. **Pause LOOP** after this subphase. Operator: `pipenv run alembic -x test=true upgrade head` on a **new** template `TEST_DATABASE_URL` (create empty Postgres if missing). Never Revy DBs.
**Files:** `backend/alembic/versions/2026_07_24_0300_0004_github_installations.py` (delete), `backend/alembic/versions/2026_07_25_2217_0005_user_locale_timezone.py`
**Deliverable:** `rg -n '2026_07_24_0300_0004_github_installations' backend/alembic/versions && exit 1 || true; rg -n 'down_revision = "2026_07_24_0200_0003_invitations"' backend/alembic/versions/2026_07_25_2217_0005_user_locale_timezone.py; cd backend && pipenv run alembic -x test=true current` (when `TEST_DATABASE_URL` is set)

## P1.2 — Backend product slice

**What:** Remove GitHub installations API/models/schemas/service/tests; drop `GitHubAccountType` / `GitHubInstallationStatus`; drop `installations.create` from `plan_gates` (keep the module; rewrite `test_plan_gates.py` so it does not require that feature); unhook workspace router; drop GitHub/review celery routes that have no modules at this tag (`github_tasks.*`, `github_publish`, `repo_sync`, `indexing`, `review`, `reconciliation`, `judge`).
**Files:** `backend/app/api/v1/workspaces/installations.py` (delete), `backend/app/api/v1/workspaces/__init__.py`, `backend/app/models/github_installation.py` (delete), `backend/app/models/__init__.py`, `backend/app/schemas/github_installation.py` (delete), `backend/app/services/github_installations.py` (delete), `backend/app/constants/enums.py`, `backend/app/core/plan_gates.py`, `backend/app/workers/celery_app.py`, `backend/tests/unit/test_github_installations.py` (delete), `backend/tests/unit/test_plan_gates.py`
**Deliverable:** `cd backend && pipenv run pytest tests/unit/ -q`

## P1.3 — Frontend feature and consumers

**What:** Delete `frontend/src/features/installations/`. Remove `/installations` route and nav. Stop dashboard/checklist/quick-actions/settings tests from calling installations. Drop i18n `installations*` keys (EN+LV). Keep `PlanSummaryWidget`. Rename register file; drop GitHub card + installations widget; keep plan widget. Delete `tokens.revy.css`; remove `@import` from `index.css`; fold leftover `--rv-*` into `tokens.css`.
**Files:** `frontend/src/features/installations/**` (delete), `frontend/src/lib/routerInstance.tsx`, `frontend/src/components/layout/AppShellLayout.tsx`, `frontend/src/features/dashboard/hooks.ts`, `frontend/src/features/dashboard/checklistSteps.ts`, `frontend/src/features/dashboard/widgets/QuickActionsWidget.tsx`, `frontend/src/features/dashboard/widgets/QuickActionsWidget.test.tsx`, `frontend/src/features/dashboard/widgets/SetupChecklistWidget.test.tsx`, `frontend/src/features/settings/pages/IntegrationsSettingsPage.test.tsx`, `frontend/src/platform/extensions/registerRevy.ts` (rename), `frontend/src/main.tsx`, `frontend/src/i18n/locales/en.json`, `frontend/src/i18n/locales/lv.json`, `frontend/src/styles/tokens.revy.css` (delete), `frontend/src/styles/tokens.css`, `frontend/src/index.css`
**Deliverable:** `cd frontend && npm test`

## P1.4 — Config, env, vector

**What:** Strip `github_*`, `revy_bot_login`, moonshot/voyage, `anthropic_api_key`, `revy_repos_root` / worktrees / hf cache / review-policy `revy_*` settings from config and env examples. Drop `CREATE EXTENSION vector` from `deploy/sql/postgres-extensions.sql` (keep uuid-ossp, pg_trgm, pgcrypto). Leave `app_name` / realm / nginx hostnames for **P3**. Keep Stripe keys.
**Files:** `backend/app/core/config.py`, `backend/.env.example`, `frontend/.env.example`, `deploy/env-examples/backend.env.production.example`, `deploy/env-examples/github-actions.secrets.example`, `deploy/sql/postgres-extensions.sql`
**Deliverable:** `rg -n 'github_app_id|moonshot_api_key|voyage_api_key|anthropic_api_key|revy_bot_login|CREATE EXTENSION IF NOT EXISTS vector' backend deploy && exit 1 || true`

## P1.5 — Corpus delete and P1 product grep

**What:** Delete review-pipeline tree and the two starter-pack product specs. In `docs/starter-pack/README.md` drop Active/P4 authority links to those three; do not rewrite the rest of the scaffold waves.
**Files:** `docs/review-pipeline/` (delete), `docs/starter-pack/REVY_PRODUCT_SLICE.md` (delete), `docs/starter-pack/SCAFFOLD_P4_EXECUTION.md` (delete), `docs/starter-pack/README.md`
**Deliverable:**

```bash
test ! -d docs/review-pipeline
test ! -f docs/starter-pack/REVY_PRODUCT_SLICE.md
test ! -f docs/starter-pack/SCAFFOLD_P4_EXECUTION.md
rg -n 'github_installation|features/installations|tokens\.revy' backend frontend deploy && exit 1 || true
```

**Phase gate:**

```bash
cd backend && pipenv run ruff check --fix . && pipenv run ruff check . && pipenv run pytest tests/unit/ -q
cd frontend && npm run lint && npm test
test ! -d docs/review-pipeline
rg -n 'github_installation|features/installations|tokens\.revy' backend frontend deploy && exit 1 || true
# Q14: do not grep .cursor/; rules still mention tokens.revy.css until P3
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
5. Commit: feat(platform-base): P1 strip GitHub product from the shell
6. No Revy (`integrations.revy: false`). Skip Revy poll.
7. Push (opens PR; includes P0 commit). Title: feat(platform-base): strip GitHub product from the shell. Use ship-changes **from Push onward** (already committed — do not commit again).
8. Confirm PR URL. Do not fetch or fix review comments yet.
9. Open Next immediately.

**Next:** [`PLATFORM_BASE_P2_EXECUTION.md`](./PLATFORM_BASE_P2_EXECUTION.md)
