# Dev bootstrap checklist

Operator runbook: PostgreSQL 17, **this clone’s** Keycloak, local Redis, API + SPA. **Mode A** (open registration, no admin approval, no profile form).

**Replace list + numbered start steps:** [APP_REPLACE.md](../platform-base/APP_REPLACE.md)  
**Related:** [REGISTRATION_FLAGS.md](./REGISTRATION_FLAGS.md) · [KEYCLOAK_DEV_CHECKLIST.md](./KEYCLOAK_DEV_CHECKLIST.md) · [DATABASE_CONNECTION_GUIDE.md](../utils/DATABASE_CONNECTION_GUIDE.md)

This template does not ship a running public Keycloak. Bring up your own IdP against your own Keycloak database.

---

## Prerequisites

- PostgreSQL cluster with **four app databases** (dev, test, staging, prod) and **one Keycloak database** — app role plus a **read-only** role for analysis
- Docker (local Redis; Keycloak compose in `deploy/keycloak/config/`)
- `pipenv`, Node 24 LTS+

---

## 1. Env files

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

Set `ENVIRONMENT=development`, `DEV_DATABASE_URL`, `TEST_DATABASE_URL`, matching `*_DATABASE_URL_READONLY` (separate keys — do not overwrite admin URLs), `KEYCLOAK_*`, `SECRET_KEY`. `Settings` **forbids** unknown keys. Analysis: [DATABASE_CONNECTION_GUIDE.md](../utils/DATABASE_CONNECTION_GUIDE.md).

Mode A (must match frontend — [REGISTRATION_FLAGS.md](./REGISTRATION_FLAGS.md)):

```text
REGISTRATION_REQUIRE_ADMIN_APPROVAL=false
REGISTRATION_REQUIRE_PROFILE_FORM=false
```

`ENVIRONMENT` selects the process bind (`development` → `DEV_DATABASE_URL`). Local Alembic uses that URL; `alembic -x test=true` uses `TEST_DATABASE_URL`. Production is migrated by GitHub Actions on the droplet (`alembic upgrade head` with `ENVIRONMENT=production` in the droplet env file). Do not migrate production from a laptop.

Verify:

```bash
cd backend && pipenv run python -c "from app.core.config import settings; print(settings.environment, settings.database_url.rsplit('/', 1)[-1])"
```

---

## 2. PostgreSQL extensions (doadmin)

On **each app database**, as **doadmin**:

```bash
cat deploy/sql/postgres-extensions.sql
```

Must include: `uuid-ossp`, `pg_trgm`, `pgcrypto`. **No `vector`.**

Grant the app role `USAGE, CREATE` on `public` — [DATABASE_CONNECTION_GUIDE.md](../utils/DATABASE_CONNECTION_GUIDE.md).

---

## 3. Migrations

From `backend/`, use the **direct** (non-pooled) connection URL in `.env` for DDL:

```bash
cd backend
pipenv run alembic upgrade head
pipenv run alembic current
pipenv run alembic -x test=true upgrade head
```

Production schema is applied by `.github/workflows/deploy.yml` on the droplet. A staging droplet is not part of the initial topology.

Online migrations use `AUTOCOMMIT` in `backend/alembic/env.py`.

---

## 4. Local Redis

```bash
cd backend
docker compose up -d
docker compose ps   # redis healthy
```

---

## 5. Keycloak

Follow [KEYCLOAK_DEV_CHECKLIST.md](./KEYCLOAK_DEV_CHECKLIST.md) and `deploy/keycloak/config/README.md`. Point Keycloak at **this clone’s** Keycloak database.

Optional bootstrap: set `BOOTSTRAP_SUPER_ADMIN_EMAIL`, run `cd backend && pipenv run python -m scripts.seed_bootstrap_super_admin`, then remove the env var after first login. Register the **same email** in Keycloak.

---

## 6. Start API and frontend

```bash
# Terminal 1 — API
cd backend && pipenv run uvicorn app.main:app --reload --port 8000

# Terminal 2 — SPA
cd frontend && npm run dev
```

---

## 7. Smoke (Mode A, JIT)

| Step | Pass criteria |
|------|----------------|
| Open `http://localhost:5173` | Login page loads |
| Sign in / register via Keycloak | Redirect back without console auth errors |
| `GET http://localhost:8000/health` | `200` |
| Browser → API `GET /api/v1/me` (authenticated) | `200`, `"status": "active"`, a `users` row |
| Dashboard | Loads after login |

**Fail common causes:**

- `Invalid token audience` — client ids / realm mismatch; see Keycloak checklist.
- `permission denied for schema public` — DB grants on the correct database/user.
- `pending_email_verification` — verify email in Keycloak or disable required action for dev.

Webhook listener is **not** required for this smoke.

---

## 8. Celery (export + maintenance)

```bash
cd backend
pipenv run celery -A app.workers.celery_app worker -Q maintenance,default --loglevel=info
```

`EXPORT_STORAGE_PATH` default `/tmp/app/exports`. Production: `deploy/env-examples/backend.env.production.example`.

---

## Phase gate (automated — no Keycloak required)

```bash
cd backend && pipenv run lint && pipenv run pytest tests/unit/ -q
cd frontend && npm run lint && npm test -- --run
```
