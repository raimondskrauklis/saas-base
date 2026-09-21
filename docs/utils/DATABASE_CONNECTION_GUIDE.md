# PostgreSQL connection guide

How to connect to this template’s **DigitalOcean managed PostgreSQL 17** databases — for operators (migrations, grants) and for **retrieving / analysing data** (Cursor, pgAdmin, `psql`).

**Canonical env:** `backend/.env.example` → `backend/.env` (gitignored).  
**SQL:** `deploy/sql/postgres-extensions.sql` (app DBs) · `deploy/sql/postgres-readonly-role.sql` (analysis role)

---

## Two roles

| Role (this template) | Privilege | Used by |
|----------------------|-----------|---------|
| `saas_base-user-admin` | read-write + DDL | FastAPI, Celery, Alembic |
| `saas_base-user-readonly` | `SELECT` only | Cursor, pgAdmin analysis, ad hoc scripts |

FastAPI and Alembic use the **admin** URL for `ENVIRONMENT`. Local Alembic is development (and `-x test=true`). Production Alembic runs on the droplet via GitHub Actions. Cursor uses `*_DATABASE_URL_READONLY`.

**Build a read-only URL (separate env key — never overwrite the admin URL):** copy the admin URL into `*_DATABASE_URL_READONLY`. Change the user to `saas_base-user-readonly` and use that DigitalOcean user’s password. Keep host, port, database, `?ssl=require`. FastAPI and Alembic keep using `saas_base-user-admin`. Cursor always reads `database_url_readonly_for` / `*_READONLY`. DigitalOcean passwords are per user — swapping only the username on `DEV_DATABASE_URL` breaks the API.

```text
# admin (API / Alembic)
postgresql+asyncpg://saas_base-user-admin:ADMIN_PASS@HOST:25060/saas_base_dev?ssl=require
# analysis (Cursor) — same URL, different user (+ that user’s password)
postgresql+asyncpg://saas_base-user-readonly:READONLY_PASS@HOST:25060/saas_base_dev?ssl=require
```

---

## Environment variables

`ENVIRONMENT` selects the **process bind** (admin). Analysis URLs are independent — set the stages you need to inspect.

| Variable | Database | Who |
|----------|----------|-----|
| `DEV_DATABASE_URL` | `saas_base_dev` | API / Alembic when `ENVIRONMENT=development` |
| `TEST_DATABASE_URL` | `saas_base_test` | pytest fixtures; `alembic -x test=true` |
| `STAGING_DATABASE_URL` | `saas_base_staging` | Later: staging droplet (`ENVIRONMENT=staging`). Not the initial deploy. |
| `PRODUCTION_DATABASE_URL` | `saas_base_prod` | Production droplet. Migrated by GitHub Actions (`alembic upgrade head`). |
| `DEV_DATABASE_URL_READONLY` | `saas_base_dev` | Cursor / analysis |
| `TEST_DATABASE_URL_READONLY` | `saas_base_test` | Cursor / analysis |
| `STAGING_DATABASE_URL_READONLY` | `saas_base_staging` | Cursor / analysis |
| `PRODUCTION_DATABASE_URL_READONLY` | `saas_base_prod` | Cursor / analysis |

```text
ENVIRONMENT=development
DEV_DATABASE_URL=postgresql+asyncpg://saas_base-user-admin:****@….db.ondigitalocean.com:25060/saas_base_dev?ssl=require
TEST_DATABASE_URL=postgresql+asyncpg://saas_base-user-admin:****@….db.ondigitalocean.com:25060/saas_base_test?ssl=require
DEV_DATABASE_URL_READONLY=postgresql+asyncpg://saas_base-user-readonly:****@….db.ondigitalocean.com:25060/saas_base_dev?ssl=require
PRODUCTION_DATABASE_URL_READONLY=postgresql+asyncpg://saas_base-user-readonly:****@….db.ondigitalocean.com:25060/saas_base_prod?ssl=require
```

Resolve a read-only URL in Python (does not print secrets):

```python
from app.core.config import settings, database_url_readonly_for

url = database_url_readonly_for(settings, "production")  # or "development" / "test"
```

A leftover `DATABASE_URL` key is invalid — Settings forbids unknown keys.

---

## DigitalOcean: pooled vs direct

| Mode | Typical port | Use for |
|------|--------------|---------|
| **Connection pool** | `25060` | FastAPI runtime; Cursor analysis is fine on pooled |
| **Direct / session** | DO console “Connection parameters” | **Alembic**, extensions, grants, DDL |

Run local `pipenv run alembic upgrade head` with the **direct** admin URL for **dev**. Pooled DDL can look successful while nothing persists. Production DDL runs on the droplet (GitHub Actions), also with a direct URL in the droplet env file.

---

## Operator setup (once per database)

Run as **`doadmin`**, connected to the **target database** (not `defaultdb`). Repeat on each app DB. Keycloak has its own database and roles — not these.

### 1. Extensions

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

See `deploy/sql/postgres-extensions.sql`.

### 2. App role (read-write)

PostgreSQL 15+ / DO: `public` is owned by `pg_database_owner`. The app role needs `CREATE`:

```sql
GRANT CONNECT ON DATABASE saas_base_dev TO "saas_base-user-admin";
GRANT USAGE, CREATE ON SCHEMA public TO "saas_base-user-admin";
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "saas_base-user-admin";
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "saas_base-user-admin";
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO "saas_base-user-admin";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "saas_base-user-admin";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO "saas_base-user-admin";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO "saas_base-user-admin";
```

Repeat while connected to `saas_base_test`, `saas_base_staging`, and `saas_base_prod`. `GRANT CONNECT` can run from any database; schema grants must be on the target DB.

### 3. Read-only role (Cursor / analysis)

Create user `saas_base-user-readonly` in the DigitalOcean control panel (Users). Then run `deploy/sql/postgres-readonly-role.sql` as **doadmin** on **each** app database.

Tables are created by `saas_base-user-admin` (Alembic), so default privileges are granted **for that role**:

```sql
GRANT CONNECT ON DATABASE saas_base_dev TO "saas_base-user-readonly";
GRANT USAGE ON SCHEMA public TO "saas_base-user-readonly";
GRANT SELECT ON ALL TABLES IN SCHEMA public TO "saas_base-user-readonly";
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO "saas_base-user-readonly";
ALTER DEFAULT PRIVILEGES FOR ROLE "saas_base-user-admin" IN SCHEMA public
  GRANT SELECT ON TABLES TO "saas_base-user-readonly";
ALTER DEFAULT PRIVILEGES FOR ROLE "saas_base-user-admin" IN SCHEMA public
  GRANT SELECT ON SEQUENCES TO "saas_base-user-readonly";
```

**Verify** (connected as the read-only user, or as doadmin):

```sql
SELECT has_table_privilege('saas_base-user-readonly', 'users', 'SELECT');
SELECT has_table_privilege('saas_base-user-readonly', 'users', 'INSERT');  -- must be false
SELECT has_schema_privilege('saas_base-user-admin', 'public', 'CREATE');
```

---

## Retrieve and analyse (Cursor)

1. Copy the admin URL into a **new** `*_DATABASE_URL_READONLY` key. Replace user `saas_base-user-admin` → `saas_base-user-readonly`. Same host, port, database, `?ssl=require`. Password = the DO password for the read-only user. Do **not** change `DEV_DATABASE_URL` / `TEST_DATABASE_URL` / droplet admin URLs.
2. Connect with that URL. Database name in the URL is the database you query (`saas_base_prod`, not `defaultdb`).
3. Run `SELECT` only. Do not migrate, insert, update, or delete — and do not use the admin user for analysis.
4. Pick the stage explicitly: `database_url_readonly_for(settings, "production")` — do not reuse the API process bind.

Useful starting queries:

```sql
SELECT current_user, current_database();
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY 1;
SELECT version_num FROM alembic_version;

SELECT id, email, status, created_at FROM users ORDER BY created_at DESC LIMIT 20;
SELECT id, name, status FROM workspaces ORDER BY created_at DESC LIMIT 20;
```

## SSL (DigitalOcean)

Managed Postgres **requires TLS**. The query parameter is **client-specific** — this is the usual connect error.

| Client | Query string | Notes |
|--------|----------------|-------|
| FastAPI / Alembic (SQLAlchemy + asyncpg) | `?ssl=require` | Canonical app URL. Leave it on `*_DATABASE_URL`. |
| `psql` / libpq | `?sslmode=require` | `ssl=require` is not a libpq key. Strip `postgresql+asyncpg://` → `postgresql://`. |
| pgAdmin | SSL mode **Require** | Same host/port/db/user as the URL. |
| raw `asyncpg.connect` | **no** `ssl=` in the URL | `ssl=require` is sent as a server GUC → `CantChangeRuntimeParamError`. Pass TLS as a connect argument. |

Raw asyncpg (analysis scripts):

```python
import ssl
import asyncpg
from app.core.config import settings, database_url_readonly_for

url = database_url_readonly_for(settings, "production").replace("postgresql+asyncpg://", "postgresql://")
url = url.split("?", 1)[0]  # drop ?ssl=require
conn = await asyncpg.connect(url, ssl=ssl.create_default_context())
```

If that raises `CERTIFICATE_VERIFY_FAILED` (macOS Python often does not trust the DO CA):

```python
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
conn = await asyncpg.connect(url, ssl=ctx)
```

That still **encrypts**; it skips cert verification. Do not put `ssl=false` on a DO URL. Prefer the verified context when the CA is in the trust store.

`psql`:

```bash
psql "${DEV_DATABASE_URL_READONLY/postgresql+asyncpg:/postgresql:}" \
  -c "SELECT current_user, current_database();"
# if needed, rewrite ssl=require → sslmode=require in that string
```

---

## Migrations (Alembic) — admin URLs only

**Laptop** (prove the chain):

```bash
pipenv run alembic upgrade head
pipenv run alembic current
pipenv run alembic -x test=true upgrade head
```

**Production** — `.github/workflows/deploy.yml` SSHs to the droplet and runs `alembic upgrade head` with that host’s env file (`ENVIRONMENT=production` → `PRODUCTION_DATABASE_URL`). Do not migrate production from a laptop.

**Staging droplet** — not initial. One droplet = production until you add a second host; then the same GitHub Actions pattern with `ENVIRONMENT=staging`.

Hand-written revisions only — **no** `--autogenerate`. Revision ids: `YYYY_MM_DD_HHMM_NNNN_slug`.

Default Alembic uses `VARCHAR(32)`. This repo’s ids are longer. `RevyPostgresqlImpl` (`backend/app/core/alembic_postgresql.py`) uses **`VARCHAR(128)`**; `alembic/env.py` widens an existing `VARCHAR(32)` column before migrating.

---

## App schema (analysis)

| Table | Contents |
|-------|----------|
| `users` | Keycloak-linked accounts, `user_status` |
| `workspaces` | Tenants |
| `workspace_memberships` | User ↔ workspace + `user_role` |
| `workspace_invitations` | Invites |
| `items` | Starter-pack demo CRUD |
| `api_audit` | Request audit |
| `stripe_webhook_events` | Stripe idempotency |
| `data_export_jobs` | Account export jobs |
| `impersonation_sessions` | Support impersonation |
| `keycloak_webhook_deliveries` | Keycloak webhook idempotency |
| `alembic_version` | Migration head |

Enums: `user_role`, `user_status`, `workspace_status`, `platform_role`.

---

## Troubleshooting

| Issue | What to check |
|-------|----------------|
| `permission denied for schema public` | App role: `GRANT CREATE` on **this** database |
| `permission denied for table` as readonly | Grants from `postgres-readonly-role.sql` on **this** database; default privileges **for** `saas_base-user-admin` |
| `has_schema_privilege` true in pgAdmin but false from app | Wrong database (`defaultdb` vs `saas_base_dev`) or wrong role |
| `StringDataRightTruncationError` on `version_num` | Alembic impl + widen helper (see above) |
| Migrations log success but no tables | Pooled URL used for Alembic — switch to **direct** |
| `CREATE EXTENSION` fails for app user | Run extensions as **doadmin** first |
| `CantChangeRuntimeParamError` (`ssl`) | Raw asyncpg: drop `?ssl=require` from the URL; pass `ssl=` (see SSL section) |
| `CERTIFICATE_VERIFY_FAILED` | Verified context vs DO CA — unverified `SSLContext` encrypts but skips verify (see SSL section) |
| `sslmode` errors in `psql` | Use `sslmode=require`, not `ssl=require` |
| Connection refused | DO trusted sources / firewall; VPN |
