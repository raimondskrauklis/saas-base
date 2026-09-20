# Mini SaaS — program index

Close the platform-console gap that W5 deferred: **in-app user directory** (list, inspect, suspend/reactivate), plus a catalog of what else is worth adding to this template versus leaving to Keycloak / Stripe / clones.

**Not** Irbene overlay. **Not** KP institutions/roles. Identity remains Keycloak.

| Doc | Role |
|-----|------|
| [MINI_SAAS_FINDINGS.md](./MINI_SAAS_FINDINGS.md) | Baseline — users page + mini-SaaS extras. No execution steps. |
| [MINI_SAAS_GENERAL_PLAN.md](./MINI_SAAS_GENERAL_PLAN.md) | Phases P0–P6. No file lists. |
| [MINI_SAAS_P0_EXECUTION.md](./MINI_SAAS_P0_EXECUTION.md) | P0 victim UX + Q17 inbound machine |
| [MINI_SAAS_P1_EXECUTION.md](./MINI_SAAS_P1_EXECUTION.md) | P1 Keycloak Admin helper |
| [MINI_SAAS_P2_EXECUTION.md](./MINI_SAAS_P2_EXECUTION.md) | P2 directory + detail APIs |
| [MINI_SAAS_P3_EXECUTION.md](./MINI_SAAS_P3_EXECUTION.md) | P3 lifecycle mutations |
| [MINI_SAAS_P4_EXECUTION.md](./MINI_SAAS_P4_EXECUTION.md) | P4 admin users UI |
| [MINI_SAAS_P5_EXECUTION.md](./MINI_SAAS_P5_EXECUTION.md) | P5 Revy review |
| [MINI_SAAS_P6_EXECUTION.md](./MINI_SAAS_P6_EXECUTION.md) | P6 closeout + `saas-base-v3` |
| Operator runbooks | [KEYCLOAK_SETUP.md](../utils/KEYCLOAK_SETUP.md), [MAILGUN_SETUP.md](../utils/MAILGUN_SETUP.md), [SPACES_STORAGE.md](../utils/SPACES_STORAGE.md), [API_KEYS.md](../utils/API_KEYS.md) |

| Phase | File | Push | Status |
|:---|:---|:---|:---|
| P0 — Shared infra | [MINI_SAAS_P0_EXECUTION.md](./MINI_SAAS_P0_EXECUTION.md) | local | done |
| P1 — Keycloak Admin helper | [MINI_SAAS_P1_EXECUTION.md](./MINI_SAAS_P1_EXECUTION.md) | first-push | pending |
| P2 — Directory APIs | [MINI_SAAS_P2_EXECUTION.md](./MINI_SAAS_P2_EXECUTION.md) | local | pending |
| P3 — Lifecycle mutations | [MINI_SAAS_P3_EXECUTION.md](./MINI_SAAS_P3_EXECUTION.md) | local | pending |
| P4 — Admin users UI | [MINI_SAAS_P4_EXECUTION.md](./MINI_SAAS_P4_EXECUTION.md) | batch | pending |
| P5 — Revy review | [MINI_SAAS_P5_EXECUTION.md](./MINI_SAAS_P5_EXECUTION.md) | batch | pending |
| P6 — Closeout + `saas-base-v3` | [MINI_SAAS_P6_EXECUTION.md](./MINI_SAAS_P6_EXECUTION.md) | batch | pending |

**Next:** `execution-peer-review` on this folder, then `phase-execution` from P0. After P6: tag **`saas-base-v3`**, copy into `../irbene_gate`.

**Precedent:** KP platform-console users + Keycloak Admin (`enabled`, execute-actions). Session logout (KP did not). Do not copy institutions or KP’s silent Admin client.

**W5 lock this program reverses:** “No in-app user directory — identity ops via Keycloak Admin link” (`docs/saas-base/waves/SAAS_BASE_W5_EXECUTION.md`).
