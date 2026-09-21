# Agent guide — saas-base

Generic SaaS platform template (FastAPI + React + Keycloak). This is a public starting point, not a private product clone.

Coding rules: [.cursorrules](.cursorrules) and `.cursor/rules/` (modular `.mdc` files).

## Agent workflow

| Topic | File |
|-------|------|
| **Flow manifest** | [.agent/manifest.json](.agent/manifest.json) — `hosting`, `pack_source`, `default_scope` |
| **Skill catalog** | [.agent/skills.catalog.json](.agent/skills.catalog.json) |
| **Review context SSOT** | [.agent/review-context.json](.agent/review-context.json) |
| **Orchestration** | [docs/agents/README.md](docs/agents/README.md) |
| **Quick ref** | [docs/utils/CURSOR_AGENT_WORKFLOW.md](docs/utils/CURSOR_AGENT_WORKFLOW.md) |
| **Bugbot (pre-push)** | [.cursor/BUGBOT.md](.cursor/BUGBOT.md) |
| **Roles + verbs** | [docs/agents/prompts/ROLES.md](docs/agents/prompts/ROLES.md) |

Active LOOP program: see review-context SSOT → `active_program` (`null` when idle).

**LOOP contract:** The agent **executes until the program is done**. Do **not** ask “Continue?”. Local commit every phase. Before a later push: ensure CI green, then push. **Only pause:** migration subphase.

Read **only** the current `*_Pn_EXECUTION.md`. Each subphase Deliverable must be green before the next heading — then continue immediately.

### Skills (installed)

Full catalog: `.agent/skills.catalog.json`. Installed set in `.agent/manifest.json` → `skills.installed`.

| Tier | Skills |
|------|--------|
| **Meta** | `bootstrap-workflow` |
| **Core** | `phase-execution`, `ship-changes`, `chunk-execution` |
| **Planning** | `create-findings`, `create-general-plan`, `create-execution-plan`, `architecture-peer-review`, `execution-peer-review`, `devils-advocate`, `post-finish-gap-pass` |
| **Sentry** | `sentry-fix-issues` — one issue the user points at; never unprompted |

**Default gate:** local Bugbot before every ship.

**Pack:** sibling `../agent-workflow`. Re-audit: invoke `bootstrap-workflow`.

## Read first

| Topic | Where |
|-------|------|
| **Dev bootstrap** | [docs/starter-pack/DEV_BOOTSTRAP.md](docs/starter-pack/DEV_BOOTSTRAP.md) |
| **Keycloak (dev/prod)** | [docs/utils/KEYCLOAK_SETUP.md](docs/utils/KEYCLOAK_SETUP.md) — checklist: [KEYCLOAK_DEV_CHECKLIST.md](docs/starter-pack/KEYCLOAK_DEV_CHECKLIST.md) |
| **Registration flags** | [docs/starter-pack/REGISTRATION_FLAGS.md](docs/starter-pack/REGISTRATION_FLAGS.md) |
| **SaaS base (W0–W8, already in the shell)** | [docs/saas-base/README.md](docs/saas-base/README.md) |
| **Scaffold runbooks** | [docs/starter-pack/README.md](docs/starter-pack/README.md) |
| **Stripe billing setup** | [docs/utils/STRIPE_BILLING_SETUP.md](docs/utils/STRIPE_BILLING_SETUP.md) |
| **Mailgun + Keycloak SMTP** | [docs/utils/MAILGUN_SETUP.md](docs/utils/MAILCLOUD_SETUP.md) |
| **Env examples** | `deploy/env-examples/`, `backend/.env.example`, `frontend/.env.example` |

`internal-docs/` is gitignored and is **not** required to run this template.

## Cursor rules (modular)

| Rule | Scope |
|------|------|
| `.cursor/rules/00-core.mdc` | Always |
| `.cursor/rules/backend-python.mdc` | `backend/**` |
| `.cursor/rules/frontend-react.mdc` | `frontend/**` |
| `.cursor/rules/app-color-tokens.mdc` | `frontend/**/*.{tsx,ts,css}` |
| `.cursor/rules/app-i18n.mdc` | `frontend/**` |
| `.cursor/rules/testing.mdc` | tests |

Root [`.cursorrules`](.cursorrules) is a short pointer.

## Backend quick ref

- Stack: Python 3.12, FastAPI, SQLAlchemy 2.0 async, Pydantic v2, PostgreSQL, Celery.
- Errors: `app.core.exceptions` — never bare `HTTPException`.
- Auth: Keycloak JWT + async JWKS cache — `app/core/auth.py`, `app/core/jwks.py`.
- Lists: cursor pagination (`CursorParams`, `CursorResponse`).
- ORM: `*ORM` suffix, enums in `app/constants/enums.py` (`snake_case` values).
- Migrations: hand-written Alembic — **never** `--autogenerate`.
- Tests: `backend/tests/unit/` (mocked) + `backend/tests/api/` (HTTP smokes). No `tests/service/`.
- Run from `backend/`: `pipenv run lint`, `pipenv run pytest tests/unit/ tests/api/`.

## Frontend quick ref

- Stack: React 19, TypeScript strict, Vite, Tailwind 4, TanStack Query, Zustand (UI only).
- Tokens: `--app-*` in feature code.
- i18n: `t()` — EN + LV (`frontend/src/i18n/`).
- Dates/numbers: `@/lib/date`, `@/lib/locale`, `@/lib/number`.
- Inputs: `QuietInput`, `QuietSelect`, `QuietDateInput` from `@/components/ui/`.
- Errors: `mapApiError()` → `showDomainErrorToast()` (`@/shared/errors`).
- Run from `frontend/`: `npm run lint`, `npm test`, `npm run build`.

## First commands

See [DEV_BOOTSTRAP.md](docs/starter-pack/DEV_BOOTSTRAP.md).

```bash
# Backend (from backend/)
pipenv install && pipenv run uvicorn app.main:app --reload

# Frontend (from frontend/)
npm install && npm run dev
```
