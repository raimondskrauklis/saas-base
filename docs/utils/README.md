# docs/utils/

Shared operator runbooks (committed — not gitignored). Clone placeholders: realm `app`, clients `app-api` / `app-web`, host `app.example.com`. Replace per [APP_REPLACE.md](../platform-base/APP_REPLACE.md).

| Runbook | Use |
|---------|-----|
| [DATABASE_CONNECTION_GUIDE.md](./DATABASE_CONNECTION_GUIDE.md) | Managed Postgres URLs, admin vs readonly |
| [KEYCLOAK_SETUP.md](./KEYCLOAK_SETUP.md) | Realm, clients, service-account Admin roles, realm-as-code, smokes |
| [MAILGUN_SETUP.md](./MAILGUN_SETUP.md) | App HTTP API + **Keycloak SMTP** (execute-actions, verify email) |
| [SPACES_STORAGE.md](./SPACES_STORAGE.md) | DigitalOcean Spaces — one bucket per clone (no MinIO) |
| [API_KEYS.md](./API_KEYS.md) | Workspace API keys — **design locked, not implemented** |
| [STRIPE_BILLING_SETUP.md](./STRIPE_BILLING_SETUP.md) | Checkout, Portal, webhooks |
| [CERTBOT_DIGITALOCEAN_DNS_RENEWAL.md](./CERTBOT_DIGITALOCEAN_DNS_RENEWAL.md) | TLS for app + `auth.*` |
| [CURSOR_AGENT_WORKFLOW.md](./CURSOR_AGENT_WORKFLOW.md) | Agent LOOP quick ref |
| [deploy-user-migration.md](./deploy-user-migration.md) | Droplet deploy user |

One-page Keycloak cheat sheet (login smoke only): [KEYCLOAK_DEV_CHECKLIST.md](../starter-pack/KEYCLOAK_DEV_CHECKLIST.md).
