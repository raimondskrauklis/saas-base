# Environment templates

Canonical env examples. Copy from here — do not commit real `.env` files.

**Initial topology:** one droplet = production. A staging droplet is added later (second host / load balancer), not at first deploy.

## Where variables live

| Group | Local dev | Production droplet (initial) | GitHub Actions |
|-------|-----------|------------------------------|----------------|
| Backend | `backend/.env` | `/mnt/app_volume/backend/.env` | `CI_*` test secrets; deploy SSHs to the droplet |
| Frontend `VITE_*` | `frontend/.env.local` | Baked at CI build — **not** on droplet | Repository secrets |
| Keycloak | — | `/mnt/app_volume/keycloak/config/` | `deploy/keycloak/config/` |
| Deploy | — | — | `DOCR_TOKEN`, `DROPLET_IP`, `SSH_PRIVATE_KEY` |
| Nginx vhosts | — | `/etc/nginx/sites-available/` | `deploy/nginx/*.conf` |

Production frontend is static `serve -s dist` — changing `VITE_*` requires **rebuild + redeploy** of `app-web`.

**Production URLs (placeholders):** SPA/API `https://app.example.com`, Keycloak `https://auth.app.example.com` (not `/auth` on the app host).

Laptop `ENVIRONMENT=development` → `DEV_DATABASE_URL`. The production droplet file has `ENVIRONMENT=production` → `PRODUCTION_DATABASE_URL`. GitHub Actions runs `alembic upgrade head` on that droplet — not from a laptop. `backend.env.staging.example` is for a later second droplet.

## Files

| File | Copy to |
|------|---------|
| `backend/.env.example` | `backend/.env` (local dev — canonical) |
| `backend.env.staging.example` | Later: staging droplet `/mnt/app_volume/backend/.env` (not initial) |
| `backend.env.production.example` | production droplet `/mnt/app_volume/backend/.env` (initial deploy) |
| `frontend.env.local.example` | `frontend/.env.local` |
| `frontend.env.production.example` | GitHub Actions secrets (build-time `VITE_*`) |
| `github-actions.secrets.example` | GitHub → Settings → Secrets checklist |
| `deploy.workflow.env.example` | Reference for `.github/workflows/deploy.yml` |

## Quick start (local)

```bash
cp backend/.env.example backend/.env
# Set ENVIRONMENT=development plus DEV_DATABASE_URL / TEST_DATABASE_URL (see deploy/sql/postgres-extensions.sql)
docker compose -f backend/docker-compose.yml up -d   # Redis only
```

Generate `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```
