# P0 — Repo and prefix (execution)

Phase **P0** of [`PLATFORM_BASE_GENERAL_PLAN.md`](./PLATFORM_BASE_GENERAL_PLAN.md). Baseline: [`PLATFORM_BASE_FINDINGS.md`](./PLATFORM_BASE_FINDINGS.md). **P0 only.**

**Goal:** This directory is a git repo whose history is the frozen shell through `saas-base-v1.1`, program docs in `docs/platform-base/`, private GitHub remote exists, no push yet.

**Push:** local

Do not ask Continue?. After each Deliverable, next heading. After the ship gate, open Next immediately.

## Decisions locked for P0

- Import **into** `/Users/raimonds.krauklis/projects/saas-base`. Never `git clone` Revy (or any URL) as this folder — that wipes `docs/`.
- Program docs live in `docs/platform-base/`, not `docs/` root (shell already has `starter-pack/`, `saas-base/`, `review-pipeline/`).
- History from `0db2f60` through tag `saas-base-v1.1` commit `48c361e20081bd71a4cbf176c9ba71bd09869082` only. No squash. Do not fetch `revy/main` or `ed773f4`.
- Source: local `/Users/raimonds.krauklis/projects/revy` (fetch by path). Not a nested clone inside this tree.
- Preserve program files: `docs/platform-base/`, `docs/agents/`, `docs/utils/CURSOR_AGENT_WORKFLOW.md`, `.agent/`, pack skills, this execution file.
- After checkout: keep shell `.cursorrules` and `.cursor/rules/`. Overlay pack skills from `../agent-workflow`. Remove legacy `babysit-pr`. Do **not** install `babysit-revy-pr`. Do **not** copy kp-platform `.cursorrules`.
- Hosting: GitHub **without** Revy. Create private `raimondskrauklis/saas-base` and add `origin`. Do **not** push.
- SSOT is `.agent/review-context.json` (no `.revy/`).
- Root README must say this is the generic SaaS shell, not Revy the GitHub reviewer.

## Out of scope for P0

- Strip GitHub installations / `0004` / `vector` / LLM env → **P1**
- Port Auth #32 / `ed773f4` → **P2**
- Full Revy-string genericize → **P3**
- Tag `saas-base-v2` / Mode A smoke → **P4**
- Copy into `../irbene_gate` → **P5–P6**
- `internal-docs/`
- Writing P1–P6 execution files
- Push / PR / Revy

## P0.0 — Program PR review context

**What:** Wire `.agent/review-context.json` + `.cursor/BUGBOT.md`. One `programs[]` entry `platform-base`. Scope `backend/**`, `frontend/**`, and `deploy/**` (imported tree is full-stack). Omit `rule_packs` (`manifest.review_context.rule_packs` is null). Keep `rule_packs_catalog` as `{}`. Bugbot: three program docs only. Do not ask which packs. Do not create `.revy/`. **P0 is landed — do not re-execute this subphase** (LOOP starts at P1). The JSON below is the current SSOT snapshot, not a rewrite ticket.
**Files:** `.agent/review-context.json`, `.cursor/BUGBOT.md`
**Deliverable:** `python3 -m json.tool .agent/review-context.json`

```json
{
  "active_program": "platform-base",
  "programs": [
    {
      "id": "platform-base",
      "scope": ["backend/**", "frontend/**", "deploy/**"],
      "paths": [
        { "path": "docs/platform-base/README.md", "description": "execution" },
        { "path": "docs/platform-base/PLATFORM_BASE_FINDINGS.md", "description": "findings" },
        { "path": "docs/platform-base/PLATFORM_BASE_GENERAL_PLAN.md", "description": "general plan" }
      ]
    }
  ],
  "rule_packs_catalog": {}
}
```

## P0.1 — Import shell history into this tree

**What:** Backup the overlay. `git init` here. `git fetch` the **tag only** from local `../revy`. Point `main` at `saas-base-v1.1`. Restore the overlay on top. Never clone into this directory.
**Files:** `.git/` (new), restored `docs/platform-base/`, `docs/agents/`, `.agent/`, `.cursor/skills/` (pack), `AGENTS.md` overlay notes
**Deliverable:**

```bash
test -f docs/platform-base/PLATFORM_BASE_FINDINGS.md
test -f docs/platform-base/PLATFORM_BASE_GENERAL_PLAN.md
test -f docs/platform-base/PLATFORM_BASE_P0_EXECUTION.md
test "$(git rev-parse saas-base-v1.1^{commit})" = "48c361e20081bd71a4cbf176c9ba71bd09869082"
git merge-base --is-ancestor 0db2f60 HEAD
git cat-file -e ed773f4^{commit} 2>/dev/null && echo FAIL_fetched_auth32 && exit 1 || true
test -d backend && test -d frontend
```

Exact import (do not substitute a clone):

```bash
TARGET=/Users/raimonds.krauklis/projects/saas-base
REVY=/Users/raimonds.krauklis/projects/revy
BACKUP=$(mktemp -d /tmp/saas-base-overlay.XXXXXX)
# copy overlay: docs/platform-base/, docs/agents, docs/utils/CURSOR_AGENT_WORKFLOW.md,
# .agent, .cursor (pack skills + BUGBOT), AGENTS.md, this execution file if not under docs/ already
cd "$TARGET"
git init -b main
git fetch "$REVY" refs/tags/saas-base-v1.1:refs/tags/saas-base-v1.1
git switch -C main saas-base-v1.1
# restore overlay files from $BACKUP without deleting shell docs/saas-base, docs/starter-pack, .cursor/rules, .cursorrules
git switch -c feat/platform-base
```

## P0.2 — README is the generic shell

**What:** Replace root `README.md` (imported Revy blurb) with a generic saas-base README. Keep layout/quick-start pointers to `docs/starter-pack/DEV_BOOTSTRAP.md`. Point program work at `docs/platform-base/README.md`. Do not rewrite starter-pack runbooks.
**Files:** `README.md`, `docs/platform-base/README.md` (execution table)
**Deliverable:** `grep -n 'GitHub reviewer\|AI-assisted code review' README.md && exit 1 || true; head -20 README.md`

## P0.3 — Re-apply agent-workflow overlay

**What:** Pack skills overwrite core/meta/planning under `.cursor/skills/` from `../agent-workflow/templates`. Restore `.agent/manifest.json` (hosting github, `integrations.revy: false`, test_commands pipenv/npm). Merge `AGENTS.md`: keep shell stack tables; product name **saas-base** not Revy; installed-skills table matches manifest. Delete `.cursor/skills/babysit-pr` and `.cursor/commands/babysit-pr.md`. Do not create `.revy/`. Keep `.cursorrules` and `.cursor/rules/`. Leave imported `docs/utils/` deploy notes; keep `CURSOR_AGENT_WORKFLOW.md`.
**Files:** `.cursor/skills/`, `.agent/`, `AGENTS.md`, `.cursor/BUGBOT.md`
**Deliverable:** `test ! -d .cursor/skills/babysit-pr; test ! -d .cursor/skills/babysit-revy-pr; test -f .cursor/skills/bootstrap-workflow/SKILL.md; python3 -m json.tool .agent/manifest.json >/dev/null; test -f .cursorrules; test -d .cursor/rules`

## P0.4 — Private GitHub repo, no push

**What:** `gh repo create raimondskrauklis/saas-base --private`. Add `origin`. Do not `git push`. Do not `--source` clone-over.
**Files:** `.git/config` remote `origin`
**Deliverable:** `git remote get-url origin; gh repo view raimondskrauklis/saas-base --json name,visibility,isPrivate`

## P0.5 — Prefix verification

**What:** Another agent could inspect this tree and see the frozen tag, program docs, and workflow. `HEAD` may be this P0 commit on `feat/platform-base` (equivalent tip: tag is ancestor, Auth #32 is not).
**Files:** none extra
**Deliverable:**

```bash
git log -1 --decorate
git merge-base --is-ancestor 48c361e20081bd71a4cbf176c9ba71bd09869082 HEAD
test -f docs/platform-base/PLATFORM_BASE_FINDINGS.md
test -f backend/Pipfile
test -f frontend/package.json
```

**Phase gate:**

```bash
test "$(git rev-parse saas-base-v1.1^{commit})" = "48c361e20081bd71a4cbf176c9ba71bd09869082"
git merge-base --is-ancestor 0db2f60 HEAD
git merge-base --is-ancestor 48c361e20081bd71a4cbf176c9ba71bd09869082 HEAD
test -f docs/platform-base/PLATFORM_BASE_FINDINGS.md
test -f docs/platform-base/PLATFORM_BASE_GENERAL_PLAN.md
test -f docs/platform-base/PLATFORM_BASE_P0_EXECUTION.md
python3 -m json.tool .agent/review-context.json >/dev/null
python3 -m json.tool .agent/manifest.json >/dev/null
git remote get-url origin | grep -q 'raimondskrauklis/saas-base'
test -d backend && test -d frontend
git cat-file -e ed773f4^{commit} 2>/dev/null && echo FAIL_fetched_auth32 && exit 1 || true
```

No backend pytest this phase (no Python app edits; venv not required).

## LOOP ship gate

Do not ask Continue?. After this gate, open the Next file immediately.
Pause LOOP only if a subphase above said Pause LOOP (migration).

1. Branch — not main (`feat/platform-base`)
2. Lint — skip `backend`/`frontend` pipenv/npm unless those globs changed in the P0 overlay diff. Overlay is docs + workflow + README.
3. Phase gate above — green
4. Bugbot:
REPEAT until Bugbot CLOSE:
  1. Invoke review-bugbot (run_in_background: false)
  2. Diff: uncommitted changes
  3. Custom Instructions: VERB FIND + this phase locked decisions + .cursor/BUGBOT.md
  4. Fix blockers; re-lint if code changed
END REPEAT
5. Commit: feat(platform-base): P0 repo and prefix
6. Do not push.
7. Update README status row.
8. Open Next immediately.

**Next:** [`PLATFORM_BASE_P1_EXECUTION.md`](./PLATFORM_BASE_P1_EXECUTION.md)
