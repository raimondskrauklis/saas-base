# Keycloak checklist

Configure realm and clients so browser tokens pass `app.core.auth` validation.

**Env canon:** `backend/.env.example`, `frontend/.env.example`  
**Audience logic:** `backend/app/core/auth.py` — allowlist `app-api` + `app-web`  
**Replace list / new clone:** [APP_REPLACE.md](../platform-base/APP_REPLACE.md)

Each clone has its **own** Keycloak (own Keycloak database). Do not share a realm with another product.

---

## Realm

| Setting | Value |
|---------|--------|
| Realm name | `app` |
| Login with email | On |
| Email as username | Recommended |
| Verify email | On (dev users: complete verification or relax required action) |

Backend: `KEYCLOAK_REALM=app`  
Production API (docker): `KEYCLOAK_URL=http://keycloak:8080` **and** `KEYCLOAK_ISSUER=https://auth.app.example.com/realms/app` (JWT `iss` from browser login uses the public host).  
Frontend: `VITE_KEYCLOAK_REALM=app`

---

## Client: `app-api` (confidential)

| Setting | Value |
|---------|--------|
| Client ID | `app-api` |
| Client authentication | On |
| Standard flow | Off (API client — tokens via service/user flows as needed) |
| Direct access grants | Off (prefer browser via `app-web`) |

**Backend env:**

```text
KEYCLOAK_CLIENT_ID=app-api
KEYCLOAK_CLIENT_SECRET=<from Keycloak credentials tab>
```

Service account / mapper: ensure access tokens intended for the API include audience or azp the backend accepts (see below).

---

## Client: `app-web` (public SPA)

| Setting | Value |
|---------|--------|
| Client ID | `app-web` |
| Client authentication | Off (public) |
| Standard flow | On |
| Valid redirect URIs | `http://localhost:5173/*`, `http://127.0.0.1:5173/*`, `https://app.example.com/*` |
| Web origins | `http://localhost:5173`, `http://127.0.0.1:5173`, `https://app.example.com` |

**Frontend env:**

```text
VITE_KEYCLOAK_CLIENT_ID=app-web
VITE_KEYCLOAK_URL=http://localhost:8080
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

**Production (placeholders — replace hosts):**

```text
VITE_KEYCLOAK_URL=https://auth.app.example.com
VITE_API_BASE_URL=https://app.example.com/api/v1
```

Keycloak is on a **dedicated subdomain** (`auth.app.example.com`), not a path on the app host (`/auth`). Nginx: `deploy/nginx/auth.app.example.com.conf`. TLS: DNS-01 — `docs/utils/CERTBOT_DIGITALOCEAN_DNS_RENEWAL.md`.

---

## JWT audience / azp (critical)

The API allowlist is `app-api` + `app-web` (`auth.py`).

**Required:** `azp` must be `app-web` (browser) or `app-api`.

**`aud` handling:**

- If `aud` is **omitted**, validation passes when `azp` is allowed.
- If `aud` is a **string**, it must be `app-api` or `app-web` — `aud: account` alone returns `Invalid token audience`.
- If `aud` is a **list**, at least one entry must be in the allowlist.

Browser tokens often include `aud: account`. Configure Keycloak so the access token either omits `aud`, includes `app-api` / `app-web` in `aud`, or use a mapper that adds the API client to audience.

**Verify after login** (decode access token at [jwt.io](https://jwt.io) or API logs):

- `iss` ends with `/realms/app`
- `azp` is `app-web`
- `email` / `sub` present

Failure symptom: `401` / `Invalid token audience` on `/api/v1/me`.

---

## Optional: bootstrap super admin

If using `BOOTSTRAP_SUPER_ADMIN_EMAIL`, register that exact email in Keycloak before first API login. See [DEV_BOOTSTRAP.md](./DEV_BOOTSTRAP.md).

---

## Optional: identity webhook (vymalo)

Local Mode A works with **JIT** (first `/me`). The Keycloak HTTP listener is optional until you deploy Keycloak that can POST to the API. See `deploy/keycloak/config/README.md`. Production: include `backend` in `TRUSTED_HOSTS`.

---

## Smoke

1. Login at `http://localhost:5173`
2. Authenticated `GET /api/v1/me` → `status: active` (Mode A) and a `users` row
3. No repeated 401 on API calls
