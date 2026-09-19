# Platform base — findings

Baseline for a **clean reusable SaaS template** (then copy into `irbene_gate`). **No execution steps.**

**Status:** baseline updated after architecture-peer-review pass 2 (2026-09-19). Q11–Q14 locked.  
**Codebase verified:** this template repo at `saas-base-v1.1` (`48c361e`) plus local `/Users/raimonds.krauklis/projects/revy` for Auth #32.  
**Not verified:** a live DB for `saas-base-v1.1` (none required).

Revy was built to **spin any upcoming platform**. The shell was tagged. Full user provisioning was **not** tagged — it shipped on the reviewer tree. This program freezes that missing cut: shell + auth, no Revy product.

---

## Build principles

- **Cleaner template over faster strip.** Do not clone `main` and delete review code. Start from the frozen shell and **add** auth.
- **Two artefacts, two homes.** This repo **is** the canonical template. `../irbene_gate` **consumes** a tagged release (`saas-base-v2`). Program docs live in `docs/platform-base/` here.
- **Keycloak = identity, PostgreSQL = lifecycle + RBAC.** Same as starter-pack `AUTHZ_MODEL.md`. Do not read KC realm roles in FastAPI.
- **Subtract product, not SaaS.** GitHub installations are Revy. Stripe, impersonation, items demo, settings, platform admin stay (env-gate Stripe).
- **Hand-written Alembic.** Use the **full** `revision` / `down_revision` strings. Do not keep review-era ids (`2026_07_26_1900_0019_*` / `0018_*`). Never `--autogenerate`.
- **Generic `<app>` identity** in the template. Revy hostnames, realm, tokens, bot login do not ship in the base.
- **EN+LV, unit tests only** (`tests/unit/`), `--app-*` tokens. Same rails as scaffold.
- **No Irbene objects in this program.** Scan / Issue / Product wait until the base runs.

---

## Terminology

| Term | Meaning |
|------|---------|
| **Shell** | Tag `saas-base-v1.1` — W0–W8 + Alembic AUTOCOMMIT. Login/JWT exist. Keycloak **webhook provisioning does not.** |
| **Auth #32** | Commit `ed773f4` — unified `provision_user_from_keycloak()`, KC webhook, vymalo listener, bootstrap guard, FE toasts. |
| **Revy product (at shell)** | P4 `github_installations` slice + `registerRevy` GitHub widgets + `tokens.revy.css` + `github_*` / `revy_*` / LLM env. **No** reviewer UI at this tag (verified: no `frontend/.../reviewer` on `saas-base-v1.1`). |
| **Clean base** | New repo: shell − Revy product + Auth #32 + generic brand. Tag `saas-base-v2`. |
| **Template repo** | This git tree: `/Users/raimonds.krauklis/projects/saas-base`. P0–P4 run here. |
| **Consumer repo** | A product that copies a `saas-base-v2` tree. First consumer: `../irbene_gate`. P5–P6 run there. |
| **starter-pack (docs)** | `revy/internal-docs/starter-pack/` — **gitignored**, not on GitHub. Runnable app at the tag **is** `backend/` + `frontend/` in git. Do not require `internal-docs` to scaffold the new repo. |

---

## What exists vs genuinely new

### Verified — frozen shell (`saas-base-v1.1` = `48c361e`)

| Layer | What | Evidence |
|-------|------|----------|
| History | Initial `0db2f60` → scaffold P1–P4 → saas W0–W8 → tag | `git log --reverse`; tag message on `48c361e` |
| Auth (incomplete) | OIDC JWT, JWKS, login SPA, Mode A/B flags, JIT user on first `/me` | `backend/app/core/auth.py`; `frontend/src/lib/keycloak.ts`; `docs/starter-pack/REGISTRATION_FLAGS.md` |
| SaaS W0–W8 | Settings, dashboard, Stripe (default off), lifecycle, impersonation, platform admin | `docs/saas-base/README.md`; migrations through `2026_07_25_2340_0009_impersonation_sessions` |
| Items demo | CRUD + cursor list | `0002_p1_items`; `backend/app/api/v1/items.py` |
| Alembic head | impersonation sessions | `revision = "2026_07_25_2340_0009_impersonation_sessions"` |
| Product mixed in | GitHub installations + live consumers (not only the feature folder) | `2026_07_24_0300_0004_github_installations`; `features/installations/`; `registerRevy.ts`; also `routerInstance.tsx`, `AppShellLayout.tsx`, `checklistSteps.ts`, `QuickActionsWidget.tsx`, `dashboard/hooks.ts`, settings tests, `plan_gates.py` (`installations.create`), `enums.py` (`GitHubAccountType` / `GitHubInstallationStatus`), `models/__init__.py`, i18n `installations*` |
| Revy corpus on the tag | Review program + product-slice specs | `docs/review-pipeline/`; `docs/starter-pack/REVY_PRODUCT_SLICE.md`; `docs/starter-pack/SCAFFOLD_P4_EXECUTION.md` |
| Brand leak | `revy.createit.digital`, realm/env `revy`, `revy_*` config, `tokens.revy.css` | `deploy/nginx/`; `backend/app/core/config.py` (github/moonshot/voyage/revy_* keys) |
| Extensions SQL | `vector` + uuid-ossp + pg_trgm + pgcrypto | `deploy/sql/postgres-extensions.sql` — `vector` is review-era, unused by shell schema |
| File count | 462 files at the tag; 161 backend `.py` | vs `revy/main` 1076 / 394. P0 overlay added workflow/docs (expected). |
| `internal-docs/` | **Not in git** | `revy/.gitignore` `/internal-docs/` |

### Verified — Auth #32 (`ed773f4`, 2026-07-26)

| Claim | Evidence |
|-------|----------|
| **Not** in `saas-base-v1`, `v1.1`, or `review-r5-v1` | `git merge-base --is-ancestor` |
| Sits **after** R0–R8 on `main` (30 commits after `saas-base-v1`) | `git log saas-base-v1..ed773f4` |
| **No** GitHub/review paths in the commit | `git show ed773f4 --name-only` |
| Alembic `2026_07_26_1900_0019_keycloak_webhook_deliveries` parents **review** `2026_07_26_1800_0018_github_pull_request_is_draft` | file header in that commit |
| Index follow-up | `2026_07_26_1910_0020_keycloak_webhook_deliveries_received_at_idx` | `down_revision` = the `0019` id |
| #32 tests (adapt in P2) | `test_keycloak_provisioning.py`, `test_keycloak_webhook.py`, `test_keycloak_webhook_verify.py`, `test_keycloak_webhooks.py`, `test_bootstrap_config.py`; plus edits to `test_auth_impersonation.py` and `AuthContext.test.tsx` | `git show ed773f4 --name-only` |
| Overlap with shell (conflicts likely) | `webhooks/__init__.py` (Stripe only at v1.1), `auth.py`, `config.py`, `users.py`, `invitations.py`, `main.py`, `AuthContext.tsx`, i18n, KC Dockerfile |

### Verified — consumer repo (`../irbene_gate`)

Not this template. Do not read `docs/vision.md` as a file in `saas-base`.

| Claim | Evidence |
|-------|----------|
| No app tree yet | `backend/` / `frontend/` absent in the consumer |
| Product north star | `../irbene_gate/docs/vision.md` |
| Learning tracks gitignored | consumer `.gitignore` `/exercises/` `/palantir/` `/polimi/` |
| Env placeholders only | consumer `.env.example` `VIRAC_*` / `POLIMI_DATABASE_URL` |

### Genuinely new (this program)

- Template repo whose history **stops** at shell tag (P0 done: tip is overlay on `48c361e`).
- Delete `2026_07_24_0300_0004_github_installations`; set `2026_07_25_2217_0005_user_locale_timezone.down_revision = "2026_07_24_0200_0003_invitations"`.
- Port #32 as `2026_07_26_1900_0010_keycloak_webhook_deliveries` + `2026_07_26_1910_0011_keycloak_webhook_deliveries_received_at_idx` parented on `2026_07_25_2340_0009_impersonation_sessions` — not `0019`/`0020`/`0018`.
- Strip live consumers (nav, dashboard, plan_gates, i18n), not only `features/installations/`.
- Delete Revy review corpus (`docs/review-pipeline/`, `REVY_PRODUCT_SLICE.md`, `SCAFFOLD_P4_EXECUTION.md`). Fold `--rv-*` into `tokens.css`; drop `tokens.revy.css` and its `@import`.
- Generic brand; drop `vector` / GitHub / LLM env; retarget `.cursor/rules`.
- Copy the **whole** tagged `saas-base-v2` tree into `irbene_gate` minus consumer-owned paths.

### Reuse caveats / traps

| Trap | Detail |
|------|--------|
| **“Strip `main`”** | Auth is already there, but 109 `github` paths vs 7 at the shell. Alembic still knows every `github_*` table. **Rejected** (user: cleaner template). |
| **Cherry-pick #32 as-is** | `down_revision` is `2026_07_26_1800_0018_github_pull_request_is_draft`. Must rewrite ids **and** parent. `webhooks/__init__.py` on `main` also exports GitHub; at v1.1 it is Stripe-only — merge carefully. |
| **Keep `0004` “empty”** | Leaves `github_installations` in every consumer DB. **Remove** the revision file; set `0005.down_revision` to the **full** `0003` id (not the substring `"0003"`). |
| **Literal Alembic shorthand** | `"0003"` / `"0009"` / `"0010"` are not `revision` values. Always the `2026_07_*` strings. |
| **Repo-wide content grep** | `github_installation` / `tokens.revy` still appear in historical SaaS/scaffold runbooks after code strip. P1 gate is `backend/` `frontend/` `deploy/` plus corpus delete — not unscoped `docs/`, not `.cursor/` (Q14). |
| **`registerRevy.ts` on `main`** | Later gained reviewer widgets. At **v1.1** it is installations + `PlanSummaryWidget` only. Keep plan widget; drop GitHub registrations; rename file. |
| **`internal-docs` missing on GitHub** | Fresh clone of `revy` has the **app**, not the private pack. Copy from the **tag’s tracked files**, not from gitignored pack. |
| **JIT vs webhook** | Shell already inserts user on first JWT. #32 adds webhook-primary + JIT fallback. Both belong in the clean base. |
| **Stripe** | W4 is in the shell, `stripe_enabled: bool = False`. Keep. Do not strip for VIRAC. |
| **irbene_gate as template** | Mixed product + Polimi + Palantir drills. **Never** the canonical base. |

---

## Catalog — workstreams

| Track | Why | Method |
|-------|-----|--------|
| **A. Clean base (template repo)** | Reuse for Palantir, VIRAC, next app | History from `saas-base-v1.1`; strip product; port #32; genericize; tag `saas-base-v2` |
| **B. Consumer consumes** | Irbene Gate needs a running factory before ontology | Copy whole `saas-base-v2` tree into `irbene_gate` minus Out-list; overlay name/realm only |

Rejected: clone `revy/main` and delete; put canonical template only as a tag on `revy` (history stays a reviewer repo); implement ontology in the same program.

---

## Advice / options

| Option | Verdict |
|--------|---------|
| **A — shell + port auth** | **Adopt.** More work. Clean Alembic. Missing freeze from July. |
| **B — strip current Revy** | **Reject.** Dirtier template. User locked cleaner. |
| Tag-only on `revy` | **Reject** as canonical home. Optional *pointer* tag later. Canonical = new repo. |
| Git submodule in `irbene_gate` | **Reject** for v1 copy. Overlay + submodule fights. Copy tree; document upstream tag. |
| Drop Stripe/impersonation | **Reject.** That is SaaS base, not Revy product. |

---

## Data scope & exclusions

**In the clean base:** users, workspaces, memberships, items, invitations, audit, Stripe webhook events, lifecycle export jobs, impersonation sessions, Keycloak webhook deliveries.

**Out of the clean base:** `github_installations` and every later `github_*` / review / embedding table. `vector` extension. `docs/review-pipeline/`. GitHub installations UI consumers. `tokens.revy.css`.

**Out of this program:** Irbene ontology, VIRAC files, Palantir drills, Polimi — those live in the **consumer**, not the template.

**Product grep (phase-owned, Q14):** path **and** content for `github_installation` / `features/installations` / `tokens.revy`.
- **P1:** `backend/`, `frontend/`, `deploy/` must be empty, plus `test ! -d docs/review-pipeline`. Do **not** grep `.cursor/` in P1 (rules still mention `tokens.revy.css` until P3).
- **P4 (after P3):** same as P1 **plus** `.cursor/`.
Do **not** use an unscoped repo-wide content grep (historical `docs/saas-base/` wave files may still mention the old strip).

**Coverage:** template must boot with Keycloak + Postgres + SPA login → `GET /api/v1/me` → `status: active` (Mode A).

---

## Edge cases

- **#32 vs older `auth.py` / `users.py`:** three-way conflicts; resolve toward #32 behaviour (single `provision_user_from_keycloak()`).
- **KC Dockerfile vymalo JARs:** #32 pins `0.10.0-rc.1`; must land in the template image, not only in Revy prod.
- **Bootstrap super_admin:** seed PG then same email in KC; #32 fails fast if env set without seed (staging/prod).
- **Migration rewrite vs existing Revy DBs:** new repo, empty DBs. Never run this chain against Revy staging.
- **Copy into `irbene_gate`:** whole tagged tree minus consumer-owned paths: do not overwrite `docs/vision.md`, `docs/platform-base/`, consumer `.env.example` (`VIRAC_*`), root learning `Pipfile`. **Merge** template `.gitignore` into the consumer file (keep learning-dir ignores). App Pipfile lives under `backend/`.
- **`tokens.revy.css`:** `--app-primary` already lives in `tokens.css`. P1 deletes the Revy file and the `@import` in `index.css`. Fold any leftover `--rv-*` map into `tokens.css`. No `tokens.app.css`.

---

## Decisions registry

| Q# | Question | Status | Resolution |
|----|----------|--------|------------|
| Q1 | Strip `main` vs rebuild from shell? | **locked** | Shell `saas-base-v1.1` + port #32 |
| Q2 | Where does the canonical base live? | **locked** | Template repo: private GitHub `raimondskrauklis/saas-base`; local `/Users/raimonds.krauklis/projects/saas-base`. P0–P4 here. |
| Q3 | Where do program docs live? | **locked** | `saas-base/docs/platform-base/` (template). `irbene_gate/docs/platform-base/` is a pointer only. |
| Q4 | Keep Stripe, impersonation, items? | **locked** | Yes. Stripe stays env-gated. |
| Q5 | GitHub installations / `vector` / LLM env? | **locked** | Strip, including live consumers (nav, dashboard, plan_gates, i18n). |
| Q6 | Alembic ids for webhook tables? | **locked** | Delete `2026_07_24_0300_0004_github_installations`. Set `2026_07_25_2217_0005_user_locale_timezone.down_revision = "2026_07_24_0200_0003_invitations"`. Add `2026_07_26_1900_0010_keycloak_webhook_deliveries` (parent `2026_07_25_2340_0009_impersonation_sessions`) then `2026_07_26_1910_0011_keycloak_webhook_deliveries_received_at_idx`. Do **not** keep `0019`/`0020`/`0018` ids. |
| Q7 | History in the new repo? | **locked** | Keep commits **through** `saas-base-v1.1`, not later review commits. No squash of that prefix. P0 overlay commit(s) on top are allowed; the tag still peels to `48c361e`. |
| Q8 | How `irbene_gate` consumes? | **locked** | Copy the **whole** tagged `saas-base-v2` tree into the consumer, minus Out-list (`docs/vision.md`, `docs/platform-base/`, `palantir/` `polimi/` `exercises/`, root learning `Pipfile`, consumer `.env.example`). **Merge** template `.gitignore` rules into the consumer file (keep learning-dir ignores; do not replace). Record upstream tag in consumer `docs/platform-base/`. Not a submodule. Not an enumerated-dir-only copy. |
| Q9 | Irbene ontology in this program? | **locked** | No |
| Q10 | Repo visibility / exact GitHub name | **locked** | Private `saas-base` under `raimondskrauklis` |
| Q11 | Historical Revy corpus on the v1.1 tag? | **locked** | **Delete** `docs/review-pipeline/`, `docs/starter-pack/REVY_PRODUCT_SLICE.md`, `docs/starter-pack/SCAFFOLD_P4_EXECUTION.md`. Retarget or drop inbound links in `docs/starter-pack/README.md` (those three are still listed as Active / P4 authority). Do not keep-with-grep-exclusions. Do not move to gitignored `internal-docs`. |
| Q12 | P5 copy shape | **locked** | Same as Q8: whole tree minus Out-list; merge `.gitignore`. |
| Q13 | Theme after deleting `tokens.revy.css` | **locked** | Fold leftover `--rv-*` into `tokens.css`. P1 drops file + `@import`. P3 retargets `.cursor/rules` (no GitHub installations; brand is `tokens.css`). Do **not** edit those rules in P1. |
| Q14 | Product grep `.cursor/` ownership? | **locked** | **Omit `.cursor/` until P4.** P1 = `backend/` `frontend/` `deploy/` + corpus delete. P4 (after P3) adds `.cursor/`. Do not split rule edits across P1 and P3. |
| Q15 | Template test / migrate DB? | **locked** | Four app DBs: `saas_base_dev` / `saas_base_test` / `saas_base_staging` / `saas_base_prod`. `ENVIRONMENT` selects the admin URL. Local Alembic: dev + `alembic -x test=true`. Production is upgraded on the droplet by GitHub Actions (`alembic upgrade head`, `ENVIRONMENT=production`). Initial topology is **one droplet = production**; a staging droplet comes later. Cursor / analysis uses `*_DATABASE_URL_READONLY`. Default unit tests stay mocked (Q16). |
| Q16 | Testing baseline before `saas-base-v2`? | **locked** | Finish the half-built kp/tender_pro pattern **in this template before the tag**, not inside P1–P3. L1 seed: user + workspace + membership, fixed UUIDs, `TEST_DATABASE_URL` only, DB name must contain `test`, idempotent upsert (not skip-if-any-row). `tests/api/` HTTP contract smokes (status / envelope / 401 / 403; cap 2–3 per route). Mocked `tests/unit/` stays default; a unit test **may** take `db_session` for SQL/constraints. Do **not** copy kp’s domain `seed_test_data.py`. Flip the “no `tests/api/`” rule. Empty `tests/service/` — do not add. **Playwright is out of P0–P6** (parking lot). |
| Q17 | Template Keycloak / how a new project starts? | **locked** | **No hosted saas-base product IdP.** Each clone owns app Postgres (dev+test) **and** its own Keycloak (own Keycloak database — never the app DB, never Revy). Template ships generic placeholders (`app` / `app-api` / `app-web`) plus start instructions — not a running public realm. `APP_REPLACE.md` + rewritten `DEV_BOOTSTRAP.md` / `KEYCLOAK_DEV_CHECKLIST.md` (P3). Strip Revy JDBC/hosts from `deploy/keycloak/config/.env.example`. Local Mode A = JIT; vymalo webhook is optional for a deployed Keycloak. |

---

## Parking lot

- Sync starter-pack templates in gitignored `revy/internal-docs/` after `saas-base-v2` (nice; not a gate for Irbene).
- Optional `saas-base-v2` pointer tag on `revy` (do not make `revy` the clone source).
- Later: how consumers pull base fixes (manual copy / subtree). Not v1.
- **Playwright E2E (deferred, do not drop):** after `saas-base-v2` Mode A is green, a follow-up program — 1–3 specs for Keycloak redirect → SPA callback → shell. Not a CI gate until KC is reliable. Vitest stays for components. Not a substitute for `tests/api/`. Do not start in P0–P6.

**Phase-0 prerequisites:** **done** (P0). Template repo exists; history through `saas-base-v1.1`; `docs/platform-base/` preserved; workflow pack installed.

---

## Devil's advocate

- Porting #32 onto July 25 auth is still a merge, not a checkout. If conflicts explode, the fallback is still **not** strip-`main`; it is port behaviour from #32 files by hand onto the shell.
- Genericizing every `revy` string will miss JSON i18n and nginx files. Grep is a gate, not a hope.
- Copying into `irbene_gate` without a `backend/` gitignore change will start tracking the app — intended. Learning dirs stay ignored.
- Two-repo drift: Irbene will patch the copy. Accept until a subtree policy exists.

---

## Experiment / verification

Pass/fail for **clean base / template repo** (P4 gate):

- `cd backend && pipenv run pytest tests/unit/ tests/api/ -q` green (`TEST_DATABASE_URL` set). **pass** (266).
- `cd frontend && npm test` green. **pass** (99).
- No Playwright config in this tag (`test ! -f frontend/playwright.config.ts`). **pass**.
- Product grep P1-tree empty (`backend/` `frontend/` `deploy/`); `.cursor/` empty (after P3); `docs/review-pipeline/` absent. **pass**.
- `alembic heads` = `2026_09_19_2000_0012_workspace_memberships_updated_at` (adds `workspace_memberships.updated_at` so TimestampedModel matches 0001); parent is `0011`. History has no `0004` github_installations file and no `0018`. **pass**.
- Mode A: register in this clone’s Keycloak (`start-dev` Path A, realm `app`, clients `app-web`/`app-api`) → SPA callback → `GET /api/v1/me` **200** and `users.status = active` on `saas_base_dev`. **pass** (JIT; webhook not required). First token had `email_verified=false` until the KC user was marked verified — same fail cause as DEV_BOOTSTRAP.
- Tag `saas-base-v2` peels to `b58c2925c96a1eacfb2ae79034e53f72d3fe7cf9`.

Pass/fail for **consumer repo** (`irbene_gate`, P6 gate):

- `backend/` + `frontend/` present; `docs/vision.md` still the Irbene north star.
- App boots locally against **new** DBs (not Revy’s). Login smoke same as above.
- No ontology tables.

---

## References

| What | Where |
|------|--------|
| Shell tag | `revy` `saas-base-v1.1` (`48c361e`) |
| Auth commit | `revy` `ed773f4` / PR #32 |
| SaaS program | `revy/docs/saas-base/README.md` (shipped W0–W8) |
| Provisioning | `revy/docs/authorization/USER_PROVISIONING_FINDINGS.md` |
| Scaffold | `revy/docs/starter-pack/README.md` |
| Irbene north star | `../irbene_gate/docs/vision.md` |
| Architecture review | [pass-01](./reviews/architecture-peer-review/pass-01-2026-09-19.md), [pass-02](./reviews/architecture-peer-review/pass-02-2026-09-19.md) |
| Skills used | `../agent-workflow` planning skills (findings written earlier via kp-platform copies) |
