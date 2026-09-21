# Workspace API keys (design lock)

**Status:** not implemented in saas-base, Revy, or KP. This file is the locked contract for a follow-on program — not a substitute for code.

Nav slot already reserved (no link until the wave ships): [SETTINGS_IA.md](../saas-base/SETTINGS_IA.md).

---

## Research (2026)

| Source | Takeaway | Adopt |
|--------|----------|-------|
| [OWASP Multi-Tenant](https://cheatsheetseries.owasp.org/cheatsheets/Multi_Tenant_Security_Cheat_Sheet.html) | High-entropy CSPRNG key; store hash; return plaintext **once**; tenant id from the key, never from the client | **Yes** |
| [OWASP REST](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html) | HTTPS only; key in **header**, never query string; 429; revoke on abuse | **Yes** |
| [Stripe keys](https://docs.stripe.com/keys) / [best practices](https://docs.stripe.com/keys-best-practices) | Prefix + environment (`sk_test_` / `sk_live_`); live secret shown once; restricted keys over god-mode | **Yes** (our own prefix — do not reuse `sk_` or GitHub will treat leaks as Stripe) |
| [apikeys.guide](https://apikeys.guide/docs/introduction/getting-started) | SHA-256 of high-entropy key is enough (not bcrypt); unique prefix column for lookup; identical errors for unknown/revoked | **Yes** |
| [Customer-facing keys](https://averagedevs.com/blog/design-customer-facing-api-keys-saas) | Prefix lookup + constant-time compare; HMAC pepper in env; dual-key rotation window | **HMAC-SHA256 + pepper**; rotation grace in v1.1 not v1 |
| [GitHub secret scanning partners](https://docs.github.com/en/code-security/tutorials/secret-scanning-partner-program) | Unique prefix so scanners can find leaks; partner program later | Prefix now; partner endpoint **defer** |

KP/Revy only have **vendor** keys in env (Mailgun, Anthropic). That is not this feature.

---

## Locked decisions

| Topic | Lock |
|-------|------|
| Owner | **Workspace** key. Created/revoked by workspace `admin`. Not a personal user token in v1 (CLI-as-user can wait). |
| Auth | Separate from Keycloak JWT. Header `Authorization: Bearer <key>` only. After lookup, same workspace RBAC as a member with the key’s scope. |
| Format | `{clone}_sk_test_` / `{clone}_sk_live_` + `secrets.token_urlsafe(32)`. Template placeholder: `app_sk_test_` / `app_sk_live_`. APP_REPLACE changes `app_` to the product slug (`irbene_sk_live_`). **Do not** use Stripe’s `sk_live_` prefix. |
| Storage | HMAC-SHA256(key, `API_KEY_PEPPER`). Never store plaintext. Columns: `id`, `workspace_id`, `name`, `key_prefix` (unique, first ~16 chars), `key_hash`, `scope`, `created_by`, `created_at`, `last_used_at`, `revoked_at`. |
| Pepper | `API_KEY_PEPPER` in server env. Feature refuses to mint/verify if unset. |
| Show once | Create response includes the full key. List/detail show prefix + last 4 only. Lost key → revoke + create. |
| Lookup | Parse prefix → indexed row → `hmac.compare_digest` on hash. Do not scan the table by hash. |
| Scopes | `read` (GET only) and `full` (same as workspace admin mutations the product allows). No custom permission matrix in v1. |
| Lifecycle | Create, list, revoke, `last_used_at`. No recover. Multiple active keys per workspace (so rotation is “create new, swap, revoke old”). |
| Errors | Same 401 body for unknown, revoked, malformed. Do not log the secret (prefix only). |
| Rate limit | Per-key 429 in the same program as the middleware (Redis already in the stack). |
| Audit | `record_audit` on create/revoke. |
| Leak response | Distinct prefix is enough for v1. GitHub partner webhook later. |

Reject: keys in query strings; bcrypt (slow, pointless on 256-bit random); storing keys in Keycloak; platform-level keys that skip workspace isolation; returning the secret on GET.

---

## Settings IA

When the wave ships: Personal group stays without API keys; **Workspace** group gains **API keys** (`/settings/api-keys`) — workspace `admin` only. Matches “keys belong to the tenant.”
