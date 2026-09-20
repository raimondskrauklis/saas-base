# App replace list and start recipe

This template is **not** a hosted product. There is no shared saas-base Keycloak. Each clone owns Postgres **and** Keycloak.

Placeholders in env, compose, and nginx:

| Key | Placeholder | Replace with |
|-----|-------------|--------------|
| App display name | `App` (`app_name`, i18n as needed) | Product name |
| Realm | `app` | e.g. `irbene` |
| API client (confidential) | `app-api` | e.g. `irbene-api` |
| SPA client (public) | `app-web` | e.g. `irbene-web` |
| App host | `app.example.com` | Your public hostname |
| Keycloak host | `auth.app.example.com` | Dedicated auth subdomain |
| App databases | `saas_base_dev` / `_test` / `_staging` / `_prod` | Your four app DBs |
| Keycloak database | Own DB (not one of the four app DBs) | Keycloak JDBC only |
| App role | `saas_base-user-admin` | Read-write (API + Alembic) |
| Analysis role | `saas_base-user-readonly` | `SELECT` only — Cursor |
| DB env vars | `DEV_` / `TEST_` / `STAGING_` / `PRODUCTION_DATABASE_URL` | `ENVIRONMENT` selects the process bind |
| Analysis env vars | `*_DATABASE_URL_READONLY` | Separate keys; Cursor `SELECT` only |
| Export path | `/tmp/app/exports` | Your path |
| Volume / image | `/mnt/app_volume`, `app-keycloak:26.0`, `app-net`, `app-kc` | Your names |
| Compose API hostname | `backend` (TrustedHost + webhook URL) | Your API service name |

Use this clone’s realm, Keycloak JDBC URL, and app database URLs.

---

## Start a new clone (including this repo)

1. **Create databases** — four app DBs (dev, test, staging, prod) and one Keycloak DB. Create roles `saas_base-user-admin` (read-write) and `saas_base-user-readonly` (`SELECT`). This template’s names: `saas_base_dev` / `saas_base_test` / `saas_base_staging` / `saas_base_prod`. A new product uses its own four names.
2. **Extensions + grants** — as doadmin, on **each app DB**: `uuid-ossp`, `pg_trgm`, `pgcrypto` (`deploy/sql/postgres-extensions.sql`). No `vector`. `GRANT USAGE, CREATE ON SCHEMA public` to the app role (PostgreSQL 15+ / DigitalOcean). Then `deploy/sql/postgres-readonly-role.sql`. Repeat Keycloak DB grants for the Keycloak role if KC uses managed Postgres.
3. **Migrate** — `cp backend/.env.example backend/.env`. Set `ENVIRONMENT=development` plus `DEV_DATABASE_URL` and `TEST_DATABASE_URL`. `Settings` forbids unknown keys. From `backend/`: `pipenv run alembic upgrade head` and `pipenv run alembic -x test=true upgrade head`. Production is migrated by GitHub Actions on the droplet (`alembic upgrade head` with `ENVIRONMENT=production`). Initial deploy is **one production droplet**; add a staging droplet later if you need it.
4. **Keycloak** — copy `deploy/keycloak/config/.env.example` → `.env`. Point `KC_DB_URL` at **that clone’s** Keycloak database (not the app DB). `docker network create app-net`, `docker compose build && docker compose up -d` from `deploy/keycloak/config/`.
5. **Realm + clients** — realm `app`; confidential `app-api` with **Service accounts ON** and `realm-management` roles `manage-users`, `query-users`, `view-users`; public `app-web` with redirect `http://localhost:5173/*`. Audience/azp must match those client ids. SMTP on the realm for execute-actions. Full clicks: [KEYCLOAK_SETUP.md](../utils/KEYCLOAK_SETUP.md). Cheat sheet: [KEYCLOAK_DEV_CHECKLIST.md](../starter-pack/KEYCLOAK_DEV_CHECKLIST.md). Mail: [MAILGUN_SETUP.md](../utils/MAILGUN_SETUP.md).
6. **App env** — `cp frontend/.env.example frontend/.env.local`. Align `KEYCLOAK_*` / `VITE_KEYCLOAK_*`. Mode A: `REGISTRATION_REQUIRE_ADMIN_APPROVAL=false` and `REGISTRATION_REQUIRE_PROFILE_FORM=false`.
7. **Smoke (JIT)** — `uvicorn` + `npm run dev` → register in Keycloak → SPA callback → `GET /api/v1/me` returns `active` and a `users` row. The vymalo webhook listener is optional for local Mode A.

Production docker: `TRUSTED_HOSTS` must include the compose hostname Keycloak POSTs to (`backend` if `WEBHOOK_HTTP_BASE_PATH=http://backend:8000/...`).
