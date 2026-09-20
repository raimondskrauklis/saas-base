# Keycloak setup (local + production)

How to configure **this clone’s** Keycloak 26 realm so the SPA logs in, the API accepts JWTs, and the platform can **write** identity (disable user, logout sessions, execute-actions email).

Do not leave service-account roles as a clone footnote. Apply them on the Keycloak you run (local docker + production).

**Related:** [KEYCLOAK_DEV_CHECKLIST.md](../starter-pack/KEYCLOAK_DEV_CHECKLIST.md) (one-page smoke) · [APP_REPLACE.md](../platform-base/APP_REPLACE.md) · [MAILGUN_SETUP.md](./MAILGUN_SETUP.md) · [DEV_BOOTSTRAP.md](../starter-pack/DEV_BOOTSTRAP.md) · droplet bundle `deploy/keycloak/config/`

**Pattern:** `keycloak-js` + PKCE on the SPA; confidential `app-api`; JWKS validation in FastAPI (`backend/app/core/auth.py`, `jwks.py`). App authorization stays in PostgreSQL — not Keycloak realm roles.

---

## 1. What you are building

| Piece | Role |
|-------|------|
| Realm `app` | Isolated IdP for this product (own Keycloak database) |
| Client `app-web` | Public OIDC — React SPA, Authorization Code + **PKCE S256** |
| Client `app-api` | Confidential — JWT audience + **client-credentials Admin API** |
| Service account roles | `realm-management`: `manage-users`, `query-users`, `view-users` |
| SMTP | Realm Email tab — Mailgun SMTP so execute-actions actually send |

**URLs (placeholders — replace hosts):**

| Surface | URL |
|---------|-----|
| Public app | `https://app.example.com` |
| API | `https://app.example.com/api/v1` |
| Keycloak (browser) | `https://auth.app.example.com` (nginx → `127.0.0.1:8080`) |
| Keycloak (containers) | `http://keycloak:8080` |
| Issuer (`iss` in tokens) | `https://auth.app.example.com/realms/app` |
| JWKS | `{issuer}/protocol/openid-connect/certs` |

Path-based `/auth` on the app host is **not** used (`KC_HTTP_RELATIVE_PATH` unset). Each clone has its **own** Keycloak database. Do not share a realm with another product.

---

## 2. Local development

### 2.1 Fast path — `start-dev`

Good for first-hour realm clicks. Never on the droplet.

```bash
docker run --name app-kc-dev \
  -p 127.0.0.1:8080:8080 \
  -e KC_BOOTSTRAP_ADMIN_USERNAME=admin \
  -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak:26.0 \
  start-dev
```

Open `http://localhost:8080` → Admin Console (`admin` / `admin`). Create realm **`app`**. Configure §4–§6. Env:

```text
# frontend/.env.local
VITE_KEYCLOAK_URL=http://localhost:8080
VITE_KEYCLOAK_REALM=app
VITE_KEYCLOAK_CLIENT_ID=app-web
VITE_API_BASE_URL=http://localhost:8000/api/v1

# backend/.env
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=app
KEYCLOAK_CLIENT_ID=app-api
KEYCLOAK_CLIENT_SECRET=<Credentials tab>
KEYCLOAK_FRONTEND_CLIENT_ID=app-web
```

### 2.2 Prod-like — compose

Same JDBC + `start --optimized` as the droplet. From `deploy/keycloak/config/`:

```bash
cp .env.example .env   # chmod 600; edit passwords + KC_DB_URL
docker network create app-net 2>/dev/null || true
docker compose build && docker compose up -d
curl -sf http://127.0.0.1:9000/health/ready
```

Admin: `http://localhost:8080` (bootstrap creds in `.env`).

---

## 3. Production (droplet)

Copy `deploy/keycloak/config/` to `/mnt/app_volume/keycloak/config/`. Database is **managed Postgres, separate from the four app DBs**.

```text
KC_BOOTSTRAP_ADMIN_USERNAME=admin
KC_BOOTSTRAP_ADMIN_PASSWORD=<strong — rotate after first login>
KC_DB=postgres
KC_DB_URL=jdbc:postgresql://<host>:25060/keycloak?sslmode=require
KC_DB_USERNAME=keycloak
KC_DB_PASSWORD=<secret>
KC_HOSTNAME=https://auth.app.example.com
KC_HOSTNAME_STRICT=true
KC_HTTP_ENABLED=true
KC_PROXY_HEADERS=xforwarded
KC_HEALTH_ENABLED=true   # Dockerfile build-time
```

- Bind `127.0.0.1:8080` and `127.0.0.1:9000` only. Nginx: `deploy/nginx/auth.app.example.com.conf`. TLS: [CERTBOT_DIGITALOCEAN_DNS_RENEWAL.md](./CERTBOT_DIGITALOCEAN_DNS_RENEWAL.md).
- Memory limit **1 GB** on the Keycloak container.
- Backend on docker: `KEYCLOAK_URL=http://keycloak:8080` **and** `KEYCLOAK_ISSUER=https://auth.app.example.com/realms/app` (browser tokens use the public host).
- `VITE_KEYCLOAK_*` are **build-time** GitHub secrets. Changing them requires a frontend rebuild.

Do not use `start-dev` on the droplet. Do not set `KC_HTTP_RELATIVE_PATH`.

---

## 4. Realm

1. **Create realm** → name: `app` (clone: `irbene`, etc.). Do not put app users in `master`.
2. **Realm settings → Login:** Login with email **On**. Email as username **On** (recommended). Verify email **On**.
3. **Realm settings → Sessions:** access token lifespan **5–15 min**. SPA refresh handles the rest.
4. **Realm settings → Email:** Mailgun SMTP — [MAILGUN_SETUP.md](./MAILGUN_SETUP.md). Required for execute-actions and verify-email. Use **Test connection** then send a test to yourself.
5. Do **not** create realm roles `super_admin` / `admin` for API authz. App `platform_role` and workspace memberships live in PostgreSQL.

---

## 5. Client `app-web` (public SPA)

| Setting | Value |
|---------|--------|
| Client type | OpenID Connect |
| Client ID | `app-web` |
| Client authentication | **Off** (public) |
| Standard flow | **On** |
| Direct access grants | **Off** |
| Implicit flow | **Off** |
| Valid redirect URIs | `http://localhost:5173/*`, `http://127.0.0.1:5173/*`, `https://app.example.com/*` |
| Valid post logout redirect URIs | same hosts (empty list → logout error, SSO cookie survives, `check-sso` signs the user back in) |
| Web origins | `http://localhost:5173`, `http://127.0.0.1:5173`, `https://app.example.com` |
| Advanced → PKCE | Code challenge method **S256** |

**Credentials tab must not exist.** If it does, the client is still confidential — fix authentication Off and restart Keycloak.

SPA init (`frontend/src/lib/keycloak.ts`): `pkceMethod: 'S256'`, `onLoad: 'check-sso'`, `checkLoginIframe: false`.

---

## 6. Client `app-api` (confidential + Admin API)

### 6.1 Settings

| Setting | Value |
|---------|--------|
| Client ID | `app-api` |
| Client authentication | **On** |
| Standard flow | **Off** (API does not do browser redirects) |
| Direct access grants | **Off** |
| Implicit flow | **Off** |
| **Service accounts roles** | **On** — required |

Copy **Credentials → Client secret** to `KEYCLOAK_CLIENT_SECRET`. Never commit it.

### 6.2 Service account roles (required)

These roles let the backend call Keycloak Admin REST: GET user, GET-merge-PUT `enabled`, `POST …/logout`, `PUT …/execute-actions-email`.

1. **Clients** → `app-api` → **Service accounts roles** tab.
2. **Assign role**.
3. Filter by clients → **`realm-management`**.
4. Assign **all three**:

| Role | Why |
|------|-----|
| `manage-users` | Enable/disable, execute-actions (VERIFY_EMAIL, UPDATE_PASSWORD) |
| `query-users` | Lookup / list |
| `view-users` | Read profile + sessions |

Do **not** assign `realm-admin`. Optional later: `view-events` for webhook debugging.

Without these roles, client-credentials token succeeds and **GET/PUT `/admin/realms/{realm}/users/{id}` returns 403**. App mutations must fail closed — do not persist app-only suspend.

### 6.3 Audience so SPA tokens pass the API

Browser tokens often have `aud: account`. The API allowlist is `app-api` + `app-web` (`auth.py`). `azp` must be `app-web` (browser) or `app-api`.

Configure so access tokens include `app-api` (or omit `aud` and keep `azp` allowed):

1. **Client scopes** → Create `app-api-audience` (or add a mapper on `app-web`).
2. Mapper type **Audience**, included client audience **`app-api`**, add to access token **On**.
3. **Clients** → `app-web` → **Client scopes** → add that scope as **Default** (not optional).

Decode a token at [jwt.io](https://jwt.io) after login:

- `iss` ends with `/realms/app`
- `azp` is `app-web`
- `aud` includes `app-api` **or** `app-web`, or `aud` is omitted
- `email` and `sub` present

Failure: `401` / `Invalid token audience` on `/api/v1/me`.

---

## 7. Realm as code (first file: irbene_gate)

Console clicks (§4–§6) stay the source of truth for **what** to configure. A committed `*-realm.json` is **not** produced in saas-base during the mini-saas program.

**First live activation** is the consumer `../irbene_gate` (after this base’s next tag is copied there). There: follow this runbook until login + Admin API smokes pass, **then** export and commit the JSON. Also walk [MAILGUN_SETUP.md](./MAILGUN_SETUP.md) and the checklist — that is where the runbooks are proven, not invented.

Export (users skipped, secrets stripped):

```bash
docker compose exec keycloak /opt/keycloak/bin/kc.sh export \
  --realm irbene --file /tmp/irbene.json --users skip
# copy off the container; strip client secret; commit deploy/keycloak/import/
```

Later clones can `--import-realm` from that file. Keycloak skips import if the realm already exists ([import docs](https://www.keycloak.org/server/importExport)). Staging vs production differ only in redirect URIs / web origins. Set the API client secret **per environment** after import.

---

## 8. Bootstrap super admin

App `super_admin` is a PostgreSQL `platform_role`, not a Keycloak realm role.

1. `BOOTSTRAP_SUPER_ADMIN_EMAIL` in backend `.env` (temporary).
2. `pipenv run python -m scripts.seed_bootstrap_super_admin`
3. Register **that exact email** in Keycloak (registration or Admin Console).
4. First SPA login binds `keycloak_user_id` and sets `active`.
5. Remove the env var and restart the API.

---

## 9. Identity webhook (optional locally)

Local Mode A works with **JIT** on first `/me`. Production listener: vymalo in the Keycloak image — `deploy/keycloak/config/README.md`. Same secret in `KEYCLOAK_WEBHOOK_SECRET` and `WEBHOOK_HTTP_AUTH_PASSWORD`. `TRUSTED_HOSTS` must include the compose hostname Keycloak POSTs to (`backend`).

Inbound `ADMIN*` enable/disable is handled in `apply_keycloak_user_disabled` (status machine: disable only `active`→`suspended`; enable only `suspended`→`active`). Current `WEBHOOK_EVENTS_TAKEN` in `.env.example` lists user events only — inbound Admin Enable/Disable is **latent** until those events are added. Confirm event names against vymalo docs for your image version. First live apply is the clone after `saas-base-v3` (not this template’s local default).

App outbound suspend/reject/reactivate/approve: mutate the Postgres row in the **open** transaction → Keycloak Admin `enabled` (raise on HTTP/role errors) → `commit`. If commit fails after Admin succeeded, restore KC `enabled`. Session logout is not undoable. No committed app-only status.

---

## 10. Admin API smoke (after §6)

Client-credentials token, then GET the bootstrap user’s Keycloak id (`users.keycloak_user_id`):

```bash
TOKEN=$(curl -s -X POST \
  "$KEYCLOAK_URL/realms/app/protocol/openid-connect/token" \
  -d grant_type=client_credentials \
  -d client_id=app-api \
  -d client_secret="$KEYCLOAK_CLIENT_SECRET" | jq -r .access_token)

curl -sS -o /dev/null -w "%{http_code}\n" \
  -H "Authorization: Bearer $TOKEN" \
  "$KEYCLOAK_URL/admin/realms/app/users/$KEYCLOAK_USER_ID"
```

Expect **200**. **403** = service-account roles missing. **401** = wrong secret or Service accounts Off.

Logout (KC 26): `POST /admin/realms/app/users/{id}/logout`.  
Execute-actions: `PUT /admin/realms/app/users/{id}/execute-actions-email?client_id=app-web&redirect_uri=http://localhost:5173/login` with body `["UPDATE_PASSWORD"]`. If both query params are omitted, Keycloak sends the mail with **no return link**. SMTP must work first ([MAILGUN_SETUP.md](./MAILGUN_SETUP.md)).

GET-merge-PUT for `enabled`: GET the full user representation, change `enabled`, PUT the whole object. A body of `{ "enabled": false }` only is unsafe on Keycloak 26.

---

## 11. Troubleshooting

| Symptom | Fix |
|---------|-----|
| Redirect loop / Invalid redirect URI | Exact `http://localhost:5173/*` (or prod host) on `app-web` |
| Logout then immediately signed in | Set **Valid post logout redirect URIs** |
| CORS on token | **Web origins** on `app-web` |
| `Invalid token audience` | Audience mapper §6.3; `azp` allowlist |
| `iss` mismatch | `KC_HOSTNAME` = public HTTPS URL; backend `KEYCLOAK_ISSUER` matches token `iss` |
| `No suitable driver` JDBC | Set **`KC_DB=postgres`** explicitly |
| Admin API 403 | §6.2 three `realm-management` roles |
| execute-actions 4xx / no mail | Realm Email + Mailgun SMTP; EU host `smtp.eu.mailgun.org` |
| execute-actions link `iss` http vs https | Call Admin API with public hostname or send `X-Forwarded-Proto: https` so links match nginx TLS |
| 502 behind nginx | Container up; `X-Forwarded-*`; health on :9000 |
| UI still old Keycloak URL | Rebuild frontend — `VITE_*` not read on the droplet |

---

## 12. Security

- Never commit realm exports with secrets or production user passwords.
- Rotate `KC_BOOTSTRAP_ADMIN_PASSWORD` and `app-api` client secret after bootstrap.
- GitHub App / Stripe webhooks stay outside Keycloak (HMAC).
- Do not create or delete Keycloak users from the app console — JIT + workspace invitations already provision.
