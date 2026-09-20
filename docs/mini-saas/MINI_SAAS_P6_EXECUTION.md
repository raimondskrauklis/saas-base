# P6 — Closeout and `saas-base-v3` (execution)

Phase **P6** of [`MINI_SAAS_GENERAL_PLAN.md`](./MINI_SAAS_GENERAL_PLAN.md). Baseline: [`MINI_SAAS_FINDINGS.md`](./MINI_SAAS_FINDINGS.md). **P6 only.** Last file — closeout.

**Goal:** Frozen factory tag clones copy.

**Push:** batch

Do not ask Continue?. After each Deliverable, next heading. After the ship gate, Next is none.

## Decisions locked for P6

- Q21: annotated tag **`saas-base-v3`** on `main` after merge. Not a PR branch. Not a retag of `v2`. Do not amend the tag.
- SHA recorded in a **follow-up** docs commit after the tag exists (`git rev-parse 'saas-base-v3^{commit}'`).
- Clear `active_program` → `null` in `.revy/review-context.json` **and** `.agent/review-context.json` (identical) only after the gap table has no fix-now rows. Keep `rule_packs_catalog`.
- Inbound `ADMIN*` stays latent until Q20; do not change live `WEBHOOK_EVENTS_TAKEN` in this repo.
- W5 “no in-app user directory” is superseded by this program — say so in the W5 docs; do not treat it as already done before this subphase.

## Out of scope for P6

- Copy into `../irbene_gate`; realm JSON; live Keycloak clicks (Q20)
- Spaces (Q18); workspace API keys (Q19)
- Retag `v2`

## P6.1 — Gap table

**What:** Re-read findings + general plan + P0–P5 vs shipped code. Table: `| Gap | Severity | Action |` (`fix-now` or `later`). Zero `fix-now` rows before P6.3. Write the table into [`MINI_SAAS_FINDINGS.md`](./MINI_SAAS_FINDINGS.md) (closeout section).
**Files:** `docs/mini-saas/MINI_SAAS_FINDINGS.md`
**Deliverable:** gap table present in findings; after P6.2, Action column has no `fix-now` rows.

## P6.2 — Fix-now code

**What:** If P6.1 has `fix-now` rows, fix them here. If none, skip with table row `no gaps`.
**Files:** only paths listed as fix-now
**Deliverable:** `cd backend && pipenv run pytest tests/unit/test_admin_users.py tests/unit/test_keycloak_admin.py tests/unit/test_keycloak_provisioning.py tests/api/test_admin_users.py -q; cd frontend && npm test -- --run AdminUsersPage UserDetailPage AdminDashboardPage src/lib/api.test.ts`

## P6.3 — Doc sync

**What:** Platform + operator pointers. Then set both review-context files `active_program` to `null` (identical JSON); keep `rule_packs_catalog`. Update `.cursor/BUGBOT.md` idle stub (three program docs, no active LOOP).

| Doc | Change |
|-----|--------|
| `docs/mini-saas/README.md` | Execution table P0–P6 done; next = tag then irbene_gate copy |
| `docs/saas-base/waves/SAAS_BASE_W5_EXECUTION.md` | “No in-app user directory” superseded by `docs/mini-saas/` |
| `docs/saas-base/SAAS_BASE_W5_PLATFORM_GENERAL_PLAN.md` | Same supersede one-liner |
| `docs/saas-base/SAAS_BASE_FINDINGS.md` | Directory lock superseded by mini-saas |
| `docs/platform-base/APP_REPLACE.md` | Confirm step 5 still points at KEYCLOAK_SETUP + three roles |
| `docs/utils/KEYCLOAK_SETUP.md` §9 | Confirm inbound `ADMIN*` latent + Q22 dual-write; do not add events |
| `AGENTS.md` | Point mini-saas / users directory at `docs/mini-saas/` if missing |

**Files:** paths in the table; `.revy/review-context.json`; `.agent/review-context.json`; `.cursor/BUGBOT.md`
**Deliverable:** `python3 -c "import json; a=json.load(open('.revy/review-context.json')); b=json.load(open('.agent/review-context.json')); assert a==b and a['active_program'] is None"`

## P6.4 — SHA slot (no merge, no tag)

**What:** Put a SHA calibration row in findings + README for `saas-base-v3` (unfilled until 8b). Do **not** merge the PR, do **not** create the tag, do **not** `git rev-parse` the tag as a pass. Merge / annotated tag / SHA docs commit happen **only** in ship-gate 8b after WHILE idle.
**Files:** `docs/mini-saas/MINI_SAAS_FINDINGS.md`, `docs/mini-saas/MINI_SAAS_GENERAL_PLAN.md`, `docs/mini-saas/README.md`
**Deliverable:** `rg -n 'saas-base-v3' docs/mini-saas/README.md; ! git rev-parse 'saas-base-v3^{commit}' >/dev/null 2>&1`

**Phase gate:**

```bash
python3 -c "import json; a=json.load(open('.revy/review-context.json')); b=json.load(open('.agent/review-context.json')); assert a==b and a['active_program'] is None"
cd backend && pipenv run ruff check --fix . && pipenv run ruff check . && pipenv run pytest tests/unit/test_admin_users.py tests/unit/test_keycloak_admin.py tests/unit/test_admin_kpis.py tests/api/test_admin_users.py -q
cd frontend && npm run lint && npm test -- --run AdminUsersPage UserDetailPage AdminDashboardPage src/lib/api.test.ts
rg -n 'superseded' docs/saas-base/waves/SAAS_BASE_W5_EXECUTION.md
! git rev-parse 'saas-base-v3^{commit}' >/dev/null 2>&1
```

## LOOP ship gate

Do not ask Continue?. After this gate, Next is none.
Pause LOOP only if a subphase above said Pause LOOP (migration).

1. Branch — not main (`feat/mini-saas`) until merge in step 8b
2. Lint (from backend/: `pipenv run ruff check --fix . && pipenv run ruff check .`; from frontend/: `npm run lint`)
3. Phase gate above — green (tag does not exist yet; 8b creates it)
4. Bugbot:
REPEAT until Bugbot CLOSE:
  1. Invoke review-bugbot (run_in_background: false)
  2. Diff: uncommitted changes
  3. Custom Instructions: VERB FIND + this phase locked decisions + .cursor/BUGBOT.md
  4. Fix blockers; re-lint if code changed
END REPEAT
5. Commit: feat(mini-saas): P6 closeout
6. Fetch Revy first (comments from the P1 PR — include outdated / unresolved, not only Files-changed):
REPEAT until Revy status is NOT pending/in_progress/queued:
  gh pr checks <PR> 2>&1 | grep -iE 'revy|Revy' || true
  IF pending/in_progress/queued: poll again (do not push, do not ask)
END REPEAT
   gh pr view <PR> --comments
   gh api repos/<owner>/<repo>/pulls/<PR>/comments --paginate --jq '.[] | select(.user.login|test("revy";"i"))'
   Fix what still applies to current HEAD. Skip obsolete with a one-line note. Lint + Bugbot CLOSE. Commit Revy fixes.
   Re-fetch comments once. If new actionable arrived: fix → lint + Bugbot CLOSE → commit (still the same upcoming push).
7. One push: Revy fixes + this phase + any unpushed local commits. Never force-push. Never push while Revy is pending.
8. After push, Revy reviews the combined tip (new cycle — required):
WHILE actionable Revy comments OR Revy running after push:
  fetch → fix → lint + gate → Bugbot until CLOSE → poll idle → commit → push → poll
END WHILE
8b. Merge PR to `main` (no force, no retag of `v2`). Pull `main`. Annotated tag `saas-base-v3` on that commit; push the tag. Record SHA (`git rev-parse 'saas-base-v3^{commit}'`) in findings + README in a follow-up docs commit; push. Never amend the tag. Do not copy irbene_gate.
9. Next: none.

**Next:** none
