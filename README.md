# saas-base

Generic SaaS platform template (FastAPI + React + Keycloak). This is the reusable shell, not Revy.

History through tag `saas-base-v1.1`. First consumer after `saas-base-v2`: `../irbene_gate`.

## Quick start

1. [Dev bootstrap](docs/starter-pack/DEV_BOOTSTRAP.md) — env, DB, Keycloak, local API + frontend
2. [Keycloak checklist](docs/starter-pack/KEYCLOAK_DEV_CHECKLIST.md)
3. [Agent guide](AGENTS.md)

## Repo layout

| Path | Purpose |
|------|---------|
| `backend/` | FastAPI API (`pipenv`, Alembic, `tests/unit/`) |
| `frontend/` | React 19 + Vite SPA |
| `deploy/` | Env examples, SQL snippets, Keycloak |
| `docs/starter-pack/` | Committed scaffold runbooks |
| `docs/README.md` | Platform-base program (this template → Irbene copy) |

## This program

P0–P4 run here. P5–P6 copy `saas-base-v2` into `../irbene_gate`. See [docs/README.md](docs/README.md).
