# P6 — Irbene overlay and closeout (execution)

Phase **P6** of [`PLATFORM_BASE_GENERAL_PLAN.md`](./PLATFORM_BASE_GENERAL_PLAN.md). Baseline: [`PLATFORM_BASE_FINDINGS.md`](./PLATFORM_BASE_FINDINGS.md). **P6 only.** **Runs in** `/Users/raimonds.krauklis/projects/irbene_gate`. Last file — closeout.

**Goal:** The consumer copy says Irbene Gate, talks to its DBs and realm — still no ontology. Then close the program.

**Push:** batch

Do not ask Continue?. After each Deliverable, next heading. After the ship gate, Next is none.

## Decisions locked for P6

- Q9: no Scan/Issue/Product.
- Overlay identity only: app name, tokens, Keycloak realm/clients, `VIRAC_*` / local DB URLs, nginx names if any.
- Do not leak Irbene names back into the tagged `saas-base` template.
- `docs/vision.md` in the consumer stays the north star (do not rewrite as a SaaS runbook).
- Findings consumer P6 gate: `backend/` + `frontend/` present; vision unchanged; new DBs; no ontology tables.
- Clear `active_program` → `null` in **template** `.revy/review-context.json` (SSOT) **and** the `.agent/review-context.json` mirror only after the gap table has no fix-now rows. Keep `rule_packs_catalog`. Both files must stay identical.

## Out of scope for P6

- Ontology, pipelines, operator UI beyond stock dashboard/settings
- Editing `saas-base-v2` tag contents except program-doc SHA/gap already allowed in the template `docs/platform-base/`

**Cwd for overlay work (P6.1–P6.2):** `/Users/raimonds.krauklis/projects/irbene_gate`. Template SSOT (P6.3–P6.4, review-context) uses absolute `/Users/raimonds.krauklis/projects/saas-base`.

## P6.1 — Identity overlay

**What:** Apply Irbene Gate names/realm/clients/URLs using `VIRAC_*` and consumer `.env.example`. Follow template `APP_REPLACE.md` keys. EN+LV for any user-facing string change.
**Files:** `backend/.env.example` / app env, `frontend/.env.example`, `backend/app/core/config.py` defaults if still generic, `frontend/src/i18n/locales/en.json`, `frontend/src/i18n/locales/lv.json`, `deploy/keycloak/**`, `deploy/nginx/**` if copied
**Deliverable:** `rg -q 'VIRAC_' backend/.env.example; rg -n 'revy.createit.digital' backend frontend deploy && exit 1 || true`

## P6.2 — Mode A on Irbene DBs

**What:** Boot against **new** Irbene local Postgres+KC (not Revy, not the template smoke DBs). Login smoke same as P4. No ontology migrations. **If Postgres or Keycloak is down, fail this phase — do not skip smoke.**
**Files:** none if green
**Deliverable:** `GET /api/v1/me` → `active` + `users` row; `rg -n 'scan|ontology' backend/alembic/versions && exit 1 || true`

## P6.3 — Gap table

**What:** Compare general plan P0–P6 vs shipped. Rows: item | expected | shipped | fix-now or later. No fix-now rows before closeout. Optional code fixes in this subphase only if the table says fix-now.
**Files:** `/Users/raimonds.krauklis/projects/saas-base/docs/platform-base/PLATFORM_BASE_FINDINGS.md` (gap section)
**Deliverable:** gap table with zero fix-now rows

## P6.4 — Doc sync and idle review-context

**What:** Platform doc grep for this program (`| Doc | Change |`): findings P6 gate green; general plan SHA already recorded; consumer pointer has `saas-base-v2`; template `docs/platform-base/README.md` status rows P0–P6 done. Then set template `.revy/review-context.json` and `.agent/review-context.json` `active_program` to `null` (same JSON); keep `rule_packs_catalog`. Update `.cursor/BUGBOT.md` idle stub.
**Files:** `/Users/raimonds.krauklis/projects/saas-base/docs/platform-base/README.md`, `/Users/raimonds.krauklis/projects/saas-base/docs/platform-base/PLATFORM_BASE_FINDINGS.md`, `/Users/raimonds.krauklis/projects/saas-base/.revy/review-context.json`, `/Users/raimonds.krauklis/projects/saas-base/.agent/review-context.json`, `/Users/raimonds.krauklis/projects/saas-base/.cursor/BUGBOT.md`; consumer `docs/platform-base/README.md` if needed
**Deliverable:** `python3 -c "import json; a=json.load(open('/Users/raimonds.krauklis/projects/saas-base/.revy/review-context.json')); b=json.load(open('/Users/raimonds.krauklis/projects/saas-base/.agent/review-context.json')); assert a==b and a['active_program'] is None"`

**Phase gate:**

```bash
# consumer cwd
test -f docs/vision.md
test -d backend && test -d frontend
rg -n 'saas-base-v2' docs/platform-base/README.md
rg -q 'VIRAC_' backend/.env.example
rg -n 'revy.createit.digital' backend frontend deploy && exit 1 || true
# template SSOT + mirror
python3 -c "import json; a=json.load(open('/Users/raimonds.krauklis/projects/saas-base/.revy/review-context.json')); b=json.load(open('/Users/raimonds.krauklis/projects/saas-base/.agent/review-context.json')); assert a==b and a['active_program'] is None"
```

(Run overlay pytest/npm in the consumer if env allows; Mode A evidence in findings P6 rows.)

## LOOP ship gate

Do not ask Continue?. After this gate, Next is none.
Pause LOOP only if a subphase above said Pause LOOP (migration).

1. Overlay commits: branch not main, **cwd** `/Users/raimonds.krauklis/projects/irbene_gate`. Template-repo doc/SSOT edits: `feat/platform-base` in `/Users/raimonds.krauklis/projects/saas-base`.
2. Lint consumer app if overlay touched backend/frontend (`cd backend && pipenv run ruff check --fix . && pipenv run ruff check .`; `cd frontend && npm run lint`) — from irbene_gate cwd
3. Phase gate above — green
4. Bugbot:
REPEAT until Bugbot CLOSE:
  1. Invoke review-bugbot (run_in_background: false) for each dirty repo (irbene_gate first, then saas-base if docs/SSOT changed)
  2. Diff: uncommitted changes
  3. Custom Instructions: VERB FIND + this phase locked decisions + .cursor/BUGBOT.md
  4. Fix blockers; re-lint if code changed
END REPEAT
5. Commit in irbene_gate: feat(platform-base): P6 Irbene overlay
6. Commit in saas-base (if dirty): docs(platform-base): P6 closeout
7. No Revy (`integrations.revy: false`). Skip Revy REPEAT/WHILE.
8. One push per repo that has unpushed commits (Irbene PR + template PR if docs moved). Never force-push.
9. Confirm PR URL(s).
10. Next: none

**Next:** none
