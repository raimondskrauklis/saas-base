# Mini SaaS — general plan

From [MINI_SAAS_FINDINGS.md](./MINI_SAAS_FINDINGS.md). **No file lists or steps.** Decisions Q1–Q22 are **locked**.

**Home:** all phases in this template repo. Copy of tag **`saas-base-v3`** into `../irbene_gate`, live Keycloak, realm JSON, and runbook dogfood are **after this LOOP** (Q20). Out — Spaces, workspace API keys, Irbene overlay, Playwright, extra platform roles.

**Program slug:** `mini-saas` (`.revy/review-context.json` `active_program` + `.cursor/BUGBOT.md`). Execution writes P0.0 before code. Scope: `backend/**` + `frontend/**`.

**Cross-cutting (every phase):** unit tests (mocked Admin client); EN+LV on any new UI string; `--app-*` tokens; `require_super_admin()` + `require_impersonation_allowed()`; fail closed on Keycloak Admin errors; no new `users` columns or enum values; no Keycloak user create/delete from the app. No Alembic expected.

**Push:** GitHub with Revy (`hosting` / PR check). P0 `local`. P1 `first-push`. P2–P3 `local`. P4–P6 `batch` after Revy idle. Follow ship-changes; never push while Revy is `pending`.

---

## P0 — Shared infra

**Goal:** Suspended actors hit `/account-suspended`; inbound Keycloak enable/disable cannot clobber `rejected` / pending / `deleted`.

**Scope:** In — P0.0 `active_program=mini-saas`; axios `account_suspended` interceptor (mirror `workspace_suspended`); Q17 status machine on `apply_keycloak_user_disabled`; unit tests for both. Out — weakening `get_current_user`; `GET /me` 200-with-status; live Keycloak; adding `ADMIN*` to `WEBHOOK_EVENTS_TAKEN` (inbound is latent until Q20; [KEYCLOAK_SETUP.md](../utils/KEYCLOAK_SETUP.md) §9 already flags this).

**Deliverables:** Suspended session lands on `/account-suspended`. Disable webhook is a no-op unless status is `active`; enable is a no-op unless `suspended`.

**Depends on:** none.

---

## P1 — Outbound Keycloak Admin helper

**Goal:** One fail-closed client-credentials helper: GET-merge-PUT `enabled`, session logout, execute-actions (`client_id=app-web` + SPA `redirect_uri`).

**Scope:** In — lives in `backend/app/services/integrations/` (outbound httpx, not next to `keycloak_provisioning.py`); token, GET user, merge-PUT, `POST …/logout`, `PUT …/execute-actions-email`; raise on HTTP/role errors (no `None`/`False` swallow); tests with mocked httpx. Out — applying roles on a live realm (Q20); create/delete KC users; SMTP in this repo (runbook already exists).

**Deliverables:** Helper used by no product path yet except tests; 403/timeout leaves DB unchanged in helper contract tests. Runbooks already committed stay the operator SSOT.

**Depends on:** P0.

---

## P2 — Directory and detail APIs

**Goal:** Super-admin cursor list + user detail, same contract as workspaces.

**Scope:** In — `GET /api/v1/admin/users` (`CursorParams`, `?status=`, `?search=`, order `created_at DESC, id DESC`, default omit `deleted`); `GET /{id}` with memberships + impersonate eligibility (W7 rules); `users_suspended` on `AdminKpisResponse`; keep `GET /pending` until P4 then drop. Out — FE (including dashboard card — that is P4); mutations; email/password fields.

**Deliverables:** Mode A lists the bootstrap `active` user; detail hides impersonate CTA for SA and non-active; KPI field on the dashboard **API** contract.

**Depends on:** P0.

---

## P3 — Lifecycle mutations

**Goal:** Approve, reject, suspend, reactivate, and send-password-reset go through the helper; dual-write (Q22); audit; last-active-SA and self-suspend guards.

**Scope:** In — SELECT FOR UPDATE; Q22 (mutate row → helper raise → commit; restore KC `enabled` if commit fails after Admin success; logout not undoable; wrapper owns commit); approve `VERIFY_EMAIL` (when unverified) **before** PUT `enabled=true`; reject/suspend `enabled=false` + logout; reactivate `suspended`→`active` + `enabled=true` only; `POST /api/v1/admin/users/{id}/send-password-reset` (`UPDATE_PASSWORD`, fail closed, no status row); audits `platform.user.approved` / `rejected` / `suspended` / `reactivated`. Out — reactivate from `rejected`/`deleted`; promote `super_admin`; live SMTP (tests mock execute-actions; [MAILGUN_SETUP.md](../utils/MAILGUN_SETUP.md) already accepts 4xx until Q20).

**Deliverables:** Mutation tests with mocked helper: Admin failure rolls back; commit-fail restores `enabled`; last active SA cannot be suspended; self-suspend rejected; password-reset 4xx does not silent-skip.

**Depends on:** P1, P2.

---

## P4 — Admin users UI

**Goal:** `/admin/users` is a directory (filter, search, load-more); detail route with impersonate CTA and send-password-reset; dashboard shows `users_suspended`.

**Scope:** In — model on `WorkspacesPage`; approve/reject on `pending_approval` rows; EN+LV; `users_suspended` card + i18n on `AdminDashboardPage` (same grid as `users_pending_approval`); password-reset button calls P3 `POST …/send-password-reset`; drop `GET /pending` once FE uses the new list. Out — in-app password/email edit; merging with `/settings/team`.

**Deliverables:** Queue-only page gone. Mode B pending actions still work. Dashboard card matches the P2 field. Password-reset calls execute-actions (fail closed, no silent skip).

**Depends on:** P2, P3.

---

## P5 — Revy review

**Goal:** PR findings on this program are idle or fixed.

**Scope:** In — Revy loop on the implementation PR; valid findings fixed; local Bugbot. Out — new features; irbene_gate copy.

**Deliverables:** Revy check not `pending`; no open valid findings that contradict Q1–Q22.

**Depends on:** P4.

---

## P6 — Closeout and `saas-base-v3`

**Goal:** Frozen factory tag clones copy.

**Scope:** In — gap pass vs findings; doc/README pointers (`APP_REPLACE`, program index, W5 “no directory” superseded); pointer that inbound `ADMIN*` stays latent until Q20 / KEYCLOAK_SETUP §9; merge to `main`; annotated tag **`saas-base-v3`**. Out — retag `v2`; copy into irbene_gate; realm JSON; Spaces/API keys; changing live `WEBHOOK_EVENTS_TAKEN` in this repo.

**Deliverables:** Tag on `main` (not a PR branch). SHA recorded in a follow-up docs commit (do not amend the tag). Findings P6/v3 row filled after the tag exists.

**Depends on:** P5.

---

## Open item

Calibration: `saas-base-v3` SHA after P6 tag (`git rev-parse 'saas-base-v3^{commit}'`).

**Not this LOOP:** irbene_gate recopy + Keycloak activation + realm JSON + runbook validation (Q20). Spaces (Q18). Workspace API keys (Q19).

**Next:** `execution-peer-review` on this folder, then `phase-execution` from P0.
