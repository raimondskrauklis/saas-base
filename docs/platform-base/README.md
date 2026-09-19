# Platform base — program index

**This repo is deliverable 1** (clean template). Deliverable 2 is copy into `../irbene_gate` (P5–P6). **No Irbene ontology here.**

| Doc | Role |
|-----|------|
| [PLATFORM_BASE_FINDINGS.md](./PLATFORM_BASE_FINDINGS.md) | Baseline — verified against `../revy` git. No execution steps. |
| [PLATFORM_BASE_GENERAL_PLAN.md](./PLATFORM_BASE_GENERAL_PLAN.md) | Phases P0–P6. No file lists. |
| [PLATFORM_BASE_P0_EXECUTION.md](./PLATFORM_BASE_P0_EXECUTION.md) | P0 execution (landed). |
| [PLATFORM_BASE_P1_EXECUTION.md](./PLATFORM_BASE_P1_EXECUTION.md) | P1 execution. |
| [PLATFORM_BASE_P2_EXECUTION.md](./PLATFORM_BASE_P2_EXECUTION.md) | P2 execution. |
| [PLATFORM_BASE_P3_EXECUTION.md](./PLATFORM_BASE_P3_EXECUTION.md) | P3 execution. |
| [PLATFORM_BASE_P4_EXECUTION.md](./PLATFORM_BASE_P4_EXECUTION.md) | P4 execution. |
| [PLATFORM_BASE_P5_EXECUTION.md](./PLATFORM_BASE_P5_EXECUTION.md) | P5 execution (runs in `../irbene_gate`). |
| [PLATFORM_BASE_P6_EXECUTION.md](./PLATFORM_BASE_P6_EXECUTION.md) | P6 execution + closeout (runs in `../irbene_gate`). |

| Phase | File | Push | Status |
|:---|:---|:---|:---|
| P0 — Repo and prefix | [PLATFORM_BASE_P0_EXECUTION.md](./PLATFORM_BASE_P0_EXECUTION.md) | local | done |
| P1 — Strip Revy product | [PLATFORM_BASE_P1_EXECUTION.md](./PLATFORM_BASE_P1_EXECUTION.md) | first-push | done |
| P2 — Port user provisioning | [PLATFORM_BASE_P2_EXECUTION.md](./PLATFORM_BASE_P2_EXECUTION.md) | local | done |
| P3 — Generic platform identity | [PLATFORM_BASE_P3_EXECUTION.md](./PLATFORM_BASE_P3_EXECUTION.md) | local | done |
| P4 — Prove and tag saas-base-v2 | [PLATFORM_BASE_P4_EXECUTION.md](./PLATFORM_BASE_P4_EXECUTION.md) | batch | pending |
| P5 — Copy base into irbene_gate | [PLATFORM_BASE_P5_EXECUTION.md](./PLATFORM_BASE_P5_EXECUTION.md) | first-push | pending |
| P6 — Irbene overlay | [PLATFORM_BASE_P6_EXECUTION.md](./PLATFORM_BASE_P6_EXECUTION.md) | batch | pending |

**Next:** `phase-execution` from P4. Do not start P5 until `saas-base-v2` exists.

**Source (local):** `/Users/raimonds.krauklis/projects/revy`  
**Source (GitHub):** `https://github.com/raimondskrauklis/revy`  
**Frozen shell:** tag `saas-base-v1.1` (`48c361e`)  
**Auth to port:** `ed773f4` (`feat(auth): Keycloak user provisioning (P0–P4) (#32)`) — **not** in that tag.
