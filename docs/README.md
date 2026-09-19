# Platform base — program index

**This repo is deliverable 1** (clean template). Deliverable 2 is copy into `../irbene_gate` (P5–P6). **No Irbene ontology here.**

| Doc | Role |
|-----|------|
| [PLATFORM_BASE_FINDINGS.md](./PLATFORM_BASE_FINDINGS.md) | Baseline — verified against `../revy` git. No execution steps. |
| [PLATFORM_BASE_GENERAL_PLAN.md](./PLATFORM_BASE_GENERAL_PLAN.md) | Phases P0–P6. No file lists. |
| [PLATFORM_BASE_P0_EXECUTION.md](./PLATFORM_BASE_P0_EXECUTION.md) | P0 execution. P1–P6 files not written yet. |

| Phase | File | Push | Status |
|:---|:---|:---|:---|
| P0 — Repo and prefix | [PLATFORM_BASE_P0_EXECUTION.md](./PLATFORM_BASE_P0_EXECUTION.md) | local | done |
| P1 — Strip Revy product | — | first-push | not written |
| P2 — Port user provisioning | — | local | not written |
| P3 — Generic platform identity | — | local | not written |
| P4 — Prove and tag saas-base-v2 | — | batch | not written |
| P5–P6 | run in `../irbene_gate` | — | not written |

**P0 trap:** `docs/` already lives in this working tree. Import `saas-base-v1.1` history **into** this directory. Do **not** `git clone` Revy on top of this folder.

**Source (local):** `/Users/raimonds.krauklis/projects/revy`  
**Source (GitHub):** `https://github.com/raimondskrauklis/revy`  
**Frozen shell:** tag `saas-base-v1.1` (`48c361e`)  
**Auth to port:** `ed773f4` (`feat(auth): Keycloak user provisioning (P0–P4) (#32)`) — **not** in that tag.

**After workflow bootstrap:** `create-execution-plan` for P0.
