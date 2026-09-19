# P5 — Copy base into irbene_gate (execution)

Phase **P5** of [`PLATFORM_BASE_GENERAL_PLAN.md`](./PLATFORM_BASE_GENERAL_PLAN.md). Baseline: [`PLATFORM_BASE_FINDINGS.md`](./PLATFORM_BASE_FINDINGS.md). **P5 only.** **Runs in** `/Users/raimonds.krauklis/projects/irbene_gate`.

**Goal:** Consumer repo has a runnable SaaS tree beside existing docs/learning.

**Push:** first-push (Irbene remote)

Do not ask Continue?. After each Deliverable, next heading. After the ship gate, open Next immediately.

## Decisions locked for P5

- Q8 = Q12: copy the **whole** tagged `saas-base-v2` tree, not an enumerated dir list.
- Out-list (do not overwrite): `docs/vision.md`, `docs/platform-base/`, `palantir/`, `polimi/`, `exercises/`, root learning `Pipfile` / `Pipfile.lock`, consumer `.env.example`.
- **Merge** template `.gitignore` into the existing consumer `.gitignore` (keep learning-dir ignores; add `node_modules/`, frontend build, `backend/.venv`). Do not replace the file.
- App Pipfile is `backend/Pipfile`. Root Pipfile stays learning.
- Record upstream tag in consumer `docs/platform-base/` (pointer stays a pointer; add SHA/tag).
- Consumer folder is currently **not** a git repo — `git init` here is in scope. Do not clone saas-base **over** this folder.
- No ontology.

## Out of scope for P5

- Irbene name/realm/DB overlay → **P6**
- Tracking learning dirs
- Changing the tagged template

**Cwd for this file:** `/Users/raimonds.krauklis/projects/irbene_gate` (all relative paths below). Source tree: tag `saas-base-v2` in `/Users/raimonds.krauklis/projects/saas-base`.

## P5.1 — Copy tagged tree around the Out-list

**What:** Copy **every path** on `saas-base-v2` into this consumer except the Out-list. No directory menu. If a source path would replace an Out-list file, skip it. **Merge** template `.gitignore` rules into the existing consumer `.gitignore` (keep learning-dir ignores; add `node_modules/`, frontend build, `backend/.venv`, etc.). Follow template `docs/platform-base/CONSUMER_COPY.md`. Do not clone saas-base over this folder.
**Files:** all paths on `saas-base-v2` minus Out-list. Out-list stays: `docs/vision.md`, `docs/platform-base/`, `palantir/`, `polimi/`, `exercises/`, root `Pipfile` / `Pipfile.lock`, `.env.example`. `.gitignore` is merged, not replaced.
**Deliverable:** `test -d backend && test -d frontend && test -f docs/vision.md && test -f .env.example && test -f Pipfile && test -f README.md && test -f .gitignore`

## P5.2 — Consumer git

**What:** If this directory has no `.git`, `git init -b main` then `git switch -c feat/platform-base`. Do not commit secrets (`.env`). Add GitHub origin when creating/using private `raimondskrauklis/irbene-gate` or the existing remote — do not invent a second host. First-push happens in the ship gate.
**Files:** `.git/`
**Deliverable:** `git branch --show-current | grep -v -E '^(main|master)$'`

## P5.3 — Pointer notes upstream tag

**What:** Consumer `docs/platform-base/README.md` still points at the template SSOT. Add the `saas-base-v2` **tag and SHA** (`git -C /Users/raimonds.krauklis/projects/saas-base rev-parse saas-base-v2^{commit}`). Do not duplicate findings.
**Files:** `docs/platform-base/README.md`
**Deliverable:** `rg -n 'saas-base-v2' docs/platform-base/README.md`

**Phase gate:**

```bash
test -d backend && test -d frontend && test -d deploy
test -f README.md
test -f docs/vision.md
test -f docs/platform-base/README.md
test -f .gitignore
rg -n 'node_modules' .gitignore
test -f .env.example
rg -n 'VIRAC_|POLIMI_DATABASE_URL' .env.example
test -f backend/Pipfile
rg -n 'numpy|matplotlib' Pipfile
rg -n 'saas-base-v2' docs/platform-base/README.md
test -d palantir && test -d polimi && test -d exercises
```

## LOOP ship gate

Do not ask Continue?. After this gate, open the Next file immediately.
Pause LOOP only if a subphase above said Pause LOOP (migration).

1. Branch — not main, **cwd** `/Users/raimonds.krauklis/projects/irbene_gate`
2. Lint if app tree is runnable (`cd backend && pipenv run ruff check .`; `cd frontend && npm run lint`) — skip pipenv/npm install failure only if the copy is complete and install is an env gap (record in chat; do not skip if files are missing)
3. Phase gate above — green
4. Bugbot:
REPEAT until Bugbot CLOSE:
  1. Invoke review-bugbot (run_in_background: false) on `/Users/raimonds.krauklis/projects/irbene_gate`
  2. Diff: uncommitted changes
  3. Custom Instructions: VERB FIND + this phase locked decisions + saas-base `.cursor/BUGBOT.md`
  4. Fix blockers; re-lint if code changed
END REPEAT
5. Commit: feat(platform-base): P5 copy saas-base-v2 tree
6. No Revy. Skip Revy poll.
7. Push (opens PR on the Irbene remote; first commit on this branch). Title: feat(platform-base): copy saas-base-v2 into Irbene Gate. Use ship-changes **from Push onward**.
8. Confirm PR URL. Do not fetch or fix review comments yet.
9. Open Next immediately.

**Next:** [`PLATFORM_BASE_P6_EXECUTION.md`](./PLATFORM_BASE_P6_EXECUTION.md)
