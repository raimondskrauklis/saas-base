# P0 — Shared infra (execution)

Phase **P0** of [`MINI_SAAS_GENERAL_PLAN.md`](./MINI_SAAS_GENERAL_PLAN.md). Baseline: [`MINI_SAAS_FINDINGS.md`](./MINI_SAAS_FINDINGS.md). **P0 only.**

**Goal:** Suspended actors hit `/account-suspended`; inbound Keycloak enable/disable cannot clobber `rejected` / pending / `deleted`.

**Push:** local

Do not ask Continue?. After each Deliverable, next heading. After the ship gate, open Next immediately.

## Decisions locked for P0

- Q10: axios `403` + `account_suspended` → `/account-suspended`, mirroring `workspace_suspended`.
- Q17: `enabled=false` only `active`→`suspended`; `enabled=true` only `suspended`→`active`; else no-op.
- `active_program` slug `mini-saas`. SSOT `.revy/review-context.json`; mirror `.agent/review-context.json` identical. Omit `rule_packs` (`manifest.review_context.rule_packs` is null; no `.revy/rules/`). Keep `rule_packs_catalog` as `{}`.
- Do not weaken `get_current_user`. Do not return `GET /me` 200-with-status for suspended.
- Do not add `ADMIN*` to `WEBHOOK_EVENTS_TAKEN` (inbound latent until Q20).

## Out of scope for P0

- Keycloak Admin helper → **P1**
- Directory / detail / KPI APIs → **P2**
- Lifecycle mutations → **P3**
- Admin users UI / dashboard card → **P4**
- Live Keycloak / realm JSON / irbene_gate → **Q20, not this LOOP**

## P0.0 — Program PR review context

**What:** Wire `.revy/review-context.json` + `.agent/review-context.json` (identical) + `.cursor/BUGBOT.md`. One `programs[]` entry `mini-saas`. Scope `backend/**` + `frontend/**`. Omit `rule_packs`. Keep `rule_packs_catalog` as `{}`. Bugbot: three program docs only (README, findings, general plan). Do not ask which packs.
**Files:** `.revy/review-context.json`, `.agent/review-context.json`, `.cursor/BUGBOT.md`
**Deliverable:** `python3 -c "import json; a=json.load(open('.revy/review-context.json')); b=json.load(open('.agent/review-context.json')); assert a==b and a['active_program']=='mini-saas'"`

```json
{
  "active_program": "mini-saas",
  "programs": [
    {
      "id": "mini-saas",
      "scope": ["backend/**", "frontend/**"],
      "paths": [
        { "path": "docs/mini-saas/README.md", "description": "execution" },
        { "path": "docs/mini-saas/MINI_SAAS_FINDINGS.md", "description": "findings" },
        { "path": "docs/mini-saas/MINI_SAAS_GENERAL_PLAN.md", "description": "general plan" }
      ]
    }
  ],
  "rule_packs_catalog": {}
}
```

## P0.1 — Victim interceptor

**What:** In `api.ts` response interceptor, map `403` + `error === 'account_suspended'` to `window.location.assign('/account-suspended')`, same guard as `workspace_suspended` (skip if already on that path). Do not change `get_current_user` or `/me`.
**Files:** `frontend/src/lib/api.ts`, `frontend/src/lib/api.test.ts` (new)
**Deliverable:** `cd frontend && npm test -- --run src/lib/api.test.ts`

## P0.2 — Q17 inbound status machine

**What:** `apply_keycloak_user_disabled`: disable only if `status == active` → `suspended`; enable only if `status == suspended` → `active`. No-op on `rejected`, all pending*, `deleted`. Do not change webhook event subscription.
**Files:** `backend/app/services/keycloak_provisioning.py`, `backend/tests/unit/test_keycloak_provisioning.py`
**Deliverable:** `cd backend && pipenv run pytest tests/unit/test_keycloak_provisioning.py -q`

**Phase gate:**

```bash
cd backend && pipenv run ruff check --fix . && pipenv run ruff check . && pipenv run pytest tests/unit/test_keycloak_provisioning.py -q
cd frontend && npm run lint && npm test -- --run src/lib/api.test.ts
python3 -c "import json; a=json.load(open('.revy/review-context.json')); b=json.load(open('.agent/review-context.json')); assert a==b and a['active_program']=='mini-saas'"
```

## LOOP ship gate

Do not ask Continue?. After this gate, open the Next file immediately.
Pause LOOP only if a subphase above said Pause LOOP (migration).

1. Branch — not main (`feat/mini-saas`)
2. Lint (from backend/: `pipenv run ruff check --fix . && pipenv run ruff check .`; from frontend/: `npm run lint`)
3. Phase gate above — green
4. Bugbot:
REPEAT until Bugbot CLOSE:
  1. Invoke review-bugbot (run_in_background: false)
  2. Diff: uncommitted changes
  3. Custom Instructions: VERB FIND + this phase locked decisions + .cursor/BUGBOT.md
  4. Fix blockers; re-lint if code changed
END REPEAT
5. Commit: feat(mini-saas): P0 victim UX and inbound status machine
6. Do not push.
7. Update README status row.
8. Open Next immediately.

**Next:** [`MINI_SAAS_P1_EXECUTION.md`](./MINI_SAAS_P1_EXECUTION.md)
