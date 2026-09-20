# Mini SaaS — findings

**Baseline for planning. No execution steps.**

**Scope:** What `/admin/users` must become for a generic SaaS template, and what else is worth adding to this mini base. Verified against this repo (post platform-base PR merge) plus KP as *pattern only*.

**DB (readonly, 2026-09-20):** `database_url_readonly_for(settings, "development")` → `saas_base_dev`. `users` columns: `id`, `keycloak_user_id`, `email`, `full_name`, `status`, `platform_role`, `created_at`, `updated_at`, `locale`, `timezone`. Status counts: `active=1`, no other statuses present. No schema change is required for suspend — `user_status.suspended` already exists.

---

## Build principles

- **No corner-cutting.** We own this product’s Postgres, API, and Keycloak. Realm service-account roles, Admin API, session logout, and operator emails are **this program**, not a later clone footnote.
- App `users.status` is the API access gate. Keycloak remains IdP; this page does not become a full Admin console clone. Suspend/reject **must** set `enabled=false` **and** logout sessions so a live token cannot outlive the action.
- Fail closed: Admin API errors abort the operator action. Do not copy KP’s `return None` / `return False` swallow.
- Real rows only. No fake “live” toggles for env-backed registration flags.
- Reuse W5 workspace directory patterns (`CursorParams`, `?status=`, `?search=`, audit writes) — do not invent a second admin list style.
- Platform vs workspace admin stays split: this page is `require_super_admin()` only. Workspace invites stay on `/settings/team`.
- EN + LV via `t()`. `--app-*` tokens only.
- Generic SaaS: workspaces, memberships, billing, settings. No KP institutions, provision-ops, or product roles.

---

## Terminology

| Term | Meaning |
|------|---------|
| **Signup queue** | Mode B list of `pending_approval` — already shipped. |
| **User directory** | Cursor-paginated list of app users (all lifecycle statuses operators need). **New.** |
| **App suspend** | Set `users.status = suspended`. APIs 403 `account_suspended`. Belt: even after IdP disable + session logout, interceptor still maps 403 (Q10). |
| **KC disable** | `enabled=false` on the Keycloak user. Inbound webhook: `apply_keycloak_user_disabled`. Outbound: Admin API GET-merge-PUT. |
| **KC session logout** | `POST /admin/realms/{realm}/users/{id}/logout` (KC 26) — kills refresh + SSO sessions at the IdP. Required on suspend and reject. |
| **KC execute-actions email** | `PUT …/users/{id}/execute-actions-email` — `UPDATE_PASSWORD` from user detail; `VERIFY_EMAIL` on approve when KC `emailVerified` is false. |

Enums already in `backend/app/constants/enums.py`: `UserStatus` includes `suspended`; `PlatformRole` is only `super_admin`.

---

## What exists vs genuinely new

### Verified — already in saas-base

| Capability | Evidence |
|------------|----------|
| Mode B pending list (unordered-by-id, ordered `created_at ASC`, **no cursor**) | `GET /api/v1/admin/users/pending` — `backend/app/api/v1/admin/users.py:26`, `list_pending_users` — `backend/app/services/users.py:229` |
| Approve / reject | `POST …/{user_id}/approve\|reject` — same router; `approve_pending_user` / `reject_pending_user` |
| Approve/reject **do not** `record_audit` | Contrast `admin_workspaces.py:177` (`platform.workspace.suspended`) |
| FE page is queue-only | `AdminUsersPage.tsx` + `PendingUsersTable.tsx`; route `/admin/users` — `frontend/src/features/admin/routes.tsx:27` |
| Dashboard KPI `users_pending_approval` + banner link | `admin_kpis.py:34`, `AdminDashboardPage.tsx:65` — **no** `users_suspended` |
| Workspace directory (the copy target) | `GET /admin/workspaces?status=&search=` cursor — `admin/workspaces.py:44` |
| Workspace suspend / unsuspend + audit | `admin_workspaces.py` |
| Suspended **user** blocked on every authenticated call | `get_current_user` — `auth.py:219` → `ForbiddenError(error_code="account_suspended")` |
| Status gate page exists | `/account-suspended` — `routerInstance.tsx:60`; `ProtectedRoute.tsx:41` if `user.status === 'suspended'` |
| **Victim UX hole:** `/me` never returns `suspended` | `GET /me` depends on `get_current_user`, which 403s first. `AuthContext` sets `user=null` on fetch failure (`AuthContext.tsx:56`). `api.ts` interceptor redirects `workspace_suspended` only — **not** `account_suspended`. Suspended operator-visible UX is therefore incomplete. |
| JIT will not auto-reactivate suspended | `maybe_auto_provision_user` only continues for `pending_profile` / `pending_email_verification` / `pending_approval` — `onboarding.py:80` |
| Inbound KC disable → app suspend; KC enable → `suspended`→`active` | `apply_keycloak_user_disabled` — `keycloak_provisioning.py:201` |
| **No outbound Keycloak Admin client yet** | Grep `KEYCLOAK_ADMIN` / admin API in `backend/app`: none. Credentials already exist: `keycloak_client_id` + `keycloak_client_secret` (`config.py:113`). `httpx` already a backend dep (`jwks.py`, mailgun). |
| **`app-api` service account / Admin roles** | Runbooks already require Service accounts ON + `realm-management` `manage-users` / `query-users` / `view-users` (`KEYCLOAK_DEV_CHECKLIST.md`, `APP_REPLACE.md` step 5, [KEYCLOAK_SETUP.md](../utils/KEYCLOAK_SETUP.md) §6). **Live apply is Q20** (irbene_gate after `saas-base-v3`). Helper code this program; no live realm clicks here. |
| Impersonation (W7) | `POST /admin/impersonation/start`; target must be `active` and not `super_admin` — `impersonation.py:60` |
| Platform audit search | `GET /admin/audit` |
| Settings: read-only registration flags + KC Admin **link** | `admin/settings.py`, `AdminSettingsPage.tsx` |
| Tenant billing UI | `BillingSettingsPage.tsx` (workspace admin, not platform) |
| Invitations | Workspace team settings, not platform users page |

### Verified — W5 explicitly deferred (this program)

W5 locked **no in-app user directory** (`SAAS_BASE_W5_EXECUTION.md` “Decisions locked for W5”). Signup queue was the only `/admin/users` surface. That lock is **superseded** by this findings set.

### KP pattern (adopt / reject)

Source of truth for *shape*, not for copy-paste: KP `admin/users.py` — `GET ?status=pending_approval|active` (active tab includes `suspended`), `GET /{id}`, approve/reject, suspend/reactivate, `_commit_and_sync_keycloak` (`enabled` flag).

| KP piece | This template |
|----------|----------------|
| Status-filtered directory + detail | **Adopt** (workspaces analogue) |
| Suspend / reactivate | **Adopt** (app status **and** KC `enabled`) |
| KC `enabled` sync on approve / reject / suspend / reactivate | **Adopt** — Q22 (row in open txn → helper → commit; restore `enabled` if commit fails). Reuse `app-api` client credentials. |
| KC `manage-users` + `query-users` + `view-users` on `app-api` service account | **Adopt** — KP required set (`KP-Auth-Complete-v2.md`). We apply on owned realms + `KEYCLOAK_DEV_CHECKLIST.md` + `APP_REPLACE.md` step 5. |
| Session logout on suspend / reject | **Adopt** — KP left live tokens until TTL; we will not. KC 26 `POST …/users/{id}/logout`. |
| `execute-actions-email` (`UPDATE_PASSWORD`, `VERIFY_EMAIL`) | **Adopt** — operator password-reset from detail; verify-email on approve when KC says unverified. Fail closed if KC SMTP / Admin call fails. |
| KP `keycloak_admin.py` create / delete user | **Reject** — JIT + workspace invitations already create identity. A second create path forks provisioning. |
| KP swallow-errors Admin client (`get_token` → `None`, `update` → `False`) | **Reject** — raise; rollback / restore like KP’s *intent*, not their swallow. |
| Institutions, platform staff roles, provision-ops | **Reject** |
| Email / password *field* edits from console | **Reject** — change password via Keycloak execute-actions email, not a local password form. |

### Genuinely new

- Cursor user directory + filters + search.
- `GET` user detail (profile fields + memberships).
- `POST` suspend / reactivate.
- Audit actions for user lifecycle (including existing approve/reject gap).
- Dashboard `users_suspended` KPI (Q11).
- Shared-infra: map `account_suspended` so the victim hits `/account-suspended` (Phase-0).
- Outbound Keycloak Admin helper (shared): client-credentials token; GET user; GET-merge-PUT `enabled`; logout sessions; execute-actions-email. All lifecycle mutations use it.
- Keycloak realm work we own: Service accounts on `app-api`; assign `realm-management` `manage-users`, `query-users`, `view-users`. Committed runbook [KEYCLOAK_SETUP.md](../utils/KEYCLOAK_SETUP.md) + checklist + `APP_REPLACE.md` step 5. Helper code this program. **Live apply + smoke GET** `/admin/realms/{realm}/users/{id}`: **irbene_gate** after `saas-base-v3` (Q20).
- Inbound disable status machine: `enabled=false` only `active`→`suspended`; `enabled=true` only `suspended`→`active`. No-op on `rejected` / pending / `deleted` (reject echo must not clobber).

No new `users` columns. No new enum values.

---

## Catalog — users page (this program)

| Item | Rationale | Method |
|------|-----------|--------|
| **A. Cursor list** `GET /api/v1/admin/users` | Queue-only page is unusable in Mode A (open signup) and hides everyone already `active`. | Same contract as workspaces: `CursorParams`, `?status=` (`UserStatus` or omit=all except `deleted`), `?search=` email/name ILIKE. Order `(created_at DESC, id DESC)` like workspaces, **not** the pending-queue ASC. Keep `GET /pending` until P4 FE uses the new list, then **drop**. |
| **B. Columns** | Operators need to tell staff from tenants. | `id`, `email`, `full_name`, `status`, `platform_role`, `created_at`. Not `keycloak_user_id` in the table (detail only). |
| **C. Mode B actions stay** | Approval is still the gated-signup path. | Existing approve/reject; show only when `status=pending_approval`. Audit `platform.user.approved` / `platform.user.rejected`. Same Q22 dual-write as suspend. Approve: `enabled=true`; if KC `emailVerified` is false, `execute-actions-email` `VERIFY_EMAIL`. Reject: `enabled=false` + session logout. |
| **D. Suspend / reactivate** | Abuse / stop-access at user grain. Same IdP+app pair as KP, plus session kill KP skipped. | Suspend: `users.status=suspended` + KC `enabled=false` + **logout sessions**. Reactivate: `active` + `enabled=true`. Dual-write (Q22): mutate row in the open transaction → helper (raise) → commit; restore KC `enabled` if commit fails after Admin success. Logout is not undoable. Fail closed (no committed app-only status). Audit `platform.user.suspended` / `platform.user.reactivated`. |
| **E. Guards** | `get_current_user` 403s suspended actors, including super_admin (`auth.py:219`). Suspending yourself or the last SA bricks the console. | Forbid self-suspend. Forbid suspend of the last remaining **active** `platform_role=super_admin`. Other super_admins may be suspended if ≥2 **active** remain. Reactivate allowed for any `suspended` user (including SA) by a remaining SA. |
| **F. Detail** `/admin/users/:userId` | List actions are not enough once memberships matter. | `GET /api/v1/admin/users/{id}`: user fields + memberships + impersonate CTA (W7 rules). **Send password reset** → `POST /api/v1/admin/users/{id}/send-password-reset` → `execute-actions-email` `UPDATE_PASSWORD` (fail closed; no status dual-write). No local password or email edit fields. |
| **G. Victim UX (Phase-0)** | Without this, a 403 mid-session is a blank SPA. | Axios interceptor: `403` + `account_suspended` → `/account-suspended`, mirroring `workspace_suspended` (`api.ts:92`). Do **not** weaken `get_current_user`. |
| **H. KPI** | Matching workspace suspended card. | `users_suspended` on `AdminKpisResponse` (plan P2) and `AdminDashboardPage` card + EN/LV (plan P4). |
| **I. Keycloak we own** | Admin API is dead without service-account roles. We do not leave this to “clone later.” | **This program:** committed clicks in [KEYCLOAK_SETUP.md](../utils/KEYCLOAK_SETUP.md) + helper code + SMTP runbook. **First live apply + realm JSON:** `../irbene_gate` after the next base tag (Q20). Roles: `manage-users`, `query-users`, `view-users`. Smoke there: client-credentials GET `/admin/realms/{realm}/users/{id}`. |

**FE:** Replace queue-only `AdminUsersPage` with directory (status filter + search + load-more) modeled on `WorkspacesPage.tsx`. Keep approve/reject on pending rows. New detail route next to `workspaces/:workspaceId`. i18n EN+LV.

---

## Catalog — what else is worth for a mini SaaS base

Already shipped (do **not** rebuild): admin shell, workspace directory + suspend, audit search, impersonation APIs, Mode A/B, invitations, tenant billing, account export/delete, settings flags + Stripe **link**. Keycloak Admin **link** stays; it is not a substitute for I.

Impersonate-from-detail, approve/reject audit, and `users_suspended` KPI are **this program** (catalog F/C/H), not a follow-on.

### Defer (conscious — not lifecycle)

| Item | Why defer |
|------|-----------|
| Live registration-flag toggles in admin settings | Flags are process env. A UI switch that does not change the running process would mislead. Runtime config store would be a different program. |
| Promote / demote `platform_role` | Bootstrap email exists. A misclick creates a second god-mode. Not required to manage tenant users. |
| Create Keycloak users from this page | JIT + workspace invitations already provision. A second create path forks identity. |
| In-app notification feed | Deferred in `SAAS_BASE_FINDINGS.md`; not user-directory. |
| Workspace API keys | Deferred follow-on. Shape locked: [API_KEYS.md](../utils/API_KEYS.md). |
| File handling / Spaces | Deferred follow-on. Spaces only (no MinIO): [SPACES_STORAGE.md](../utils/SPACES_STORAGE.md). First consumer: W6 export off local disk. |
| Platform billing console (refunds, invoices) | Stripe Dashboard link is the W5 decision; keep it. |
| Feature-flag service | Env + Keycloak + Stripe cover template needs. |
| Extra platform staff roles (`platform_ops`) | One `super_admin` is the template. |
| Playwright E2E | Previously deferred for this template. |
| Items demo FE | Pattern reference only. |
| Cross-tenant email blast / MAU charts | Product, not base. |

### Reject

| Item | Why |
|------|-----|
| KP institutions, campus roles, provision-ops | Wrong domain. |
| Editing `email` / `keycloak_user_id` in-app | Identity lives in Keycloak; JIT already syncs email in `_apply_live_identity`. |
| Merging this page with workspace team | Different RBAC layer (`super_admin` vs `AppRole.admin`). |
| Soft-delete from this page | Account delete is W6 self-serve / lifecycle, not a console bulk tool. |

---

## Data scope & exclusions

**In:** rows in `public.users` with any `UserStatus` except default-hide `deleted` (include via explicit `?status=deleted` if needed; default list omits deleted).

**Out:** Keycloak users with no app row (never JIT-provisioned). Workspace memberships listed on detail only — not a second tenant-admin UI.

**Compute vs filter:** status and search are query filters (like workspaces), not client-side on a full dump. Today’s pending list loads the entire queue — fine at N=1 in dev; wrong as the directory grows.

---

## Edge cases

1. **Self-suspend** — actor `id == target` → validation error. Last **active** SA suspend → validation error (count `platform_role=super_admin` and `status=active` only).
2. **Inbound webhook echo** — outbound PUT `enabled` fires Keycloak `ADMIN*` into `apply_keycloak_user_disabled`. **Status machine (locked):** `enabled=false` only if `active` → `suspended`; `enabled=true` only if `suspended` → `active`. No-op on `rejected` / pending / `deleted`. Reject then KC disable must not rewrite `rejected` as `suspended`. KC Admin **Enable** remains recovery **from suspended only**.
3. **Admin API 403 without roles** — client-credentials token succeeds; GET/PUT users 403s. Mutation fails closed. Fix is item **I** on the owned realm, not an app workaround.
4. **Mode A** — pending tab empty is normal; directory still required.
5. **Impersonate suspended** — already forbidden (`impersonation.py:71`). Hide CTA.
6. **Approve does not create a second workspace if somehow already member** — `activate_user_with_workspace` always inserts a workspace (`onboarding.py:51`). Out of scope to change; do not call approve on non-pending.
7. **Rejected user** — no reactivate-to-pending in this program; they re-register via Keycloak only if a later product wants that.
8. **Concurrent suspend** — `SELECT … FOR UPDATE` like approve/reject.

---

## Advice / options

**Recommended path (locked):** This program ships **code + committed runbooks** in saas-base. Item I clicks are documented in [KEYCLOAK_SETUP.md](../utils/KEYCLOAK_SETUP.md); SMTP in [MAILGUN_SETUP.md](../utils/MAILGUN_SETUP.md). Shared Admin helper (enabled, logout, execute-actions, fail closed, GET-merge-PUT) → victim UX → user directory / detail / suspend / approve / reject / KPI / audit / impersonate.

**First real Keycloak activation** is not this repo’s JSON file. After this program tags **`saas-base-v3`**, **`../irbene_gate`** is the first consumer: copy that tag (not a PR branch), bring up Irbene’s Keycloak, follow the runbooks, export realm JSON as the realm becomes correct, and treat that as runbook validation. Irbene ontology / platform-base P6 overlay stays **after** that factory works.

**Not a v1/v2 split** of the users page. Realm JSON is a **consumer artefact**, not a mini-saas deliverable.

**Still reject:** create/delete Keycloak users from this page (forks JIT); KP institutions; swallowing Admin errors.

**Rejected as “good enough”:** App 403 without KC disable; KC disable without session logout; documenting service-account roles without applying them on the Keycloak we run.

---

## External research / patterns

| Pattern | Verdict |
|---------|---------|
| KP `_commit_and_sync_keycloak` (KC `enabled`, then DB commit, restore KC if commit fails) | **Adopt restore, not IdP-first.** Mutate the app row in the open transaction → helper (raise) → commit. If commit fails after Admin `enabled` succeeded, restore KC `enabled`. Logout is not restored. |
| KP `keycloak_admin.update_keycloak_user` PUT body `{enabled: bool}` only | **Adopt with GET-merge-PUT.** Keycloak 26 `PUT /admin/realms/{realm}/users/{id}` is a full user representation. |
| KP token/update returning `None`/`False` | **Reject.** Raise. |
| KP create/delete Keycloak user from the app | **Reject.** JIT + invitations. |
| KP `execute-actions-email` (VERIFY_EMAIL, UPDATE_PASSWORD) | **Adopt.** Fail closed (KP logs a warning and continues — we will not). |
| KP `manage-users` + `query-users` + `view-users` on API client service account | **Adopt.** Apply on owned Keycloak. |
| Live session kill | **Adopt** (`POST …/users/{id}/logout`). KP did not; live JWT until TTL is a hole we close. |

---

## Decisions registry

| Q# | Question | Status | Resolution |
|----|----------|--------|------------|
| Q1 | Outbound Keycloak `enabled` on suspend / reject / reactivate / approve? | **locked** | **Adopt.** Shared Admin helper; existing `app-api` secret; fail closed. |
| Q22 | Dual-write order (app status + KC `enabled`)? | **locked** | Open transaction: mutate row → helper (raise on HTTP/role errors) → `commit`. If commit fails after Admin `enabled` succeeded, restore KC `enabled`. Session logout is **not** undoable. Password-reset / `VERIFY_EMAIL` are Admin-only (no status row). No committed app-only status. |
| Q14 | Logout all Keycloak sessions on suspend / reject? | **locked** | **Adopt.** `POST …/users/{id}/logout`. Required, not optional. |
| Q15 | `execute-actions-email` (password reset + verify email)? | **locked** | **Adopt.** Detail: `POST /api/v1/admin/users/{id}/send-password-reset` → `UPDATE_PASSWORD`. Approve: `VERIFY_EMAIL` when KC `emailVerified` is false, **before** PUT `enabled=true`. Fail closed. `client_id=app-web` + `redirect_uri = (app_public_url or "http://localhost:5173").rstrip("/") + "/login"`. Realm SMTP: [MAILGUN_SETUP.md](../utils/MAILGUN_SETUP.md). Tests mock the helper; live SMTP is Q20. |
| Q16 | Who applies `app-api` service account + Admin roles? | **locked** | Runbooks + helper **this program**. First live realm clicks + export: **irbene_gate** after the next base tag (Q20). Roles: `manage-users`, `query-users`, `view-users`. |
| Q17 | Inbound KC disable/enable vs app status? | **locked** | `false`: `active`→`suspended` only. `true`: `suspended`→`active` only. Else no-op. |
| Q18 | Object storage? | **locked** | DigitalOcean Spaces per clone. No MinIO. [SPACES_STORAGE.md](../utils/SPACES_STORAGE.md). Follow-on program. |
| Q19 | Workspace API keys? | **locked** | Follow-on. Contract: [API_KEYS.md](../utils/API_KEYS.md) (`app_sk_live_` HMAC-SHA256, workspace-scoped). |
| Q20 | Realm JSON / first clone? | **locked** | No realm JSON in this program. First consumer is `../irbene_gate` (already has P5 copy of `saas-base-v2`, commit `909f83b`). After mini-saas tags the next base: copy that tag into irbene_gate → activate Keycloak → export JSON as you go → validate KEYCLOAK/MAILGUN/checklist runbooks. Overlay/ontology after factory. |
| Q21 | Next freeze name after this program? | **locked** | Annotated tag **`saas-base-v3`** on `main` after mini-saas ships. Not a PR branch. Not a retag of `v2`. irbene_gate recopies **v3**, not `feat/platform-base`. History through `v1.1` stays (platform-base Q7). |
| Q2 | Copy KP institutions / extra platform roles? | **locked** | No. |
| Q3 | Who can call the APIs? | **locked** | `require_super_admin()` + `require_impersonation_allowed()` (same as current admin users router). |
| Q4 | List shape? | **locked** | Cursor + `status` + `search`, copy workspaces. Keep `/pending` until P4 FE uses the new list, then drop. |
| Q5 | Self-suspend / last super_admin? | **locked** | Forbid both. Count **active** SAs only. Other SA suspend allowed if ≥2 active SA remain. |
| Q6 | Email edit from console? | **locked** | No. |
| Q7 | Detail + memberships + impersonate CTA? | **locked** | Yes. Impersonate uses existing W7 rules. |
| Q8 | Audit approve/reject? | **locked** | Yes; they are the same operator surface. |
| Q9 | Registration flags writable in UI? | **locked** | No — read-only. |
| Q10 | Victim `/account-suspended` wiring? | **locked** | Required Phase-0 (interceptor). |
| Q11 | `users_suspended` KPI? | **locked** | Yes. Schema on `AdminKpisResponse` (plan P2); dashboard card + EN/LV on `AdminDashboardPage` (plan P4). |
| Q12 | Default list statuses? | **locked** | Omit `deleted` unless filtered. Include `suspended`, `rejected`, pending* , `active`. |
| Q13 | Reactivate target status? | **locked** | `suspended` → `active` only. Not from `rejected` / `deleted`. |

---

## Parking lot

- Create Keycloak users from the platform console (forks JIT).
- `GET /me` 200-with-status for suspended (instead of interceptor) — every other endpoint still 403s; interceptor is the shared fix.
- Promote-to-`super_admin` UI.
- Irbene overlay — separate program; do not mix.

**Phase-0 (shared infra, this product + clones):** (1) `account_suspended` client redirect (plan P0). (2) Admin helper in `backend/app/services/integrations/` + runbooks in this repo (plan P1). (3) First live service-account roles + Mailgun SMTP + realm JSON: **irbene_gate** (Q20). Inbound `ADMIN*` enable/disable is latent until `WEBHOOK_EVENTS_TAKEN` includes those events ([KEYCLOAK_SETUP.md](../utils/KEYCLOAK_SETUP.md) §9). Without (2) in code, every clone Admin call is guesswork; without (3) on the first consumer, runbooks are unproven.

---

## Devil's advocate

- **Both layers plus session kill.** `enabled=false` stops new tokens; logout drops SSO/refresh; Q10 still catches a request that arrives with a leftover access token.
- **Realm not applied.** Code + runbooks without a first consumer stay theoretical. **irbene_gate** is that consumer (Q20) — not a JSON file invented in this repo.
- **Directory without search** becomes useless after tens of workspaces.
- **Approving still creates a personal workspace.** Tenants and staff share one table; do not add institution columns.

---

## Experiment / verification

Pass/fail (for a later plan — not work now):

- Mode A: `/admin/users` lists the bootstrap `active` user (dev DB currently 1).
- Mode B: pending row still approve/reject; audit row appears.
- Suspend target → KC `enabled=false`, **no active KC sessions**, `/me` 403 `account_suspended` → SPA `/account-suspended`.
- Reactivate → KC `enabled=true` and `/me` 200 `status=active`.
- Reject → KC `enabled=false` + sessions logged out.
- Password-reset from detail → KC execute-actions accepted (or 4xx if SMTP missing — no silent skip).
- Client-credentials GET user succeeds on **irbene_gate** after live item I (Q20).
- Admin API down or missing roles → mutation fails; DB status unchanged.
- Impersonate CTA absent for SA and non-active.
- irbene_gate: runbooks walked; realm JSON exported (`--users skip`, secrets stripped).

---

## References

- `backend/app/api/v1/admin/users.py` — current queue
- `backend/app/services/users.py` — `list_pending_users`, approve/reject
- `backend/app/services/admin_kpis.py`, `backend/app/schemas/admin.py`
- `backend/app/core/auth.py` — `account_suspended`
- `backend/app/services/keycloak_provisioning.py` — `apply_keycloak_user_disabled`
- `backend/app/services/onboarding.py` — JIT skip non-pending
- `backend/app/services/impersonation.py` — target rules
- `backend/app/api/v1/admin/workspaces.py` — list contract to copy
- `frontend/src/features/admin/pages/AdminUsersPage.tsx`, `WorkspacesPage.tsx`
- `frontend/src/lib/api.ts`, `contexts/AuthContext.tsx`, `components/auth/ProtectedRoute.tsx`
- `docs/starter-pack/REGISTRATION_FLAGS.md`
- `docs/saas-base/waves/SAAS_BASE_W5_EXECUTION.md` (deferred directory)
- `docs/utils/DATABASE_CONNECTION_GUIDE.md`
- KP: `keycloak_admin.py`, `AdminUserService._commit_and_sync_keycloak`; roles in `docs/KP-Auth-Complete-v2.md` (~1913)
- `docs/utils/KEYCLOAK_SETUP.md`, `docs/starter-pack/KEYCLOAK_DEV_CHECKLIST.md`, `docs/platform-base/APP_REPLACE.md` — item I
- `docs/utils/MAILGUN_SETUP.md` — Keycloak SMTP + app HTTP API
- `docs/utils/SPACES_STORAGE.md`, `docs/utils/API_KEYS.md` — follow-on contracts
- Keycloak 26 Admin: `PUT /admin/realms/{realm}/users/{id}`, `POST …/users/{id}/logout`, `PUT …/users/{id}/execute-actions-email`
