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
| App databases | `app` / `app_test` | New DBs — never `saas_base*` and never Revy |
| Keycloak database | `app_keycloak` | New DB on the same cluster or local Postgres |
| DB role | `app` | New role |
| Export path | `/tmp/app/exports` | Your path |
| Volume / image | `/mnt/app_volume`, `app-keycloak:26.0`, `app-net`, `app-kc` | Your names |
| Compose API hostname | `backend` (TrustedHost + webhook URL) | Your API service name |

Do not copy another product’s realm, Keycloak JDBC URL, or app `DATABASE_URL`.

---

## Start a new clone (including this repo)

1. **Create databases** — two app DBs (dev + test) and one Keycloak DB. New roles. Never template `saas_base` / `saas_base_test` and never any `revy-*` database.
2. **Extensions + grants** — as doadmin, on **each app DB**: `uuid-ossp`, `pg_trgm`, `pgcrypto` (`deploy/sql/postgres-extensions.sql`). No `vector`. `GRANT USAGE, CREATE ON SCHEMA public` to the app role (PostgreSQL 15+ / DigitalOcean). Repeat Keycloak DB grants for the Keycloak role if KC uses managed Postgres.
3. **Migrate** — `cp backend/.env.example backend/.env`, set `DATABASE_URL` / `TEST_DATABASE_URL`, then from `backend/`: `pipenv run alembic upgrade head` and `pipenv run alembic -x test=true upgrade head`.
4. **Keycloak** — copy `deploy/keycloak/config/.env.example` → `.env`. Point `KC_DB_URL` at **that clone’s** Keycloak database (not the app DB). `docker network create app-net`, `docker compose build && docker compose up -d` from `deploy/keycloak/config/`.
5. **Realm + clients** — realm `app`; confidential `app-api`; public `app-web` with redirect `http://localhost:5173/*`. Audience/azp must match those client ids. See [KEYCLOAK_DEV_CHECKLIST.md](../starter-pack/KEYCLOAK_DEV_CHECKLIST.md).
6. **App env** — `cp frontend/.env.example frontend/.env.local`. Align `KEYCLOAK_*` / `VITE_KEYCLOAK_*`. Mode A: `REGISTRATION_REQUIRE_ADMIN_APPROVAL=false` and `REGISTRATION_REQUIRE_PROFILE_FORM=false`.
7. **Smoke (JIT)** — `uvicorn` + `npm run dev` → register in Keycloak → SPA callback → `GET /api/v1/me` returns `active` and a `users` row. The vymalo webhook listener is optional for local Mode A.

Production docker: `TRUSTED_HOSTS` must include the compose hostname Keycloak POSTs to (`backend` if `WEBHOOK_HTTP_BASE_PATH=http://backend:8000/...`).
