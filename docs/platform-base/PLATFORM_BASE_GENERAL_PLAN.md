# Platform base — general plan

From [PLATFORM_BASE_FINDINGS.md](./PLATFORM_BASE_FINDINGS.md). **No file lists or steps.** Decisions Q1–Q16 are **locked**.

**Homes:** P0–P4 in the **template repo** (this tree). P5–P6 in the **consumer** `../irbene_gate`.

**Cross-cutting (every phase):** unit tests; EN+LV for any user-facing string change; hand-written Alembic with **full** `revision` strings (never `--autogenerate`); generic `<app>` names (no new `revy` brand); do not touch Revy staging DBs. Template `TEST_DATABASE_URL` is a new DB (Q15).

**Push (template repo, GitHub without Revy):** P0 `local` (done). P1 `first-push`. P2–P3 `local`. P4 `batch`. Follow the program README Push column; do not invent a fourth kind; no Revy poll (`integrations.revy` is false). Consumer P5 `first-push`, P6 `batch` on the Irbene remote.

---

## P0 — Repo and prefix

**Goal:** Template repo whose import invariant is history through `saas-base-v1.1` (`48c361e`).

**Scope:** **Done.** Do not re-open. Overlay commit(s) on top of the tag are expected. Out — later review commits; squash; `internal-docs/`.

**Deliverables:** Tag peels to `48c361e`; program docs in `docs/platform-base/`; origin is private `raimondskrauklis/saas-base`.

**Depends on:** none (landed).

---

## P1 — Strip Revy product from the shell

**Goal:** Runtime tree is SaaS only: no GitHub installations, no Revy tokens/LLM/GitHub env, no `vector`, no review-pipeline corpus.

**Scope:** In — delete `2026_07_24_0300_0004_github_installations` and set `2026_07_25_2217_0005_user_locale_timezone.down_revision` to `2026_07_24_0200_0003_invitations`; drop installations API/models/enums/`plan_gates` `installations.create`; drop FE feature **and** live consumers (router, nav, dashboard hooks/checklist/quick actions, settings tests, i18n `installations*`); keep `PlanSummaryWidget`; rename `registerRevy`; strip `github_*` / `revy_*` / moonshot / voyage settings; drop `vector`; delete `tokens.revy.css` and its `@import` (fold leftover `--rv-*` into `tokens.css`); delete `docs/review-pipeline/`, `REVY_PRODUCT_SLICE.md`, `SCAFFOLD_P4_EXECUTION.md`; retarget or drop inbound links to those three in `docs/starter-pack/README.md`; placeholder nginx/realm/env only as needed to boot. Out — Auth #32; Irbene names; deleting Stripe/impersonation/items; retargeting `.cursor/rules` (P3).

**Deliverables:** `cd backend && pipenv run pytest tests/unit/ -q` green without GitHub tests; `cd frontend && npm test` green; P1 product grep (`backend/` `frontend/` `deploy/`) empty; `docs/review-pipeline/` gone. Do **not** require `.cursor/` clean.

**Depends on:** P0.

---

## P2 — Port user provisioning (#32)

**Goal:** Shell has webhook-primary + JIT Keycloak → Postgres provisioning.

**Scope:** In — behaviour of `ed773f4` (provision service, `/api/v1/webhooks/keycloak`, vymalo `0.10.0-rc.1` on the KC image — not already in this tree, bootstrap guard, FE toasts); Alembic `2026_07_26_1900_0010_keycloak_webhook_deliveries` then `2026_07_26_1910_0011_keycloak_webhook_deliveries_received_at_idx` after `2026_07_25_2340_0009_impersonation_sessions`. Out — keeping `0019`/`0020`/`0018` revision ids; GitHub webhook module; running against Revy DBs.

**Deliverables:** Adapted #32 tests green (`test_keycloak_provisioning.py`, `test_keycloak_webhook.py`, `test_keycloak_webhook_verify.py`, `test_keycloak_webhooks.py`, `test_bootstrap_config.py`, plus the #32 edits to impersonation/AuthContext tests); `alembic heads` is the `0011` **full** id; KC event can create a `users` row before first `/me`.

**Depends on:** P1.

---

## P3 — Generic platform identity

**Goal:** A consumer can rename realm/hosts/app slug without leftover Revy product strings, and agents will not put GitHub installations back.

**Scope:** In — AGENTS.md, README, env examples, i18n product name (`app_name`, account-delete copy, fixtures), docker/nginx/image names, extension ids leftover after P1; **`.cursor/rules`** (`00-core.mdc`, `app-color-tokens.mdc`) retargeted to generic SaaS (workspaces/settings/billing; brand in `tokens.css`; no `tokens.revy.css`, no GitHub installations); **Q17 start recipe** (`APP_REPLACE.md` + rewrite `DEV_BOOTSTRAP.md` / `KEYCLOAK_DEV_CHECKLIST.md`). Out — designing Irbene brand; rewriting gitignored starter-pack; re-adding `tokens.app.css`; standing up a public template Keycloak.

**Deliverables:** Documented `<app>` replace list **and** consumer start steps (own app DBs, own KC DB, realm/clients, env, Mode A); grep for `revy.createit.digital` / `revy[bot]` / `KEYCLOAK_REALM=revy` / `keycloak_realm="revy"` / `app_name.*Revy` / `revy-keycloak` / `/tmp/revy` is empty or placeholder-only.

**Depends on:** P2.

---

## P4 — Prove and tag `saas-base-v2`

**Goal:** Frozen reusable release.

**Scope:** In — unit tests (backend + frontend); Q16 testing baseline (L1 seed + `tests/api/` smokes); Mode A login smoke on **new** Postgres+KC; P1 product grep **plus** `.cursor/` (rules already retargeted in P3); tag `saas-base-v2`; short consumer copy recipe (whole tree minus Out-list). Out — droplet deploy of the template; Irbene overlay; **Playwright** (parking lot after v2).

**Deliverables:** Tag on `raimondskrauklis/saas-base` (on the ship-gate commit); P4 verification table in findings is green; SHA recorded in this folder in a **follow-up docs commit** after the tag exists (do not amend).

**Depends on:** P3.

---

## P5 — Copy base into `irbene_gate`

**Goal:** The **consumer repo** has a runnable SaaS tree beside existing docs/learning.

**Scope:** In — copy the **whole** tagged `saas-base-v2` tree. Out — overwriting `docs/vision.md` or `docs/platform-base/`; tracking `palantir/` `polimi/` `exercises/`; replacing the consumer root learning `Pipfile` with the app Pipfile (app Pipfile stays `backend/Pipfile`); replacing consumer `.env.example`; replacing consumer `.gitignore` (merge template ignore rules in instead).

**Deliverables:** App paths exist; Irbene vision/pointer docs still there; upstream tag noted in consumer `docs/platform-base/`.

**Depends on:** P4. **Runs in** `../irbene_gate`.

---

## P6 — Irbene overlay (identity only)

**Goal:** The consumer copy says Irbene Gate, talks to **its** DBs and realm — still no ontology.

**Scope:** In — app name, tokens, Keycloak realm/clients, `VIRAC_*` / local DB URLs, nginx names if any. Out — Scan/Issue/Product tables, pipelines, operator UI beyond stock dashboard/settings; leaking those names back into the tagged template.

**Deliverables:** Local Mode A smoke on Irbene DBs; `../irbene_gate/docs/vision.md` unchanged as north star; findings **consumer** P6 gate green.

**Depends on:** P5. **Runs in** `../irbene_gate`.

---

## Open item

Calibration: the `saas-base-v2` SHA after P4 (write it back into this folder **after** the tag exists, second docs commit).

**Deferred (not this LOOP):** Playwright E2E — findings parking lot; pick up after Mode A on `saas-base-v2`.

**Next:** `execution-peer-review` on this folder, then `phase-execution` from P1. Do not start P5 until `saas-base-v2` exists.
