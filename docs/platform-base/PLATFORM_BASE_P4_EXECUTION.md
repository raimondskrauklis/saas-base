# P4 — Prove and tag saas-base-v2 (execution)

Phase **P4** of [`PLATFORM_BASE_GENERAL_PLAN.md`](./PLATFORM_BASE_GENERAL_PLAN.md). Baseline: [`PLATFORM_BASE_FINDINGS.md`](./PLATFORM_BASE_FINDINGS.md). **P4 only.** Last implementation phase **in this template repo**.

**Goal:** Frozen reusable release `saas-base-v2`.

**Push:** batch

Do not ask Continue?. After each Deliverable, next heading. After the ship gate, open Next immediately.

## Decisions locked for P4

- Q14: P1 product grep **plus** `.cursor/`.
- Q16: L1 seed + `tests/api/` smokes in this phase (before tag). Playwright **not** here.
- Findings P4 table: pytest, npm test, alembic head `2026_09_19_2000_0012_workspace_memberships_updated_at`, no `0004` github_installations file, no `0018`, Mode A on **new** Postgres+KC (not Revy staging).
- Tag `saas-base-v2` on `raimondskrauklis/saas-base` **after** the ship-gate commit. Record the peeled SHA in a **second** docs commit (never amend the tag commit; never write SHA in P4.4).
- Short consumer copy recipe = Q8 whole tree minus Out-list (do not copy into Irbene yet).
- Do **not** clear `active_program` here (P6 closeout).

## Out of scope for P4

- Droplet deploy of the template
- Irbene overlay / copy → **P5–P6**
- Playwright E2E → findings parking lot (after `saas-base-v2` Mode A). Do not add in P4.

## P4.0 — Testing baseline (Q16)

**What:** L1 seed + HTTP contract smokes before the tag. Script `backend/scripts/seed_test_data.py`: `TEST_DATABASE_URL` only; refuse DB name without `test`; upsert user + workspace + membership (fixed UUIDs). `conftest.py`: same upsert, override `get_db` + `get_current_user`, `async_client`. `tests/api/`: `GET /api/v1/me` 200, 401 without auth, one workspace list envelope, one **403** forbidden-path smoke. Flip “no `tests/api/`” in `.cursor/rules/testing.mdc`, `.cursor/rules/backend-python.mdc`, and `AGENTS.md`. Set `.agent/manifest.json` `backend_test` to `pytest tests/unit/ tests/api/ -q`. `pytest.ini` `testpaths = tests`. Do **not** add Playwright. Do **not** copy kp domain seed.
**Files:** `backend/scripts/seed_test_data.py` (new), `backend/tests/conftest.py`, `backend/tests/api/test_me.py` (new), `backend/tests/api/test_workspaces.py` (new), `backend/pytest.ini`, `.cursor/rules/testing.mdc`, `.cursor/rules/backend-python.mdc`, `AGENTS.md`, `.agent/manifest.json`
**Deliverable:** `cd backend && pipenv run python scripts/seed_test_data.py && pipenv run pytest tests/api/ -q`; `test ! -f frontend/playwright.config.ts`

## P4.1 — Product grep including .cursor

**What:** Same strings as P1 on `backend/` `frontend/` `deploy/`, plus `.cursor/`. `docs/review-pipeline/` still absent.
**Files:** none unless grep fails (then fix in this phase — rules should already be clean from P3)
**Deliverable:**

```bash
rg -n 'github_installation|features/installations|tokens\.revy' backend frontend deploy .cursor && exit 1 || true
test ! -d docs/review-pipeline
```

## P4.2 — Unit tests and Alembic head

**What:** Full unit suites. Confirm webhook `0011` is the only head.
**Files:** none if green
**Deliverable:**

```bash
cd backend && pipenv run pytest tests/unit/ tests/api/ -q
cd frontend && npm test
cd backend && pipenv run alembic heads | grep -q '2026_09_19_2000_0012_workspace_memberships_updated_at'
cd backend && pipenv run alembic history | rg -n '0004_github_installations|0018_github_pull_request' && exit 1 || true
```

## P4.3 — Mode A smoke on new DBs

**What:** Follow `docs/platform-base/APP_REPLACE.md` start steps and `docs/starter-pack/DEV_BOOTSTRAP.md` against **this clone’s** Postgres (`DEV_DATABASE_URL` / `TEST_DATABASE_URL`) + **this clone’s** Keycloak. Not Revy, not a hosted template IdP. Register in KC → SPA callback → `GET /api/v1/me` returns `active` and a `users` row. JIT is enough (Q17); webhook optional. Record pass/fail in findings P4 table. **If Postgres or Keycloak is down, fail this phase — do not skip smoke.**
**Files:** `docs/platform-base/PLATFORM_BASE_FINDINGS.md` (P4 verification rows)
**Deliverable:** findings P4 table all green; `cd backend && pipenv run python -c "from app.core.config import settings; assert 'revy' not in (settings.database_url or '')"`

## P4.4 — Consumer copy recipe

**What:** Write `docs/platform-base/CONSUMER_COPY.md`: copy the **whole** tagged tree into the consumer minus the Out-list (`docs/vision.md`, `docs/platform-base/`, `palantir/` `polimi/` `exercises/`, root learning `Pipfile`/`Pipfile.lock`, consumer `.env.example`). **Merge** template `.gitignore` rules into the consumer `.gitignore` (do not replace; keep learning-dir ignores). Do **not** write the `saas-base-v2` SHA here — that commit does not exist yet.
**Files:** `docs/platform-base/CONSUMER_COPY.md` (new)
**Deliverable:** `test -f docs/platform-base/CONSUMER_COPY.md`

**Phase gate:**

```bash
cd backend && pipenv run ruff check . && pipenv run pytest tests/unit/ tests/api/ -q
cd frontend && npm run lint && npm test
rg -n 'github_installation|features/installations|tokens\.revy' backend frontend deploy .cursor && exit 1 || true
cd backend && pipenv run alembic heads | grep -q '2026_09_19_2000_0012_workspace_memberships_updated_at'
test ! -f frontend/playwright.config.ts
```

Tag **after** the ship-gate commit (same SHA). Record SHA in a **second** docs commit — do not amend, do not write SHA in P4.4.

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
5. Commit: feat(platform-base): P4 prove and tag saas-base-v2
6. No Revy (`integrations.revy: false`). Skip Revy REPEAT/WHILE.
7. One push: this phase + any unpushed local commits (P2–P3). Never force-push.
8. Confirm PR URL. Create annotated tag `saas-base-v2` on **this** commit and push the tag.
9. Record SHA: `git rev-parse saas-base-v2^{commit}` into findings P4 row and general-plan open item. Commit `docs(platform-base): record saas-base-v2 SHA`. Push. Never amend the tag commit.
10. Open Next immediately.

**Next:** [`PLATFORM_BASE_P5_EXECUTION.md`](./PLATFORM_BASE_P5_EXECUTION.md)
