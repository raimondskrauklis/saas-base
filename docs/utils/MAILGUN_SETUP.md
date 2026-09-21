# Mailgun setup (app HTTP API + Keycloak SMTP)

This template uses Mailgun in **two different ways**. Mixing them up is the usual failure: the HTTP **API key** does not work as Keycloak’s SMTP password.

| Channel | Who sends | Credential | Host (EU) | Host (US) |
|---------|-----------|------------|-----------|-----------|
| **HTTP API** | FastAPI (`EMAIL_PROVIDER=mailgun`) — invitations, app mail | `MAILGUN_API_KEY` | `https://api.eu.mailgun.net/v3` | `https://api.mailgun.net/v3` |
| **SMTP** | Keycloak — verify email, execute-actions (`UPDATE_PASSWORD`, `VERIFY_EMAIL`) | Domain **SMTP** user + password | `smtp.eu.mailgun.org` | `smtp.mailgun.org` |

This clone’s env defaults to **EU** (`MAILGUN_REGION=eu`). EU domains **fail** against `smtp.mailgun.org` (often a silent close). Use `smtp.eu.mailgun.org`.

**Related:** [KEYCLOAK_SETUP.md](./KEYCLOAK_SETUP.md) §4 Email · `backend/app/core/email/providers/mailgun.py` · `backend/.env.example`

Official: [SMTP credentials](https://help.mailgun.com/hc/en-us/articles/203380100-Where-can-I-find-my-API-keys-and-SMTP-credentials) · [Send via SMTP](https://documentation.mailgun.com/docs/mailgun/user-manual/sending-messages/send-smtp) · [Keycloak realm email](https://www.keycloak.org/docs/latest/server_admin/#_email)

---

## 1. Domain

1. Mailgun → **Sending → Domains** → add `mg.app.example.com` (or the clone’s sending domain).
2. Add DNS (SPF, DKIM, MX if inbound). Wait until the domain is **verified**.
3. Pick the region when creating the domain. This template: **EU**.

App sending address: `EMAIL_FROM=noreply@mg.app.example.com` (must be allowed on that domain).

---

## 2. App — HTTP API (invites, transactional)

Dashboard → **API Keys** (account or domain sending key). Not the SMTP password.

```text
EMAIL_PROVIDER=mailgun
EMAIL_FROM=noreply@mg.app.example.com
EMAIL_FROM_NAME=App
MAILGUN_API_KEY=key-...
MAILGUN_DOMAIN=mg.app.example.com
MAILGUN_REGION=eu
```

Local default is `EMAIL_PROVIDER=console` (prints mail, no Mailgun). Production/staging examples: `deploy/env-examples/backend.env.production.example`.

Health: `GET /api/v1/health` checks Mailgun when the provider is `mailgun`.

---

## 3. Keycloak — SMTP (required for execute-actions)

Keycloak does **not** call the Mailgun HTTP API. Configure **Realm settings → Email**.

Dashboard → **Sending → Domain settings** → domain dropdown → **SMTP credentials**. Username is typically `postmaster@mg.app.example.com`. Reset password if needed — Mailgun shows the SMTP password **once**.

### Console clicks

1. Realm `app` → **Realm settings → Email**.
2. **From** / **From display name** / **Reply to**: same brand as `EMAIL_FROM` (e.g. `noreply@mg.app.example.com`).
3. **Host:** `smtp.eu.mailgun.org` (EU) or `smtp.mailgun.org` (US).
4. **Port:** `587`.
5. **Encryption:** Enable **StartTLS**. Do not use SSL on 587 (use 465 only if you switch port to implicit TLS).
6. **Authentication:** On. **Username** = SMTP user. **Password** = SMTP password (**not** `MAILGUN_API_KEY`).
7. **Test connection**. Then **Send test email** to an address you control.

If Test connection fails: region/host mismatch, unverified domain, or API key pasted into the password field.

### execute-actions from the app

After SMTP works, Admin API:

```http
PUT /admin/realms/app/users/{id}/execute-actions-email?client_id=app-web&redirect_uri=https://app.example.com/login
Content-Type: application/json

["UPDATE_PASSWORD"]
```

Local redirect: `http://localhost:5173/login` — must be in `app-web` **Valid redirect URIs**.

If `client_id` and `redirect_uri` are both omitted, Keycloak sends the email with **no link back** to the SPA after the action. Default link lifespan is 12 hours.

Approve-with-`VERIFY_EMAIL` is the same endpoint with `["VERIFY_EMAIL"]`. Fail closed if SMTP or Admin API fails — do not skip silently.

Links in the email use Keycloak’s public hostname. Production: `KC_HOSTNAME=https://auth.app.example.com` and nginx `X-Forwarded-Proto`. If the API calls Keycloak over `http://keycloak:8080` without forwarded proto, action tokens can mint `iss` as `http://…` and the user hits “invalid token issuer” after clicking HTTPS.

---

## 4. What not to do

- Do not put Mailgun SMTP inside FastAPI — the app already has the HTTP provider.
- Do not expect console local email to satisfy Keycloak execute-actions. Local Keycloak still needs SMTP (or you accept 4xx on password-reset / verify-email until it is configured).
- Do not share one Mailgun domain across unrelated products if you need separate bounce/complaint handling — clones usually get their own sending domain.
