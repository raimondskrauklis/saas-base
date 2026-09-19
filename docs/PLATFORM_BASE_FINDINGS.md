# Platform base — findings

Baseline for a **clean reusable SaaS template** (then copy into `irbene_gate`). **No execution steps.**

**Status:** baseline-ready for general plan (2026-09-19).  
**Codebase verified:** local `/Users/raimonds.krauklis/projects/revy` (same as `github.com/raimondskrauklis/revy`).  
**Not verified:** a live DB for `saas-base-v1.1` (none required; this is a new tree).

Revy was built to **spin any upcoming platform**. The shell was tagged. Full user provisioning was **not** tagged — it shipped on the reviewer tree. This program freezes that missing cut: shell + auth, no Revy product.

---

## Build principles

- **Cleaner template over faster strip.** Do not clone `main` and delete review code. Start from the frozen shell and **add** auth.
- **Two artefacts, two homes.** This repo **is** the canonical template. `../irbene_gate` **consumes** a tagged release (`saas-base-v2`). Program docs live in `docs/` here.
- **Keycloak = identity, PostgreSQL = lifecycle + RBAC.** Same as starter-pack `AUTHZ_MODEL.md`. Do not read KC realm roles in FastAPI.
- **Subtract product, not SaaS.** GitHub installations are Revy. Stripe, impersonation, items demo, settings, platform admin stay (env-gate Stripe).
- **Hand-written Alembic.** Retarget chains; do not keep review-era revision ids (`0019` / `0018`).
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
| **Consumer** | A product repo that copies a `saas-base-v2` tree (`irbene_gate` is the first). |
| **starter-pack (docs)** | `revy/internal-docs/starter-pack/` — **gitignored**, not on GitHub. Runnable app at the tag **is** `backend/` + `frontend/` in git. Do not require `internal-docs` to scaffold the new repo. |

---

## What exists vs genuinely new

### Verified — frozen shell (`saas-base-v1.1` = `48c361e`)

| Layer | What | Evidence |
|-------|------|----------|
| History | Initial `0db2f60` → scaffold P1–P4 → saas W0–W8 → tag | `git log --reverse`; tag message on `48c361e` |
| Auth (incomplete) | OIDC JWT, JWKS, login SPA, Mode A/B flags, JIT user on first `/me` | `backend/app/core/auth.py`; `frontend/src/lib/keycloak.ts`; `docs/starter-pack/REGISTRATION_FLAGS.md` |
| SaaS W0–W8 | Settings, dashboard, Stripe (default off), lifecycle, impersonation, platform admin | `docs/saas-base/README.md`; migrations `0005`–`0009` |
| Items demo | CRUD + cursor list | `0002_p1_items`; `backend/app/api/v1/items.py` |
| Alembic head | `0009_impersonation_sessions` | `revision = "2026_07_25_2340_0009_impersonation_sessions"` |
| Product mixed in | `0004_github_installations`; FE `features/installations/`; `registerRevy.ts` (GitHub + plan widgets) | `backend/alembic/versions/2026_07_24_0300_0004_github_installations.py`; `frontend/src/platform/extensions/registerRevy.ts` |
| Brand leak | `revy.createit.digital`, realm/env `revy`, `revy_*` config, `tokens.revy.css` | `deploy/nginx/`; `backend/app/core/config.py` (github/moonshot/voyage/revy_* keys) |
| Extensions SQL | `vector` + uuid-ossp + pg_trgm + pgcrypto | `deploy/sql/postgres-extensions.sql` — `vector` is review-era, unused by shell schema |
| File count | 462 files; 161 backend `.py` | vs `main` 1076 / 394 |
| `internal-docs/` | **Not in git** | `revy/.gitignore` `/internal-docs/` |

### Verified — Auth #32 (`ed773f4`, 2026-07-26)

| Claim | Evidence |
|-------|----------|
| **Not** in `saas-base-v1`, `v1.1`, or `review-r5-v1` | `git merge-base --is-ancestor` |
| Sits **after** R0–R8 on `main` (30 commits after `saas-base-v1`) | `git log saas-base-v1..ed773f4` |
| **No** GitHub/review paths in the commit | `git show ed773f4 --name-only` |
| Alembic `0019` parents **review** revision `0018_github_pull_request_is_draft` | file header in that commit |
| Overlap with shell (conflicts likely) | `webhooks/__init__.py` (Stripe only at v1.1), `auth.py`, `config.py`, `users.py`, `invitations.py`, `main.py`, `AuthContext.tsx`, i18n, KC Dockerfile |

### Verified — this repo (`irbene_gate`)

| Claim | Evidence |
|-------|----------|
| No app tree | `backend/` / `frontend/` absent |
| Product north star | `docs/vision.md` |
| Learning tracks gitignored | `.gitignore` `/exercises/` `/palantir/` `/polimi/` |
| Env placeholders only | `.env.example` `VIRAC_*` / `POLIMI_DATABASE_URL` |

### Genuinely new (this program)

- New GitHub repo + local clone that **stops** at shell history.
- Drop `0004` and retarget `0005` → `0003`.
- Port #32 as **`0010` + `0011`** on `0009`, not `0019`/`0020`.
- Generic brand + drop `vector` / GitHub / LLM env.
- Copy tagged tree into `irbene_gate` without eating `docs/vision.md` or learning dirs.

### Reuse caveats / traps

| Trap | Detail |
|------|--------|
| **“Strip `main`”** | Auth is already there, but 109 `github` paths vs 7 at the shell. Alembic still knows every `github_*` table. **Rejected** (user: cleaner template). |
| **Cherry-pick #32 as-is** | `down_revision` is `0018` (review). Must rewrite ids. `webhooks/__init__.py` on `main` also exports GitHub; at v1.1 it is Stripe-only — merge carefully. |
| **Keep `0004` “empty”** | Leaves `github_installations` in every consumer DB. **Remove** the revision; rewrite `0005.down_revision`. |
| **`registerRevy.ts` on `main`** | Later gained reviewer widgets. At **v1.1** it is installations + `PlanSummaryWidget` only. Keep plan widget; drop GitHub registrations; rename file. |
| **`internal-docs` missing on GitHub** | Fresh clone of `revy` has the **app**, not the private pack. Copy from the **tag’s tracked files**, not from gitignored pack. |
| **JIT vs webhook** | Shell already inserts user on first JWT. #32 adds webhook-primary + JIT fallback. Both belong in the clean base. |
| **Stripe** | W4 is in the shell, `stripe_enabled: bool = False`. Keep. Do not strip for VIRAC. |
| **irbene_gate as template** | Mixed product + Polimi + Palantir drills. **Never** the canonical base. |

---

## Catalog — workstreams

| Track | Why | Method |
|-------|-----|--------|
| **A. Clean base repo** | Reuse for Palantir, VIRAC, next app | New repo from `saas-base-v1.1` history; strip product; port #32; genericize; tag `saas-base-v2` |
| **B. This repo consumes** | Irbene Gate needs a running factory before ontology | Copy `saas-base-v2` into `irbene_gate`; overlay name/realm only |

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

**Out of the clean base:** `github_installations` and every later `github_*` / review / embedding table. `vector` extension.

**Out of this program:** Irbene ontology, VIRAC files, Palantir drills, Polimi.

**Coverage:** template must boot with Keycloak + Postgres + SPA login → `GET /api/v1/me` → `status: active` (Mode A).

---

## Edge cases

- **#32 vs older `auth.py` / `users.py`:** three-way conflicts; resolve toward #32 behaviour (single `provision_user_from_keycloak()`).
- **KC Dockerfile vymalo JARs:** #32 pins `0.10.0-rc.1`; must land in the template image, not only in Revy prod.
- **Bootstrap super_admin:** seed PG then same email in KC; #32 fails fast if env set without seed (staging/prod).
- **Migration rewrite vs existing Revy DBs:** new repo, empty DBs. Never run this chain against Revy staging.
- **Copy into `irbene_gate`:** do not overwrite `docs/vision.md`, `docs/platform-base/`, `.gitignore` learning entries, root `Pipfile` (numpy/matplotlib learning). App Pipfile lives under `backend/`.

---

## Decisions registry

| Q# | Question | Status | Resolution |
|----|----------|--------|------------|
| Q1 | Strip `main` vs rebuild from shell? | **locked** | Shell `saas-base-v1.1` + port #32 |
| Q2 | Where does the canonical base live? | **locked** | New private GitHub repo `raimondskrauklis/saas-base`; local `/Users/raimonds.krauklis/projects/saas-base`; **fresh Cursor window** for P0–P4 |
| Q3 | Where do program docs live? | **locked** | `saas-base/docs/` (this repo). `irbene_gate/docs/platform-base/` is a pointer only. |
| Q4 | Keep Stripe, impersonation, items? | **locked** | Yes. Stripe stays env-gated. |
| Q5 | GitHub installations / `vector` / LLM env? | **locked** | Strip |
| Q6 | Alembic ids for webhook tables? | **locked** | New `0010` + `0011` after `0009`; delete `0004`; `0005.down_revision = 0003` |
| Q7 | History in the new repo? | **locked** | Keep commits **through** `saas-base-v1.1`, not later review commits. No squash of that prefix. |
| Q8 | How `irbene_gate` consumes? | **locked** | Copy tagged `saas-base-v2` tree in. Record upstream tag in `docs/platform-base/`. Not a submodule. |
| Q9 | Irbene ontology in this program? | **locked** | No |
| Q10 | Repo visibility / exact GitHub name | **locked** | Private `saas-base` under `raimondskrauklis` |

---

## Parking lot

- Sync starter-pack templates in gitignored `revy/internal-docs/` after `saas-base-v2` (nice; not a gate for Irbene).
- Optional `saas-base-v2` pointer tag on `revy` (do not make `revy` the clone source).
- Later: how consumers pull base fixes (manual copy / subtree). Not v1.

**Phase-0 prerequisites:** GitHub repo `raimondskrauklis/saas-base` (human, private); this working tree already exists with `docs/`. Preserve `docs/` when importing shell history. Agent workflow pack: sibling `../agent-workflow`.

---

## Devil's advocate

- Porting #32 onto July 25 auth is still a merge, not a checkout. If conflicts explode, the fallback is still **not** strip-`main`; it is port behaviour from #32 files by hand onto the shell.
- Genericizing every `revy` string will miss JSON i18n and nginx files. Grep is a gate, not a hope.
- Copying into `irbene_gate` without a `backend/` gitignore change will start tracking the app — intended. Learning dirs stay ignored.
- Two-repo drift: Irbene will patch the copy. Accept until a subtree policy exists.

---

## Experiment / verification

Pass/fail for **clean base** (P4 gate):

- `cd backend && pipenv run pytest tests/unit/ -q` green on the new repo.
- No path match `github_installation` / `features/installations` / `tokens.revy`.
- `alembic heads` = webhook `0011` only; `alembic history` has no `0004` and no `0018`.
- Mode A: register in KC → SPA callback → `GET /api/v1/me` returns `active` **and** a `users` row (webhook and/or JIT).

Pass/fail for **this repo** (P6 gate):

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
| Irbene north star | `docs/vision.md` |
| Skills used | `kp-platform/.cursor/skills/create-findings/SKILL.md`, `create-general-plan/SKILL.md` |
