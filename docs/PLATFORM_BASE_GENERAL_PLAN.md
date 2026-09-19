# Platform base — general plan

From [PLATFORM_BASE_FINDINGS.md](./PLATFORM_BASE_FINDINGS.md). **No file lists or steps.** Decisions Q1–Q10 are **locked**.

**Cross-cutting (every phase):** unit tests; EN+LV for any user-facing string change; hand-written Alembic; generic `<app>` names (no new `revy` brand); do not touch Revy staging DBs.

**Where to run:** P0–P4 **in this repo**. P5–P6 in `../irbene_gate`. Bootstrap `../agent-workflow` before P0 execution.

---

## P0 — Repo and prefix

**Goal:** Empty local+GitHub `saas-base` whose git history **ends** at `saas-base-v1.1`.

**Scope:** In — private `raimondskrauklis/saas-base`; clone path above; history from `0db2f60` through `48c361e` only. Out — any commit after `saas-base-v1.1`; squash; `internal-docs/`.

**Deliverables:** Other agent can `git log -1 --decorate` and see `saas-base-v1.1` as tip (or equivalent). README says this is the generic shell, not Revy.

**Depends on:** GitHub repo exists (human). `docs/` in this tree preserved. Workflow pack bootstrapped.

---

## P1 — Strip Revy product from the shell

**Goal:** Tree is SaaS only: no GitHub installations, no Revy tokens/LLM/GitHub env, no `vector` extension.

**Scope:** In — drop `0004` and retarget `0005` → `0003`; drop installations API/FE/extensions; keep `PlanSummaryWidget`; rename `registerRevy`; strip `github_*` / `revy_*` / moonshot / voyage settings; placeholder nginx/realm/env. Out — Auth #32; Irbene names; deleting Stripe/impersonation/items.

**Deliverables:** `pytest tests/unit/` green without GitHub tests; grep gate for `github_installation` / `tokens.revy` is empty.

**Depends on:** P0.

---

## P2 — Port user provisioning (#32)

**Goal:** Shell has webhook-primary + JIT Keycloak → Postgres provisioning.

**Scope:** In — behaviour of `ed773f4` (provision service, `/api/v1/webhooks/keycloak`, vymalo on KC image, bootstrap guard, FE toasts); new Alembic `0010`+`0011` after `0009`. Out — keeping revision ids `0019`/`0020`; GitHub webhook module; running against Revy DBs.

**Deliverables:** Same #32 tests adapted and green; `alembic heads` is `0011`; KC event can create a `users` row before first `/me`.

**Depends on:** P1.

---

## P3 — Generic platform identity

**Goal:** A consumer can rename realm/hosts/app slug without leftover Revy product strings.

**Scope:** In — AGENTS.md, README, env examples, i18n product name, docker/nginx placeholders, extension ids. Out — designing Irbene brand; rewriting starter-pack gitignored docs.

**Deliverables:** Documented `<app>` replace list; grep for `revy.createit.digital` / `revy[bot]` / `KEYCLOAK_REALM=revy` is empty or placeholder-only.

**Depends on:** P2.

---

## P4 — Prove and tag `saas-base-v2`

**Goal:** Frozen reusable release.

**Scope:** In — unit tests; Mode A login smoke on **new** Postgres+KC; tag `saas-base-v2`; short consumer copy recipe. Out — droplet deploy of the template; Irbene overlay.

**Deliverables:** Tag on `raimondskrauklis/saas-base`; P4 verification table in findings is green; SHA recorded in this folder.

**Depends on:** P3.

---

## P5 — Copy base into `irbene_gate`

**Goal:** This repo has a runnable SaaS tree beside existing docs/learning.

**Scope:** In — copy `saas-base-v2` `backend/`, `frontend/`, `deploy/`, agent/cursor rails, app env examples. Out — overwriting `docs/vision.md` or `docs/platform-base/`; tracking `palantir/` `polimi/` `exercises/`; root learning `Pipfile` as the app Pipfile.

**Deliverables:** App paths exist; program docs still here; upstream tag noted.

**Depends on:** P4.

---

## P6 — Irbene overlay (identity only)

**Goal:** The copy says Irbene Gate, talks to **its** DBs and realm — still no ontology.

**Scope:** In — app name, tokens, Keycloak realm/clients, `VIRAC_*` / local DB URLs, nginx names if any. Out — Scan/Issue/Product tables, pipelines, operator UI beyond stock dashboard/settings.

**Deliverables:** Local Mode A smoke on Irbene DBs; vision.md unchanged as north star; findings P6 gate green.

**Depends on:** P5.

---

## Open item

None on direction. Calibration only: the `saas-base-v2` SHA after P4 (write it back into this folder).

**Next:** bootstrap agent workflow, then `create-execution-plan` for **P0**. Do not start P5 until `saas-base-v2` exists.
